from os import listdir as os__listdir
from pathlib import Path
from PySide6.QtGui import QImage
from time import time
from urllib.parse import unquote_plus

from .cargomanager import CargoManager
from .constants import SEVEN_DAYS_IN_SECONDS
from .downloader import Downloader
from .iofunc import get_cached_cargo_data


class ImageManager():
    """Manages icons and ship images"""

    def __init__(
            self, images_dir: Path, ship_images_dir: Path, cargo_cache: CargoManager,
            downloader: Downloader):
        """
        Parameters:
        - :param images_dir: path to directory storing icons
        - :param ship_images_dir: path to directory storing ship images
        - :param cargo_cache: used to access cache
        - :param downloader: used to download icons and ship images
        """
        self._images_dir: Path = images_dir
        self._ship_images_dir: Path = ship_images_dir
        self._cargo_cache: CargoManager = cargo_cache
        self._downloader: Downloader = downloader
        self.empty = QImage()
        self.image_set: set[str] = set()
        self.failed_images: dict[str, int] = dict()

    def get_downloaded_icons(self) -> set[str]:
        """
        Returns set containing all images currently in the images folder.
        """
        return set(map(lambda x: unquote_plus(x)[:-4], os__listdir(str(self._images_dir))))

    def download_images(self, skill_cache: dict[str, dict]):
        """
        Ensures that all required images are downloaded to disk. Updates `failed_images`.

        Parameters:
        - :param skill_cache: cache containing skills for extracting skill icon names
        """
        no_retry_images = set()
        retry_images = list()
        now = time()
        for image_name, timestamp in self.failed_images.items():
            if now - timestamp < SEVEN_DAYS_IN_SECONDS:
                no_retry_images.add(image_name)
            else:
                retry_images.append(image_name)
        for image_name in retry_images:
            del self.failed_images[image_name]
        available_images = self.get_downloaded_icons() | no_retry_images

        # TODO have all icons (including skills) in image_set from the start
        ultimate_skill_icons = {'Focused Frenzy', 'Probability Manipulation', 'EPS Corruption'}
        image_set = self.image_set | ultimate_skill_icons
        images = image_set - available_images - self._cargo_cache.boff_abilities['all'].keys()
        failed = self._downloader.download_image_list(list(images))
        self.failed_images.update(failed)

        boff_images = self._cargo_cache.boff_abilities['all'].keys() - available_images
        failed = self._downloader.download_image_list(
            list(boff_images), image_suffix='_icon_(Federation).png')
        self.failed_images.update(failed)

        skill_images = self.get_skill_icons(skill_cache) - available_images
        failed = self._downloader.download_image_list(list(skill_images), image_suffix='.png')
        self.failed_images.update(failed)

    def get_skill_icons(self, skill_cache: dict[str, dict]) -> set[str]:
        """
        Extracts skill icon names from skill cache.

        Parameters:
        - :param skill_cache: contains ground and space skill tree
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
