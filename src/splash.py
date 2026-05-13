from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QLabel, QTabWidget


class SplashScreen(QObject):
    """Manages splash screen"""

    show: Signal = Signal(bool)
    loading_text: Signal = Signal(str)
    progress_visible: Signal = Signal(bool)
    progress_init: Signal = Signal(int)
    progress_step: Signal = Signal()

    def __init__(self):
        super().__init__()
        self.loading_label: QLabel
        self.progress_label: QLabel
        self.tabber: QTabWidget
        self._progress_total: int = 0
        self._progress_current: int = 0
        self.show.connect(self._show_splash)
        self.loading_text.connect(self._set_loading_text)
        self.progress_visible.connect(self._show_progress)
        self.progress_init.connect(self._init_progress)
        self.progress_step.connect(self._increment_progress)

    def show_splash(self, visible: bool):
        """
        Shows/hides splash.

        Parameters:
        - :param visible: `True` to show splash, `False` to hide it
        """
        self.show.emit(visible)

    def init_progress(self, total_progress: int):
        """
        Makes progress label ready.

        Parameters:
        - :param total_progress: total number of steps
        """
        self.progress_init.emit(total_progress)

    def increment_progress(self):
        """
        Increments progress count by 1.
        """
        self.progress_step.emit()

    def show_progress(self, visible: bool):
        """
        Shows/hides progress label.

        Parameters:
        - :param visible: `True` to show progress label, `False` to hide it
        """
        self.progress_visible.emit(visible)

    def set_loading_text(self, message: str):
        """
        Sets loading labels' text.

        Parameters:
        - :param message: message to show
        """
        self.loading_text.emit(message)

    @Slot(bool)
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

    @Slot(int)
    def _init_progress(self, total_progress: int):
        """
        Makes progress label ready.

        Parameters:
        - :param total_progress: total number of steps
        """
        self._progress_total = total_progress
        self._progress_current = 0
        self.progress_label.setText(
            f'({self._progress_current:>4}/{self._progress_total:>4})')
        self.progress_label.show()

    @Slot()
    def _increment_progress(self):
        """
        Increments progress count by 1.
        """
        self._progress_current += 1
        self.progress_label.setText(
            f'({self._progress_current:>4}/{self._progress_total:>4})')

    @Slot(bool)
    def _show_progress(self, visible: bool):
        """
        Shows/hides progress label.

        Parameters:
        - :param visible: `True` to show progress label, `False` to hide it
        """
        self.progress_label.setVisible(visible)

    @Slot(str)
    def _set_loading_text(self, message: str):
        """
        Sets loading labels' text.

        Parameters:
        - :param message: message to show
        """
        self.loading_label.setText(message)
