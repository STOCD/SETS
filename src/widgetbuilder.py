from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
        QCheckBox, QComboBox, QCompleter, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
        QPushButton, QSizePolicy, QSlider, QVBoxLayout)

from .callbacks import (
        boff_label_callback_ground, boff_profession_callback_space, doff_spec_callback,
        doff_variant_callback, picker, skill_callback_ground, skill_callback_space,
        skill_unlock_callback)
from .constants import (
        ABOTTOM, AHCENTER, ALEFT, ATOP, AVCENTER, CALLABLE, CAREERS, GROUND_BOFF_SPECS, SMAXMAX,
        SMAXMIN, SMINMAX)
from .style import get_style, get_style_class, merge_style, theme_font
from .textedit import format_skill_tooltip
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
            self.box_width, self.box_height, self.theme['item'], label, frame,
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
        button.clicked.connect(lambda subkey=i, bt=button: picker(
                self, environment, build_key, subkey, bt, is_equipment))
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
        button.clicked.connect(lambda subkey=i, bt=button: picker(
                self, 'space', 'boffs', subkey, bt, boff_id=boff_id))
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
        button.clicked.connect(lambda subkey=i, bt=button: picker(
                self, 'ground', 'boffs', subkey, bt, boff_id=boff_id))
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
            button.clicked.connect(
                    lambda subkey=i, bt=button: picker(self, environment, 'traits', subkey, bt))
            button.rightclicked.connect(
                    lambda e, i=i: self.context_menu.invoke(e, 'traits', i, environment))
            layout.addWidget(button, row + 1, col, alignment=ALEFT)
            widget_storage['traits'][i] = button
    # Last button is for innate trait and should not be clickable
    button.setEnabled(False)
    button.set_style(self.theme['item_dark'])
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
        button.clicked.connect(lambda subkey=col, bt=button: picker(
                self, 'space', 'starship_traits', subkey, bt))
        button.rightclicked.connect(
                lambda e, i=col: self.context_menu.invoke(e, 'starship_traits', i, 'space'))
        layout.addWidget(button, 1, col, alignment=ALEFT)
        widget_storage['starship_traits'][col] = button
    for col in range(2):
        button = create_item_button(self)
        button.sizePolicy().setRetainSizeWhenHidden(True)
        button.clicked.connect(lambda subkey=col + 5, bt=button: picker(
                self, 'space', 'starship_traits', subkey, bt))
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


def create_skill_group_space(self, group_data: dict, id_offset: int) -> GridLayout:
    """
    Creates a skill group (3 related skill nodes) in appropriate shape

    Parameters:
    - :param group_data: skill group data
    - :param id_offset: index of the first skill node in self.widgets and self.build
    """
    layout = GridLayout(spacing=self.theme['defaults']['csp'] * self.config['ui_scale'])
    # one skill with 3 ranks
    if group_data['grouping'] == 'column':
        for index, node in enumerate(group_data['nodes']):
            button = create_item_button(self)
            button.clicked.connect(lambda id=id_offset + index: skill_callback_space(
                    self, group_data['career'], id, 'column'))
            # button.rightclicked.connect(lambda e: None)
            button.skill_image_name = node['image']
            button.tooltip = format_skill_tooltip(
                    self, group_data['skill'], group_data, index, 'space')
            self.widgets.build['space_skills'][group_data['career']][id_offset + index] = button
            layout.addWidget(button, index, 0)
    # == 'pair+1': one skill with 2 ranks and one sub-skill with 1 rank
    # == 'separate': 3 separate skills
    else:
        button = create_item_button(self)
        button.clicked.connect(lambda id=id_offset: skill_callback_space(
                self, group_data['career'], id, group_data['grouping']))
        # button.rightclicked.connect(lambda e: None)
        button.skill_image_name = group_data['nodes'][0]['image']
        button.tooltip = format_skill_tooltip(
                self, group_data['skill'][0], group_data, 0, 'space')
        layout.addWidget(button, 0, 0, 1, 2, alignment=AHCENTER | ABOTTOM)
        self.widgets.build['space_skills'][group_data['career']][id_offset] = button
        button = create_item_button(self)
        button.clicked.connect(lambda id=id_offset + 1: skill_callback_space(
                self, group_data['career'], id, group_data['grouping']))
        # button.rightclicked.connect(lambda e: None)
        button.skill_image_name = group_data['nodes'][1]['image']
        button.tooltip = format_skill_tooltip(
                self, group_data['skill'][1], group_data, 1, 'space')
        layout.addWidget(button, 1, 0, alignment=ATOP)
        self.widgets.build['space_skills'][group_data['career']][id_offset + 1] = button
        button = create_item_button(self)
        button.clicked.connect(lambda id=id_offset + 2: skill_callback_space(
                self, group_data['career'], id, group_data['grouping']))
        # button.rightclicked.connect(lambda e: None)
        button.skill_image_name = group_data['nodes'][2]['image']
        button.tooltip = format_skill_tooltip(
                self, group_data['skill'][2], group_data, 2, 'space')
        layout.addWidget(button, 1, 1, alignment=ATOP)
        self.widgets.build['space_skills'][group_data['career']][id_offset + 2] = button
    return layout


def create_skill_button_ground(self, group_data: dict, id: int, node_id: int) -> ItemButton:
    """
    Creates ground skill button and returns it

    Parameters:
    - :param group_data: skill group data
    - :param id: index of the skill node in self.widgets and self.build
    - :param node_id: 0 or 1 for first or second node
    """
    button = create_item_button(self)
    button.clicked.connect(lambda: skill_callback_ground(self, group_data['tree'], id))
    # button.rightclicked.connect(lambda e: None)
    button.skill_image_name = group_data['nodes'][node_id]['image']
    button.tooltip = format_skill_tooltip(
            self, group_data['nodes'][node_id]['name'], group_data, node_id, 'ground')
    self.widgets.build['ground_skills'][group_data['tree']][id] = button
    return button


def create_bonus_bar_segment(
        self, bar: str, index: int, style: str = 'bonus_bar',
        style_override: dict = {}) -> QPushButton:
    """
    Creates segment of bar showing the spent skill points.

    Parameters:
    - :param bar: identifies the bar ("tac" / "sci" / "eng" / "ground")
    - :param index: index of the segment within the bar
    - :param style: style key
    - :param style_override: overrides style specified by self.theme
    """
    seg = QPushButton()
    seg.setEnabled(False)
    seg.setCheckable(True)
    seg.setStyleSheet(get_style_class(self, 'QPushButton', style, style_override))
    seg.setFixedSize(7 * self.config['ui_scale'], 21 * self.config['ui_scale'])
    self.widgets.skill_bonus_bars[bar][index] = seg
    return seg


def create_bonus_bar_space(self, career: str, layout: GridLayout, column: int):
    """
    Creates bonus bar for space career and inserts it into the given layout.

    Parameters:
    - :param career: "tac" / "eng" / "sci"
    - :param layout: layout to insert the bar into
    - :param column: column of the layout to use
    """
    segment_index = 0
    button_index = 0
    for row in range(29, 5, -1):
        if row % 6 == 0:
            button = create_item_button(self)
            button.clicked.connect(lambda i=button_index: skill_unlock_callback(self, career, i))
            layout.addWidget(button, row, column, alignment=AHCENTER)
            self.widgets.build['skill_unlocks'][career][button_index] = button
            button_index += 1
        else:
            segment = create_bonus_bar_segment(self, career, segment_index)
            layout.addWidget(segment, row, column, alignment=AHCENTER)
            segment_index += 1
    for row in range(5, 1, -1):
        segment = create_bonus_bar_segment(self, career, segment_index)
        layout.addWidget(segment, row, column, alignment=AHCENTER)
        segment_index += 1
    button = create_item_button(self)
    button.clicked.connect(lambda: skill_unlock_callback(self, career, 4))
    layout.addWidget(button, 1, column, alignment=AHCENTER)
    self.widgets.build['skill_unlocks'][career][4] = button


def create_annotated_slider(
        self, default_value: int = 1, min: int = 0, max: int = 3,
        style: str = 'slider', style_override_slider: dict = {}, style_override_label: dict = {},
        callback: Callable = lambda v: v) -> QHBoxLayout:
    """
    Creates Slider with label to display the current value.

    Parameters:
    - :param default_value: start value for the slider
    - :param min: lowest value of the slider
    - :param max: highest value of the slider
    - :param style: key for self.theme -> default style
    - :param style_override_slider: style dict to override default style
    - :param style_override_label: style dict to override default style
    - :param callback: callable to be attached to the valueChanged signal of the slider; will be \
    passed value the slider was moved to; must return value that the label should be set to

    :return: layout with slider
    """
    def label_updater(new_value):
        if isinstance(callback, CALLABLE):
            new_text = callback(new_value)
            slider_label.setText(str(new_text))

    layout = QHBoxLayout()
    layout.setContentsMargins(0, 0, 0, 3)
    layout.setSpacing(self.theme['defaults']['margin'])
    slider_label = create_label(
            self, '', style, style_override=style_override_label)
    layout.addWidget(slider_label, alignment=AVCENTER)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(min, max)
    slider.setSingleStep(1)
    slider.setPageStep(1)
    slider.setValue(default_value)
    slider.setTickPosition(QSlider.TickPosition.NoTicks)
    slider.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
    slider.setSizePolicy(SMINMAX)
    slider.setStyleSheet(get_style_class(self, 'QSlider', style, style_override_slider))
    slider.valueChanged.connect(label_updater)
    layout.addWidget(slider, stretch=1, alignment=AVCENTER)
    label_updater(default_value)
    return layout
