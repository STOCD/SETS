import os
from pathlib import Path

from PySide6.QtCore import QDir, QPoint, Qt, QThread
from PySide6.QtGui import QCloseEvent, QFontDatabase, QTextOption
from PySide6.QtWidgets import (
    QApplication, QFrame, QPlainTextEdit, QPushButton, QScrollArea, QTabWidget, QWidget)

from .buildloader import BuildLoader
from .buildmanager import BuildManager
from .cargomanager import CargoManager
from .config import SETSConfig, SETSSettings
from .constants import (
    ABOTTOM, AHCENTER, ALEFT, ARIGHT, ATOP, AVCENTER, CAREERS, FACTIONS, GROUND_BOFF_SPECS, MARKS,
    PRIMARY_SPECS, RARITIES, SCROLLOFF, SCROLLON, SECONDARY_SPECS, SMAXMAX, SMAXMIN, SMINMAX,
    SMINMIN)
from .contextmenu import ContextMenu
from .downloader import Downloader
from .exportwindow import ExportWindow
from .imagemanager import ImageManager
from .iofunc import delete_folder_contents, load_icon, open_url, store_json
from .picker import ItemEditor, Picker, ShipSelector
from .splash import SplashScreen
from .textedit import format_skill_tooltip
from .theme import AppTheme
from .widgetbuilder import (
    create_annotated_slider2, create_button2, create_button_series2, create_checkbox2,
    create_combo_box2, create_entry2, create_frame2, create_item_button2, create_label2)
from .widgets import (
    Cache, DoffCombobox, GridLayout, HBoxLayout, ImageLabel, ItemButton, ShipButton, ShipImage,
    Tabbers, TooltipLabel, VBoxLayout, WidgetStorage)

# only for developing; allows to terminate the qt event loop with keyboard interrupt
# from signal import signal, SIGINT, SIG_DFL
# signal(SIGINT, SIG_DFL)


class SETS():

    from .datafunctions import backup_cargo_data, empty_build, init_backend
    from .splash import enter_splash, exit_splash, splash_text
    from .style import prepare_tooltip_css

    app_dir = None
    # (release version, dev version)
    versions = ('', '')
    # stores widgets that need to be accessed from outside their creating function
    widgets: WidgetStorage
    # stores refined cargo data
    cache: Cache
    # stores current build
    build: dict
    # for picking items
    picker_window: Picker
    # for selecting ships
    ship_selector_window: ShipSelector
    # for editing equipment items
    edit_window: ItemEditor
    # context menu for equipment
    context_menu: ContextMenu
    # shows markdown export
    export_window: ExportWindow

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
        self.app_dir2: Path = Path(path)
        self.widgets = WidgetStorage()
        self.cache = Cache()
        self.config: SETSConfig = SETSConfig()
        self.config.config_dir = self.get_config_dir_path()
        self.settings = SETSSettings(self.config.config_dir / self.config.settings_file)
        self.init_config()
        QDir.addSearchPath('local_folder', os.path.join(path, 'local'))
        self.theme2: AppTheme = AppTheme(self.config.ui_scale)
        self.prepare_tooltip_css()
        self.init_environment()
        self.downloader = Downloader(
            self.config.config_subfolders['images'],
            self.config.config_subfolders['ship_images'])
        self.cargo: CargoManager = CargoManager(
            self.config.config_subfolders, self.app_dir2, self.downloader, self.settings,
            self.theme2)
        self.images: ImageManager = ImageManager(
            Path(self.config.config_subfolders['images']),
            Path(self.config.config_subfolders['ship_images']),
            self.app_dir2, self.cargo, self.downloader)
        self.build2: BuildManager = BuildManager(
            self.cargo, self.images, self.config.autosave_path, self.theme2.tooltips)
        self.splash: SplashScreen = SplashScreen()
        self.tabbers: Tabbers = Tabbers()
        self.app, self.window = self.create_main_window()
        self.cache_icons()
        self.building = True
        self.build = self.empty_build()
        self.cargo.load_static_data()
        self.setup_main_layout()
        self.build_loader: BuildLoader = BuildLoader(
            self.build2, self.cargo, self.config, self.settings, self.window)
        self.export_window = ExportWindow(self.theme2, self.window, self.build2, self.cargo)
        self.picker_window: Picker = Picker(self.theme2, self.window, self.settings, self.images)
        self.picker_window.dialog_result.connect(self.build2.handle_picker_result)
        self.edit_window: ItemEditor = ItemEditor(self.theme2, self.window)
        self.edit_window.dialog_result.connect(self.build2.finish_item_edit)
        self.ship_selector_window: ShipSelector = ShipSelector(self.theme2, self.window)
        self.ship_selector_window.dialog_result.connect(self.build2.finish_ship_pick)
        self.context_menu: ContextMenu = ContextMenu(self.theme2, self.build2, self.cargo)
        self.context_menu.edit_slot.connect(self.edit_window.edit_item)
        self.window.show()
        self.init_backend()

    def run(self) -> int:
        """
        Runs the event loop.

        :return: exit code of event loop
        """
        return self.app.exec()

    def setup_config_dir(self, dir_path: Path) -> None | OSError:
        """
        Sets up config directory.
        """
        try:
            dir_path.mkdir(exist_ok=True)
            for folder in self.config.config_subfolders:
                folder_path = dir_path / folder
                folder_path.mkdir(exist_ok=True)
                self.config.config_subfolders[folder] = folder_path
        except OSError as e:
            return e

    def get_config_dir_path(self, override: str | None = None) -> Path | None:
        """
        Identifies appropriate config directory and returns path to that directory. Returns `None`
        if no usable config dir could be identified.
        """
        if override is not None:
            config_dir = Path(override)
            if self.setup_config_dir(config_dir) is None:
                return config_dir
            else:
                return

        if os.name == 'nt':
            for env_name in ('APPDATA', 'USERPROFILE'):
                config_basedir = os.getenv(env_name)
                if config_basedir is not None:
                    config_dir = Path(config_basedir, 'SETS')
                    if self.setup_config_dir(config_dir) is None:
                        return config_dir
        else:
            config_basedir = os.getenv('XDG_CONFIG_HOME')
            if config_basedir is not None:
                config_dir = Path(config_basedir, 'SETS')
                if self.setup_config_dir(config_dir) is None:
                    return config_dir
            home_dir = os.getenv('HOME')
            if home_dir is None:
                return
            config_dir = Path(home_dir, '.config', 'SETS')
            if self.setup_config_dir(config_dir) is None:
                return config_dir
            config_dir = Path(home_dir, '.sets')
            if self.setup_config_dir(config_dir) is None:
                return config_dir

    def init_config(self):
        """
        Prepares config.
        """
        self.config.autosave_path = self.config.config_dir / self.config.autosave_filename
        self.config.ui_scale = self.settings.ui_scale
        # TODO move these to new theme
        self.box_width = self.config.box_width * self.config.ui_scale * 0.8
        self.box_height = self.config.box_height * self.config.ui_scale * 0.8

    def init_environment(self):
        """
        Creates external files before starting the app.
        """
        if not self.config.autosave_path.exists():
            store_json(self.empty_build(), str(self.config.autosave_path))

    def cache_icons(self):
        """
        Loads static icons.
        """
        self.cache.icons['copy'] = load_icon('copy.png', self.app_dir2)
        self.cache.icons['paste'] = load_icon('paste.png', self.app_dir2)
        self.cache.icons['clear'] = load_icon('clear.png', self.app_dir2)
        self.cache.icons['edit'] = load_icon('edit.png', self.app_dir2)
        self.cache.icons['link'] = load_icon('external_link.png', self.app_dir2)
        self.cache.icons['dual_cannons'] = load_icon('DC_icon.svg', self.app_dir2, size=(16, 24.5))
        icon_size = (self.theme2.opt.box_width * 1.2, self.theme2.opt.box_width * 1.2)
        self.cache.icons['ground'] = load_icon('ground_icon.png', self.app_dir2, icon_size)
        icon_size = (self.theme2.opt.box_width, self.theme2.opt.box_width)
        self.cache.icons['tac'] = load_icon('tac_icon.png', self.app_dir2, icon_size)
        self.cache.icons['sci'] = load_icon('sci_icon.png', icon_size)
        self.cache.icons['eng'] = load_icon('eng_icon.png', icon_size)
        self.cache.icons['tac-small'] = load_icon('tac-small.svg', self.app_dir2, size=(25, 25))
        self.cache.icons['sci-small'] = load_icon('sci-small.svg', self.app_dir2, size=(25, 25))
        icon_size = (self.theme2.opt.box_height, self.theme2.opt.box_width * 182 / 106)
        self.cache.icons['STOCD'] = load_icon('stocd.png', self.app_dir2, icon_size)
        self.theme2.icons = self.cache.icons

    def main_window_close_callback(self, event: QCloseEvent):
        """
        Executed when application is closed.
        """
        window_geometry = self.window.saveGeometry()
        self.settings.state__geometry = window_geometry
        self.autosave()
        self.settings.store_settings()
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
        font_database.addApplicationFont(self.app_dir2 / 'local' / 'Overpass-VariableFont_wght.ttf')
        font_database.addApplicationFont(self.app_dir2 / 'local' / 'RobotoMono-Regular.ttf')
        app.setStyleSheet(self.theme2.create_style_sheet(self.theme2['app']['style']))
        window = QWidget()
        window.setWindowIcon(load_icon('SETS_icon_small.png', self.app_dir2))
        window.setWindowTitle('STO Equipment and Trait Selector')
        if self.settings.state__geometry:
            window.restoreGeometry(self.settings.state__geometry)
        window.closeEvent = self.main_window_close_callback
        app.focusWindowChanged.connect(self.hide_tooltips)
        QThread.currentThread().setPriority(QThread.Priority.TimeCriticalPriority)
        return app, window

    def picker(
            self, environment: str, build_key: str, build_subkey: int, button: ItemButton,
            equipment: bool = False, boff_id: int | None = None):
        """
        opens dialog to select item, stores it to build and updates item button

        Parameters:
        - :param items: iterable of items available to pick from
        - :param environment: space or ground
        - :param build_key: key to self.build[environment]; for storing picked item
        - :param build_subkey: index of the item within its build_key (category)
        - :param button: reference to the button clicked
        - :param equipment: set to True to show rarity, mark, and modifier selector (optional)
        - :param boff_id: id of the boff; only set when picking boff abilities! (optional)
        """
        modifiers = {}
        image_suffix = ''
        if equipment:
            items = self.cargo.equipment[build_key].keys()
            modifiers = self.cargo.modifiers[build_key]
        elif build_key == 'boffs':
            if environment == 'space':
                profession, specialization = self.build2['space']['boff_specs'][boff_id]
                if specialization == 'Temporal Operative':
                    specialization = 'Temporal'
            else:
                profession = self.build['ground']['boff_profs'][boff_id]
                specialization = self.build['ground']['boff_specs'][boff_id]
            items = self.cargo.boff_abilities[environment][profession][build_subkey]
            if specialization != '':
                items = items + self.cache.boff_abilities[environment][specialization][build_subkey]
        elif build_key == 'starship_traits':
            items = self.cargo.starship_traits.keys()
            image_suffix = '__space__starship_traits'
        elif 'traits' in build_key:
            if environment == 'space':
                items = self.cargo.space_traits[build_key].keys()
            else:
                items = self.cargo.ground_traits[build_key].keys()
            image_suffix = f'__{environment}__{build_key}'
        else:
            items = []
        if self.settings.picker_relative == 1:
            pos = button.mapToGlobal(QPoint(0, 0))
        else:
            pos = None
        self.picker_window.pick_item(items, pos, equipment, modifiers, image_suffix)

    def setup_main_layout(self):
        """
        Creates the main layout and places it into the main window.
        """
        # master layout: banner, borders and splash screen
        layout = VBoxLayout()
        background_frame = create_frame2(
            self.theme2, style_override={'background-color': '@sets'}, size_policy=SMINMIN)
        layout.addWidget(background_frame)
        self.window.setLayout(layout)
        main_layout = VBoxLayout()
        banner = ImageLabel(self.app_dir / 'local' / 'sets_banner.png', (2880, 126))
        main_layout.addWidget(banner)
        frame_width = 8 * self.theme2.scale
        tabber_layout = VBoxLayout(margins=frame_width)
        splash_tabber = QTabWidget()
        splash_tabber.setStyleSheet(self.theme2.get_style_class('QTabWidget', 'tabber'))
        splash_tabber.tabBar().setStyleSheet(self.theme2.get_style_class('QTabBar', 'tabber_tab'))
        splash_tabber.setSizePolicy(SMINMIN)
        self.splash.tabber = splash_tabber
        tabber_layout.addWidget(splash_tabber)
        main_layout.addLayout(tabber_layout)
        background_frame.setLayout(main_layout)
        content_frame = create_frame2(self.theme2)
        splash_frame = create_frame2(self.theme2)
        splash_tabber.addTab(content_frame, 'Main')
        splash_tabber.addTab(splash_frame, 'Splash')
        self.setup_splash(splash_frame)

        content_layout = GridLayout()
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 4)

        margin = 3 * self.theme2.scale
        menu_layout = GridLayout(margins=(margin, margin, margin, 0))
        menu_layout.setColumnStretch(0, 2)
        menu_layout.setColumnStretch(1, 5)
        menu_layout.setColumnStretch(2, 2)
        left_button_group = {
            'Save': {'callback': self.build_loader.save_build_callback},
            'Open': {'callback': self.build_loader.load_build_callback},
            'Clear Current Tab': {'callback': lambda: self.build2.clear_build_callback(
                self.tabbers.build_tabber.currentIndex())},
            'Clear All Tabs': {'callback': self.build2.clear_all}
        }
        menu_layout.addLayout(
            create_button_series2(self.theme2, left_button_group), 0, 0, alignment=ALEFT | ATOP)
        center_button_group = {
            'default': {'font': ('Overpass', 16, 'medium')},
            'SPACE': {'callback': lambda: self.tabbers.switch(0), 'stretch': 1, 'size': SMINMAX},
            'GROUND': {'callback': lambda: self.tabbers.switch(1), 'stretch': 1, 'size': SMINMAX},
            'SPACE SKILLS': {
                'callback': lambda: self.tabbers.switch(2),
                'stretch': 1,
                'size': SMINMAX
            },
            'GROUND SKILLS': {
                'callback': lambda: self.tabbers.switch(3),
                'stretch': 1,
                'size': SMINMAX
            }
        }
        center_buttons = create_button_series2(self.theme2, center_button_group, 'heavy_button')
        menu_layout.addLayout(center_buttons, 0, 1)
        right_button_group = {
            'Export': {'callback': self.export_window.invoke},
            'Settings': {'callback': lambda: self.tabbers.switch(5)},
        }
        menu_layout.addLayout(
            create_button_series2(self.theme2, right_button_group), 0, 2, alignment=ARIGHT | ATOP)
        content_layout.addLayout(menu_layout, 0, 0, 1, 2)

        # sidebar
        sidebar = create_frame2(self.theme2, size_policy=SMINMIN)
        sidebar_layout = GridLayout()

        sidebar_tabber = QTabWidget()
        sidebar_tabber.setStyleSheet(self.theme2.get_style_class('QTabWidget', 'tabber'))
        sidebar_tabber.tabBar().setStyleSheet(self.theme2.get_style_class('QTabBar', 'tabber_tab'))
        sidebar_tabber.setSizePolicy(SMINMIN)
        self.tabbers.sidebar_tabber = sidebar_tabber
        for tab_name in ('space', 'ground', 'space_skills', 'ground_skills', 'empty', 'settings'):
            tab_frame = create_frame2(self.theme2)
            sidebar_tabber.addTab(tab_frame, tab_name)
            self.tabbers.sidebar_frames.append(tab_frame)
        self.setup_ship_frame()
        sidebar_layout.addWidget(sidebar_tabber, 0, 0)

        character_tabber = QTabWidget()
        character_tabber.setStyleSheet(self.theme2.get_style_class('QTabWidget', 'tabber'))
        character_tabber.tabBar().setStyleSheet(
            self.theme2.get_style_class('QTabBar', 'tabber_tab'))
        character_tabber.setSizePolicy(SMINMAX)
        self.tabbers.character_tabber = character_tabber
        char_frame = create_frame2(self.theme2)
        self.setup_character_frame(char_frame)
        character_tabber.addTab(char_frame, 'char')
        empty_frame = create_frame2(self.theme2)
        character_tabber.addTab(empty_frame, 'empty')
        settings_frame = create_frame2(self.theme2)
        character_tabber.addTab(settings_frame, 'settings')
        self.tabbers.character_frames = [char_frame, empty_frame, settings_frame]
        sidebar_layout.addWidget(character_tabber, 1, 0)

        seperator = create_frame2(self.theme2, size_policy=SMAXMIN, style_override={
            'background-color': '@sets', 'margin-top': '@isp', 'margin-bottom': '@isp'})
        seperator.setFixedWidth(self.theme2['defaults']['sep'] * self.theme2.scale)
        sidebar_layout.addWidget(seperator, 0, 1, 2, 1)
        sidebar.setLayout(sidebar_layout)
        content_layout.addWidget(sidebar, 1, 0)

        # build section
        build_tabber = QTabWidget()
        build_tabber.setStyleSheet(self.theme2.get_style_class('QTabWidget', 'tabber'))
        build_tabber.tabBar().setStyleSheet(self.theme2.get_style_class('QTabBar', 'tabber_tab'))
        build_tabber.setSizePolicy(SMINMIN)
        self.tabbers.build_tabber = build_tabber
        build_tab_names = (
            'space_build', 'ground_build', 'space_skills', 'ground_skills', 'library', 'settings')
        for tab_name in build_tab_names:
            tab_frame = create_frame2(self.theme2)
            build_tabber.addTab(tab_frame, tab_name)
            self.tabbers.build_frames.append(tab_frame)
        content_layout.addWidget(build_tabber, 1, 1)
        self.setup_space_build_frame()
        self.setup_ground_build_frame()
        self.setup_space_skill_frame()
        self.setup_ground_skill_frame()
        self.setup_settings_frame()

        content_frame.setLayout(content_layout)

    def setup_ship_frame(self):
        """
        Creates ship info frame
        """
        frame = self.widgets.sidebar_frames[0]
        csp = self.theme2['defaults']['csp'] * self.theme2.scale
        layout = VBoxLayout(margins=csp, spacing=csp)

        image_frame = create_frame2(self.theme2, size_policy=SMINMIN)
        image_layout = GridLayout()
        ship_image = ShipImage()
        ship_image.setSizePolicy(SMINMIN)
        self.build2.ship.image = ship_image
        image_layout.addWidget(ship_image, 0, 0)
        image_frame.setLayout(image_layout)
        layout.addWidget(image_frame, stretch=1)

        ship_frame = create_frame2(self.theme2, size_policy=SMINMIN)
        ship_layout = GridLayout(spacing=csp)
        ship_layout.setRowStretch(4, 1)
        ship_layout.setColumnStretch(2, 1)
        ship_selector = ShipButton('<Pick Ship>')
        ship_selector.setSizePolicy(SMINMAX)
        ship_selector.setStyleSheet(
            self.theme2.get_style_class('ShipButton', 'button', override={'margin': 0}))
        ship_selector.setFont(self.theme2.get_font(font_spec='@subhead'))
        ship_selector.clicked.connect(self.ship_selector_window.pick_ship)
        self.build2.ship.button = ship_selector
        ship_layout.addWidget(ship_selector, 0, 0, 1, 4, alignment=ATOP)
        tier_label = create_label2(self.theme2, 'Ship Tier:')
        ship_layout.addWidget(tier_label, 1, 0)
        tier_combo = create_combo_box2(self.theme2)
        tier_combo.currentTextChanged.connect(self.build2.tier_callback)
        tier_combo.setSizePolicy(SMAXMAX)
        self.build2.ship.tier = tier_combo
        ship_layout.addWidget(tier_combo, 1, 1, alignment=ALEFT)
        dc_tooltip = create_label2(self.theme2, 'Can equip Dual Cannons', 'label_tooltip')
        dc_label = TooltipLabel('', dc_tooltip)
        dc_label.setPixmap(self.theme2.icons['dual_cannons'])
        dc_label_size_policy = dc_label.sizePolicy()
        dc_label_size_policy.setRetainSizeWhenHidden(True)
        dc_label.setSizePolicy(dc_label_size_policy)
        self.build2.ship.dc = dc_label
        ship_layout.addWidget(dc_label, 1, 2, alignment=ARIGHT)
        info_button = create_button2(self.theme, 'Ship Info', style_override={'margin': 0})
        info_button.clicked.connect(self.build2.ship_info_callback)
        ship_layout.addWidget(info_button, 1, 3, alignment=ARIGHT)
        name_label = create_label2(self.theme2, 'Ship Name:')
        ship_layout.addWidget(name_label, 2, 0)
        name_entry = create_entry2(self.theme2)
        name_entry.editingFinished.connect(
            lambda: self.build2.set('space', 'ship_name', value=name_entry.text()))
        self.build2.ship.name = name_entry
        name_entry.setSizePolicy(SMINMAX)
        ship_layout.addWidget(name_entry, 2, 1, 1, 3)
        desc_label = create_label2(self.theme2, 'Build Description:')
        ship_layout.addWidget(desc_label, 3, 0, 1, 4)
        desc_edit = QPlainTextEdit()
        desc_edit.setSizePolicy(SMINMIN)
        desc_edit.setStyleSheet(self.theme2.get_style_class('QPlainTextEdit', 'textedit'))
        desc_edit.setFont(self.theme2.get_font('textedit'))
        desc_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        desc_edit.textChanged.connect(lambda: self.build2.set(
            'space', 'ship_desc', value=desc_edit.toPlainText(), autosave=False))
        self.build2.ship.desc = desc_edit
        ship_layout.addWidget(desc_edit, 4, 0, 1, 4)
        ship_frame.setLayout(ship_layout)
        layout.addWidget(ship_frame, stretch=2)
        frame.setLayout(layout)

    def create_build_section(
            self, label_text: str, button_count: int, environment: str, build_key: str,
            is_equipment: bool = False, label_store: str = '') -> GridLayout:
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
        layout = GridLayout(spacing=self.theme2['defaults']['margin'] * self.theme2.scale)
        label = create_label2(self.theme2, label_text, style_override={'margin': (0, 0, 6, 0)})
        label_size_policy = label.sizePolicy()
        label_size_policy.setRetainSizeWhenHidden(True)
        label.setSizePolicy(label_size_policy)
        layout.addWidget(label, 0, 0, 1, button_count, alignment=ALEFT)
        widget_storage = self.build2.space if environment == 'space' else self.build2.ground
        if label_store != '':
            setattr(widget_storage, label_store, label)
        for i in range(button_count):
            button = create_item_button2(self.theme2)
            button.clicked.connect(lambda subkey=i, bt=button: self.picker(
                environment, build_key, subkey, bt, is_equipment))
            button.rightclicked.connect(lambda event, subkey=i: self.context_menu.invoke(
                event, build_key, subkey, environment))
            getattr(widget_storage, build_key)[i] = button
            layout.addWidget(button, 1, i, alignment=ALEFT)
        return layout

    def create_boff_station_space(
            self, profession: str, specialization: str = '', boff_id: int = 0) -> GridLayout:
        """
        Creates a block of item buttons with label / Combobox representing boff station.

        Parameters:
        - :param profession: "Tactical", "Science", "Engineering" or "Universal"
        - :param specialization: specialization of the seat; empty if it has no specialization
        - :param boff_id: identifies the boff station
        """
        layout = GridLayout(spacing=self.theme2['defaults']['margin'] * self.theme2.scale)
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
        widget_storage = self.build2.space
        label_layout = HBoxLayout(spacing=self.config.ui_scale * 3)
        icon_label = TooltipLabel('', create_label2(self.theme2, '', 'label_tooltip'))
        widget_storage.boff_label_icons[boff_id] = icon_label
        label_layout.addWidget(icon_label, alignment=ALEFT)
        icon_label.hide()
        label = create_combo_box2(
            self.theme2, size_policy=SMAXMAX, style_override=self.theme['boff_combo'])
        label.currentTextChanged.connect(
            lambda new: self.build2.boff_profession_callback_space(boff_id, new))
        label.addItems(label_options)
        label_size_policy = label.sizePolicy()
        label_size_policy.setRetainSizeWhenHidden(True)
        label.setSizePolicy(label_size_policy)
        widget_storage.boff_labels[boff_id] = label
        label_layout.addWidget(label, alignment=ALEFT)
        layout.addLayout(label_layout, 0, 0, 1, 4, alignment=ALEFT)
        for i in range(4):
            button = create_item_button2(self.theme2)
            button.sizePolicy().setRetainSizeWhenHidden(True)
            button.clicked.connect(lambda subkey=i, bt=button: self.picker(
                'space', 'boffs', subkey, bt, boff_id=boff_id))
            button.rightclicked.connect(lambda event, subkey=i: self.context_menu.invoke(
                event, 'boffs', subkey, 'space', boff_id))
            layout.addWidget(button, 1, i, alignment=ALEFT)
            widget_storage.boffs[boff_id][i] = button
        return layout

    def create_boff_station_ground(self, boff_id: int) -> VBoxLayout:
        """
        Creates a block of item buttons with label / Combobox representing boff station.

        Parameters:
        - :param boff_id: identifies the boff station
        """
        widget_storage = self.build2.ground
        m = self.theme2['defaults']['margin'] * self.theme2.scale
        layout = VBoxLayout(spacing=m)
        label_layout = HBoxLayout(spacing=m)
        label_layout.setAlignment(ALEFT)
        prof_label = create_combo_box2(self.theme2, style_override=self.theme['boff_combo'])
        prof_label.currentTextChanged.connect(
            lambda new: self.build2.boff_label_callback_ground(boff_id, 'boff_profs', new))
        prof_label.addItems(CAREERS)
        widget_storage.boff_profs[boff_id] = prof_label
        label_layout.addWidget(prof_label)
        spec_label = create_combo_box2(self.theme2, style_override=self.theme['boff_combo'])
        spec_label.currentTextChanged.connect(
            lambda new: self.build2.boff_label_callback_ground(boff_id, 'boff_specs', new))
        spec_label.addItems(GROUND_BOFF_SPECS)
        widget_storage['boff_specs'][boff_id] = spec_label
        label_layout.addWidget(spec_label)
        layout.addLayout(label_layout)
        button_layout = HBoxLayout(spacing=m)
        button_layout.setAlignment(ALEFT)
        for i in range(4):
            button = create_item_button2(self.theme2)
            button.clicked.connect(lambda subkey=i, bt=button: self.picker(
                'ground', 'boffs', subkey, bt, boff_id=boff_id))
            button.rightclicked.connect(lambda event, subkey=i: self.context_menu.invoke(
                event, 'boffs', subkey, 'ground', boff_id))
            button_layout.addWidget(button)
            widget_storage.boffs[boff_id][i] = button
        layout.addLayout(button_layout)
        return layout

    def create_personal_trait_section(self, environment: str) -> GridLayout:
        """
        Creates build section for personal traits

        Parameters:
        - :param environment: "space" / "ground"
        """
        layout = GridLayout(spacing=self.theme2['defaults']['margin'] * self.theme2.scale)
        label = create_label2(
            self.theme2, 'Personal Traits', style_override={'margin': (0, 0, 6, 0)})
        layout.addWidget(label, 0, 0, 1, 4, alignment=ALEFT)
        widget_storage = self.build2.space if environment == 'space' else self.build2.ground
        for row in range(3):
            for col in range(4):
                i = row * 4 + col
                button = create_item_button2(self)
                button.clicked.connect(
                    lambda subkey=i, bt=button: self.picker(environment, 'traits', subkey, bt))
                button.rightclicked.connect(lambda event, subkey=i: self.context_menu.invoke(
                    event, 'traits', subkey, environment))
                layout.addWidget(button, row + 1, col, alignment=ALEFT)
                widget_storage.traits[i] = button
        # Last button is for innate trait and should not be clickable
        button.setEnabled(False)
        button.set_style(self.theme2['item_dark'])
        return layout

    def create_starship_trait_section(self) -> GridLayout:
        """
        Creates build section for starship traits
        """
        layout = GridLayout(spacing=self.theme2['defaults']['margin'] * self.theme2.scale)
        label = create_label2(
            self.theme2, 'Starship Traits', style_override={'margin': (0, 0, 6, 0)})
        label.sizePolicy().setRetainSizeWhenHidden(True)
        layout.addWidget(label, 0, 0, 1, 4, alignment=ALEFT)
        widget_storage = self.build2.space
        for col in range(5):
            button = create_item_button2(self.theme2)
            button.sizePolicy().setRetainSizeWhenHidden(True)
            button.clicked.connect(
                lambda subkey=col, bt=button: self.picker('space', 'starship_traits', subkey, bt))
            button.rightclicked.connect(lambda event, subkey=col: self.context_menu.invoke(
                event, 'starship_traits', subkey, 'space'))
            layout.addWidget(button, 1, col, alignment=ALEFT)
            widget_storage.starship_traits[col] = button
        for col in range(2):
            button = create_item_button2(self.theme2)
            button.sizePolicy().setRetainSizeWhenHidden(True)
            button.clicked.connect(lambda subkey=col + 5, bt=button: self.picker(
                'space', 'starship_traits', subkey, bt))
            button.rightclicked.connect(lambda event, subkey=col + 5: self.context_menu.invoke(
                event, 'starship_traits', subkey, 'space'))
            layout.addWidget(button, 2, col, alignment=ALEFT)
            widget_storage.starship_traits[col + 5] = button
        return layout

    def create_doff_section(self, environment: str) -> GridLayout:
        """
        Creates duty officer section

        Parameters:
        - :param environment: "space" / "ground"
        """
        doff_layout = GridLayout(spacing=self.theme2['defaults']['bw'] * self.theme2.scale)
        doff_layout.setColumnStretch(1, 1)
        widget_storage = self.build2.space if environment == 'space' else self.build2.ground
        for i in range(6):
            spec_combo = create_combo_box2(self.theme2, style_override=self.theme['doff_combo'])
            spec_combo.currentTextChanged.connect(
                lambda spec, id=i: self.build2.doff_spec_callback(spec, environment, id))
            doff_layout.addWidget(spec_combo, i, 0)
            widget_storage.doffs_spec[i] = spec_combo
            variant_combo = create_combo_box2(
                self.theme2, style_override=self.theme['doff_combo'], class_=DoffCombobox)
            variant_combo.currentTextChanged.connect(
                lambda variant, id=i: self.build2.doff_variant_callback(variant, environment, id))
            doff_layout.addWidget(variant_combo, i, 1)
            widget_storage.doffs_variant[i] = variant_combo
        return doff_layout

    def create_skill_group_space(self, group_data: dict, id_offset: int) -> GridLayout:
        """
        Creates a skill group (3 related skill nodes) in appropriate shape

        Parameters:
        - :param group_data: skill group data
        - :param id_offset: index of the first skill node in self.widgets and self.build
        """
        layout = GridLayout(spacing=self.theme['defaults']['csp'] * self.config.ui_scale)
        # one skill with 3 ranks
        if group_data['grouping'] == 'column':
            for index, node in enumerate(group_data['nodes']):
                button = create_item_button2(self.theme2)
                skill_id = id_offset + index
                button.clicked.connect(lambda id=skill_id: self.build2.skill_callback_space(
                    group_data['career'], id, 'column'))
                button.skill_image_name = node['image']
                button.tooltip = format_skill_tooltip(
                    group_data['skill'], group_data, index, 'space', self.theme2.tooltips)
                self.build2.skills.space[group_data['career']][id_offset + index] = button
                layout.addWidget(button, index, 0)
        # == 'pair+1': one skill with 2 ranks and one sub-skill with 1 rank
        # == 'separate': 3 separate skills
        else:
            button = create_item_button2(self.theme2)
            button.clicked.connect(lambda id=id_offset: self.build2.skill_callback_space(
                group_data['career'], id, group_data['grouping']))
            button.skill_image_name = group_data['nodes'][0]['image']
            button.tooltip = format_skill_tooltip(
                group_data['skill'][0], group_data, 0, 'space', self.theme2.tooltips)
            layout.addWidget(button, 0, 0, 1, 2, alignment=AHCENTER | ABOTTOM)
            self.build2.skills.space[group_data['career']][id_offset] = button
            button = create_item_button2(self.theme2)
            button.clicked.connect(lambda id=id_offset + 1: self.build2.skill_callback_space(
                group_data['career'], id, group_data['grouping']))
            button.skill_image_name = group_data['nodes'][1]['image']
            button.tooltip = format_skill_tooltip(
                group_data['skill'][1], group_data, 1, 'space', self.theme2.tooltips)
            layout.addWidget(button, 1, 0, alignment=ATOP)
            self.build2.skills.space[group_data['career']][id_offset + 1] = button
            button = create_item_button2(self.theme2)
            button.clicked.connect(lambda id=id_offset + 2: self.build2.skill_callback_space(
                group_data['career'], id, group_data['grouping']))
            button.skill_image_name = group_data['nodes'][2]['image']
            button.tooltip = format_skill_tooltip(
                group_data['skill'][2], group_data, 2, 'space', self.theme2.tooltips)
            layout.addWidget(button, 1, 1, alignment=ATOP)
            self.build2.skills.space[group_data['career']][id_offset + 2] = button
        return layout

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
        seg.setStyleSheet(self.theme2.get_style_class('QPushButton', style, style_override))
        seg.setFixedSize(7 * self.theme2.scale, 17 * self.theme2.scale)
        self.build2.skills.bonus_bars[bar][index] = seg
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
                button = create_item_button2(self.theme2)
                button.clicked.connect(
                    lambda i=button_index: self.build2.skill_unlock_callback(career, i))
                layout.addWidget(button, row, column, alignment=AHCENTER)
                self.build2.skills.unlocks[career][button_index] = button
                button_index += 1
            else:
                segment = self.create_bonus_bar_segment(career, segment_index)
                layout.addWidget(segment, row, column, alignment=AHCENTER)
                segment_index += 1
        for row in range(5, 1, -1):
            segment = self.create_bonus_bar_segment(career, segment_index)
            layout.addWidget(segment, row, column, alignment=AHCENTER)
            segment_index += 1
        button = create_item_button2(self.theme2)
        button.clicked.connect(lambda: self.build2.skill_unlock_callback(self, career, 4))
        layout.addWidget(button, 1, column, alignment=AHCENTER)
        self.build2.skills.unlocks[career][4] = button

    def create_skill_button_ground(self, group_data: dict, id: int, node_id: int) -> ItemButton:
        """
        Creates ground skill button and returns it

        Parameters:
        - :param group_data: skill group data
        - :param id: index of the skill node in self.widgets and self.build
        - :param node_id: 0 or 1 for first or second node
        """
        button = create_item_button2(self.theme2)
        button.clicked.connect(lambda: self.build2.skill_callback_ground(group_data['tree'], id))
        button.skill_image_name = group_data['nodes'][node_id]['image']
        button.tooltip = format_skill_tooltip(
            group_data['nodes'][node_id]['name'], group_data, node_id, 'ground',
            self.theme2.tooltips)
        self.build2.skills.ground[group_data['tree']][id] = button
        return button

    def setup_space_build_frame(self):
        """
        Creates space build layout
        """
        frame = self.tabbers.build_frames[0]
        isp = self.theme2['defaults']['isp'] * 2 * self.theme2.scale
        layout = GridLayout(margins=isp, spacing=isp)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(10, 1)
        layout.setRowStretch(7, 1)

        # Equipment
        fore_layout = self.create_build_section('Fore Weapons', 5, 'space', 'fore_weapons', True)
        layout.addLayout(fore_layout, 0, 1, alignment=ALEFT)
        aft_layout = self.create_build_section(
            'Aft Weapons', 5, 'space', 'aft_weapons', True, 'aft_weapons_label')
        layout.addLayout(aft_layout, 1, 1, alignment=ALEFT)
        exp_layout = self.create_build_section(
            'Experimental Weapon', 1, 'space', 'experimental', True, 'experimental_label')
        layout.addLayout(exp_layout, 2, 1, alignment=ALEFT)
        device_layout = self.create_build_section('Devices', 6, 'space', 'devices', True)
        layout.addLayout(device_layout, 3, 1, alignment=ALEFT)
        hangar_layout = self.create_build_section(
            'Hangars', 2, 'space', 'hangars', True, 'hangars_label')
        layout.addLayout(hangar_layout, 4, 1, alignment=ALEFT)
        sep1 = create_frame2(self.theme2, size_policy=SMAXMIN, style_override={
            'background-color': '@bg', 'margin-top': '@isp', 'margin-bottom': '@isp'})
        sep1.setFixedWidth(self.theme2['defaults']['sep'] * self.theme2.scale)
        layout.addWidget(sep1, 0, 2, 5, 1)

        deflector_layout = self.create_build_section('Deflector', 1, 'space', 'deflector', True)
        layout.addLayout(deflector_layout, 0, 3, alignment=ALEFT)
        secdef_layout = self.create_build_section(
            'Sec-Def', 1, 'space', 'sec_def', True, 'sec_def_label')
        layout.addLayout(secdef_layout, 1, 3, alignment=ALEFT)
        engine_layout = self.create_build_section('Engines', 1, 'space', 'engines', True)
        layout.addLayout(engine_layout, 2, 3, alignment=ALEFT)
        warp_layout = self.create_build_section('Warp Core', 1, 'space', 'core', True)
        layout.addLayout(warp_layout, 3, 3, alignment=ALEFT)
        shield_layout = self.create_build_section('Shield', 1, 'space', 'shield', True)
        layout.addLayout(shield_layout, 4, 3, alignment=ALEFT)
        sep2 = create_frame2(self.theme2, size_policy=SMAXMIN, style_override={
            'background-color': '@bg', 'margin-top': '@isp', 'margin-bottom': '@isp'})
        sep2.setFixedWidth(self.theme2['defaults']['sep'] * self.theme2.scale)
        layout.addWidget(sep2, 0, 4, 5, 1)

        uni_layout = self.create_build_section(
            'Universal Consoles', 3, 'space', 'uni_consoles', True, 'uni_consoles_label')
        layout.addLayout(uni_layout, 0, 5, alignment=ALEFT)
        eng_layout = self.create_build_section(
            'Engineering Consoles', 5, 'space', 'eng_consoles', True, 'eng_consoles_label')
        layout.addLayout(eng_layout, 1, 5, alignment=ALEFT)
        sci_layout = self.create_build_section(
            'Science Consoles', 5, 'space', 'sci_consoles', True, 'sci_consoles_label')
        layout.addLayout(sci_layout, 2, 5, alignment=ALEFT)
        tac_layout = self.create_build_section(
            'Tactical Consoles', 5, 'space', 'tac_consoles', True, 'tac_consoles_label')
        layout.addLayout(tac_layout, 3, 5, alignment=ALEFT)
        sep3 = create_frame2(self.theme2, size_policy=SMAXMIN, style_override={
            'background-color': '@bg', 'margin-top': '@isp', 'margin-bottom': '@isp'})
        sep3.setFixedWidth(self.theme2['defaults']['sep'] * self.theme2.scale)
        layout.addWidget(sep3, 0, 6, 5, 1)

        # Boffs
        boff_1_layout = self.create_boff_station_space('Universal', 'Miracle Worker', boff_id=0)
        layout.addLayout(boff_1_layout, 0, 7, alignment=ALEFT)
        boff_2_layout = self.create_boff_station_space('Universal', 'Command', boff_id=1)
        layout.addLayout(boff_2_layout, 1, 7, alignment=ALEFT)
        boff_3_layout = self.create_boff_station_space('Universal', 'Intelligence', boff_id=2)
        layout.addLayout(boff_3_layout, 2, 7, alignment=ALEFT)
        boff_4_layout = self.create_boff_station_space('Universal', 'Pilot', boff_id=3)
        layout.addLayout(boff_4_layout, 3, 7, alignment=ALEFT)
        boff_5_layout = self.create_boff_station_space('Universal', 'Temporal', boff_id=4)
        layout.addLayout(boff_5_layout, 4, 7, alignment=ALEFT)
        boff_6_layout = self.create_boff_station_space('Universal', boff_id=5)
        width_placeholder = create_combo_box2(self.theme2, size_policy=SMAXMAX)
        width_placeholder.addItem('Engineering / Miracle Worker')
        width_placeholder_sizepolicy = width_placeholder.sizePolicy()
        width_placeholder_sizepolicy.setRetainSizeWhenHidden(True)
        width_placeholder.setSizePolicy(width_placeholder_sizepolicy)
        width_placeholder.setFixedHeight(1)
        boff_6_layout.addWidget(width_placeholder, 2, 0, 1, 4)
        width_placeholder.hide()
        layout.addLayout(boff_6_layout, 5, 7, alignment=ALEFT)
        # no seperator here as the width placehoder takes care of it

        # Traits
        trait_layout = GridLayout(margins=0, spacing=isp)
        personal_trait_layout = self.create_personal_trait_section('space')
        trait_layout.addLayout(personal_trait_layout, 0, 0, alignment=ALEFT)
        starship_trait_layout = self.create_starship_trait_section()
        trait_layout.addLayout(starship_trait_layout, 1, 0)
        rep_trait_layout = self.create_build_section('Reputation Traits', 5, 'space', 'rep_traits')
        trait_layout.addLayout(rep_trait_layout, 2, 0)
        active_trait_layout = self.create_build_section(
            'Active Reputation Traits', 5, 'space', 'active_rep_traits')
        trait_layout.addLayout(active_trait_layout, 3, 0)
        layout.addLayout(trait_layout, 0, 9, 6, 1, alignment=ATOP)

        # Doffs
        spacing = self.theme2['defaults']['bw'] * self.theme2.scale
        doff_container = create_frame2(self.theme2, size_policy=SMINMAX)
        doff_container_layout = VBoxLayout(spacing=spacing * 2)
        doff_label = create_label2(self.theme2, 'Space Duty Officers')
        doff_container_layout.addWidget(doff_label, alignment=ALEFT)
        doff_frame = create_frame2(self.theme2, 'doff_frame', size_policy=SMINMAX)
        doff_frame_layout = VBoxLayout()
        doff_style_nullifier = create_frame2(self.theme2, size_policy=SMINMAX)
        doff_frame_layout.addWidget(doff_style_nullifier)
        doff_layout = self.create_doff_section('space')
        doff_style_nullifier.setLayout(doff_layout)
        doff_frame.setLayout(doff_frame_layout)
        doff_container_layout.addWidget(doff_frame)
        doff_container.setLayout(doff_container_layout)
        layout.addWidget(doff_container, 5, 1, 2, 5)

        frame.setLayout(layout)

    def setup_ground_build_frame(self):
        """
        Creates Ground build frame
        """
        frame = self.widgets.build_frames[1]
        isp = self.theme2['defaults']['isp'] * 2 * self.theme2.scale
        layout = GridLayout(margins=isp, spacing=isp)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(8, 1)
        layout.setRowStretch(5, 1)

        # Equipment
        modules_layout = self.create_build_section('Kit Modules', 6, 'ground', 'kit_modules', True)
        layout.addLayout(modules_layout, 0, 1, alignment=ALEFT)
        weapons_layout = self.create_build_section('Weapons', 2, 'ground', 'weapons', True)
        layout.addLayout(weapons_layout, 1, 1, alignment=ALEFT)
        devices_layout = self.create_build_section('Devices', 5, 'ground', 'ground_devices', True)
        layout.addLayout(devices_layout, 2, 1, alignment=ALEFT)
        sep1 = create_frame2(self.theme2, size_policy=SMAXMIN, style_override={
            'background-color': '@bg', 'margin-top': '@isp', 'margin-bottom': '@isp'})
        sep1.setFixedWidth(self.theme2['defaults']['sep'] * self.theme2.scale)
        layout.addWidget(sep1, 0, 2)
        kit_layout = self.create_build_section('Kit Frame', 1, 'ground', 'kit', True)
        layout.addLayout(kit_layout, 0, 3, alignment=ALEFT)
        armor_layout = self.create_build_section('Armor', 1, 'ground', 'armor', True)
        layout.addLayout(armor_layout, 1, 3, alignment=ALEFT)
        ev_layout = self.create_build_section('EV Suit', 1, 'ground', 'ev_suit', True)
        layout.addLayout(ev_layout, 2, 3, alignment=ALEFT)
        shield_layout = self.create_build_section('Shield', 1, 'ground', 'personal_shield', True)
        layout.addLayout(shield_layout, 3, 3, alignment=ALEFT)
        sep2 = create_frame2(self.theme2, size_policy=SMAXMIN, style_override={
            'background-color': '@bg', 'margin-top': '@isp', 'margin-bottom': '@isp'})
        sep2.setFixedWidth(self.theme2['defaults']['sep'] * self.theme2.scale)
        layout.addWidget(sep2, 0, 4)

        # Boffs
        boff_1_layout = self.create_boff_station_ground(boff_id=0)
        layout.addLayout(boff_1_layout, 0, 5, alignment=ALEFT)
        boff_2_layout = self.create_boff_station_ground(boff_id=1)
        layout.addLayout(boff_2_layout, 1, 5, alignment=ALEFT)
        boff_3_layout = self.create_boff_station_ground(boff_id=2)
        layout.addLayout(boff_3_layout, 2, 5, alignment=ALEFT)
        boff_4_layout = self.create_boff_station_ground(boff_id=3)
        layout.addLayout(boff_4_layout, 3, 5, alignment=ALEFT)
        sep3 = create_frame2(self.theme2, size_policy=SMAXMIN, style_override={
            'background-color': '@bg', 'margin-top': '@isp', 'margin-bottom': '@isp'})
        sep3.setFixedWidth(self.theme2['defaults']['sep'] * self.theme2.scale)
        layout.addWidget(sep3, 0, 6)

        # Traits
        trait_layout = GridLayout(margins=0, spacing=isp)
        personal_trait_layout = self.create_personal_trait_section('ground')
        trait_layout.addLayout(personal_trait_layout, 0, 0, alignment=ALEFT)
        rep_trait_layout = self.create_build_section('Reputation Traits', 5, 'ground', 'rep_traits')
        trait_layout.addLayout(rep_trait_layout, 1, 0)
        active_trait_layout = self.create_build_section(
            'Active Reputation Traits', 5, 'ground', 'active_rep_traits')
        trait_layout.addLayout(active_trait_layout, 2, 0)
        layout.addLayout(trait_layout, 0, 7, 4, 1, alignment=ATOP)

        # Doffs
        spacing = self.theme2['defaults']['bw'] * self.theme2.scale
        doff_container = create_frame2(self.theme2, size_policy=SMINMAX)
        doff_container_layout = VBoxLayout(spacing=spacing * 2)
        doff_label = create_label2(self.theme2, 'Ground Duty Officers')
        doff_container_layout.addWidget(doff_label, alignment=ALEFT)
        doff_frame = create_frame2(self.theme2, 'doff_frame', size_policy=SMINMAX)
        doff_frame_layout = VBoxLayout()
        doff_style_nullifier = create_frame2(self.theme2, size_policy=SMINMAX)
        doff_frame_layout.addWidget(doff_style_nullifier)
        doff_layout = self.create_doff_section('ground')
        doff_style_nullifier.setLayout(doff_layout)
        doff_frame.setLayout(doff_frame_layout)
        doff_container_layout.addWidget(doff_frame)
        doff_container.setLayout(doff_container_layout)
        layout.addWidget(doff_container, 4, 1, 1, 7)

        frame.setLayout(layout)

        # sidebar
        sidebar_frame = self.tabbers.sidebar_frames[1]
        csp = self.theme2['defaults']['csp'] * self.theme2.scale
        sidebar_layout = GridLayout(margins=(csp, isp, csp, csp), spacing=csp)
        sidebar_layout.setColumnStretch(0, 1)
        desc_label = create_label2(self.theme2, 'Build Description:')
        sidebar_layout.addWidget(desc_label, 0, 0)
        desc_edit = QPlainTextEdit()
        desc_edit.setStyleSheet(self.theme2.get_style_class('QPlainTextEdit', 'textedit'))
        desc_edit.setFont(self.theme2.get_font('textedit'))
        desc_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        desc_edit.textChanged.connect(lambda: self.build2.set(
            'ground', 'ground_desc', value=desc_edit.toPlainText(), autosave=False))
        self.build2.ground.desc = desc_edit
        sidebar_layout.addWidget(desc_edit, 1, 0)
        sidebar_frame.setLayout(sidebar_layout)

    def setup_character_frame(self, frame: QFrame):
        """
        Creates character customization area.
        """
        csp = self.theme2['defaults']['csp'] * self.theme2.scale
        layout = GridLayout(margins=csp, spacing=csp)
        layout.setColumnStretch(1, 1)
        seperator = create_frame2(self.theme2, size_policy=SMINMAX, style_override={
            'background-color': '@sets', 'margin': '@isp'})
        seperator.setFixedHeight(self.theme2['defaults']['sep'] * self.theme2.scale)
        layout.addWidget(seperator, 0, 0, 1, 2, alignment=ATOP)  # ATOP makes it respect the margin?
        char_name = create_entry2(self.theme2, placeholder='NAME')
        char_name.setAlignment(AHCENTER)
        char_name.setSizePolicy(SMINMAX)
        char_name.editingFinished.connect(
            lambda: self.build2.set('captain', 'name', value=char_name.text()))
        layout.addWidget(char_name, 1, 0, 1, 2)
        self.build2.character.name = char_name
        elite_label = create_label2(self.theme2, 'Elite Captain')
        layout.addWidget(elite_label, 2, 0, alignment=ARIGHT)
        elite_checkbox = create_checkbox2(self.theme2)
        elite_checkbox.checkStateChanged.connect(self.build2.elite_callback)
        layout.addWidget(elite_checkbox, 2, 1, alignment=ALEFT)
        self.build2.character.elite = elite_checkbox
        career_label = create_label2(self.theme2, 'Captain Career')
        layout.addWidget(career_label, 3, 0, alignment=ARIGHT)
        career_combo = create_combo_box2(self.theme2)
        career_combo.addItems({''} | CAREERS)
        career_combo.currentTextChanged.connect(
            lambda new_career: self.build2.set('captain', 'career', value=new_career))
        layout.addWidget(career_combo, 3, 1)
        self.build2.character.career = career_combo
        faction_label = create_label2(self.theme2, 'Faction')
        layout.addWidget(faction_label, 4, 0, alignment=ARIGHT)
        faction_combo = create_combo_box2(self.theme2)
        faction_combo.addItems({''} | FACTIONS)
        faction_combo.currentTextChanged.connect(self.build2.faction_combo_callback)
        layout.addWidget(faction_combo, 4, 1)
        self.build2.character.faction = faction_combo
        species_label = create_label2(self.theme2, 'Species')
        layout.addWidget(species_label, 5, 0, alignment=ARIGHT)
        species_combo = create_combo_box2(self.theme2)
        species_combo.addItems({''})
        species_combo.currentTextChanged.connect(self.build2.species_combo_callback)
        layout.addWidget(species_combo, 5, 1)
        self.build2.character.species = species_combo
        primary_label = create_label2(self.theme2, 'Primary Spec')
        layout.addWidget(primary_label, 6, 0, alignment=ARIGHT)
        primary_combo = create_combo_box2(self.theme2)
        primary_combo.addItems({''} | PRIMARY_SPECS)
        primary_combo.currentTextChanged.connect(
            lambda new_spec: self.build2.spec_combo_callback(True, new_spec))
        layout.addWidget(primary_combo, 6, 1)
        self.build2.character.primary = primary_combo
        secondary_label = create_label2(
            self.theme2, 'Secondary Spec', style_override={'margin-bottom': 0})
        layout.addWidget(secondary_label, 7, 0, alignment=ARIGHT)
        secondary_combo = create_combo_box2(self.theme2)
        secondary_combo.addItems({''} | PRIMARY_SPECS | SECONDARY_SPECS)
        secondary_combo.currentTextChanged.connect(
            lambda new_spec: self.build2.spec_combo_callback(False, new_spec))
        layout.addWidget(secondary_combo, 7, 1)
        self.build2.character.secondary = secondary_combo
        frame.setLayout(layout)

    def setup_space_skill_frame(self):
        """
        Creates Space skill GUI
        """
        frame = self.tabbers.build_frames[2]
        isp = self.theme2['defaults']['isp'] * self.theme2.scale
        csp = self.theme2['defaults']['csp'] * self.theme2.scale
        col_layout = GridLayout(margins=isp, spacing=csp)
        col_layout.setRowStretch(0, 1)
        col_layout.setColumnStretch(0, 3)
        col_layout.setColumnStretch(2, 1)
        scroll_frame = create_frame2(self.theme2)
        scroll_area = QScrollArea()
        scroll_area.setSizePolicy(SMINMIN)
        scroll_area.setHorizontalScrollBarPolicy(SCROLLOFF)
        scroll_area.setVerticalScrollBarPolicy(SCROLLON)
        scroll_area.setAlignment(AHCENTER)
        col_layout.addWidget(scroll_area, 0, 0)
        scroll_layout = GridLayout(margins=isp, spacing=isp * 4)
        scroll_layout.setVerticalSpacing(isp)
        scroll_layout.setColumnStretch(0, 1)
        scroll_layout.setColumnStretch(1, 1)
        scroll_layout.setColumnStretch(2, 1)
        scroll_layout.setColumnStretch(3, 1)
        scroll_layout.setColumnStretch(4, 1)
        scroll_layout.setColumnStretch(5, 1)

        # skill tree
        rank_texts = (
            'Lieutenant<br><small>(0 points required)</small>',
            'Lieutenant Commander<br><small>(5 points required)</small>',
            'Commander<br><small>(15 points required)</small>',
            'Captain<br><small>(25 points required)</small>',
            'Admiral<br><small>(35 points required)</small>'
        )
        sep_height = self.theme2['hr']['height'] * self.theme2.scale
        for rank, skill_groups in enumerate(self.cargo.skills['space']):
            header_layout = GridLayout(spacing=isp)
            left_sep = create_frame2(self.theme2, 'hr', size_policy=SMINMAX)
            left_sep.setFixedHeight(sep_height)
            header_layout.addWidget(left_sep, 0, 0, alignment=AVCENTER)
            rank_label = create_label2(self.theme2, rank_texts[rank], 'label_subhead')
            rank_label.setAlignment(AHCENTER)
            header_layout.addWidget(rank_label, 0, 1)
            right_sep = create_frame2(self.theme2, 'hr', size_policy=SMINMAX)
            right_sep.setFixedHeight(sep_height)
            header_layout.addWidget(right_sep, 0, 2, alignment=AVCENTER)
            scroll_layout.addLayout(header_layout, rank * 3, 0, 1, 6)
            for group_id, group_data in enumerate(skill_groups):
                id_offset = rank * 6 + (group_id % 2) * 3
                group_layout = self.create_skill_group_space(group_data, id_offset)
                scroll_layout.addLayout(group_layout, rank * 3 + 1, group_id)
            spacer = create_frame2(self.theme2)
            spacer.setFixedHeight(isp)
            scroll_layout.addWidget(spacer, rank * 3 + 2, 0)
        VBoxLayout().addWidget(spacer)
        scroll_frame.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_frame)
        seperator = create_frame2(self.theme2, size_policy=SMAXMIN, style_override={
            'background-color': '@sets'})
        seperator.setFixedWidth(self.theme2['defaults']['sep'] * self.theme2.scale)
        col_layout.addWidget(seperator, 0, 1)
        bonus_bar_container = create_frame2(self.theme2, size_policy=SMINMIN)

        # bonus bars
        bonus_bar_layout = GridLayout(margins=isp)
        bonus_bar_layout.setRowStretch(0, 1)
        bonus_bar_layout.setRowStretch(32, 1)
        self.create_bonus_bar_space('eng', bonus_bar_layout, 1)
        eng_label = create_label2(self.theme2, '', style='unlock_label')
        eng_label.setPixmap(self.theme2.icons['eng'])
        bonus_bar_layout.addWidget(eng_label, 30, 1, alignment=AHCENTER)
        eng_count = create_label2(self.theme2, '0', 'label_subhead')
        bonus_bar_layout.addWidget(eng_count, 31, 1, alignment=AHCENTER)
        self.build2.skills.count_labels['eng'] = eng_count
        self.create_bonus_bar_space('sci', bonus_bar_layout, 2)
        sci_label = create_label2(self.theme2, '', style='unlock_label')
        sci_label.setPixmap(self.theme2.icons['sci'])
        bonus_bar_layout.addWidget(sci_label, 30, 2, alignment=AHCENTER)
        sci_count = create_label2(self.theme2, '0', 'label_subhead')
        bonus_bar_layout.addWidget(sci_count, 31, 2, alignment=AHCENTER)
        self.build2.skills.count_labels['sci'] = sci_count
        self.create_bonus_bar_space('tac', bonus_bar_layout, 3)
        tac_label = create_label2(self.theme2, '', style='unlock_label')
        tac_label.setPixmap(self.theme2.icons['tac'])
        bonus_bar_layout.addWidget(tac_label, 30, 3, alignment=AHCENTER)
        tac_count = create_label2(self.theme2, '0', 'label_subhead')
        bonus_bar_layout.addWidget(tac_count, 31, 3, alignment=AHCENTER)
        self.build2.skills.count_labels['tac'] = tac_count
        bonus_bar_container.setLayout(bonus_bar_layout)
        col_layout.addWidget(bonus_bar_container, 0, 2)
        frame.setLayout(col_layout)

        # sidebar
        sidebar_frame = self.tabbers.sidebar_frames[2]
        sidebar_layout = GridLayout(margins=(csp, isp * 2, csp, csp), spacing=csp)
        desc_label = create_label2(self.theme2, 'Space Skill Notes:')
        sidebar_layout.addWidget(desc_label, 0, 0, 1, 2)
        desc_edit = QPlainTextEdit()
        desc_edit.setStyleSheet(self.theme2.get_style_class('QPlainTextEdit', 'textedit'))
        desc_edit.setFont(self.theme2.get_font('textedit'))
        desc_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        desc_edit.textChanged.connect(lambda: self.build2.set(
            'space', 'skill_desc', value=desc_edit.toPlainText(), autosave=False))
        self.build2.skills.space_desc = desc_edit
        sidebar_layout.addWidget(desc_edit, 1, 0, 1, 2)
        load_skills_button = create_button2(self.theme2, 'Load Skills')
        load_skills_button.clicked.connect(self.load_skills_callback)
        sidebar_layout.addWidget(load_skills_button, 2, 0, alignment=AHCENTER)
        save_skills_button = create_button2(self.theme2, 'Save Skills')
        save_skills_button.clicked.connect(self.save_skills_callback)
        sidebar_layout.addWidget(save_skills_button, 2, 1, alignment=AHCENTER)
        sidebar_frame.setLayout(sidebar_layout)

    def setup_ground_skill_frame(self):
        """
        Creates Ground skill GUI
        """
        frame = self.tabbers.build_frames[3]
        isp = self.theme2['defaults']['isp'] * self.theme2.scale
        csp = self.theme2['defaults']['csp'] * self.theme2.scale
        col_layout = GridLayout(margins=isp, spacing=csp)
        col_layout.setRowStretch(0, 1)
        col_layout.setColumnStretch(0, 3)
        col_layout.setColumnStretch(2, 1)
        tree_frame = create_frame2(self.theme2, size_policy=SMINMIN)
        col_layout.addWidget(tree_frame, 0, 0)

        # skill tree
        tree_layout = GridLayout(spacing=5 * isp)
        tree_layout.setColumnStretch(0, 1)
        tree_layout.setColumnStretch(3, 1)
        tree_layout.setRowStretch(0, 1)
        tree_layout.setRowStretch(3, 1)
        skills = self.cargo.skills['ground']
        group_layout = GridLayout(spacing=csp)
        group_layout.addWidget(self.create_skill_button_ground(skills[0], 0, 0), 0, 1)
        group_layout.addWidget(self.create_skill_button_ground(skills[0], 1, 1), 1, 1)
        group_layout.addWidget(self.create_skill_button_ground(skills[1], 2, 0), 1, 0)
        group_layout.addWidget(self.create_skill_button_ground(skills[1], 3, 1), 2, 0)
        group_layout.addWidget(self.create_skill_button_ground(skills[2], 4, 0), 1, 2)
        group_layout.addWidget(self.create_skill_button_ground(skills[2], 5, 1), 2, 2)
        tree_layout.addLayout(group_layout, 1, 1)
        group_layout = GridLayout(spacing=csp)
        group_layout.addWidget(self.create_skill_button_ground(skills[3], 0, 0), 0, 1)
        group_layout.addWidget(self.create_skill_button_ground(skills[3], 1, 1), 1, 1)
        group_layout.addWidget(self.create_skill_button_ground(skills[4], 2, 0), 1, 0)
        group_layout.addWidget(self.create_skill_button_ground(skills[4], 3, 1), 2, 0)
        group_layout.addWidget(self.create_skill_button_ground(skills[5], 4, 0), 1, 2)
        group_layout.addWidget(self.create_skill_button_ground(skills[5], 5, 1), 2, 2)
        tree_layout.addLayout(group_layout, 1, 2)
        group_layout = GridLayout(spacing=csp)
        group_layout.addWidget(
            self.create_skill_button_ground(skills[6], 0, 0), 0, 0, 1, 2, alignment=AHCENTER)
        group_layout.addWidget(
            self.create_skill_button_ground(skills[6], 1, 1), 1, 0, alignment=ARIGHT)
        group_layout.addWidget(
            self.create_skill_button_ground(skills[7], 2, 0), 1, 1, alignment=ALEFT)
        group_layout.addWidget(
            self.create_skill_button_ground(skills[7], 3, 1), 2, 1, alignment=ALEFT)
        tree_layout.addLayout(group_layout, 2, 1)
        group_layout = GridLayout(spacing=csp)
        group_layout.addWidget(
            self.create_skill_button_ground(skills[8], 0, 0), 0, 0, 1, 2, alignment=AHCENTER)
        group_layout.addWidget(
            self.create_skill_button_ground(skills[8], 1, 1), 1, 1, alignment=ALEFT)
        group_layout.addWidget(
            self.create_skill_button_ground(skills[9], 2, 0), 1, 0, alignment=ARIGHT)
        group_layout.addWidget(
            self.create_skill_button_ground(skills[9], 3, 1), 2, 0, alignment=ARIGHT)
        tree_layout.addLayout(group_layout, 2, 2)
        tree_frame.setLayout(tree_layout)
        seperator = create_frame2(self.theme2, size_policy=SMAXMIN, style_override={
            'background-color': '@sets'})
        seperator.setFixedWidth(self.theme2['defaults']['sep'] * self.theme2.scale)
        col_layout.addWidget(seperator, 0, 1)
        bonus_bar_container = create_frame2(self.theme2, size_policy=SMINMIN)

        # bonus bars
        bonus_bar_layout = GridLayout(margins=isp)
        bonus_bar_layout.setRowStretch(0, 1)
        bonus_bar_layout.setRowStretch(18, 1)
        row = 15
        for i in range(5):
            seg1 = self.create_bonus_bar_segment('ground', i * 2)
            bonus_bar_layout.addWidget(seg1, row, 1, alignment=AHCENTER)
            seg2 = self.create_bonus_bar_segment('ground', i * 2 + 1)
            bonus_bar_layout.addWidget(seg2, row - 1, 1, alignment=AHCENTER)
            button = create_item_button2(self.theme2)
            button.clicked.connect(lambda i=i: self.build2.skill_unlock_callback('ground', i))
            bonus_bar_layout.addWidget(button, row - 2, 1, alignment=AHCENTER)
            self.build2.skills.unlocks['ground'][i] = button
            row -= 3
        icon_label = create_label2(self.theme2, '', style='unlock_label')
        icon_label.setPixmap(self.cache.icons['ground'])
        bonus_bar_layout.addWidget(icon_label, 16, 1, alignment=AHCENTER)
        self.build2.skills.count_labels['ground'] = create_label2(self.theme2, '0', 'label_subhead')
        bonus_bar_layout.addWidget(self.widgets.skill_count_ground, 17, 1, alignment=AHCENTER)
        bonus_bar_container.setLayout(bonus_bar_layout)
        col_layout.addWidget(bonus_bar_container, 0, 2)
        frame.setLayout(col_layout)

        # sidebar
        sidebar_frame = self.tabbers.sidebar_frames[3]
        sidebar_layout = GridLayout(margins=(csp, isp * 2, csp, csp), spacing=csp)
        desc_label = create_label2(self.theme2, 'Ground Skill Notes:')
        sidebar_layout.addWidget(desc_label, 0, 0, 1, 2)
        desc_edit = QPlainTextEdit()
        desc_edit.setStyleSheet(self.theme2.get_style_class('QPlainTextEdit', 'textedit'))
        desc_edit.setFont(self.theme2.get_font('textedit'))
        desc_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        desc_edit.textChanged.connect(lambda: self.build2.set(
            'ground', 'skill_desc', value=desc_edit.toPlainText(), autosave=False))
        self.widgets.build['skill_desc']['ground'] = desc_edit
        sidebar_layout.addWidget(desc_edit, 1, 0, 1, 2)
        load_skills_button = create_button2(self.theme2, 'Load Skills')
        load_skills_button.clicked.connect(self.load_skills_callback)
        sidebar_layout.addWidget(load_skills_button, 2, 0, alignment=AHCENTER)
        save_skills_button = create_button2(self.theme2, 'Save Skills')
        save_skills_button.clicked.connect(self.save_skills_callback)
        sidebar_layout.addWidget(save_skills_button, 2, 1, alignment=AHCENTER)
        sidebar_frame.setLayout(sidebar_layout)

    def setup_splash(self, frame: QFrame):
        """
        Creates Splash screen.
        """
        layout = GridLayout()
        layout.setRowStretch(0, 1)
        layout.setRowStretch(3, 1)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 3)
        loading_image = ImageLabel(self.app_dir2 / 'local' / 'sets_loading.png', (1, 1))
        layout.addWidget(loading_image, 1, 1)
        loading_label = create_label2(self.theme2, 'Loading: ...', 'label_subhead')
        self.splash.loading_label = loading_label
        layout.addWidget(loading_label, 2, 0, 1, 3, alignment=AHCENTER)
        frame.setLayout(layout)

    def hide_tooltips(self):
        """
        Hides tooltip windows when main window isn't the active window anymore.
        """
        if not self.window.isActiveWindow():
            for window in self.app.topLevelWindows():
                if window.type() == Qt.WindowType.ToolTip:
                    window.hide()

    def setup_settings_frame(self):
        """
        Populates the settings frame.
        """
        settings_frame = self.tabbers.build_frames[5]
        isp = self.theme2['defaults']['isp'] * self.theme2.scale
        settings_layout = HBoxLayout(margins=(2 * isp, isp, isp, isp), spacing=isp)
        scroll_layout = VBoxLayout(margins=(0, isp, 0, 0), spacing=isp)
        scroll_layout.setSpacing(isp)
        scroll_frame = create_frame2(self.theme2)
        scroll_area = QScrollArea()
        scroll_area.setSizePolicy(SMINMIN)
        scroll_area.setHorizontalScrollBarPolicy(SCROLLOFF)
        scroll_area.setVerticalScrollBarPolicy(SCROLLON)
        settings_layout.addWidget(scroll_area)
        settings_frame.setLayout(settings_layout)

        # first section
        settings_header = create_label2(self.theme2, 'Settings:', 'label_heading')
        scroll_layout.addWidget(settings_header, alignment=ALEFT)
        sec_1 = GridLayout(spacing=isp)
        sec_1.setColumnMinimumWidth(1, 3 * isp)
        sec_1.setColumnMinimumWidth(2, 12 * isp)
        sec_1.setColumnMinimumWidth(3, 3 * isp)
        sec_1.setColumnStretch(5, 1)
        ui_scale_label = create_label2(self.theme2, 'UI Scale')
        sec_1.addWidget(ui_scale_label, 0, 0, alignment=ALEFT)
        ui_scale_slider = create_annotated_slider2(
            self.theme2, default_value=round(self.settings.ui_scale * 50, 0), min=25, max=75,
            callback=self.settings.set_ui_scale)
        sec_1.addLayout(ui_scale_slider, 0, 2, alignment=ALEFT)
        ui_scale_desc = create_label2(self.theme2, 'Requires restart.', 'hint_label')
        sec_1.addWidget(ui_scale_desc, 0, 4, alignment=ALEFT)
        mark_label = create_label2(self.theme2, 'Default Mark')
        sec_1.addWidget(mark_label, 1, 0, alignment=ALEFT)
        mark_combo = create_combo_box2(self.theme2, style_override={'font': '@small_text'})
        mark_combo.addItems(('',) + MARKS)
        mark_combo.setCurrentText(self.settings.default_mark)
        mark_combo.currentTextChanged.connect(
            lambda new_mark: self.settings.set('default_mark', new_mark))
        sec_1.addWidget(mark_combo, 1, 2, alignment=ALEFT)
        rarity_label = create_label2(self.theme2, 'Default Rarity')
        sec_1.addWidget(rarity_label, 2, 0, alignment=ALEFT)
        rarity_combo = create_combo_box2(self.theme2, style_override={'font': '@small_text'})
        rarity_combo.addItems(RARITIES.keys())
        rarity_combo.setCurrentText(self.settings.default_rarity)
        rarity_combo.currentTextChanged.connect(
            lambda new_rarity: self.settings.set('default_rarity', new_rarity))
        sec_1.addWidget(rarity_combo, 2, 2, alignment=ALEFT | AVCENTER)
        picker_rel_label = create_label2(self.theme2, 'Picker Position')
        sec_1.addWidget(picker_rel_label, 3, 0, alignment=ALEFT)
        picker_rel_combo = create_combo_box2(self.theme2, style_override={'font': '@small_text'})
        picker_rel_combo.addItems(('Absolute', 'Relative'))
        picker_rel_combo.setCurrentIndex(self.settings.picker_relative)
        picker_rel_combo.currentIndexChanged.connect(
            lambda new_i: self.settings.set('picker_relative', new_i))
        sec_1.addWidget(picker_rel_combo, 3, 2, alignment=ALEFT | AVCENTER)
        picker_rel_label = create_label2(self.theme2, 'Default Save Format')
        sec_1.addWidget(picker_rel_label, 4, 0, alignment=ALEFT)
        picker_rel_combo = create_combo_box2(self.theme2, style_override={'font': '@small_text'})
        picker_rel_combo.addItems(('JSON', 'PNG'))
        picker_rel_combo.setCurrentText(self.settings.default_save_format)
        picker_rel_combo.currentTextChanged.connect(
            lambda new_t: self.settings.set('default_save_format', new_t))
        sec_1.addWidget(picker_rel_combo, 4, 2, alignment=ALEFT | AVCENTER)
        backup_label = create_label2(self.theme2, 'Preferred Backup')
        sec_1.addWidget(backup_label, 5, 0, alignment=ALEFT)
        backup_combo = create_combo_box2(self.theme2, style_override={'font': '@small_text'})
        backup_combo.addItems(('Auto', 'Manual'))
        backup_combo.setCurrentIndex(self.settings.pref_backup)
        backup_combo.currentIndexChanged.connect(
            lambda new_i: self.settings.set('pref_backup', new_i))
        sec_1.addWidget(backup_combo, 5, 2, alignment=ALEFT | AVCENTER)
        scroll_layout.addLayout(sec_1)

        # second section
        sep = create_frame2(self.theme2)
        sep.setFixedHeight(isp)
        scroll_layout.addWidget(sep)
        maintenance_header = create_label2(self.theme2, 'Maintenance:', 'label_heading')
        scroll_layout.addWidget(maintenance_header, alignment=ALEFT)
        sec_2 = GridLayout(spacing=isp)
        sec_2.setColumnMinimumWidth(1, 3 * isp)
        sec_2.setColumnStretch(3, 1)
        cargo_clear_button = create_button2(self.theme2, 'Clear Cargo Data')
        cargo_clear_button.clicked.connect(
            lambda: delete_folder_contents(self.config.config_subfolders['cargo']))
        sec_2.addWidget(cargo_clear_button, 0, 0, alignment=ALEFT)
        cargo_clear_label = create_label2(
            self.theme2, 'Clears cargo data. Restart to refresh data.', 'hint_label')
        sec_2.addWidget(cargo_clear_label, 0, 2, alignment=ALEFT)
        cache_clear_button = create_button2(self.theme2, 'Clear Cache')
        cache_clear_button.clicked.connect(
            lambda: delete_folder_contents(self.config.config_subfolders['cache']))
        sec_2.addWidget(cache_clear_button, 1, 0, alignment=ALEFT)
        cache_clear_label = create_label2(
            self.theme2, 'Clears cache. Restart to rebuild cache.', 'hint_label')
        sec_2.addWidget(cache_clear_label, 1, 2, alignment=ALEFT)
        backup_cargo_button = create_button2(self.theme2, 'Backup Cargo Data')
        backup_cargo_button.clicked.connect(self.backup_cargo_data)
        sec_2.addWidget(backup_cargo_button, 2, 0, alignment=ALEFT)
        backup_cargo_label = create_label2(
            self.theme2, 'Creates cargo backup to protect against download failures.', 'hint_label')
        sec_2.addWidget(backup_cargo_label, 2, 2, alignment=ALEFT)
        scroll_layout.addLayout(sec_2)

        # third section
        sep = create_frame2(self.theme2)
        sep.setFixedHeight(isp)
        scroll_layout.addWidget(sep)
        compatibility_header = create_label2(self.theme2, 'Compatibility:', 'label_heading')
        scroll_layout.addWidget(compatibility_header, alignment=ALEFT)
        sec_3 = GridLayout(spacing=isp)
        sec_3.setColumnMinimumWidth(1, 3 * isp)
        sec_3.setColumnStretch(3, 1)
        build_image_button = create_button2(self.theme2, 'Convert Legacy Build Image')
        build_image_button.clicked.connect(self.build_loader.load_legacy_build_image)
        sec_3.addWidget(build_image_button, 0, 0, alignment=ALEFT)
        build_image_label = create_label2(
            self.theme2, 'Loads build from legacy build image. Use the "Load" button to load '
            'legacy JSON build files.', 'hint_label')
        sec_3.addWidget(build_image_label, 0, 2, alignment=ALEFT)
        scroll_layout.addLayout(sec_3)

        scroll_frame.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_frame)

        # sidebar
        sidebar_frame = self.tabbers.sidebar_frames[5]
        csp = self.theme2['defaults']['csp'] * self.theme2.scale
        sidebar_layout = VBoxLayout(margins=csp, spacing=isp)
        sidebar_layout.setAlignment(ATOP)
        sidebar_layout.addWidget(
            create_label2(self.theme2, 'About SETS:', 'label_heading'), alignment=ALEFT)
        about_label = create_label2(
            self.theme2, 'Thank you for using the STO Equipment and Trait Selector (SETS)! Make '
            'sure to check out other projects of the STO Community Developers on our Github page '
            'and contact us on Discord for support.')
        about_label.setWordWrap(True)
        about_label.setMinimumWidth(50)  # to fix the word wrap
        about_label.setSizePolicy(SMINMAX)
        sidebar_layout.addWidget(about_label)
        link_button_style = {
            'Website': {
                'callback': lambda: open_url(self.config.link_website), 'align': AHCENTER},
            'Github': {
                'callback': lambda: open_url(self.config.link_github), 'align': AHCENTER},
            'STOBuilds Discord': {
                'callback': lambda: open_url(self.config.link_discord), 'align': AHCENTER},
            'Downloads': {
                'callback': lambda: open_url(self.config.link_downloads), 'align': AHCENTER}
        }
        button_layout, buttons = create_button_series2(
            self.theme2, link_button_style, 'button', shape='column', ret=True)
        buttons[0].setToolTip(self.config.link_website)
        buttons[1].setToolTip(self.config.link_github)
        buttons[2].setToolTip(self.config.link_discord)
        buttons[3].setToolTip(self.config.link_downloads)
        link_button_frame = create_frame2(self.theme2)
        link_button_frame.setLayout(button_layout)
        sidebar_layout.addWidget(link_button_frame, alignment=AHCENTER)
        sidebar_frame.setLayout(sidebar_layout)

        footer_frame = self.tabbers.character_frames[2]
        footer_layout = GridLayout(margins=csp, spacing=isp)
        version_label = create_label2(
            self.theme2, f"Version: {self.versions[0]}\n({self.versions[1]})", 'hint_label')
        footer_layout.addWidget(version_label, 0, 0, alignment=ALEFT | ABOTTOM)
        stocd_label = create_label2(self.theme2, '')
        stocd_label.setPixmap(self.cache.icons['STOCD'])
        footer_layout.addWidget(stocd_label, 0, 1, alignment=ARIGHT | ABOTTOM)
        footer_frame.setLayout(footer_layout)
