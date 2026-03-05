from json import loads as json__loads, JSONDecodeError
from pathlib import Path
from requests import Session
from requests.exceptions import Timeout
from time import time
from threading import Thread
from urllib.parse import quote_plus

from .constants import GITHUB_CACHE_URL, WIKI_IMAGE_URL
from .textedit import compensate_json


class ReturnValueThread(Thread):
    def __init__(self, target, args: tuple = tuple()):
        super().__init__(target=target, args=args)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args)

    def join(self):
        super().join()
        return self._return


class Downloader():
    """Downloads images and cargo tables"""

    def __init__(self, images_dir: Path, ship_images_dir: Path):
        """
        Parameters:
        - :param images_dir: path to directory storing icons
        - :param ship_images_dir: path to directory storing ship images
        """
        self._images_dir: str = str(images_dir)
        self._ship_images_dir: str = str(ship_images_dir)
        self._session: Session = Session()
        self._cookies: dict[str, str] = dict()
        self._headers: dict[str, str] = dict()

    def configure_default_session(self, cookies: dict[str, str] = {}, headers: dict[str, str] = {}):
        """
        Update default session with cookies and headers, these will also be used for new sessions.

        Parameters:
        - :param cookies: cookies to update session and session defaults with
        - :param headers: headers to update session and session defaults with
        """
        self._cookies.update(cookies)
        self._headers.update(headers)
        self._session.cookies.clear()
        self._session.cookies.update(self._cookies)
        self._session.headers.clear()
        self._session.headers.update(self._headers)

    def fetch_json(self, url: str) -> dict | list | None:
        """
        Fetches json from url and returns parsed object. Returns `None` if retrieveing the json
        takes longer than 10 seconds or returned data is invalid.

        Paramters:
        - :param url: url to json file
        """
        try:
            response = self._session.get(url, timeout=10)
            if response.ok:
                response.encoding = 'utf-8'
                return json__loads(compensate_json(response.text))
            return None
        except (Timeout, JSONDecodeError):
            return None

    def download_cargo_table(self, url: str, file_name: str) -> dict | list | None:
        """
        Downloads cargo data for specific table from `url` and stores it as `file_name`. Downloads
        from the wiki first and if that failes from GitHub cache. Returns `None` if data unavailable
        or corrupt.

        Parameters:
        - :param url: url to cargo table
        - :param file_name: filename of cache file
        """
        cargo_data = self.fetch_json(url)
        if cargo_data is None:
            cache_url = f'{GITHUB_CACHE_URL}/cargo/{file_name}'
            cargo_data = self.fetch_json(cache_url)
        return cargo_data

    def download_image(
            self, name: str, failed_images: dict[str, int], session: Session,
            image_suffix: str = '_icon.png'):
        """
        Downloads image using provided session. If downloading from the wiki fails, tries to
        download from GitHub cache. Updates `failed_images` if download fails from both sources.

        Parameters:
        - :param name: name of the image to download
        - :param failed_images: dictionary containing failed images and their time of failure
        - :param session: session to use for downloading
        - :param image_suffix: suffix used to construct url
        """
        filepath = f'{self._images_dir}/{quote_plus(name)}.png'
        url = WIKI_IMAGE_URL + name.replace(' ', '_') + image_suffix
        image_response = session.get(url)
        if image_response.ok:
            with open(filepath, 'wb') as image_file:
                image_file.write(image_response.content)
        else:
            url = f'{GITHUB_CACHE_URL}/images/{quote_plus(name).replace('%', '%25')}.png'
            image_response = session.get(url)
            if image_response.ok:
                with open(filepath, 'wb') as image_file:
                    image_file.write(image_response.content)
            else:
                failed_images[name] = int(time())

    def download_ship_image(
            self, name: str, failed_images: dict[str, int], session: Session | None = None):
        """
        Downloads image using provided session. If downloading from the wiki fails, tries to
        download from GitHub cache. Updates `failed_images` if download fails from both sources.

        Parameters:
        - :param name: name of the image to download
        - :param failed_images: dictionary containing failed images and their time of failure
        - :param session: session to use for downloading, uses default session if `None`
        - :param image_suffix: suffix used to construct url
        """
        if session is None:
            session = self._session
        filepath = f'{self._ship_images_dir}/{quote_plus(name)}'
        url = WIKI_IMAGE_URL + name.replace(' ', '_')
        image_response = session.get(url)
        if image_response.ok:
            with open(filepath, 'wb') as image_file:
                image_file.write(image_response.content)
        else:
            url = f'{GITHUB_CACHE_URL}/ship_images/{quote_plus(name)}'
            image_response = session.get(url)
            if image_response.ok:
                with open(filepath, 'wb') as image_file:
                    image_file.write(image_response.content)
            else:
                failed_images[name] = int(time())

    def download_image_chunk(
            self, image_list: list[str], image_suffix: str = '_icon.png',
            image_type: str = 'icon') -> dict[str, int]:
        """
        Downloads chunk of images and saves them to disk. Returns dictionary
        mapping failed images to the timestamp at which the download failed.

        Parameters:
        - :param image_list: list of image names to download
        - :param image_suffix: suffix used to construct download url
        - :param image_type: `icon` for saving to the `images` folder, `ship` for saving to the
        `ship_images` folder
        """
        requests_session = Session()
        requests_session.cookies.update(self._cookies)
        requests_session.headers.update(self._headers)
        failed_images = dict()
        if image_type == 'icon':
            for image_name in image_list:
                self.download_image(image_name, failed_images, requests_session, image_suffix)
        elif image_type == 'ship':
            for image_name in image_list:
                self.download_ship_image(image_name, failed_images, requests_session)
        return failed_images

    def download_image_list(
            self, image_list: list[str], image_suffix: str = '_icon.png',
            image_type: str = 'icon') -> dict[str, int]:
        """
        Downloads list of images using mutiple threads and saves them. Returns dictionary
        mapping failed images to the timestamp at which the download failed.

        Parameters:
        - :param image_list: list of image names to download
        - :param image_suffix: suffix used to construct download url
        - :param image_type: `icon` for saving to the `images` folder, `ship` for saving to the
        `ship_images` folder
        """
        total_threads = 16
        image_chunk_size = len(image_list) // total_threads
        while image_chunk_size < 4 and total_threads > 1:
            total_threads -= 1
            image_chunk_size = len(image_list) // total_threads
        threads: list[ReturnValueThread] = list()
        for thread_num in range(total_threads):
            image_chunk_start = image_chunk_size * thread_num
            if thread_num == total_threads - 1:
                images = image_list[image_chunk_start:]
            else:
                image_chunk_end = image_chunk_size * (thread_num + 1)
                images = image_list[image_chunk_start:image_chunk_end]
            thread = ReturnValueThread(
                target=self.download_image_chunk, args=(images, image_suffix, image_type))
            thread.start()
            threads.append(thread)
        failed_images = dict()
        for thread in threads:
            failed_images.update(thread.join())
        return failed_images
