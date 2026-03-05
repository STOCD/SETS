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
        self.icon_set: set[str] = set()
        self.failed_images: dict[str, int] = dict()

    def get_downloaded_icons(self) -> set[str]:
        """
        Returns set containing all images currently in the images folder.
        """
        return set(map(lambda x: unquote_plus(x)[:-4], os__listdir(str(self._images_dir))))

    def download_images(self):
        """
        Ensures that all required images are downloaded to disk. Updates `failed_images`.
        """
        no_retry_images = set()
        now = time()
        for image_name, timestamp in self.failed_images.items():
            if now - timestamp < 7:
                no_retry_images.add(image_name)
            else:
                self.failed_images.pop(image_name)
        images = self.icon_set - no_retry_images - self.get_downloaded_icons()

        images_to_download = images - self._cargo_cache.boff_abilities['all'].keys()
        failed = self._downloader.download_image_list(list(images_to_download))
        self.failed_images.update(failed)

        boff_images_to_download = images & self._cargo_cache.boff_abilities['all'].keys()
        failed = self._downloader.download_image_list(
            list(boff_images_to_download), image_suffix='_icon_(Federation).png')
        self.failed_images.update(failed)
