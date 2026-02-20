# Eye Controlled Mouse using OpenCV, MediaPipe, and PyAutoGUI

## Overview

This project implements a **vision-based mouse controller** that allows users to move the cursor and perform clicks using eye movements. It leverages real-time facial landmark detection to track eye positions and translate them into screen coordinates.

The system uses:

* **Computer Vision** for webcam capture and frame processing
* **Facial Landmark Detection** for eye tracking
* **Automation Control** for cursor movement and clicking

---

## Features

* Real-time eye tracking via webcam
* Cursor movement mapped to eye position
* Blink detection for mouse click
* Lightweight implementation with minimal dependencies

---

## Installation

Install required libraries:

```bash
pip install mediapipe
pip install opencv-contrib-python
pip install pyautogui
```

---

## Dependencies Explained

| Library   | Purpose                                     |
| --------- | ------------------------------------------- |
| OpenCV    | Captures webcam frames and renders visuals  |
| MediaPipe | Detects face landmarks including eye points |
| PyAutoGUI | Controls mouse cursor and clicks            |

---

## Code Walkthrough

### 1. Import Libraries

```python
import cv2
import mediapipe as mp
import pyautogui
```

Loads required modules for vision, tracking, and automation.

---

### 2. Initialize Webcam

```python
cam = cv2.VideoCapture(0)
```

* Opens default camera (index 0).
* Streams frames continuously.

---

### 3. Initialize Face Mesh Model

```python
face_mesh = mp.solutions.face_mesh.FaceMesh(refine_landmarks=True)
```

* Loads MediaPipe face mesh detector.
* `refine_landmarks=True` enables iris tracking for precise eye positioning.

---

### 4. Screen Size Detection

```python
screen_w, screen_h = pyautogui.size()
```

Retrieves monitor resolution to map eye coordinates → screen coordinates.

---

### 5. Main Processing Loop

```python
while True:
```

Runs continuously until user exits.

---

### 6. Frame Capture & Preprocessing

```python
_, frame = cam.read()
frame = cv2.flip(frame, 1)
rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
```

Steps:

1. Capture frame from camera
2. Flip horizontally for mirror effect
3. Convert color space because MediaPipe expects RGB

---

### 7. Face Landmark Detection

```python
output = face_mesh.process(rgb_frame)
landmark_points = output.multi_face_landmarks
```

Returns coordinates of 468+ facial points if a face is detected.

---

### 8. Cursor Control Using Eye Landmark

```python
for id in range(474, 478):
```

These indices correspond to **iris landmarks**.

Coordinates scaled to frame size:

```python
x = int(landmarks[id].x * frame_w)
y = int(landmarks[id].y * frame_h)
```

Mouse movement mapping:

```python
screen_x = screen_w * landmarks[id].x
screen_y = screen_h * landmarks[id].y
pyautogui.moveTo(screen_x, screen_y)
```

---

### 9. Blink Detection (Click Action)

```python
left = [landmarks[145], landmarks[159]]
```

These two points represent upper and lower eyelid.

Blink detection:

```python
if (left[0].y - left[1].y) < 0.004:
    pyautogui.click()
    pyautogui.sleep(1)
```

Logic:

* When eyelids get very close → blink detected
* Mouse click triggered
* 1 second delay prevents multiple clicks

---

### 10. Display Output Window

```python
cv2.imshow('Eye Controlled Mouse', frame)
```

Shows camera feed with landmarks drawn.

Exit condition:

```python
if cv2.waitKey(1) == ord('q'):
    break
```

---

### 11. Cleanup

```python
cam.release()
cv2.destroyAllWindows()
```

Releases camera and closes display windows.

---

## Controls

| Action      | Gesture            |
| ----------- | ------------------ |
| Move Cursor | Move eye direction |
| Left Click  | Blink              |

---

## System Flow

```
Camera → Frame Capture → Face Mesh Detection → Eye Landmark Extraction → Cursor Mapping → Blink Detection → Click Action
```

---

## Limitations

* Sensitive to lighting conditions
* Requires stable head position
* Blink threshold may vary per user
* Performance depends on camera FPS

---

## Possible Improvements

* Calibration stage for personalized accuracy
* Smoothing filter for cursor movement
* Multi-monitor support
* Right-click gesture detection
* Head pose compensation

---

## Applications

* Assistive technology for physically impaired users
* Hands-free computer interaction
* Experimental human-computer interfaces
* Gaming and AR interaction systems

---

## Author Notes

This implementation demonstrates a foundational approach to gaze-driven input systems. For production use, incorporate calibration, filtering, and predictive tracking to improve robustness.
