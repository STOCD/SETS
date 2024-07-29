from datetime import datetime
from json import JSONDecodeError
import os
import sys

from PySide6.QtCore import Qt
from requests.exceptions import Timeout
from requests_html import Element

from .callbacks import (
        enter_splash, exit_splash, faction_combo_callback, spec_combo_callback, splash_text)
from .constants import (
        BOFF_URL, CAREERS, DOFF_QUERY_URL, EQUIPMENT_TYPES, ITEM_QUERY_URL, MODIFIER_QUERY,
        PRIMARY_SPECS, SHIP_QUERY_URL, STARSHIP_TRAIT_QUERY_URL, TRAIT_QUERY_URL, WIKI_IMAGE_URL)
from .iofunc import (
        get_cargo_data, fetch_html, get_asset_path, load_image, load_json, retrieve_image,
        store_json)
from .textedit import dewikify, sanitize_equipment_name
from .widgets import CustomThread


def init_backend(self, after):
    """
    Loads cargo and build data.
    """
    def check_exit(result):
        if cargo_thread.isFinished() and build_ready:
            insert_cargo_data(self)
            load_build(self)
            exit_splash(self)
            after()

    enter_splash(self)
    build_ready = False
    cargo_thread = CustomThread(self.window, populate_cache, self)
    cargo_thread.update_splash.connect(lambda new_text: splash_text(self, new_text))
    cargo_thread.result.connect(check_exit)
    cargo_thread.start()

    build_ready = False
    load_build_file(self, self.config['autosave_filename'])
    build_ready = True
    check_exit(None)


def insert_cargo_data(self):
    """
    Updates UI elements depending on cargo data with the loaded data
    """
    self.widgets.ship['combo'].addItems(self.cache.ships.keys())


def load_build(self):
    """
    Updates UI to show the build currently in self.build
    """
    # Character section
    self.widgets.character['name'].setText(self.build['captain']['name'])
    elite = Qt.CheckState.Checked if self.build['captain']['elite'] else Qt.CheckState.Unchecked
    self.widgets.character['elite'].setCheckState(elite)
    self.widgets.character['career'].setCurrentText(self.build['captain']['career'])
    species = self.build['captain']['species']
    self.widgets.character['faction'].setCurrentText(self.build['captain']['faction'])
    self.widgets.character['species'].setCurrentText(species)
    self.build['captain']['species'] = species
    self.widgets.character['primary'].setCurrentText(self.build['captain']['primary_spec'])
    self.widgets.character['secondary'].setCurrentText(self.build['captain']['secondary_spec'])


def load_build_file(self, filepath: str):
    """
    Loads build from json or png file and puts it into self.build

    Parameters:
    - :param filepath: path to build file
    """
    *_, extension = filepath.rpartition('.')
    if extension.lower() == 'json':
        self.build = load_json(filepath)
    else:
        raise NotImplementedError()


def populate_cache(self, thread: CustomThread):
    """
    Loads cargo data and images into cache
    """
    load_cargo_data(self, thread)
    self.cache.empty_image = load_image(get_asset_path('Common_icon.png', self.app_dir))
    self.cache.overlays.common = self.cache.empty_image
    self.cache.overlays.uncommon = load_image(get_asset_path('Uncommon_icon.png', self.app_dir))
    self.cache.overlays.rare = load_image(get_asset_path('Rare_icon.png', self.app_dir))
    self.cache.overlays.veryrare = load_image(get_asset_path('Very_rare_icon.png', self.app_dir))
    self.cache.overlays.ultrarare = load_image(get_asset_path('Ultra_rare_icon.png', self.app_dir))
    self.cache.overlays.epic = load_image(get_asset_path('Epic_icon.png', self.app_dir))
    load_images(self, thread)
    thread.result.emit(tuple())


def load_cargo_data(self, thread: CustomThread):
    """
    Loads cargo data for all cargo tables and puts them into variables.
    """
    thread.update_splash.emit('Loading: Starships')
    ship_cargo_data = get_cargo_data(self, 'ship_list.json', SHIP_QUERY_URL)
    self.cache.ships = {ship['Page']: ship for ship in ship_cargo_data}

    thread.update_splash.emit('Loading: Equipment')
    equipment_cargo_data = get_cargo_data(self, 'equipment.json', ITEM_QUERY_URL)
    equipment_types = set(EQUIPMENT_TYPES.keys())
    for item in equipment_cargo_data:
        if item['type'] in equipment_types and not (
                item['name'].startswith('Hangar - Advanced')
                or item['name'].startswith('Hangar - Elite')):
            item['name'] = sanitize_equipment_name(item['name'])
            self.cache.equipment[EQUIPMENT_TYPES[item['type']]][item['name']] = item

    thread.update_splash.emit('Loading: Traits')
    trait_cargo_data = get_cargo_data(self, 'traits.json', TRAIT_QUERY_URL)
    for trait in trait_cargo_data:
        if trait['chartype'] == 'char' and trait['name'] is not None:
            if trait['type'] == 'reputation':
                trait_type = 'rep'
            elif trait['type'] == 'activereputation':
                trait_type = 'active_rep'
            else:
                trait_type = 'personal'
            try:
                self.cache.traits[trait['environment']][trait_type][trait['name']] = trait
            except KeyError:
                pass

    thread.update_splash.emit('Loading: Starship Traits')
    shiptrait_cargo_data = get_cargo_data(self, 'starship_traits.json', STARSHIP_TRAIT_QUERY_URL)
    self.cache.starship_traits = {ship_trait['name'] for ship_trait in shiptrait_cargo_data}

    thread.update_splash.emit('Loading: Bridge Officers')
    get_boff_data(self)

    thread.update_splash.emit('Loading: Skills')
    cache_skills(self)

    thread.update_splash.emit('Loading: Modifiers')
    mod_cargo_data = get_cargo_data(self, 'modifiers.json', MODIFIER_QUERY)
    for modifier in mod_cargo_data:
        try:
            if modifier['available'][0] == '':
                modifier['available'] = list()
        except (IndexError, TypeError):
            modifier['available'] = list()
        for mod_type in modifier['type']:
            try:
                mod_key = EQUIPMENT_TYPES[mod_type]
                self.cache.modifiers[mod_key][modifier['modifier']] = modifier
            except KeyError:
                pass

    thread.update_splash.emit('Loading: Duty Officers')
    doff_cargo_data = get_cargo_data(self, 'doffs.json', DOFF_QUERY_URL)
    for doff in doff_cargo_data:
        doff['description'] = dewikify(doff['description'], remove_formatting=True)
        for rarity in ('white', 'green', 'blue', 'purple', 'violet', 'gold'):
            if isinstance(doff[rarity], str):
                doff[rarity] = dewikify(doff[rarity], remove_formatting=True)
        if doff['shipdutytype'] == 'Space':
            cache_doff_single(self, self.cache.space_doffs, doff)
        elif doff['shipdutytype'] == 'Ground':
            cache_doff_single(self, self.cache.ground_doffs, doff)
        elif doff['shipdutytype'] is not None:
            cache_doff_single(self, self.cache.space_doffs, doff)
            cache_doff_single(self, self.cache.ground_doffs, doff)


def load_images(self, thread: CustomThread):
    """
    Loads all images and puts them into cache.
    """
    img_folder = self.config['config_subfolders']['images']

    thread.update_splash.emit('Loading: Images (Starship Traits)')
    for trait in self.cache.starship_traits:
        self.cache.images[trait] = retrieve_image(self, trait, img_folder, thread.update_splash)

    thread.update_splash.emit('Loading: Images (Personal Traits)')
    for environment in self.cache.traits.values():
        for trait_type in environment.values():
            for trait in trait_type:
                self.cache.images[trait] = retrieve_image(
                        self, trait, img_folder, thread.update_splash)

    thread.update_splash.emit('Loading: Images (Equipment)')
    for equip_type in self.cache.equipment.values():
        for item in equip_type:
            self.cache.images[item] = retrieve_image(self, item, img_folder, thread.update_splash)

    thread.update_splash.emit('Loading: Images (Skills)')
    for rank_group in self.cache.skills['space'].values():
        for skill_group in rank_group:
            for skill_node in skill_group['nodes']:
                self.cache.images[skill_node['image']] = retrieve_image(
                    self, skill_node['image'], img_folder, thread.update_splash,
                    f'{WIKI_IMAGE_URL}{skill_node['image']}.png')
    self.cache.images['arrow-up'] = load_image(
            get_asset_path('arrow-up.png', self.app_dir))
    self.cache.images['arrow-down'] = load_image(
            get_asset_path('arrow-down.png', self.app_dir))
    self.cache.images['Focused Frenzy'] = retrieve_image(
            self, 'Focused Frenzy', img_folder)
    self.cache.images['Probability Manipulation'] = retrieve_image(
            self, 'Probability Manipulation', img_folder)
    self.cache.images['EPS Corruption'] = retrieve_image(
            self, 'EPS Corruption', img_folder)

    thread.update_splash.emit('Loading: Images (Bridge Officer Abilities)')
    for environment in self.cache.boff_abilities.values():
        for profession in environment.values():
            # all ranks have the same image; ranks Ensign and Commander contain all abilties once
            for rank in (0, 3):
                for ability in profession[rank]:
                    image_url = f'{WIKI_IMAGE_URL}{ability.replace(' ', '_')}_icon_(Federation).png'
                    self.cache.images[ability] = retrieve_image(
                        self, ability, img_folder, thread.update_splash, image_url)


def cache_doff_single(self, cache: dict, doff: dict):
    """
    Puts a single doff into cache.

    Parameters:
    - :param cache: cache dictionary to store doff into
    - :param doff: the doff itself
    """
    try:
        cache[doff['spec']][doff['description']] = doff
    except KeyError:
        cache[doff['spec']] = dict()
        cache[doff['spec']][doff['description']] = doff


def cache_skills(self):
    """
    Loads skills into cache.
    """
    space_skill_data = load_json(get_asset_path('space_skills.json', self.app_dir))
    self.cache.skills['space'] = space_skill_data['space']
    self.cache.skills['space_unlocks'] = space_skill_data['space_unlocks']
    ground_skill_data = load_json(get_asset_path('ground_skills.json', self.app_dir))
    self.cache.skills['ground'] = ground_skill_data['ground']
    self.cache.skills['ground_unlocks'] = ground_skill_data['ground_unlocks']


def empty_build(self, build_type: str = 'full') -> dict:
    """
    Creates empty build and returns it.

    Parameters:
    - :param build_type: `build` -> space and ground build; `skills` -> space and ground skills;
        `full` -> space and ground build and skills
    """
    # None means not available on the build; empty string means empty slot
    new_build = {
        'space': {
            'active_rep_traits': [None] * 5,
            'aft_weapons': [None] * 5,
            'boffs': [[None] * 4] * 6,
            'boff_specs': [None] * 6,
            'core': [''],
            'deflector': [''],
            'devices': [None] * 6,
            'doffs': [''] * 6,
            'eng_consoles': [None] * 5,
            'engines': [''],
            'experimental': [None],
            'fore_weapons': [None] * 5,
            'hangars': [None] * 2,
            'rep_traits': [None] * 5,
            'sci_consoles': [None] * 5,
            'sec_def': [None],
            'shield': [''],
            'ship': '',
            'ship_name': '',
            'starship_traits': [None] * 7,
            'tac_consoles': [None] * 5,
            'tier': '',
            'traits': [None] * 12,
            'uni_consoles': [None] * 3,
        },

        'ground': {
            'active_rep_traits': [None] * 5,
            'armor': '',
            'boffs': [[''] * 4] * 4,
            'boff_careers': [''] * 4,
            'boff_specs': [''] * 4,
            'devices': [None] * 5,
            'ev_suit': '',
            'kit': '',
            'kit_modules': [None] * 6,
            'rep_traits': [None] * 5,
            'personal_shield': '',
            'traits': [None] * 12,
            'weapons': [''] * 2,
        },

        'captain': {
            'career': '',
            'elite': False,
            'faction': '',
            'name': '',
            'primary_spec': '',
            'secondary_spec': '',
            'species': '',
        }
    }

    new_skills = {
        'space_skills': dict(),
        'ground_skills': dict()
    }

    if build_type == 'build':
        return new_build
    elif build_type == 'full':
        new_build.update(new_skills)
        return new_build
    elif build_type == 'skills':
        return new_skills


def autosave(self):
    """
    Saves build to autosave file.
    """
    store_json(self.build, self.config['autosave_filename'])


def get_boff_data(self):
    """
    Populates self.cache.boff_abilities until boff abilties are available from cargo
    """
    filename = 'boff_abilities.json'
    filepath = f"{self.config['config_subfolders']['cache']}\\{filename}"

    # try loading from cache
    if os.path.exists(filepath) and os.path.isfile(filepath):
        last_modified = os.path.getmtime(filepath)
        if (datetime.now() - datetime.fromtimestamp(last_modified)).days < 7:
            try:
                self.cache.boff_abilities = load_json(filepath)
                return
            except JSONDecodeError:
                backup_filepath = f"{self.config['config_subfolders']['backups']}\\{filename}"
                if os.path.exists(backup_filepath) and os.path.isfile(backup_filepath):
                    try:
                        cargo_data = load_json(backup_filepath)
                        store_json(cargo_data, filepath)
                        self.cache.boff_abilities = cargo_data
                        return
                    except JSONDecodeError:
                        pass

    # download if not exists
    try:
        boff_html = fetch_html(BOFF_URL)
    except Timeout:
        sys.stderr.write(f'[Error] Html could not be retrieved ({filename})\n')
        sys.exit(1)

    boffCategories = CAREERS | PRIMARY_SPECS
    for environment in ('space', 'ground'):
        l0 = [h2 for h2 in boff_html.find('h2') if ' Abilities' in h2.html]
        if environment == 'ground':
            l0 = [line for line in l0 if "Pilot" not in line.text]
            l1 = boff_html.find('h2+h3+table+h3+table')
        else:
            l1 = boff_html.find('h2+h3+table')

        for category in boffCategories:
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#'
                     + category.replace(' ', '_') + '_Abilities', first=True), Element)]
            if not len(table):
                continue
            trs = table[0].find('tr')
            for tr in trs:
                tds = tr.find('td')
                rank1 = 1
                for i in [0, 1, 2, 3]:
                    if len(tds) > 0 and tds[rank1 + i].text.strip() != '':
                        cname = tds[0].text.strip()
                        desc = tds[5].text.strip()
                        if desc == 'III':
                            desc = tds[6].text.strip()
                        self.cache.boff_abilities[environment][category][i][cname] = desc
                        if i == 2 and tds[rank1 + i].text.strip() in ['I', 'II']:
                            self.cache.boff_abilities[environment][category][i + 1][cname] \
                                = desc
    store_json(self.cache.boff_abilities, filepath)
