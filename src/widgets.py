from PySide6.QtCore import QRect
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QFrame, QLabel, QTabWidget, QWidget

from .widgetbuilder import SMINMIN
from .datafunctions import EQUIPMENT_TYPES


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
