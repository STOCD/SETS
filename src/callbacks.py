from .buildupdater import (
        align_space_frame, clear_captain, clear_doffs, clear_ground_build, clear_ship, clear_traits,
        get_variable_slot_counts, set_skill_unlock_ground, set_skill_unlock_space,
        slot_equipment_item, slot_trait_item, update_equipment_cat, update_starship_traits)
from .constants import (
        EQUIPMENT_TYPES, PRIMARY_SPECS, SECONDARY_SPECS, SHIP_TEMPLATE, SKILL_POINTS_FOR_RANK,
        SPECIES, SPECIES_TRAITS)
from .datafunctions import (
        load_build_file, load_skill_tree_file, save_build_file, save_skill_tree_file)
from .iofunc import browse_path, get_ship_image, image, open_wiki_page
from .widgets import exec_in_thread

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
        self.widgets.character['species'].addItems(('', *SPECIES[new_faction]))
    self.build['captain']['species'] = ''
    self.autosave()


def species_combo_callback(self, new_species: str):
    """
    Saves new species to build and changes species trait
    """
    self.build['captain']['species'] = new_species
    if new_species == 'Alien':
        if not self.building:
            self.build['space']['traits'][10] = ''
            self.build['ground']['traits'][10] = ''
            self.build['space']['traits'][11] = ''
            self.build['ground']['traits'][11] = ''
        self.widgets.build['space']['traits'][10].show()
        self.widgets.build['ground']['traits'][10].show()
        self.widgets.build['space']['traits'][11].clear()
        self.widgets.build['ground']['traits'][11].clear()
    else:
        self.widgets.build['space']['traits'][10].hide()
        self.widgets.build['ground']['traits'][10].hide()
        self.widgets.build['space']['traits'][10].clear()
        self.widgets.build['ground']['traits'][10].clear()
        self.build['space']['traits'][10] = None
        self.build['ground']['traits'][10] = None
        new_space_trait = SPECIES_TRAITS['space'].get(new_species, '')
        new_ground_trait = SPECIES_TRAITS['ground'].get(new_species, '')
        if new_space_trait == '':
            self.widgets.build['space']['traits'][11].clear()
            self.build['space']['traits'][11] = ''
        else:
            slot_trait_item(self, {'item': new_space_trait}, 'space', 'traits', 11)
        if new_ground_trait == '':
            self.widgets.build['ground']['traits'][11].clear()
            self.build['ground']['traits'][11] = ''
        else:
            slot_trait_item(self, {'item': new_ground_trait}, 'ground', 'traits', 11)
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


def elite_callback(self, state):
    """
    Saves new state and updates build.

    Parameters:
    - :param state: new state of the checkbox
    """
    if state == Qt.CheckState.Checked:
        if not self.building:
            self.build['captain']['elite'] = True
            self.build['space']['traits'][9] = ''
            self.build['ground']['traits'][9] = ''
            self.build['ground']['kit_modules'][5] = ''
            self.build['ground']['ground_devices'][4] = ''
        self.widgets.build['space']['traits'][9].show()
        self.widgets.build['ground']['traits'][9].show()
        self.widgets.build['ground']['kit_modules'][5].show()
        self.widgets.build['ground']['ground_devices'][4].show()
    else:
        if not self.building:
            self.build['captain']['elite'] = False
            self.build['space']['traits'][9] = None
            self.build['ground']['traits'][9] = None
            self.build['ground']['kit_modules'][5] = None
            self.build['ground']['ground_devices'][4] = None
        self.widgets.build['space']['traits'][9].hide()
        self.widgets.build['space']['traits'][9].clear()
        self.widgets.build['ground']['traits'][9].hide()
        self.widgets.build['ground']['traits'][9].clear()
        self.widgets.build['ground']['kit_modules'][5].hide()
        self.widgets.build['ground']['kit_modules'][5].clear()
        self.widgets.build['ground']['ground_devices'][4].hide()
        self.widgets.build['ground']['ground_devices'][4].clear()
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
    if environment == 'space':
        profession, specialization = self.build['space']['boff_specs'][boff_id]
    else:
        profession = self.build['ground']['boff_profs'][boff_id]
        specialization = self.build['ground']['boff_specs'][boff_id]
    abilities = self.cache.boff_abilities[environment][profession][rank].keys()
    if specialization != '':
        abilities |= self.cache.boff_abilities[environment][specialization][rank].keys()
    return abilities


def picker(
        self, environment: str, build_key: str, build_subkey: int, equipment: bool = False,
        boff_id=None):
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
    modifiers = {}
    if equipment:
        items = self.cache.equipment[build_key].keys()
        modifiers = self.cache.modifiers[build_key]
    elif build_key == 'boffs':
        items = get_boff_abilities(self, environment, build_subkey, boff_id)
    elif build_key == 'traits':
        items = self.cache.traits[environment]['personal'].keys()
    elif build_key == 'starship_traits':
        items = self.cache.starship_traits.keys()
    elif build_key == 'rep_traits':
        items = self.cache.traits[environment]['rep'].keys()
    elif build_key == 'active_rep_traits':
        items = self.cache.traits[environment]['active_rep'].keys()
    else:
        items = []
    new_item = self.picker_window.pick_item(items, equipment, modifiers)
    if new_item is not None:
        widget_storage = self.widgets.build[environment]
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
                item_image = image(self, new_item['item'])
                widget_storage['boffs'][boff_id][build_subkey].set_item(item_image)
                widget_storage['boffs'][boff_id][build_subkey].tooltip = (
                        self.cache.boff_abilities['all'][new_item['item']])
        self.autosave()


def boff_profession_callback_space(self, boff_id: int, new_spec: str):
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


def boff_label_callback_ground(self, boff_id: int, type_: str, new_text: str):
    """
    updates build with newly assigned profession or specialization; clears invalid abilities

    Parameters:
    - :param boff_id: number of the boff station
    - :param type_: "boff_profs" / "boff_specs"
    - :param new_text: new profession / specialization
    """
    if self.building:
        return
    self.build['ground'][type_][boff_id] = new_text
    other_type = 'boff_profs' if type_ == 'boff_specs' else 'boff_specs'
    other_text = self.build['ground'][other_type][boff_id]
    for ability_num, ability in enumerate(self.build['ground']['boffs'][boff_id]):
        if ability is not None and ability != '':
            # Lt. Commander rank contains all abilities
            if (ability['item'] not in self.cache.boff_abilities['ground'][new_text][2]
                    and ability['item'] not in self.cache.boff_abilities['ground'][other_text][2]):
                self.build['ground']['boffs'][boff_id][ability_num] = ''
                self.widgets.build['ground']['boffs'][boff_id][ability_num].clear()
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
    exec_in_thread(
            self, get_ship_image, self, ship_data['image'],
            result=lambda img: self.widgets.ship['image'].set_image(*img))
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
    if self.building:
        return
    self.build['space']['tier'] = new_tier
    ship_name = self.build['space']['ship']
    if ship_name == '<Pick Ship>':
        ship_data = SHIP_TEMPLATE
    else:
        ship_data = self.cache.ships[ship_name]
    uni, eng, sci, tac, devices, starship_traits = get_variable_slot_counts(self, ship_data)
    update_equipment_cat(self, 'uni_consoles', uni, can_hide=True)
    update_equipment_cat(self, 'eng_consoles', eng)
    update_equipment_cat(self, 'sci_consoles', sci)
    update_equipment_cat(self, 'tac_consoles', tac)
    update_equipment_cat(self, 'devices', devices)
    update_starship_traits(self, starship_traits)
    self.autosave()


def clear_build_callback(self):
    """
    Clears current build section
    """
    current_tab = self.widgets.build_tabber.currentIndex()
    self.building = True
    if current_tab == 0:
        clear_space_build(self)
    elif current_tab == 1:
        clear_ground_build(self)
    elif current_tab == 2:
        clear_space_skills(self)
    elif current_tab == 3:
        clear_ground_skills(self)
    self.building = False


def clear_space_build(self):
    """
    clears space build
    """
    self.building = True
    clear_ship(self)
    align_space_frame(self, SHIP_TEMPLATE, clear=True)
    clear_traits(self, 'space')
    clear_doffs(self, 'space')
    self.building = False
    self.autosave()


def clear_space_skills(self):
    """
    resets space skill tree
    """
    self.widgets.build['skill_desc']['space'].clear()
    self.build['skill_desc']['space'] = ''
    self.build['space_skills'] = {
        'eng': [False] * 30,
        'sci': [False] * 30,
        'tac': [False] * 30
    }
    self.cache.skills['space_points_total'] = 0
    self.cache.skills['space_points_eng'] = 0
    self.widgets.skill_counts_space['eng'].setText('0')
    self.cache.skills['space_points_sci'] = 0
    self.widgets.skill_counts_space['sci'].setText('0')
    self.cache.skills['space_points_tac'] = 0
    self.widgets.skill_counts_space['tac'].setText('0')
    self.cache.skills['space_points_rank'] = [0] * 5
    for career in ('eng', 'sci', 'tac'):
        for skill_button in self.widgets.build['space_skills'][career]:
            skill_button.clear_overlay()
        self.build['skill_unlocks'][career] = [None] * 5
        for bar_segment in self.widgets.skill_bonus_bars[career]:
            bar_segment.setChecked(False)
        for unlock_button in self.widgets.build['skill_unlocks'][career]:
            unlock_button.clear()


def clear_ground_skills(self):
    """
    resets ground skill tree
    """
    self.widgets.build['skill_desc']['ground'].clear()
    self.build['skill_desc']['ground'] = ''
    self.build['ground_skills'] = [
        [False] * 6,
        [False] * 6,
        [False] * 4,
        [False] * 4
    ]
    self.build['skill_unlocks']['ground'] = [None] * 5
    self.cache.skills['ground_points_total'] = 0
    self.widgets.skill_count_ground.setText('0')
    for skill_subtree in self.widgets.build['ground_skills']:
        for skill_button in skill_subtree:
            skill_button.clear_overlay()
    for unlock_button in self.widgets.build['skill_unlocks']['ground']:
        unlock_button.clear()
    for bar_segment in self.widgets.skill_bonus_bars['ground']:
        bar_segment.setChecked(False)


def clear_all(self):
    """
    Clears space and ground build, skills and captain info
    """
    self.building = True
    clear_space_build(self)
    clear_ground_build(self)
    clear_captain(self)
    clear_space_skills(self)
    clear_ground_skills(self)
    self.building = False
    self.autosave()


def set_ui_scale_setting(self, new_value: int):
    """
    Calculates new_value / 50 and stores it to settings.

    Parameters:
    - :param new_value: 50 times the ui scale percentage
    """
    setting_value = f'{new_value / 50:.2f}'
    self.settings.setValue('ui_scale', setting_value)
    return setting_value


def load_build_callback(self):
    """
    Loads build from file
    """
    load_path = browse_path(
            self, self.config['config_subfolders']['library'],
            'SETS Files (*.json *.png);;JSON file (*.json);;PNG image (*.png);;Any File (*.*)')
    if load_path != '':
        load_build_file(self, load_path)


def load_skills_callback(self):
    """
    Loads skills from file
    """
    load_path = browse_path(
            self, self.config['config_subfolders']['library'],
            'SETS Files (*.json *.png);;JSON file (*.json);;PNG image (*.png);;Any File (*.*)')
    if load_path != '':
        load_skill_tree_file(self, load_path)


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
        save_build_file(self, save_path)


def save_skills_callback(self):
    """
    Save skills to file
    """
    default_path = f"{self.config['config_subfolders']['library']}\\Skill Tree.json"
    save_path = browse_path(
            self, default_path,
            'JSON file (*.json);;PNG image (*.png);;Any File (*.*)', save=True)
    if save_path != '':
        save_skill_tree_file(self, save_path)


def ship_info_callback(self):
    """
    Opens wiki page of ship if ship is slotted
    """
    if self.build['space']['ship'] != '<Pick Ship>':
        open_wiki_page(self.cache.ships[self.build['space']['ship']]['Page'])


def open_wiki_context(self):
    """
    Opens wiki page of item in `self.context_menu.clicked_slot`.
    """
    slot = self.context_menu.clicked_slot
    if self.context_menu.clicked_boff_station != -1:
        boff_id = self.context_menu.clicked_boff_station
        item = self.build[slot.environment][slot.type][boff_id][slot.index]
        if item is not None and item != '':
            open_wiki_page(f"Ability: {item['item']}")
        return
    item = self.build[slot.environment][slot.type][slot.index]
    if item is None or item == '':
        return
    if 'traits' in slot.type:
        open_wiki_page(f"Trait: {item['item']}")
    else:
        open_wiki_page(f"{self.cache.equipment[slot.type][item['item']]['Page']}#{item['item']}")


def copy_equipment_item(self):
    """
    Copies equipment item clicked on.
    """
    slot = self.context_menu.clicked_slot
    item = self.build[slot.environment][slot.type][slot.index]
    if item is None or item == '':
        self.context_menu.copied_item = None
        self.context_menu.copied_item_type = None
    else:
        self.context_menu.copied_item = item
        item_type = EQUIPMENT_TYPES[self.cache.equipment[slot.type][item['item']]['type']]
        self.context_menu.copied_item_type = item_type


def paste_equipment_item(self):
    """
    Pastes copied item into clicked slot if slot types are compatible
    """
    slot = self.context_menu.clicked_slot
    copied_type = self.context_menu.copied_item_type
    if slot.type == copied_type:
        slot_equipment_item(
                self, self.context_menu.copied_item, slot.environment, slot.type, slot.index)
    elif copied_type == 'ship_weapon' and (
            slot.type == 'fore_weapons' or slot.type == 'aft_weapons'):
        slot_equipment_item(
                self, self.context_menu.copied_item, slot.environment, slot.type, slot.index)
    elif (copied_type == 'uni_consoles' and 'consoles' in slot.type
            or slot.type == 'uni_consoles' and 'consoles' in copied_type):
        slot_equipment_item(
                self, self.context_menu.copied_item, slot.environment, slot.type, slot.index)
    self.autosave()


def clear_slot(self):
    """
    Clears slot that was rightclicked on.
    """
    slot = self.context_menu.clicked_slot
    if self.context_menu.clicked_boff_station == -1:
        self.widgets.build[slot.environment][slot.type][slot.index].clear()
        self.build[slot.environment][slot.type][slot.index] = ''
    else:
        boff_id = self.context_menu.clicked_boff_station
        self.widgets.build[slot.environment][slot.type][boff_id][slot.index].clear()
        self.build[slot.environment][slot.type][boff_id][slot.index] = ''
    self.autosave()


def edit_equipment_item(self):
    """
    Edit mark, modifiers and rarity of rightclicked item.
    """
    slot = self.context_menu.clicked_slot
    item = self.build[slot.environment][slot.type][slot.index]
    modifiers = self.cache.modifiers[slot.type]
    new_item = self.edit_window.edit_item(item, modifiers)
    if new_item is not None:
        slot_equipment_item(self, new_item, slot.environment, slot.type, slot.index)
        self.autosave()


def doff_spec_callback(self, new_spec: str, environment: str, doff_id: int):
    """
    Callback for duty officer specialization combobox.

    Parameters:
    - :param new_spec: selected specialization
    - :param environment: "space" / "ground"
    - :param doff_id: index of the doff
    """
    if self.building:
        return
    self.build[environment]['doffs_spec'][doff_id] = new_spec
    self.build[environment]['doffs_variant'][doff_id] = ''
    self.widgets.build[environment]['doffs_variant'][doff_id].clear()
    if new_spec != '':
        variants = getattr(self.cache, f'{environment}_doffs')[new_spec].keys()
        self.widgets.build[environment]['doffs_variant'][doff_id].addItems({''} | variants)
    self.autosave()


def doff_variant_callback(self, new_variant: str, environment: str, doff_id: int):
    """
    Callback for duty officer variant combobox.

    Parameters:
    - :param new_variant: selected variant
    - :param environment: "space" / "ground"
    - :param doff_id: index of the doff
    """
    if self.building:
        return
    self.build[environment]['doffs_variant'][doff_id] = new_variant
    self.autosave()


def toggle_space_skill(self, current_state: bool, career: str, skill_id: int):
    """
    Activates space skill if it's deactivated, deactivates skill if it's activated.

    Parameters:
    - :param current_state: state of the button before toggling
    - :param career: "eng" / "tac" / "sci"
    - :param skill_id: id of the skill node (index in self.build and self.widgets.build)
    """
    if current_state:
        self.widgets.build['space_skills'][career][skill_id].clear_overlay()
        self.build['space_skills'][career][skill_id] = False
        self.cache.skills['space_points_total'] -= 1
        self.cache.skills[f'space_points_{career}'] -= 1
        self.cache.skills['space_points_rank'][int(skill_id / 6)] -= 1
        segment_index = self.cache.skills[f'space_points_{career}']
        if segment_index < 24:
            self.widgets.skill_bonus_bars[career][segment_index].setChecked(False)
            if segment_index % 5 == 4:
                button_index = (segment_index - 4) // 5
                set_skill_unlock_space(self, career, button_index, None)
            elif segment_index == 23:
                set_skill_unlock_space(self, career, 4, None)
        elif 25 <= segment_index <= 26:
            set_skill_unlock_space(self, career, 4, 0, segment_index)
    else:
        self.widgets.build['space_skills'][career][skill_id].set_overlay(self.cache.overlays.check)
        self.build['space_skills'][career][skill_id] = True
        self.cache.skills['space_points_total'] += 1
        self.cache.skills[f'space_points_{career}'] += 1
        self.cache.skills['space_points_rank'][int(skill_id / 6)] += 1
        segment_index = self.cache.skills[f'space_points_{career}'] - 1
        if segment_index < 24:
            self.widgets.skill_bonus_bars[career][segment_index].setChecked(True)
            if segment_index % 5 == 4:
                button_index = (segment_index - 4) // 5
                set_skill_unlock_space(self, career, button_index, 0)
            elif segment_index == 23:
                set_skill_unlock_space(self, career, 4, -1, 24)
        elif 24 <= segment_index <= 25:
            set_skill_unlock_space(self, career, 4, 0, segment_index + 1)
        elif segment_index == 26:
            set_skill_unlock_space(self, career, 4, 3, 27)
    self.widgets.skill_counts_space[career].setText(
            str(self.cache.skills[f'space_points_{career}']))
    self.autosave()


def skill_unlock_callback(self, bar: str, unlock_id: int):
    """
    Callback for skill unlock buttons

    Parameters:
    - :param bar: "eng" / "sci" / "tac" / "ground"
    - :param unlock_id: index of the unlock button
    """
    current_state = self.build['skill_unlocks'][bar][unlock_id]
    if current_state is None:
        return
    if bar == 'ground':
        if current_state == 0:
            set_skill_unlock_ground(self, unlock_id, 1)
        elif current_state == 1:
            set_skill_unlock_ground(self, unlock_id, 0)
        self.autosave()
    else:
        if unlock_id < 4:
            if current_state == 0:
                set_skill_unlock_space(self, bar, unlock_id, 1)
            elif current_state == 1:
                set_skill_unlock_space(self, bar, unlock_id, 0)
            self.autosave()
        else:
            points_spent = self.cache.skills[f'space_points_{bar}']
            if 25 <= points_spent <= 26:
                set_skill_unlock_space(self, bar, 4, (current_state + 1) % 3, points_spent)
                self.autosave()


def toggle_ground_skill(self, current_state: bool, skill_group: int, skill_id: int):
    """
    Activates ground skill if it's deactivated, deactivates skill if it's activated.

    Parameters:
    - :param current_state: state of the button before toggling
    - :param skill_group: number [0, 3] identifying the skill group
    - :param skill_id: index of the skill within the group
    """
    if current_state:
        self.widgets.build['ground_skills'][skill_group][skill_id].clear_overlay()
        self.build['ground_skills'][skill_group][skill_id] = False
        self.cache.skills['ground_points_total'] -= 1
        segment_index = self.cache.skills['ground_points_total']
        self.widgets.skill_bonus_bars['ground'][segment_index].setChecked(False)
        if segment_index % 2 == 1:
            button_index = (segment_index - 1) // 2
            set_skill_unlock_ground(self, button_index, None)
    else:
        self.widgets.build['ground_skills'][skill_group][skill_id].set_overlay(
                self.cache.overlays.check)
        self.build['ground_skills'][skill_group][skill_id] = True
        self.cache.skills['ground_points_total'] += 1
        segment_index = self.cache.skills['ground_points_total'] - 1
        self.widgets.skill_bonus_bars['ground'][segment_index].setChecked(True)
        if segment_index % 2 == 1:
            button_index = (segment_index - 1) // 2
            set_skill_unlock_ground(self, button_index, 0)
    self.widgets.skill_count_ground.setText(str(self.cache.skills['ground_points_total']))
    self.autosave()


def skill_callback_space(self, career: str, skill_id: int, grouping: str):
    """
    Callback for space skill node

    Parameters:
    - :param career: "eng" / "tac" / "sci"
    - :param skill_id: id of the skill node (index in self.build and self.widgets.build)
    - :param grouping: type of skill grouping: "column" / "pair+1" / "separate"
    """
    skill_active = self.build['space_skills'][career][skill_id]
    skill_lvl = skill_id % 3
    skill_rank = int(skill_id / 6)
    if skill_active:  # check for valid deselect
        if (skill_lvl == 2
                or grouping != 'column' and skill_lvl == 1
                or not self.build['space_skills'][career][skill_id + 1]):
            skill_count = sum(self.cache.skills['space_points_rank'][:skill_rank + 1])
            for rank_offset, points_required in enumerate(SKILL_POINTS_FOR_RANK[skill_rank + 1:]):
                if (skill_count - 1 < points_required
                        and self.cache.skills['space_points_total'] - skill_count > 0):
                    return
                skill_count += self.cache.skills['space_points_rank'][skill_rank + rank_offset + 1]
            toggle_space_skill(self, skill_active, career, skill_id)
    else:  # check for valid select
        if 46 > self.cache.skills['space_points_total'] >= SKILL_POINTS_FOR_RANK[skill_rank]:
            if skill_lvl == 0:
                toggle_space_skill(self, skill_active, career, skill_id)
            elif grouping == 'column' and self.build['space_skills'][career][skill_id - 1]:
                toggle_space_skill(self, skill_active, career, skill_id)
            elif grouping != 'column' and self.build['space_skills'][career][skill_id - skill_lvl]:
                toggle_space_skill(self, skill_active, career, skill_id)


def skill_callback_ground(self, skill_group: int, skill_id: int):
    """
    Callback for ground skill node

    Parameters:
    - :param skill_group: number [0, 3] identifying the skill group
    - :param skill_id: index of the skill within the group
    """
    skill_active = self.build['ground_skills'][skill_group][skill_id]
    if skill_active:  # check for valid deselect
        if skill_id == 0 and (
                self.build['ground_skills'][skill_group][1]
                or self.build['ground_skills'][skill_group][2]
                or skill_group <= 1 and self.build['ground_skills'][skill_group][4]):
            return
        elif skill_id % 2 == 0 and self.build['ground_skills'][skill_group][skill_id + 1]:
            return
        toggle_ground_skill(self, skill_active, skill_group, skill_id)
    else:  # check for valid select
        if self.cache.skills['ground_points_total'] < 10:
            if skill_id % 2 == 1 and self.build['ground_skills'][skill_group][skill_id - 1]:
                toggle_ground_skill(self, skill_active, skill_group, skill_id)
            elif skill_id == 0:
                toggle_ground_skill(self, skill_active, skill_group, skill_id)
            elif (skill_id == 2 or skill_id == 4) and self.build['ground_skills'][skill_group][0]:
                toggle_ground_skill(self, skill_active, skill_group, skill_id)
