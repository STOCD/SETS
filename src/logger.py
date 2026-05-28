from datetime import datetime

from PySide6.QtCore import QObject, Signal, Slot

from .config import SETSConfig


class Logger(QObject):
    """Logs events for debugging purposes"""

    log_event: Signal = Signal(str)

    def __init__(self, config: SETSConfig):
        super().__init__()
        self._config: SETSConfig = config
        self.log_event.connect(self.log_to_file)

    @Slot(str)
    def log_to_file(self, message: str):
        """
        Writes log message to standard log file.

        Parameters:
        - :param message: text to show in logfile
        """
        now = datetime.now()
        log_line = (
            f'[{now.year}-{now.month:02d}-{now.day:02d}] [{now.hour:02d}:{now.minute:02d}:'
            f'{now.second:02d}] {message}\n')
        with self._config.log_path.open('a') as log_file:
            log_file.write(log_line)
