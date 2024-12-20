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
        self.cap = cv2.VideoCapture(0)
        self.cursor = (0, 0)
        self.state = 'movement'
        self.__state = 'movement'
        self.last_time = -1

    def put_text(self, frame, text: str) -> None:
        cv2.putText(
            frame,
            text,
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1, (0, 255, 0), 2
        )

    def dist(self, point1: tuple, point2: tuple) -> float:
        return math.hypot(point1[0] - point2[0], point1[1] - point2[1])

    def normalize_coordinates(self, x: float, y: float) -> tuple:
        screen_x = int(x * self.width)
        screen_y = int(y * self.height)
        return screen_x, screen_y

    def update_fingers_indexes(self) -> None:
        self.middle_finger_tip = self.hand_landmarks.landmark[
            self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP
        ]
        self.middle_finger_tip = self.normalize_coordinates(
            self.middle_finger_tip.x, self.middle_finger_tip.y
        )
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
            if self.__state != 'drag' and self.__state != 'click':
                self.__state = 'click'
                self.last_time = time.time()
        elif self.are_fingers_pinned(
            [self.index_finger_tip, self.middle_finger_tip], threshold=45
        ):
            self.state = 'scroll'
        else:
            if self.__state == 'click':
                self.state = 'click'
            else:
                self.default_state()

    def start_video(self, debug: bool = False) -> None:
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
                        self.put_text(frame, "Click!")

                    case 'drag':
                        self.system_controller.start_dragging_object()
                        self.put_text(frame, "Dragging!")

                    case 'scroll':
                        self.system_controller.scroll(
                            0.1 * (self.cursor[1] - self.index_finger_tip[1])
                        )
                        self.put_text(frame, "Scrolling!")

                    case 'movement':
                        self.system_controller.stop_dragging_object()

                if self.state != 'scroll':
                    if self.dist(self.cursor, self.index_finger_tip) > 3:
                        self.cursor = self.index_finger_tip
                        self.system_controller.set_position_cursor(
                            self.cursor[0], self.cursor[1]
                        )

                self.mp_draw.draw_landmarks(
                    frame, self.hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )

            if debug:
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

