from typing import Literal, NoReturn

from PySide6.QtWidgets import QApplication, QGraphicsView, QWidget

from engram.gui.filled_button import FillMode, W_FilledButton  # TODO  Relative import


class Key:  # HACK Key class shouldn't be here
    hand: Literal["L", "R"]
    finger: Literal[0, 1, 2, 3, 4]
    h_dist: int  # h_dist > 0 ⇔ inward
    v_dist: int  # v_dist > 0 ⇔ upward

    # TEST: Key.__init__(…)
    def __init__(self, finger: str, h_dist: int, v_dist: int) -> None:
        finger = finger.upper()
        try:
            self.hand = finger[0]  # type: ignore
            assert self.hand in "LR"
            self.finger = "T1234".index(finger[1])  # type: ignore
        except (ValueError, AssertionError):
            self.__raise_invalid_finger(finger)
        self.h_dist = h_dist
        self.v_dist = v_dist

    @staticmethod
    def __raise_invalid_finger(finger: str) -> NoReturn:
        raise ValueError(f"Invalid finger: {finger}")

    # TEST: Key.__str__()
    def __str__(self) -> str:
        return f"{self.hand}{self.finger or 'T'}{self.__movement()}"

    def __movement(self) -> str:
        movement = ""
        y = self.v_dist
        x = self.h_dist
        if self.hand == "R":
            x *= -1
        while y or x:
            x_sign = self.__sign(x)
            y_sign = self.__sign(y)
            movement += {
                (-1, +1): "↖", (0, +1): "↑", (+1, +1): "↗",
                (-1,  0): "←", (0,  0): "●", (+1,  0): "→",
                (-1, -1): "↙", (0, -1): "↓", (+1, -1): "↘",
            }[x_sign, y_sign]  # fmt: skip
            x -= x_sign
            y -= y_sign
        return movement or "●"

    @staticmethod
    def __sign(x: int) -> Literal[-1, 0, 1]:
        if x < 0:
            return -1
        if x > 0:
            return 1
        return 0


class W_Key(W_FilledButton):
    __x: float
    __y: float

    def __init__(
        self,
        x: float,
        y: float,
        parent: QWidget | None = None,
        /,
        mode: FillMode = FillMode.CenterSize,
    ) -> None:
        super().__init__(parent, mode=mode)
        self.__x = x
        self.__y = y

    def setSize(self, size: int) -> None:
        self.setGeometry(round(self.__x * size), round(self.__y * size), size, size)


class W_Keyboard(QGraphicsView):
    keys: dict[Key, W_Key]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.keys = {}
        # HACK Keyboard directly implemented as Sofle
        y_ = [0.6062, 0.6062, 0.1347, 0.0, 0.1347, 0.2642]
        x_ = list(range(6))
        h_dist_ = [-1, 0, 0, 0, 0, 1]
        finger_ = [str(f) for f in (4, 4, 3, 2, 1, 1)]
        v_dist_ = [2, 1, 0, -1]
        for hand in "LR":
            if hand == "R":
                x_ = [x + 6 + 3.7979 for x in x_]
                y_.reverse()
                h_dist_.reverse()
                finger_.reverse()
            for row, v_dist in enumerate(v_dist_):
                for x, y, h_dist, finger in zip(x_, y_, h_dist_, finger_):
                    y += row
                    key = Key(hand + finger, h_dist, v_dist)
                    self.__add_key(key, x, y)
        h_dist_ = [-3, -2, -1, 0, 1]
        x_ = [2.0, 3.0, 4.0, 5.17, 6.27]
        y_ = [4.1347, 4.0, 4.1347, 4.404, 4.664]
        for hand in "LR":
            if hand == "R":
                x_ = [11 + 3.7979 - x for x in x_]
                x_.reverse()
                y_.reverse()
                h_dist_.reverse()
            for x, y, h_dist in zip(x_, y_, h_dist_):
                key = Key(hand + "T", h_dist, 0)
                self.__add_key(key, x, y)
        self.__compute_geometry()

    def __add_key(self, key: Key, x: float, y: float) -> None:
        self.keys[key] = W_Key(x, y, self)

    def __compute_geometry(self) -> None:
        # HACK Fixed size
        key_size = 70
        self.setFixedSize(
            round((12 + 3.7979) * key_size), round(5.664 * key_size)
        )  # HACK Sizing based on Sofle geometry
        for key in self.keys.values():
            key.setSize(key_size)


if __name__ == "__main__":
    import sys

    from engram.gui.esc_window import EscapableWindow

    app = QApplication(sys.argv)
    window = EscapableWindow()
    window.setCentralWidget(W_Keyboard())

    window.show()
    sys.exit(app.exec())
