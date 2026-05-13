from os import listdir as os__listdir
from pathlib import Path
from PySide6.QtGui import QIcon, QImage, QPixmap
from time import time
from urllib.parse import quote_plus, unquote_plus

from .cargomanager import CargoManager
from .constants import SEVEN_DAYS_IN_SECONDS
from .downloader import Downloader
from .iofunc import get_image_file_name


class Overlays():
    """Stores overlay icons."""

    __slots__ = ('common', 'uncommon', 'rare', 'veryrare', 'ultrarare', 'epic', 'check')

    def __init__(self):
        self.common: QImage
        self.uncommon: QImage
        self.rare: QImage
        self.veryrare: QImage
        self.ultrarare: QImage
        self.epic: QImage
        self.check: QImage


class ImageManager():
    """Manages icons and ship images"""

    def __init__(
            self, images_dir: Path, ship_images_dir: Path, app_dir: Path, cargo_cache: CargoManager,
            downloader: Downloader):
        """
        Parameters:
        - :param images_dir: path to directory storing icons
        - :param ship_images_dir: path to directory storing ship images
        - :param app_dir: path to directory containing the app installation
        - :param cargo_cache: used to access cache
        - :param downloader: used to download icons and ship images
        """
        self._images_dir: Path = images_dir
        self._ship_images_dir: Path = ship_images_dir
        self._app_dir: Path = app_dir
        self._cargo_cache: CargoManager = cargo_cache
        self._downloader: Downloader = downloader
        self.empty: QImage = QImage()
        self.overlays: Overlays = Overlays()
        self.icons: dict[str, QIcon | QPixmap] = dict()
        self._images: dict[str, QImage] = dict()
        self.image_set: set[str] = set()
        self.failed_images: dict[str, int] = dict()

    def get(self, image_name: str) -> QImage:
        """
        Returns image from cache if cached, loads and returns image if not cached.

        Parameters:
        - :param image_name: name of the image
        """
        image = self._images[image_name]
        if image.isNull():
            image.load(str(self._images_dir / get_image_file_name(image_name)))
        return image

    def get_alt(self, image_name: str, image_suffix: str = '') -> QImage:
        """
        Returns image from cache if cached, loads and returns image if not cached. Tries to get
        alternate image first.

        Parameters:
        - :param image_name: name of the image
        - :param image_suffix: suffix to check in self.cache.alt_images
        """
        if image_name + image_suffix in self._cargo_cache.alt_images:
            return self.get(self._cargo_cache.alt_images[image_name + image_suffix])
        else:
            return self.get(image_name)

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

    def get_ship_image(self, image_name: str) -> QImage:
        """
        Tries to load ship image from local filesystem. If it is not avilable, downloads and
        stores it. Passes the image back using the provided signal. TODO improve result handling

        Parameters:
        - :image_name: filename of the image
        - :param threaded_worker: thread object supplying signals
        """
        image_path = self._ship_images_dir / quote_plus(image_name)
        image = QImage(image_path)
        if image.isNull():
            # TODO integrate with failed images
            self._downloader.download_ship_image(image_name, {})
            image = QImage(image_path)
        return image

    def load_base_images(self):
        """
        Loads all images that are required for the app to start (skills, overlays)
        """
        local_folder = self._app_dir / 'local'
        self._images = {image_name: QImage() for image_name in self.image_set}
        self.overlays.common = QImage(local_folder / 'Common_icon.png')
        self.overlays.uncommon = QImage(local_folder / 'Uncommon_icon.png')
        self.overlays.rare = QImage(local_folder / 'Rare_icon.png')
        self.overlays.veryrare = QImage(local_folder / 'Very_rare_icon.png')
        self.overlays.ultrarare = QImage(local_folder / 'Ultra_rare_icon.png')
        self.overlays.epic = QImage(local_folder / 'Epic_icon.png')
        self.overlays.check = QImage(local_folder / 'check_overlay.png')

        for rank_group in self._cargo_cache.skills['space']:
            for skill_group in rank_group:
                for skill_node in skill_group['nodes']:
                    self._images[skill_node['image']] = QImage(
                        self._images_dir / get_image_file_name(skill_node['image']))
        for skill_group in self._cargo_cache.skills['ground']:
            for skill_node in skill_group['nodes']:
                self._images[skill_node['image']] = QImage(
                    self._images_dir / get_image_file_name(skill_node['image']))
        self._images['arrow-up'] = QImage(local_folder / 'arrow-up.png')
        self._images['arrow-down'] = QImage(local_folder / 'arrow-down.png')
        self._images['Focused Frenzy'] = QImage(
            self._images_dir / get_image_file_name('Focused Frenzy'))
        self._images['Probability Manipulation'] = QImage(
            self._images_dir / get_image_file_name('Probability Manipulation'))
        self._images['EPS Corruption'] = QImage(
            self._images_dir / get_image_file_name('EPS Corruption'))

    def load_images(self):
        """
        Loads images from drive.
        """
        image_dir = str(self._images_dir)
        for image_name, image in self._images.items():
            if image.isNull():
                image.load(f'{image_dir}/{get_image_file_name(image_name)}')
