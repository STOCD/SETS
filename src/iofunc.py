from datetime import datetime
import json
import os
from re import sub as re_sub
import sys
from urllib.parse import quote_plus

from PySide6.QtGui import QIcon, QPixmap
import requests
from requests_html import HTMLSession

from .constants import WIKI_IMAGE_URL
from .textedit import compensate_json


def get_cargo_data(self, filename: str, url: str, ignore_cache_age=False) -> dict | list:
    """
    Retrieves cargo data for specific table. Downloads cargo data from wiki if cache is empty.
    Updates cache.

    Parameters:
    - :param filename: filename of cache file
    - :param url: url to cargo table
    - :param ignore_cache_age: True if cache of any age should be accepted
    """
    filepath = f"{self.config['config_subfolders']['cache']}\\{filename}"
    cargo_data = None

    # try loading from cache
    if os.path.exists(filepath) and os.path.isfile(filepath):
        last_modified = os.path.getmtime(filepath)
        if (datetime.now() - datetime.fromtimestamp(last_modified)).days < 7 or ignore_cache_age:
            try:
                return load_json(filepath)
            except json.JSONDecodeError:
                backup_filepath = f"{self.config['config_subfolders']['backups']}\\{filename}"
                if os.path.exists(backup_filepath) and os.path.isfile(backup_filepath):
                    try:
                        cargo_data = load_json(backup_filepath)
                        store_json(cargo_data, filepath)
                        return cargo_data
                    except json.JSONDecodeError:
                        pass

    # download cargo data if loading from cache failed or data should be updated
    try:
        cargo_data = fetch_json(url)
        store_json(cargo_data, filepath)
        return cargo_data
    except requests.exceptions.JSONDecodeError:
        if ignore_cache_age:
            sys.stderr.write(f'[Error] Cargo table could not be retrieved ({filename})\n')
            sys.exit(1)
        else:
            return get_cargo_data(self, filename, url, ignore_cache_age=True)


def retrieve_image(
        self, name: str, image_folder_path: str, signal=None, url_override: str = '') -> QPixmap:
    """
    Downloads image or fetches image from cache.

    Parameters:
    - :param name: name of the item
    - :param image_folder_path: path to the image folder
    - :param signal: signal that is emitted to chance splash when downloading image (optional)
    - :param url_override: non default image url (optional)
    """
    filename = get_image_file_name(name)
    filepath = f'{image_folder_path}\\{filename}'
    image = QPixmap(filepath)
    if image.isNull():
        if signal is not None:
            signal.emit(f'Loading Image: {name}')
        if url_override == '':
            image_url = f'{WIKI_IMAGE_URL}{name.replace(' ', '_')}_icon.png'
        else:
            image_url = url_override
        image_response = requests.get(image_url)
        if image_response.ok:
            image.loadFromData(image_response.content, 'png')
            image.save(filepath)
        else:
            return self.cache.empty_image
    return image


def get_ship_image(self, name: str, image_name: str, thread):
    image_url = WIKI_IMAGE_URL + image_name.replace(' ', '_')
    image_folder = self.config['config_subfolders']['ship_images']
    image = retrieve_image(self, name, image_folder, url_override=image_url)
    thread.result.emit((image,))

# --------------------------------------------------------------------------------------------------
# static functions
# --------------------------------------------------------------------------------------------------


def load_image(path: str) -> QPixmap:
    """
    Reads image from filesystem, scales it accordingly and returns it.

    Parameters:
    - :param path: path to image
    """
    image = QPixmap(path)
    return image


def create_folder(path_to_folder):
    """
    Creates the folder at path_to_folder in case it does not exist.

    Parameters:
    - :path_to_folder: absolute path to folder
    """
    if not os.path.exists(path_to_folder) and not os.path.isdir(path_to_folder):
        os.mkdir(path_to_folder)


def get_asset_path(asset_name: str, app_directory: str) -> str:
    """
    returns the absolute path to a file in the asset folder

    Parameters:
    - :param asset_name: filename of the asset
    - :param app_directory: absolute path to app directory
    """
    fp = os.path.join(app_directory, 'local', asset_name)
    if os.path.exists(fp):
        return fp
    else:
        return ''


def load_icon(filename: str, app_directory: str) -> QIcon:
    """
    Loads icon from path and returns it.

    Parameters:
    - :param path: path to icon
    - :param app_directory: absolute path to the app directory
    """
    return QIcon(get_asset_path(filename, app_directory))


def load_json(path: str) -> dict | list:
    """
    Loads json from path and returns dictionary or list.

    Parameters:
    - :param path: absolute path to json file
    """
    if not (os.path.exists(path) and os.path.isfile(path) and os.path.isabs(path)):
        raise FileNotFoundError(f'Invalid / not absolute path: {path}')
    with open(path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data


def store_json(data: dict | list, path: str):
    """
    Stores data to json file at path. Overwrites file at target location. Raises ValueError if path
    is not absolute.

    Paramters:
    - :param data: dictionary or list that should be stored
    - :param path: target location; must be absolute path
    """
    if not os.path.isabs(path):
        raise ValueError(f'Path to file must be absolute: {path}')
    try:
        with open(path, 'w') as file:
            json.dump(data, file)
    except OSError as e:
        sys.stdout.write(f'[Error] Data could not be saved: {e}')


def fetch_json(url: str) -> dict | list:
    """
    Fetches json from url and returns parsed object. Raises requests.exceptions.JSONDecodeError if
    result cannot be decoded or 2 download attempts failed.

    Parameters:
    - :param url: URL to file
    """
    try:
        r = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        try:
            r = requests.get(url, timeout=10)
        except requests.exceptions.Timeout:
            raise requests.exceptions.JSONDecodeError
    r.encoding = 'utf-8'
    return json.loads(compensate_json(r.text))


def fetch_html(url: str):
    """
    Fetches html from url and returns plain text. Raises requests.exceptions.Timeout if
    2 download attempts failed.

    Parameters:
    - :param url: URL to file
    """
    session = HTMLSession()
    r = session.get(url)
    return r.html


def sanitize_file_name(txt, chr_set='extended') -> str:
    """Converts txt to a valid filename.
    """
    FILLER = '-'
    MAX_LEN = 255  # Maximum length of filename is 255 bytes in Windows and some *nix flavors.

    # Step 1: Remove excluded characters.
    BLACK_LIST = set(chr(127) + r'<>:"/\|?*')
    white_lists = {
        'universal': {'-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'},
        'printable': {chr(x) for x in range(32, 127)} - BLACK_LIST,     # 0-32, 127 are unprintable,
        'extended': {chr(x) for x in range(32, 256)} - BLACK_LIST,
    }
    white_list = white_lists[chr_set]
    result = ''.join(x if x in white_list else FILLER for x in txt)

    # Step 2: Device names, '.', and '..' are invalid filenames in Windows.
    DEVICE_NAMES = (
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7',
            'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
            'CONIN$', 'CONOUT$', '..', '.')
    if '.' in txt:
        name, _, ext = result.rpartition('.')
        ext = f'.{ext}'
    else:
        name = result
        ext = ''
    if name in DEVICE_NAMES:
        result = f'-{result}-{ext}'

    # Step 3: Truncate long files while preserving the file extension.
    if len(result) > MAX_LEN:
        result = result[:MAX_LEN - len(ext)] + ext

    # Step 4: Windows does not allow filenames to end with '.' or ' ' or begin with ' '.
    result = re_sub(r"[. ]$", FILLER, result)
    result = re_sub(r"^ ", FILLER, result)

    return result


def get_image_file_name(name: str) -> str:
    """
    Converts image name to valid file name
    """
    identifier = quote_plus(name)
    return f'{identifier}+icon.png'
