from json import loads as json__loads, JSONDecodeError
from pathlib import Path
from requests import Session
from requests.exceptions import Timeout

from .constants import GITHUB_CACHE_URL
from .textedit import compensate_json


class Downloader():
    """Downloads images and cargo tables"""

    def __init__(self):
        """
        Parameters:
        - :param target_paths: collection of paths for saving downloaded data to
        """
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
