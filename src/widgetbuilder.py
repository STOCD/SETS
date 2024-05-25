from types import FunctionType, BuiltinFunctionType, MethodType

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QSizePolicy, QVBoxLayout

from .style import get_style, get_style_class, merge_style, theme_font

CALLABLE = (FunctionType, BuiltinFunctionType, MethodType)

SMINMIN = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
SMAXMAX = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
SMAXMIN = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
SMINMAX = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

ATOP = Qt.AlignmentFlag.AlignTop
ABOTTOM = Qt.AlignmentFlag.AlignBottom
ARIGHT = Qt.AlignmentFlag.AlignRight
ALEFT = Qt.AlignmentFlag.AlignLeft
ACENTER = Qt.AlignmentFlag.AlignCenter
AVCENTER = Qt.AlignmentFlag.AlignVCenter
AHCENTER = Qt.AlignmentFlag.AlignHCenter


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
