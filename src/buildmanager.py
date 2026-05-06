from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QLineEdit, QPlainTextEdit, QPushButton

from .buildhelpers import get_boff_spec, get_variable_slot_counts, empty_build
from .cargomanager import CargoManager
from .constants import SHIP_TEMPLATE
from .imagemanager import ImageManager
from .iofunc import store_json__new
from .textedit import add_equipment_tooltip_header__new, get_ultimate_skill_unlock_tooltip__new
from .theme import TooltipCSS
from .widgets import ItemButton, ShipButton, ShipImage, Thread, TooltipLabel



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
        self.fore_weapons: list[ItemButton] = [None]
        self.hangars: list[ItemButton] = [None] * 2
        self.hangars_label: QLabel = None
        self.rep_traits: list[ItemButton] = [None] * 5
        self.sci_consoles: list[ItemButton] = [None] * 5
        self.sci_consoles_label: QLabel = None
        self.sec_def: list[ItemButton] = [None]
        self.sec_def_label: list[ItemButton] = [None]
        self.shield: list[ItemButton] = [None]
        self.starship_traits: list[ItemButton] = [None]
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
    
    def autosave(self):
        """
        Saves build to autosave file.
        """
        if not self._building:
            store_json__new(self._build_data, self._autosave_path)
    
    def load_build(self):
        """
        Updates UI to show the build currently in self._build_data
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
        if ship == '' or ship == '<Pick Ship>':
            self.align_space_frame(ship_data, clear=True)
        else:
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

        boff_specs = map(lambda s: get_boff_spec(self, s), ship_data['boffs'])
        if 'Science Destroyer' in ship_data['type']:
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

    def update_equipment_cat(
            self, build_key: str, target_quantity: int | None, clear: bool = False,
            can_hide: bool = False):
        """
        Shows/hides appropriate amount of buttons of the given category; updates build; space build
        only

        Parameters:
        - :param build_key: key to self.build and self.widgets
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
        Shows/hides appropriate amount of starship trait buttons; updates `self.build`

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

    def load_trait_cat(self, build_key: str, environment: str):
        """
        Updates trait category buttons to show items from build.

        Parameters:
        - :param build_key: trait category
        - :param environment: space/ground
        """
        for subkey, item in enumerate(self.build[environment][build_key]):
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
        - :param build_key: key to self.build[environment]
        - :param build_subkey: index of the item within its build_key (category)
        """
        self._build_data[environment][build_key][build_subkey] = item
        overlay = getattr(self._images.overlays, item['rarity'].lower().replace(' ', ''))
        tooltip = add_equipment_tooltip_header__new(
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
        - :param build_key: key to self.build[environment]
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

    def load_doffs(self, environment: str):
        """
        Updates UI to show doffs in self.build

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
        Updates UI to show skill trees in self.build
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
                self.set_skill_unlock_space(self, career, unlock_id, unlock_choice, skill_points)
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
                    unlock_button.tooltip = get_ultimate_skill_unlock_tooltip__new(
                        unlock_data, state, 3, self._tooltip_styles)
                    self._build_data['skill_unlocks'][career][id] = 3
                else:
                    unlock_button.tooltip = get_ultimate_skill_unlock_tooltip__new(
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
