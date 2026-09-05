from pathlib import Path
import threading

import webview
import win32com.client

from camera.camera_controller import CameraController


class TPCAPI:
    def __init__(self):
        self._window = None
        self._camera = CameraController()

        self._powerpoint = None
        self._presentation = None
        self._presentation_path = ""

    def set_window(self, window):
        self._window = window
        self._camera.set_window(window)

    def get_app_info(self):
        return {
            "name": "Touchless Presentation Controller",
            "version": "1.0.0",
        }

    def choose_file(self):
        """
        Membuka Windows native OpenFileDialog melalui WinForms.
        """

        try:
            import clr

            clr.AddReference("System.Windows.Forms")

            from System.Windows.Forms import (
                OpenFileDialog,
                DialogResult,
            )

            dialog = OpenFileDialog()

            dialog.Title = (
                "Choose PowerPoint Presentation"
            )

            dialog.Filter = (
                "PowerPoint Presentation "
                "(*.pptx;*.ppt)|*.pptx;*.ppt|"
                "PowerPoint (*.pptx)|*.pptx|"
                "All Files (*.*)|*.*"
            )

            dialog.FilterIndex = 1
            dialog.Multiselect = False
            dialog.CheckFileExists = True
            dialog.CheckPathExists = True

            result = dialog.ShowDialog()

            if result != DialogResult.OK:
                print("File picker dibatalkan.")

                return {
                    "success": False,
                    "path": "",
                    "filename": "",
                }

            file_path = Path(
                str(dialog.FileName)
            )

            print(
                f"File dipilih: {file_path}"
            )

            if not file_path.exists():
                print(
                    "File tidak ditemukan."
                )

                return {
                    "success": False,
                    "path": "",
                    "filename": "",
                }

            if file_path.suffix.lower() not in (
                ".pptx",
                ".ppt",
            ):
                print(
                    "File bukan PowerPoint."
                )

                return {
                    "success": False,
                    "path": "",
                    "filename": "",
                }

            return {
                "success": True,
                "path": str(file_path),
                "filename": file_path.name,
            }

        except Exception as error:
            print(
                "ERROR CHOOSE FILE:"
            )

            print(
                repr(error)
            )

            return {
                "success": False,
                "path": "",
                "filename": "",
            }

    def open_presentation(self, file_path):

        try:
            path = Path(file_path)

            if (
                not path.exists()
                or path.suffix.lower()
                not in (".pptx", ".ppt")
            ):
                return False

            self.close_presentation()

            self._powerpoint = (
                win32com.client.Dispatch(
                    "PowerPoint.Application"
                )
            )

            self._powerpoint.Visible = True

            self._presentation = (
                self._powerpoint.Presentations.Open(
                    str(path),
                    ReadOnly=True,
                    WithWindow=True,
                )
            )

            self._presentation_path = str(path)

            self._presentation.SlideShowSettings.Run()

            return True

        except Exception as error:

            print(
                f"ERROR membuka PowerPoint: {error}"
            )

            self._powerpoint = None
            self._presentation = None
            self._presentation_path = ""

            return False

    def next_slide(self):

        try:
            if not self._presentation:
                return False

            slide_show = (
                self._presentation.SlideShowWindow
            )

            if not slide_show:
                return False

            slide_show.View.Next()

            return True

        except Exception as error:

            print(
                f"ERROR next slide: {error}"
            )

            return False

    def previous_slide(self):

        try:
            if not self._presentation:
                return False

            slide_show = (
                self._presentation.SlideShowWindow
            )

            if not slide_show:
                return False

            slide_show.View.Previous()

            return True

        except Exception as error:

            print(
                f"ERROR previous slide: {error}"
            )

            return False

    def close_presentation(self):

        try:

            if self._presentation:

                try:

                    slide_show = (
                        self._presentation.SlideShowWindow
                    )

                    if slide_show:
                        slide_show.View.Exit()

                except Exception:
                    pass

                try:
                    self._presentation.Close()

                except Exception:
                    pass

            if self._powerpoint:

                try:
                    self._powerpoint.Quit()

                except Exception:
                    pass

        except Exception as error:

            print(
                f"ERROR menutup PowerPoint: {error}"
            )

        finally:

            self._presentation = None
            self._powerpoint = None
            self._presentation_path = ""

        return True

    def start_camera(self):

        try:
            return self._camera.start()

        except Exception as error:

            print(
                f"ERROR start camera: {error}"
            )

            return False

    def stop_camera(self):

        try:
            return self._camera.stop()

        except Exception as error:

            print(
                f"ERROR stop camera: {error}"
            )

            return False

    def exit_app(self):

        print(
            "EXIT BUTTON DIPANGGIL"
        )

        try:
            self.close_presentation()

        except Exception as error:

            print(
                f"ERROR PowerPoint saat exit: {error}"
            )

        try:
            self._camera.stop()

        except Exception as error:

            print(
                f"ERROR kamera saat exit: {error}"
            )

        print(
            "TPC akan ditutup."
        )

        # Tutup aplikasi setelah API call selesai.
        def close_window():

            try:

                if self._window:
                    self._window.destroy()

            except Exception as error:

                print(
                    f"ERROR destroy window: {error}"
                )

        threading.Timer(
            0.2,
            close_window
        ).start()

        return True


def get_project_path() -> Path:
    return Path(__file__).resolve().parent


def get_index_path() -> str:

    return str(
        get_project_path()
        / "web"
        / "index.html"
    )


def main():

    index_path = Path(
        get_index_path()
    )

    if not index_path.exists():

        raise FileNotFoundError(
            "Frontend file tidak ditemukan:\n"
            f"{index_path}"
        )

    api = TPCAPI()

    window = webview.create_window(
        title="Touchless Presentation Controller",
        url=index_path.as_uri(),
        js_api=api,
        width=1100,
        height=700,
        min_size=(900, 600),
        resizable=True,
    )

    api.set_window(window)

    webview.start(
        debug=False,
        func=lambda: window.maximize(),
    )


if __name__ == "__main__":
    main()