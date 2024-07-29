from typing import Iterable

from .widgets import CustomThread
from .constants import PRIMARY_SPECS, SECONDARY_SPECS
from .iofunc import get_ship_image

from PySide6.QtCore import Qt


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


def faction_combo_callback(self, new_faction: str):
    """
    Saves new faction to build and changes species selector choices.
    """
    self.build['captain']['faction'] = new_faction
    self.widgets.character['species'].clear()
    if new_faction != '':
        self.widgets.character['species'].addItems(('', *self.cache.species[new_faction].keys()))
    self.build['captain']['species'] = ''
    self.autosave()


def spec_combo_callback(self, primary: bool, new_spec: str):
    """
    Saves new spec to build and adjusts choices in other spec combo box.
    """
    if primary:
        self.build['captain']['primary_spec'] = new_spec
        secondary_combo = self.widgets.character['secondary']
        secondary_specs = set()
        remove_index = None
        for i in range(secondary_combo.count()):
            secondary_specs.add(secondary_combo.itemText(i))
            if secondary_combo.itemText(i) == new_spec and new_spec != '':
                remove_index = i
        if remove_index is not None:
            secondary_combo.removeItem(remove_index)
        secondary_combo.addItems((PRIMARY_SPECS | SECONDARY_SPECS) - secondary_specs)
    else:
        self.build['captain']['secondary_spec'] = new_spec
        primary_combo = self.widgets.character['primary']
        primary_specs = set()
        remove_index = None
        for i in range(primary_combo.count()):
            primary_specs.add(primary_combo.itemText(i))
            if primary_combo.itemText(i) == new_spec and new_spec != '':
                remove_index = i
        if remove_index is not None:
            primary_combo.removeItem(remove_index)
        primary_combo.addItems(PRIMARY_SPECS - primary_specs)
    self.autosave()


def set_build_item(self, dictionary, key, value):
    """
    Assigns value to dictionary item. Triggers autosave.

    Parameters:
    - :param dictionary: dictionary to use key on
    - :param key: key for the dictionary
    - :param value: value to be assigned to the item
    """
    dictionary[key] = value
    self.autosave()


def elite_callback(self, state: bool):
    """
    Saves new state and updates build.

    Parameters:
    - :param state: new state of the checkbox
    """
    if state == Qt.CheckState.Checked:
        self.build['captain']['elite'] = True
    else:
        self.build['captain']['elite'] = False
    self.autosave()


def picker(
        self, items: Iterable, environment: str, build_key: str, build_subkey: int,
        equipment: bool = False):
    """
    opens dialog to select item, stores it to build and updates item button
    """
    size = (self.window.width() * 0.2, self.window.height() * 0.9)
    pos = (self.window.x() + size[0] / 4, self.window.y() + size[1] / 18)
    new_item = self.picker_window.pick_item(size, pos, items, equipment)
    if new_item is not None:
        if environment == 'space':
            widget_storage = self.widgets.space_build
        else:
            widget_storage = self.widgets.ground_build
        item_image = self.cache.images[new_item['item']]
        if equipment:
            self.build[environment][build_key][build_subkey] = new_item
            overlay = getattr(self.cache.overlays, new_item['rarity'].lower().replace(' ', ''))
            widget_storage[build_key][build_subkey].set_item_overlay(item_image, overlay)
        else:
            self.build[environment][build_key][build_subkey] = {'item': new_item['item']}
            widget_storage[build_key][build_subkey].set_item(item_image)
        self.autosave()


def slot_ship(self, new_ship: str):
    """
    Updates UI to reflect new ship.
    """
    ship_data = self.cache.ships[new_ship]
    image_name = ship_data['image'].replace(' ', '_')
    image_thread = CustomThread(self.window, get_ship_image, self, new_ship, image_name)
    image_thread.result.connect(lambda img: self.widgets.ship['image'].set_pixmap(*img))
    image_thread.start()
