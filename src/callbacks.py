from .buildupdater import (
        align_space_frame, clear_captain, clear_doffs, clear_ground_build, clear_ship, clear_traits,
        get_variable_slot_counts, set_skill_unlock_ground, set_skill_unlock_space,
        slot_equipment_item, slot_trait_item, update_equipment_cat, update_starship_traits)
from .constants import EQUIPMENT_TYPES, SHIP_TEMPLATE, SKILL_POINTS_FOR_RANK
from .datafunctions import (
        load_build_file, load_skill_tree_file, save_build_file, save_skill_tree_file)
from .iofunc import browse_path, image, open_wiki_page
from .widgets import exec_in_thread

from PySide6.QtCore import Qt


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
        if specialization == 'Temporal Operative':
            specialization = 'Temporal'
    else:
        profession = self.build['ground']['boff_profs'][boff_id]
        specialization = self.build['ground']['boff_specs'][boff_id]
    abilities = self.cache.boff_abilities[environment][profession][rank]
    if specialization != '':
        abilities = abilities + self.cache.boff_abilities[environment][specialization][rank]
    return abilities


def picker(
        self, environment: str, build_key: str, build_subkey: int, button, equipment: bool = False,
        boff_id=None):
    """
    opens dialog to select item, stores it to build and updates item button

    Parameters:
    - :param items: iterable of items available to pick from
    - :param environment: space or ground
    - :param build_key: key to self.build[environment]; for storing picked item
    - :param build_subkey: index of the item within its build_key (category)
    - :param button: reference to the button clicked
    - :param equipment: set to True to show rarity, mark, and modifier selector (optional)
    - :param boff_id: id of the boff; only set when picking boff abilities! (optional)
    """
    modifiers = {}
    image_suffix = ''
    if equipment:
        items = self.cache.equipment[build_key].keys()
        modifiers = self.cache.modifiers[build_key]
    elif build_key == 'boffs':
        items = get_boff_abilities(self, environment, build_subkey, boff_id)
    elif build_key == 'traits':
        items = self.cache.traits[environment]['traits'].keys()
        image_suffix = f'__{environment}__{build_key}'
    elif build_key == 'starship_traits':
        items = self.cache.starship_traits.keys()
        image_suffix = '__space__starship_traits'
    elif build_key == 'rep_traits':
        items = self.cache.traits[environment]['rep_traits'].keys()
        image_suffix = f'__{environment}__{build_key}'
    elif build_key == 'active_rep_traits':
        items = self.cache.traits[environment]['active_rep_traits'].keys()
        image_suffix = f'__{environment}__{build_key}'
    else:
        items = []
    if self.settings.picker_relative == 1:
        pos = button.parent().mapToGlobal(button.pos())
    else:
        pos = None
    new_item = self.picker_window.pick_item(items, pos, equipment, modifiers, image_suffix)
    if new_item is not None:
        widget_storage = self.widgets.build[environment]
        if equipment:
            if 'consoles' in build_key:
                type_ = EQUIPMENT_TYPES[self.cache.equipment[build_key][new_item['item']]['type']]
                for i, mod in enumerate(new_item['modifiers']):
                    if mod not in self.cache.modifiers[type_]:
                        new_item['modifiers'][i] = ''
            slot_equipment_item(self, new_item, environment, build_key, build_subkey)
        else:
            if boff_id is None:
                slot_trait_item(
                        self, {'item': new_item['item']}, environment, build_key, build_subkey)
            elif build_key == 'boffs':
                ability_name, _, ability_rank = new_item['item'].rpartition(' ')
                self.build[environment]['boffs'][boff_id][build_subkey] = {
                    'item': ability_name,
                    'rank': ability_rank
                }
                widget_storage['boffs'][boff_id][build_subkey].set_item(image(self, ability_name))
                widget_storage['boffs'][boff_id][build_subkey].tooltip = (
                        self.cache.boff_abilities['all'][ability_name][ability_rank])
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
            self, self.images.get_ship_image, ship_data['image'][5:],
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
    if ship_data['equipcannons'] == 'yes':
        self.widgets.ship['dc'].show()
    else:
        self.widgets.ship['dc'].hide()
    align_space_frame(self, ship_data, clear=True)
    self.building = False
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
            skill_button.highlight = False
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
            skill_button.highlight = False
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


def load_build_callback(self):
    """
    Loads build from file
    """
    load_path = browse_path(
            self, str(self.config.config_subfolders['library']),
            'SETS Files (*.json *.png);;JSON file (*.json);;PNG image (*.png);;Any File (*.*)')
    if load_path != '':
        load_build_file(self, load_path)


def load_skills_callback(self):
    """
    Loads skills from file
    """
    load_path = browse_path(
            self, str(self.config.config_subfolders['library']),
            'SETS Files (*.json *.png);;JSON file (*.json);;PNG image (*.png);;Any File (*.*)')
    if load_path != '':
        load_skill_tree_file(self, load_path)


def save_build_callback(self):
    """
    Saves build to file
    """
    if self.widgets.ship['button'].text() == '<Pick Ship>':
        proposed_filename = '(Ship Template)'
    else:
        proposed_filename = f"({self.widgets.ship['button'].text()})"
    if self.widgets.ship['name'].text() != '':
        proposed_filename = f"{self.widgets.ship['name'].text()} {proposed_filename}"
    default_path = str(self.config.config_subfolders['library'] / proposed_filename)
    if self.settings.default_save_format == 'PNG':
        file_types = 'PNG image (*.png);;JSON file (*.json);;Any File (*.*)'
    else:
        file_types = 'JSON file (*.json);;PNG image (*.png);;Any File (*.*)'
    save_path = browse_path(self, default_path, file_types, save=True)
    if save_path != '':
        save_build_file(self, save_path)


def save_skills_callback(self):
    """
    Save skills to file
    """
    default_path = str(self.config.config_subfolders['library'] / 'Skill Tree')
    if self.settings.default_save_format == 'PNG':
        file_types = 'PNG image (*.png);;JSON file (*.json);;Any File (*.*)'
    else:
        file_types = 'JSON file (*.json);;PNG image (*.png);;Any File (*.*)'
    save_path = browse_path(self, default_path, file_types, save=True)
    if save_path != '':
        save_skill_tree_file(self, save_path)
