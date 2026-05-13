from pathlib import Path
from time import time

from .config import SETSSettings
from .constants import (
    CAREERS, BOFF_RANKS, DOFF_QUERY_URL, EQUIPMENT_TYPES, ITEM_QUERY_URL, MODIFIER_QUERY,
    PRIMARY_SPECS, SEVEN_DAYS_IN_SECONDS, SHIP_QUERY_URL, STARSHIP_TRAIT_QUERY_URL, TRAIT_QUERY_URL,
    TRAYSKILL_QUERY)
from .downloader import Downloader
from .iofunc import load_json__new, store_json__new
from .textedit import (
    create_equipment_tooltip__new, create_trait_tooltip__new, dewikify, parse_wikitext,
    sanitize_equipment_name)
from .theme import AppTheme


class CargoManager():
    """Manages Cargo data and cache"""

    def __init__(
            self, folders: dict[str, Path], app_dir: Path, downloader: Downloader,
            settings: SETSSettings, theme: AppTheme):
        """
        Parameters:
        - :param folders: folder names and paths of config folder
        """
        self._folders: dict[str, Path] = folders
        self._app_dir: Path = app_dir
        self._downloader: Downloader = downloader
        self._settings: SETSSettings = settings
        self._theme: AppTheme = theme
        self.ships: dict[str, dict[str]] = dict()
        self.equipment: dict[str, dict[str, dict[str]]] = {
            equipment_type: dict() for equipment_type in EQUIPMENT_TYPES.values()}
        self.modifiers: dict[str, dict[str, dict[str, str | bool]]] = {
            type_: dict() for type_ in EQUIPMENT_TYPES.values()}
        self.starship_traits: dict[str, dict[str]] = dict()
        self.space_traits: dict[str, dict[str, dict[str]]] = {
            'traits': dict(),
            'rep_traits': dict(),
            'active_rep_traits': dict()
        }
        self.ground_traits: dict[str, dict[str, dict[str]]] = {
            'traits': dict(),
            'rep_traits': dict(),
            'active_rep_traits': dict()
        }
        self.ground_doffs: dict[str, dict[str, dict[str]]] = dict()
        self.space_doffs: dict[str, dict[str, dict[str]]] = dict()
        self.boff_abilities: dict[str, dict[str, list[list[str]] | dict[str, str]]] = {
            'space': self.boff_dict(),
            'ground': self.boff_dict(),
            'all': dict()
        }
        self.item_aliases: dict = dict()
        self.skills = {
            'space': dict(),
            'space_unlocks': dict(),
            'ground': dict(),
            'ground_unlocks': dict()
        }
        self.image_set: set[str] = set()
        self.alt_images: dict[str, str] = dict()
        self.failed_images: dict[str, int] = dict()

    def load_static_data(self):
        """
        Loads skill data and item aliases.
        """
        local_folder = self._app_dir / 'local'
        self.item_aliases = load_json__new(local_folder / 'aliases.json')
        space_skill_data = load_json__new(local_folder / 'space_skills.json')
        self.skills['space'] = space_skill_data['space']
        self.skills['space_unlocks'] = space_skill_data['space_unlocks']
        ground_skill_data = load_json__new(local_folder / 'ground_skills.json')
        self.skills['ground'] = ground_skill_data['ground']
        self.skills['ground_unlocks'] = ground_skill_data['ground_unlocks']

    def provision_cargo_data(self):
        """
        (Down-) loads cargo data or gets cached cargo data.
        """
        images_updated = False
        force_image_update = False
        all_images = self.get_cached_data('images_list.json')
        if all_images is None:
            image_set = set()
            force_image_update = True
        else:
            image_set = set(all_images)
        alt_images = self.get_cached_data('alt_images.json')
        if alt_images is None:
            alt_images = set()
            force_image_update = True
        self.ships = self.get_cached_data('ships.json')
        if self.ships is None:
            self.cache_ship_data()
        equipment_data = self.get_cached_data('equipment.json')
        if equipment_data is None or force_image_update:
            self.cache_equipment_data()
            images_updated = True
        else:
            self.equipment = equipment_data
        space_trait_data = self.get_cached_data('space_traits.json')
        ground_trait_data = self.get_cached_data('ground_traits.json')
        if space_trait_data is None or ground_trait_data is None or force_image_update:
            self.cache_trait_data()
            images_updated = True
        else:
            self.space_traits = space_trait_data
            self.ground_traits = ground_trait_data
        starship_trait_data = self.get_cached_data('starship_traits.json')
        if starship_trait_data is None or force_image_update:
            self.cache_starship_trait_data()
            images_updated = True
        else:
            self.starship_traits = starship_trait_data
        boff_data = self.get_cached_data('boff_abilities.json')
        if boff_data is None or force_image_update:
            self.cache_boff_data()
            images_updated = True
        else:
            self.boff_abilities = boff_data
        modifier_data = self.get_cached_data('modifiers.json')
        if modifier_data is None:
            self.cache_modifier_data()
        else:
            self.modifiers = modifier_data
        space_doff_data = self.get_cached_data('space_doffs.json')
        ground_doff_data = self.get_cached_data('ground_doffs.json')
        if space_doff_data is None or ground_doff_data is None:
            self.cache_duty_officer_data()
        else:
            self.space_doffs = space_doff_data
            self.ground_doffs = ground_doff_data
        if images_updated:
            alt_images.update(self.alt_images)
            store_json__new(alt_images, self._folders['cache'] / 'alt_images.json')
            image_set |= self.image_set
            store_json__new(list(image_set), self._folders['cache'] / 'images_list.json')
        self.alt_images = alt_images
        self.image_set = image_set
        self.failed_images = self.get_cached_data('images_failed.json')
        if self.failed_images is None:
            self.failed_images = dict()

    def get_cached_data(self, file_name: str) -> dict | list | None:
        """
        Retrieves cached cargo data. Returns `None` when cache is too old or corrupted.

        Parameters:
        - :param file_name: name of the cache file to load
        """
        file_path = self._folders['cache'] / file_name
        if file_path.is_file():
            last_modified = file_path.stat().st_mtime
            if time() - last_modified < SEVEN_DAYS_IN_SECONDS:
                return load_json__new(file_path)
        return None

    def store_failed_images(self):
        """
        Stores failed images to cache folder
        """
        store_json__new(self.failed_images, self._folders['cache'] / 'images_failed.json')

    def cache_ship_data(self):
        """
        Retrieves ship data and caches it.
        """
        ship_cargo_data: list[dict[str]] = self.get_cargo_data('ship_list.json', SHIP_QUERY_URL)
        self.ships = {ship['Page']: ship for ship in ship_cargo_data}
        store_json__new(self.ships, self._folders['cache'] / 'ships.json')

    def cache_equipment_data(self):
        """
        Retrieves equipment data and caches it.
        """
        equipment_cargo_data: list[dict[str, str | None]] = self.get_cargo_data(
            'equipment.json', ITEM_QUERY_URL)
        equipment_types = set(EQUIPMENT_TYPES.keys())
        tooltip_styles = self._theme.tooltips
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
                self.equipment[EQUIPMENT_TYPES[item['type']]][name] = {
                    'Page': item['Page'],
                    'name': name,
                    'rarity': item['rarity'],
                    'type': item['type'],
                    'tooltip': create_equipment_tooltip__new(item, tooltip_styles)
                }
                self.image_set.add(name)
        self.equipment['fore_weapons'].update(self.equipment['ship_weapon'])
        self.equipment['aft_weapons'].update(self.equipment['ship_weapon'])
        del self.equipment['ship_weapon']
        self.equipment['tac_consoles'].update(self.equipment['uni_consoles'])
        self.equipment['sci_consoles'].update(self.equipment['uni_consoles'])
        self.equipment['eng_consoles'].update(self.equipment['uni_consoles'])
        self.equipment['uni_consoles'].update(self.equipment['tac_consoles'])
        self.equipment['uni_consoles'].update(self.equipment['sci_consoles'])
        self.equipment['uni_consoles'].update(self.equipment['eng_consoles'])
        store_json__new(self.equipment, self._folders['cache'] / 'equipment.json')

    def cache_trait_data(self):
        """
        Retrieves personal and reputation trait data and caches it.
        """
        trait_cargo_data: list[dict[str]] = self.get_cargo_data('traits.json', TRAIT_QUERY_URL)
        tooltip_styles = self._theme.tooltips
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
                    trait_data = {
                        'Page': trait['Page'],
                        'name': name,
                        'tooltip': create_trait_tooltip__new(
                            name, trait['description'], trait_type, trait['environment'],
                            tooltip_styles)
                    }
                    if trait['environment'] == 'space':
                        self.space_traits[trait_type][name] = trait_data
                    else:
                        self.ground_traits[trait_type][name] = trait_data
                    if trait['icon_name'] is None:
                        self.image_set.add(name)
                    else:
                        self.image_set.add(trait['icon_name'])
                        self.alt_images[f'{name}__{trait["environment"]}__{trait_type}'] = (
                            trait['icon_name'])
                # catch wrong values in trait['environment'] (cargo issue)
                except (KeyError, AttributeError):
                    pass
        store_json__new(self.space_traits, self._folders['cache'] / 'space_traits.json')
        store_json__new(self.ground_traits, self._folders['cache'] / 'ground_traits.json')

    def cache_starship_trait_data(self):
        """
        Retrieves starship trait data and caches it.
        """
        shiptrait_cargo = self.get_cargo_data('starship_traits.json', STARSHIP_TRAIT_QUERY_URL)
        styles = self._theme.tooltips
        for ship_trait in shiptrait_cargo:
            name = ship_trait['name']
            if ship_trait['icon_name'] is None:
                self.image_set.add(name)
            else:
                self.image_set.add(ship_trait['icon_name'])
                self.alt_images[f"{name}__space__starship_traits"] = ship_trait['icon_name']
            self.starship_traits[name] = {
                'Page': ship_trait['Page'],
                'name': name,
                'obtained': ship_trait['obtained'],
                'tooltip': (
                    f"<p style='{styles.trait_header}'>{name}</p>"
                    f"<p style='{styles.trait_subheader}'>Starship Trait</p><p style='margin:0'>"
                    f"{ship_trait['short']}</p>{parse_wikitext(ship_trait['detailed'], styles)}")
            }
        store_json__new(self.starship_traits, self._folders['cache'] / 'starship_traits.json')

    def cache_boff_data(self):
        """
        Retrieves bridge officer data and caches it.
        """
        boff_cargo: list[dict[str, str]] = self.get_cargo_data(
            'boff_abilities.json', TRAYSKILL_QUERY)
        boff_types = CAREERS | PRIMARY_SPECS
        styles = self._theme.tooltips
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
                    self.boff_abilities[boff_region][boff_type][rank_id].append(
                        boff_name + ' ' + roman)
                    ability_item[roman] = (
                        f"<p style='{styles.boff_header}'>{boff_name} {roman}</p>"
                        f"<p style={styles.boff_subheader}>{desc}</p><p>{desc_long}</p>"
                        f"{parse_wikitext(dewikify(boff_ability[f'rank{decimal}info']), styles)}")
            self.boff_abilities['all'][boff_name] = ability_item
        self.image_set |= self.boff_abilities['all'].keys()
        store_json__new(self.boff_abilities, self._folders['cache'] / 'boff_abilities.json')

    def cache_modifier_data(self):
        """
        Retrieves modifier data and caches it.
        """
        mod_cargo_data: list[dict[str, str | list[str] | int | None]] = self.get_cargo_data(
            'modifiers.json', MODIFIER_QUERY)
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
                    self.modifiers[EQUIPMENT_TYPES[mod_type]][mod_name] = {
                        'stats': modifier['stats'],
                        'available': modifier['available'],
                        'epic': epic,
                        'isunique': False if epic else bool(modifier['isunique']),
                    }
                except KeyError:
                    pass
        self.modifiers['fore_weapons'].update(self.modifiers['ship_weapon'])
        self.modifiers['aft_weapons'].update(self.modifiers['ship_weapon'])
        del self.modifiers['ship_weapon']
        self.modifiers['uni_consoles'].update(self.modifiers['sci_consoles'])
        self.modifiers['uni_consoles'].update(self.modifiers['eng_consoles'])
        self.modifiers['uni_consoles'].update(self.modifiers['tac_consoles'])
        store_json__new(self.modifiers, self._folders['cache'] / 'modifiers.json')

    def cache_duty_officer_data(self):
        """
        Retrieves duty officer data and caches it.
        """
        doff_cargo_data = self.get_cargo_data('doffs.json', DOFF_QUERY_URL)
        for doff in doff_cargo_data:
            doff['description'] = dewikify(doff['description'], remove_formatting=True)
            for rarity in ('white', 'green', 'blue', 'purple', 'violet', 'gold'):
                if isinstance(doff[rarity], str):
                    doff[rarity] = dewikify(doff[rarity], remove_formatting=True)
            if doff['shipdutytype'] == 'Space':
                self.cache_doff_single(self.space_doffs, doff)
            elif doff['shipdutytype'] == 'Ground':
                self.cache_doff_single(self.ground_doffs, doff)
            elif doff['shipdutytype'] is not None:
                self.cache_doff_single(self.space_doffs, doff)
                self.cache_doff_single(self.ground_doffs, doff)
        store_json__new(self.space_doffs, self._folders['cache'] / 'space_doffs.json')
        store_json__new(self.ground_doffs, self._folders['cache'] / 'ground_doffs.json')

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

    def get_cargo_data(
            self, filename: str, url: str, ignore_cache_age: bool = False) -> dict | list:
        """
        Retrieves cargo data for specific table. Downloads cargo data from wiki if cargo cache is
        empty. Updates cargo cache.

        Parameters:
        - :param filename: filename of cache file
        - :param url: url to cargo table
        - :param ignore_cache_age: True if cache of any age should be accepted
        """
        cargo_file = self._folders['cargo'] / filename

        # try loading from cache
        if cargo_file.is_file():
            last_modified = cargo_file.stat().st_mtime
            if time() - last_modified < SEVEN_DAYS_IN_SECONDS or ignore_cache_age:
                cargo_data = load_json__new(cargo_file)
                if cargo_data is not None:
                    return cargo_data

        # download cargo data if loading from cache failed or data should be updated
        cargo_data = self._downloader.download_cargo_table(url, filename)
        if cargo_data is None:
            if ignore_cache_age:
                backup_path = self._folders['backups'] / filename
                auto_backup_path = self._folders['auto_backups'] / filename
                if self._settings.pref_backup == 0:
                    backup_paths = (auto_backup_path, backup_path)
                else:
                    backup_paths = (backup_path, auto_backup_path)
                for path in backup_paths:
                    if path.is_file():
                        cargo_data = load_json__new(path)
                        if cargo_data is not None:
                            store_json__new(cargo_data, cargo_file)
                            return cargo_data
                # TODO what happens when both backups fail?
            else:
                return self.get_cargo_data(filename, url, ignore_cache_age=True)
        else:
            if cargo_file.is_file():
                cargo_file.copy_into(self._folders['auto_backups'])
            store_json__new(cargo_data, cargo_file)
            return cargo_data

    def backup_cargo_data(self):
        """
        Saves current cargo data to backup folder.
        """
        cargo_files = (
            'boff_abilities.json', 'doffs.json', 'equipment.json', 'modifiers.json',
            'ship_list.json', 'starship_traits.json', 'traits.json')
        cargo_folder = self._folders['cargo']
        backups_folder = self._folders['backups']
        for file_name in cargo_files:
            (cargo_folder / file_name).copy_into(backups_folder)

    def boff_dict(self):
        return {
            'Tactical': [list(), list(), list(), list()],
            'Engineering': [list(), list(), list(), list()],
            'Science': [list(), list(), list(), list()],
            'Intelligence': [list(), list(), list(), list()],
            'Command': [list(), list(), list(), list()],
            'Pilot': [list(), list(), list(), list()],
            'Temporal': [list(), list(), list(), list()],
            'Miracle Worker': [list(), list(), list(), list()],
        }
