from typing import Callable, Iterable, Iterator

from PySide6.QtCore import QPoint, QSortFilterProxyModel, QStringListModel, Qt
from PySide6.QtGui import QMouseEvent, QTextOption
from PySide6.QtWidgets import QAbstractItemView, QDialog, QListView, QPlainTextEdit

from .constants import AHCENTER, ALEFT, ATOP, MARKS, RARITIES, SMAXMAX, SMINMAX, SMINMIN
from .iofunc import image
from .widgetbuilder import (
    create_button, create_button_series, create_combo_box, create_entry, create_frame,
    create_item_button, create_label)
from .widgets import GridLayout, HBoxLayout, VBoxLayout
from .style import get_style, get_style_class, theme_font


class BasePicker(QDialog):
    """
    Base class of SETS item picker / editor housing shared methods.
    """
    @property
    def empty_item(self):
        return {
            'item': '',
            'rarity': 'Common',
            'mark': '',
            'modifiers': [''] * 5
        }

    def insert_modifiers(self, modifiers: dict = {}):
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

    def unique_mods(self, modifiers: dict = {}) -> Iterator[str]:
        """
        yields mods for first mod slot from modifier dict
        """
        yield ''
        for mod, details in modifiers.items():
            if not details['epic']:
                yield mod

    def standard_mods(self, modifiers: dict = {}) -> Iterator[str]:
        """
        yields mods for second to fourth mod slot from modifier list
        """
        yield ''
        for mod, details in modifiers.items():
            if not details['epic'] and not details['isunique']:
                yield mod

    def not_epic_mods(self, modifiers: dict = {}) -> Iterator[str]:
        """
        yields mods for first to fourth mod slot from modifier list
        """
        yield ''
        for mod, details in modifiers.items():
            if not details['epic']:
                yield mod

    def epic_mods(self, modifiers: dict = {}) -> Iterator[str]:
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
                self, sets, parent_window, style: str = 'picker',
                default_rarity_getter: Callable = lambda: 'Common',
                default_mark_getter: Callable = lambda: ''):
        super().__init__(parent=parent_window)
        self.start_pos = None
        self.setWindowFlags(
                self.windowFlags() | Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(get_style(sets, style))
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumSize(10, 10)
        self.setSizePolicy(SMAXMAX)
        self._image_getter = lambda image_name: image(sets, image_name)
        self._item = self.empty_item
        self._result = None
        self._modifiers = {}
        ui_scale = sets.config['ui_scale']
        spacing = sets.theme['defaults']['isp'] * ui_scale
        layout = VBoxLayout(margins=(spacing, 0, spacing, spacing), spacing=0)
        top_layout = HBoxLayout(spacing=spacing)
        self._item_button = create_item_button(
                sets, style_override={'margin-top': '@isp', 'margin-bottom': '@isp'})
        top_layout.addWidget(self._item_button, alignment=ALEFT)
        self._item_label = create_label(
                sets, '<Item Name>', 'label_subhead', style_override={'margin-bottom': 0})
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
            mod_combo.currentIndexChanged.connect(lambda mod, i=i: self.modifier_callback(mod, i))
            self._mod_combos[i] = mod_combo
            mod_layout.addWidget(mod_combo, i // 2, i % 2)
        mod_combo = create_combo_box(sets, style_override={'font': '@font'}, editable=True)
        mod_combo.currentIndexChanged.connect(lambda mod: self.modifier_callback(mod, 4))
        self._mod_combos[4] = mod_combo
        mod_layout.addWidget(mod_combo, 2, 0, 1, 2)
        prop_layout.addLayout(mod_layout)
        spacer_1 = create_frame(sets)
        spacer_1.setFixedHeight(spacing - csp)
        prop_layout.addWidget(spacer_1)
        self._prop_frame.setLayout(prop_layout)
        layout.addWidget(self._prop_frame)
        seperator = create_frame(sets, size_policy=SMINMAX, style_override={
                'background-color': '@lbg', 'margin': '@isp'})
        seperator.setFixedHeight(sets.theme['defaults']['sep'] * ui_scale)
        layout.addWidget(seperator)
        spacer_2 = create_frame(sets)
        spacer_2.setFixedHeight(spacing)
        layout.addWidget(spacer_2)
        self._item_model = QStringListModel()
        self._sort_model = QSortFilterProxyModel()
        self._sort_model.setSourceModel(self._item_model)
        self._sort_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._search_bar = create_entry(sets, placeholder='Search')
        self._search_bar.textChanged.connect(
                lambda new_text: self._sort_model.setFilterFixedString(new_text))
        self._search_bar.setSizePolicy(SMINMAX)
        layout.addWidget(self._search_bar)
        spacer_3 = create_frame(sets)
        spacer_3.setFixedHeight(spacing)
        layout.addWidget(spacer_3)
        self._items_list = QListView()
        self._items_list.setStyleSheet(get_style_class(sets, 'QListView', 'picker_list'))
        self._items_list.setSizePolicy(SMINMIN)
        self._items_list.setModel(self._sort_model)
        self._items_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._items_list.clicked.connect(self.slot_item)
        self._items_list.doubleClicked.connect(self.select_item)
        layout.addWidget(self._items_list)
        spacer_4 = create_frame(sets)
        spacer_4.setFixedHeight(spacing)
        layout.addWidget(spacer_4)
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

        self._get_default_rarity = default_rarity_getter
        self._get_default_mark = default_mark_getter

    def slot_item(self, new_index):
        """
        called when item is clicked
        """
        new_item = str(new_index.data(Qt.ItemDataRole.DisplayRole))
        self._item['item'] = new_item
        self._item_button.set_item(self._image_getter(new_item))
        self._item_label.setText(new_item)
        for i in range(5):
            self._mod_combos[i].setCurrentText('')

    def select_item(self, new_index):
        """
        shortcut for selecting item and pressing ok
        """
        new_item = str(new_index.data(Qt.ItemDataRole.DisplayRole))
        self._item['item'] = new_item
        self.accept()

    def pick_item(
            self, items: Iterable, button_pos: QPoint | None, equipment: bool = False,
            modifiers: dict = {}):
        """
        Executes picker, returns selected item. Returns None when picker is closed without saving.
        """
        window = self.parentWidget()
        if button_pos is None:
            window_size = (window.width() * 0.2, window.height() * 0.9)
            window_position = (window.x() + window_size[0] / 4, window.y() + window_size[1] / 18)
        else:
            if button_pos.y() > window.y() + window.frameGeometry().height() * 0.5:
                button_pos.setY(window.y() + window.frameGeometry().height() * 0.5)
            window_size = (window.width() * 0.2, (window.height() - button_pos.y()) * 0.95)
            window_position = (button_pos.x() - window_size[0] * 1.05, button_pos.y())
        self._result = None
        self.setFixedSize(*window_size)
        self.move(*window_position)
        self._item_model.setStringList(items)
        self._item_label.setMinimumWidth(window_size[0] * 0.75)
        self._sort_model.sort(0, Qt.SortOrder.AscendingOrder)
        self._items_list.scrollToTop()
        if equipment:
            self.insert_modifiers(modifiers)
            self._mark_combo.setCurrentText(self._get_default_mark())
            self._rarity_combo.setCurrentText(self._get_default_rarity())
            self._prop_frame.show()
        else:
            self._prop_frame.hide()
        self._search_bar.setFocus()
        action = self.exec()
        if action == 1 and self._item['item'] != '':
            self._result = {
                'item': self._item['item'],
                'rarity': self._item['rarity'],
                'mark': self._item['mark'],
                'modifiers': [mod for mod in self._item['modifiers']]
            }
        self._item_button.clear()
        self._search_bar.clear()
        self._item_label.setText('')
        self._item_model.removeRows(0, self._item_model.rowCount())
        self._mark_combo.setCurrentText('')
        self._rarity_combo.setCurrentText('Common')
        for mod_combo in self._mod_combos:
            mod_combo.setCurrentText('')
        self._item = self.empty_item
        return self._result

    def mousePressEvent(self, event: QMouseEvent):
        pr = self._prop_frame.rect()
        pr.moveTopLeft(self._prop_frame.pos())
        if pr.contains(event.pos()):
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
    """
    Selection Window for ships
    """
    def __init__(self, sets, parent_window, style: str = 'picker'):
        super().__init__(parent=parent_window)
        self.setWindowFlags(
                self.windowFlags() | Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(get_style(sets, style))
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumSize(10, 10)
        self.setSizePolicy(SMAXMAX)

        ui_scale = sets.config['ui_scale']
        spacing = sets.theme['defaults']['isp'] * ui_scale
        layout = VBoxLayout(margins=spacing, spacing=spacing)
        self._ship_data_model = QStringListModel()
        sort_model = QSortFilterProxyModel()
        sort_model.setSourceModel(self._ship_data_model)
        sort_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        heading = create_label(sets, 'Select Ship', 'label_heading')
        layout.addWidget(heading, alignment=AHCENTER)
        self._search_bar = create_entry(sets, placeholder='Search')
        self._search_bar.textChanged.connect(
                lambda new_text: sort_model.setFilterFixedString(new_text))
        self._search_bar.setSizePolicy(SMINMAX)
        layout.addWidget(self._search_bar)
        self._ship_list = QListView()
        self._ship_list.setStyleSheet(get_style_class(
                sets, 'QListView', 'picker_list',
                override={'::item:selected': {'border-color': '@sets'}}))
        self._ship_list.setSizePolicy(SMINMIN)
        self._ship_list.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._ship_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._ship_list.setModel(sort_model)
        self._ship_list.doubleClicked.connect(self.accept)
        layout.addWidget(self._ship_list)
        csp = sets.theme['defaults']['csp'] * ui_scale
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

    def set_ships(self, ships: Iterable):
        self._ship_data_model.setStringList(ships)

    def pick_ship(self):
        """
        Executes Picker, returns selected ship, returns None when cancelled.
        """
        window = self.parentWidget()
        size = (window.width() * 0.2, window.height() * 0.9)
        pos = (window.x() + size[0] / 4, window.y() + size[1] / 18)
        self.setFixedSize(*size)
        self.move(*pos)
        self._ship_list.scrollToTop()
        action = self.exec()
        self._search_bar.clear()
        if action == 1:
            ship_name = self._ship_list.currentIndex().data(Qt.ItemDataRole.DisplayRole)
            if ship_name != '':
                return ship_name
        return None

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
    def __init__(self, sets, parent_window, style: str = 'picker'):
        """
        Dialog to edit mark, rarity and mods of equipment items.

        Parameters:
        - :param sets: SETS object
        - :param parent_window: parent window of dialog
        - :param style: style key for sets.theme
        """
        super().__init__(parent=parent_window)
        self.setWindowFlags(
                self.windowFlags() | Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet(get_style(sets, style))
        self.setWindowModality(Qt.WindowModality.WindowModal)
        self.setMinimumSize(10, 10)
        self.setSizePolicy(SMAXMAX)
        self._item = self.empty_item
        self._result = None
        self._modifiers = {}
        ui_scale = sets.config['ui_scale']
        csp = sets.theme['defaults']['csp'] * ui_scale
        layout = VBoxLayout(spacing=csp)
        rarity_layout = HBoxLayout(spacing=csp)
        self._mark_combo = create_combo_box(sets)
        self._mark_combo.addItems(('', *MARKS))
        self._mark_combo.currentTextChanged.connect(self.mark_callback)
        rarity_layout.addWidget(self._mark_combo, 1)
        self._rarity_combo = create_combo_box(sets)
        self._rarity_combo.addItems(RARITIES.keys())
        self._rarity_combo.currentTextChanged.connect(self.rarity_callback)
        rarity_layout.addWidget(self._rarity_combo, 1)
        layout.addLayout(rarity_layout)
        mod_layout = GridLayout(spacing=csp)
        self._mod_combos = [None] * 5
        for i in range(4):
            mod_combo = create_combo_box(
                    sets, style_override={'font': '@font'}, editable=True, size_policy=SMINMAX)
            mod_combo.currentIndexChanged.connect(lambda mod, i=i: self.modifier_callback(mod, i))
            self._mod_combos[i] = mod_combo
            mod_layout.addWidget(mod_combo, i // 2, i % 2)
        mod_combo = create_combo_box(sets, style_override={'font': '@font'}, editable=True)
        mod_combo.currentIndexChanged.connect(lambda mod: self.modifier_callback(mod, 4))
        self._mod_combos[4] = mod_combo
        mod_layout.addWidget(mod_combo, 2, 0, 1, 2)
        layout.addLayout(mod_layout)
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
        content_frame = create_frame(sets, size_policy=SMINMIN)
        content_frame.setLayout(layout)
        margin = sets.theme['defaults']['isp'] * ui_scale
        main_layout = VBoxLayout(margins=margin)
        main_layout.addWidget(content_frame)
        self.setLayout(main_layout)

    def edit_item(self, item: dict, modifiers: dict):
        """
        Executes editor, returns edited item. Returns None when editor is closed without saving.
        """
        self._result = None
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
        action = self.exec()
        if action == 1:
            self._result = {
                'item': self._item['item'],
                'rarity': self._item['rarity'],
                'mark': self._item['mark'],
                'modifiers': [mod for mod in self._item['modifiers']]
            }
        self._mark_combo.setCurrentText('')
        self._rarity_combo.setCurrentText('Common')
        for mod_combo in self._mod_combos:
            mod_combo.setCurrentText('')
        self._item = self.empty_item
        return self._result


class ExportWindow(QDialog):
    """
    Holds Export Window
    """
    def __init__(self, sets, parent_window, data_getter: Callable):
        super().__init__(parent=parent_window)
        thick = sets.theme['app']['frame_thickness'] * sets.config['ui_scale']
        dialog_layout = VBoxLayout(margins=thick)
        main_frame = create_frame(sets, size_policy=SMINMIN)
        dialog_layout.addWidget(main_frame)
        main_layout = VBoxLayout(margins=thick, spacing=thick)
        content_frame = create_frame(sets, size_policy=SMINMIN)
        content_layout = VBoxLayout(spacing=thick)
        content_layout.setAlignment(ATOP)

        header_label = create_label(sets, 'Markdown Export:', 'label_heading')
        content_layout.addWidget(header_label, alignment=ALEFT)
        md_textedit = QPlainTextEdit()
        button_def = {
            'default': {'margin-top': 0},
            'Space Build': {
                'callback': lambda: md_textedit.setPlainText(data_getter('space', 'build'))
            },
            'Ground Build': {
                'callback': lambda: md_textedit.setPlainText(data_getter('ground', 'build'))
            },
            'Space Skills': {
                'callback': lambda: md_textedit.setPlainText(data_getter('space', 'skills'))
            },
            'Ground Skills': {
                'callback': lambda: md_textedit.setPlainText(data_getter('ground', 'skills'))
            },
        }
        top_buttons, (self._space_button, *_) = create_button_series(sets, button_def, ret=True)
        top_buttons.setAlignment(AHCENTER)
        content_layout.addLayout(top_buttons)
        md_textedit.setSizePolicy(SMINMIN)
        md_textedit.setStyleSheet(get_style_class(sets, 'QPlainTextEdit', 'textedit'))
        md_textedit.setFont(theme_font(sets, 'textedit'))
        md_textedit.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        content_layout.addWidget(md_textedit, stretch=1)
        content_frame.setLayout(content_layout)
        main_layout.addWidget(content_frame, stretch=1)

        seperator = create_frame(sets, style='light_frame', size_policy=SMINMAX)
        seperator.setFixedHeight(1)
        main_layout.addWidget(seperator)
        footer_button_def = {
            'Copy': {'callback': lambda: sets.app.clipboard().setText(md_textedit.toPlainText())},
            'Close': {'callback': lambda: self.done(0)}
        }
        footer_buttons = create_button_series(sets, footer_button_def)
        footer_buttons.setAlignment(AHCENTER)
        main_layout.addLayout(footer_buttons)
        main_frame.setLayout(main_layout)

        self.setLayout(dialog_layout)
        self.setWindowTitle('SETS - Markdown Export')
        self.setStyleSheet(get_style(sets, 'dialog_window'))

    def invoke(self):
        """
        Shows Export Window.
        """
        window_rect = self.parent().geometry()
        self.setGeometry(
                window_rect.x() + window_rect.width() * 0.25,
                window_rect.y() + window_rect.height() * 0.25,
                window_rect.width() * 0.5,
                window_rect.height() * 0.5)
        self._space_button.click()
        self.exec()
