from collections import namedtuple
from pathlib import Path
from typing import Callable

from PySide6.QtCore import QEvent, QPoint, QRect, QSize, Qt, QThread, Signal, Slot
from PySide6.QtGui import (
    QBrush, QColor, QCursor, QEnterEvent, QImage, QMouseEvent, QPainter, QPaintEvent, QPen)
from PySide6.QtWidgets import (
    QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QSizePolicy, QTabWidget, QVBoxLayout,
    QWidget)

from .constants import AHCENTER, ATOP, SMINMIN

CHAR_TAB_MAP = {
    0: 0,
    1: 0,
    2: 0,
    3: 0,
    4: 1,
    5: 2
}


class Tabbers():
    """Manages tabbers"""

    def __init__(self):
        self.build_tabber: QTabWidget
        self.build_frames: list[QFrame] = list()
        self.sidebar_tabber: QTabWidget
        self.sidebar_frames: list[QFrame] = list()
        self.character_tabber: QTabWidget
        self.character_frames: list[QFrame] = list()

    def switch(self, index):
        """
        Callback to switch between tabs. Switches build and both sidebar tabs.

        Parameters:
        - :param index: index to switch to (0: space build, 1: ground build, 2: space skills,
        3: ground skills, 4: library, 5: settings)
        """
        self.build_tabber.setCurrentIndex(index)
        self.sidebar_tabber.setCurrentIndex(index)
        self.character_tabber.setCurrentIndex(CHAR_TAB_MAP[index])


class ImageLabel(QWidget):
    """
    Label displaying image that resizes according to its parents width while preserving aspect
    ratio.
    """
    def __init__(self, path: Path | None = None, aspect_ratio: tuple[int, int] = (0, 0)):
        super().__init__()
        self._w, self._h = aspect_ratio
        if path is None:
            self.p = QImage()
        else:
            self.p = QImage(path)
        self.setSizePolicy(SMINMIN)
        self.setMinimumHeight(10)  # forces visibility
        self.update()

    def set_image(self, p: QImage):
        self.p = p
        self._w = p.width()
        self._h = p.height()
        self.update()

    def paintEvent(self, event: QPaintEvent):
        if not self.p.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            w = int(self.width())
            h = int(w * self._h / self._w)
            rect = QRect(0, 0, w, h)
            painter.drawImage(rect, self.p)
            self.setFixedHeight(h)


class ShipImage(ImageLabel):
    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.p.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            current_width = self.width()
            current_height = self.height()
            scale_factor = min(current_width / self._w, current_height / self._h)
            w = self._w * scale_factor
            h = self._h * scale_factor
            new_p = self.p.scaledToWidth(w, Qt.TransformationMode.SmoothTransformation)
            painter.drawImage(abs(w - current_width) // 2, abs(h - current_height) // 2, new_p)
            self.setFixedHeight(new_p.height())


class ItemButton(QFrame):
    """
    Button used to show items with overlay.
    """

    clicked = Signal()
    rightclicked = Signal(QMouseEvent)

    def __init__(
            self, width=49, height=64, style: dict = {},
            tooltip_label: QLabel = '', tooltip_frame: QFrame = '', frame_padding: int = 0, *args,
            **kwargs):
        super().__init__(*args, *kwargs)
        size_policy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        size_policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(size_policy)
        self._base: QImage = None
        self._overlay: QImage = None
        self._border_width = style['border-width']
        self._pen = QPen(QColor(style['border-color']), self._border_width)
        self._brush = QBrush(style['background-color'])
        self._highlight_color = style.get('border-highlight-color', style['border-color'])
        self._tooltip_label = tooltip_label
        self._tooltip_label.setAlignment(ATOP)
        self._tooltip_label.setWordWrap(True)
        self._tooltip_frame = tooltip_frame
        self._tooltip_frame.setWindowFlags(Qt.WindowType.ToolTip)
        self._total_padding = frame_padding * 2
        self.skill_image_name = ''
        self._width = width
        self._height = height
        self._highlight = False
        self.setFixedSize(width + 2 * self._border_width, height + 2 * self._border_width)

    @property
    def tooltip(self):
        return self._tooltip_label.text()

    @tooltip.setter
    def tooltip(self, new_tooltip):
        self._tooltip_label.setText(new_tooltip)

    @property
    def highlight(self):
        return self._highlight

    @highlight.setter
    def highlight(self, new_highlight_state: bool):
        self._highlight = new_highlight_state
        self.update()

    def enterEvent(self, event: QEnterEvent) -> None:
        if self.tooltip != '':
            # for some reason doubleclick-selecting an item fires enter event despite not hovering
            r = QRect(self.mapToGlobal(QPoint(0, 0)), self.mapToGlobal(self.rect().bottomRight()))
            if r.contains(QCursor.pos()):
                tooltip_width = self.window().width() // 5
                position = self.parentWidget().mapToGlobal(self.geometry().topLeft())
                position.setX(position.x() - tooltip_width - 1 - self._total_padding)
                self._tooltip_label.setFixedWidth(tooltip_width)
                self._tooltip_frame.move(position)
                self._tooltip_frame.updateGeometry()
                self._tooltip_frame.show()
        event.accept()

    def leaveEvent(self, event: QEvent) -> None:
        self._tooltip_frame.hide()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if not self.isEnabled():
            return
        if (event.button() == Qt.MouseButton.LeftButton
                and event.localPos().x() < self.width()
                and event.localPos().y() < self.height()):
            self.clicked.emit()
        elif (event.button() == Qt.MouseButton.RightButton
                and event.localPos().x() < self.width()
                and event.localPos().y() < self.height()):
            self.rightclicked.emit(event)
        event.accept()

    def set_item(self, image: QImage):
        self._base = image
        self.update()

    def set_overlay(self, image: QImage):
        self._overlay = image
        self.update()

    def set_item_overlay(self, item_image: QImage, overlay_image: QImage):
        self._base = item_image
        self._overlay = overlay_image
        self.update()

    def set_item_full(self, item_image: QImage, overlay_image: QImage, tooltip: str):
        self._base = item_image
        self._overlay = overlay_image
        self._tooltip_label.setText(tooltip)
        self.update()

    def clear(self):
        self._base = None
        self._overlay = None
        self._tooltip_label.setText('')
        self.update()

    def clear_item(self):
        self._base = None
        self.update()

    def clear_overlay(self):
        self._overlay = None
        self.update()

    def force_tooltip_update(self):
        if self.underMouse():
            self._tooltip_frame.hide()
            self._tooltip_frame.show()

    def set_style(self, style):
        self._border_width = style['border-width']
        self._pen = QPen(QColor(style['border-color']), self._border_width)
        self._brush = QBrush(style['background-color'])
        self._highlight_color = style.get('border-highlight-color', style['border-color'])

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(self._brush)
        painter.setPen(self._pen)
        if self._highlight:
            painter.setPen(QPen(QColor(self._highlight_color), self._border_width))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        image_rect = self.rect().adjusted(
                self._border_width, self._border_width, -self._border_width, -self._border_width)
        if self._base is not None:
            painter.drawImage(image_rect, self._base)
        if self._overlay is not None:
            painter.drawImage(image_rect, self._overlay)


class GridLayout(QGridLayout):
    def __init__(self, margins=0, spacing: int = 0, parent: QWidget = None):
        """
        Creates Grid Layout

        Parameters:
        - :param margins: number or sequence with 4 items specifying content margins
        - :param spacing: item spacing for content
        - :param parent: parent of the layout
        """
        super().__init__(parent)
        if isinstance(margins, (int, float)):
            self.setContentsMargins(margins, margins, margins, margins)
        else:
            self.setContentsMargins(*margins)
        self.setSpacing(spacing)


class HBoxLayout(QHBoxLayout):
    def __init__(self, margins=0, spacing: int = 0, parent: QWidget = None):
        """
        Creates horizontal Box Layout

        Parameters:
        - :param margins: number or sequence with 4 items specifying content margins
        - :param spacing: item spacing for content
        - :param parent: parent of the layout
        """
        super().__init__(parent)
        if isinstance(margins, (int, float)):
            self.setContentsMargins(margins, margins, margins, margins)
        else:
            self.setContentsMargins(*margins)
        self.setSpacing(spacing)


class VBoxLayout(QVBoxLayout):
    def __init__(self, margins=0, spacing: int = 0, parent: QWidget = None):
        """
        Creates vertical Box Layout

        Parameters:
        - :param margins: number or sequence with 4 items specifying content margins
        - :param spacing: item spacing for content
        - :param parent: parent of the layout
        """
        super().__init__(parent)
        if isinstance(margins, (int, float)):
            self.setContentsMargins(margins, margins, margins, margins)
        else:
            self.setContentsMargins(*margins)
        self.setSpacing(spacing)


class Thread(QThread):
    """
    Thread based on QThread with convenience functionality.
    """
    result: Signal = Signal(object)
    done: Signal = Signal()

    def __init__(self, target: Callable, args: tuple = (), kwargs: dict[str] = {}):
        super().__init__()
        self._target: Callable = target
        self._args: tuple = args
        self._kwargs: dict[str] = kwargs

    def set_args(self, new_args: tuple) -> bool:
        """
        Sets new arguments that should be passed to the target. Only works while thread is not
        running. Returns `True` on success, `False` on failure.
        """
        if self.isRunning():
            return False
        else:
            self._args = new_args
            return True

    @Slot()
    def run(self):
        """
        This function will be executed in a separate thread.
        """
        self.result.emit(self._target(*self._args, **self._kwargs))
        self.done.emit()


class ShipButton(QLabel):
    """
    Button with word wrap
    """
    clicked = Signal()

    def __init__(self, text: str):
        super().__init__()
        self.setWordWrap(True)
        self.setText(text)
        self.setAlignment(AHCENTER)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, ev: QMouseEvent):
        if ev.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
            ev.accept()
        else:
            super().mousePressEvent(ev)


ItemSlot = namedtuple('ItemSlot', ('environment', 'type', 'index', 'boff_id', 'is_equipment'))


class DoffCombobox(QComboBox):
    def minimumSizeHint(self) -> QSize:
        return QSize(100, super().minimumSizeHint().height())

    def sizeHint(self) -> QSize:
        return QSize(100, super().minimumSizeHint().height())


class notempty():
    """
    Yields items from iterable that are neither None nor an empty string.
    """
    def __init__(self, iterable):
        self._gen = (element for element in iterable if element is not None and element != '')

    def __iter__(self):
        return self._gen


class pixel_range():
    """
    Returns appropriate indices to access the RGB (not A) channels of the pixel row of `num` pixels,
    as well as an 1-step increasing range index -> (range_index, pixel_index)
    """
    def __init__(self, num: int = 0, range_start: int = 0, /):
        def generator():
            counter = range_start
            for index in range(0, num * 4, 4):
                yield counter, index
                counter += 1
                yield counter, index + 1
                counter += 1
                yield counter, index + 2
                counter += 1
        self.__gen = generator()

    def __iter__(self):
        return self.__gen


class TooltipLabel(QLabel):
    """Label with tooltip"""
    def __init__(self, text: str, tooltip: QLabel):
        super().__init__(text)
        self._tooltip = tooltip
        self._tooltip.setWindowFlags(Qt.WindowType.ToolTip)

    def enterEvent(self, event: QEnterEvent) -> None:
        position = self.parentWidget().mapToGlobal(self.geometry().bottomLeft())
        position.setY(position.y() + 1)
        self._tooltip.move(position)
        self._tooltip.updateGeometry()
        self._tooltip.show()
        event.accept()

    def leaveEvent(self, event: QEvent) -> None:
        self._tooltip.hide()
        event.accept()
