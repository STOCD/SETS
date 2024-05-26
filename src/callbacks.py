from PySide6.QtCore import QEventLoop


def enter_splash(self):
    """
    Shows splash screen
    """
    self.widgets.loading_label.setText('Loading: ...')
    self.widgets.splash_tabber.setCurrentIndex(1)
    self.app.processEvents()
    self.app.processEvents()


def exit_splash(self):
    """
    Leaves splash screen
    """
    self.widgets.splash_tabber.setCurrentIndex(0)


def splash_text(self, new_text: str):
    """
    Updates the label of the splash screen with new text

    Parameters:
    - :param new_text: will be displayed on the splsh screen
    """
    self.widgets.loading_label.setText(new_text)
    self.app.processEvents()


def switch_main_tab(self, index):
    """
    Callback to switch between tabs. Switches build and both sidebar tabs.

    Parameters:
    - :param index: index to switch to (0: space build, 1: ground build, 2: space skills,
    3: ground skills, 4: library, 5: settings)
    """
    CHAR_TAB_MAP = {
        0: 0,
        1: 0,
        2: 0,
        3: 0,
        4: 1,
        5: 2
    }
    self.widgets.build_tabber.setCurrentIndex(index)
    self.widgets.sidebar_tabber.setCurrentIndex(index)
    self.widgets.character_tabber.setCurrentIndex(CHAR_TAB_MAP[index])
    if index == 4:
        self.widgets.sidebar.setVisible(False)
    else:
        self.widgets.sidebar.setVisible(True)
