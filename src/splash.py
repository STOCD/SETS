def enter_splash(self):
    """
    Shows splash screen
    """
    self.widgets.loading_label.setText('Loading: ...')
    self.widgets.splash_tabber.setCurrentIndex(1)


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
