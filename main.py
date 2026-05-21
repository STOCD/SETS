from argparse import ArgumentParser
from os.path import abspath as os__abspath, dirname as os__dirname
import sys

from src import SETS


class Launcher():

    __version__ = '3.0.1'

    @staticmethod
    def base_path() -> str:
        """initialize the base path"""
        try:
            base_path = sys._MEIPASS
        except Exception:
            if getattr(sys, 'frozen', False):
                # The application is frozen
                base_path = os__dirname(sys.executable)
            else:
                base_path = os__abspath(os__dirname(__file__))
        return base_path

    @staticmethod
    def launch():
        argparser = ArgumentParser(prog='SETS', description='STO Equipment and Trait Selector')
        # argparser.add_argument(
        #     '--build-cache', action='store_true', required=False,
        #     help='Provide this flag to build the cache instead of starting the app.')
        argparser.add_argument(
            '--config-dir', type=str, required=False,
            help='Change configuration directory (must be readable and writable)')
        args, _ = argparser.parse_known_args()
        exit_code = SETS(
            args=args, app_dir_path=Launcher.base_path(), version=Launcher.__version__).run()
        sys.exit(exit_code)


if __name__ == '__main__':
    Launcher.launch()
