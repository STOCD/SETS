from datetime import datetime
from json import dumps as json_dumps, loads as json_loads, JSONDecodeError
import os
import sys
from zlib import compress as zlib_compress, decompress as zlib_decompress
from numpy import array, append, fromiter, packbits, uint8, unpackbits, zeros
from PySide6.QtGui import QImage
from requests.exceptions import Timeout
from requests_html import Element

from .buildupdater import get_boff_spec, load_build
from .constants import (
        BOFF_URL, BUILD_CONVERSION, CAREERS, DOFF_QUERY_URL, EQUIPMENT_TYPES, ITEM_QUERY_URL,
        MODIFIER_QUERY, PRIMARY_SPECS, SHIP_QUERY_URL, STARSHIP_TRAIT_QUERY_URL, TRAIT_QUERY_URL,
        WIKI_IMAGE_URL)
from .iofunc import (
        download_image, fetch_html, get_asset_path, get_cached_cargo_data, get_cargo_data,
        get_downloaded_images, load_image, load_json, retrieve_image, store_json, store_to_cache)
from .splash import enter_splash, exit_splash, splash_text
from .textedit import dewikify, sanitize_equipment_name
from .widgets import exec_in_thread, ThreadObject


def init_backend(self):
    """
    Loads cargo and build data.
    """
    def finish_backend_init():
        splash_text(self, 'Injecting Cargo Data')
        insert_cargo_data(self)
        splash_text(self, 'Loading Build')
        load_build(self)
        exec_in_thread(self, load_images, self)
        exit_splash(self)

    enter_splash(self)
    load_build_file(self, self.config['autosave_filename'], update_ui=False)
    exec_in_thread(
            self, populate_cache, self, finished=finish_backend_init,
            update_splash=lambda new_text: splash_text(self, new_text))


def insert_cargo_data(self):
    """
    Updates UI elements depending on cargo data with the loaded data
    """
    self.ship_selector_window.set_ships(self.cache.ships.keys())


def populate_cache(self, threaded_worker: ThreadObject):
    """
    Loads cargo data and images into cache

    Parameters:
    - :param threaded_worker: worker object supplying signals
    """
    success = load_cargo_cache(self, threaded_worker)
    if not success:
        self.cache.reset_cache()
        load_cargo_data(self, threaded_worker)
    self.cache.empty_image = QImage()
    self.cache.images_failed = get_cached_cargo_data(self, 'images_failed.json')
    download_images(self, threaded_worker)
    store_to_cache(self, self.cache.images_failed, 'images_failed.json')
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
    if len(self.cache.boff_abilities) == 0:
        return False
    self.cache.skills = get_cached_cargo_data(self, 'skills.json')
    if len(self.cache.skills) == 0:
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

    threaded_worker.update_splash.emit('Loading: Equipment')
    equipment_cargo_data = get_cargo_data(self, 'equipment.json', ITEM_QUERY_URL)
    equipment_types = set(EQUIPMENT_TYPES.keys())
    for item in equipment_cargo_data:
        if item['type'] in equipment_types and not (
                item['name'].startswith('Hangar - Advanced')
                or item['name'].startswith('Hangar - Elite')):
            item['name'] = sanitize_equipment_name(item['name'])
            self.cache.equipment[EQUIPMENT_TYPES[item['type']]][item['name']] = item
            self.cache.images_set.add(item['name'])
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
                self.cache.images_set.add(trait['name'])
            except KeyError:
                pass
    store_to_cache(self, self.cache.traits, 'traits.json')

    threaded_worker.update_splash.emit('Loading: Starship Traits')
    shiptrait_cargo = get_cargo_data(self, 'starship_traits.json', STARSHIP_TRAIT_QUERY_URL)
    self.cache.starship_traits = {ship_trait['name']: ship_trait for ship_trait in shiptrait_cargo}
    self.cache.images_set |= self.cache.starship_traits.keys()
    store_to_cache(self, self.cache.starship_traits, 'starship_traits.json')

    threaded_worker.update_splash.emit('Loading: Bridge Officers')
    get_boff_data(self)
    store_to_cache(self, self.cache.boff_abilities, 'boff_abilities.json')

    threaded_worker.update_splash.emit('Loading: Skills')
    cache_skills(self)
    store_to_cache(self, self.cache.skills, 'skills.json')

    threaded_worker.update_splash.emit('Loading: Modifiers')
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

    threaded_worker.update_splash.emit('Loading: Images (Skills)')
    img_folder = self.config['config_subfolders']['images']
    for rank_group in self.cache.skills['space'].values():
        for skill_group in rank_group:
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
    img_folder = self.config['config_subfolders']['images']
    for img_name, img in self.cache.images.items():
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
    images = self.cache.images_set - no_retry_images - get_downloaded_images(self)
    img_folder = self.config['config_subfolders']['images']

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
    new_build['space']['traits'] = build['personalSpaceTrait'] + build['personalSpaceTrait2']
    if len(new_build['space']['traits']) < 12:
        new_build['space']['traits'] += [None] * (12 - len(new_build['space']['traits']))
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
    new_build['ground']['traits'] = build['personalGroundTrait'] + build['personalGroundTrait2']
    if len(new_build['ground']['traits']) < 12:
        new_build['ground']['traits'] += [None] * (12 - len(new_build['ground']['traits']))

    # captain
    map_build_items(self, build, new_build['captain'], BUILD_CONVERSION['captain'])
    new_build['captain']['name'] = build['playerName'] + build['playerHandle']
    new_build['captain']['faction'] = build['captain']['faction']

    # skills TODO
    return new_build


def encode_in_image(self, image: QImage, data: str):
    """
    Embeds data into image

    Parameters:
    - :param image: image to edit
    - :param data: data string to embed into image
    """
    data_bytes = zlib_compress(bytes(data, encoding='utf-8'))
    total_characters = len(data_bytes)
    bits = zeros(total_characters * 8 + 32 + 8, dtype=uint8)
    prefix = array([167, total_characters >> 8, total_characters & 0b11111111, 167], dtype=uint8)
    bits[0:32] = unpackbits(prefix)
    bits[32:-8] = unpackbits(fromiter(data_bytes, dtype=uint8, count=total_characters))
    bits[-8:] = unpackbits(array([167], dtype=uint8))
    total_characters += 5  # prefix and suffix length
    w = image.width()
    total_bits = total_characters * 8
    full_rows = total_bits // (w * 3)
    additional_pixels = (total_bits - full_rows * w * 3) // 3
    additional_subpixels = total_bits % 3
    i = -1
    for row in range(full_rows):
        row_data = image.scanLine(row)
        for i, subpixel in pixel_range(w, i + 1):
            row_data[subpixel] = row_data[subpixel] & 0b11111110 | bits[i]
    row_data = image.scanLine(row + 1)
    for i, subpixel in pixel_range(additional_pixels, i + 1):
        row_data[subpixel] = row_data[subpixel] & 0b11111110 | bits[i]
    if additional_pixels == 0:
        subpixel = -2
    if additional_subpixels == 1:
        row_data[subpixel + 2] = row_data[subpixel + 2] & 0b11111110 | bits[i + 1]
    elif additional_subpixels == 2:
        row_data[subpixel + 2] = row_data[subpixel + 2] & 0b11111110 | bits[i + 1]
        row_data[subpixel + 3] = row_data[subpixel + 3] & 0b11111110 | bits[i + 2]


def decode_from_image(self, image: QImage) -> str:
    """
    Extracts embedded data from image; returns empty string if no data was found

    Parameters:
    - :param image: image with embedded data
    """
    # prefix: §15000§ where 15000 is the number (as uint16) of bytes the encoded data occupies
    prefix_bits = zeros(32, dtype=uint8)
    first_row = image.constScanLine(0)
    for i, subpixel in pixel_range(10):
        prefix_bits[i] = first_row[subpixel] & 0b1
    prefix_bits[30] = first_row[40] & 0b1
    prefix_bits[31] = first_row[41] & 0b1
    prefix_bytes = packbits(prefix_bits)
    if prefix_bytes[0] != 167 or prefix_bytes[3] != 167:  # ord('§') == 167
        return ''
    total_characters = int(prefix_bytes[1]) << 8 | int(prefix_bytes[2])  # constructs 16-bit int
    total_characters += 5  # prefix and suffix length
    w = image.width()
    total_bits = total_characters * 8
    bits = zeros(total_bits, dtype=uint8)
    full_rows = total_bits // (w * 3)
    additional_pixels = (total_bits - full_rows * w * 3) // 3
    additional_subpixels = total_bits % 3
    i = -1
    for row in range(full_rows):
        row_data = image.constScanLine(row)
        for i, subpixel in pixel_range(w, i + 1):
            bits[i] = row_data[subpixel] & 0b1
    row_data = image.constScanLine(row + 1)
    for i, subpixel in pixel_range(additional_pixels, i + 1):
        bits[i] = row_data[subpixel] & 0b1
    if additional_pixels == 0:
        subpixel = -2
    if additional_subpixels == 1:
        bits[i + 1] = row_data[subpixel + 2] & 0b1
    elif additional_subpixels == 2:
        bits[i + 1] = row_data[subpixel + 2] & 0b1
        bits[i + 2] = row_data[subpixel + 3] & 0b1
    decoded_bytes = bytes(packbits(bits))
    if decoded_bytes[-1] != 167:
        raise ValueError('End delimiter not found! Decoded data not intact.')
    return str(zlib_decompress(decoded_bytes[4:-1]), 'utf-8')


def legacy_decode_from_image(self, image_path: str) -> str:
    """
    Decodes build from image using old embedding specification.

    Parameters:
    - :param image_path: path to image
    """
    message = ''
    image = QImage(image_path)
    width = image.width()
    pixel_num = width * 3
    bit_diff = pixel_num % 8
    decoded_binary = zeros(pixel_num, dtype=uint8)
    extra_bits = zeros(0, dtype=uint8)
    for line in range(image.height()):
        data = image.constScanLine(line)
        for col in range(width):
            pixel_index = col * 4
            bin_index = col * 3
            decoded_binary[bin_index] = data[pixel_index + 2] & 0b1
            decoded_binary[bin_index + 1] = data[pixel_index + 1] & 0b1
            decoded_binary[bin_index + 2] = data[pixel_index] & 0b1
        if bit_diff == 0:
            decoded_bytes = packbits(append(extra_bits, decoded_binary))
        else:
            decoded_bytes = packbits(append(extra_bits, decoded_binary[:-1 * bit_diff]))
            bit_diff = (pixel_num + len(extra_bits)) % 8
            bit_diff = (pixel_num + bit_diff) % 8
        new_message = ''.join(map(chr, decoded_bytes))
        message += new_message
        if '$t3g0' in new_message:
            break
    return message.split('$t3g0', maxsplit=1)[0]


def load_build_file(self, filepath: str, update_ui: bool = True):
    """
    Loads build from json or png file and puts it into self.build

    Parameters:
    - :param filepath: path to build file
    """
    _, _, extension = filepath.rpartition('.')
    if extension.lower() == 'json':
        build_data = load_json(filepath)
    elif extension.lower() == 'png':
        decoded_str = decode_from_image(self, QImage(filepath))
        if decoded_str == '':
            print('NO DATA FOUND!')
            return
        build_data = json_loads(decoded_str)
    else:
        return
    if 'space' in build_data:
        self.build = build_data
    else:
        self.build = convert_old_build(self, build_data)
    if update_ui:
        load_build(self)


def save_build_file(self, filepath: str):
    """
    Saves build to json or png file

    Parameters:
    - :param filepath: path to build file
    """
    _, _, extension = filepath.rpartition('.')
    if extension.lower() == 'json':
        store_json(self.build, filepath)
    elif extension.lower() == 'png':
        image = self.window.grab().toImage()
        encode_in_image(self, image, json_dumps(self.build))
        image.save(filepath)


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


def pixel_range(num: int = 0, range_start: int = 0, /):
    """
    Returns appropriate indices to access the RGB (not A) channels of the pixel row of `num` pixels,
    as well as an 1-step increasing range index -> (range_index, pixel_index)
    """
    counter = range_start
    for index in range(0, num * 4, 4):
        yield counter, index
        counter += 1
        yield counter, index + 1
        counter += 1
        yield counter, index + 2
        counter += 1


def get_boff_data(self):
    """
    Populates self.cache.boff_abilities until boff abilties are available from cargo
    """
    filename = 'boff_abilities.json'
    filepath = f"{self.config['config_subfolders']['cargo']}\\{filename}"

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
                    self.cache.boff_abilities['all'][a_name] = a_desc
                    self.cache.images_set.add(a_name)
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
