from typing import Iterable

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QDialog, QListWidget

from .constants import ALEFT, MARKS, RARITIES, SMAXMAX, SMINMAX, SMINMIN
from .widgetbuilder import (
    create_button, create_combo_box, create_frame, create_item_button, create_label)
from .widgets import GridLayout, HBoxLayout, VBoxLayout
from .style import get_style, get_style_class


class Picker(QDialog):
    """
    Picker Window
    """
    def __init__(self, sets, parent_window, style: str = 'picker'):
        super().__init__(parent=parent_window)
        self.setWindowFlags(
                self.windowFlags() | Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(get_style(sets, style))
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumSize(10, 10)
        self.setSizePolicy(SMAXMAX)
        self._image_cache = sets.cache.images
        self._item = self.empty_item
        self._result = None
        ui_scale = sets.config['ui_scale']
        spacing = sets.theme['defaults']['isp'] * ui_scale
        layout = VBoxLayout(spacing, spacing)
        top_layout = HBoxLayout(spacing=spacing)
        self._item_button = create_item_button(sets)
        top_layout.addWidget(self._item_button, alignment=ALEFT)
        self._item_label = create_label(sets, '<Item Name>', 'label_subhead')
        self._item_label.setWordWrap(True)
        self._item_label.setSizePolicy(SMINMAX)
        top_layout.addWidget(self._item_label, stretch=1)
        layout.addLayout(top_layout)
        self._prop_frame = create_frame(sets, size_policy=SMINMAX)
        csp = sets.theme['defaults']['csp'] * ui_scale
        prop_layout = VBoxLayout(spacing=csp)
        rarity_layout = HBoxLayout(spacing=csp)
        self._mark_combo = create_combo_box(sets)
        self._mark_combo.addItems(('', *MARKS))
        self._mark_combo.currentTextChanged.connect(self.mark_callback)
        rarity_layout.addWidget(self._mark_combo, 1)
        self._rarity_combo = create_combo_box(sets)
        self._rarity_combo.addItems(RARITIES.keys())
        self._rarity_combo.currentTextChanged.connect(self.rarity_callback)
        rarity_layout.addWidget(self._rarity_combo, 1)
        prop_layout.addLayout(rarity_layout)
        mod_layout = GridLayout(spacing=csp)
        self._mod_combos = [None] * 5
        for i in range(4):
            mod_combo = create_combo_box(sets, style_override={'font': '@font'}, editable=True)
            mod_combo.currentTextChanged.connect(lambda mod, i=i: self.modifier_callback(mod, i))
            self._mod_combos[i] = mod_combo
            mod_layout.addWidget(mod_combo, i // 2, i % 2)
        mod_combo = create_combo_box(sets, style_override={'font': '@font'}, editable=True)
        mod_combo.currentTextChanged.connect(lambda: self.modifier_callback(4))
        self._mod_combos[4] = mod_combo
        mod_layout.addWidget(mod_combo, 2, 0, 1, 2)
        prop_layout.addLayout(mod_layout)
        self._prop_frame.setLayout(prop_layout)
        layout.addWidget(self._prop_frame)
        self._items_list = QListWidget()
        self._items_list.setStyleSheet(get_style_class(sets, 'QListWidget', 'picker_list'))
        self._items_list.setSizePolicy(SMINMIN)
        self._items_list.currentTextChanged.connect(self.slot_item)
        layout.addWidget(self._items_list)
        control_layout = HBoxLayout(spacing=csp)
        cancel_button = create_button(sets, 'Cancel')
        cancel_button.setSizePolicy(SMINMAX)
        cancel_button.clicked.connect(self.reject)
        control_layout.addWidget(cancel_button)
        save_button = create_button(sets, 'Save')
        save_button.clicked.connect(self.accept)
        save_button.setSizePolicy(SMINMAX)
        control_layout.addWidget(save_button)
        layout.addLayout(control_layout)
        self.setLayout(layout)

    @property
    def empty_item(self):
        return {
            'item': '',
            'rarity': 'Common',
            'mark': '',
            'modifiers': [None] * 5
        }

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
            self._mod_combos[i].setEnabled(False)

    def modifier_callback(self, new_mod: str, mod_num: int):
        """
        called when modifier is changed
        """
        if new_mod == '' and mod_num > RARITIES[self._item['rarity']] - 1:
            self._item['modifiers'][mod_num] = None
        else:
            self._item['modifiers'][mod_num] = new_mod

    def slot_item(self, new_item: str):
        """
        called when item is clicked
        """
        if new_item != '':
            self._item['item'] = new_item
            self._item_button.set_item(self._image_cache[new_item])
            self._item_label.setText(new_item)
            for i in range(5):
                self._mod_combos[i].setCurrentText('')

    def pick_item(
            self, window_size: tuple, window_position: tuple, items: Iterable,
            equipment: bool = False):
        """
        Executes picker, returns selected item. Returns None when picker is closed without saving.
        """
        self._result = None
        self.setFixedSize(*window_size)
        self.move(*window_position)
        self._items_list.addItems(items)
        if equipment:
            self._prop_frame.show()
        else:
            self._prop_frame.hide()
        action = self.exec()
        if action == 1:
            self._result = {**self._item}
        self._item_button.clear()
        self._item_label.setText('')
        self._items_list.clear()
        self._mark_combo.setCurrentText('')
        self._rarity_combo.setCurrentText('Common')
        for mod_combo in self._mod_combos:
            mod_combo.setCurrentText('')
        self._item = self.empty_item
        return self._result

    def mousePressEvent(self, event: QMouseEvent):
        self.start_pos = event.globalPosition().toPoint()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        pos_delta = QPoint(event.globalPosition().toPoint() - self.start_pos)
        self.move(self.x() + pos_delta.x(), self.y() + pos_delta.y())
        self.start_pos = event.globalPosition().toPoint()
        event.accept()
