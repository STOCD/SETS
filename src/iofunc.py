import json
import os
from re import sub as re_sub
import sys

from PySide6.QtGui import QIcon
import requests


def create_folder(self, path_to_folder):
    """
    Creates the folder at path_to_folder in case it does not exist.

    Parameters:
    - :path_to_folder: absolute path to folder
    """
    if not os.path.exists(path_to_folder) and not os.path.isdir(path_to_folder):
        os.mkdir(path_to_folder)


# --------------------------------------------------------------------------------------------------
# static functions
# --------------------------------------------------------------------------------------------------


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
    return r.json()


def sanitize_file_name(txt, chr_set='extended') -> str:
    """Converts txt to a valid filename.

    Parameters:
    - :param txt: The path to convert.
    - :param chr_set:
        - 'printable':    Any printable character except those disallowed on Windows/*nix.
        - 'extended':     'printable' + extended ASCII character codes 128-255
        - 'universal':    For almost *any* file system.
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
