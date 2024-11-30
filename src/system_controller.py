from pynput.mouse import Button, Controller as MouseController
from pynput.keyboard import Controller as KeyboardController


class SystemController:
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.left_button_pressed = False

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
        self.mouse.move(x, y)

    def set_position_cursor(self, x: float, y: float) -> None:
        self.mouse.position = (x, y)

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

    def start_dragging_object(self) -> None:
        if not self.left_button_pressed:
            self.mouse.press(Button.left)
            self.left_button_pressed = True

    def stop_dragging_object(self) -> None:
        self.mouse.release(Button.left)
        self.left_button_pressed = False


if __name__ == "__main__":
    pass
