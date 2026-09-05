import base64
import json
import math
import threading
import time
import urllib.request
from collections import deque
from pathlib import Path

import cv2
import mediapipe as mp


MODEL_URL = (
    "https://storage.googleapis.com/"
    "mediapipe-models/hand_landmarker/hand_landmarker/float16/1/"
    "hand_landmarker.task"
)


class CameraController:

    def __init__(self):
        self.running = False
        self.thread = None
        self.window = None
        self.camera = None
        
        self.gesture_repeat_interval = 1.0
        self.last_gesture_action_time = 0
        self.active_gesture = None

        self.gesture_history = deque(maxlen=8)

        self.required_stable_frames = 8

        self.last_action_time = 0
        self.cooldown = 0.8

        # True = gesture boleh digunakan
        # False = harus keluar zona terlebih dahulu
        self.armed = True

        self.gesture_zone = {
            "x": 0.68,
            "y": 0.04,
            "width": 0.29,
            "height": 0.34,
        }

    # ZONE

    def is_hand_in_zone(self, x, y):
        """
        Mengecek apakah titik tengah telapak tangan
        berada di dalam gesture zone.
        """

        zone = self.gesture_zone

        return (
            zone["x"] <= x <= zone["x"] + zone["width"]
            and
            zone["y"] <= y <= zone["y"] + zone["height"]
        )

    def _get_hand_position(self, landmarks):
        """
        Mengambil posisi tengah telapak tangan.

        Menggunakan beberapa landmark telapak,
        bukan hanya wrist, agar zona lebih stabil.
        """

        palm_indices = [
            0,   # wrist
            5,   # index MCP
            9,   # middle MCP
            13,  # ring MCP
            17,  # pinky MCP
        ]

        x = sum(
            landmarks[index].x
            for index in palm_indices
        ) / len(palm_indices)

        y = sum(
            landmarks[index].y
            for index in palm_indices
        ) / len(palm_indices)

        return x, y

    # WINDOW

    def set_window(self, window):
        self.window = window

    # CAMERA START / STOP

    def start(self):
        if self.running:
            return True

        self.running = True

        self.thread = threading.Thread(
            target=self._camera_loop,
            daemon=True
        )

        self.thread.start()

        return True

    def stop(self):
        self.running = False

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)

        self.thread = None

        if self.camera:
            self.camera.release()
            self.camera = None

        self.gesture_history.clear()
        self.armed = True

        self._update_status("Camera stopped")

        return True

    # MEDIAPIPE MODEL

    def _ensure_model(self):
        model_directory = (
            Path(__file__).resolve().parent.parent
            / "models"
        )

        model_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        model_path = (
            model_directory
            / "hand_landmarker.task"
        )

        if model_path.exists():
            return model_path

        self._update_status(
            "Downloading hand model..."
        )

        urllib.request.urlretrieve(
            MODEL_URL,
            model_path
        )

        return model_path

    def _create_landmarker(self, model_path):
        base_options = mp.tasks.BaseOptions(
            model_asset_path=str(model_path)
        )

        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=(
                mp.tasks.vision.RunningMode.VIDEO
            ),
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )

        return (
            mp.tasks.vision.HandLandmarker
            .create_from_options(options)
        )

    # DISTANCE

    @staticmethod
    def _distance(point_a, point_b):
        return math.sqrt(
            (point_a.x - point_b.x) ** 2
            + (point_a.y - point_b.y) ** 2
            + (point_a.z - point_b.z) ** 2
        )

    # FINGER DETECTION

    def _is_finger_extended(
        self,
        landmarks,
        tip_index,
        pip_index
    ):
        wrist = landmarks[0]
        tip = landmarks[tip_index]
        pip = landmarks[pip_index]

        tip_distance = self._distance(
            wrist,
            tip
        )

        pip_distance = self._distance(
            wrist,
            pip
        )

        return (
            tip_distance
            > pip_distance * 1.15
        )

    # GESTURE DETECTION

    def _detect_gesture(self, landmarks):

        index_extended = (
            self._is_finger_extended(
                landmarks,
                8,
                6
            )
        )

        middle_extended = (
            self._is_finger_extended(
                landmarks,
                12,
                10
            )
        )

        ring_extended = (
            self._is_finger_extended(
                landmarks,
                16,
                14
            )
        )

        pinky_extended = (
            self._is_finger_extended(
                landmarks,
                20,
                18
            )
        )

        extended_count = sum(
            [
                index_extended,
                middle_extended,
                ring_extended,
                pinky_extended,
            ]
        )

        # Open Palm
        if extended_count >= 4:
            return "open_palm"

        # Fist
        if extended_count <= 1:
            return "fist"

        return "unknown"

    # PROCESS GESTURE

    def _process_gesture(
        self,
        gesture,
        landmarks
        ):
        
        now = time.monotonic()

        if not landmarks:
            self.gesture_history.clear()

            self.armed = True
            self.active_gesture = None

            return

        x, y = self._get_hand_position(
            landmarks
        )

        in_zone = self.is_hand_in_zone(
            x,
            y
        )

        if not in_zone:
            self.gesture_history.clear()

            self.armed = True
            self.active_gesture = None

            return

        self.gesture_history.append(
            gesture
        )

        # Belum cukup stabil.
        if (
            len(self.gesture_history)
            < self.required_stable_frames
        ):
            return

        recent = list(
            self.gesture_history
        )[-self.required_stable_frames:]

        # Gesture harus stabil.
        if recent.count(gesture) < (
            self.required_stable_frames - 1
        ):
            return

        if gesture not in (
            "open_palm",
            "fist"
        ):
            return

        if self.active_gesture != gesture:
            self.active_gesture = gesture

            self.armed = True

            self.last_gesture_action_time = (
                now - self.gesture_repeat_interval
            )


        if not self.armed:
            return

        if (
            now - self.last_gesture_action_time
            < self.gesture_repeat_interval
        ):
            return

        if gesture == "open_palm":

            self._send_gesture(
                "next"
            )

        elif gesture == "fist":

            self._send_gesture(
                "previous"
            )

        self.last_gesture_action_time = now

        self.armed = True

    # SEND GESTURE TO JAVASCRIPT

    def _send_gesture(self, action):

        if not self.window:
            return

        try:
            script = (
                "handleGesture("
                + json.dumps(action)
                + ");"
            )

            self.window.evaluate_js(
                script
            )

        except Exception as error:
            print(
                f"Gesture callback error: {error}"
            )

    def _update_status(self, status):

        if not self.window:
            return

        try:
            self.window.evaluate_js(
                "updateCameraStatus("
                + json.dumps(status)
                + ");"
            )

        except Exception:
            pass

    def _update_frame(self, frame):

        if not self.window:
            return

        try:
            success, encoded = cv2.imencode(
                ".jpg",
                frame,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    70
                ]
            )

            if not success:
                return

            image_data = base64.b64encode(
                encoded.tobytes()
            ).decode("utf-8")

            data_uri = (
                "data:image/jpeg;base64,"
                + image_data
            )

            self.window.evaluate_js(
                "updateCameraFrame("
                + json.dumps(data_uri)
                + ");"
            )

        except Exception:
            pass

    # DRAW HAND LANDMARKS

    def _draw_landmarks(
        self,
        frame,
        landmarks
    ):
        height, width = frame.shape[:2]

        points = []

        for landmark in landmarks:

            x = int(
                landmark.x * width
            )

            y = int(
                landmark.y * height
            )

            points.append(
                (x, y)
            )

            cv2.circle(
                frame,
                (x, y),
                4,
                (145, 80, 255),
                -1
            )

        connections = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),

            (0, 5),
            (5, 6),
            (6, 7),
            (7, 8),

            (0, 9),
            (9, 10),
            (10, 11),
            (11, 12),

            (0, 13),
            (13, 14),
            (14, 15),
            (15, 16),

            (0, 17),
            (17, 18),
            (18, 19),
            (19, 20),

            (5, 9),
            (9, 13),
            (13, 17),
        ]

        for start, end in connections:

            if (
                start < len(points)
                and end < len(points)
            ):
                cv2.line(
                    frame,
                    points[start],
                    points[end],
                    (255, 180, 80),
                    2
                )

    def _draw_gesture_zone(self, frame):

        height, width = frame.shape[:2]

        zone = self.gesture_zone

        x1 = int(
            width * zone["x"]
        )

        y1 = int(
            height * zone["y"]
        )

        x2 = int(
            width
            * (
                zone["x"]
                + zone["width"]
            )
        )

        y2 = int(
            height
            * (
                zone["y"]
                + zone["height"]
            )
        )

        overlay = frame.copy()

        red = (
            0,
            0,
            255
        )

        cv2.rectangle(
            overlay,
            (x1, y1),
            (x2, y2),
            red,
            -1
        )

        alpha = 0.25

        frame[:] = cv2.addWeighted(
            overlay,
            alpha,
            frame,
            1 - alpha,
            0
        )

    # CAMERA LOOP

    def _camera_loop(self):

        landmarker = None

        try:

            # LOAD MODEL

            model_path = (
                self._ensure_model()
            )

            landmarker = (
                self._create_landmarker(
                    model_path
                )
            )

            # OPEN CAMERA

            self.camera = (
                cv2.VideoCapture(0)
            )

            if not self.camera.isOpened():

                self._update_status(
                    "Camera unavailable"
                )

                self.running = False

                if landmarker:
                    landmarker.close()

                return

            self.camera.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                640
            )

            self.camera.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                480
            )

            self.camera.set(
                cv2.CAP_PROP_FPS,
                30
            )

            self._update_status(
                "Camera on"
            )

            frame_timestamp = 0

            # MAIN CAMERA LOOP

            while self.running:

                success, frame = (
                    self.camera.read()
                )

                if not success:

                    self._update_status(
                        "Camera frame error"
                    )

                    time.sleep(0.4)

                    continue

                # Mirror camera.
                frame = cv2.flip(
                    frame,
                    1
                )

                # DRAW ZONE

                self._draw_gesture_zone(
                    frame
                )

                # MEDIAPIPE

                rgb_frame = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2RGB
                )

                mp_image = mp.Image(
                    image_format=(
                        mp.ImageFormat.SRGB
                    ),
                    data=rgb_frame
                )

                frame_timestamp += 33

                result = (
                    landmarker.detect_for_video(
                        mp_image,
                        frame_timestamp
                    )
                )

                gesture = "unknown"
                landmarks = None

                # HAND DETECTED

                if result.hand_landmarks:

                    landmarks = (
                        result.hand_landmarks[0]
                    )

                    # Gambar landmark tangan.
                    self._draw_landmarks(
                        frame,
                        landmarks
                    )

                    # Deteksi gesture.
                    gesture = (
                        self._detect_gesture(
                            landmarks
                        )
                    )

                # PROCESS GESTURE

                self._process_gesture(
                    gesture,
                    landmarks
                )

                # DISPLAY GESTURE

                display_gesture = {
                    "open_palm": "Open Palm",
                    "fist": "Fist",
                    "unknown": "Show your hand",
                }.get(
                    gesture,
                    "Show your hand"
                )

                cv2.putText(
                    frame,
                    display_gesture,
                    (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.9,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA
                )

                # SEND FRAME TO UI

                self._update_frame(
                    frame
                )

                time.sleep(0.03)

        except Exception as error:

            print(
                f"Camera error: {error}"
            )

            self._update_status(
                "Camera error"
            )

        finally:

            if landmarker:

                try:
                    landmarker.close()

                except Exception:
                    pass

            if self.camera:

                try:
                    self.camera.release()

                except Exception:
                    pass

                self.camera = None

            self.running = False