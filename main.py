import cv2
import threading
import pystray
from PIL import Image, ImageDraw
from config import (
    GESTURE_HOLD_FRAMES, VOLUME_DEADBAND,
    MIN_PINCH_DIST, MAX_PINCH_DIST, SMOOTHING_WINDOW,
    PINCH_GATE_THRESHOLD, PINCH_ENTRY_FRAMES, PEACE_HOLD_FRAMES
)
from gesture_detector import GestureDetector
from tv_controller import TVController

LOCK_FRAMES = 30
stop_flag = threading.Event()


def create_tray_icon():
    img = Image.new("RGB", (64, 64), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)
    draw.ellipse((16, 16, 48, 48), fill=(0, 200, 100))
    icon = pystray.Icon(
        "GestureControl", img, "Gesture Control",
        menu=pystray.Menu(
            pystray.MenuItem("Quit", lambda icon, item: stop_flag.set())
        )
    )
    icon.run()


def main():
    tray_thread = threading.Thread(target=create_tray_icon, daemon=True)
    tray_thread.start()

    detector = GestureDetector(smoothing_window=SMOOTHING_WINDOW)
    controller = TVController()

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam.")
        return

    current_volume = 50
    last_sent_volume = -1
    fist_hold = 0
    palm_hold = 0
    muted = False
    playing = True

    was_pinching = False
    pinch_locked = False
    stable_frames = 0
    pinch_entry_frames = 0      # debounce: frames of continuous valid pinch
    pinch_state = "IDLE"
    gesture_label = "None"

    print("Running in background. Right-click tray icon to quit.")

    while not stop_flag.is_set():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        results = detector.process(frame)
        gesture_label = "None"

        if results.multi_hand_landmarks:
            hand = results.multi_hand_landmarks[0]
            lm = hand.landmark

            # --- Priority 1: fist (mute) ---
            if detector.is_fist(lm):
                pinch_entry_frames = 0
                was_pinching = False
                pinch_state = "IDLE"
                palm_hold = 0
                fist_hold += 1
                gesture_label = f"FIST ({fist_hold}/{GESTURE_HOLD_FRAMES})"
                if fist_hold == GESTURE_HOLD_FRAMES:
                    muted = controller.toggle_mute()
                    fist_hold = 0

            # --- Priority 2: open palm (play/pause) ---
            elif detector.is_two_fingers_up(lm):
                pinch_entry_frames = 0
                was_pinching = False
                pinch_state = "IDLE"
                fist_hold = 0
                palm_hold += 1
                gesture_label = f"PEACE ({palm_hold}/{PEACE_HOLD_FRAMES})"
                if palm_hold == PEACE_HOLD_FRAMES:
                    playing = controller.toggle_play_pause()
                    palm_hold = 0

            # --- Priority 3: pinch (volume) ---
            else:
                fist_hold = 0
                palm_hold = 0

                is_pinching, dist, p1, p2 = detector.get_pinch_state(
                    lm, frame.shape, PINCH_GATE_THRESHOLD
                )
                valid_pinch = is_pinching

                if valid_pinch:
                    pinch_entry_frames += 1

                    # Must hold for PINCH_ENTRY_FRAMES before activating
                    if pinch_entry_frames < PINCH_ENTRY_FRAMES:
                        gesture_label = f"PINCH? ({pinch_entry_frames}/{PINCH_ENTRY_FRAMES})"
                        was_pinching = False  # not yet confirmed

                    else:
                        if not was_pinching:
                            pinch_locked = False
                            stable_frames = 0
                            was_pinching = True

                        if not pinch_locked:
                            new_volume = detector.distance_to_volume(
                                dist, MIN_PINCH_DIST, MAX_PINCH_DIST
                            )
                            if abs(new_volume - current_volume) <= VOLUME_DEADBAND:
                                stable_frames += 1
                            else:
                                stable_frames = 0
                                current_volume = new_volume

                            if stable_frames >= LOCK_FRAMES:
                                pinch_locked = True
                                pinch_state = "LOCKED"
                                print(f"\nVolume locked at {current_volume}%")
                            else:
                                pinch_state = "ACTIVE"
                                if abs(current_volume - last_sent_volume) > VOLUME_DEADBAND:
                                    controller.set_volume(current_volume)
                                    last_sent_volume = current_volume

                            gesture_label = f"PINCH {current_volume}%"
                        else:
                            gesture_label = f"LOCKED @ {current_volume}%"
                            pinch_state = "LOCKED"

                else:
                    pinch_entry_frames = 0
                    was_pinching = False
                    pinch_state = "IDLE"
                    gesture_label = "None"

        else:
            was_pinching = False
            pinch_entry_frames = 0
            fist_hold = 0
            palm_hold = 0
            pinch_state = "IDLE"
            gesture_label = "No hand"

        print(f"\r{pinch_state:<8} | Vol: {current_volume:>3}% | {gesture_label:<30}", end="", flush=True)

    cap.release()
    controller.disconnect()
    print("\nStopped.")


if __name__ == "__main__":
    main()