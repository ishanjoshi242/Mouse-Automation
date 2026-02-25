import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time
import sys
import traceback

# ================== CONFIG ==================
CAMERA_INDEX = 0
SMOOTHING_FACTOR = 5
BLINK_THRESHOLD = 0.004
CLICK_COOLDOWN = 1.0
DOUBLE_BLINK_WINDOW = 1.0
FRAME_REDUCTION = 50  # reduce frame area for stable mapping
# ============================================

class EyeMouseController:
    def __init__(self):
        try:
            self.cam = cv2.VideoCapture(CAMERA_INDEX)
            if not self.cam.isOpened():
                raise RuntimeError("Camera could not be opened.")

            self.face_mesh = mp.solutions.face_mesh.FaceMesh(
                refine_landmarks=True,
                max_num_faces=1
            )

            self.screen_w, self.screen_h = pyautogui.size()
            self.prev_x, self.prev_y = 0, 0

            self.last_click_time = 0
            self.last_blink_time = 0

            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0

            print("[INFO] Eye Mouse Controller initialized.")

        except Exception as e:
            print("[ERROR] Initialization failed:", str(e))
            traceback.print_exc()
            sys.exit(1)

    def smooth_move(self, x, y):
        curr_x = self.prev_x + (x - self.prev_x) / SMOOTHING_FACTOR
        curr_y = self.prev_y + (y - self.prev_y) / SMOOTHING_FACTOR
        pyautogui.moveTo(curr_x, curr_y)
        self.prev_x, self.prev_y = curr_x, curr_y

    def detect_blink(self, landmarks):
        left = [landmarks[145], landmarks[159]]
        return (left[0].y - left[1].y) < BLINK_THRESHOLD

    def run(self):
        try:
            while True:
                success, frame = self.cam.read()
                if not success:
                    print("[WARNING] Frame not captured.")
                    continue

                frame = cv2.flip(frame, 1)
                frame_h, frame_w, _ = frame.shape

                # Reduce working frame area to avoid edge instability
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                output = self.face_mesh.process(rgb_frame)

                if output.multi_face_landmarks:
                    landmarks = output.multi_face_landmarks[0].landmark

                    # -------- Cursor Control --------
                    iris_points = landmarks[474:478]
                    iris = iris_points[1]  # stable center

                    x = int(iris.x * frame_w)
                    y = int(iris.y * frame_h)

                    # Map camera coords to screen coords
                    screen_x = np.interp(x, (FRAME_REDUCTION, frame_w - FRAME_REDUCTION), (0, self.screen_w))
                    screen_y = np.interp(y, (FRAME_REDUCTION, frame_h - FRAME_REDUCTION), (0, self.screen_h))

                    self.smooth_move(screen_x, screen_y)

                    cv2.circle(frame, (x, y), 3, (0, 255, 0), -1)

                    # -------- Blink Detection --------
                    if self.detect_blink(landmarks):
                        current_time = time.time()

                        if current_time - self.last_click_time > CLICK_COOLDOWN:
                            pyautogui.click()
                            print("[INFO] Single Click Triggered")

                            # Double blink detection
                            if current_time - self.last_blink_time < DOUBLE_BLINK_WINDOW:
                                pyautogui.hotkey('ctrl', 'w')
                                print("[INFO] Double Blink - Ctrl+W Triggered")

                            self.last_blink_time = current_time
                            self.last_click_time = current_time

                cv2.imshow("Eye Controlled Mouse", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            print("\n[INFO] Interrupted by user.")

        except Exception as e:
            print("[ERROR] Runtime error:", str(e))
            traceback.print_exc()

        finally:
            self.cleanup()

    def cleanup(self):
        try:
            self.cam.release()
            cv2.destroyAllWindows()
            print("[INFO] Resources released successfully.")
        except Exception as e:
            print("[ERROR] Cleanup failed:", str(e))


if __name__ == "__main__":
    controller = EyeMouseController()
    controller.run()
