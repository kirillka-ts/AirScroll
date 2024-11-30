import cv2
import mediapipe as mp
from system_controller import SystemController
import time
import math


class HandProcessor:
    def __init__(self) -> None:
        self.system_controller = SystemController()
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False, max_num_hands=1,
            min_detection_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.cap = cv2.VideoCapture(1)
        self.state = 'movement'
        self.__state = 'movement'
        self.last_time = -1

    def dist(self, point1: tuple, point2: tuple) -> float:
        return math.hypot(point1[0] - point2[0], point1[1] - point2[1])
        
    def normalize_coordinates(self, x: float, y: float) -> tuple:
        screen_x = int(x * self.width)
        screen_y = int(y * self.height)
        return screen_x, screen_y

    def update_fingers_indexes(self) -> None:
        self.index_finger_tip = self.hand_landmarks.landmark[
            self.mp_hands.HandLandmark.INDEX_FINGER_TIP
        ]
        self.index_finger_tip = self.normalize_coordinates(
            self.index_finger_tip.x, self.index_finger_tip.y
        )
        self.thumb_tip = self.hand_landmarks.landmark[
            self.mp_hands.HandLandmark.THUMB_TIP
        ]
        self.thumb_tip = self.normalize_coordinates(
            self.thumb_tip.x, self.thumb_tip.y
        )

    def are_fingers_pinned(self, fingers: [list], threshold=40) -> bool:
        for i in range(len(fingers) - 1):
            for j in range(i+1, len(fingers)):
                x1, y1 = fingers[i]
                x2, y2 = fingers[j]
                distance = self.dist((x1, y1), (x2, y2))
                if distance > threshold:
                    return False
        return True

    def default_state(self) -> None:
        self.state = 'movement'
        self.__state = 'movement'

    def update_state(self) -> None:
        if self.are_fingers_pinned([self.index_finger_tip, self.thumb_tip]):
            if self.__state == 'click':
                if time.time() - self.last_time > 0.3:
                    self.state = 'drag'
                    self.__state = 'drag'
                    # self.last_time = time.time()
            if self.__state != 'drag' and self.__state != 'click':
                self.__state = 'click'
                self.last_time = time.time()
        else:
            if self.__state == 'click':
                self.state = 'click'
            else:
                self.default_state()

    def start_video(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            hand_results = self.hands.process(rgb_frame)
            self.height, self.width, _ = frame.shape

            if hand_results.multi_hand_landmarks:
                self.hand_landmarks = hand_results.multi_hand_landmarks[0]

                self.update_fingers_indexes()
                cv2.circle(frame, self.index_finger_tip, 10, (0, 255, 0), -1)

                self.update_state()

                match self.state:
                    case 'click':
                        self.system_controller.click()
                        self.default_state()
                        cv2.putText(frame, "Click!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    case 'drag':
                        self.system_controller.start_dragging_object()
                        cv2.putText(frame, "Dragging!", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    case 'movement':
                        self.system_controller.stop_dragging_object()
 
                if True:
                    self.system_controller.set_position_cursor(
                        self.index_finger_tip[0], self.index_finger_tip[1]
                    )

                # self.mp_draw.draw_landmarks(frame, self.hands, self.mp_hands.HAND_CONNECTIONS)

            cv2.imshow("Hand Tracking as Trackpad", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()

def main():
    hand_processor = HandProcessor()
    hand_processor.start_video()

if __name__ == "__main__":
    main()
