from PySide6.QtCore import QEvent, QObject, Qt, QRect, QThread, Signal, QRunnable, Slot
from PySide6.QtGui import QEnterEvent, QMouseEvent, QPainter, QPixmap
from PySide6.QtWidgets import (
        QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
        QPlainTextEdit, QSizePolicy, QTabWidget, QVBoxLayout, QWidget)

from .constants import AHCENTER, EQUIPMENT_TYPES, SMAXMAX, SMINMIN


class WidgetStorage():
    """
    Stores Widgets
    """
    def __init__(self):
        self.splash_tabber: QTabWidget
        self.loading_label: QLabel

        self.build_tabber: QTabWidget
        self.build_frames: list[QFrame] = list()
        self.sidebar: QFrame
        self.sidebar_tabber: QTabWidget
        self.sidebar_frames: list[QFrame] = list()
        self.ship: dict = {
            'image': ShipImage,
            'button': ShipButton,
            'tier': QComboBox,
            'name': QLineEdit,
            'desc': QPlainTextEdit
        }
        self.character_tabber: QTabWidget
        self.character_frames: list[QFrame] = list()

        self.character: dict = {
            'name': QLineEdit,
            'elite': QCheckBox,
            'career': QComboBox,
            'faction': QComboBox,
            'species': QComboBox,
            'primary': QComboBox,
            'secondary': QComboBox,
        }

        self.build: dict = {
            'space': {
                'active_rep_traits': [None] * 5,
                'aft_weapons': [None] * 5,
                'aft_weapons_label': None,
                'boffs': [[None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4],
                'boff_labels': [None] * 6,
                'boff_specs': [None] * 6,
                'core': [''],
                'deflector': [''],
                'devices': [None] * 6,
                'doffs': [''] * 6,
                'eng_consoles': [None] * 5,
                'eng_consoles_label': None,
                'engines': [''],
                'experimental': [None],
                'experimental_label': None,
                'fore_weapons': [None] * 5,
                'hangars': [None] * 2,
                'hangars_label': None,
                'rep_traits': [None] * 5,
                'sci_consoles': [None] * 5,
                'sci_consoles_label': None,
                'sec_def': [None],
                'sec_def_label': None,
                'shield': [''],
                'ship': '',
                'ship_desc': '',
                'ship_name': '',
                'starship_traits': [None] * 7,
                'tac_consoles': [None] * 5,
                'tac_consoles_label': None,
                'tier': '',
                'traits': [None] * 12,
                'uni_consoles': [None] * 3,
                'uni_consoles_label': None
            }
        }


class Cache():
    """
    Stores data
    """
    def __init__(self):
        self.reset_cache()

    def reset_cache(self):
        self.ships: dict = dict()
        self.equipment: dict = {type_: dict() for type_ in set(EQUIPMENT_TYPES.values())}
        self.starship_traits: dict = dict()
        self.traits: dict = {
            'space': {
                'personal': dict(),
                'rep': dict(),
                'active_rep': dict()
            },
            'ground': {
                'personal': dict(),
                'rep': dict(),
                'active_rep': dict()
            }
        }
        self.ground_doffs: dict = dict()
        self.space_doffs: dict = dict()
        self.boff_abilities: dict = {
            'space': self.boff_dict(),
            'ground': self.boff_dict(),
            'all': dict()
        }
        self.skills = {
            'space': dict(),
            'space_unlocks': dict(),
            'ground': dict(),
            'ground_unlocks': dict()
        }
        self.species: dict = {
            'Federation': dict(),
            'Klingon': dict(),
            'Romulan': dict(),
            'Dominion': dict(),
            'TOS Federation': dict(),
            'DSC Federation': dict()
        }
        self.modifiers: dict = {type_: dict() for type_ in set(EQUIPMENT_TYPES.values())}

        self.empty_image: QPixmap
        self.overlays: OverlayCache = OverlayCache()
        self.images: dict = dict()
        self.images_set: set = set()
        self.images_populated: bool = False
        self.images_failed: dict = dict()

    def boff_dict(self):
        return {
            'Tactical': [dict(), dict(), dict(), dict()],
            'Engineering': [dict(), dict(), dict(), dict()],
            'Science': [dict(), dict(), dict(), dict()],
            'Intelligence': [dict(), dict(), dict(), dict()],
            'Command': [dict(), dict(), dict(), dict()],
            'Pilot': [dict(), dict(), dict(), dict()],
            'Temporal': [dict(), dict(), dict(), dict()],
            'Miracle Worker': [dict(), dict(), dict(), dict()],
        }

    def __getitem__(self, key: str):
        return getattr(self, key)


class OverlayCache():
    def __init__(self):
        self.common: QPixmap
        self.uncommon: QPixmap
        self.rare: QPixmap
        self.veryrare: QPixmap
        self.ultrarare: QPixmap
        self.epic: QPixmap


class ImageLabel(QWidget):
    """
    Label displaying image that resizes according to its parents width while preserving aspect
    ratio.
    """
    def __init__(self, path: str = '', aspect_ratio: tuple[int, int] = (0, 0), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._w, self._h = aspect_ratio
        if path == '':
            self.p = QPixmap()
        else:
            self.p = QPixmap(path)
        self.setSizePolicy(SMINMIN)
        self.setMinimumHeight(10)  # forces visibility
        self.update()

    def set_pixmap(self, p: QPixmap):
        self.p = p
        self._w = p.width()
        self._h = p.height()
        self.update()

    def paintEvent(self, event):
        if not self.p.isNull():
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            w = int(self.width())
            h = int(w * self._h / self._w)
            rect = QRect(0, 0, w, h)
            painter.drawPixmap(rect, self.p)
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
            painter.drawPixmap(abs(w - current_width) // 2, abs(h - current_height) // 2, new_p)
            self.setFixedHeight(new_p.height())


class ItemButton(QFrame):
    """
    Button used to show items with overlay.
    """

    clicked = Signal()
    rightclicked = Signal()

    def __init__(
            self, width=49, height=64, stylesheet: str = '',
            tooltip_label: QLabel = '', *args, **kwargs):
        super().__init__(*args, *kwargs)
        size_policy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        size_policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(size_policy)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self._image_space = ItemImage(self, width, height)
        self._image_space.setFixedWidth(width)
        self._image_space.setFixedHeight(height)
        layout.addWidget(self._image_space)
        self.setLayout(layout)
        self._base: QPixmap = None
        self._overlay: QPixmap = None
        self.setStyleSheet(stylesheet)
        self._tooltip = tooltip_label
        self._tooltip.setWindowFlags(Qt.WindowType.ToolTip)
        self._tooltip.setWordWrap(True)

    @property
    def tooltip(self):
        return self._tooltip.text()

    @tooltip.setter
    def tooltip(self, new_tooltip):
        self._tooltip.setText(new_tooltip)

    def enterEvent(self, event: QEnterEvent) -> None:
        if self.tooltip != '':
            tooltip_width = self.window().width() // 5
            position = self.parentWidget().mapToGlobal(self.geometry().topLeft())
            position.setX(position.x() - tooltip_width - 1)
            self._tooltip.setFixedWidth(tooltip_width)
            self._tooltip.move(position)
            self._tooltip.show()
        event.accept()

    def leaveEvent(self, event: QEvent) -> None:
        self._tooltip.hide()
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if (event.button() == Qt.MouseButton.LeftButton
                and event.localPos().x() < self.width()
                and event.localPos().y() < self.height()):
            self.clicked.emit()
        elif (event.button() == Qt.MouseButton.RightButton
                and event.localPos().x() < self.width()
                and event.localPos().y() < self.height()):
            self.rightclicked.emit()
        event.accept()

    def set_item(self, pixmap: QPixmap):
        self._base = pixmap
        self._image_space.update()

    def set_overlay(self, pixmap: QPixmap):
        self._overlay = pixmap
        self._image_space.update()

    def set_item_overlay(self, item_pixmap: QPixmap, overlay_pixmap: QPixmap):
        self._base = item_pixmap
        self._overlay = overlay_pixmap
        self._image_space.update()

    def set_item_full(self, item_pixmap: QPixmap, overlay_pixmap: QPixmap, tooltip: str):
        self._base = item_pixmap
        self._overlay = overlay_pixmap
        self._tooltip.setText(tooltip)
        self._image_space.update()

    def clear(self):
        self._base = None
        self._overlay = None
        self._tooltip.setText('')
        self._image_space.update()

    def clear_item(self):
        self._base = None
        self._image_space.update()

    def clear_overlay(self):
        self._overlay = None
        self._image_space.update()


class ItemImage(QWidget):
    def __init__(self, button: ItemButton, width, height, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._button = button
        self._rect = QRect(0, 0, width, height)
        self.setFixedSize(width, height)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if self._button._base is not None:
            painter.drawPixmap(self._rect, self._button._base)
        if self._button._overlay is not None:
            painter.drawPixmap(self._rect, self._button._overlay)


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


class CustomThread(QThread):
    """
    Subclass of QThread able to execute an arbitrary function in a seperate thread.
    """
    result = Signal(tuple)
    update_splash = Signal(str)

    def __init__(self, parent, func, *args, **kwargs) -> None:
        """
        Executes a function in a seperate thread. Positional and keyword parameters besides the
        parameters listed below are passed to the function. The function should also take a keyword
        parameter `thread` which will contain this thread. This thread has two additional signals
        `result` (type: tuple) and `update_splash` (type: str).

        Parameters:
        - :param parent: parent of the thread, should be the main window, prevents the thread to go
        out of scope and be destroyed by the garbage collector
        - :param func: function to execute in seperate thread, must take parameter `thread`
        """
        self._func = func
        self._args = args
        self._kwargs = kwargs
        super().__init__(parent)

    def run(self):
        self._func(*self._args, thread=self, **self._kwargs)


class ThreadObject(QObject):

    start = Signal(tuple)
    result = Signal(object)
    update_splash = Signal(str)
    finished = Signal()

    def __init__(self, func, *args, **kwargs) -> None:
        self._func = func
        self._args = args
        self._kwargs = kwargs
        super().__init__()

    @Slot()
    def run(self, start_args=tuple()):
        self._func(*self._args, *start_args, thread=self, **self._kwargs)
        self.finished.emit()


def exec_in_thread(self, func, *args, result=None, update_splash=None, start_later=False, **kwargs):
    worker = ThreadObject(func, *args, **kwargs)
    if result is not None:
        worker.result.connect(result)
    if update_splash is not None:
        worker.update_splash.connect(update_splash)
    thread = QThread(self.app)
    worker.moveToThread(thread)
    if start_later:
        worker.start.connect(worker.run)
    else:
        thread.started.connect(worker.run)
    worker.finished.connect(thread.quit)
    worker.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread.worker = worker
    thread.start(QThread.Priority.LowestPriority)
    print('start')
    if start_later:
        return worker.start


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
