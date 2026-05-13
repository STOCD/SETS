from json import dumps as json__dumps, JSONDecodeError, loads as json__loads
from numpy import (
    array as np__array, append as np__append, fromiter as np__fromiter, packbits as np__packbits,
    uint8, unpackbits as np__unpackbits, zeros as np__zeros)
from pathlib import Path
from zlib import compress as zlib_compress, decompress as zlib_decompress

from PySide6.QtGui import QImage
from PySide6.QtWidgets import QWidget

from .buildhelpers import empty_build, get_boff_spec
from .buildmanager import BuildManager
from .cargomanager import CargoManager
from .config import SETSConfig, SETSSettings
from .constants import BUILD_CONVERSION, BUILD_VERSION, SETS_FILE_FILTER
from .iofunc import browse_path, load_json__new, store_json__new
from .widgets import bundle, pixel_range


class BuildLoader():
    """Loads/saves build files from/to disk."""

    def __init__(
            self, build: BuildManager, cargo: CargoManager, config: SETSConfig,
            settings: SETSSettings, window: QWidget):
        self._build: BuildManager = build
        self._cargo: CargoManager = cargo
        self._config: SETSConfig = config
        self._settings: SETSSettings = settings
        self._window: QWidget = window
        self._current_build_path: Path | None = None

    def load_build_callback(self):
        """
        Loads build from file
        """
        load_path = browse_path(
            self.get_library_path(), SETS_FILE_FILTER, parent_window=self._window)
        if load_path is not None:
            self.load_build_file(load_path)
            self._current_build_path = load_path

    def save_build_callback(self):
        """
        Saves build to file it was opened from, overwriting that file.
        """
        if self._current_build_path is None:
            self.save_build_as_callback()
        else:
            self.save_build_file(self._current_build_path)

    def save_build_as_callback(self):
        """
        Saves build to file
        """
        if self._build.ship.button.text() == '<Pick Ship>':
            proposed_filename = '(Ship Template)'
        else:
            proposed_filename = f"({self._build['space']['ship']})"
        if self._build['space']['ship_name'] != '':
            proposed_filename = f"{self._build['space']['ship_name']} {proposed_filename}"
        preset_path = self.get_library_path() / proposed_filename
        if self._settings.default_save_format == 'PNG':
            file_types = 'PNG image (*.png);;JSON file (*.json);;Any File (*.*)'
        else:
            file_types = 'JSON file (*.json);;PNG image (*.png);;Any File (*.*)'
        save_path = browse_path(preset_path, file_types, save=True, parent_window=self._window)
        if save_path is not None:
            self.save_build_file(save_path)
            self._current_build_path = save_path

    def load_skills_callback(self):
        """
        Loads skills from file
        """
        load_path = browse_path(
            self.get_library_path(), SETS_FILE_FILTER, parent_window=self._window)
        if load_path is not None:
            self.load_skill_tree_file(load_path)

    def save_skills_callback(self):
        """
        Save skills to file
        """
        preset_path = self.get_library_path() / 'Skill Tree'
        if self._settings.default_save_format == 'PNG':
            file_types = 'PNG image (*.png);;JSON file (*.json);;Any File (*.*)'
        else:
            file_types = 'JSON file (*.json);;PNG image (*.png);;Any File (*.*)'
        save_path = browse_path(preset_path, file_types, save=True, parent_window=self._window)
        if save_path is not None:
            self.save_skill_tree_file(save_path)

    def load_build_file(self, filepath: Path, update_ui: bool = True):
        """
        Loads build from json or png file and puts it into self.build

        Parameters:
        - :param filepath: path to build file
        """
        extension = filepath.suffix.lower()
        if extension == '.json':
            build_data = load_json__new(filepath)
        elif extension == '.png':
            decoded_str = self.decode_from_image(self, QImage(filepath))
            if decoded_str == '':
                return
            build_data = json__loads(decoded_str)
        else:
            return
        new_build = empty_build()
        if build_data.get('_version', -1) == BUILD_VERSION:
            self.merge_build(new_build, build_data)
        elif 'versionJSON' in build_data:
            build_data = json__loads(self.compensate_old_build(json__dumps(build_data)))
            new_build.update(self.convert_old_build(build_data))
        else:
            self.merge_build(new_build, build_data)
            self.update_build_version(new_build)
        self._build.data = new_build
        if update_ui:
            try:
                self._build.load_build()
            except KeyError:
                self.remove_invalid_build_items(self._build.data)
                self._build.load_build()

    def save_build_file(self, filepath: Path):
        """
        Saves build to json or png file

        Parameters:
        - :param filepath: path to build file
        """
        extension = filepath.suffix.lower()
        if extension == '.json':
            store_json__new(self._build.data, filepath)
        elif extension == '.png':
            image = self._window.grab().toImage()
            self.encode_in_image(image, json__dumps(self._build.data))
            image.save(filepath)

    def load_skill_tree_file(self, filepath: Path):
        """
        Loads skill tree from json or png file and puts it into self.build

        Parameters:
        - :param filepath: path to skill tree file
        """
        extension = filepath.suffix.lower()
        if extension == '.json':
            build_data = load_json__new(filepath)
        elif extension == '.png':
            decoded_str = self.decode_from_image(self, QImage(filepath))
            if decoded_str == '':
                return
            build_data = json__loads(decoded_str)
        else:
            return
        new_build = empty_build('skills')
        self.merge_build(new_build, build_data)
        self._build.data['space_skills'] = new_build['space_skills']
        self._build.data['ground_skills'] = new_build['ground_skills']
        self._build.data['skill_unlocks'] = new_build['skill_unlocks']
        self._build.data['skill_desc'] = new_build['skill_desc']
        self._build.load_skill_pages()

    def save_skill_tree_file(self, filepath: Path):
        """
        Saves skill tree to json or png file

        Parameters:
        - :param filepath: path to skill tree file
        """
        extension = filepath.suffix.lower()
        skill_tree = {
            'space_skills': self._build['space_skills'],
            'ground_skills': self._build['ground_skills'],
            'skill_unlocks': self._build['skill_unlocks'],
            'skill_desc': self._build['skill_desc'],
        }
        if extension == '.json':
            store_json__new(skill_tree, filepath)
        elif extension == '.png':
            image = self._window.grab().toImage()
            self.encode_in_image(image, json__dumps(skill_tree))
            image.save(filepath)

    def get_library_path(self) -> Path:
        """
        Returns current library path.
        """
        if self._settings.library_path != '':
            path = Path(self._settings.library_path)
            if path.is_dir():
                return path
        return self._config.config_subfolders['library']

    def merge_build(self, original_build: dict[str, dict[str]], new_build: dict[str, dict[str]]):
        """
        updates `original_build` with contents of `new_build`
        """
        for build_segment in original_build:
            subdict = new_build.get(build_segment, None)
            if subdict is None:
                continue
            if isinstance(subdict, dict):
                original_build[build_segment].update(subdict)
            else:
                original_build[build_segment] = subdict

    def update_build_version(self, build: dict[str]):
        """
        Updates contents of `build` to match the newest version.

        Parameters:
        - :param build: contains build data of outdated version
        """
        def _fix_boff_seat(environment):
            for rank_id in range(4):
                if isinstance(boff_seat[rank_id], dict) and 'rank' not in boff_seat[rank_id]:
                    ability_name = boff_seat[rank_id]['item']
                    prof_abilities = self._cargo.boff_abilities[environment][prof]
                    spec_abilities = self._cargo.boff_abilities[environment].get(spec, None)
                    for rank in ('III', 'II', 'I'):
                        if f'{ability_name} {rank}' in prof_abilities[rank_id]:
                            boff_seat[rank_id]['rank'] = rank
                            break
                        elif (spec_abilities is not None
                                and f'{ability_name} {rank}' in spec_abilities[rank_id]):
                            boff_seat[rank_id]['rank'] = rank
                            break
                    else:
                        boff_seat[rank_id] = ''

        for boff_seat, (prof, spec) in zip(build['space']['boffs'], build['space']['boff_specs']):
            _fix_boff_seat('space')
        for station_id, boff_seat in enumerate(build['ground']['boffs']):
            prof = build['ground']['boff_profs'][station_id]
            spec = build['ground']['boff_specs'][station_id]
            _fix_boff_seat('ground')

        alt_images_inverted = {image: key for key, image in self._cargo.alt_images.items()}
        alt_image_items = bundle(
            build['space']['traits'], build['ground']['traits'], build['ground']['rep_traits'])
        for trait in alt_image_items:
            if isinstance(trait, dict) and trait['item'] in alt_images_inverted:
                trait['item'] = alt_images_inverted[trait['item']].split('__', 1)[0]

        build['_version'] = BUILD_VERSION

    def remove_invalid_build_items(self, build: dict[str, int | dict[str]]):
        """
        Checks build for invalid items and removes these to maintain compatibility.

        Parameters:
        - :param build: build to remove items from (in place)
        """
        for environment in ('space', 'ground'):
            for category, category_items in build[environment].items():
                if isinstance(category_items, str):
                    continue
                elif category == 'boffs':
                    for station in category_items:
                        for index, ability in enumerate(station):
                            if (isinstance(ability, dict)
                                    and ability['item'] not in self._cargo.image_set):
                                station[index] = ''
                elif (category.startswith('doff')
                        or category == 'boff_specs'
                        or category == 'boff_profs'):
                    continue
                elif isinstance(category_items, list):
                    for index, item in enumerate(category_items):
                        if isinstance(item, dict) and item['item'] not in self._cargo.image_set:
                            category_items[index] = ''

    def encode_in_image(self, image: QImage, data: str):
        """
        Embeds data into image

        Parameters:
        - :param image: image to edit
        - :param data: data string to embed into image
        """
        data_bytes = zlib_compress(bytes(data, encoding='utf-8'))
        total_characters = len(data_bytes)
        bits = np__zeros(total_characters * 8 + 32 + 8, dtype=uint8)
        prefix = np__array(
            [167, total_characters >> 8, total_characters & 0b11111111, 167], dtype=uint8)
        bits[0:32] = np__unpackbits(prefix)
        bits[32:-8] = np__unpackbits(np__fromiter(data_bytes, dtype=uint8, count=total_characters))
        bits[-8:] = np__unpackbits(np__array([167], dtype=uint8))
        total_characters += 5  # prefix and suffix length
        w = image.width()
        total_bits = total_characters * 8
        full_rows = total_bits // (w * 3)
        additional_pixels = (total_bits - full_rows * w * 3) // 3
        additional_subpixels = total_bits % 3
        i = -1
        row = -1
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
        prefix_bits = np__zeros(32, dtype=uint8)
        first_row = image.constScanLine(0)
        for i, subpixel in pixel_range(10):
            prefix_bits[i] = first_row[subpixel] & 0b1
        prefix_bits[30] = first_row[40] & 0b1
        prefix_bits[31] = first_row[41] & 0b1
        prefix_bytes = np__packbits(prefix_bits)
        if prefix_bytes[0] != 167 or prefix_bytes[3] != 167:  # ord('§') == 167
            return ''
        total_characters = int(prefix_bytes[1]) << 8 | int(prefix_bytes[2])  # constructs 16-bit int
        total_characters += 5  # prefix and suffix length
        w = image.width()
        total_bits = total_characters * 8
        bits = np__zeros(total_bits, dtype=uint8)
        full_rows = total_bits // (w * 3)
        additional_pixels = (total_bits - full_rows * w * 3) // 3
        additional_subpixels = total_bits % 3
        i = -1
        row = -1
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
        decoded_bytes = bytes(np__packbits(bits))
        if decoded_bytes[-1] != 167:
            return ''
        return str(zlib_decompress(decoded_bytes[4:-1]), 'utf-8')

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
                        try:
                            if isinstance(element, dict) and 'modifiers' in element:
                                element['modifiers'] += [None] * (5 - len(element['modifiers']))
                            new_build[target_key][index] = element
                        except IndexError:
                            break
                else:
                    new_build[target_key] = old_build[source_key]
            except KeyError:
                continue

    def load_legacy_build_image(self):
        """
        Loads legacy build from image file
        """
        load_path = browse_path(
            self.get_library_path(),
            'PNG image (*.png);;Any File (*.*)', parent_window=self._window)
        if load_path is not None:
            if load_path.suffix.lower() != '.png':
                return
            raw_build = self.legacy_decode_from_image(load_path)
            try:
                build_data = json__loads(self.compensate_old_build(raw_build))
            except JSONDecodeError:
                return
            if 'versionJSON' in build_data:
                new_build = empty_build()
                new_build.update(self.convert_old_build(build_data))
                self._build.data = new_build
                try:
                    self._build.load_build()
                except KeyError:
                    self.remove_invalid_build_items(self._build.data)
                    self._build.load_build()

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
        decoded_binary = np__zeros(pixel_num, dtype=uint8)
        extra_bits = np__zeros(0, dtype=uint8)
        for line in range(image.height()):
            data = image.constScanLine(line)
            for col in range(width):
                pixel_index = col * 4
                bin_index = col * 3
                decoded_binary[bin_index] = data[pixel_index + 2] & 0b1
                decoded_binary[bin_index + 1] = data[pixel_index + 1] & 0b1
                decoded_binary[bin_index + 2] = data[pixel_index] & 0b1
            if bit_diff == 0:
                decoded_bytes = np__packbits(np__append(extra_bits, decoded_binary))
                extra_bits = np__zeros(0, dtype=uint8)
                bit_diff = pixel_num % 8
            else:
                decoded_bytes = np__packbits(np__append(extra_bits, decoded_binary[:-1 * bit_diff]))
                extra_bits = decoded_binary[-1 * bit_diff:].copy()
                bit_diff = (pixel_num + len(extra_bits)) % 8
            new_message = ''.join(map(chr, decoded_bytes))
            message += new_message
            if '$t3g0' in new_message:
                break
        return message.split('$t3g0', maxsplit=1)[0]

    def compensate_old_build(self, build: str):
        """
        replaces known wrong terms in build string
        """
        build = build.replace('Ultra rare', 'Ultra Rare')
        build = build.replace('Very rare', 'Very Rare')
        return build

    def convert_old_build(self, build: dict) -> dict:
        """
        converts build from old spec to current spec
        """
        new_build = empty_build(self)

        # space
        self.map_build_items(build, new_build['space'], BUILD_CONVERSION['space'])

        new_build['space']['traits'] = build['personalSpaceTrait'] + build['personalSpaceTrait2']
        if len(new_build['space']['traits']) < 12:
            new_build['space']['traits'] += [None] * (12 - len(new_build['space']['traits']))
        elite_captain_trait = new_build['space']['traits'][5]
        new_build['space']['traits'][5] = new_build['space']['traits'][9]
        new_build['space']['traits'][9] = elite_captain_trait

        ship_data = self._cargo.ships[new_build['space']['ship']]
        boff_data = sorted(map(lambda s: get_boff_spec(s), ship_data['boffs']), reverse=True)
        boff_data_old = []
        for boff_id, boff_profession in enumerate(build['boffseats']['space']):
            if f'spaceBoff_{boff_id}' in build['boffs'] and boff_profession is not None:
                abilities = build['boffs'][f'spaceBoff_{boff_id}']
                boff_data_old.append((len(abilities), boff_profession, abilities))
        boff_data_old.sort(reverse=True)
        for boff_id, (new_station, old_station) in enumerate(zip(boff_data, boff_data_old)):
            if new_station[1] == old_station[1] or new_station[1] == 'Universal':
                continue
            for i, test_station in enumerate(boff_data):
                if old_station[0] == test_station[0] and old_station[1] == test_station[1]:
                    boff_data_old[boff_id] = boff_data_old[i]
                    boff_data_old[i] = old_station
                    break
            else:
                for i, test_station in enumerate(boff_data):
                    if old_station[0] == test_station[0] and test_station[1] == 'Universal':
                        boff_data_old[boff_id] = boff_data_old[i]
                        boff_data_old[i] = old_station
                        break
        for boff_id, station in enumerate(boff_data_old):
            new_build['space']['boff_specs'][boff_id] = [station[1], boff_data[boff_id][2]]
            for i, ability in enumerate(station[2]):
                if ability is None or ability == '':
                    new_build['space']['boffs'][boff_id][i] = ''
                else:
                    new_build['space']['boffs'][boff_id][i] = {'item': ability}

        # ground
        self.map_build_items(build, new_build['ground'], BUILD_CONVERSION['ground'])

        try:
            for boff_id in range(4):
                new_build['ground']['boff_profs'][boff_id] = build['boffseats']['ground'][boff_id]
                new_build['ground']['boff_specs'][boff_id] = (
                    build['boffseats']['ground_spec'][boff_id])
                if new_build['ground']['boff_specs'][boff_id] is None:
                    new_build['ground']['boff_specs'][boff_id] = 'Command'
                for i, ability in enumerate(build['boffs'][f'groundBoff_{boff_id}']):
                    if ability is None or ability == '':
                        new_build['ground']['boffs'][boff_id][i]
                    else:
                        new_build['ground']['boffs'][boff_id][i] = {'item': ability}
        except KeyError:
            pass

        new_build['ground']['traits'] = build['personalGroundTrait'] + build['personalGroundTrait2']
        if len(new_build['ground']['traits']) < 12:
            new_build['ground']['traits'] += [None] * (12 - len(new_build['ground']['traits']))
        elite_captain_trait = new_build['ground']['traits'][5]
        new_build['ground']['traits'][5] = new_build['ground']['traits'][9]
        new_build['ground']['traits'][9] = elite_captain_trait

        # captain
        self.map_build_items(build, new_build['captain'], BUILD_CONVERSION['captain'])
        try:
            new_build['captain']['name'] = build['playerName'] + build['playerHandle']
            new_build['captain']['faction'] = build['captain']['faction']
        except KeyError:
            pass

        # doffs
        for environment in ('space', 'ground'):
            for doff_index, doff in enumerate(build['doffs'][environment]):
                if doff is not None and doff != '':
                    new_build[environment]['doffs_spec'][doff_index] = doff['spec']
                    try:
                        for variant in getattr(self._cargo, f'{environment}_doffs')[doff['spec']]:
                            if doff['effect'] in variant:
                                new_build[environment]['doffs_variant'][doff_index] = variant
                                break
                    except KeyError:
                        pass

        return new_build
