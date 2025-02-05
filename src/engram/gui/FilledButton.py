from enum import Enum
from math import sqrt

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPalette
from PySide6.QtWidgets import QPushButton


class FilledButton(QPushButton):
    fill: float
    mode: "FilledButton.Mode"  # TODO ultimately private and static

    __corner_radius: int = 5
    __padding: int = 2

    def __init__(
        self,
        mode: "FilledButton.Mode | None" = None,
    ) -> None:  # TODO mode not in args
        super().__init__()
        self.fill = 0
        self.mode = mode if mode else self.Mode.CenterSize
        self.setCheckable(True)
        self.setFixedSize(70, 70)

    def paintEvent(self, arg__1: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        if self.isChecked():
            rect = self.rect()
            painter.setBrush(self.__color_selection())
            cr = self.__corner_radius + self.__padding
            painter.drawRoundedRect(rect, cr, cr)
        rect = self.__rect()
        painter.setBrush(self.__color_background())
        cr = self.__corner_radius
        painter.drawRoundedRect(rect, cr, cr)
        rect = self.__fill_rect()
        if rect:
            painter.setBrush(self.__color_fill())
            cr = 10000 if self.mode.circle() else self.__corner_radius
            painter.drawRoundedRect(rect, cr, cr)
        if self.underMouse():
            color = self.__color_selection()
            color.setAlpha(40)
            painter.setBrush(color)
            cr = self.__corner_radius
            painter.drawRoundedRect(self.__rect(), cr, cr)

    def __rect(self) -> QRectF:
        rect = QRectF(self.rect())
        d = self.__padding
        rect.adjust(d, d, -d, -d)
        return rect

    def __fill_rect(self) -> QRectF | None:
        if not self.fill:
            return None
        rect = self.__rect()
        if self.fill == 1:
            return rect
        a = sqrt(self.fill) if self.mode.sqrt_cut() else self.fill
        a = 1 - a
        s = self.mode._start_cut()
        if self.mode.horizontal_cut():
            d = rect.width() * a
            rect.adjust(d * s, 0, -d * (1 - s), 0)
        if self.mode.vertical_cut():
            d = rect.height() * a
            rect.adjust(0, d * s, 0, -d * (1 - s))
        return rect

    @staticmethod
    def __color_fill() -> QColor:
        return QPalette().color(QPalette.ColorGroup.Active, QPalette.ColorRole.Accent)

    @staticmethod
    def __color_background() -> QColor:
        return QPalette().color(QPalette.ColorGroup.Active, QPalette.ColorRole.Button)

    @staticmethod
    def __color_selection() -> QColor:
        return QPalette().color(QPalette.ColorGroup.Active, QPalette.ColorRole.Text)

    class Mode(Enum):
        Top = "0V"
        Bottom = "1V"
        Left = "0H"
        Right = "1H"
        CenterVertical = "CV"
        CenterHorizontal = "CH"
        CenterArea = "CA"
        CenterSize = "CS"
        CircleArea = "OA"
        CircleSize = "OS"

        def _start_cut(self) -> float:
            match self.value[0]:
                case "0":
                    return 0.0
                case "1":
                    return 1.0
                case "C":
                    return 0.5
                case "O":
                    return 0.5
            raise NotImplementedError

        def vertical_cut(self) -> bool:
            return self.value[1] in "VAS"

        def horizontal_cut(self) -> bool:
            return self.value[1] in "HAS"

        def sqrt_cut(self) -> bool:
            return self.value[1] == "A"

        def circle(self) -> bool:
            return self.value[0] == "O"
