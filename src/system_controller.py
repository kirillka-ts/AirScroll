from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController
from math import hypot
import time


class SystemController:
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

    @property
    def x(self) -> float:
        return self.mouse.position[0]

    @x.setter
    def x(self, x: float) -> None:
        self.set_position_cursor(x, self.y)

    @property
    def y(self) -> float:
        return self.mouse.position[1]

    @y.setter
    def y(self, y: float) -> None:
        self.set_position_cursor(self.x, y)

    def move_cursor(self, x: float, y: float) -> None:
        lengh = int(hypot(self.x, self.y))
        x_change = x / lengh
        y_change = y / lengh
        for _ in range(lengh):
            self.mouse.move(x_change, y_change)
            time.sleep(0.0015)

    def set_position_cursor(self, x: float, y: float) -> None:
        self.move_cursor(x - self.x, y - self.y)

    def click(self) -> None:
        self.mouse.click(Button.left)

    def scroll(self, y: float, x: float = 0) -> None:
        y = -y
        x = -x
        self.mouse.scroll(x, y)

    def __hold_click(func):
        def wrapper(self, *args, **kwargs):
            self.mouse.press(Button.left)
            result = func(self, *args, **kwargs)
            self.mouse.release(Button.left)
            return result
        return wrapper

    @__hold_click
    def drag_object(self, x: float, y: float) -> None:
        self.move_cursor(x, y)


if __name__ == "__main__":
    pass
