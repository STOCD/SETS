import os
from pathlib import Path

from PySide6.QtCore import QByteArray, QSettings


class SETSConfig():

    __slots__ = ('autosave_filename', 'box_height', 'box_width', 'config_dir', 'config_subfolders',
                 'home_dir', 'link_discord', 'link_downloads', 'link_github', 'link_website',
                 'settings_file', 'ui_scale')

    def __init__(self):
        self.autosave_filename: str = 'autosave.json'
        self.box_height: int = 64
        self.box_width: int = 49
        self.config_dir: Path = Path()
        self.config_subfolders: dict[str, Path | None] = {
            'library': None,
            'cache': None,
            'cargo': None,
            'images': None,
            'ship_images': None,
            'backups': None,
            'auto_backups': None
        }
        self.home_dir: Path = Path()
        self.link_discord: str = 'https://discord.gg/kxwHxbsqzF'
        self.link_downloads: str = 'https://github.com/STOCD/SETS/releases'
        self.link_github: str = 'https://github.com/STOCD'
        self.link_website: str = 'https://stobuilds.com/apps/sets'
        self.settings_file: str = 'SETS_settings.ini'
        self.ui_scale: float = 1.0

    def __repr__(self):
        return f'<SETS-Config config_dir={self.config_dir} box_height={self.box_height} ...>'


class SETSSettings():

    __slots__ = ('_settings', 'default_mark', 'default_save_format', 'default_rarity',
                 'picker_relative', 'pref_backup', 'state__geometry', 'ui_scale')

    def __init__(self, settings_file_path: Path):
        self.default_mark: str = ''
        self.default_save_format: str = 'JSON',
        self.default_rarity: str = 'Common',
        self.picker_relative: int = 0
        self.pref_backup: int = 0

        self.state__geometry: QByteArray = QByteArray()

        if os.name == 'nt':
            self._settings = QSettings(str(settings_file_path), QSettings.Format.IniFormat)
        else:
            self._settings = QSettings(str(settings_file_path), QSettings.Format.NativeFormat)

        self.load_settings()

    def load_settings(self):
        """
        Loads settings from settings file given in constructor into attributes.
        """
        for setting in self.__slots__:
            if setting.startswith('_'):
                continue
            setting_id = setting.replace('__', '/')
            if self._settings.contains(setting_id):
                item_type = type(getattr(self, setting))
                if item_type is list:
                    settings_item: list = getattr(self, setting)
                    if len(settings_item) > 0:
                        list_element_type = type(settings_item[0])
                    else:
                        list_element_type = str
                    item_list = self._settings.value(setting_id, type=list)
                    if list_element_type is bool:
                        items = [True if el == 'true' else False for el in item_list]
                        setattr(self, setting, items)
                    else:
                        setattr(self, setting, [list_element_type(el) for el in item_list])
                else:
                    setattr(self, setting, self._settings.value(setting_id, type=item_type))

    def store_settings(self):
        """
        Stores settings from attributes to settings file given in constructor.
        """
        for setting in self.__slots__:
            if not setting.startswith('_'):
                setting_id = setting.replace('__', '/')
                self._settings.setValue(setting_id, getattr(self, setting))

    def set(self, setting_name: str, value):
        """
        Sets setting `setting_name` to `value`. Only use when direct assignment cannot be used
        (e.g. inside a lambda function).
        """
        setattr(self, setting_name, value)

    def set_ui_scale(self, new_value: int) -> str:
        """
        Calculates `new_value` / 50 and stores it to `ui_scale`. Returns the calculated value.

        Parameters:
        - :param new_value: 50 times the ui scale percentage
        """
        setting_value = round(new_value / 50, 2)
        self.ui_scale = setting_value
        return f'{setting_value:.2f}'

    def __repr__(self):
        return f'<SETS-Settings "{self._settings.fileName()}">'
