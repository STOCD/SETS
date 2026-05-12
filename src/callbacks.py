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
