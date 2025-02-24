from datetime import datetime
import json
import os
from shutil import copyfile as shutil__copyfile, rmtree as shutil__rmtree
import sys
from urllib.parse import quote_plus, unquote_plus
from webbrowser import open as webbrowser_open

from PySide6.QtGui import QIcon, QImage
from PySide6.QtWidgets import QFileDialog
import requests
from requests_html import HTMLSession

from .constants import WIKI_IMAGE_URL, WIKI_URL
from .textedit import compensate_json


def browse_path(self, default_path: str = None, types: str = 'Any File (*.*)', save=False) -> str:
    """
    Opens file dialog prompting the user to select a file.

    Parameters:
    - :param default_path: path that the file dialog opens at
    - :param types: string containing all file extensions and their respective names that are
    allowed.
    Format: "<name of file type> (*.<extension>);;<name of file type> (*.<extension>);; [...]"
    Example: "Logfile (*.log);;Any File (*.*)"
    """
    if default_path is None or default_path == '':
        default_path = self.app_dir
    default_path = os.path.abspath(default_path)
    if not os.path.exists(os.path.dirname(default_path)):
        default_path = self.app_dir
    if save:
        file, _ = QFileDialog.getSaveFileName(self.window, 'Save...', default_path, types)
    else:
        file, _ = QFileDialog.getOpenFileName(self.window, 'Open...', default_path, types)
    return file


def get_cargo_data(self, filename: str, url: str, ignore_cache_age=False) -> dict | list:
    """
    Retrieves cargo data for specific table. Downloads cargo data from wiki if cargo cache is empty.
    Updates cargo cache.

    Parameters:
    - :param filename: filename of cache file
    - :param url: url to cargo table
    - :param ignore_cache_age: True if cache of any age should be accepted
    """
    filepath = os.path.join(self.config['config_subfolders']['cargo'], filename)
    cargo_data = None

    # try loading from cache
    if os.path.exists(filepath) and os.path.isfile(filepath):
        last_modified = os.path.getmtime(filepath)
        if (datetime.now() - datetime.fromtimestamp(last_modified)).days < 7 or ignore_cache_age:
            try:
                return load_json(filepath)
            except json.JSONDecodeError:
                pass

    # download cargo data if loading from cache failed or data should be updated
    try:
        cargo_data = fetch_json(url)
        store_json(cargo_data, filepath)
        return cargo_data
    except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, json.JSONDecodeError):
        if ignore_cache_age:
            backup_path = os.path.join(self.config['config_subfolders']['backups'], filename)
            if os.path.exists(backup_path) and os.path.isfile(backup_path):
                try:
                    cargo_data = load_json(backup_path)
                    store_json(cargo_data, filepath)
                    return cargo_data
                except json.JSONDecodeError:
                    pass
            sys.stderr.write(f'[Error] Cargo table could not be retrieved ({filename})\n')
            sys.exit(1)
        else:
            return get_cargo_data(self, filename, url, ignore_cache_age=True)


def get_cached_cargo_data(self, filename: str) -> dict | list:
    """
    Retrieves cached cargo data from filename. Returns empty dict when cache is too old or
    corrupted.

    Parameters:
    - :param filename: name of the cache file
    """
    filepath = os.path.join(self.config['config_subfolders']['cache'], filename)
    if os.path.exists(filepath) and os.path.isfile(filepath):
        last_modified = os.path.getmtime(filepath)
        if (datetime.now() - datetime.fromtimestamp(last_modified)).days < 7:
            try:
                return load_json(filepath)
            except json.JSONDecodeError:
                pass
    return {}


def store_to_cache(self, data, filename: str):
    """
    Stores data to cache file with filename.

    Parameters:
    - :param data: data that will be stored
    - :param filename: filename of the cache file
    """
    filepath = os.path.join(self.config['config_subfolders']['cache'], filename)
    store_json(data, filepath)


def retrieve_image(
        self, name: str, image_folder_path: str, signal=None, url_override: str = '') -> QImage:
    """
    Downloads image or fetches image from cache.

    Parameters:
    - :param name: name of the item
    - :param image_folder_path: path to the image folder
    - :param signal: signal that is emitted to chance splash when downloading image (optional)
    - :param url_override: non default image url (optional)
    """
    filename = get_image_file_name(name)
    filepath = os.path.join(image_folder_path, filename)
    image = QImage(filepath)
    if image.isNull():
        if signal is not None:
            signal.emit(f'Downloading Image: {name}')
        image = download_image(self, name, image_folder_path, url_override)
    return image


def download_image(self, name: str, image_folder_path: str, url_override: str = ''):
    """
    Downloads image from wiki and stores it in images folder. Returns the image.

    Parameters:
    - :param name: name of the item
    - :param image_folder_path: path to the image folder
    - :param url_override: non default image url (optional)
    """
    filepath = os.path.join(image_folder_path, get_image_file_name(name))
    if url_override == '':
        image_url = f'{WIKI_IMAGE_URL}{name.replace(' ', '_')}_icon.png'
    else:
        image_url = url_override
    image_response = requests.get(image_url)
    image = QImage()
    if image_response.ok:
        image.loadFromData(image_response.content, 'png')
        image.save(filepath)
    else:
        self.cache.images_failed[name] = int(datetime.now().timestamp())
    return image


def get_ship_image(self, image_name: str, threaded_worker):
    """
    Tries to fetch ship image from local filesystem, downloads it otherwise. Returns the image.

    Parameters:
    - :image_name: filename of the image
    - :param threaded_worker: thread object supplying signals
    """
    image_url = WIKI_IMAGE_URL + image_name.replace(' ', '_')
    image_path = os.path.join(
            self.config['config_subfolders']['ship_images'], quote_plus(image_name))
    _, _, fmt = image_name.rpartition('.')
    image = QImage(image_path)
    if image.isNull():
        image_response = requests.get(image_url)
        if image_response.ok:
            image.loadFromData(image_response.content, fmt)
            image.save(image_path)
        # else: returns null image
    threaded_worker.result.emit((image,))


def load_image(image_name: str, image: QImage, image_folder_path: str) -> QImage:
    """
    Retrieves image from images folder and returns it. Assumes the image exists.

    Parameters:
    - :param image_name: name of the image
    - :param image: preconstructed (empty) Image
    - :param image_folder_path: path to the image folder
    """
    image_path = os.path.join(image_folder_path, get_image_file_name(image_name))
    image.load(image_path)


def image(self, image_name: str) -> QImage:
    """
    Returns image from cache if cached, loads and returns image if not cached.

    Parameters:
    - :param image_name: name of the image
    """
    img = self.cache.images[image_name]
    if img.isNull():
        img_folder = self.config['config_subfolders']['images']
        load_image(image_name, img, img_folder)
    return img


def get_downloaded_images(self) -> set:
    """
    Returns set containing all images currently in the images folder.
    """
    img_folder = self.config['config_subfolders']['images']
    return set(map(lambda x: unquote_plus(x)[:-4], os.listdir(img_folder)))


# --------------------------------------------------------------------------------------------------
# static functions
# --------------------------------------------------------------------------------------------------


def create_folder(path_to_folder):
    """
    Creates the folder at path_to_folder in case it does not exist.

    Parameters:
    - :param path_to_folder: absolute path to folder
    """
    if not os.path.exists(path_to_folder) and not os.path.isdir(path_to_folder):
        os.mkdir(path_to_folder)


def delete_folder_contents(path_to_folder):
    """
    Delets all files and folders within a folder.

    Parameters:
    - :param path_to_folder: absolute path to folder
    """
    if os.path.exists(path_to_folder) and os.path.isdir(path_to_folder):
        shutil__rmtree(path_to_folder)
        os.mkdir(path_to_folder)


def copy_file(source_path, target_path):
    """
    Tries to copy file from `source_path` to `target_path`

    Parameters:
    - :param source_path: file to copy
    - :param target_path: location and name of the target file
    """
    if os.path.exists(source_path) and os.path.isfile(source_path):
        shutil__copyfile(source_path, target_path)


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
    Fetches json from url and returns parsed object. Raises `requests.exceptions.JSONDecodeError` if
    result cannot be decoded. Raises `requests.exceptions.Timeout` or 2 download attempts failed.

    Parameters:
    - :param url: URL to file
    """
    try:
        r = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        r = requests.get(url, timeout=10)
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
    """
    Converts txt to a valid filename.

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
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6',
            'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8',
            'LPT9', 'CONIN$', 'CONOUT$', '..', '.')
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
    result = result.strip()
    while len(result) > 0 and result[-1] == '.':
        result = result[:-1]

    return result


def get_image_file_name(name: str) -> str:
    """
    Converts image name to valid file name
    """
    return f'{quote_plus(name)}.png'


def open_url(url: str):
    """
    Opens URL in webbrowser
    """
    webbrowser_open(url, new=2, autoraise=True)


def open_wiki_page(page_name: str):
    """
    Converts page name to URL and opens page in webbrowser.
    """
    open_url(WIKI_URL + page_name.replace(' ', '_'))
