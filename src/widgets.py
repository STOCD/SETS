from PySide6.QtCore import QEvent, Qt, QRect, Signal
from PySide6.QtGui import QEnterEvent, QHelpEvent, QImage, QMouseEvent, QPainter, QPixmap
from PySide6.QtWidgets import (
        QCheckBox, QComboBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QTabWidget, QToolTip, QWidget)

from .datafunctions import EQUIPMENT_TYPES
from .constants import SMAXMAX, SMINMIN


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

        self.space_build: dict = {
            'active_rep_traits': [None] * 5,
            'aft_weapons': [None] * 5,
            'boffs': [[None] * 4] * 6,
            'boff_specs': [None] * 6,
            'core': '',
            'deflector': '',
            'devices': [None] * 6,
            'doffs': [''] * 6,
            'eng_consoles': [None] * 5,
            'engines': '',
            'experimental': None,
            'fore_weapons': [None] * 5,
            'hangars': [None] * 2,
            'rep_traits': [None] * 5,
            'sci_consoles': [None] * 5,
            'sec_def': None,
            'shield': '',
            'ship': '',
            'ship_name': '',
            'starship_traits': [None] * 7,
            'tac_consoles': [None] * 5,
            'tier': '',
            'traits': [None] * 11,
            'uni_consoles': [None] * 3,
        }


class Cache():
    """
    Stores data
    """
    def __init__(self):
        self.ships: dict = dict()
        self.equipment: dict = {type_: dict() for type_ in EQUIPMENT_TYPES}
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
            'ground': self.boff_dict()
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

        self.empty_image: QPixmap
        self.overlays: OverlayCache = OverlayCache()
        self.images: dict = dict()

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


class ItemButton(QFrame):
    """
    Button used to show items with overlay.
    """

    clicked = Signal(dict)
    rightclicked = Signal(dict)

    def __init__(
            self, width=49, height=64, stylesheet: str = '',
            tooltip_label: QLabel = '', *args, **kwargs):
        super().__init__(*args, *kwargs)
        self.setSizePolicy(SMAXMAX)
        self.sizePolicy().setRetainSizeWhenHidden(True)
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

    def enterEvent(self, event: QEnterEvent) -> None:
        if self._tooltip.text() != '':
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
            self.clicked.emit({})
        elif (event.button() == Qt.MouseButton.RightButton
                and event.localPos().x() < self.width()
                and event.localPos().y() < self.height()):
            self.rightclicked.emit({})
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

    def clear(self):
        self._base = None
        self._overlay = None
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
