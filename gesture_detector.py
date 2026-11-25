import cv2
import mediapipe as mp
import numpy as np
from collections import deque
import math


class GestureDetector:
    def __init__(self, smoothing_window=5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.distance_history = deque(maxlen=smoothing_window)

    def process(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return self.hands.process(rgb)

    def draw(self, frame, hand_landmarks):
        self.mp_draw.draw_landmarks(
            frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
        )

    def get_pinch_distance(self, landmarks, frame_shape):
        h, w = frame_shape[:2]
        thumb = landmarks[4]
        index = landmarks[8]
        x1, y1 = int(thumb.x * w), int(thumb.y * h)
        x2, y2 = int(index.x * w), int(index.y * h)

        raw_dist = math.hypot(x2 - x1, y2 - y1)
        self.distance_history.append(raw_dist)
        smoothed = float(np.mean(self.distance_history))

        return smoothed, (x1, y1), (x2, y2)

    def get_pinch_state(self, landmarks, frame_shape, threshold):
        dist, p1, p2 = self.get_pinch_distance(landmarks, frame_shape)
        is_active = dist < threshold
        return is_active, dist, p1, p2

    def distance_to_volume(self, distance, min_dist, max_dist):
        vol = np.interp(distance, [min_dist, max_dist], [0, 100])
        return int(np.clip(vol, 0, 100))

    def is_fist(self, landmarks):
        """All five fingers curled — four fingers tips below PIPs, thumb tip below its IP joint."""
        finger_tips = [8, 12, 16, 20]
        finger_pips = [6, 10, 14, 18]
        fingers_curled = all(
            landmarks[t].y > landmarks[p].y
            for t, p in zip(finger_tips, finger_pips)
        )
        thumb_curled = landmarks[4].y > landmarks[3].y  # tip below thumb IP knuckle
        return fingers_curled and thumb_curled

    def is_open_palm(self, landmarks):
        tips = [8, 12, 16, 20]
        mcps = [5,  9, 13, 17]
        return all(landmarks[t].y < landmarks[m].y for t, m in zip(tips, mcps))

    def is_valid_pinch(self, landmarks):
        # Other fingers (middle, ring, pinky) extended
        other_tips = [12, 16, 20]
        other_pips = [10, 14, 18]
        extended = sum(
            1 for t, p in zip(other_tips, other_pips)
            if landmarks[t].y < landmarks[p].y
        )
        # Index must be bent toward thumb — tip (8) below PIP (6)
        # Open palm has index pointing straight up, so this filters it out
        index_bent = landmarks[8].y > landmarks[6].y
        return extended >= 2 and index_bent

    def is_two_fingers_up(self, landmarks):
        """Peace sign: index and middle extended, ring and pinky curled."""
        index_up  = landmarks[8].y  < landmarks[6].y
        middle_up = landmarks[12].y < landmarks[10].y
        ring_down = landmarks[16].y > landmarks[14].y
        pinky_down = landmarks[20].y > landmarks[18].y
        return index_up and middle_up and ring_down and pinky_down