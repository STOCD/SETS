from datetime import datetime
from json import JSONDecodeError
import os
import sys

from PySide6.QtGui import QPixmap
from requests.exceptions import Timeout
from requests_html import Element

from .buildupdater import load_build, get_boff_spec
from .constants import (
        BOFF_URL, BUILD_CONVERSION, CAREERS, DOFF_QUERY_URL, EQUIPMENT_TYPES, ITEM_QUERY_URL,
        MODIFIER_QUERY, PRIMARY_SPECS, SHIP_QUERY_URL, STARSHIP_TRAIT_QUERY_URL, TRAIT_QUERY_URL,
        WIKI_IMAGE_URL)
from .iofunc import (
        get_cargo_data, fetch_html, get_asset_path, load_image, load_json,
        retrieve_image, store_json)
from .splash import enter_splash, exit_splash, splash_text
from .textedit import dewikify, sanitize_equipment_name
from .widgets import CustomThread


def init_backend(self):
    """
    Loads cargo and build data.
    """
    def check_exit(result):
        if cargo_thread.isFinished() and build_ready:
            splash_text(self, 'Injecting Cargo Data')
            insert_cargo_data(self)
            splash_text(self, 'Loading Build')
            load_build(self)
            exit_splash(self)

    enter_splash(self)
    build_ready = False
    cargo_thread = CustomThread(self.window, populate_cache, self)
    cargo_thread.update_splash.connect(lambda new_text: splash_text(self, new_text))
    cargo_thread.result.connect(check_exit)
    cargo_thread.start()

    build_ready = False
    load_build_file(self, self.config['autosave_filename'], update_ui=False)
    build_ready = True
    check_exit(None)


def insert_cargo_data(self):
    """
    Updates UI elements depending on cargo data with the loaded data
    """
    self.ship_selector_window.set_ships(self.cache.ships.keys())


def populate_cache(self, thread: CustomThread):
    """
    Loads cargo data and images into cache
    """
    load_cargo_data(self, thread)
    self.cache.empty_image = QPixmap()
    self.cache.overlays.common = load_image(get_asset_path('Common_icon.png', self.app_dir))
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
    self.cache.equipment['fore_weapons'].update(self.cache.equipment['ship_weapon'])
    self.cache.equipment['aft_weapons'].update(self.cache.equipment['ship_weapon'])
    del self.cache.equipment['ship_weapon']
    self.cache.equipment['tac_consoles'].update(self.cache.equipment['uni_consoles'])
    self.cache.equipment['sci_consoles'].update(self.cache.equipment['uni_consoles'])
    self.cache.equipment['eng_consoles'].update(self.cache.equipment['uni_consoles'])
    self.cache.equipment['uni_consoles'].update(self.cache.equipment['tac_consoles'])
    self.cache.equipment['uni_consoles'].update(self.cache.equipment['sci_consoles'])
    self.cache.equipment['uni_consoles'].update(self.cache.equipment['eng_consoles'])

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
    shiptrait_cargo = get_cargo_data(self, 'starship_traits.json', STARSHIP_TRAIT_QUERY_URL)
    self.cache.starship_traits = {ship_trait['name']: ship_trait for ship_trait in shiptrait_cargo}

    thread.update_splash.emit('Loading: Bridge Officers')
    get_boff_data(self)
    self.cache.all_boff_abilities = dict()
    for cat in self.cache.boff_abilities['space'].values():
        self.cache.all_boff_abilities.update(cat[2])
    for cat in self.cache.boff_abilities['ground'].values():
        self.cache.all_boff_abilities.update(cat[2])

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


def autosave(self):
    """
    Saves build to autosave file.
    """
    if not self.building:
        store_json(self.build, self.config['autosave_filename'])


def map_build_items(self, old_build: dict, new_build: dict, mapping):
    """
    Inserts items from old build into new build according to mapping; in-place

    Parameters:
    - :param old_build: source
    - :param new_build: target
    - :param mapping: iterable of 2-tuples containing source and target key
    """
    for source_key, target_key in mapping:
        try:
            if isinstance(new_build[target_key], list):
                for index, element in enumerate(old_build[source_key]):
                    new_build[target_key][index] = element
            else:
                new_build[target_key] = old_build[source_key]
        except KeyError:
            continue


def convert_old_build(self, build: dict) -> dict:
    """
    converts build from old spec to current spec
    """
    new_build = empty_build(self)

    # space
    map_build_items(self, build, new_build['space'], BUILD_CONVERSION['space'])
    new_build['space']['traits'] = (
            build['personalSpaceTrait'] + build['personalSpaceTrait2'] + [None])
    ship_data = self.cache.ships[new_build['space']['ship']]
    boff_data = sorted(map(lambda s: get_boff_spec(self, s), ship_data['boffs']), reverse=True)
    for boff_id in range(5):
        # taking profession from ship specifications
        if boff_data[boff_id][1] == 'Universal':
            new_profession = build['boffseats']['space'][boff_id]
        else:
            new_profession = boff_data[boff_id][1]
        # taking specialization from ship specifications
        new_specialization = boff_data[boff_id][2]
        new_build['space']['boff_specs'][boff_id] = [new_profession, new_specialization]
        for i, ability in enumerate(build['boffs'][f'spaceBoff_{boff_id}']):
            if ability is None or ability == '':
                new_build['space']['boffs'][boff_id][i]
            else:
                new_build['space']['boffs'][boff_id][i] = {'item': ability}

    # ground
    map_build_items(self, build, new_build['ground'], BUILD_CONVERSION['ground'])
    for boff_id in range(4):
        new_build['ground']['boff_profs'][boff_id] = build['boffseats']['ground'][boff_id]
        new_build['ground']['boff_specs'][boff_id] = build['boffseats']['ground_spec'][boff_id]
        for i, ability in enumerate(build['boffs'][f'groundBoff_{boff_id}']):
            if ability is None or ability == '':
                new_build['ground']['boffs'][boff_id][i]
            else:
                new_build['ground']['boffs'][boff_id][i] = {'item': ability}
    new_build['ground']['traits'] = (
            build['personalGroundTrait'] + build['personalGroundTrait2'] + [None])

    # captain
    map_build_items(self, build, new_build['captain'], BUILD_CONVERSION['captain'])
    new_build['captain']['name'] = build['playerName'] + build['playerHandle']
    new_build['captain']['faction'] = build['captain']['faction']

    # skills TODO
    return new_build


def load_build_file(self, filepath: str, update_ui: bool = True):
    """
    Loads build from json or png file and puts it into self.build

    Parameters:
    - :param filepath: path to build file
    """
    *_, extension = filepath.rpartition('.')
    if extension.lower() == 'json':
        build_data = load_json(filepath)
    else:
        raise NotImplementedError()
    if 'space' in build_data:
        self.build = build_data
    else:
        self.build = convert_old_build(self, build_data)
    if update_ui:
        load_build(self)


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
            'boffs': [[None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4],
            'boff_specs': [[None, None]] * 6,
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
            'ship_desc': '',
            'starship_traits': [None] * 7,
            'tac_consoles': [None] * 5,
            'tier': '',
            'traits': [None] * 12,
            'uni_consoles': [None] * 3,
        },

        'ground': {
            'active_rep_traits': [None] * 5,
            'armor': '',
            'boffs': [[''] * 4, [''] * 4, [''] * 4, [''] * 4],
            'boff_profs': [''] * 4,
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
                if len(tds) > 0:
                    a_name = tds[0].text.strip()
                    a_desc = tds[5].text.strip()
                    if a_desc == 'III':
                        a_desc = tds[6].text.strip()
                    self.boff_abilities['all'][a_name] = a_desc
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
