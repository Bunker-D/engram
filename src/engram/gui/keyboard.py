from math import ceil, cos, radians, sin
from typing import Literal, NoReturn

from PySide6.QtGui import QTransform
from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView, QWidget

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
    __w: float
    __h: float
    __a: float

    def __init__(
        self,
        x: float,
        y: float,
        w: float = 1,
        h: float = 1,
        a: float = 0,
        scene: QGraphicsScene | None = None,
        parent: QWidget | None = None,
        mode: FillMode = FillMode.CenterSize,
    ) -> None:
        super().__init__(parent=parent, mode=mode)
        if scene:
            scene.addWidget(self)
        self.setPosition(x, y, w, h, a)

    def setPosition(
        self, x: float, y: float, w: float = 1, h: float = 1, a: float = 0
    ) -> None:
        self.__x = x
        self.__y = y
        self.__w = w
        self.__h = h
        self.__a = a
        if not a:
            return
        self.__apply_a_rotation(a)
        self.__apply_a_translation(a)

    def __apply_a_rotation(self, a: float) -> None:
        proxy = self.graphicsProxyWidget()
        if proxy is None:
            raise AttributeError(
                "Cannot set an angle without being in a QGraphicsScene."
            )
        transform = QTransform()
        transform.rotate(a)
        proxy.setTransform(transform)

    def __apply_a_translation(self, a: float) -> None:
        c = cos(radians(a)) - 1
        s = sin(radians(a))
        self.__x -= (c * self.__w - s * self.__h) / 2
        self.__y -= (s * self.__w + c * self.__h) / 2

    def setSize(self, size: int) -> None:
        self.setGeometry(
            round(self.__x * size),
            round(self.__y * size),
            round(self.__w * size),
            round(self.__h * size),
        )


class W_Keyboard(QGraphicsView):
    keys: dict[Key, W_Key]

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.keys = {}
        self.__build_sofle()  # HACK Keyboard directly implemented as Sofle
        self.__compute_geometry()

    def __build_sofle(self) -> None:
        scene = QGraphicsScene(self)
        self.setScene(scene)

        x_ = [0, 1, 2, 3, 4, 5] * 4
        y_ = [0.6062, 0.6062, 0.1347, 0.0, 0.1347, 0.2642]
        y_ = [y + r for r in range(4) for y in y_]
        finger_ = [str(f) for f in (4, 4, 3, 2, 1, 1)] * 4
        h_dist_ = [-1, 0, 0, 0, 0, 1] * 4
        v_dist_ = [v for v in [2, 1, 0, -1] for _ in range(6)]

        x_ += [2, 3, 4, 5.15126, 6.25210]
        y_ += [4.1347, 4.0, 4.1347, 4.38605, 4.64655]
        finger_ += ["T"] * 5
        h_dist_ += [-3, -2, -1, 0, 1]
        v_dist_ += [0] * 5
        a_ = [0.0] * (len(x_) - 2) + [22.8, 29.7]
        w_ = [1] * len(x_)
        h_ = [1] * (len(x_) - 1) + [1.25]

        for hand in "LR":
            if hand == "R":
                x_ = [14.8 - x for x in x_]
                a_ = [-a for a in a_]
            for x, y, finger, h_dist, v_dist, a, w, h in zip(
                x_, y_, finger_, h_dist_, v_dist_, a_, w_, h_
            ):
                key = Key(hand + finger, h_dist, v_dist)
                w_key = W_Key(x, y, w, h, a, scene=scene)
                self.keys[key] = w_key

    def __compute_geometry(self) -> None:
        key_size = 70  # HACK Fixed size
        for key in self.keys.values():
            key.setSize(key_size)
        bounding_rect = self.scene().itemsBoundingRect()
        margin = 5
        bounding_rect.adjust(-margin, -margin, margin, margin)
        self.setFixedSize(ceil(bounding_rect.width()), ceil(bounding_rect.height()))


if __name__ == "__main__":
    import sys

    from engram.gui.esc_window import EscapableWindow

    app = QApplication(sys.argv)
    window = EscapableWindow()
    window.setCentralWidget(W_Keyboard())

    window.show()
    sys.exit(app.exec())
