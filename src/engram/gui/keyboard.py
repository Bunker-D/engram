from math import sqrt
from typing import Literal, NoReturn

import PySide6.QtCore as QC  # noqa: F401
import PySide6.QtGui as QG  # noqa: F401
import PySide6.QtWidgets as QW  # noqa: F401
from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPaintEvent
from PySide6.QtWidgets import QApplication


def main():
    print("Hello from kbgui!")


# class W_Test(QWidget, Ui_Form):
#     def __init__(self) -> None:
#         super().__init__()
#         self.setupUi(self)


class Key:
    hand: Literal["L", "R"]
    finger: Literal[0, 1, 2, 3, 4]
    h_dist: int  # h_dist > 0 ⇔ inward
    v_dist: int  # v_dist > 0 ⇔ upward

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

    def __post_init__(self):
        pass

    def __str__(self) -> str:
        return f"{self.hand}{self.finger or 'T'}{self.movement()}"

    def movement(self) -> str:
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


class W_Key(QW.QPushButton):
    key: Key
    fill: float
    __center_fill: bool = False
    __padding: int = 3
    __corner_radius: int = 5

    def __init__(self, key: Key, parent: QW.QWidget | None = None) -> None:
        super().__init__(str(key), parent=parent)
        self.key = key
        self.fill = 0
        self.setCheckable(True)
        self.underMouse

    def paintEvent(self, arg__1: QPaintEvent) -> None:
        super().paintEvent(arg__1)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Outer rounded rectangle
        self.__draw_fill(painter)

        # # Inner rounded rectangle
        # inner_rect = QRectF(30, 20, self.width() - 60, self.height() - 40)
        # painter.setBrush(QBrush(QColor(200, 100, 150)))
        # painter.drawRoundedRect(inner_rect, 10, 10)

    def __draw_fill(self, painter: QPainter) -> None:
        if not self.fill:
            return
        fill_rect = (
            self.__center_fill_rect()
            if self.__center_fill
            else self.__bottom_fill_rect()
        )

        app = QApplication.instance()
        assert app is not None
        palette = QG.QPalette()
        painter.setBrush(
            palette.color(QG.QPalette.ColorGroup.Active, QG.QPalette.ColorRole.Accent)
            # TODO Go through all QPalette.ColorGroup & QPalette.ColorRole to know what's what
        )
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(fill_rect, self.__corner_radius, self.__corner_radius)
        painter.end()

    def __center_fill_rect(self) -> QC.QRectF:
        a = sqrt(self.fill)
        w = a * (self.width() - 2 * self.__padding)
        h = a * (self.height() - 2 * self.__padding)
        return QC.QRectF((self.width() - w) / 2, (self.height() - h) / 2, w, h)

    def __bottom_fill_rect(self) -> QC.QRectF:
        h = self.fill * (self.height() - 2 * self.__padding)
        return QC.QRectF(
            self.__padding,
            self.height() - self.__padding - h,
            self.width() - 2 * self.__padding,
            h,
        )


class W_Keyboard(QW.QGraphicsView):
    def __init__(self, *kargs, **kwargs) -> None:
        super().__init__(*kargs, **kwargs)

        key_size = 100

        # Sofle
        self.setFixedSize(round((12 + 3.7979) * key_size), round(5.664 * key_size))
        y_ = [0.6062, 0.6062, 0.1347, 0.0, 0.1347, 0.2642]
        x_ = list(range(6))
        h_dist_ = [-1, 0, 0, 0, 0, 1]
        finger_ = [str(f) for f in (4, 4, 3, 2, 1, 1)]
        v_dist_ = [2, 1, 0, -1]
        i = 0.0  # hack
        for hand in "LR":
            if hand == "R":
                x_ = [x + 6 + 3.7979 for x in x_]
                y_.reverse()
                h_dist_.reverse()
                finger_.reverse()
            for row, v_dist in enumerate(v_dist_):
                for x, y, h_dist, finger in zip(x_, y_, h_dist_, finger_):
                    y += row
                    key = W_Key(Key(hand + finger, h_dist, v_dist), self)
                    key.setGeometry(
                        round(x * key_size), round(y * key_size), key_size, key_size
                    )
                    if i < 0.99:  # hack
                        if h_dist < 0:  # hack
                            continue  # hack
                        i += 0.1  # hack
                        key.fill = i  # hack
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
                key = W_Key(Key(hand + "T", h_dist, 0), self)
                key.setGeometry(
                    round(x * key_size), round(y * key_size), key_size, key_size
                )


d = [-0.4715, -0.1347, 0.1347, 0.1295]
y = [0.0]
for dy in d:
    y.append(y[-1] + dy)
dy = min(y)
y = [y - dy for y in y]
print(y)


# class W_Keyboard_layout(QW.QWidget):
#     keys: list[W_Key]

#     def __init__(self) -> None:
#         super().__init__()
#         self.keys = []
#         layout = QW.QHBoxLayout(self)
#         for n in range(1, 4):
#             column = QW.QVBoxLayout()
#             layout.addLayout(column)
#             for i in range(n):
#                 key = W_Key(f"{n} {i}", self)
#                 column.addWidget(key)
#         column = QW.QVBoxLayout()
#         layout.addLayout(column)
#         for i in "QWE":
#             btn = QW.QPushButton(f"Button &{i}")
#             btn.setCheckable(True)
#             btn.clicked.connect(eval(f"lambda: print('{i}')"))
#             column.addWidget(btn)
#             if i == "W":
#                 btn.setFocus()


class EscapableWindow(QW.QMainWindow):
    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = EscapableWindow()
    window.setCentralWidget(W_Keyboard())

    window.show()
    sys.exit(app.exec())
