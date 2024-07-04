from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
        QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
        QSizePolicy, QVBoxLayout)

from .constants import ALEFT, CALLABLE, SMAXMAX, SMAXMIN, SMINMAX
from .style import get_style, get_style_class, merge_style, theme_font
from .widgets import ItemButton


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


def create_combo_box(self, style: str = 'combobox', style_override: dict = {}) -> QComboBox:
    """
    Creates a combobox with given style and returns it.

    Parameters:
    - :param style: key for self.theme -> default style
    - :param style_override: style dict to override default style

    :return: styled QCombobox
    """
    combo_box = QComboBox()
    combo_box.setStyleSheet(get_style_class(self, 'QComboBox', style, style_override))
    if 'font' in style_override:
        combo_box.setFont(theme_font(self, style, style_override['font']))
    else:
        combo_box.setFont(theme_font(self, style))
    combo_box.setSizePolicy(SMINMAX)
    combo_box.setCursor(Qt.CursorShape.PointingHandCursor)
    combo_box.view().setCursor(Qt.CursorShape.PointingHandCursor)
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


def create_item_button(self) -> ItemButton:
    """
    Creates Item Button.
    """
    label = create_label(self, '', 'infobox')
    button = ItemButton(self.box_width, self.box_height, get_style(self, 'item'), label)
    return button


def create_build_section(self, label_text: str, button_count: int) -> QGridLayout:
    """
    Creates a block of item buttons below a label.

    Parameters:
    - :param label_text: text to be displayed above the buttons
    - :param button_count: number of buttons to be created
    """
    layout = QGridLayout()
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(self.theme['defaults']['margin'] * self.config['ui_scale'])
    label = create_label(self, label_text, style_override={'margin': 0})
    label.sizePolicy().setRetainSizeWhenHidden(True)
    layout.addWidget(label, 0, 0, 1, button_count, alignment=ALEFT)
    for i in range(button_count):
        button = create_item_button(self)
        button.clicked.connect(self.picker)
        button.rightclicked.connect(lambda data, i=i: print(f'Rightclicked on {label_text} #{i}'))
        layout.addWidget(button, 1, i)
    return layout
