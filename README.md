# Touchless Presentation Controller

A Windows desktop application that enables hands-free PowerPoint presentation control using real-time hand gesture recognition.

Touchless Presentation Controller (TPC) uses a webcam, computer vision, and hand tracking to let presenters navigate PowerPoint slides without touching a keyboard or mouse.


## ✨ Features

- 🖐️ **Open Palm — Next Slide**
  Advance to the next PowerPoint slide using an open palm gesture.

- ✊ **Fist — Previous Slide**
  Return to the previous slide using a fist gesture.

- 🎯 **Dedicated Gesture Zone**
  Gestures are only processed when the hand is inside the designated gesture zone, reducing accidental slide changes caused by normal presentation body language.

- 📷 **Real-Time Hand Tracking**
  Uses the webcam to detect and track hand landmarks in real time.

- 📂 **PowerPoint File Selection**
  Select `.pptx` or `.ppt` presentations directly from the application.

- ▶️ **Automatic Slide Show**
  The selected presentation is opened directly in PowerPoint Slide Show mode.

- 📖 **Built-in Tutorial**
  Includes an interactive tutorial explaining how to use the gesture controls.

- 🖥️ **Windows Desktop Application**
  Designed specifically for Windows with PowerPoint integration.


## 🎮 Gesture Controls

| Gesture | Action |
|--------|--------|
| 🖐️ Open Palm | Next Slide |
| ✊ Fist | Previous Slide |

### 🟥 Gesture Zone

The gesture zone is located in the **top-right area of the camera view**.

Only gestures detected inside this zone are processed as presentation commands.

This design helps prevent accidental triggers when the presenter naturally moves their hands while speaking.


## 🏗️ Architecture

```text
Touchless Presentation Controller
│
├── Web Interface
│   ├── Home
│   ├── Presentation Mode
│   └── Tutorial
│
├── Python Backend
│   ├── Application API
│   ├── Camera Controller
│   └── PowerPoint Controller
│
├── Computer Vision
│   ├── OpenCV
│   └── MediaPipe Hand Landmarker
│
└── PowerPoint Integration
    └── Microsoft PowerPoint COM
```

## 🛠️ Technologies

-  Python
-  pywebview
-  OpenCV
-  MediaPipe
-  Microsoft PowerPoint COM
-  HTML
-  CSS
-  JavaScript
-  PyInstaller


## ⚙️ Requirements

-  Windows 10 / Windows 11
-  Python 3.11
-  webcam
-  Microsoft PowerPoint
-  Internet connection for the initial MediaPipe model download if the model is not already available


## 🚀 Installation

1. Clone the repository
   git clone https://github.com/YOUR_USERNAME/Touchless-Presentation-Controller.git
   cd Touchless-Presentation-Controller

2. Create a virtual environment
   python -m venv venv

3. Activate the virtual environment
   .\venv\Scripts\Activate.ps1

4. Install dependencies
   pip install -r requirements.txt

5. Run the application
   python main.py


## 📖 How to Use

1. Launch the application.
2. Click Choose File.
3. Select a PowerPoint presentation (.pptx or .ppt).
4. Click Start Presentation.
5. Position your hand inside the gesture zone.
6. Use:
   - 🖐️ Open Palm → Next Slide
   - ✊ Fist → Previous Slide
7. Use the built-in tutorial if you need help understanding the controls.


## 🔒 Design Considerations

A major design consideration of TPC is preventing accidental gesture activation.

During a presentation, users naturally move their hands while explaining content. A gesture recognition system that reacts to every open palm or fist could therefore trigger slides unintentionally.

TPC addresses this by requiring the hand to be inside a dedicated gesture zone before a command is recognized.

This makes the interaction more intentional and suitable for real presentation environments.


## 🎯 Project Goals

TPC was developed to explore the combination of:
-  Computer vision
-  Hand gesture recognition
-  Human-computer interaction
-  Desktop application development
-  PowerPoint automation
-  Python and web-based UI integration

The main goal is to create a simple and practical presentation controller that allows presenters to control slides without physically interacting with their computer.


## 👩‍💻 Author

Syakira Aisya Fiandifa
Student — Software Engineering / RPL
