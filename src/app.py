import os

from PySide6.QtCore import QSettings
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import (
        QApplication, QFrame, QGridLayout, QHBoxLayout, QTabWidget, QVBoxLayout, QWidget)

from .iofunc import get_asset_path, load_icon
from .widgetbuilder import AHCENTER, ALEFT, ARIGHT, ATOP, AVCENTER, SMINMAX, SMINMIN
from .widgets import ImageLabel, WidgetStorage

# only for developing; allows to terminate the qt event loop with keyboard interrupt
from signal import signal, SIGINT, SIG_DFL
signal(SIGINT, SIG_DFL)


class SETS():

    from .callbacks import enter_splash, exit_splash, splash_text
    from .iofunc import create_folder
    from .style import create_style_sheet, get_style, get_style_class
    from .subwindows import create_splash_screen
    from .widgetbuilder import create_button, create_button_series, create_frame, create_label

    app_dir = None

    versions = ('', '')  # (release version, dev version)

    config = {}  # see main.py for contents

    settings: QSettings  # see main.py for defaults

    # stores widgets that need to be accessed from outside their creating function
    widgets: WidgetStorage

    def __init__(self, theme, args, path, config, versions):
        """
        Creates new Instance of SETS

        Parameters:
        - :param version: version of the app
        - :param theme: dict -> default theme
        - :param args: command line arguments
        - :param path: absolute path to directory containing the main.py file
        - :param config: app configuration (!= settings these are not changed by the user)
        """
        self.versions = versions
        self.theme = theme
        self.args = args
        self.app_dir = path
        self.config = config
        self.widgets = WidgetStorage()
        self.init_settings()
        self.init_config()
        self.init_environment()
        self.app, self.window = self.create_main_window()
        self.setup_main_layout()
        self.window.show()

    def run(self) -> int:
        """
        Runs the event loop.

        :return: exit code of event loop
        """
        return self.app.exec()

    def init_settings(self):
        """
        Prepares settings. Loads stored settings. Saves current settings for next startup.
        """
        settings_path = os.path.abspath(self.app_dir + self.config['settings_path'])
        self.settings = QSettings(settings_path, QSettings.Format.IniFormat)
        for setting, value in self.config['default_settings'].items():
            if self.settings.value(setting, None) is None:
                self.settings.setValue(setting, value)

    def init_config(self):
        """
        Prepares config.
        """
        config_folder = os.path.abspath(
                self.app_dir + self.config['config_folder_path'])
        self.config['config_folder_path'] = config_folder
        for folder, path in self.config['config_subfolders'].items():
            self.config['config_subfolders'][folder] = config_folder + path
        self.config['ui_scale'] = self.settings.value('ui_scale', type=float)

    def init_environment(self):
        """
        Creates required folders if necessary.
        """
        self.create_folder(self.config['config_folder_path'])
        self.create_folder(self.config['config_subfolders']['library'])
        self.create_folder(self.config['config_subfolders']['cache'])
        self.create_folder(self.config['config_subfolders']['backups'])
        self.create_folder(self.config['config_subfolders']['images'])
        self.create_folder(self.config['config_subfolders']['ship_images'])

    def main_window_close_callback(self, event):
        """
        Executed when application is closed.
        """
        window_geometry = self.window.saveGeometry()
        self.settings.setValue('geometry', window_geometry)
        event.accept()

    # ----------------------------------------------------------------------------------------------
    # GUI functions below
    # ----------------------------------------------------------------------------------------------

    def create_main_window(self, argv=[]) -> tuple[QApplication, QWidget]:
        """
        Creates and initializes main window

        :return: QApplication, QWidget
        """
        app = QApplication(argv)
        font_database = QFontDatabase()
        font_database.addApplicationFont(get_asset_path('Overpass-Bold.ttf', self.app_dir))
        font_database.addApplicationFont(get_asset_path('Overpass-Medium.ttf', self.app_dir))
        font_database.addApplicationFont(get_asset_path('Overpass-Regular.ttf', self.app_dir))
        app.setStyleSheet(self.create_style_sheet(self.theme['app']['style']))
        window = QWidget()
        window.setWindowIcon(load_icon('SETS_icon_small.png', self.app_dir))
        window.setWindowTitle('STO Equipment and Trait Selector')
        if self.settings.value('geometry'):
            window.restoreGeometry(self.settings.value('geometry'))
        window.closeEvent = self.main_window_close_callback
        return app, window

    def setup_main_layout(self):
        """
        Creates the main layout and places it into the main window.
        """
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        background_frame = self.create_frame(
                style_override={'background-color': '@sets'}, size_policy=SMINMIN)
        layout.addWidget(background_frame)
        self.window.setLayout(layout)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        banner = ImageLabel(get_asset_path('sets_banner.png', self.app_dir), (2880, 126))
        main_layout.addWidget(banner)
        tabber_layout = QVBoxLayout()
        tabber_layout.setContentsMargins(8, 8, 8, 8)
        tabber_layout.setSpacing(0)
        splash_tabber = QTabWidget()
        splash_tabber.setStyleSheet(self.get_style_class('QTabWidget', 'tabber'))
        splash_tabber.tabBar().setStyleSheet(self.get_style_class('QTabBar', 'tabber_tab'))
        splash_tabber.setSizePolicy(SMINMIN)
        self.widgets.splash_tabber = splash_tabber
        tabber_layout.addWidget(splash_tabber)
        main_layout.addLayout(tabber_layout)
        background_frame.setLayout(main_layout)

        content_frame = self.create_frame()
        splash_frame = self.create_frame()
        splash_tabber.addTab(content_frame, 'Main')
        splash_tabber.addTab(splash_frame, 'Splash')
        self.setup_splash(splash_frame)

        content_layout = QVBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        menu_layout = QGridLayout()
        menu_layout.setContentsMargins(3, 3, 3, 0)
        menu_layout.setSpacing(0)
        menu_layout.setAlignment(ATOP)
        menu_layout.setColumnStretch(0, 2)
        menu_layout.setColumnStretch(1, 5)
        menu_layout.setColumnStretch(2, 2)
        left_button_group = {
            'Save': {'callback': lambda: None},
            'Open': {'callback': lambda: None},
            'Clear': {'callback': lambda: None},
            'Clear all': {'callback': lambda: None}
        }
        menu_layout.addLayout(self.create_button_series(left_button_group), 0, 0, ALEFT | ATOP)
        center_button_group = {
            'default': {'font': ('Overpass', 16, 'medium')},
            'SPACE': {'callback': lambda: None, 'stretch': 1, 'size': SMINMAX},
            'GROUND': {'callback': lambda: None, 'stretch': 1, 'size': SMINMAX},
            'SPACE SKILLS': {'callback': lambda: None, 'stretch': 1, 'size': SMINMAX},
            'GROUND SKILLS': {'callback': lambda: None, 'stretch': 1, 'size': SMINMAX}
        }
        center_buttons = self.create_button_series(center_button_group, 'heavy_button')
        menu_layout.addLayout(center_buttons, 0, 1)
        right_button_group = {
            'Export': {'callback': lambda: None},
            'Settings': {'callback': lambda: None},
        }
        menu_layout.addLayout(self.create_button_series(right_button_group), 0, 2, ARIGHT | ATOP)
        content_layout.addLayout(menu_layout)
        content_frame.setLayout(content_layout)

    def setup_splash(self, frame: QFrame):
        """
        Creates Splash screen.
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        center_frame = self.create_frame(size_policy=SMINMIN)
        center_layout = QVBoxLayout()
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(self.theme['defaults']['csp'])
        loading_image = ImageLabel(get_asset_path('sets_loading.png', self.app_dir), (1, 1))
        center_layout.addWidget(loading_image)
        loading_label = self.create_label('Loading: ...', 'label_subhead')
        self.widgets.loading_label = loading_label
        center_layout.addWidget(loading_label, alignment=ALEFT)
        center_frame.setLayout(center_layout)
        left_frame = self.create_frame(size_policy=SMINMIN)
        layout.addWidget(left_frame, 3)
        layout.addWidget(center_frame, 2, AVCENTER)
        right_frame = self.create_frame(size_policy=SMINMIN)
        layout.addWidget(right_frame, 3)
        frame.setLayout(layout)
