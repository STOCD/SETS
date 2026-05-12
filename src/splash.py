from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QLabel, QTabWidget


class SplashScreen(QObject):
    """Manages splash screen"""

    show: Signal = Signal(bool)
    loading_text: Signal = Signal(str)
    progress_init: Signal = Signal(str, int)
    progress_step: Signal = Signal()

    def __init__(self):
        super().__init__()
        self.loading_label: QLabel
        self.progress_label: QLabel
        self.tabber: QTabWidget
        self._progress_text: str = 'Progress:'
        self._progress_total: int = 0
        self._progress_current: int = 0
        self.show.connect(self._show_splash)
        self.loading_text.connect(self._set_loading_text)
        self.progress_init.connect(self._init_progress)
        self.progress_step.connect(self._increment_progress)

    def show_splash(self, visible: bool):
        """
        Shows/hides splash.

        Parameters:
        - :param visible: `True` to show splash, `False` to hide it
        """
        self.show.emit(visible)

    def init_progress(self, message: str, total_progress: int):
        """
        Makes progress label ready.

        Parameters:
        - :param message: progress message
        - :param total_progress: total number of steps
        """
        self.progress_init.emit(message, total_progress)

    def increment_progress(self):
        """
        Increments progress count by 1.
        """
        self.progress_step.emit()

    def set_loading_text(self, message: str):
        """
        Sets loading labels' text.

        Parameters:
        - :param message: message to show
        """
        self.loading_text.emit(message)

    def _show_splash(self, visible: bool):
        """
        Shows/hides splash.

        Parameters:
        - :param visible: `True` to show splash, `False` to hide it
        """
        if visible:
            self.tabber.setCurrentIndex(1)
        else:
            self.tabber.setCurrentIndex(0)

    def _init_progress(self, message: str, total_progress: int):
        """
        Makes progress label ready.

        Parameters:
        - :param message: progress message
        - :param total_progress: total number of steps
        """
        self._progress_text = message
        self._progress_total = total_progress
        self._progress_current = 0
        self.progress_label.setText(
            f'{self._progress_text} ({self._progress_current:>4}/{self._progress_total:>4})')

    def _increment_progress(self):
        """
        Increments progress count by 1.
        """
        self._progress_current += 1
        self.progress_label.setText(
            f'{self._progress_text} ({self._progress_current:>4}/{self._progress_total:>4})')

    def _set_loading_text(self, message: str):
        """
        Sets loading labels' text.

        Parameters:
        - :param message: message to show
        """
        self.loading_label.setText(message)
