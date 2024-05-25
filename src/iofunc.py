import os

from PySide6.QtGui import QIcon


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
