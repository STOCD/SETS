from collections import namedtuple

from PySide6.QtCore import QEvent, QObject, QPoint, QRect, QSize, Qt, QThread, Signal, Slot
from PySide6.QtGui import QBrush, QColor, QCursor, QEnterEvent, QImage, QMouseEvent, QPainter, QPen
from PySide6.QtWidgets import (
        QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMenu,
        QPlainTextEdit, QSizePolicy, QTabWidget, QVBoxLayout, QWidget)

from .constants import AHCENTER, ATOP, EQUIPMENT_TYPES, SMINMIN


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
            'dc': TooltipLabel,
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
        self.ground_desc: QPlainTextEdit

        self.skill_bonus_bars = {
            'eng': [None] * 24,
            'sci': [None] * 24,
            'tac': [None] * 24,
            'ground': [None] * 10,
        }
        self.skill_count_ground: QLabel
        self.skill_counts_space: dict = {
            'eng': None,
            'sci': None,
            'tac': None
        }

        self.build: dict = {
            'space': {
                'active_rep_traits': [None] * 5,
                'aft_weapons': [None] * 5,
                'aft_weapons_label': None,
                'boffs': [[None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4],
                'boff_labels': [None] * 6,
                # 'boff_specs': [None] * 6,
                'core': [''],
                'deflector': [''],
                'devices': [None] * 6,
                'doffs_spec': [''] * 6,
                'doffs_variant': [''] * 6,
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
                # 'ship': '',
                # 'ship_desc': '',
                # 'ship_name': '',
                'starship_traits': [None] * 7,
                'tac_consoles': [None] * 5,
                'tac_consoles_label': None,
                # 'tier': '',
                'traits': [None] * 12,
                'uni_consoles': [None] * 3,
                'uni_consoles_label': None
            },
            'ground': {
                'active_rep_traits': [None] * 5,
                'armor': [''],
                'boffs': [[''] * 4, [''] * 4, [''] * 4, [''] * 4],
                'boff_profs': [''] * 4,
                'boff_specs': [''] * 4,
                'ground_devices': [None] * 5,
                'doffs_spec': [''] * 6,
                'doffs_variant': [''] * 6,
                'ev_suit': [''],
                'kit': [''],
                'kit_modules': [None] * 6,
                'rep_traits': [None] * 5,
                'personal_shield': [''],
                'traits': [None] * 12,
                'weapons': [''] * 2,
            },
            'space_skills': {
                'eng': [None] * 30,
                'sci': [None] * 30,
                'tac': [None] * 30
            },
            'ground_skills': [
                [False] * 6,
                [False] * 6,
                [False] * 4,
                [False] * 4,
            ],
            'skill_unlocks': {
                'eng': [None] * 5,
                'sci': [None] * 5,
                'tac': [None] * 5,
                'ground': [None] * 5
            },
            'skill_desc': {
                'space': None,
                'ground': None
            }
        }


class Cache():
    """
    Stores data
    """
    def __init__(self):
        self.reset_cache()

    def reset_cache(self, keep_skills=False):
        self.ships: dict = dict()
        self.equipment: dict = {type_: dict() for type_ in set(EQUIPMENT_TYPES.values())}
        self.starship_traits: dict = dict()
        self.traits: dict = {
            'space': {
                'traits': dict(),
                'rep_traits': dict(),
                'active_rep_traits': dict()
            },
            'ground': {
                'traits': dict(),
                'rep_traits': dict(),
                'active_rep_traits': dict()
            }
        }
        self.ground_doffs: dict = dict()
        self.space_doffs: dict = dict()
        self.boff_abilities: dict = {
            'space': self.boff_dict(),
            'ground': self.boff_dict(),
            'all': dict()
        }

        if not keep_skills:
            self.skills = {
                'space': dict(),
                'space_unlocks': dict(),
                'ground': dict(),
                'ground_unlocks': dict(),
                'space_points_total': 0,
                'space_points_eng': 0,
                'space_points_sci': 0,
                'space_points_tac': 0,
                'space_points_rank': [0] * 5,
                'ground_points_total': 0,
            }

        self.modifiers: dict = {type_: dict() for type_ in set(EQUIPMENT_TYPES.values())}

        self.empty_image: QImage
        self.overlays: OverlayCache = OverlayCache()
        self.icons: dict = dict()
        self.images: dict = dict()
        self.alt_images: dict = dict()
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
        self.common: QImage
        self.uncommon: QImage
        self.rare: QImage
        self.veryrare: QImage
        self.ultrarare: QImage
        self.epic: QImage
        self.check: QImage


class ImageLabel(QWidget):
    """
    Label displaying image that resizes according to its parents width while preserving aspect
    ratio.
    """
    def __init__(self, path: str = '', aspect_ratio: tuple[int, int] = (0, 0), *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._w, self._h = aspect_ratio
        if path == '':
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

    def paintEvent(self, event):
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


class PySideThread(QThread):
    def __init__(self, parent, finished_func, worker):
        self.finished_func = finished_func
        self.worker = worker
        super().__init__(parent)

    def worker_finished(self):
        if self.finished_func is not None:
            self.finished_func()
        self.quit()


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
        self._func(*self._args, *start_args, threaded_worker=self, **self._kwargs)
        self.finished.emit()


def exec_in_thread(
        self, func, *args, result=None, update_splash=None, finished=None, start_later=False,
        **kwargs):
    """
    Executes function `func` in separate thread. All positional and keyword parameters not listed
    are passed to the function. The function must take a parameter `threaded_worker` which will
    contain the worker object holding the signals: `start` (tuple), `result` (object),
    `update_splash` (str), `finished` (no data)

    Parameters:
    - :param func: function to execute
    - :param *args: positional parameters passed to the function [optional]
    - :param result: callable that is executed when signal result is emitted (takes object)
    [optional]
    - :param update_splash: callable that is executed when signal update_splash is emitted
    (takes str) [optional]
    - :param finished: callable that is executed after `func` returns (takes no parameters)
    [optional]
    - :param start_later: set to True to defer execution of the function; makes this function
    return signal that can be emitted to start execution. That signal takes a tuple with additional
    positional parameters passed to `func` [optional]
    - :param **kwargs: keyword parameters passed to the function [optional]
    """
    worker = ThreadObject(func, *args, **kwargs)
    thread = PySideThread(self.app, finished, worker)
    if result is not None:
        worker.result.connect(result)
    if update_splash is not None:
        worker.update_splash.connect(update_splash)
    worker.moveToThread(thread)
    if start_later:
        worker.start.connect(worker.run)
    else:
        thread.started.connect(worker.run)
    worker.finished.connect(thread.worker_finished)
    thread.finished.connect(worker.deleteLater)
    thread.finished.connect(thread.deleteLater)
    thread.start(QThread.Priority.LowestPriority)
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


TagStyles = namedtuple('TagStyles', ('ul', 'li', 'indent'))

ItemSlot = namedtuple('ItemSlot', ('type', 'index', 'environment'))


class ContextMenu(QMenu):
    """
    Custom context menu with data storage
    """
    def __init__(self):
        super().__init__()
        self.clicked_slot: ItemSlot = None
        self.clicked_boff_station: int = -1
        self.clicked_modifiers: dict = {}
        self.copied_item: dict = None
        self.copied_item_type: str = None

    def invoke(self, event: QMouseEvent, key: str, subkey: int, environment: str, boff: int = -1):
        """
        Opens context menu for equipment

        Parameters:
        - :param event: event containing the clicked point
        - :param key: slot type in self.build[environment]
        - :param subkey: slot index
        - :param environment: "space" / "ground"
        - :param boff: id of the boff station
        """
        self.clicked_slot = ItemSlot(key, subkey, environment)
        self.clicked_boff_station = boff
        actions = self.actions()
        if key in {'boffs', 'rep_traits', 'starship_traits', 'traits', 'active_rep_traits'}:
            actions[0].setEnabled(False)
            actions[1].setEnabled(False)
            actions[4].setEnabled(False)
        else:
            actions[0].setEnabled(True)
            actions[1].setEnabled(True)
            actions[4].setEnabled(True)
        self.exec(event.globalPos())


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
