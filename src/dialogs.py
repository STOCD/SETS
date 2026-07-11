from PySide6.QtCore import QObject, Qt
from PySide6.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QWidget

from .theme import AppTheme
from .constants import ALEFT, ARIGHT, ATOP, AVCENTER, SMAXMAX, SMINMAX, SMINMIN
from .widgetbuilder import create_button2, create_frame2, create_label2


class DialogsWrapper(QObject):
    """Contains simple, multi-purpose dialogs"""

    def __init__(self, parent_window: QWidget, theme: AppTheme):
        """
        Parameters:
        - :param parent_window: window to center dialog on
        - :param theme: AppTheme
        """
        super().__init__()
        self._theme: AppTheme = theme
        self._confirm_dialog: QDialog = QDialog(parent_window, modal=True)
        self._icon_label_c: QLabel
        self._message_label_c: QLabel
        self.build_confirmation_dialog()

    def build_confirmation_dialog(self):
        """Creates layout for confirmation dialog"""
        thick = self._theme['app']['frame_thickness']
        item_spacing = self._theme['defaults']['isp']
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(thick, thick, thick, thick)
        dialog_frame = create_frame2(self._theme, size_policy=SMINMIN)
        main_layout.addWidget(dialog_frame)
        dialog_layout = QVBoxLayout()
        dialog_layout.setContentsMargins(thick, thick, thick, thick)
        dialog_layout.setSpacing(thick)
        content_frame = create_frame2(self._theme, size_policy=SMINMIN)
        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(item_spacing)
        content_layout.setAlignment(ATOP)

        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(2 * thick)
        self._icon_label_c = create_label2(self._theme, '')
        top_layout.addWidget(self._icon_label_c, alignment=ALEFT | AVCENTER)
        self._message_label_c = create_label2(self._theme, '')
        self._message_label_c.setWordWrap(True)
        self._message_label_c.setSizePolicy(SMINMAX)
        self._message_label_c.setTextFormat(Qt.TextFormat.RichText)
        top_layout.addWidget(self._message_label_c, stretch=1)
        content_layout.addLayout(top_layout)

        content_frame.setLayout(content_layout)
        dialog_layout.addWidget(content_frame, stretch=1)

        seperator = create_frame2(self._theme, style='light_frame', size_policy=SMINMAX)
        seperator.setFixedHeight(1)
        dialog_layout.addWidget(seperator)
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(thick)
        cancel_button = create_button2(self._theme, 'Cancel')
        cancel_button.clicked.connect(lambda: self._confirm_dialog.done(0))
        button_layout.addWidget(cancel_button, alignment=ARIGHT)
        ok_button = create_button2(self._theme, 'OK')
        ok_button.clicked.connect(lambda: self._confirm_dialog.done(1))
        button_layout.addWidget(ok_button, alignment=ALEFT)
        dialog_layout.addLayout(button_layout)
        dialog_frame.setLayout(dialog_layout)

        self._confirm_dialog.setStyleSheet(self._theme.get_style('dialog_window'))
        self._confirm_dialog.setSizePolicy(SMAXMAX)
        self._confirm_dialog.setLayout(main_layout)

    def confirm(self, title: str, message: str, icon: str = 'info') -> int:
        """
        Asks user for confirmation. Returns `1` if the user confirms, `0` if the use rejects.

        Parameters:
        - :param title: title of the confirmation dialog
        - :param message: message to be displayed
        - :param icon: ("warning" or) "info" (or "error")
        """
        self._confirm_dialog.setWindowTitle('SETS - ' + title)
        self._message_label_c.setText(message)
        icon_size = self._theme.opt.default_box_height * self._theme.scale
        self._icon_label_c.setPixmap(self._theme.icons[icon].pixmap(icon_size))
        return self._confirm_dialog.exec()
