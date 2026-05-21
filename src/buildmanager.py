from pathlib import Path

from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QLineEdit, QPlainTextEdit, QPushButton

from .buildhelpers import get_boff_spec, get_variable_slot_counts, empty_build
from .cargomanager import CargoManager
from .constants import (
    EQUIPMENT_TYPES, PRIMARY_SPECS, SECONDARY_SPECS, SHIP_TEMPLATE, SKILL_POINTS_FOR_RANK, SPECIES,
    SPECIES_TRAITS)
from .imagemanager import ImageManager
from .iofunc import open_wiki_page, store_json
from .textedit import add_equipment_tooltip_header, get_ultimate_skill_unlock_tooltip
from .theme import TooltipCSS
from .widgets import ItemButton, ItemSlot, ShipButton, ShipImage, Thread, TooltipLabel


class SpaceBuild():
    """Stores widgets for space build"""
    def __init__(self):
        self.active_rep_traits: list[ItemButton] = [None] * 5
        self.aft_weapons: list[ItemButton] = [None] * 5
        self.aft_weapons_label: QLabel = None
        self.boffs: list[list[ItemButton]] = [
            [None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4]
        self.boff_labels: list[QComboBox] = [None] * 6
        self.boff_label_icons: list[TooltipLabel] = [None] * 6
        self.core: list[ItemButton] = [None]
        self.deflector: list[ItemButton] = [None]
        self.devices: list[ItemButton] = [None] * 6
        self.doffs_spec: list[QComboBox] = [None] * 6
        self.doffs_variant: list[QComboBox] = [None] * 6
        self.eng_consoles: list[ItemButton] = [None] * 5
        self.eng_consoles_label: QLabel = None
        self.engines: list[ItemButton] = [None]
        self.experimental: list[ItemButton] = [None]
        self.experimental_label: QLabel = [None]
        self.fore_weapons: list[ItemButton] = [None] * 5
        self.hangars: list[ItemButton] = [None] * 2
        self.hangars_label: QLabel = None
        self.rep_traits: list[ItemButton] = [None] * 5
        self.sci_consoles: list[ItemButton] = [None] * 5
        self.sci_consoles_label: QLabel = None
        self.sec_def: list[ItemButton] = [None]
        self.sec_def_label: QLabel = [None]
        self.shield: list[ItemButton] = [None]
        self.starship_traits: list[ItemButton] = [None] * 7
        self.tac_consoles: list[ItemButton] = [None] * 5
        self.tac_consoles_label: QLabel = None
        self.traits: list[ItemButton] = [None] * 12
        self.uni_consoles: list[ItemButton] = [None] * 3
        self.uni_consoles_label: QLabel = None


class GroundBuild():
    """Stores widgets for ground build"""
    def __init__(self):
        self.active_rep_traits: list[ItemButton] = [None] * 5
        self.armor: list[ItemButton] = [None]
        self.boffs: list[list[ItemButton]] = [[None] * 4, [None] * 4, [None] * 4, [None] * 4]
        self.boff_profs: list[QComboBox] = [None] * 4
        self.boff_specs: list[QComboBox] = [None] * 4
        self.ground_devices: list[ItemButton] = [None] * 5
        self.desc: QPlainTextEdit = None
        self.doffs_spec: list[QComboBox] = [None] * 6
        self.doffs_variant: list[QComboBox] = [None] * 6
        self.ev_suit: list[ItemButton] = [None]
        self.kit: list[ItemButton] = [None]
        self.kit_modules: list[ItemButton] = [None] * 6
        self.rep_traits: list[ItemButton] = [None] * 5
        self.personal_shield: list[ItemButton] = [None]
        self.traits: list[ItemButton] = [None] * 12
        self.weapons: list[ItemButton] = [None] * 2


class SkillTree():
    """Stores widgets for space and ground skill tree"""
    def __init__(self):
        self.space: dict[str, list[ItemButton]] = {
            'eng': [None] * 30,
            'sci': [None] * 30,
            'tac': [None] * 30
        }
        self.ground: list[list[ItemButton]] = [
            [False] * 6,
            [False] * 6,
            [False] * 4,
            [False] * 4,
        ]
        self.unlocks: dict[str, list[ItemButton]] = {
            'eng': [None] * 5,
            'sci': [None] * 5,
            'tac': [None] * 5,
            'ground': [None] * 5
        }
        self.bonus_bars: dict[str, list[QPushButton]] = {
            'eng': [None] * 24,
            'sci': [None] * 24,
            'tac': [None] * 24,
            'ground': [None] * 10,
        }
        self.count_labels: dict[str, QLabel] = {
            'eng': None,
            'sci': None,
            'tac': None,
            'ground': None
        }
        self.space_desc: QPlainTextEdit
        self.ground_desc: QPlainTextEdit


class ShipBuild():
    """Stores widgets for ship description."""
    def __init__(self):
        self.image: ShipImage
        self.button: ShipButton
        self.tier: QComboBox
        self.dc: TooltipLabel
        self.name: QLineEdit
        self.desc: QPlainTextEdit


class CharacterBuild():
    """Stores WIdgets for character building."""
    def __init__(self):
        self.name: QLineEdit
        self.elite: QCheckBox
        self.career: QComboBox
        self.faction: QComboBox
        self.species: QComboBox
        self.primary: QComboBox
        self.secondary: QComboBox


class BuildManager():
    """Manages build data and widgets"""

    def __init__(
            self, cache: CargoManager, images: ImageManager, autosave_path: Path,
            tooltip_styles: TooltipCSS):
        self._building: bool = False  # disables side-effects (including autosave)
        self._cache: CargoManager = cache
        self._images: ImageManager = images
        self._image_thread: Thread = Thread(target=self._images.get_ship_image)
        self._image_thread.result.connect(lambda image: self.ship.image.set_image(image))
        self._autosave_path: Path = autosave_path
        self._tooltip_styles: TooltipCSS = tooltip_styles
        self.space: SpaceBuild = SpaceBuild()
        self.ground: GroundBuild = GroundBuild()
        self.skills: SkillTree = SkillTree()
        self.ship: ShipBuild = ShipBuild()
        self.character: CharacterBuild = CharacterBuild()
        self._build_data: dict[str, int | dict[str]] = empty_build()
        self._skill_state: dict[str, int | list[int]] = {
            'space_points_total': 0,
            'space_points_eng': 0,
            'space_points_sci': 0,
            'space_points_tac': 0,
            'space_points_rank': [0] * 5,
            'ground_points_total': 0
        }

    @property
    def data(self) -> dict[str, int | dict[str]]:
        """Raw build data"""
        return self._build_data

    @data.setter
    def data(self, build_data: dict[str, int | dict[str]]):
        self._build_data = build_data

    def autosave(self):
        """
        Saves build to autosave file.
        """
        if not self._building:
            store_json(self._build_data, self._autosave_path)

    def __getitem__(self, key: str):
        return self._build_data[key]

    def set(
            self, category: str, key: str, subkey: int = -1, value: str | dict = '',
            autosave: bool = True):
        """
        Sets build data for situations in which assignment is not possible.

        Parameters:
        - :param category: build category, e.g. `space`, `ground`, ...
        - :param key: build key, e.g. `aft_weapons`, `armor`, ...
        - :param subkey: build subkey, i.e. index of item under build key
        - :param value: data to be set
        - :param autosave: set to `False` to prevent autosaving
        """
        if subkey == -1:
            self._build_data[category][key] = value
        else:
            self._build_data[category][key][subkey] = value
        if autosave:
            self.autosave()

    def load_build(self):
        """
        Updates UI to show the build currently in self._build_data.
        """
        self._building = True
        # ship section
        ship = self._build_data['space']['ship']
        if ship == '<Pick Ship>' or ship == '':
            ship_data = SHIP_TEMPLATE
            self.ship.button.setText('<Pick Ship>')
            self.ship.tier.clear()
            self.ship.image.set_image(self._images.empty)
            self.ship.dc.hide()
        else:
            self.ship.button.setText(ship)
            ship_data = self._cache.ships[ship]
            self.set_ship_image(ship_data['image'][5:])
            tier = self._build_data['space']['tier']
            ship_tier = ship_data['tier']
            self.ship.tier.clear()
            if ship_tier == 6:
                self.ship.tier.addItems(('T6', 'T6-X', 'T6-X2'))
            elif ship_tier == 5:
                self.ship.tier.addItems(('T5', 'T5-U', 'T5-X', 'T5-X2'))
            else:
                self.ship.tier.addItem(f'T{ship_tier}')
            self.ship.tier.setCurrentText(tier)
            if ship_data['equipcannons'] == 'yes':
                self.ship.dc.show()
            else:
                self.ship.dc.hide()
        self.ship.name.setText(self._build_data['space']['ship_name'])
        self.ship.desc.setPlainText(self._build_data['space']['ship_desc'])

        # Character section
        elite_captain = self._build_data['captain']['elite']
        self.character.name.setText(self._build_data['captain']['name'])
        elite_state = Qt.CheckState.Checked if elite_captain else Qt.CheckState.Unchecked
        self.character.elite.setCheckState(elite_state)
        self.character.career.setCurrentText(self._build_data['captain']['career'])
        species = self._build_data['captain']['species']
        self.character.faction.setCurrentText(self._build_data['captain']['faction'])
        self.character.species.setCurrentText(species)
        if species != 'Alien':
            self.space.traits[10].hide()
            self.ground.traits[10].hide()
        self.character.primary.setCurrentText(self._build_data['captain']['primary_spec'])
        self.character.secondary.setCurrentText(self._build_data['captain']['secondary_spec'])

        # Space Build Section
        self.align_space_frame(ship_data)
        self.load_equipment_cat('fore_weapons', 'space')
        self.load_equipment_cat('aft_weapons', 'space')
        self.load_equipment_cat('experimental', 'space')
        self.load_equipment_cat('devices', 'space')
        self.load_equipment_cat('hangars', 'space')
        self.load_equipment_cat('deflector', 'space')
        self.load_equipment_cat('sec_def', 'space')
        self.load_equipment_cat('engines', 'space')
        self.load_equipment_cat('core', 'space')
        self.load_equipment_cat('shield', 'space')
        self.load_equipment_cat('uni_consoles', 'space')
        self.load_equipment_cat('eng_consoles', 'space')
        self.load_equipment_cat('sci_consoles', 'space')
        self.load_equipment_cat('tac_consoles', 'space')
        self.load_boff_stations('space')
        self.load_trait_cat('traits', 'space')
        if not elite_captain:
            self.space.traits[9].hide()
        self.load_trait_cat('starship_traits', 'space')
        self.load_trait_cat('rep_traits', 'space')
        self.load_trait_cat('active_rep_traits', 'space')
        self.load_doffs('space')

        # Ground Build Section
        self.ground.desc.setPlainText(self._build_data['ground']['ground_desc'])
        self.load_equipment_cat('kit_modules', 'ground')
        if not elite_captain:
            self.ground.kit_modules[5].hide()
        self.load_equipment_cat('weapons', 'ground')
        self.load_equipment_cat('ground_devices', 'ground')
        if not elite_captain:
            self.ground.ground_devices[4].hide()
        self.load_equipment_cat('kit', 'ground')
        self.load_equipment_cat('armor', 'ground')
        self.load_equipment_cat('ev_suit', 'ground')
        self.load_equipment_cat('personal_shield', 'ground')
        self.load_boff_stations('ground')
        self.load_trait_cat('traits', 'ground')
        if not elite_captain:
            self.ground.traits[9].hide()
        self.load_trait_cat('rep_traits', 'ground')
        self.load_trait_cat('active_rep_traits', 'ground')
        self.load_doffs('ground')

        self.load_skill_pages()

        self._building = False
        self.autosave()

    def set_ship_image(self, image_name: str):
        """
        Updates ship image with image specified by `image_name`.

        Parameters:
        - :param image_name: name of the image to obtain and show
        """
        if self._image_thread.isRunning():
            self._image_thread.finished.connect(
                lambda name=image_name: self.set_ship_image(name),
                type=Qt.ConnectionType.SingleShotConnection)
        else:
            self._image_thread.set_args((image_name,))
            self._image_thread.start()

    def align_space_frame(self, ship_data: dict, clear: bool = False):
        """
        Hides / shows the appropriate buttons of the ship build. Updates Boff stations.

        Parameters:
        - :param ship_data: ship specifications
        - :param clear: set to True to clear build
        """
        uni, eng, sci, tac, devices, starship_traits = get_variable_slot_counts(
            ship_data, self._build_data['space']['tier'])

        self.update_equipment_cat('fore_weapons', ship_data['fore'], clear)
        self.update_equipment_cat('aft_weapons', ship_data['aft'], clear, can_hide=True)
        self.update_equipment_cat('experimental', ship_data['experimental'], clear, can_hide=True)
        self.update_equipment_cat('devices', devices, clear)
        self.update_equipment_cat('hangars', ship_data['hangars'], clear, can_hide=True)
        self.update_equipment_cat('sec_def', ship_data['secdeflector'], clear, can_hide=True)
        if clear:
            self.space.deflector[0].clear()
            self._build_data['space']['deflector'][0] = ''
            self.space.engines[0].clear()
            self._build_data['space']['engines'][0] = ''
            self.space.core[0].clear()
            self._build_data['space']['core'][0] = ''
            self.space.shield[0].clear()
            self._build_data['space']['shield'][0] = ''
        self.update_equipment_cat('uni_consoles', uni, clear, can_hide=True)
        self.update_equipment_cat('eng_consoles', eng, clear, can_hide=True)
        self.update_equipment_cat('sci_consoles', sci, clear, can_hide=True)
        self.update_equipment_cat('tac_consoles', tac, clear, can_hide=True)

        self.update_starship_traits(starship_traits, clear)

        boff_specs = map(lambda s: get_boff_spec(s), ship_data['boffs'])
        if ('Science Destroyer' in ship_data['type']
                or 'Science Destroyer Warbird' in ship_data['type']):
            for boff_num, boff_details in enumerate(sorted(boff_specs, reverse=True)):
                if (boff_details[0] == 3 and boff_details[1] == 'Tactical'
                        or boff_details[0] == 4 and boff_details[1] == 'Science'):
                    self.update_boff_seat(boff_num, *boff_details, clear, sci_destroyer_seat=True)
                else:
                    self.update_boff_seat(boff_num, *boff_details, clear)
        else:
            for boff_num, boff_details in enumerate(sorted(boff_specs, reverse=True)):
                self.update_boff_seat(boff_num, *boff_details, clear)
        for boff_to_hide in range(boff_num + 1, 6):
            self.update_boff_seat(boff_to_hide, rank=0, profession='', clear=clear, hide_seat=True)

    def clear_all(self):
        """
        Clears space and ground build, skills and captain info
        """
        self._building = True
        self.clear_space_build()
        self.clear_ground_build()
        self.clear_captain()
        self.clear_space_skills()
        self.clear_ground_skills()
        self._building = False
        self.autosave()

    def clear_build_callback(self, current_tab: int):
        """
        Clears current build section
        """
        self._building = True
        if current_tab == 0:
            self.clear_space_build()
        elif current_tab == 1:
            self.clear_ground_build()
        elif current_tab == 2:
            self.clear_space_skills()
        elif current_tab == 3:
            self.clear_ground_skills()
        self._building = False
        self.autosave()

    def clear_space_build(self):
        """
        clears space build
        """
        self.clear_ship()
        self.align_space_frame(SHIP_TEMPLATE, clear=True)
        self.clear_traits('space')
        self.clear_doffs('space')

    def clear_ship(self):
        """
        Clears ship section of sidebar
        """
        self.ship.image.set_image(self._images.empty)
        self.ship.button.setText('<Pick Ship>')
        self._build_data['space']['ship'] = '<Pick Ship>'
        self.ship.tier.clear()
        self.ship.dc.hide()
        self.ship.name.setText('')
        self._build_data['space']['ship_name'] = ''
        self.ship.desc.setPlainText('')
        self._build_data['space']['ship_desc'] = ''

    def clear_ground_build(self):
        """
        Clears ground build
        """
        self.ground.desc.clear()
        self._build_data['ground']['ground_desc'] = ''
        self.clear_equipment_cat_ground('kit_modules')
        self.clear_equipment_cat_ground('weapons')
        self.clear_equipment_cat_ground('ground_devices')
        self.clear_equipment_cat_ground('kit')
        self.clear_equipment_cat_ground('armor')
        self.clear_equipment_cat_ground('ev_suit')
        self.clear_equipment_cat_ground('personal_shield')
        self.clear_boff_seat_ground(0)
        self.clear_boff_seat_ground(1)
        self.clear_boff_seat_ground(2)
        self.clear_boff_seat_ground(3)
        self.clear_traits('ground')
        self.clear_doffs('ground')

    def clear_traits(self, environment: str = 'both'):
        """
        Clears traits from build and UI

        Parameters:
        - :param environment: environment to clear the traits from (space/ground/both)
        """
        if environment == 'space' or environment == 'both':
            for i, trait_button in enumerate(self.space.traits):
                trait_button.clear()
                self._build_data['space']['traits'][i] = ''
            for i, trait_button in enumerate(self.space.starship_traits):
                trait_button.clear()
                self._build_data['space']['starship_traits'][i] = ''
            for i, trait_button in enumerate(self.space.rep_traits):
                trait_button.clear()
                self._build_data['space']['rep_traits'][i] = ''
            for i, trait_button in enumerate(self.space.active_rep_traits):
                trait_button.clear()
                self._build_data['space']['active_rep_traits'][i] = ''
        if environment == 'ground' or environment == 'both':
            for i, trait_button in enumerate(self.ground.traits):
                trait_button.clear()
                self._build_data['ground']['traits'][i] = ''
            for i, trait_button in enumerate(self.ground.rep_traits):
                trait_button.clear()
                self._build_data['ground']['rep_traits'][i] = ''
            for i, trait_button in enumerate(self.ground.active_rep_traits):
                trait_button.clear()
                self._build_data['ground']['active_rep_traits'][i] = ''

    def clear_doffs(self, environment: str = 'both'):
        """
        Clears doff frame(s)

        Parameters:
        - :param environment: "space" / "ground" / "both"
        """
        if environment == 'space' or environment == 'both':
            for i in range(6):
                self.space.doffs_spec[i].setCurrentText('')
                self.space.doffs_variant[i].clear()
                self._build_data['space']['doffs_spec'][i] = ''
                self._build_data['space']['doffs_variant'][i] = ''
        if environment == 'ground' or environment == 'both':
            for i in range(6):
                self.ground.doffs_spec[i].setCurrentText('')
                self.ground.doffs_variant[i].clear()
                self._build_data['ground']['doffs_spec'][i] = ''
                self._build_data['ground']['doffs_variant'][i] = ''

    def clear_space_skills(self):
        """
        resets space skill tree
        """
        self.skills.space_desc.clear()
        self._build_data['skill_desc']['space'] = ''
        self._build_data['space_skills'] = {
            'eng': [False] * 30,
            'sci': [False] * 30,
            'tac': [False] * 30
        }
        self._skill_state['space_points_total'] = 0
        self._skill_state['space_points_eng'] = 0
        self.skills.count_labels['eng'].setText('0')
        self._skill_state['space_points_sci'] = 0
        self.skills.count_labels['sci'].setText('0')
        self._skill_state['space_points_tac'] = 0
        self.skills.count_labels['tac'].setText('0')
        self._skill_state['space_points_rank'] = [0] * 5
        for career in ('eng', 'sci', 'tac'):
            for skill_button in self.skills.space[career]:
                skill_button.clear_overlay()
                skill_button.highlight = False
            self._build_data['skill_unlocks'][career] = [None] * 5
            for bar_segment in self.skills.bonus_bars[career]:
                bar_segment.setChecked(False)
            for unlock_button in self.skills.unlocks[career]:
                unlock_button.clear()

    def clear_ground_skills(self):
        """
        resets ground skill tree
        """
        self.skills.ground_desc.clear()
        self._build_data['skill_desc']['ground'] = ''
        self._build_data['ground_skills'] = [
            [False] * 6,
            [False] * 6,
            [False] * 4,
            [False] * 4
        ]
        self._build_data['skill_unlocks']['ground'] = [None] * 5
        self._skill_state['ground_points_total'] = 0
        self.skills.count_labels['ground'].setText('0')
        for skill_subtree in self.skills.ground:
            for skill_button in skill_subtree:
                skill_button.clear_overlay()
                skill_button.highlight = False
        for unlock_button in self.skills.unlocks['ground']:
            unlock_button.clear()
        for bar_segment in self.skills.bonus_bars['ground']:
            bar_segment.setChecked(False)

    def clear_captain(self):
        """
        Clears Captain information from build and UI
        """
        self.character.name.clear()
        self._build_data['captain']['name'] = ''
        self.character.elite.setCheckState(Qt.CheckState.Unchecked)
        self._build_data['captain']['elite'] = False
        self.character.career.setCurrentText('')
        self._build_data['captain']['career'] = ''
        self.character.faction.setCurrentText('')
        self._build_data['captain']['faction'] = ''
        self.character.species.setCurrentText('')
        self._build_data['captain']['species'] = ''
        self.character.primary.setCurrentText('')
        self._build_data['captain']['primary_spec'] = ''
        self.character.secondary.setCurrentText('')
        self._build_data['captain']['secondary_spec'] = ''

    def update_equipment_cat(
            self, build_key: str, target_quantity: int | None, clear: bool = False,
            can_hide: bool = False):
        """
        Shows/hides appropriate amount of buttons of the given category; updates build; space build
        only

        Parameters:
        - :param build_key: key to self._build_data
        - :param target_quantity: number of slots that should be available in this category
        - :param clear: True to clear build
        - :param can_hide: hides/shows category label when target_quantity is 0/None
        """
        if target_quantity is None or target_quantity == 0:
            target_quantity = 0
            getattr(self.space, build_key + '_label').hide()
        elif can_hide:
            getattr(self.space, build_key + '_label').show()
        buttons: list[ItemButton] = getattr(self.space, build_key)
        max_quantity = len(buttons)
        for show_index in range(target_quantity):
            buttons[show_index].show()
            if clear:
                buttons[show_index].clear()
                self._build_data['space'][build_key][show_index] = ''
        for hide_index in range(target_quantity, max_quantity):
            buttons[hide_index].clear()
            buttons[hide_index].hide()
            self._build_data['space'][build_key][hide_index] = None

    def update_starship_traits(self, target_quantity: int, clear: bool = False):
        """
        Shows/hides appropriate amount of starship trait buttons; updates `self._build_data`

        Parameters:
        - :param target_quantity: number of slots that should be available in this category
        - :param clear: True to clear build
        """
        buttons = self.space.starship_traits
        for show_index in range(target_quantity):
            buttons[show_index].show()
            if clear:
                buttons[show_index].clear()
                self._build_data['space']['starship_traits'][show_index] = ''
        for hide_index in range(target_quantity, 7):
            buttons[hide_index].clear()
            buttons[hide_index].hide()
            self._build_data['space']['starship_traits'][hide_index] = None

    def update_boff_seat(
            self, boff_id: int, rank: int, profession: str, specialization: str = '',
            clear: bool = False, hide_seat: bool = False, sci_destroyer_seat: bool = False):
        """
        Shows/hides appropriate amount of buttons of the boff seat; updates build; space build only

        Parameters:
        - :param boff_id: boff number counted from the top/beginning
        - :param rank: number of slots that should be available in this category
        - :param profession: seat profession
        - :param specialization: seat specialization
        - :param clear: set to True to clear build
        - :param hide_seat: hides/shows seat label
        - :param sci_destroyer_seat: set to `True` to upgrade seat to commander and show info label
        """
        buttons = self.space.boffs[boff_id]
        max_quantity = 4
        if sci_destroyer_seat:
            rank = 4
        for show_index in range(rank):
            buttons[show_index].show()
            if clear:
                buttons[show_index].clear()
                self._build_data['space']['boffs'][boff_id][show_index] = ''
        for hide_index in range(rank, max_quantity):
            buttons[hide_index].clear()
            buttons[hide_index].hide()
            self._build_data['space']['boffs'][boff_id][hide_index] = None
        label = self.space.boff_labels[boff_id]
        label.clear()
        if hide_seat:
            label.hide()
        else:
            label.show()
            if specialization != '':
                spec_label = f' / {specialization}'
            else:
                spec_label = ''
            if profession == 'Universal':
                label_options = (
                    f'Tactical{spec_label}',
                    f'Science{spec_label}',
                    f'Engineering{spec_label}'
                )
                label.setDisabled(False)
            else:
                label_options = (profession + spec_label,)
                label.setDisabled(True)
            label.addItems(label_options)
        icon_label = self.space.boff_label_icons[boff_id]
        if sci_destroyer_seat:
            if profession == 'Science':
                icon_label.setPixmap(self._images.icons['sci-small'])
                icon_label._tooltip.setText('Commander slot only available in science mode.')
            elif profession == 'Tactical':
                icon_label.setPixmap(self._images.icons['tac-small'])
                icon_label._tooltip.setText('Commander slot only available in tactical mode.')
            icon_label.show()
        else:
            icon_label.hide()
        if clear:
            default_profession = 'Tactical' if profession == 'Universal' else profession
            self._build_data['space']['boff_specs'][boff_id] = [default_profession, specialization]

    def load_equipment_cat(self, build_key: str, environment: str):
        """
        Updates equipment category buttons to show items from build.

        Parameters:
        - :param build_key: equipment category
        - :param environment: space/ground
        """
        for subkey, item in enumerate(self._build_data[environment][build_key]):
            if item is not None and item != '':
                self.slot_equipment_item(item, environment, build_key, subkey)
            else:
                getattr(getattr(self, environment), build_key)[subkey].clear()

    def clear_equipment_cat_ground(self, build_key: str):
        """
        Clears buttons and build; ground build only

        Parameters:
        - :param build_key: key to self._build_data
        """
        category: list[ItemButton] = getattr(self.ground, build_key)
        for subkey, button in enumerate(category):
            button.clear()
            self._build_data['ground'][build_key][subkey] = ''

    def load_trait_cat(self, build_key: str, environment: str):
        """
        Updates trait category buttons to show items from build.

        Parameters:
        - :param build_key: trait category
        - :param environment: space/ground
        """
        for subkey, item in enumerate(self._build_data[environment][build_key]):
            if item is not None and item != '':
                self.slot_trait_item(item, environment, build_key, subkey)
            else:
                getattr(getattr(self, environment), build_key)[subkey].clear()

    def slot_equipment_item(
            self, item: dict[str, str], environment: str, build_key: str, build_subkey: int):
        """
        Updates build and UI with item

        Parameters:
        - :param item: item to be slotted
        - :param environment: space/ground
        - :param build_key: key to self._build_data[environment]
        - :param build_subkey: index of the item within its build_key (category)
        """
        self._build_data[environment][build_key][build_subkey] = item
        overlay = getattr(self._images.overlays, item['rarity'].lower().replace(' ', ''))
        tooltip = add_equipment_tooltip_header(
            item, self._cache.equipment[build_key][item['item']], self._tooltip_styles)
        item_button: ItemButton = getattr(getattr(self, environment), build_key)[build_subkey]
        item_button.set_item_full(self._images.get(item['item']), overlay, tooltip)

    def slot_trait_item(
            self, item: dict[str, str], environment: str, build_key: str, build_subkey: int):
        """
        Updates build and UI with item

        Parameters:
        - :param item: item to be slotted
        - :param environment: space/ground
        - :param build_key: key to self._build_data[environment]
        - :param build_subkey: index of the item within its build_key (category)
        """
        item_name = item['item']
        self._build_data[environment][build_key][build_subkey] = item
        alt_image_key = f"{item_name}__{environment}__{build_key}"
        if alt_image_key in self._cache.alt_images:
            item_image = self._images.get(self._cache.alt_images[alt_image_key])
        else:
            item_image = self._images.get(item_name)
        item_button: ItemButton = getattr(getattr(self, environment), build_key)[build_subkey]
        if build_key == 'starship_traits':
            tooltip = self._cache.starship_traits[item_name]['tooltip']
        elif environment == 'space':
            tooltip = self._cache.space_traits[build_key][item_name]['tooltip']
        else:
            tooltip = self._cache.ground_traits[build_key][item_name]['tooltip']
        item_button.set_item_full(item_image, None, tooltip)

    def unslot_item(self, environment: str, build_key: str, build_subkey: int, boff_id: int = -1):
        """
        Updates build and UI with item

        Parameters:
        - :param item: item to be slotted
        - :param environment: space/ground
        - :param build_key: key to self._build_data[environment]
        - :param build_subkey: index of the item within its build_key (category)
        - :param boff_id: id of the boff seat; assumes non-boff item when `-1` or not supplied
        """
        if boff_id == -1:
            self._build_data[environment][build_key][build_subkey] = ''
            item_button: ItemButton = getattr(getattr(self, environment), build_key)[build_subkey]
            item_button.clear()
        else:
            self._build_data[environment][build_key][boff_id][build_subkey] = ''
            item_button: ItemButton = getattr(
                getattr(self, environment), build_key)[boff_id][build_subkey]
            item_button.clear()

    @Slot(dict, ItemSlot)
    def handle_picker_result(self, new_item: dict[str, str | list[str]], slot: ItemSlot):
        """
        Inserts picked item into given slot if picking was not cancelled.

        Parameters:
        - :param new_item: contains picked item, or empty item if picking was cancelled
        - :param slot: information about the slot
        """
        if new_item['item'] != '':
            widget_storage = self.space if slot.environment == 'space' else self.ground
            if slot.is_equipment:
                if 'consoles' in slot.type:
                    item_data = self._cache.equipment[slot.type][new_item['item']]
                    type_ = EQUIPMENT_TYPES[item_data['type']]
                    for i, mod in enumerate(new_item['modifiers']):
                        if mod not in self._cache.modifiers[type_]:
                            new_item['modifiers'][i] = ''
                self.slot_equipment_item(new_item, slot.environment, slot.type, slot.index)
            else:
                if slot.boff_id is None:
                    self.slot_trait_item(
                        {'item': new_item['item']}, slot.environment, slot.type, slot.index)
                elif slot.type == 'boffs':
                    ability_name, _, ability_rank = new_item['item'].rpartition(' ')
                    self._build_data[slot.environment]['boffs'][slot.boff_id][slot.index] = {
                        'item': ability_name,
                        'rank': ability_rank
                    }
                    button: ItemButton = widget_storage.boffs[slot.boff_id][slot.index]
                    button.set_item(self._images.get(ability_name))
                    button.tooltip = (self._cache.boff_abilities['all'][ability_name][ability_rank])
            self.autosave()

    @Slot(str)
    def finish_ship_pick(self, ship_name: str):
        """
        Switches to selected ship.

        Parameters:
        - :param ship_name: name of the selected ship, or empty
        """
        if ship_name == '':
            return
        self._building = True
        self.ship.button.setText(ship_name)
        ship_data = self._cache.ships[ship_name]
        self.set_ship_image(ship_data['image'][5:])
        tier = ship_data['tier']
        self.ship.tier.clear()
        if tier == 6:
            self.ship.tier.addItems(('T6', 'T6-X', 'T6-X2'))
        elif tier == 5:
            self.ship.tier.addItems(('T5', 'T5-U', 'T5-X', 'T5-X2'))
        else:
            self.ship.tier.addItem(f'T{tier}')
        self._build_data['space']['ship'] = ship_name
        self._build_data['space']['tier'] = f'T{tier}'
        if ship_data['equipcannons'] == 'yes':
            self.ship.dc.show()
        else:
            self.ship.dc.hide()
        self.align_space_frame(ship_data, clear=True)
        self._building = False
        self.autosave()

    @Slot(dict, ItemSlot)
    def finish_item_edit(self, new_item: dict[str], slot: ItemSlot):
        """
        Updates item after editing if editing was not cancelled. Autosaves.

        Parameters:
        - :param new_item: contains the new item
        - :param slot: information about the slot
        """
        if new_item['item'] != '':
            self.slot_equipment_item(new_item, slot.environment, slot.type, slot.index)
            self.autosave()

    def load_boff_stations(self, environment: str):
        """
        Updates boff stations to show items from build

        Parameters:
        - :param environment: "space" / "ground"
        """
        if environment == 'space':
            for boff_id, boff_data in enumerate(self._build_data['space']['boffs']):
                boff_spec = self._build_data['space']['boff_specs'][boff_id]
                if boff_spec[1] == '':
                    boff_text = boff_spec[0]
                else:
                    boff_text = f'{boff_spec[0]} / {boff_spec[1]}'
                self.space.boff_labels[boff_id].setCurrentText(boff_text)
                for ability, slot in zip(boff_data, self.space.boffs[boff_id]):
                    if ability is not None and ability != '':
                        slot.set_item_full(
                            self._images.get(ability['item']), None,
                            self._cache.boff_abilities['all'][ability['item']][ability['rank']])
                    else:
                        slot.clear()
        elif environment == 'ground':
            for boff_id, boff_data in enumerate(self._build_data['ground']['boffs']):
                self.ground.boff_profs[boff_id].setCurrentText(
                    self._build_data['ground']['boff_profs'][boff_id])
                self.ground.boff_specs[boff_id].setCurrentText(
                    self._build_data['ground']['boff_specs'][boff_id])
                for ability, slot in zip(boff_data, self.ground.boffs[boff_id]):
                    if ability is not None and ability != '':
                        slot.set_item_full(
                            self._images.get(ability['item']), None,
                            self._cache.boff_abilities['all'][ability['item']][ability['rank']])
                    else:
                        slot.clear()

    def clear_boff_seat_ground(self, boff_id: int):
        """
        Resets boff seat.

        Parameters:
        - :param boff_id: boff number counted from the top/beginning
        """
        boff_station: list[ItemButton] = self.ground.boffs[boff_id]
        for subkey, button in enumerate(boff_station):
            button.clear()
            self._build_data['ground']['boffs'][boff_id][subkey] = ''
        self.ground.boff_profs[boff_id].setCurrentText('Tactical')
        self._build_data['ground']['boff_profs'][boff_id] = 'Tactical'
        self.ground.boff_specs[boff_id].setCurrentText('Command')
        self._build_data['ground']['boff_specs'][boff_id] = 'Command'

    def load_doffs(self, environment: str):
        """
        Updates UI to show doffs in self._build_data

        Parameters:
        - :param environment: "space" / "ground"
        """
        if environment == 'space':
            doff_zipper = zip(
                self.space.doffs_spec, self._build_data['space']['doffs_spec'],
                self.space.doffs_variant, self._build_data['space']['doffs_variant'])
        elif environment == 'ground':
            doff_zipper = zip(
                self.ground.doffs_spec, self._build_data['ground']['doffs_spec'],
                self.ground.doffs_variant, self._build_data['ground']['doffs_variant'])
        for spec_combo, spec, variant_combo, variant in doff_zipper:
            spec_combo.setCurrentText(spec)
            if spec != '':
                variants = getattr(self._cache, f'{environment}_doffs')[spec].keys()
                variant_combo.addItems({''} | variants)
                variant_combo.setCurrentText(variant)

    def load_skill_pages(self):
        """
        Updates UI to show skill trees in self._build_data
        """
        self.skills.space_desc.setPlainText(self._build_data['skill_desc']['space'])
        self._skill_state['space_points_eng'] = 0
        self._skill_state['space_points_sci'] = 0
        self._skill_state['space_points_tac'] = 0
        self._skill_state['space_points_rank'] = [0] * 5
        self._skill_state['space_points_total'] = 0
        for career in ('eng', 'sci', 'tac'):
            for skill_id, (button, enable) in enumerate(zip(
                    self.skills.space[career], self._build_data['space_skills'][career])):
                if enable:
                    button.set_overlay(self._images.overlays.check)
                    button.highlight = True
                    self._skill_state[f'space_points_{career}'] += 1
                    self._skill_state['space_points_rank'][int(skill_id / 6)] += 1
                else:
                    button.clear_overlay()
                    button.highlight = False
        self._skill_state['space_points_total'] = sum(self._skill_state['space_points_rank'])
        for career in ('eng', 'sci', 'tac'):
            skill_points = self._skill_state[f'space_points_{career}']
            self.skills.count_labels[career].setText(str(skill_points))
            for unlock_id, unlock_choice in enumerate(self._build_data['skill_unlocks'][career]):
                self.set_skill_unlock_space(career, unlock_id, unlock_choice, skill_points)
            if skill_points > 24:
                skill_points = 24
            for i in range(skill_points):
                self.skills.bonus_bars[career][i].setChecked(True)
            for i in range(skill_points, 24, 1):
                self.skills.bonus_bars[career][i].setChecked(False)

        self.skills.ground_desc.setPlainText(self._build_data['skill_desc']['ground'])
        self._skill_state['ground_points_total'] = 0
        ground_skills: list[list[bool]] = self._build_data['ground_skills']
        for skill_buttons, skill_data in zip(self.skills.ground, ground_skills):
            for skill_button, enable in zip(skill_buttons, skill_data):
                if enable:
                    skill_button.set_overlay(self._images.overlays.check)
                    skill_button.highlight = True
                    self._skill_state['ground_points_total'] += 1
                else:
                    skill_button.clear_overlay()
                    skill_button.highlight = False
        self.skills.count_labels['ground'].setText(str(self._skill_state['ground_points_total']))
        for i in range(self._skill_state['ground_points_total']):
            self.skills.bonus_bars['ground'][i].setChecked(True)
        for i in range(self._skill_state['ground_points_total'], 10, 1):
            self.skills.bonus_bars['ground'][i].setChecked(False)
        for unlock_id, unlock_choice in enumerate(self._build_data['skill_unlocks']['ground']):
            self.set_skill_unlock_ground(unlock_id, unlock_choice)

    def set_skill_unlock_space(
            self, career: str, id: int, state: int | None = None, points_spent: int = -1):
        """
        Sets unlock button to state and updates build

        Parameters:
        - :param career: "eng" / "sci" / "tac"
        - :param id: id of the unlock, counted from the unlock with the lowest requirement
        - :param state: `0`, `1` set the button to the respective unlock, `None` clears
        """
        unlock_button = self.skills.unlocks[career][id]
        if id == 4:
            if points_spent > 27 and state == self._build_data['skill_unlocks'][career][id]:
                return
            if state is None:
                unlock_button.clear()
                self._build_data['skill_unlocks'][career][id] = None
            else:
                unlock_data = self._cache.skills['space_unlocks'][career][4]
                unlock_button.set_item(self._images.get(unlock_data['name']))
                if points_spent > 26:
                    unlock_button.tooltip = get_ultimate_skill_unlock_tooltip(
                        unlock_data, state, 3, self._tooltip_styles)
                    self._build_data['skill_unlocks'][career][id] = 3
                else:
                    unlock_button.tooltip = get_ultimate_skill_unlock_tooltip(
                        unlock_data, state, points_spent - 24, self._tooltip_styles)
                    self._build_data['skill_unlocks'][career][id] = state
                if not self._building:
                    unlock_button.force_tooltip_update()
        else:
            if state is None:
                unlock_button.clear()
                self._build_data['skill_unlocks'][career][id] = None
            else:
                unlock_data = self._cache.skills['space_unlocks'][career][id]['nodes'][state]
                if state == 0:
                    unlock_button.set_item(self._images.get('arrow-up'))
                elif state == 1:
                    unlock_button.set_item(self._images.get('arrow-down'))
                unlock_button.tooltip = (
                    f"<p style='{self._tooltip_styles.equipment_name}color:#ffd700;'>"
                    f"{unlock_data['name']}</p>"
                    f"<p style='{self._tooltip_styles.equipment_type_subheader}color:#ffd700;'>"
                    f"Space Skill</p><p>{unlock_data['desc']}</p>")
                self._build_data['skill_unlocks'][career][id] = state
                if not self._building:
                    unlock_button.force_tooltip_update()

    def set_skill_unlock_ground(self, id: int, state: int | None):
        """
        Sets unlock button to state and updates build

        Parameters:
        - :param id: id of the unlock, counted from the unlock with the lowest requirement
        - :param state: `0`, `1` set the button to the respective unlock, `None` clears
        """
        unlock_button = self.skills.unlocks['ground'][id]
        if state is None:
            unlock_button.clear()
            self._build_data['skill_unlocks']['ground'][id] = None
        else:
            unlock_data = self._cache.skills['ground_unlocks'][id]['nodes'][state]
            if state == 0:
                unlock_button.set_item(self._images.get('arrow-up'))
            elif state == 1:
                unlock_button.set_item(self._images.get('arrow-down'))
            unlock_button.tooltip = (
                f"<p style='{self._tooltip_styles.equipment_name}color:#ffd700;'>"
                f"{unlock_data['name']}</p>"
                f"<p style='{self._tooltip_styles.equipment_type_subheader}color:#ffd700;'>"
                f"Space Skill</p><p>{unlock_data['desc']}</p>")
            self._build_data['skill_unlocks']['ground'][id] = state
            if not self._building:
                unlock_button.force_tooltip_update()

    def faction_combo_callback(self, new_faction: str):
        """
        Saves new faction and changes species selector choices.

        Parameters:
        - :param new_faction: name of the new faction
        """
        self._build_data['captain']['faction'] = new_faction
        self.character.species.clear()
        if new_faction != '':
            self.character.species.addItems(('', *SPECIES[new_faction]))
        self._build_data['captain']['species'] = ''
        self.autosave()

    def species_combo_callback(self, new_species: str):
        """
        Saves new species to build and changes species trait

        Parameters:
        - :param new_species: name of the new species
        """
        self._build_data['captain']['species'] = new_species
        if new_species == 'Alien':
            if not self._building:
                self._build_data['space']['traits'][10] = ''
                self._build_data['ground']['traits'][10] = ''
                self._build_data['space']['traits'][11] = ''
                self._build_data['ground']['traits'][11] = ''
            self.space.traits[10].show()
            self.ground.traits[10].show()
            self.space.traits[11].clear()
            self.ground.traits[11].clear()
        else:
            self.space.traits[10].hide()
            self.ground.traits[10].hide()
            self.space.traits[10].clear()
            self.ground.traits[10].clear()
            self._build_data['space']['traits'][10] = None
            self._build_data['ground']['traits'][10] = None
            new_space_trait = SPECIES_TRAITS['space'].get(new_species, '')
            new_ground_trait = SPECIES_TRAITS['ground'].get(new_species, '')
            if new_space_trait == '':
                self.space.traits[11].clear()
                self._build_data['space']['traits'][11] = ''
            else:
                self.slot_trait_item({'item': new_space_trait}, 'space', 'traits', 11)
            if new_ground_trait == '':
                self.ground.traits[11].clear()
                self._build_data['ground']['traits'][11] = ''
            else:
                self.slot_trait_item({'item': new_ground_trait}, 'ground', 'traits', 11)
        self.autosave()

    def spec_combo_callback(self, primary: bool, new_spec: str):
        """
        Saves new spec to build and adjusts choices in other spec combo box.

        Parameters:
        - :param primary: `True` when editing primary spec, `False` when editing secondary spec
        - :param new_spec: name of the new specialization
        """
        if primary:
            self._build_data['captain']['primary_spec'] = new_spec
            secondary_combo = self.character.secondary
            secondary_specs = set()
            remove_index = None
            for i in range(secondary_combo.count()):
                secondary_specs.add(secondary_combo.itemText(i))
                if secondary_combo.itemText(i) == new_spec and new_spec != '':
                    remove_index = i
            if remove_index is not None:
                secondary_combo.removeItem(remove_index)
            secondary_combo.addItems((PRIMARY_SPECS | SECONDARY_SPECS) - secondary_specs)
        else:
            self._build_data['captain']['secondary_spec'] = new_spec
            primary_combo = self.character.primary
            primary_specs = set()
            remove_index = None
            for i in range(primary_combo.count()):
                primary_specs.add(primary_combo.itemText(i))
                if primary_combo.itemText(i) == new_spec and new_spec != '':
                    remove_index = i
            if remove_index is not None:
                primary_combo.removeItem(remove_index)
            primary_combo.addItems(PRIMARY_SPECS - primary_specs)
        self.autosave()

    def elite_callback(self, state: Qt.CheckState):
        """
        Saves new state and updates build.

        Parameters:
        - :param state: new state of the checkbox
        """
        if state == Qt.CheckState.Checked:
            if not self._building:
                self._build_data['captain']['elite'] = True
                self._build_data['space']['traits'][9] = ''
                self._build_data['ground']['traits'][9] = ''
                self._build_data['ground']['kit_modules'][5] = ''
                self._build_data['ground']['ground_devices'][4] = ''
            self.space.traits[9].show()
            self.ground.traits[9].show()
            self.ground.kit_modules[5].show()
            self.ground.ground_devices[4].show()
        else:
            if not self._building:
                self._build_data['captain']['elite'] = False
                self._build_data['space']['traits'][9] = None
                self._build_data['ground']['traits'][9] = None
                self._build_data['ground']['kit_modules'][5] = None
                self._build_data['ground']['ground_devices'][4] = None
            self.space.traits[9].hide()
            self.space.traits[9].clear()
            self.ground.traits[9].hide()
            self.ground.traits[9].clear()
            self.ground.kit_modules[5].hide()
            self.ground.kit_modules[5].clear()
            self.ground.ground_devices[4].hide()
            self.ground.ground_devices[4].clear()
        self.autosave()

    def boff_profession_callback_space(self, boff_id: int, new_spec: str):
        """
        updates build with newly assigned profession; clears abilities of the old profession

        Parameters:
        - :param boff_id: identifies the boff station
        - :param new_spec: new profession and specialization
        """
        if self._building:
            return
        if ' / ' in new_spec:
            profession, specialization = new_spec.split(' / ')
            if specialization == 'Temporal Operative':
                specialization = 'Temporal'
            # Lt. Commander rank contains all abilities
            all_abilities = self._cache.boff_abilities['space'][specialization][2]
            for ability_num, ability in enumerate(self._build_data['space']['boffs'][boff_id]):
                if ability is not None and ability != '' and ability['item'] not in all_abilities:
                    self._build_data['space']['boffs'][boff_id][ability_num] = ''
                    self.space.boffs[boff_id][ability_num].clear()
        else:
            profession = new_spec
            specialization = ''
            for ability_num, ability in enumerate(self._build_data['space']['boffs'][boff_id]):
                if ability is not None and ability != '':
                    self._build_data['space']['boffs'][boff_id][ability_num] = ''
                    self.space.boffs[boff_id][ability_num].clear()
        self._build_data['space']['boff_specs'][boff_id] = [profession, specialization]
        self.autosave()

    def boff_label_callback_ground(self, boff_id: int, type_: str, new_text: str):
        """
        updates build with newly assigned profession or specialization; clears invalid abilities

        Parameters:
        - :param boff_id: number of the boff station
        - :param type_: "boff_profs" / "boff_specs"
        - :param new_text: new profession / specialization
        """
        if self._building:
            return
        self._build_data['ground'][type_][boff_id] = new_text
        other_type = 'boff_profs' if type_ == 'boff_specs' else 'boff_specs'
        other_text = self._build_data['ground'][other_type][boff_id]
        ground_abilities = self._cache.boff_abilities['ground']
        for ability_num, ability in enumerate(self._build_data['ground']['boffs'][boff_id]):
            if ability is not None and ability != '':
                # Lt. Commander and Commander rank combined contain all abilities
                if (ability['item'] not in ground_abilities[new_text][2]
                        and ability['item'] not in ground_abilities[new_text][3]
                        and ability['item'] not in ground_abilities[other_text][2]
                        and ability['item'] not in ground_abilities[other_text][3]):
                    self._build_data['ground']['boffs'][boff_id][ability_num] = ''
                    self.ground.boffs[boff_id][ability_num].clear()
        self.autosave()

    def tier_callback(self, new_tier: str):
        """
        Updates build according to new tier
        """
        if self._building:
            return
        self._build_data['space']['tier'] = new_tier
        ship_name = self._build_data['space']['ship']
        if ship_name == '<Pick Ship>':
            ship_data = SHIP_TEMPLATE
        else:
            ship_data = self._cache.ships[ship_name]
        uni, eng, sci, tac, devices, starship_traits = get_variable_slot_counts(ship_data, new_tier)
        self.update_equipment_cat('uni_consoles', uni, can_hide=True)
        self.update_equipment_cat('eng_consoles', eng)
        self.update_equipment_cat('sci_consoles', sci)
        self.update_equipment_cat('tac_consoles', tac)
        self.update_equipment_cat('devices', devices)
        self.update_starship_traits(starship_traits)
        self.autosave()

    def ship_info_callback(self):
        """
        Opens wiki page of ship if ship is slotted
        """
        if self._build_data['space']['ship'] != '<Pick Ship>':
            open_wiki_page(self._cache.ships[self._build_data['space']['ship']]['Page'])

    def doff_spec_callback(self, new_spec: str, environment: str, doff_id: int):
        """
        Callback for duty officer specialization combobox.

        Parameters:
        - :param new_spec: selected specialization
        - :param environment: "space" / "ground"
        - :param doff_id: index of the doff
        """
        if self._building:
            return
        self._build_data[environment]['doffs_spec'][doff_id] = new_spec
        self._build_data[environment]['doffs_variant'][doff_id] = ''
        widget_storage = self.space if environment == 'space' else self.ground
        widget_storage.doffs_variant[doff_id].clear()
        if new_spec != '':
            variants = getattr(self._cache, f'{environment}_doffs')[new_spec].keys()
            widget_storage.doffs_variant[doff_id].addItems({''} | variants)
        self.autosave()

    def doff_variant_callback(self, new_variant: str, environment: str, doff_id: int):
        """
        Callback for duty officer variant combobox.

        Parameters:
        - :param new_variant: selected variant
        - :param environment: "space" / "ground"
        - :param doff_id: index of the doff
        """
        if self._building:
            return
        self._build_data[environment]['doffs_variant'][doff_id] = new_variant
        self.autosave()

    def toggle_space_skill(self, current_state: bool, career: str, skill_id: int):
        """
        Activates space skill if it's deactivated, deactivates skill if it's activated.

        Parameters:
        - :param current_state: state of the button before toggling
        - :param career: "eng" / "tac" / "sci"
        - :param skill_id: id of the skill node
        """
        if current_state:
            self.skills.space[career][skill_id].clear_overlay()
            self.skills.space[career][skill_id].highlight = False
            self._build_data['space_skills'][career][skill_id] = False
            self._skill_state['space_points_total'] -= 1
            self._skill_state[f'space_points_{career}'] -= 1
            self._skill_state['space_points_rank'][int(skill_id / 6)] -= 1
            segment_index: int = self._skill_state[f'space_points_{career}']
            if segment_index < 24:
                self.skills.bonus_bars[career][segment_index].setChecked(False)
                if segment_index % 5 == 4:
                    button_index = (segment_index - 4) // 5
                    self.set_skill_unlock_space(career, button_index, None)
                elif segment_index == 23:
                    self.set_skill_unlock_space(career, 4, None)
            elif 24 <= segment_index <= 26:
                self.set_skill_unlock_space(career, 4, 0, segment_index)
        else:
            self.skills.space[career][skill_id].set_overlay(self._images.overlays.check)
            self.skills.space[career][skill_id].highlight = True
            self._build_data['space_skills'][career][skill_id] = True
            self._skill_state['space_points_total'] += 1
            self._skill_state[f'space_points_{career}'] += 1
            self._skill_state['space_points_rank'][int(skill_id / 6)] += 1
            segment_index: int = self._skill_state[f'space_points_{career}'] - 1
            if segment_index < 24:
                self.skills.bonus_bars[career][segment_index].setChecked(True)
                if segment_index % 5 == 4:
                    button_index = (segment_index - 4) // 5
                    self.set_skill_unlock_space(career, button_index, 0)
                elif segment_index == 23:
                    self.set_skill_unlock_space(career, 4, -1, 24)
            elif 24 <= segment_index <= 25:
                self.set_skill_unlock_space(career, 4, 0, segment_index + 1)
            elif segment_index == 26:
                self.set_skill_unlock_space(career, 4, 3, 27)
        self.skills.count_labels[career].setText(str(self._skill_state[f'space_points_{career}']))
        self.autosave()

    def skill_unlock_callback(self, bar: str, unlock_id: int):
        """
        Callback for skill unlock buttons

        Parameters:
        - :param bar: "eng" / "sci" / "tac" / "ground"
        - :param unlock_id: index of the unlock button
        """
        current_state = self._build_data['skill_unlocks'][bar][unlock_id]
        if current_state is None:
            return
        if bar == 'ground':
            if current_state == 0:
                self.set_skill_unlock_ground(unlock_id, 1)
            elif current_state == 1:
                self.set_skill_unlock_ground(unlock_id, 0)
            self.autosave()
        else:
            if unlock_id < 4:
                if current_state == 0:
                    self.set_skill_unlock_space(bar, unlock_id, 1)
                elif current_state == 1:
                    self.set_skill_unlock_space(bar, unlock_id, 0)
                self.autosave()
            else:
                points_spent = self._skill_state[f'space_points_{bar}']
                if 25 <= points_spent <= 26:
                    self.set_skill_unlock_space(bar, 4, (current_state + 1) % 3, points_spent)
                    self.autosave()

    def toggle_ground_skill(self, current_state: bool, skill_group: int, skill_id: int):
        """
        Activates ground skill if it's deactivated, deactivates skill if it's activated.

        Parameters:
        - :param current_state: state of the button before toggling
        - :param skill_group: number [0, 3] identifying the skill group
        - :param skill_id: index of the skill within the group
        """
        if current_state:
            self.skills.ground[skill_group][skill_id].clear_overlay()
            self.skills.ground[skill_group][skill_id].highlight = False
            self._build_data['ground_skills'][skill_group][skill_id] = False
            self._skill_state['ground_points_total'] -= 1
            segment_index = self._skill_state['ground_points_total']
            self.skills.bonus_bars['ground'][segment_index].setChecked(False)
            if segment_index % 2 == 1:
                button_index = (segment_index - 1) // 2
                self.set_skill_unlock_ground(button_index, None)
        else:
            self.skills.ground[skill_group][skill_id].set_overlay(self._images.overlays.check)
            self.skills.ground[skill_group][skill_id].highlight = True
            self._build_data['ground_skills'][skill_group][skill_id] = True
            self._skill_state['ground_points_total'] += 1
            segment_index = self._skill_state['ground_points_total'] - 1
            self.skills.bonus_bars['ground'][segment_index].setChecked(True)
            if segment_index % 2 == 1:
                button_index = (segment_index - 1) // 2
                self.set_skill_unlock_ground(button_index, 0)
        self.skills.count_labels['ground'].setText(str(self._skill_state['ground_points_total']))
        self.autosave()

    def skill_callback_space(self, career: str, skill_id: int, grouping: str):
        """
        Callback for space skill node

        Parameters:
        - :param career: "eng" / "tac" / "sci"
        - :param skill_id: id of the skill node (index in self._build_data)
        - :param grouping: type of skill grouping: "column" / "pair+1" / "separate"
        """
        space_skills = self._build_data['space_skills']
        skill_active = space_skills[career][skill_id]
        skill_lvl = skill_id % 3
        skill_rank = int(skill_id / 6)
        if skill_active:  # check for valid deselect
            if (skill_lvl == 2
                    or grouping != 'column' and skill_lvl == 1
                    or not space_skills[career][skill_id + 1]):
                skill_count = sum(self._skill_state['space_points_rank'][:skill_rank + 1])
                for offset, points_required in enumerate(SKILL_POINTS_FOR_RANK[skill_rank + 1:]):
                    if (skill_count - 1 < points_required
                            and self._skill_state['space_points_total'] - skill_count > 0):
                        return
                    skill_count += self._skill_state['space_points_rank'][skill_rank + offset + 1]
                self.toggle_space_skill(skill_active, career, skill_id)
        else:  # check for valid select
            if 46 > self._skill_state['space_points_total'] >= SKILL_POINTS_FOR_RANK[skill_rank]:
                if skill_lvl == 0:
                    self.toggle_space_skill(skill_active, career, skill_id)
                elif (grouping == 'column' and space_skills[career][skill_id - 1]):
                    self.toggle_space_skill(skill_active, career, skill_id)
                elif (grouping != 'column' and space_skills[career][skill_id - skill_lvl]):
                    self.toggle_space_skill(skill_active, career, skill_id)

    def skill_callback_ground(self, skill_group: int, skill_id: int):
        """
        Callback for ground skill node

        Parameters:
        - :param skill_group: number [0, 3] identifying the skill group
        - :param skill_id: index of the skill within the group
        """
        ground_skills = self._build_data['ground_skills']
        skill_active = ground_skills[skill_group][skill_id]
        if skill_active:  # check for valid deselect
            if skill_id == 0 and (
                    ground_skills[skill_group][1] or ground_skills[skill_group][2]
                    or skill_group <= 1 and ground_skills[skill_group][4]):
                return
            elif skill_id % 2 == 0 and ground_skills[skill_group][skill_id + 1]:
                return
            self.toggle_ground_skill(skill_active, skill_group, skill_id)
        else:  # check for valid select
            if self._skill_state['ground_points_total'] < 10:
                if skill_id % 2 == 1 and ground_skills[skill_group][skill_id - 1]:
                    self.toggle_ground_skill(skill_active, skill_group, skill_id)
                elif skill_id == 0:
                    self.toggle_ground_skill(skill_active, skill_group, skill_id)
                elif (skill_id == 2 or skill_id == 4) and ground_skills[skill_group][0]:
                    self.toggle_ground_skill(skill_active, skill_group, skill_id)
