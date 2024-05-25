from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QLabel, QTabWidget, QWidget

from .widgetbuilder import SMINMIN


class WidgetStorage():
    """
    Stores Widgets
    """
    def __init__(self):
        self.splash_tabber: QTabWidget
        self.loading_label: QLabel


class ImageLabel(QWidget):
    """
    Label displaying image that resizes according to its parents width while preserving aspect
    ratio.
    """
    def __init__(self, path: str, aspect_ratio: tuple[int, int], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._w, self._h = aspect_ratio
        self.setPixmap(QPixmap(path))
        self.setSizePolicy(SMINMIN)
        self.setMinimumHeight(10)  # forces visibility

    def setPixmap(self, p):
        self.p = p
        self.update()

    def paintEvent(self, event):
        if not self.p.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            w = int(self.rect().width())
            h = int(w * self._h / self._w)
            rect = QRect(0, 0, w, h)
            painter.drawPixmap(rect, self.p)
            self.setMaximumHeight(h)
            self.setMinimumHeight(h)
