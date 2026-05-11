from PySide6.QtCore import Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QMenu

from .cargomanager import CargoManager
from .constants import EQUIPMENT_TYPES
from .buildmanager import BuildManager
from .iofunc import open_wiki_page
from .theme import AppTheme
from .widgets import ItemSlot


class ContextMenu(QMenu):
    """
    Custom context menu with data storage
    """

    edit_slot: Signal = Signal(dict, dict, ItemSlot)

    def __init__(self, theme: AppTheme, build: BuildManager, cargo: CargoManager):
        super().__init__()
        self._build: BuildManager = build
        self._cargo: CargoManager = cargo
        self.clicked_slot: ItemSlot | None = None
        self.clicked_modifiers: dict = {}
        self.copied_item: dict = None
        self.copied_item_type: str = None

        self.setStyleSheet(theme.get_style_class('ContextMenu', 'context_menu'))
        self.setFont(theme.get_font('context_menu'))
        self.addAction(theme.icons['copy'], 'Copy Item', self.copy_equipment_item)
        self.addAction(theme.icons['paste'], 'Paste Item', self.paste_equipment_item)
        self.addAction(theme.icons['clear'], 'Clear Slot', self.clear_slot)
        self.addAction(theme.icons['link'], 'Open Wiki', self.open_wiki)
        self.addAction(theme.icons['edit'], 'Edit Slot', self.edit_equipment_item)

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
        actions = self.actions()
        if key in {'boffs', 'rep_traits', 'starship_traits', 'traits', 'active_rep_traits'}:
            actions[0].setEnabled(False)
            actions[1].setEnabled(False)
            actions[4].setEnabled(False)
            is_equipment = False
        else:
            actions[0].setEnabled(True)
            actions[1].setEnabled(True)
            actions[4].setEnabled(True)
            is_equipment = True
        self.clicked_slot = ItemSlot(environment, key, subkey, boff, is_equipment)
        self.popup(event.globalPos())

    def copy_equipment_item(self):
        """
        Copies equipment item clicked on.
        """
        slot = self.clicked_slot
        item = self._build[slot.environment][slot.type][slot.index]
        if item is None or item == '':
            self.copied_item = None
            self.copied_item_type = None
        else:
            # TODO check if dict must be deep-copied
            self.copied_item = item
            item_type = EQUIPMENT_TYPES[self._cargo.equipment[slot.type][item['item']]['type']]
            self.copied_item_type = item_type

    def paste_equipment_item(self):
        """
        Pastes copied item into clicked slot if slot types are compatible
        """
        slot = self.clicked_slot
        if (self.copied_item_type == slot.type
                or self.copied_item_type == 'ship_weapon' and (
                    slot.type == 'fore_weapons' or slot.type == 'aft_weapons')
                or self.copied_item_type == 'uni_consoles' and 'consoles' in slot.type
                or slot.type == 'uni_consoles' and 'consoles' in self.copied_item_type):
            self._build.slot_equipment_item(
                self.copied_item, slot.environment, slot.type, slot.index)
        self._build.autosave()

    def edit_equipment_item(self):
        """
        Edit mark, modifiers and rarity of rightclicked item.
        """
        slot = self.clicked_slot
        item = self._build[slot.environment][slot.type][slot.index]
        if slot.type == 'fore_weapons' or slot.type == 'aft_weapons':
            item_type = slot.type
        else:
            item_type = EQUIPMENT_TYPES[self._cargo.equipment[slot.type][item['item']]['type']]
        modifiers = self._cargo.modifiers[item_type]
        self.edit_slot.emit(item, modifiers, slot)

    def clear_slot(self):
        """
        Clears slot that was rightclicked on.
        """
        slot = self.clicked_slot
        self._build.unslot_item(slot.environment, slot.type, slot.index, slot.boff_id)
        self._build.autosave()

    def open_wiki(self):
        """
        Opens wiki page of item that was rightclicked on.
        """
        slot = self.clicked_slot
        if slot.boff_id != -1:
            item = self._build[slot.environment][slot.type][slot.boff_id][slot.index]
            if item is not None and item != '':
                open_wiki_page(f"{item['item']}_(ability)")
            return
        item = self._build[slot.environment][slot.type][slot.index]
        if item is None or item == '':
            return
        if slot.type == 'starship_traits':
            open_wiki_page(f"{item['item']}_(starship_trait)")
        elif 'traits' in slot.type:
            open_wiki_page(f"{item['item']}_({slot.environment}_trait)")
        else:
            open_wiki_page(
                f"{self._cargo.equipment[slot.type][item['item']]['Page']}#{item['item']}")
