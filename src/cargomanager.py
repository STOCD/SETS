from pathlib import Path
from time import time

from .constants import SEVEN_DAYS_IN_SECONDS
from .iofunc import load_json__new


class CargoManager():
    """Manages Cargo data and cache"""

    def __init__(self, folders: dict[str, str]):
        """
        Parameters:
        - :param folders: folder names and paths of config folder
        """
        self._folders: dict[str, Path] = {name: Path(path) for name, path in folders.items()}
        self.boff_abilities: dict[str, dict[str, dict]] = {
            'space': self.boff_dict(),
            'ground': self.boff_dict(),
            'all': dict()
        }

    def get_cached_data(self, file_name: str) -> dict | list | None:
        """
        Retrieves cached cargo data. Returns `None` when cache is too old or corrupted.

        Parameters:
        - :param file_name: name of the cache file to load
        """
        file_path = self._folders['cache'] / file_name
        last_modified = file_path.stat().st_mtime
        if time() - last_modified < SEVEN_DAYS_IN_SECONDS:
            return load_json__new(file_path)
        return None

    def boff_dict(self):
        return {
            'Tactical': [dict(), dict(), dict(), dict()],
            'Engineering': [dict(), dict(), dict(), dict()],
            'Science': [dict(), dict(), dict(), dict()],
            'Intelligence': [dict(), dict(), dict(), dict()],
            'Command': [dict(), dict(), dict(), dict()],
            'Pilot': [dict(), dict(), dict(), dict()],
            'Temporal': [dict(), dict(), dict(), dict()],
            'Miracle Worker': [dict(), dict(), dict(), dict()],
        }
