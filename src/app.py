import os

from PySide6.QtCore import QSettings
from PySide6.QtGui import QFontDatabase, QTextOption
from PySide6.QtWidgets import QApplication, QFrame, QPlainTextEdit, QTabWidget, QWidget

from .constants import (
    ACENTER, AHCENTER, ALEFT, ARIGHT, ATOP, CAREERS, FACTIONS, PRIMARY_SPECS,
    SECONDARY_SPECS, SMAXMAX, SMAXMIN, SMINMAX, SMINMIN)
from .iofunc import create_folder, get_asset_path, load_icon, store_json
from .subwindows import Picker, ShipSelector
from .widgets import (
    Cache, GridLayout, HBoxLayout, ImageLabel, ShipButton, ShipImage, VBoxLayout, WidgetStorage)

# only for developing; allows to terminate the qt event loop with keyboard interrupt
from signal import signal, SIGINT, SIG_DFL
signal(SIGINT, SIG_DFL)


class SETS():

    from .callbacks import (
            clear_build_callback, elite_callback, faction_combo_callback,
            load_build_callback, save_build_callback, set_build_item, select_ship,
            spec_combo_callback, switch_main_tab, tier_callback)
    from .datafunctions import autosave, empty_build, init_backend
    from .splash import enter_splash, exit_splash, splash_text
    from .style import create_style_sheet, get_style, get_style_class, theme_font
    from .widgetbuilder import (
            create_boff_station, create_build_section, create_button, create_button_series,
            create_checkbox, create_combo_box, create_entry, create_frame, create_item_button,
            create_label, create_personal_trait_section, create_starship_trait_section)

    app_dir = None
    versions = ('', '')  # (release version, dev version)
    config = {}  # see main.py for contents
    settings: QSettings  # see main.py for defaults
    # stores widgets that need to be accessed from outside their creating function
    widgets: WidgetStorage
    # stores refined cargo data
    cache: Cache
    build: dict  # stores current build
    box_height: int
    box_width: int
    autosave_enabled: bool

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
        self.cache = Cache()
        self.init_settings()
        self.init_config()
        self.init_environment()
        self.app, self.window = self.create_main_window()
        self.building = True
        self.build = self.empty_build()
        self.setup_main_layout()
        self.picker_window = Picker(self, self.window)
        self.ship_selector_window = ShipSelector(self, self.window)
        self.window.show()
        self.init_backend()

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
        self.config['autosave_filename'] = f'{config_folder}\\{self.config['autosave_filename']}'
        self.config['ui_scale'] = self.settings.value('ui_scale', type=float)
        self.box_width = self.config['box_width'] * self.config['ui_scale'] * 0.8
        self.box_height = self.config['box_height'] * self.config['ui_scale'] * 0.8

    def init_environment(self):
        """
        Creates required folders if necessary.
        """
        create_folder(self.config['config_folder_path'])
        create_folder(self.config['config_subfolders']['library'])
        create_folder(self.config['config_subfolders']['cache'])
        create_folder(self.config['config_subfolders']['backups'])
        create_folder(self.config['config_subfolders']['images'])
        create_folder(self.config['config_subfolders']['ship_images'])
        if not os.path.exists(self.config['autosave_filename']):
            store_json(self.empty_build(), self.config['autosave_filename'])

    def main_window_close_callback(self, event):
        """
        Executed when application is closed.
        """
        window_geometry = self.window.saveGeometry()
        self.settings.setValue('geometry', window_geometry)
        self.autosave()
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
        # master layout: banner, borders and splash screen
        layout = VBoxLayout(margins=0, spacing=0)
        background_frame = self.create_frame(
                style_override={'background-color': '@sets'}, size_policy=SMINMIN)
        layout.addWidget(background_frame)
        self.window.setLayout(layout)
        main_layout = VBoxLayout(margins=0, spacing=0)
        banner = ImageLabel(get_asset_path('sets_banner.png', self.app_dir), (2880, 126))
        main_layout.addWidget(banner)
        frame_width = 8 * self.config['ui_scale']
        tabber_layout = VBoxLayout(margins=frame_width, spacing=0)
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

        content_layout = GridLayout(margins=0, spacing=0)
        content_layout.setColumnStretch(0, 1)
        content_layout.setColumnStretch(1, 4)

        margin = 3 * self.config['ui_scale']
        menu_layout = GridLayout(margins=(margin, margin, margin, 0), spacing=0)
        menu_layout.setColumnStretch(0, 2)
        menu_layout.setColumnStretch(1, 5)
        menu_layout.setColumnStretch(2, 2)
        left_button_group = {
            'Save': {'callback': self.save_build_callback},
            'Open': {'callback': self.load_build_callback},
            'Clear': {'callback': self.clear_build_callback},
            'Clear all': {'callback': lambda: None}
        }
        menu_layout.addLayout(self.create_button_series(left_button_group), 0, 0, ALEFT | ATOP)
        center_button_group = {
            'default': {'font': ('Overpass', 16, 'medium')},
            'SPACE': {'callback': lambda: self.switch_main_tab(0), 'stretch': 1, 'size': SMINMAX},
            'GROUND': {'callback': lambda: self.switch_main_tab(1), 'stretch': 1, 'size': SMINMAX},
            'SPACE SKILLS': {
                'callback': lambda: self.switch_main_tab(2),
                'stretch': 1,
                'size': SMINMAX
            },
            'GROUND SKILLS': {
                'callback': lambda: self.switch_main_tab(3),
                'stretch': 1,
                'size': SMINMAX
            }
        }
        center_buttons = self.create_button_series(center_button_group, 'heavy_button')
        menu_layout.addLayout(center_buttons, 0, 1)
        right_button_group = {
            'Export': {'callback': lambda: None},
            'Settings': {'callback': lambda: self.switch_main_tab(5)},
        }
        menu_layout.addLayout(self.create_button_series(right_button_group), 0, 2, ARIGHT | ATOP)
        content_layout.addLayout(menu_layout, 0, 0, 1, 2)

        # sidebar
        sidebar = self.create_frame(size_policy=SMINMIN)
        self.widgets.sidebar = sidebar
        sidebar_layout = GridLayout(margins=0, spacing=0)

        sidebar_tabber = QTabWidget()
        sidebar_tabber.setStyleSheet(self.get_style_class('QTabWidget', 'tabber'))
        sidebar_tabber.tabBar().setStyleSheet(self.get_style_class('QTabBar', 'tabber_tab'))
        sidebar_tabber.setSizePolicy(SMINMIN)
        self.widgets.sidebar_tabber = sidebar_tabber
        sidebar_tab_names = (
                'space', 'ground', 'space_skills', 'ground_skills', 'empty', 'settings')
        for tab_name in sidebar_tab_names:
            tab_frame = self.create_frame()
            sidebar_tabber.addTab(tab_frame, tab_name)
            self.widgets.sidebar_frames.append(tab_frame)
        self.setup_ship_frame()
        sidebar_layout.addWidget(sidebar_tabber, 0, 0)

        character_tabber = QTabWidget()
        character_tabber.setStyleSheet(self.get_style_class('QTabWidget', 'tabber'))
        character_tabber.tabBar().setStyleSheet(self.get_style_class('QTabBar', 'tabber_tab'))
        character_tabber.setSizePolicy(SMINMAX)
        self.widgets.character_tabber = character_tabber
        char_frame = self.create_frame()
        self.setup_character_frame(char_frame)
        character_tabber.addTab(char_frame, 'char')
        empty_frame = self.create_frame()
        character_tabber.addTab(empty_frame, 'empty')
        settings_frame = self.create_frame()
        character_tabber.addTab(settings_frame, 'settings')
        self.widgets.character_frames = [char_frame, empty_frame, settings_frame]
        sidebar_layout.addWidget(character_tabber, 1, 0)

        seperator = self.create_frame(size_policy=SMAXMIN, style_override={
                'background-color': '@sets', 'margin-top': '@isp', 'margin-bottom': '@isp'})
        seperator.setFixedWidth(self.theme['defaults']['sep'] * self.config['ui_scale'])
        sidebar_layout.addWidget(seperator, 0, 1, 2, 1)
        sidebar.setLayout(sidebar_layout)
        content_layout.addWidget(sidebar, 1, 0)

        # build section
        build_tabber = QTabWidget()
        build_tabber.setStyleSheet(self.get_style_class('QTabWidget', 'tabber'))
        build_tabber.tabBar().setStyleSheet(self.get_style_class('QTabBar', 'tabber_tab'))
        build_tabber.setSizePolicy(SMINMIN)
        self.widgets.build_tabber = build_tabber
        build_tab_names = (
                'space_build', 'ground_build', 'space_skills', 'ground_skills', 'library',
                'settings')
        for tab_name in build_tab_names:
            tab_frame = self.create_frame()
            build_tabber.addTab(tab_frame, tab_name)
            self.widgets.build_frames.append(tab_frame)
        content_layout.addWidget(build_tabber, 1, 1)
        self.setup_build_frames()

        content_frame.setLayout(content_layout)

    def setup_ship_frame(self):
        """
        Creates ship info frame
        """
        frame = self.widgets.sidebar_frames[0]
        csp = self.theme['defaults']['csp'] * self.config['ui_scale']
        layout = VBoxLayout(margins=csp, spacing=csp)

        image_frame = self.create_frame(size_policy=SMINMIN)
        image_layout = GridLayout(margins=0, spacing=0)
        ship_image = ShipImage()
        ship_image.setSizePolicy(SMINMIN)
        self.widgets.ship['image'] = ship_image
        image_layout.addWidget(ship_image, 0, 0)
        image_frame.setLayout(image_layout)
        layout.addWidget(image_frame, stretch=1)

        ship_frame = self.create_frame(size_policy=SMINMIN)
        ship_layout = GridLayout(margins=0, spacing=csp)
        ship_layout.setRowStretch(4, 1)
        ship_layout.setColumnStretch(1, 1)
        ship_selector = ShipButton('<Pick Ship>')
        ship_selector.setSizePolicy(SMINMAX)
        ship_selector.setStyleSheet(
                self.get_style_class('ShipButton', 'button', override={'margin': 0}))
        ship_selector.setFont(self.theme_font(font_spec='@subhead'))
        ship_selector.clicked.connect(self.select_ship)
        self.widgets.ship['button'] = ship_selector
        ship_layout.addWidget(ship_selector, 0, 0, 1, 2, alignment=ATOP)
        tier_label = self.create_label('Ship Tier:')
        ship_layout.addWidget(tier_label, 1, 0)
        tier_combo = self.create_combo_box()
        tier_combo.currentTextChanged.connect(self.tier_callback)
        tier_combo.setSizePolicy(SMAXMAX)
        self.widgets.ship['tier'] = tier_combo
        ship_layout.addWidget(tier_combo, 1, 1, alignment=ALEFT)
        name_label = self.create_label('Ship Name:')
        ship_layout.addWidget(name_label, 2, 0)
        name_entry = self.create_entry()
        name_entry.editingFinished.connect(
                lambda: self.set_build_item(self.build['space'], 'ship_name', name_entry.text()))
        self.widgets.ship['name'] = name_entry
        name_entry.setSizePolicy(SMINMAX)
        ship_layout.addWidget(name_entry, 2, 1)
        desc_label = self.create_label('Build Description:')
        ship_layout.addWidget(desc_label, 3, 0, 1, 2)
        desc_edit = QPlainTextEdit()
        desc_edit.setSizePolicy(SMINMIN)
        desc_edit.setStyleSheet(self.get_style_class('QPlainTextEdit', 'textedit'))
        desc_edit.setFont(self.theme_font('textedit'))
        desc_edit.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        desc_edit.textChanged.connect(lambda: self.set_build_item(
                self.build['space'], 'ship_desc', desc_edit.toPlainText(), autosave=False))
        self.widgets.ship['desc'] = desc_edit
        ship_layout.addWidget(desc_edit, 4, 0, 1, 2)
        ship_frame.setLayout(ship_layout)
        layout.addWidget(ship_frame, stretch=2)
        frame.setLayout(layout)

    def setup_build_frames(self):
        """
        Creates build areas
        """
        self.setup_space_build_frame()

    def setup_space_build_frame(self):
        """
        """
        frame = self.widgets.build_frames[0]
        isp = self.theme['defaults']['isp'] * 2 * self.config['ui_scale']
        layout = GridLayout(margins=isp, spacing=isp)
        layout.setColumnStretch(0, 1)
        layout.setColumnStretch(10, 1)
        layout.setRowStretch(20, 1)
        eq = self.cache.equipment
        # Equipment
        fore_layout = self.create_build_section(
                'Fore Weapons', 5, 'space', 'fore_weapons', eq['fore_weapons'].keys(), True)
        layout.addLayout(fore_layout, 0, 1, alignment=ALEFT)
        aft_layout = self.create_build_section(
                'Aft Weapons', 5, 'space', 'aft_weapons',
                eq['aft_weapons'].keys(), True, 'aft_weapons_label')
        layout.addLayout(aft_layout, 1, 1, alignment=ALEFT)
        exp_layout = self.create_build_section(
                'Experimental Weapon', 1, 'space', 'experimental', eq['experimental'].keys(), True,
                'experimental_label')
        layout.addLayout(exp_layout, 2, 1, alignment=ALEFT)
        device_layout = self.create_build_section(
                'Devices', 6, 'space', 'devices', eq['devices'].keys(), True)
        layout.addLayout(device_layout, 3, 1, alignment=ALEFT)
        hangar_layout = self.create_build_section(
                'Hangars', 2, 'space', 'hangars', eq['hangars'].keys(), True, 'hangars_label')
        layout.addLayout(hangar_layout, 4, 1, alignment=ALEFT)
        sep1 = self.create_frame(size_policy=SMAXMIN, style_override={
            'background-color': '@bg', 'margin-top': '@isp', 'margin-bottom': '@isp'})
        sep1.setFixedWidth(self.theme['defaults']['sep'] * self.config['ui_scale'])
        layout.addWidget(sep1, 0, 2, 5, 1)

        deflector_layout = self.create_build_section(
                'Deflector', 1, 'space', 'deflector', eq['deflector'], True)
        layout.addLayout(deflector_layout, 0, 3, alignment=ALEFT)
        secdef_layout = self.create_build_section(
                'Sec-Def', 1, 'space', 'sec_def', eq['sec_def'], True, 'sec_def_label')
        layout.addLayout(secdef_layout, 1, 3, alignment=ALEFT)
        engine_layout = self.create_build_section(
                'Engines', 1, 'space', 'engines', eq['engines'], True)
        layout.addLayout(engine_layout, 2, 3, alignment=ALEFT)
        warp_layout = self.create_build_section(
                'Warp Core', 1, 'space', 'core', eq['core'], True)
        layout.addLayout(warp_layout, 3, 3, alignment=ALEFT)
        shield_layout = self.create_build_section(
                'Shield', 1, 'space', 'shield', eq['shield'], True)
        layout.addLayout(shield_layout, 4, 3, alignment=ALEFT)
        sep2 = self.create_frame(size_policy=SMAXMIN, style_override={
            'background-color': '@bg', 'margin-top': '@isp', 'margin-bottom': '@isp'})
        sep2.setFixedWidth(self.theme['defaults']['sep'] * self.config['ui_scale'])
        layout.addWidget(sep2, 0, 4, 5, 1)

        uni_layout = self.create_build_section(
                'Universal Consoles', 3, 'space', 'uni_consoles', eq['uni_consoles'], True,
                'uni_consoles_label')
        layout.addLayout(uni_layout, 0, 5, alignment=ALEFT)
        eng_layout = self.create_build_section(
                'Engineering Consoles', 5, 'space', 'eng_consoles',
                eq['eng_consoles'], True, 'eng_consoles_label')
        layout.addLayout(eng_layout, 1, 5, alignment=ALEFT)
        sci_layout = self.create_build_section(
                'Science Consoles', 5, 'space', 'sci_consoles',
                eq['sci_consoles'], True, 'sci_consoles_label')
        layout.addLayout(sci_layout, 2, 5, alignment=ALEFT)
        tac_layout = self.create_build_section(
                'Tactical Consoles', 5, 'space', 'tac_consoles',
                eq['tac_consoles'], True, 'tac_consoles_label')
        layout.addLayout(tac_layout, 3, 5, alignment=ALEFT)
        sep3 = self.create_frame(size_policy=SMAXMIN, style_override={
            'background-color': '@bg', 'margin-top': '@isp', 'margin-bottom': '@isp'})
        sep3.setFixedWidth(self.theme['defaults']['sep'] * self.config['ui_scale'])
        layout.addWidget(sep3, 0, 6, 5, 1)

        # Boffs
        boff_1_layout = self.create_boff_station('Universal', 'space', 'Miracle Worker', boff_id=0)
        layout.addLayout(boff_1_layout, 0, 7, alignment=ALEFT)
        boff_2_layout = self.create_boff_station('Universal', 'space', 'Command', boff_id=1)
        layout.addLayout(boff_2_layout, 1, 7, alignment=ALEFT)
        boff_3_layout = self.create_boff_station('Universal', 'space', 'Intelligence', boff_id=2)
        layout.addLayout(boff_3_layout, 2, 7, alignment=ALEFT)
        boff_4_layout = self.create_boff_station('Universal', 'space', 'Pilot', boff_id=3)
        layout.addLayout(boff_4_layout, 3, 7, alignment=ALEFT)
        boff_5_layout = self.create_boff_station('Universal', 'space', 'Temporal', boff_id=4)
        layout.addLayout(boff_5_layout, 4, 7, alignment=ALEFT)
        boff_6_layout = self.create_boff_station('Universal', 'space', boff_id=5)
        width_placeholder = self.create_combo_box(size_policy=SMAXMAX)
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
        starship_trait_layout = self.create_starship_trait_section('space')
        trait_layout.addLayout(starship_trait_layout, 1, 0)
        rep_trait_layout = self.create_build_section(
                'Reputation Traits', 5, 'space', 'rep_traits',
                self.cache.traits['space']['rep'].keys())
        trait_layout.addLayout(rep_trait_layout, 2, 0)
        active_trait_layout = self.create_build_section(
                'Active Reputation Traits', 5, 'space', 'active_rep_traits',
                self.cache.traits['space']['active_rep'])
        trait_layout.addLayout(active_trait_layout, 3, 0)
        layout.addLayout(trait_layout, 0, 9, 6, 1, alignment=ATOP)

        # Doffs

        frame.setLayout(layout)

    def setup_character_frame(self, frame: QFrame):
        """
        Creates character customization area.
        """
        csp = self.theme['defaults']['csp'] * self.config['ui_scale']
        layout = GridLayout(margins=csp, spacing=csp)
        layout.setColumnStretch(1, 1)
        seperator = self.create_frame(size_policy=SMINMAX, style_override={
                'background-color': '@sets', 'margin': '@isp'})
        sep = self.theme['defaults']['sep'] * self.config['ui_scale']
        seperator.setFixedHeight(sep)
        layout.addWidget(seperator, 0, 0, 1, 2, alignment=ATOP)  # ATOP makes it respect the margin?
        char_name = self.create_entry(placeholder='NAME')
        char_name.setAlignment(AHCENTER)
        char_name.setSizePolicy(SMINMAX)
        char_name.editingFinished.connect(
                lambda: self.set_build_item(self.build['captain'], 'name', char_name.text()))
        layout.addWidget(char_name, 1, 0, 1, 2)
        elite_label = self.create_label('Elite Captain')
        layout.addWidget(elite_label, 2, 0, alignment=ARIGHT)
        elite_checkbox = self.create_checkbox()
        elite_checkbox.checkStateChanged.connect(self.elite_callback)
        layout.addWidget(elite_checkbox, 2, 1, alignment=ALEFT)
        career_label = self.create_label('Captain Career')
        layout.addWidget(career_label, 3, 0, alignment=ARIGHT)
        career_combo = self.create_combo_box()
        career_combo.addItems({''} | CAREERS)
        career_combo.currentTextChanged.connect(
                lambda t: self.set_build_item(self.build['captain'], 'career', t))
        layout.addWidget(career_combo, 3, 1)
        faction_label = self.create_label('Faction')
        layout.addWidget(faction_label, 4, 0, alignment=ARIGHT)
        faction_combo = self.create_combo_box()
        faction_combo.addItems({''} | FACTIONS)
        faction_combo.currentTextChanged.connect(self.faction_combo_callback)
        layout.addWidget(faction_combo, 4, 1)
        species_label = self.create_label('Species')
        layout.addWidget(species_label, 5, 0, alignment=ARIGHT)
        species_combo = self.create_combo_box()
        species_combo.addItems({''})
        species_combo.currentTextChanged.connect(
                lambda t: self.set_build_item(self.build['captain'], 'species', t))
        layout.addWidget(species_combo, 5, 1)
        primary_label = self.create_label('Primary Spec')
        layout.addWidget(primary_label, 6, 0, alignment=ARIGHT)
        primary_combo = self.create_combo_box()
        primary_combo.addItems({''} | PRIMARY_SPECS)
        primary_combo.currentTextChanged.connect(lambda t: self.spec_combo_callback(True, t))
        layout.addWidget(primary_combo, 6, 1)
        secondary_label = self.create_label('Secondary Spec', style_override={'margin-bottom': 0})
        layout.addWidget(secondary_label, 7, 0, alignment=ARIGHT)
        secondary_combo = self.create_combo_box()
        secondary_combo.addItems({''} | PRIMARY_SPECS | SECONDARY_SPECS)
        secondary_combo.currentTextChanged.connect(lambda t: self.spec_combo_callback(False, t))
        layout.addWidget(secondary_combo, 7, 1)
        frame.setLayout(layout)
        self.widgets.character = {
            'name': char_name,
            'elite': elite_checkbox,
            'career': career_combo,
            'faction': faction_combo,
            'species': species_combo,
            'primary': primary_combo,
            'secondary': secondary_combo,
        }

    def setup_splash(self, frame: QFrame):
        """
        Creates Splash screen.
        """
        layout = GridLayout(margins=0, spacing=0)
        layout.setRowStretch(0, 1)
        layout.setRowStretch(3, 1)
        layout.setColumnStretch(0, 3)
        layout.setColumnStretch(1, 2)
        layout.setColumnStretch(2, 3)
        loading_image = ImageLabel(get_asset_path('sets_loading.png', self.app_dir), (1, 1))
        layout.addWidget(loading_image, 1, 1)
        loading_label = self.create_label('Loading: ...', 'label_subhead')
        self.widgets.loading_label = loading_label
        layout.addWidget(loading_label, 2, 0, 1, 3, alignment=AHCENTER)
        frame.setLayout(layout)
