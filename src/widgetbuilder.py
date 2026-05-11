from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QCompleter, QFrame, QLabel, QLineEdit, QPushButton, QSizePolicy, QSlider)
from .constants import ACENTER, ATOP, AVCENTER, CALLABLE, SMAXMAX, SMAXMIN, SMINMAX
from .theme import AppTheme
from .widgets import HBoxLayout, ItemButton, VBoxLayout


def create_frame2(
        theme: AppTheme, style: str = 'frame', style_override: dict = {},
        size_policy: QSizePolicy | None = None) -> QFrame:
    """
    Creates a frame with default styling

    Parameters:
    - :param theme: reference to AppTheme
    - :param style: key for theme, determines style preset
    - :param style_override: style dict to override preset style
    - :param size_policy: size policy of the frame

    :return: configured QFrame
    """
    frame = QFrame()
    frame.setStyleSheet(theme.get_style(style, style_override))
    frame.setSizePolicy(size_policy if size_policy is not None else SMAXMAX)
    return frame


def create_label2(theme: AppTheme, text: str, style: str = 'label', style_override={}) -> QLabel:
    """
    Creates a label according to style with parent.

    Parameters:
    - :param theme: reference to AppTheme
    - :param text: text to be shown on the label
    - :param style: key for theme, determines style preset
    - :param style_override: style dict to override preset style

    :return: configured QLabel
    """
    label = QLabel()
    label.setText(text)
    label.setStyleSheet(theme.get_style_class('QLabel', style, style_override))
    label.setSizePolicy(SMAXMAX)
    if 'font' in style_override:
        label.setFont(theme.get_font(style, style_override['font']))
    else:
        label.setFont(theme.get_font(style))
    return label


def create_button_series2(
        theme: AppTheme, buttons: dict[str, dict], style: str = 'button', shape: str = 'row',
        separator: str = '', ret: bool = False) -> (
            VBoxLayout | HBoxLayout | tuple[VBoxLayout | HBoxLayout, list[QPushButton]]):
    """
    Creates a row / column of buttons.

    Parameters:
    - :param theme: reference to AppTheme
    - :param buttons: dictionary containing button details
        - key "default" contains style override for all buttons (optional)
        - all other keys represent one button, key will be the text on the button; value for the
        key contains dict with details for the specific button (all optional)
            - "callback": callable that will be called on button click
            - "style": individual style override dict
            - "toggle": True or False when button should be a toggle button, None when it should
                be a normal button; the bool value indicates the default state of the button
            - "stretch": stretch value for the button
            - "align": alignment flag for button
    - :param style: key for theme, determines style preset
    - :param shape: row / column
    - :param separator: string seperator displayed between buttons (optional)
    - :param ret: set to true to return list of created buttons along with layout

    :return: populated VBoxlayout / HBoxlayout
    """
    if 'default' in buttons:
        defaults = theme.merge_style(theme[style], buttons.pop('default'))
    else:
        defaults = theme[style]

    if shape == 'column':
        layout = VBoxLayout()
    else:
        shape = 'row'
        layout = HBoxLayout()

    if separator != '':
        sep_style = {
            'color': defaults['color'], 'margin': 0, 'padding': 0, 'background': '#00000000'}

    button_list = []
    for i, (name, detail) in enumerate(buttons.items()):
        if 'style' in detail:
            button_style = theme.merge_style(defaults, detail['style'])
        else:
            button_style = defaults
        toggle_button = detail['toggle'] if 'toggle' in detail else None
        bt = create_button2(theme, name, style, button_style, toggle_button)
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
        if separator != '' and i < (len(buttons) - 1):
            sep_label = create_label2(theme, separator, 'label', sep_style)
            sep_label.setSizePolicy(SMAXMIN)
            layout.addWidget(sep_label, alignment=ACENTER)

    if ret:
        return layout, button_list
    else:
        return layout


def create_button2(
        theme: AppTheme, text: str, style: str = 'button', style_override: dict = {},
        toggle: bool = None):
    """
    Creates a button according to style with parent.

    Parameters:
    - :param theme: reference to AppTheme
    - :param text: text to be shown on the button
    - :param style: key for theme, determines style preset
    - :param style_override: style dict to override preset style
    - :param toggle: True or False when button should be a toggle button, None when it should be a \
    normal button; the bool value indicates the default state of the button

    :return: configured QPushButton
    """
    button = QPushButton(text)
    button.setStyleSheet(theme.get_style_class('QPushButton', style, style_override))
    if 'font' in style_override:
        button.setFont(theme.get_font(style, style_override['font']))
    else:
        button.setFont(theme.get_font(style))
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setSizePolicy(SMAXMAX)
    if isinstance(toggle, bool):
        button.setCheckable(True)
        button.setChecked(toggle)
    return button


def create_item_button2(theme: AppTheme) -> ItemButton:
    """
    Creates Item Button.

    Parameters:
    - :param theme: reference to AppTheme
    """
    label = create_label2(theme, '', 'infobox')
    frame = create_frame2(theme, 'infobox_frame')
    margin = theme['defaults']['csp'] * theme.scale
    layout = VBoxLayout(margin)
    layout.addWidget(label, alignment=ATOP)
    frame.setLayout(layout)
    button = ItemButton(
        theme.opt.box_width, theme.opt.box_height, theme['item'], label, frame,
        margin + theme['defaults']['bw'] * theme.scale)
    return button


def create_combo_box2(
        theme: AppTheme, style: str = 'combobox', editable: bool = False,
        size_policy: QSizePolicy = None, style_override: dict[str] = {},
        class_: type[QComboBox] = QComboBox) -> QComboBox:
    """
    Creates a combobox with given style and returns it.

    Parameters:
    - :param theme: reference to AppTheme
    - :param style: key for theme, determines style preset
    - :param editable: set to True to make combobox editable
    - :param size_policy: size policy for combobox
    - :param style_override: style dict to override preset style
    - :param class_: custom constructor for combobox; must be QCombobox or subclass

    :return: styled QCombobox
    """
    combo_box = class_()
    combo_box.setStyleSheet(theme.get_style_class('QComboBox', style, style_override))
    if 'font' in style_override:
        font = theme.get_font(style, style_override['font'])
    else:
        font = theme.get_font(style)
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
        combo_box.completer().popup().setStyleSheet(theme.get_style_class('QListView', 'popup'))
        combo_box.completer().popup().setFont(font)
        combo_box.lineEdit().setFont(font)
    return combo_box


def create_entry2(
        theme: AppTheme, default_value='', validator: QValidator | None = None,
        style: str = 'entry', style_override: dict = {}, placeholder: str = '') -> QLineEdit:
    """
    Creates an entry widget and styles it.

    Parameters:
    - :param theme: reference to AppTheme
    - :param default_value: default value for the entry
    - :param validator: validator to validate entered characters against
    - :param style: key for theme, determines style preset
    - :param style_override: style dict to override preset style
    - :param placeholder: placeholder shown when entry is empty

    :return: styled QLineEdit
    """
    entry = QLineEdit(default_value)
    entry.setValidator(validator)
    entry.setPlaceholderText(placeholder)
    entry.setStyleSheet(theme.get_style_class('QLineEdit', style, style_override))
    if 'font' in style_override:
        entry.setFont(theme.get_font(style, style_override['font']))
    else:
        entry.setFont(theme.get_font(style))
    entry.setCursor(Qt.CursorShape.IBeamCursor)
    entry.setSizePolicy(SMAXMAX)
    return entry


def create_checkbox2(
        theme: AppTheme, style: str = 'checkbox', style_override: dict = {}) -> QCheckBox:
    """
    Creates checkbox and styles it.

    Parameters:
    - :param theme: reference to AppTheme
    - :param style: key for theme, determines style preset
    - :param style_override: style dict to override preset style
    """
    checkbox = QCheckBox()
    checkbox.setStyleSheet(theme.get_style_class('QCheckBox', style, style_override))
    return checkbox


def create_annotated_slider2(
        theme: AppTheme, default_value: int = 1, min: int = 0, max: int = 3,
        style: str = 'slider', style_override_slider: dict = {}, style_override_label: dict = {},
        callback: Callable = lambda v: v) -> HBoxLayout:
    """
    Creates Slider with label to display the current value.

    Parameters:
    - :param theme: reference to AppTheme
    - :param default_value: start value for the slider
    - :param min: lowest value of the slider
    - :param max: highest value of the slider
    - :param style: key for theme, determines style preset
    - :param style_override_slider: style dict to override preset style
    - :param style_override_label: style dict to override preset style
    - :param callback: callable to be attached to the valueChanged signal of the slider; will be \
    passed value the slider was moved to; must return value that the label should be set to

    :return: layout with slider
    """
    def label_updater(new_value):
        if isinstance(callback, CALLABLE):
            new_text = callback(new_value)
            slider_label.setText(str(new_text))

    layout = HBoxLayout(margins=(0, 0, 0, 3), spacing=theme['defaults']['margin'])
    slider_label = create_label2(theme, '', style, style_override=style_override_label)
    layout.addWidget(slider_label, alignment=AVCENTER)
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(min, max)
    slider.setSingleStep(1)
    slider.setPageStep(1)
    slider.setValue(default_value)
    slider.setTickPosition(QSlider.TickPosition.NoTicks)
    slider.setFocusPolicy(Qt.FocusPolicy.WheelFocus)
    slider.setSizePolicy(SMINMAX)
    slider.setStyleSheet(theme.get_style_class('QSlider', style, style_override_slider))
    slider.setFixedHeight(22)
    slider.valueChanged.connect(label_updater)
    layout.addWidget(slider, stretch=1, alignment=AVCENTER)
    label_updater(default_value)
    return layout
