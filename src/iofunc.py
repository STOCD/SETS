import json
from json import dump as json__dump, load as json__load, JSONDecodeError
import os
from pathlib import Path
from shutil import rmtree as shutil__rmtree
import sys
from urllib.parse import quote_plus
from webbrowser import open as webbrowser_open

from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QFileDialog, QWidget

from .constants import WIKI_URL


def browse_path(
        preset_path: Path, types: str = 'Any File (*.*)', save: bool = False,
        parent_window: QWidget | None = None) -> Path | None:
    """
    Opens file dialog prompting the user to select a file.

    Parameters:
    - :param preset_path: path that the file dialog opens at; includes default file name
    - :param types: string containing all file extensions and their respective names that are \
    allowed. Format: `<name of file type> (*.<extension>);;<name of file type> (*.<extension>);; \
    [...]` Example: `Logfile (*.log);;Any File (*.*)`
    - :param save: False => open file with dialog; True => save file with dialog
    - :param parent_window: window to use as parent; uses window icon and name of parent window

    :return: returns selected path; None if user aborts or tries to open not-existing file
    """
    if save:
        f = QFileDialog.getSaveFileName(parent_window, 'Save Log', str(preset_path), types)[0]
        if f == '':
            return None
        return Path(f)
    else:
        f = QFileDialog.getOpenFileName(parent_window, 'Open Log', str(preset_path), types)[0]
        if f == '':
            return None
        selected_path = Path(f)
        if selected_path.exists():
            return selected_path
        else:
            return None


def delete_folder_contents(path_to_folder):
    """
    Delets all files and folders within a folder.

    Parameters:
    - :param path_to_folder: absolute path to folder
    """
    if os.path.exists(path_to_folder) and os.path.isdir(path_to_folder):
        shutil__rmtree(path_to_folder)
        os.mkdir(path_to_folder)


def load_icon(filename: str, app_directory: Path, size: tuple = tuple()) -> QIcon | QPixmap:
    """
    Loads icon from path and returns it.

    Parameters:
    - :param path: path to icon
    - :param app_directory: absolute path to the app directory
    """
    icon = QIcon(str(app_directory / 'local' / filename))
    if len(size) == 2:
        return icon.pixmap(*size)
    return icon


def load_json__new(file_path: Path) -> dict | list | None:
    """
    Loads json from path and returns dictionary or list. Returns `None` if no data could be found.

    Parameters:
    - :param path: path to json file
    """
    try:
        with file_path.open() as json_file:
            return json__load(json_file)
    except (OSError, JSONDecodeError):
        return None


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


def store_json__new(data: dict | list, path: Path) -> bool:
    """
    Stores data to json file at path. Overwrites file at target location. Raises ValueError if path
    is not absolute. Returns `False` if file could not be saved, `True` otherwise.

    Paramters:
    - :param data: dictionary or list that should be stored
    - :param path: file path to store the data to
    """
    try:
        with path.open('w') as file:
            json__dump(data, file)
        return True
    except OSError:
        return False


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
