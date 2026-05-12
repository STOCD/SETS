from typing import Iterable, Iterator

from PySide6.QtCore import (
    QModelIndex, QPoint, QSortFilterProxyModel, QStringListModel, Qt, Signal, Slot)
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import (
    QAbstractItemView, QComboBox, QDialog, QFrame, QLabel, QListView, QWidget)

from .config import SETSSettings
from .constants import AHCENTER, ALEFT, MARKS, RARITIES, SMAXMAX, SMINMAX, SMINMIN
from .imagemanager import ImageManager
from .theme import AppTheme
from .widgetbuilder import (
    create_button2, create_combo_box2, create_entry2, create_frame2, create_item_button2,
    create_label2)
from .widgets import GridLayout, HBoxLayout, ItemButton, ItemSlot, VBoxLayout


class BasePicker(QDialog):
    """
    Base class of SETS item picker / editor housing shared methods.
    """

    dialog_result: Signal = Signal(dict, ItemSlot)

    def __init__(self, parent: QWidget):
        super().__init__(parent=parent)
        self._item: dict[str, str | list[str]] = self.empty_item
        self._slot: ItemSlot | None = None
        self._modifiers: dict[str, dict[str]] = {}
        self._mod_combos: list[QComboBox | None] = [None] * 5
        self._mark_combo: QComboBox
        self._rarity_combo: QComboBox

    @property
    def empty_item(self) -> dict[str, str | list[str]]:
        return {
            'item': '',
            'rarity': 'Common',
            'mark': '',
            'modifiers': [''] * 5
        }

    def insert_modifiers(self, modifiers: dict[str] = {}):
        """
        Inserts the modifiers into the comboboxes
        """
        self._modifiers = modifiers
        self._mod_combos[0].clear()
        self._mod_combos[0].addItems(self.not_epic_mods(modifiers))
        self._mod_combos[1].clear()
        self._mod_combos[1].addItems(self.not_epic_mods(modifiers))
        self._mod_combos[2].clear()
        self._mod_combos[2].addItems(self.not_epic_mods(modifiers))
        self._mod_combos[3].clear()
        self._mod_combos[3].addItems(self.not_epic_mods(modifiers))
        self._mod_combos[4].clear()
        self._mod_combos[4].addItems(self.epic_mods(modifiers))

    def unique_mods(self, modifiers: dict[str] = {}) -> Iterator[str]:
        """
        yields mods for first mod slot from modifier dict
        """
        yield ''
        for mod, details in modifiers.items():
            if not details['epic']:
                yield mod

    def standard_mods(self, modifiers: dict[str] = {}) -> Iterator[str]:
        """
        yields mods for second to fourth mod slot from modifier list
        """
        yield ''
        for mod, details in modifiers.items():
            if not details['epic'] and not details['isunique']:
                yield mod

    def not_epic_mods(self, modifiers: dict[str] = {}) -> Iterator[str]:
        """
        yields mods for first to fourth mod slot from modifier list
        """
        yield ''
        for mod, details in modifiers.items():
            if not details['epic']:
                yield mod

    def epic_mods(self, modifiers: dict[str] = {}) -> Iterator[str]:
        """
        yields mods for fifth mod slot from modifier list
        """
        yield ''
        for mod, details in modifiers.items():
            if details['epic']:
                yield mod

    def mark_callback(self, new_mark: str):
        """
        called when mark is changed
        """
        self._item['mark'] = new_mark

    def rarity_callback(self, new_rarity: str):
        """
        called when rarity is changed
        """
        self._item['rarity'] = new_rarity
        for i in range(RARITIES[new_rarity]):
            self._mod_combos[i].setEnabled(True)
        for i in range(RARITIES[new_rarity], 5):
            self._mod_combos[i].setCurrentText('')
            self._mod_combos[i].setEnabled(False)
            self._item['modifiers'][i] = ''

    def modifier_callback(self, new_mod_index: int, mod_num: int):
        """
        called when modifier is changed
        """
        new_mod = self._mod_combos[mod_num].itemText(new_mod_index)
        if new_mod == '' or mod_num > RARITIES[self._item['rarity']] - 1:
            self._item['modifiers'][mod_num] = ''
        else:
            self._item['modifiers'][mod_num] = new_mod


class Picker(BasePicker):
    """
    Picker Window
    """
    def __init__(
            self, theme: AppTheme, parent_window: QWidget, settings: SETSSettings,
            images: ImageManager, style: str = 'picker'):
        super().__init__(parent=parent_window)
        self._settings: SETSSettings = settings
        self._images: ImageManager = images
        self.start_pos: QPoint | None = None
        self._image_suffix: str = ''
        self._item_button: ItemButton
        self._item_label: QLabel
        self._prop_frame: QFrame
        self._item_model: QStringListModel
        self._sort_model: QSortFilterProxyModel
        self._items_list: QListView
        self.finished.connect(self.finish_pick)

        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(theme.get_style(style))
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumSize(10, 10)
        self.setSizePolicy(SMAXMAX)
        ui_scale = theme.scale
        spacing = theme['defaults']['isp'] * ui_scale
        layout = VBoxLayout(margins=(spacing, 0, spacing, spacing), spacing=0)
        top_layout = HBoxLayout(spacing=spacing)
        button_layout = VBoxLayout(margins=(0, spacing, 0, spacing))
        button_frame = create_frame2(theme, style_override={'background': 'none'})
        self._item_button = create_item_button2(theme)
        button_layout.addWidget(self._item_button)
        button_frame.setLayout(button_layout)
        top_layout.addWidget(button_frame, alignment=ALEFT)
        self._item_label = create_label2(
            theme, '<Item Name>', 'label_subhead', style_override={'margin-bottom': 0})
        self._item_label.setWordWrap(True)
        self._item_label.setSizePolicy(SMINMAX)
        top_layout.addWidget(self._item_label, stretch=1)
        layout.addLayout(top_layout)
        self._prop_frame = create_frame2(theme, size_policy=SMINMAX)
        csp = theme['defaults']['csp'] * ui_scale
        prop_layout = VBoxLayout(spacing=csp)
        rarity_layout = HBoxLayout(spacing=csp)
        self._mark_combo = create_combo_box2(theme)
        self._mark_combo.addItems(('', *MARKS))
        self._mark_combo.currentTextChanged.connect(self.mark_callback)
        rarity_layout.addWidget(self._mark_combo, 1)
        self._rarity_combo = create_combo_box2(theme)
        self._rarity_combo.addItems(RARITIES.keys())
        self._rarity_combo.currentTextChanged.connect(self.rarity_callback)
        rarity_layout.addWidget(self._rarity_combo, 1)
        prop_layout.addLayout(rarity_layout)
        mod_layout = GridLayout(spacing=csp)
        self._mod_combos = [None] * 5
        for i in range(4):
            mod_combo = create_combo_box2(theme, style_override={'font': '@font'}, editable=True)
            mod_combo.currentIndexChanged.connect(lambda mod, i=i: self.modifier_callback(mod, i))
            self._mod_combos[i] = mod_combo
            mod_layout.addWidget(mod_combo, i // 2, i % 2)
        mod_combo = create_combo_box2(theme, style_override={'font': '@font'}, editable=True)
        mod_combo.currentIndexChanged.connect(lambda mod: self.modifier_callback(mod, 4))
        self._mod_combos[4] = mod_combo
        mod_layout.addWidget(mod_combo, 2, 0, 1, 2)
        prop_layout.addLayout(mod_layout)
        spacer_1 = create_frame2(theme)
        spacer_1.setFixedHeight(spacing - csp)
        prop_layout.addWidget(spacer_1)
        self._prop_frame.setLayout(prop_layout)
        layout.addWidget(self._prop_frame)
        seperator = create_frame2(theme, size_policy=SMINMAX, style_override={
            'background-color': '@lbg', 'margin': '@isp'})
        seperator.setFixedHeight(theme['defaults']['sep'] * ui_scale)
        layout.addWidget(seperator)
        spacer_2 = create_frame2(theme)
        spacer_2.setFixedHeight(spacing)
        layout.addWidget(spacer_2)
        self._item_model = QStringListModel()
        self._sort_model = QSortFilterProxyModel()
        self._sort_model.setSourceModel(self._item_model)
        self._sort_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._search_bar = create_entry2(theme, placeholder='Search')
        self._search_bar.textChanged.connect(
            lambda new_text: self._sort_model.setFilterFixedString(new_text))
        self._search_bar.setSizePolicy(SMINMAX)
        layout.addWidget(self._search_bar)
        spacer_3 = create_frame2(theme)
        spacer_3.setFixedHeight(spacing)
        layout.addWidget(spacer_3)
        self._items_list = QListView()
        self._items_list.setStyleSheet(theme.get_style_class('QListView', 'picker_list'))
        self._items_list.setSizePolicy(SMINMIN)
        self._items_list.setModel(self._sort_model)
        self._items_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._items_list.clicked.connect(self.slot_item)
        self._items_list.doubleClicked.connect(self.select_item)
        layout.addWidget(self._items_list)
        spacer_4 = create_frame2(theme)
        spacer_4.setFixedHeight(spacing)
        layout.addWidget(spacer_4)
        control_layout = HBoxLayout(spacing=csp)
        cancel_button = create_button2(theme, 'Cancel')
        cancel_button.setSizePolicy(SMINMAX)
        cancel_button.clicked.connect(self.reject)
        control_layout.addWidget(cancel_button)
        save_button = create_button2(theme, 'Save')
        save_button.clicked.connect(self.accept)
        save_button.setSizePolicy(SMINMAX)
        control_layout.addWidget(save_button)
        layout.addLayout(control_layout)
        self.setLayout(layout)

    def slot_item(self, new_index: QModelIndex):
        """
        called when item is clicked
        """
        new_item = str(new_index.data(Qt.ItemDataRole.DisplayRole))
        self._item['item'] = new_item
        self._item_label.setText(new_item)
        if new_item.endswith('I'):
            new_item, _, _ = new_item.rpartition(' ')
        self._item_button.set_item(self._images.get_alt(new_item, self._image_suffix))
        for i in range(5):
            self._mod_combos[i].setCurrentText('')

    def select_item(self, new_index: QModelIndex):
        """
        shortcut for selecting item and pressing ok
        """
        new_item = str(new_index.data(Qt.ItemDataRole.DisplayRole))
        self._item['item'] = new_item
        self.accept()

    def pick_item(
            self, items: Iterable[str], button_pos: QPoint | None, slot: ItemSlot,
            modifiers: dict[str, dict[str]] = {}, image_suffix: str = ''):
        """
        Shows picker window. Returns immediately.

        Parameters:
        - :param items: collection of items to select from
        - :param button_pos: positions picker next to this position if not `None`
        - :param slot: information about the slot
        - :param modifiers: collection of modifiers
        - :param image_suffix: suffix containing environment and type to check for alternative icon
        """
        window = self.parentWidget()
        if button_pos is None:
            window_size = (window.width() * 0.2, window.height() * 0.9)
            window_position = (window.x() + window_size[0] / 4, window.y() + window_size[1] / 18)
        else:
            if button_pos.y() > window.y() + window.frameGeometry().height() * 0.5:
                button_pos.setY(window.y() + window.frameGeometry().height() * 0.5)
            window_size = (
                window.width() * 0.2,
                (window.height() - button_pos.y() + window.y()) * 0.95
            )
            window_position = (button_pos.x() - window_size[0] * 1.05, button_pos.y())
        self._result = None
        self._slot = slot
        self.setFixedSize(*window_size)
        self.move(*window_position)
        self._item_model.setStringList(items)
        self._item_label.setMinimumWidth(window_size[0] * 0.75)
        self._sort_model.sort(0, Qt.SortOrder.AscendingOrder)
        self._items_list.scrollToTop()
        if slot.is_equipment:
            self.insert_modifiers(modifiers)
            self._mark_combo.setCurrentText(self._settings.default_mark)
            self._rarity_combo.setCurrentText(self._settings.default_rarity)
            self._prop_frame.show()
        else:
            self._prop_frame.hide()
        self._image_suffix = image_suffix
        self._search_bar.setFocus()
        self.open()

    @Slot(int)
    def finish_pick(self, action: int):
        """
        Completes the pick action, resets the dialog and emits the data using the `dialog_result`
        signal.

        Parameters:
        - :param action: indicates whether the result should be saved (`1`) or not (`0`)
        """
        slot = self._slot
        if action == 1 and self._item['item'] != '':
            picked_item = {
                'item': self._item['item'],
                'rarity': self._item['rarity'],
                'mark': self._item['mark'],
                'modifiers': [mod for mod in self._item['modifiers']]
            }
        else:
            picked_item = self.empty_item
        self._item_button.clear()
        self._search_bar.clear()
        self._item_label.setText('')
        self._item_model.removeRows(0, self._item_model.rowCount())
        self._mark_combo.setCurrentText('')
        self._rarity_combo.setCurrentText('Common')
        for mod_combo in self._mod_combos:
            mod_combo.setCurrentText('')
        self._item = self.empty_item
        self._slot = None
        self.dialog_result.emit(picked_item, slot)

    def mousePressEvent(self, event: QMouseEvent):
        pr = self._prop_frame.rect()
        pr.moveTopLeft(self._prop_frame.pos())
        if pr.contains(event.pos()):
            # allowing window move to start here can cause accidental clicks on comboboxes
            self.start_pos = None
        else:
            self.start_pos = event.globalPosition().toPoint()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        pr = self._prop_frame.rect()
        pr.moveTopLeft(self._prop_frame.pos())
        if self.start_pos is not None and not pr.contains(event.pos()):
            pos_delta = QPoint(event.globalPosition().toPoint() - self.start_pos)
            self.move(self.x() + pos_delta.x(), self.y() + pos_delta.y())
            self.start_pos = event.globalPosition().toPoint()
        event.accept()


class ShipSelector(QDialog):
    """Selection Window for ships"""

    dialog_result: Signal = Signal(str)

    def __init__(self, theme: AppTheme, parent_window: QWidget, style: str = 'picker'):
        super().__init__(parent=parent_window)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(theme.get_style(style))
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumSize(10, 10)
        self.setSizePolicy(SMAXMAX)
        self.finished.connect(self.finish_pick)

        ui_scale = theme.scale
        spacing = theme['defaults']['isp'] * ui_scale
        layout = VBoxLayout(margins=spacing, spacing=spacing)
        self._ship_data_model = QStringListModel()
        sort_model = QSortFilterProxyModel()
        sort_model.setSourceModel(self._ship_data_model)
        sort_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        heading = create_label2(theme, 'Select Ship', 'label_heading')
        layout.addWidget(heading, alignment=AHCENTER)
        self._search_bar = create_entry2(theme, placeholder='Search')
        self._search_bar.textChanged.connect(
            lambda new_text: sort_model.setFilterFixedString(new_text))
        self._search_bar.setSizePolicy(SMINMAX)
        layout.addWidget(self._search_bar)
        self._ship_list = QListView()
        self._ship_list.setStyleSheet(theme.get_style_class(
            'QListView', 'picker_list', override={'::item:selected': {'border-color': '@sets'}}))
        self._ship_list.setSizePolicy(SMINMIN)
        self._ship_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._ship_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._ship_list.setModel(sort_model)
        self._ship_list.doubleClicked.connect(self.accept)
        layout.addWidget(self._ship_list)
        csp = theme['defaults']['csp'] * ui_scale
        control_layout = HBoxLayout(spacing=csp)
        cancel_button = create_button2(theme, 'Cancel')
        cancel_button.setSizePolicy(SMINMAX)
        cancel_button.clicked.connect(self.reject)
        control_layout.addWidget(cancel_button)
        save_button = create_button2(theme, 'Save')
        save_button.clicked.connect(self.accept)
        save_button.setSizePolicy(SMINMAX)
        control_layout.addWidget(save_button)
        layout.addLayout(control_layout)
        self.setLayout(layout)

    def set_ships(self, ships: Iterable):
        self._ship_data_model.setStringList(ships)

    @Slot()
    def pick_ship(self):
        """
        Shows picker window.
        """
        window = self.parentWidget()
        size = (window.width() * 0.2, window.height() * 0.9)
        pos = (window.x() + size[0] / 4, window.y() + size[1] / 18)
        self.setFixedSize(*size)
        self.move(*pos)
        self._ship_list.scrollToTop()
        self.open()

    @Slot(int)
    def finish_pick(self, action: int):
        """
        Completes the ship pick action, resets the dialog and emits the data using the
        `dialog_result` signal.

        Parameters:
        - :param action: indicates whether the result should be saved (`1`) or not (`0`)
        """
        self._search_bar.clear()
        ship_name = ''
        if action == 1:
            ship_name = self._ship_list.currentIndex().data(Qt.ItemDataRole.DisplayRole)
        self.dialog_result.emit(ship_name)

    def mousePressEvent(self, event: QMouseEvent):
        self.start_pos = event.globalPosition().toPoint()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos_delta = QPoint(event.globalPosition().toPoint() - self.start_pos)
        self.move(self.x() + pos_delta.x(), self.y() + pos_delta.y())
        self.start_pos = event.globalPosition().toPoint()
        event.accept()


class ItemEditor(BasePicker):
    """
    Dialog to edit mark, rarity and mods of equipment items.
    """
    def __init__(self, theme: AppTheme, parent_window: QWidget, style: str = 'picker'):
        super().__init__(parent=parent_window)
        self.finished.connect(self.finish_edit)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(theme.get_style(style))
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumSize(10, 10)
        self.setSizePolicy(SMAXMAX)
        ui_scale = theme.scale
        csp = theme['defaults']['csp'] * ui_scale
        layout = VBoxLayout(spacing=csp)
        rarity_layout = HBoxLayout(spacing=csp)
        self._mark_combo = create_combo_box2(theme)
        self._mark_combo.addItems(('', *MARKS))
        self._mark_combo.currentTextChanged.connect(self.mark_callback)
        rarity_layout.addWidget(self._mark_combo, 1)
        self._rarity_combo = create_combo_box2(theme)
        self._rarity_combo.addItems(RARITIES.keys())
        self._rarity_combo.currentTextChanged.connect(self.rarity_callback)
        rarity_layout.addWidget(self._rarity_combo, 1)
        layout.addLayout(rarity_layout)
        mod_layout = GridLayout(spacing=csp)
        for i in range(4):
            mod_combo = create_combo_box2(
                theme, style_override={'font': '@font'}, editable=True, size_policy=SMINMAX)
            mod_combo.currentIndexChanged.connect(lambda mod, i=i: self.modifier_callback(mod, i))
            self._mod_combos[i] = mod_combo
            mod_layout.addWidget(mod_combo, i // 2, i % 2)
        mod_combo = create_combo_box2(theme, style_override={'font': '@font'}, editable=True)
        mod_combo.currentIndexChanged.connect(lambda mod: self.modifier_callback(mod, 4))
        self._mod_combos[4] = mod_combo
        mod_layout.addWidget(mod_combo, 2, 0, 1, 2)
        layout.addLayout(mod_layout)
        control_layout = HBoxLayout(spacing=csp)
        cancel_button = create_button2(theme, 'Cancel')
        cancel_button.setSizePolicy(SMINMAX)
        cancel_button.clicked.connect(self.reject)
        control_layout.addWidget(cancel_button)
        save_button = create_button2(theme, 'Save')
        save_button.clicked.connect(self.accept)
        save_button.setSizePolicy(SMINMAX)
        control_layout.addWidget(save_button)
        layout.addLayout(control_layout)
        content_frame = create_frame2(theme, size_policy=SMINMIN)
        content_frame.setLayout(layout)
        margin = theme['defaults']['isp'] * ui_scale
        main_layout = VBoxLayout(margins=margin)
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)

    @Slot(dict, dict, ItemSlot)
    def edit_item(self, item: dict[str], modifiers: dict[str, dict[str]], slot: ItemSlot):
        """
        Shows editor window. Returns immediately.

        Parameters:
        - :param item: item data for the item that should be edited
        - :param modifiers: collection of available modifiers
        - :param slot: information about the slot
        """
        self._slot = slot
        self.insert_modifiers(modifiers)
        self._mark_combo.setCurrentText(item['mark'])
        self._rarity_combo.setCurrentText(item['rarity'])
        for combo, modifier in zip(self._mod_combos, item['modifiers']):
            combo.setCurrentText(modifier if modifier is not None else '')
        self._item = {
            'item': item['item'],
            'rarity': item['rarity'],
            'mark': item['mark'],
            'modifiers': [mod for mod in item['modifiers']]
        }
        self.open()

    @Slot(int)
    def finish_edit(self, action: int):
        """
        Completes the edit action, resets the dialog and emits the data using the `dialog_result`
        signal.

        Parameters:
        - :param action: indicates whether the result should be saved (`1`) or not (`0`)
        """
        slot = self._slot
        if action == 1:
            edited_item = {
                'item': self._item['item'],
                'rarity': self._item['rarity'],
                'mark': self._item['mark'],
                'modifiers': [mod for mod in self._item['modifiers']]
            }
        else:
            edited_item = self.empty_item
        self._mark_combo.setCurrentText('')
        self._rarity_combo.setCurrentText('Common')
        for mod_combo in self._mod_combos:
            mod_combo.setCurrentText('')
        self._item = self.empty_item
        self._slot = None
        self.dialog_result.emit(edited_item, slot)
