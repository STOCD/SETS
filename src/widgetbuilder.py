from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
        QCheckBox, QComboBox, QCompleter, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QSizePolicy, QVBoxLayout)

from .callbacks import (
        boff_label_callback_ground, boff_profession_callback_space, doff_spec_callback,
        doff_variant_callback, picker)
from .constants import ALEFT, ATOP, CALLABLE, CAREERS, GROUND_BOFF_SPECS, SMAXMAX, SMAXMIN, SMINMAX
from .style import get_style, get_style_class, merge_style, theme_font
from .widgets import DoffCombobox, GridLayout, HBoxLayout, ItemButton, VBoxLayout


def create_frame(self, style='frame', style_override={}, size_policy=None) -> QFrame:
    """
    Creates a frame with default styling and parent

    Parameters:
    - :param style: style dict to override default style (optional)
    - :param size_policy: size policy of the frame (optional)

    :return: configured QFrame
    """
    frame = QFrame()
    frame.setStyleSheet(get_style(self, style, style_override))
    frame.setSizePolicy(size_policy if isinstance(size_policy, QSizePolicy) else SMAXMAX)
    return frame


def create_label(self, text, style: str = 'label', style_override={}):
    """
    Creates a label according to style with parent.

    Parameters:
    - :param text: text to be shown on the label
    - :param style: name of the style as in self.theme
    - :param style_override: style dict to override default style (optional)

    :return: configured QLabel
    """
    label = QLabel()
    label.setText(text)
    label.setStyleSheet(get_style(self, style, style_override))
    label.setSizePolicy(SMAXMAX)
    if 'font' in style_override:
        label.setFont(theme_font(self, style, style_override['font']))
    else:
        label.setFont(theme_font(self, style))
    return label


def create_button(self, text: str, style: str = 'button', style_override={}, toggle=None):
    """
    Creates a button according to style with parent.

    Parameters:
    - :param text: text to be shown on the button
    - :param style: name of the style as in self.theme or style dict
    - :param style_override: style dict to override default style (optional)
    - :param toggle: True or False when button should be a toggle button, None when it should be a
    normal button; the bool value indicates the default state of the button

    :return: configured QPushButton
    """
    button = QPushButton(text)
    button.setStyleSheet(get_style_class(self, 'QPushButton', style, style_override))
    if 'font' in style_override:
        button.setFont(theme_font(self, style, style_override['font']))
    else:
        button.setFont(theme_font(self, style))
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setSizePolicy(SMAXMAX)
    if isinstance(toggle, bool):
        button.setCheckable(True)
        button.setChecked(toggle)
    return button


def create_button_series(
        self, buttons: dict, style: str = 'button', shape: str = 'row', seperator: str = '',
        ret=False):  # QVBoxLayout | QHBoxLayout
    """
    Creates a row / column of buttons.

    Parameters:
    - :param buttons: dictionary containing button details
        - key "default" contains style override for all buttons (optional)
        - all other keys represent one button, key will be the text on the button; value for the
        key contains dict with details for the specific button (all optional)
            - "callback": callable that will be called on button click
            - "style": individual style override dict
            - "toggle": True or False when button should be a toggle button, None when it should be
            a normal button; the bool value indicates the default state of the button
            - "stretch": stretch value for the button
            - "align": alignment flag for button
            - "size": SizePolicy for button
    - :param style: key for self.theme -> default style
    - :param shape: row / column
    - :param seperator: string seperator displayed between buttons (optional)

    :return: populated QVBoxlayout / QHBoxlayout
    """
    if 'default' in buttons:
        defaults = merge_style(self, self.theme[style], buttons.pop('default'))
    else:
        defaults = self.theme[style]

    if shape == 'column':
        layout = QVBoxLayout()
    else:
        shape = 'row'
        layout = QHBoxLayout()

    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)

    button_list = []

    if seperator != '':
        sep_style = {
                'color': defaults['color'], 'margin': 0, 'padding': 0, 'background': '#00000000'}

    for i, (name, detail) in enumerate(buttons.items()):
        if 'style' in detail:
            button_style = merge_style(self, defaults, detail['style'])
        else:
            button_style = defaults
        toggle_button = detail['toggle'] if 'toggle' in detail else None
        bt = create_button(self, name, style, button_style, toggle_button)
        if 'size' in detail:
            bt.setSizePolicy(detail['size'])
        if 'callback' in detail and isinstance(detail['callback'], CALLABLE):
            if toggle_button:
                bt.clicked[bool].connect(detail['callback'])
            else:
                bt.clicked.connect(detail['callback'])
        stretch = detail['stretch'] if 'stretch' in detail else 0
        if 'align' in detail:
            layout.addWidget(bt, stretch, detail['align'])
        else:
            layout.addWidget(bt, stretch)
        button_list.append(bt)
        if seperator != '' and i < (len(buttons) - 1):
            sep_label = create_label(self, seperator, 'label', sep_style)
            sep_label.setSizePolicy(SMAXMIN)
            layout.addWidget(sep_label)

    if ret:
        return layout, button_list
    else:
        return layout


def create_combo_box(
        self, style: str = 'combobox', editable: bool = False, size_policy: QSizePolicy = None,
        style_override: dict = {}, class_=QComboBox) -> QComboBox:
    """
    Creates a combobox with given style and returns it.

    Parameters:
    - :param style: key for self.theme -> default style
    - :param editable: set to True to make combobox editable
    - :param size_policy: size policy for combobox
    - :param style_override: style dict to override default style
    - :param class_: custom constructor for combobox; must be QCombobox or subclass

    :return: styled QCombobox
    """
    combo_box = class_()
    combo_box.setStyleSheet(get_style_class(self, 'QComboBox', style, style_override))
    if 'font' in style_override:
        font = theme_font(self, style, style_override['font'])
    else:
        font = theme_font(self, style)
    combo_box.setFont(font)
    combo_box.setSizePolicy(SMINMAX if size_policy is None else size_policy)
    combo_box.setCursor(Qt.CursorShape.PointingHandCursor)
    combo_box.view().setCursor(Qt.CursorShape.PointingHandCursor)
    combo_box.setMinimumContentsLength(1)
    combo_box.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
    if editable:
        combo_box.setEditable(True)
        combo_box.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo_box.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        combo_box.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        combo_box.completer().popup().setStyleSheet(get_style_class(self, 'QListView', 'popup'))
        combo_box.completer().popup().setFont(font)
        combo_box.lineEdit().setFont(font)
    return combo_box


def create_entry(
        self, default_value='', validator=None, style: str = 'entry',
        style_override: dict = {}, placeholder='') -> QLineEdit:
    """
    Creates an entry widget and styles it.

    Parameters:
    - :param default_value: default value for the entry
    - :param validator: validator to validate entered characters against
    - :param style: key for self.theme -> default style
    - :param style_override: style dict to override default style
    - :param placeholder: placeholder shown when entry is empty

    :return: styled QLineEdit
    """
    entry = QLineEdit(default_value)
    entry.setValidator(validator)
    entry.setPlaceholderText(placeholder)
    entry.setStyleSheet(get_style_class(self, 'QLineEdit', style, style_override))
    if 'font' in style_override:
        entry.setFont(theme_font(self, style, style_override['font']))
    else:
        entry.setFont(theme_font(self, style))
    entry.setCursor(Qt.CursorShape.IBeamCursor)
    entry.setSizePolicy(SMAXMAX)
    return entry


def create_checkbox(self, style: str = 'checkbox', style_override: dict = {}) -> QCheckBox:
    """
    Creates checkbox and styles it.

    Parameters:
    - :param style: key for self.theme -> default style
    - :param style_override: style dict to override default style
    """
    checkbox = QCheckBox()
    checkbox.setStyleSheet(get_style_class(self, 'QCheckBox', style, style_override))
    return checkbox


def create_item_button(self, style_override: dict = {}) -> ItemButton:
    """
    Creates Item Button.
    """
    label = create_label(self, '', 'infobox')
    frame = create_frame(self, 'infobox_frame')
    margin = self.theme['defaults']['csp'] * self.config['ui_scale']
    layout = VBoxLayout(margin)
    layout.addWidget(label, alignment=ATOP)
    frame.setLayout(layout)
    button = ItemButton(
            self.box_width, self.box_height, get_style(self, 'item', style_override), label, frame,
            margin + self.theme['defaults']['bw'] * self.config['ui_scale'])
    return button


def create_build_section(
        self, label_text: str, button_count: int, environment: bool, build_key: str,
        is_equipment: bool = False, label_store: str = '') -> QGridLayout:
    """
    Creates a block of item buttons below a label.

    Parameters:
    - :param label_text: text to be displayed above the buttons
    - :param button_count: number of buttons to be created
    - :param environment: "space" or "ground"
    - :param build_key: key for self.build['space'/'ground']
    - :param is_equipment: True when items are equipment, False if items are abilities or traits
    - :param label_store: stores category label in self.widgets.build[`label_store`] if set
    """
    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(self.theme['defaults']['margin'] * self.config['ui_scale'])
    label = create_label(self, label_text, style_override={'margin': (0, 0, 6, 0)})
    label_size_policy = label.sizePolicy()
    label_size_policy.setRetainSizeWhenHidden(True)
    label.setSizePolicy(label_size_policy)
    layout.addWidget(label, 0, 0, 1, button_count, alignment=ALEFT)
    widget_storage = self.widgets.build[environment]
    if label_store != '':
        widget_storage[label_store] = label
    for i in range(button_count):
        button = create_item_button(self)
        button.clicked.connect(lambda subkey=i: picker(
                self, environment, build_key, subkey, is_equipment))
        button.rightclicked.connect(
                lambda e, i=i: self.context_menu.invoke(e, build_key, i, environment))
        widget_storage[build_key][i] = button
        layout.addWidget(button, 1, i, alignment=ALEFT)
    return layout


def create_boff_station_space(
        self, profession: str, specialization: str = '', boff_id: int = 0) -> QGridLayout:
    """
    Creates a block of item buttons with label / Combobox representing boff station.

    Parameters:
    - :param profession: "Tactical", "Science", "Engineering" or "Universal"
    - :param specialization: specialization of the seat; None if it has no specialization
    - :param boff_id: identifies the boff station
    """
    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(self.theme['defaults']['margin'] * self.config['ui_scale'])
    layout.setColumnStretch(3, 1)
    if specialization != '':
        specialization = f' / {specialization}'
    if profession == 'Universal':
        label_options = (
            f'Tactical{specialization}',
            f'Science{specialization}',
            f'Engineering{specialization}'
        )
    else:
        label_options = (profession + specialization,)
    widget_storage = self.widgets.build['space']
    label = create_combo_box(self, size_policy=SMAXMAX, style_override=self.theme['boff_combo'])
    label.currentTextChanged.connect(lambda new: boff_profession_callback_space(self, boff_id, new))
    label.addItems(label_options)
    label_size_policy = label.sizePolicy()
    label_size_policy.setRetainSizeWhenHidden(True)
    label.setSizePolicy(label_size_policy)
    widget_storage['boff_labels'][boff_id] = label
    layout.addWidget(label, 0, 0, 1, 4, alignment=ALEFT)
    for i in range(4):
        button = create_item_button(self)
        button.sizePolicy().setRetainSizeWhenHidden(True)
        button.clicked.connect(lambda subkey=i: picker(
                self, 'space', 'boffs', subkey, boff_id=boff_id))
        button.rightclicked.connect(
                lambda e, i=i: self.context_menu.invoke(e, 'boffs', i, 'space', boff_id))
        layout.addWidget(button, 1, i, alignment=ALEFT)
        widget_storage['boffs'][boff_id][i] = button
    return layout


def create_boff_station_ground(self, boff_id: int) -> VBoxLayout:
    """
    Creates a block of item buttons with label / Combobox representing boff station.

    Parameters:
    - :param boff_id: identifies the boff station
    """
    widget_storage = self.widgets.build['ground']
    m = self.theme['defaults']['margin'] * self.config['ui_scale']
    layout = VBoxLayout(spacing=m)
    label_layout = HBoxLayout(spacing=m)
    label_layout.setAlignment(ALEFT)
    prof_label = create_combo_box(self, style_override=self.theme['boff_combo'])
    prof_label.currentTextChanged.connect(
            lambda new: boff_label_callback_ground(self, boff_id, 'boff_profs', new))
    prof_label.addItems(CAREERS)
    widget_storage['boff_profs'][boff_id] = prof_label
    label_layout.addWidget(prof_label)
    spec_label = create_combo_box(self, style_override=self.theme['boff_combo'])
    spec_label.currentTextChanged.connect(
            lambda new: boff_label_callback_ground(self, boff_id, 'boff_specs', new))
    spec_label.addItems(GROUND_BOFF_SPECS)
    widget_storage['boff_specs'][boff_id] = spec_label
    label_layout.addWidget(spec_label)
    layout.addLayout(label_layout)
    button_layout = HBoxLayout(spacing=m)
    button_layout.setAlignment(ALEFT)
    for i in range(4):
        button = create_item_button(self)
        button.clicked.connect(lambda subkey=i: picker(
                self, 'ground', 'boffs', subkey, boff_id=boff_id))
        button.rightclicked.connect(
                lambda e, i=i: self.context_menu.invoke(e, 'boffs', i, 'ground', boff_id))
        button_layout.addWidget(button)
        widget_storage['boffs'][boff_id][i] = button
    layout.addLayout(button_layout)
    return layout


def create_personal_trait_section(self, environment: str) -> QGridLayout:
    """
    Creates build section for personal traits
    """
    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(self.theme['defaults']['margin'] * self.config['ui_scale'])
    label = create_label(self, 'Personal Traits', style_override={'margin': (0, 0, 6, 0)})
    layout.addWidget(label, 0, 0, 1, 4, alignment=ALEFT)
    widget_storage = self.widgets.build[environment]
    for row in range(3):
        for col in range(4):
            i = row * 4 + col
            button = create_item_button(self)
            button.clicked.connect(lambda subkey=i: picker(self, environment, 'traits', subkey))
            button.rightclicked.connect(
                    lambda e, i=i: self.context_menu.invoke(e, 'traits', i, environment))
            layout.addWidget(button, row + 1, col, alignment=ALEFT)
            widget_storage['traits'][i] = button
    return layout


def create_starship_trait_section(self) -> QGridLayout:
    """
    Creates build section for starship traits
    """
    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(self.theme['defaults']['margin'] * self.config['ui_scale'])
    label = create_label(self, 'Starship Traits', style_override={'margin': (0, 0, 6, 0)})
    label.sizePolicy().setRetainSizeWhenHidden(True)
    layout.addWidget(label, 0, 0, 1, 4, alignment=ALEFT)
    widget_storage = self.widgets.build['space']
    for col in range(5):
        button = create_item_button(self)
        button.sizePolicy().setRetainSizeWhenHidden(True)
        button.clicked.connect(lambda subkey=col: picker(
                self, 'space', 'starship_traits', subkey))
        button.rightclicked.connect(
                lambda e, i=col: self.context_menu.invoke(e, 'starship_traits', i, 'space'))
        layout.addWidget(button, 1, col, alignment=ALEFT)
        widget_storage['starship_traits'][col] = button
    for col in range(2):
        button = create_item_button(self)
        button.sizePolicy().setRetainSizeWhenHidden(True)
        button.clicked.connect(lambda subkey=col + 5: picker(
                self, 'space', 'starship_traits', subkey))
        button.rightclicked.connect(
                lambda e, i=col + 5: self.context_menu.invoke(e, 'starship_traits', i, 'space'))
        layout.addWidget(button, 2, col, alignment=ALEFT)
        widget_storage['starship_traits'][col + 5] = button
    return layout


def create_doff_section(self, environment: str) -> GridLayout:
    """
    Creates duty officer section
    """
    spacing = self.theme['defaults']['bw'] * self.config['ui_scale']
    doff_layout = GridLayout(spacing=spacing)
    doff_layout.setColumnStretch(1, 1)
    for i in range(6):
        spec_combo = create_combo_box(self, style_override=self.theme['doff_combo'])
        spec_combo.currentTextChanged.connect(
                lambda spec, i=i: doff_spec_callback(self, spec, environment, i))
        doff_layout.addWidget(spec_combo, i, 0)
        self.widgets.build[environment]['doffs_spec'][i] = spec_combo
        variant_combo = create_combo_box(
                self, style_override=self.theme['doff_combo'], class_=DoffCombobox)
        variant_combo.currentTextChanged.connect(
            lambda variant, i=i: doff_variant_callback(self, variant, environment, i))
        doff_layout.addWidget(variant_combo, i, 1)
        self.widgets.build[environment]['doffs_variant'][i] = variant_combo
    return doff_layout
