import os
from typing import Iterable

from .buildupdater import (
        align_space_frame, clear_ship, clear_traits, slot_equipment_item,
        slot_trait_item)
from .constants import PRIMARY_SPECS, SECONDARY_SPECS, SHIP_TEMPLATE
from .datafunctions import load_build_file
from .iofunc import browse_path, get_ship_image, sanitize_file_name, store_json
from .textedit import get_tooltip
from .widgets import CustomThread

from PySide6.QtCore import Qt


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


def set_build_item(self, dictionary, key, value, autosave: bool = True):
    """
    Assigns value to dictionary item. Triggers autosave.

    Parameters:
    - :param dictionary: dictionary to use key on
    - :param key: key for the dictionary
    - :param value: value to be assigned to the item
    - :param autosave: set to False to disable autosave
    """
    dictionary[key] = value
    if autosave:
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


def get_boff_abilities(
        self, environment: str, rank: int, boff_id: int) -> set:
    """
    Returns list of boff abilities appropriate for the station described by the parameters.

    Parameters:
    - :param environment: space/ground
    - :param rank: rank of the ability slot
    - :param boff_id: id of the boff
    """
    profession, specialization = self.build[environment]['boff_specs'][boff_id]
    abilities = self.cache.boff_abilities[environment][profession][rank].keys()
    if specialization != '':
        abilities |= self.cache.boff_abilities[environment][specialization][rank].keys()
    return abilities


def picker(
        self, items: Iterable, environment: str, build_key: str, build_subkey: int,
        equipment: bool = False, boff_id=None):
    """
    opens dialog to select item, stores it to build and updates item button

    Parameters:
    - :param items: iterable of items available to pick from
    - :param environment: space or ground
    - :param build_key: key to self.build[environment]; for storing picked item
    - :param build_subkey: index of the item within its build_key (category)
    - :param equipment: set to True to show rarity, mark, and modifier selector (optional)
    - :param boff_id: id of the boff; only set when picking boff abilities! (optional)
    """
    if build_key == 'boffs':
        items = get_boff_abilities(self, environment, build_subkey, boff_id)
    new_item = self.picker_window.pick_item(items, equipment)
    if new_item is not None:
        widget_storage = self.widgets.build[environment]
        item_image = self.cache.images[new_item['item']]
        if equipment:
            slot_equipment_item(self, new_item, environment, build_key, build_subkey)
        else:
            if boff_id is None:
                slot_trait_item(
                        self, {'item': new_item['item']}, environment, build_key, build_subkey)
            elif build_key == 'boffs':
                self.build[environment]['boffs'][boff_id][build_subkey] = {
                    'item': new_item['item']
                }
                widget_storage['boffs'][boff_id][build_subkey].set_item(item_image)
                widget_storage['boffs'][boff_id][build_subkey].tooltip = get_tooltip(
                        self, new_item, 'boff')
        self.autosave()


def boff_profession_callback(self, boff_id: int, new_spec: str):
    """
    updates build with newly assigned profession; clears abilities of the old profession
    """
    # to prevent overwriting the build while loading
    if self.building:
        return
    if ' / ' in new_spec:
        profession, specialization = new_spec.split(' / ')
        for ability_num, ability in enumerate(self.build['space']['boffs'][boff_id]):
            if ability is not None and ability != '':
                # Lt. Commander rank contains all abilities
                if ability['item'] not in self.cache.boff_abilities['space'][specialization][2]:
                    self.build['space']['boffs'][boff_id][ability_num] = ''
                    self.widgets.build['space']['boffs'][boff_id][ability_num].clear()
    else:
        profession = new_spec
        specialization = ''
        for ability_num, ability in enumerate(self.build['space']['boffs'][boff_id]):
            if ability is not None and ability != '':
                self.build['space']['boffs'][boff_id][ability_num] = ''
                self.widgets.build['space']['boffs'][boff_id][ability_num].clear()
    self.build['space']['boff_specs'][boff_id] = [profession, specialization]
    self.autosave()


def select_ship(self):
    """
    Opens ship picker and updates UI to reflect new ship.
    """
    new_ship = self.ship_selector_window.pick_ship()
    if new_ship is None:
        return
    self.building = True
    self.widgets.ship['button'].setText(new_ship)
    ship_data = self.cache.ships[new_ship]
    image_thread = CustomThread(self.window, get_ship_image, self, ship_data['image'])
    image_thread.result.connect(lambda img: self.widgets.ship['image'].set_pixmap(*img))
    image_thread.start()
    tier = ship_data['tier']
    self.widgets.ship['tier'].clear()
    if tier == 6:
        self.widgets.ship['tier'].addItems(('T6', 'T6-X', 'T6-X2'))
    elif tier == 5:
        self.widgets.ship['tier'].addItems(('T5', 'T5-U', 'T5-X', 'T5-X2'))
    else:
        self.widgets.ship['tier'].addItem(f'T{tier}')
    self.build['space']['ship'] = new_ship
    self.build['space']['tier'] = f'T{tier}'
    align_space_frame(self, ship_data, clear=True)
    self.building = False
    self.autosave()


def tier_callback(self, new_tier: str):
    """
    Updates build according to new tier
    """
    self.build['space']['tier'] = new_tier
    self.autosave()


def clear_build_callback(self):
    """
    Clears current build section
    """
    current_tab = self.widgets.build_tabber.currentIndex()
    if current_tab == 0:
        clear_space_build(self)


def clear_space_build(self):
    """
    clears space build
    """
    self.building = True
    clear_ship(self)
    align_space_frame(self, SHIP_TEMPLATE, clear=True)
    clear_traits(self, 'space')
    self.building = False
    self.autosave()


def load_build_callback(self):
    """
    Loads build from file
    """
    load_path = browse_path(
            self, self.config['config_subfolders']['library'],
            'JSON file (*.json);;PNG image (*.png);;Any File (*.*)')
    if load_path != '':
        load_build_file(self, load_path)


def save_build_callback(self):
    """
    Saves build to file
    """
    if self.widgets.ship['button'].text() == '<Pick Ship>':
        proposed_filename = '(Ship Template).json'
    else:
        proposed_filename = f"({self.widgets.ship['button'].text()}).json"
    if self.widgets.ship['name'].text() != '':
        proposed_filename = f"{self.widgets.ship['name'].text()} {proposed_filename}"
    default_path = f"{self.config['config_subfolders']['library']}\\{proposed_filename}"
    save_path = browse_path(
            self, default_path,
            'JSON file (*.json);;PNG image (*.png);;Any File (*.*)', save=True)
    if save_path != '':
        filepath, filename = os.path.split(save_path)
        clean_filename = sanitize_file_name(filename)
        store_json(self.build, f'{filepath}\\{clean_filename}')
