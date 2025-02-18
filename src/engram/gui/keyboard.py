from math import ceil, cos, radians, sin
from typing import Callable

from PySide6.QtGui import QTransform
from PySide6.QtWidgets import (
    QApplication,
    QGraphicsScene,
    QGraphicsView,
    QVBoxLayout,
    QWidget,
)

from engram.gui.filled_button import W_FilledButton, W_FillMode  # TODO  Relative import
from engram.scoring import Key


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
    ) -> None:
        super().__init__(parent=parent)
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
    __key_values: Callable[[Key], float] | None
    __pair_values: Callable[[Key, Key], float] | None
    __active_key: Key | None

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.keys = {}
        self.__build_sofle()  # HACK Keyboard directly implemented as Sofle
        self.__set_click_actions()
        self.__compute_geometry()
        self.__key_values = None  # TODO Initial value functions?
        self.__pair_values = None
        self.__active_key = None

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

    def __set_click_actions(self) -> None:
        for key, key_btn in self.keys.items():
            key_btn.clicked.connect(lambda _, key=key: self.__toggle_key(key))

    def __toggle_key(self, key: Key) -> None:
        was_active = key is self.__active_key
        self.__deactivate_key()
        if not was_active:
            self.__activate_key(key)
        self.update_shown_values()

    def __deactivate_key(self) -> None:
        if not self.__active_key:
            return
        self.keys[self.__active_key].setChecked(False)
        self.__active_key = None

    def __activate_key(self, key: Key) -> None:
        self.keys[key].setChecked(True)
        self.__active_key = key

    def set_values(
        self,
        for_keys: Callable[[Key], float],
        for_pairs: Callable[[Key, Key], float] | None = None,
    ) -> None:
        self.__key_values = for_keys
        self.__pair_values = for_pairs
        self.update_shown_values()

    def update_shown_values(self) -> None:
        val_fun: Callable[[Key], float]
        if self.__active_key:
            if self.__pair_values:
                val_fun = lambda key: self.__pair_values(self.__active_key, key)  # type:ignore
            else:
                val_fun = lambda _: 0
        else:
            val_fun = self.__key_values or (lambda _: 0)
        for key, key_btn in self.keys.items():
            key_btn.fill = val_fun(key)  # HACK Ignores rectangular keys
            key_btn.update()


if __name__ == "__main__":
    import sys
    from math import sqrt

    from engram.gui.esc_window import EscapableWindow

    app = QApplication(sys.argv)

    class MainWidget(QWidget):
        keyboard: W_Keyboard

        def __init__(self) -> None:
            super().__init__()
            layout = QVBoxLayout(self)
            self.keyboard = W_Keyboard()
            layout.addWidget(self.keyboard)
            layout.addWidget(W_FillMode())

    window = EscapableWindow()
    main_widget = MainWidget()
    window.setCentralWidget(main_widget)

    keyboard = main_widget.keyboard
    keyboard.set_values(
        lambda k: (1 + abs(k.dx) + abs(k.dy)) / 5,
        lambda k, h: sqrt((k.finger - k.dx - h.finger + h.dx) ** 2 + (k.dy - h.dy) ** 2)
        / 7
        if k.hand == h.hand
        else 0,
    )

    window.show()
    sys.exit(app.exec())
