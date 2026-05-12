from datetime import datetime
from json import dumps as json__dumps, loads as json__loads, JSONDecodeError
import os
from pathlib import Path
import sys
from zlib import compress as zlib_compress, decompress as zlib_decompress
from numpy import array, append, fromiter, packbits, uint8, unpackbits, zeros
from PySide6.QtGui import QImage
from requests import Session
from requests.cookies import create_cookie
from requests.exceptions import (
        ConnectionError as requests__ConnectionError, Timeout as requests__Timeout)
from requests_html import Element
from urllib.parse import unquote_plus

from .buildupdater import get_boff_spec, load_build, load_skill_pages
from .constants import (
        BOFF_RANKS, BUILD_CONVERSION, BUILD_VERSION, CAREERS, DOFF_QUERY_URL, EQUIPMENT_TYPES,
        ITEM_QUERY_URL, MODIFIER_QUERY, PRIMARY_SPECS, SHIP_QUERY_URL,
        STARSHIP_TRAIT_QUERY_URL, TRAIT_QUERY_URL, TRAYSKILL_QUERY, WIKI_IMAGE_URL)
from .iofunc import (
        auto_backup_cargo_file, browse_path, cache_cargo_data, copy_file, download_image,
        download_images_fast, fetch_html, get_asset_path, get_cached_cargo_data, get_cargo_data,
        get_downloaded_icons, image, load_image, load_json, read_env_file, retrieve_image,
        store_json, store_to_cache)
from .splash import enter_splash, exit_splash, splash_text
from .textedit import (
        create_equipment_tooltip, create_trait_tooltip, dewikify, parse_wikitext,
        sanitize_equipment_name)
from .widgets import exec_in_thread, notempty, TagStyles, ThreadObject


def init_backend(self):
    """
    Loads cargo and build data.
    """
    def finish_backend_init():
        splash_text(self, 'Injecting Cargo Data')
        insert_cargo_data(self)
        slot_skill_images(self)
        splash_text(self, 'Loading Build')
        load_build(self)
        exec_in_thread(self, load_images, self)
        exit_splash(self)

    enter_splash(self)
    load_build_file(self, str(self.config.autosave_path), update_ui=False)
    self.downloader.default_session_from_env()
    exec_in_thread(
            self, populate_cache, self, finished=finish_backend_init,
            update_splash=lambda new_text: splash_text(self, new_text))


def insert_cargo_data(self):
    """
    Updates UI elements depending on cargo data with the loaded data
    """
    self.ship_selector_window.set_ships(self.cache.ships.keys())
    space_doff_specs = [''] + sorted(self.cache.space_doffs.keys())
    for combobox in self.widgets.build['space']['doffs_spec']:
        combobox.addItems(space_doff_specs)
    ground_doff_specs = [''] + sorted(self.cache.ground_doffs.keys())
    for combobox in self.widgets.build['ground']['doffs_spec']:
        combobox.addItems(ground_doff_specs)


def slot_skill_images(self):
    """
    Updates the ground and skill tree, slotting the correct images into the slots.
    """
    for career_block in self.widgets.build['space_skills'].values():
        for skill_button in career_block:
            skill_button.set_item(image(self, skill_button.skill_image_name))
    for skill_group in self.widgets.build['ground_skills']:
        for skill_button in skill_group:
            skill_button.set_item(image(self, skill_button.skill_image_name))


def populate_cache(self, threaded_worker: ThreadObject):
    """
    Loads cargo data and images into cache

    Parameters:
    - :param threaded_worker: worker object supplying signals
    """
    success = load_cargo_cache(self, threaded_worker)
    if not success:
        self.cache.reset_cache(keep_static_data=True)
        load_cargo_data(self, threaded_worker)
    self.cache.empty_image = QImage()
    self.cache.images_failed = get_cached_cargo_data(self, 'images_failed.json')

    # temporary: until self.cache has been replaced
    self.images.image_set = self.cache.images_set
    self.images.failed_images = self.cache.images_failed
    self.cargo.boff_abilities = self.cache.boff_abilities

    threaded_worker.update_splash.emit('Loading: Images')
    self.images.download_images(self.cache.skills)
    store_to_cache(self, self.images.failed_images, 'images_failed.json')
    load_base_images(self, threaded_worker)


def load_cargo_cache(self, threaded_worker: ThreadObject) -> bool:
    """
    Loads cargo data for all cargo tables from cached data and puts them into variables. Returns
    True when successful, False if cache is too old

    Parameters:
    - :param threaded_worker: worker object supplying signals
    """
    threaded_worker.update_splash.emit('Loading: Cargo Data')
    self.cache.ships = get_cached_cargo_data(self, 'ships.json')
    if len(self.cache.ships) == 0:
        return False
    self.cache.equipment = get_cached_cargo_data(self, 'equipment.json')
    if len(self.cache.equipment) == 0:
        return False
    self.cache.traits = get_cached_cargo_data(self, 'traits.json')
    if len(self.cache.traits) == 0:
        return False
    self.cache.starship_traits = get_cached_cargo_data(self, 'starship_traits.json')
    if len(self.cache.starship_traits) == 0:
        return False
    self.cache.boff_abilities = get_cached_cargo_data(self, 'boff_abilities.json')
    if len(self.cache.boff_abilities) == 0 or len(self.cache.boff_abilities.get('all', {})) == 0:
        return False
    self.cache.modifiers = get_cached_cargo_data(self, 'modifiers.json')
    if len(self.cache.modifiers) == 0:
        return False
    self.cache.space_doffs = get_cached_cargo_data(self, 'space_doffs.json')
    if len(self.cache.space_doffs) == 0:
        return False
    self.cache.ground_doffs = get_cached_cargo_data(self, 'ground_doffs.json')
    if len(self.cache.ground_doffs) == 0:
        return False
    self.cache.alt_images = get_cached_cargo_data(self, 'alt_images.json')
    if len(self.cache.alt_images) == 0:
        return False
    self.cache.images_set = set(get_cached_cargo_data(self, 'images_list.json'))
    if len(self.cache.images_set) == 0:
        return False
    return True


def load_cargo_data(self, threaded_worker: ThreadObject):
    """
    Loads cargo data for all cargo tables and puts them into variables.

    Parameters:
    - :param threaded_worker: worker object supplying signals
    """
    threaded_worker.update_splash.emit('Loading: Starships')
    ship_cargo_data = get_cargo_data(self, 'ship_list.json', SHIP_QUERY_URL)
    self.cache.ships = {ship['Page']: ship for ship in ship_cargo_data}
    store_to_cache(self, self.cache.ships, 'ships.json')

    tags = TagStyles(
            self.theme['tooltip']['ul'], self.theme['tooltip']['li'],
            self.theme['tooltip']['indent'])

    threaded_worker.update_splash.emit('Loading: Equipment')
    equipment_cargo_data = get_cargo_data(self, 'equipment.json', ITEM_QUERY_URL)
    equipment_types = set(EQUIPMENT_TYPES.keys())
    head_s = self.theme['tooltip']['equipment_head']
    subhead_s = self.theme['tooltip']['equipment_subhead']
    who_s = self.theme['tooltip']['equipment_who']
    elite_hangar = {
        'Hangar - Elite Federation Mission Scout Ships',
        'Hangar - Elite Valor Fighters'
    }
    for item in equipment_cargo_data:
        if item['type'] in equipment_types:
            if item['type'] == 'Hangar Bay' and item['name'] not in elite_hangar and (
                    item['name'].startswith('Hangar - Advanced')
                    or item['name'].startswith('Hangar - Elite')):
                continue
            name = sanitize_equipment_name(item['name'])
            self.cache.equipment[EQUIPMENT_TYPES[item['type']]][name] = {
                'Page': item['Page'],
                'name': name,
                'rarity': item['rarity'],
                'type': item['type'],
                'tooltip': create_equipment_tooltip(item, head_s, subhead_s, who_s, tags)
            }
            self.cache.images_set.add(name)
    self.cache.equipment['fore_weapons'].update(self.cache.equipment['ship_weapon'])
    self.cache.equipment['aft_weapons'].update(self.cache.equipment['ship_weapon'])
    del self.cache.equipment['ship_weapon']
    self.cache.equipment['tac_consoles'].update(self.cache.equipment['uni_consoles'])
    self.cache.equipment['sci_consoles'].update(self.cache.equipment['uni_consoles'])
    self.cache.equipment['eng_consoles'].update(self.cache.equipment['uni_consoles'])
    self.cache.equipment['uni_consoles'].update(self.cache.equipment['tac_consoles'])
    self.cache.equipment['uni_consoles'].update(self.cache.equipment['sci_consoles'])
    self.cache.equipment['uni_consoles'].update(self.cache.equipment['eng_consoles'])
    store_to_cache(self, self.cache.equipment, 'equipment.json')

    threaded_worker.update_splash.emit('Loading: Traits')
    trait_cargo_data = get_cargo_data(self, 'traits.json', TRAIT_QUERY_URL)
    head_s = self.theme['tooltip']['trait_header']
    subhead_s = self.theme['tooltip']['trait_subheader']
    for trait in trait_cargo_data:
        name = trait['name']
        if trait['type'] != 'doff' and trait['type'] != 'boff' and name is not None:
            if trait['type'] == 'reputation':
                trait_type = 'rep_traits'
            elif trait['type'] == 'activereputation':
                trait_type = 'active_rep_traits'
            else:
                trait_type = 'traits'
            try:
                self.cache.traits[trait['environment']][trait_type][name] = {
                    'Page': trait['Page'],
                    'name': name,
                    'tooltip': create_trait_tooltip(
                            name, trait['description'], trait_type, trait['environment'], head_s,
                            subhead_s, tags)
                }
                if trait['icon_name'] is None:
                    self.cache.images_set.add(name)
                else:
                    self.cache.images_set.add(trait['icon_name'])
                    self.cache.alt_images[f'{name}__{trait["environment"]}__{trait_type}'] = (
                            trait['icon_name'])
            # catch wrong values in trait['environment'] (cargo issue)
            except (KeyError, AttributeError):
                pass
    store_to_cache(self, self.cache.traits, 'traits.json')

    threaded_worker.update_splash.emit('Loading: Starship Traits')
    shiptrait_cargo = get_cargo_data(self, 'starship_traits.json', STARSHIP_TRAIT_QUERY_URL)
    for ship_trait in shiptrait_cargo:
        name = ship_trait['name']
        if ship_trait['icon_name'] is None:
            self.cache.images_set.add(name)
        else:
            self.cache.images_set.add(ship_trait['icon_name'])
            self.cache.alt_images[f"{name}__space__starship_traits"] = (
                    ship_trait['icon_name'])
        self.cache.starship_traits[name] = {
            'Page': ship_trait['Page'],
            'name': name,
            'obtained': ship_trait['obtained'],
            'tooltip': (
                    f"<p style='{head_s}'>{name}</p><p style='{subhead_s}'>"
                    f"Starship Trait</p><p style='margin:0'>"
                    f"{ship_trait['short']}</p>{parse_wikitext(ship_trait['detailed'], tags)}")
        }
    self.cache.images_set |= self.cache.starship_traits.keys()
    store_to_cache(self, self.cache.starship_traits, 'starship_traits.json')
    store_to_cache(self, self.cache.alt_images, 'alt_images.json')

    threaded_worker.update_splash.emit('Loading: Bridge Officers')
    boff_head = self.theme['tooltip']['boff_header']
    boff_subhead = self.theme['tooltip']['boff_subheader']
    boff_cargo = get_cargo_data(self, 'boff_abilities.json', TRAYSKILL_QUERY)
    boff_types = CAREERS | PRIMARY_SPECS
    rank_numbers = ((1, 'I'), (2, 'II'), (3, 'III'))
    for boff_ability in boff_cargo:
        boff_region = boff_ability['region'].lower()
        boff_type = boff_ability['type']
        if boff_type not in boff_types or boff_region != 'space' and boff_region != 'ground':
            continue
        boff_name = boff_ability['name']
        ability_item = {
            'Page': boff_ability['_pageName'],
            'name': boff_name,
            'I': '',
            'II': '',
            'III': ''
        }
        desc = boff_ability['description']
        desc_long = boff_ability['description long']
        for decimal, roman in rank_numbers:
            rank_id = BOFF_RANKS.get(boff_ability[f'rank{decimal}rank'], 0) - 1
            if rank_id >= 0:
                self.cache.boff_abilities[boff_region][boff_type][rank_id].append(
                    boff_name + ' ' + roman)
                ability_item[roman] = (
                    f"<p style='{boff_head}'>{boff_name} {roman}</p><p style={boff_subhead}>"
                    f"{desc}</p><p>{desc_long}</p>"
                    f"{parse_wikitext(dewikify(boff_ability[f'rank{decimal}info']), tags)}")
        self.cache.boff_abilities['all'][boff_name] = ability_item
    self.cache.images_set |= self.cache.boff_abilities['all'].keys()
    store_to_cache(self, self.cache.boff_abilities, 'boff_abilities.json')

    threaded_worker.update_splash.emit('Loading: Modifiers')
    mod_cargo_data = get_cargo_data(self, 'modifiers.json', MODIFIER_QUERY)
    for modifier in mod_cargo_data:
        try:
            if modifier['available'][0] == '':
                modifier['available'] = list()
        except (IndexError, TypeError):
            modifier['available'] = list()
        for mod_type in modifier['type']:
            mod_name = modifier['modifier'].replace('&gt;', '>')
            try:
                epic = bool(modifier['isepic'])
                self.cache.modifiers[EQUIPMENT_TYPES[mod_type]][mod_name] = {
                    'stats': modifier['stats'],
                    'available': modifier['available'],
                    'epic': epic,
                    'isunique': False if epic else bool(modifier['isunique']),
                }
            except KeyError:
                pass
    self.cache.modifiers['fore_weapons'].update(self.cache.modifiers['ship_weapon'])
    self.cache.modifiers['aft_weapons'].update(self.cache.modifiers['ship_weapon'])
    del self.cache.modifiers['ship_weapon']
    self.cache.modifiers['uni_consoles'].update(self.cache.modifiers['sci_consoles'])
    self.cache.modifiers['uni_consoles'].update(self.cache.modifiers['eng_consoles'])
    self.cache.modifiers['uni_consoles'].update(self.cache.modifiers['tac_consoles'])
    store_to_cache(self, self.cache.modifiers, 'modifiers.json')

    threaded_worker.update_splash.emit('Loading: Duty Officers')
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
    store_to_cache(self, self.cache.space_doffs, 'space_doffs.json')
    store_to_cache(self, self.cache.ground_doffs, 'ground_doffs.json')
    store_to_cache(self, list(self.cache.images_set), 'images_list.json')


def load_base_images(self, threaded_worker: ThreadObject):
    """
    Loads all images that are required for the app to start (skills, overlays)

    Parameters:
    - :param threaded_worker: worker object supplying signals
    """
    threaded_worker.update_splash.emit('Loading: Images (Overlays)')
    self.cache.images = {image_name: QImage() for image_name in self.cache.images_set}
    self.cache.overlays.common = QImage(get_asset_path('Common_icon.png', self.app_dir))
    self.cache.overlays.uncommon = QImage(get_asset_path('Uncommon_icon.png', self.app_dir))
    self.cache.overlays.rare = QImage(get_asset_path('Rare_icon.png', self.app_dir))
    self.cache.overlays.veryrare = QImage(get_asset_path('Very_rare_icon.png', self.app_dir))
    self.cache.overlays.ultrarare = QImage(get_asset_path('Ultra_rare_icon.png', self.app_dir))
    self.cache.overlays.epic = QImage(get_asset_path('Epic_icon.png', self.app_dir))
    self.cache.overlays.check = QImage(get_asset_path('check_overlay.png', self.app_dir))

    threaded_worker.update_splash.emit('Loading: Images (Skills)')
    img_folder = self.config.config_subfolders['images']
    for rank_group in self.cache.skills['space']:
        for skill_group in rank_group:
            for skill_node in skill_group['nodes']:
                self.cache.images[skill_node['image']] = retrieve_image(
                    self, skill_node['image'], img_folder, threaded_worker.update_splash,
                    f'{WIKI_IMAGE_URL}{skill_node['image']}.png')
    for skill_group in self.cache.skills['ground']:
        for skill_node in skill_group['nodes']:
            self.cache.images[skill_node['image']] = retrieve_image(
                    self, skill_node['image'], img_folder, threaded_worker.update_splash,
                    f'{WIKI_IMAGE_URL}{skill_node['image']}.png')
    self.cache.images['arrow-up'] = QImage(get_asset_path('arrow-up.png', self.app_dir))
    self.cache.images['arrow-down'] = QImage(get_asset_path('arrow-down.png', self.app_dir))
    self.cache.images['Focused Frenzy'] = retrieve_image(
            self, 'Focused Frenzy', img_folder)
    self.cache.images['Probability Manipulation'] = retrieve_image(
            self, 'Probability Manipulation', img_folder)
    self.cache.images['EPS Corruption'] = retrieve_image(
            self, 'EPS Corruption', img_folder)


def load_images(self, threaded_worker=None):
    """

    Parameters:
    - :param threaded_worker: (unused; required for compatability with employed threading method)
    """
    img_folder = self.config.config_subfolders['images']
    for img_name, img in self.cache.images.items():
        if img.isNull():
            load_image(img_name, img, img_folder)


def download_images(self, threaded_worker: ThreadObject):
    """
    Downloads all images not already in the images folder and puts them into cache. Returns set of
    images not to be retried in this cycle.
    """
    no_retry_images = set()
    now = datetime.now()
    for img, timestamp in self.cache.images_failed.items():
        if (datetime.fromtimestamp(timestamp) - now).days < 7:
            no_retry_images.add(img)
        else:
            self.cache.images_failed.pop(img)
    images = self.cache.images_set - no_retry_images - get_downloaded_icons(
        Path(self.config.config_subfolders['images']))
    img_folder = self.config.config_subfolders['images']

    images_to_download = images - self.cache.boff_abilities['all'].keys()
    for image_name in images_to_download:
        threaded_worker.update_splash.emit(f'Downloading Image: {image_name}')
        download_image(self, image_name, img_folder)

    boff_images_to_download = images & self.cache.boff_abilities['all'].keys()
    for image_name in boff_images_to_download:
        threaded_worker.update_splash.emit(f'Downloading Image: {image_name}')
        image_url = f'{WIKI_IMAGE_URL}{image_name.replace(' ', '_')}_icon_(Federation).png'
        download_image(self, image_name, img_folder, image_url)
    return no_retry_images


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


def cache_skills(skill_cache: dict[str, dict], app_directory: str):
    """
    Loads skills into cache.
    """
    space_skill_data = load_json(get_asset_path('space_skills.json', app_directory))
    skill_cache['space'] = space_skill_data['space']
    skill_cache['space_unlocks'] = space_skill_data['space_unlocks']
    ground_skill_data = load_json(get_asset_path('ground_skills.json', app_directory))
    skill_cache['ground'] = ground_skill_data['ground']
    skill_cache['ground_unlocks'] = ground_skill_data['ground_unlocks']


def empty_build(self, build_type: str = 'full') -> dict:
    """
    Creates empty build and returns it.

    Parameters:
    - :param build_type: `build` -> space and ground build; `skills` -> space and ground skills;
        `full` -> space and ground build and skills
    """
    # None means not available on the build; empty string means empty slot
    new_build = {
        '_version': BUILD_VERSION,
        'space': {
            'active_rep_traits': [None] * 5,
            'aft_weapons': [None] * 5,
            'boffs': [[None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4],
            'boff_specs': [[None, None]] * 6,
            'core': [''],
            'deflector': [''],
            'devices': [None] * 6,
            'doffs_spec': [''] * 6,
            'doffs_variant': [''] * 6,
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
            'traits': ['', '', '', '', '', '', '', '', '', None, None, ''],
            'uni_consoles': [None] * 3,
        },
        'ground': {
            'active_rep_traits': [None] * 5,
            'armor': [''],
            'boffs': [[''] * 4, [''] * 4, [''] * 4, [''] * 4],
            'boff_profs': ['Tactical'] * 4,
            'boff_specs': ['Command'] * 4,
            'ground_desc': '',
            'ground_devices': ['', '', '', '', None],
            'doffs_spec': [''] * 6,
            'doffs_variant': [''] * 6,
            'ev_suit': [''],
            'kit': [''],
            'kit_modules': ['', '', '', '', '', None],
            'rep_traits': [''] * 5,
            'personal_shield': [''],
            'traits': ['', '', '', '', '', '', '', '', '', None, None, ''],
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
        },
    }

    new_skills = {
        '_version': BUILD_VERSION,
        'space_skills': {
            'eng': [False] * 30,
            'sci': [False] * 30,
            'tac': [False] * 30,
        },
        'skill_unlocks': {
            'eng': [None] * 5,
            'sci': [None] * 5,
            'tac': [None] * 5,
            'ground': [None] * 5
        },
        'ground_skills': [
            [False] * 6,
            [False] * 6,
            [False] * 4,
            [False] * 4
        ],
        'skill_desc': {
            'space': '',
            'ground': ''
        }
    }

    if build_type == 'build':
        return new_build
    elif build_type == 'full':
        new_build.update(new_skills)
        return new_build
    elif build_type == 'skills':
        return new_skills


def backup_cargo_data(self):
    """
    Saves current cargo data to backup folder.
    """
    cargo_files = (
            'boff_abilities.json', 'doffs.json', 'equipment.json', 'modifiers.json',
            'ship_list.json', 'starship_traits.json', 'traits.json')
    cargo_folder = self.config.config_subfolders['cargo']
    backups_folder = self.config.config_subfolders['backups']
    for file_name in cargo_files:
        cargo_path = str(cargo_folder / file_name)
        backups_path = str(backups_folder / file_name)
        copy_file(cargo_path, backups_path)


def get_icon_set(cargo_dir: Path) -> set[str]:
    """
    Creates set of all required icons from cargo data and required static images.

    Parameters:
    - :param cargo_dir: path to cargo data directory
    """
    images_set = set()
    equipment_cargo_data = load_json(str(cargo_dir / 'equipment.json'))
    equipment_types = set(EQUIPMENT_TYPES.keys())
    elite_hangar = {
        'Hangar - Elite Federation Mission Scout Ships',
        'Hangar - Elite Valor Fighters'
    }
    for item in equipment_cargo_data:
        if item['type'] in equipment_types:
            if item['type'] == 'Hangar Bay' and item['name'] not in elite_hangar and (
                    item['name'].startswith('Hangar - Advanced')
                    or item['name'].startswith('Hangar - Elite')):
                continue
            images_set.add(sanitize_equipment_name(item['name']))
    trait_cargo_data = load_json(str(cargo_dir / 'traits.json'))
    for trait in trait_cargo_data:
        if trait['type'] != 'doff' and trait['type'] != 'boff' and trait['name'] is not None:
            if trait['icon_name'] is None:
                images_set.add(trait['name'])
            else:
                images_set.add(trait['icon_name'])
    shiptrait_cargo_data = load_json(str(cargo_dir / 'starship_traits.json'))
    for ship_trait in shiptrait_cargo_data:
        if ship_trait['icon_name'] is None:
            images_set.add(ship_trait['name'])
        else:
            images_set.add(ship_trait['icon_name'])
    return images_set


def get_skill_icons(skill_cache: dict[str, dict]) -> set[str]:
    """
    """
    icons = set()
    for rank_group in skill_cache['space']:
        for skill_group in rank_group:
            for skill_node in skill_group['nodes']:
                icons.add(skill_node['image'])
    for skill_group in skill_cache['ground']:
        for skill_node in skill_group['nodes']:
            icons.add(skill_node['image'])
    return icons


def get_boff_icons(boff_cache: dict[str, dict]) -> set[str]:
    """
    """
    return set(boff_cache['all'].keys())


def get_ship_icons(ship_list: list[dict[str]]) -> set[str]:
    """
    """
    icon_set = set()
    for ship in ship_list:
        try:
            icon_set.add(ship['image'][5:])
        except TypeError:
            pass
    return icon_set


def build_cache(app_dir: Path) -> int:
    """
    Builds cache in config folder indicated by `config_path`. Returns status: success: `0`,
    failure: `1`

    Parameters:
    - :param config_path: path to build cache into
    """
    config_path = app_dir / '.config'
    env_variables = read_env_file(config_path / '.env', ['SETS_CF_CLEARANCE', 'SETS_USER_AGENT'])
    requests_session = Session()
    if 'SETS_CF_CLEARANCE' in env_variables:
        print(f'[Info] "SETS_CF_CLEARANCE" variable: "{env_variables["SETS_CF_CLEARANCE"][:10]}"')
        print(f'[Info] "SETS_CF_CLEARANCE" variable: "{env_variables["SETS_CF_CLEARANCE"][-10:]}"')
        requests_session.cookies.set_cookie(
            create_cookie(name='cf_clearance', value=env_variables['SETS_CF_CLEARANCE']))
    if 'SETS_USER_AGENT' in env_variables:
        print(f'[Info] "SETS_USER_AGENT" variable: "{env_variables["SETS_USER_AGENT"][:10]}"')
        print(f'[Info] "SETS_USER_AGENT" variable: "{env_variables["SETS_USER_AGENT"][-10:]}"')
        requests_session.headers['User-Agent'] = env_variables['SETS_USER_AGENT']
    cargo_dir = config_path / 'cargo'
    success = list()
    success.append(cache_cargo_data(cargo_dir / 'ship_list.json', SHIP_QUERY_URL, requests_session))
    success.append(cache_cargo_data(cargo_dir / 'equipment.json', ITEM_QUERY_URL, requests_session))
    success.append(cache_cargo_data(cargo_dir / 'traits.json', TRAIT_QUERY_URL, requests_session))
    success.append(cache_cargo_data(
        cargo_dir / 'starship_traits.json', STARSHIP_TRAIT_QUERY_URL, requests_session))
    success.append(cache_cargo_data(cargo_dir / 'modifiers.json', MODIFIER_QUERY, requests_session))
    success.append(cache_cargo_data(cargo_dir / 'doffs.json', DOFF_QUERY_URL, requests_session))

    image_dir = config_path / 'images'
    downloaded_images = get_downloaded_icons(image_dir)
    ultimate_icons = {'Focused Frenzy', 'Probability Manipulation', 'EPS Corruption'}
    images_set = (get_icon_set(cargo_dir) | ultimate_icons) - downloaded_images
    if len(images_set) > 0:
        download_images_fast(list(images_set), env_variables, image_dir)
    skill_cache = dict()
    cache_skills(skill_cache, app_dir)
    skill_images = get_skill_icons(skill_cache) - downloaded_images
    if len(skill_images) > 0:
        download_images_fast(list(skill_images), env_variables, image_dir, image_suffix='.png')
    boff_cache = load_json(cargo_dir / 'boff_abilities.json')
    boff_images = get_boff_icons(boff_cache) - downloaded_images
    if len(boff_images) > 0:
        download_images_fast(
            list(boff_images), env_variables, image_dir, image_suffix='_icon_(Federation).png')

    downloaded_ship_images = set(
        map(lambda x: unquote_plus(x), os.listdir(str(config_path / 'ship_images'))))
    ship_list = load_json(str(cargo_dir / 'ship_list.json'))
    ship_images = get_ship_icons(ship_list) - downloaded_ship_images
    if len(ship_images) > 0:
        download_images_fast(
            list(ship_images), env_variables, config_path / 'ship_images', image_suffix='')

    if False in success:
        return 1
    return 0
