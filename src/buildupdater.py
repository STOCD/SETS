from PySide6.QtCore import Qt

from .constants import BOFF_RANKS, SHIP_TEMPLATE
from .iofunc import get_ship_image, image
from .textedit import (
        add_equipment_tooltip_header, get_tooltip, get_skill_unlock_tooltip_ground,
        get_skill_unlock_tooltip_space, get_ultimate_skill_unlock_tooltip)
from .widgets import exec_in_thread


def load_build(self):
    """
    Updates UI to show the build currently in self.build
    """
    self.building = True
    # ship section
    ship = self.build['space']['ship']
    if ship == '<Pick Ship>' or ship == '':
        ship_data = SHIP_TEMPLATE
        self.widgets.ship['button'].setText('<Pick Ship>')
        self.widgets.ship['tier'].clear()
        self.widgets.ship['image'].set_image(self.cache.empty_image)
        self.widgets.ship['dc'].hide()
    else:
        self.widgets.ship['button'].setText(ship)
        ship_data = self.cache.ships[ship]
        exec_in_thread(
                self, get_ship_image, self, ship_data['image'],
                result=lambda img: self.widgets.ship['image'].set_image(*img))
        tier = self.build['space']['tier']
        ship_tier = ship_data['tier']
        self.widgets.ship['tier'].clear()
        if ship_tier == 6:
            self.widgets.ship['tier'].addItems(('T6', 'T6-X', 'T6-X2'))
        elif ship_tier == 5:
            self.widgets.ship['tier'].addItems(('T5', 'T5-U', 'T5-X', 'T5-X2'))
        else:
            self.widgets.ship['tier'].addItem(f'T{ship_tier}')
        self.widgets.ship['tier'].setCurrentText(tier)
        if ship_data['equipcannons'] == 'yes':
            self.widgets.ship['dc'].show()
        else:
            self.widgets.ship['dc'].hide()
    self.widgets.ship['name'].setText(self.build['space']['ship_name'])
    self.widgets.ship['desc'].setPlainText(self.build['space']['ship_desc'])

    # Character section
    elite_captain = self.build['captain']['elite']
    self.widgets.character['name'].setText(self.build['captain']['name'])
    elite_state = Qt.CheckState.Checked if elite_captain else Qt.CheckState.Unchecked
    self.widgets.character['elite'].setCheckState(elite_state)
    self.widgets.character['career'].setCurrentText(self.build['captain']['career'])
    species = self.build['captain']['species']
    self.widgets.character['faction'].setCurrentText(self.build['captain']['faction'])
    self.widgets.character['species'].setCurrentText(species)
    if species != 'Alien':
        self.widgets.build['space']['traits'][10].hide()
        self.widgets.build['ground']['traits'][10].hide()
    self.widgets.character['primary'].setCurrentText(self.build['captain']['primary_spec'])
    self.widgets.character['secondary'].setCurrentText(self.build['captain']['secondary_spec'])

    # Space Build Section
    if ship == '' or ship == '<Pick Ship>':
        align_space_frame(self, ship_data, clear=True)
    else:
        align_space_frame(self, ship_data)
    load_equipment_cat(self, 'fore_weapons', 'space')
    load_equipment_cat(self, 'aft_weapons', 'space')
    load_equipment_cat(self, 'experimental', 'space')
    load_equipment_cat(self, 'devices', 'space')
    load_equipment_cat(self, 'hangars', 'space')
    load_equipment_cat(self, 'deflector', 'space')
    load_equipment_cat(self, 'sec_def', 'space')
    load_equipment_cat(self, 'engines', 'space')
    load_equipment_cat(self, 'core', 'space')
    load_equipment_cat(self, 'shield', 'space')
    load_equipment_cat(self, 'uni_consoles', 'space')
    load_equipment_cat(self, 'eng_consoles', 'space')
    load_equipment_cat(self, 'sci_consoles', 'space')
    load_equipment_cat(self, 'tac_consoles', 'space')
    load_boff_stations(self, 'space')
    load_trait_cat(self, 'traits', 'space')
    if not elite_captain:
        self.widgets.build['space']['traits'][9].hide()
    load_trait_cat(self, 'starship_traits', 'space')
    load_trait_cat(self, 'rep_traits', 'space')
    load_trait_cat(self, 'active_rep_traits', 'space')
    load_doffs(self, 'space')

    # Ground Build Section
    self.widgets.ground_desc.setPlainText(self.build['ground']['ground_desc'])
    load_equipment_cat(self, 'kit_modules', 'ground')
    if not elite_captain:
        self.widgets.build['ground']['kit_modules'][5].hide()
    load_equipment_cat(self, 'weapons', 'ground')
    load_equipment_cat(self, 'ground_devices', 'ground')
    if not elite_captain:
        self.widgets.build['ground']['ground_devices'][4].hide()
    load_equipment_cat(self, 'kit', 'ground')
    load_equipment_cat(self, 'armor', 'ground')
    load_equipment_cat(self, 'ev_suit', 'ground')
    load_equipment_cat(self, 'personal_shield', 'ground')
    load_boff_stations(self, 'ground')
    load_trait_cat(self, 'traits', 'ground')
    if not elite_captain:
        self.widgets.build['ground']['traits'][9].hide()
    load_trait_cat(self, 'rep_traits', 'ground')
    load_trait_cat(self, 'active_rep_traits', 'ground')
    load_doffs(self, 'ground')

    load_skill_pages(self)

    self.building = False
    self.autosave()


def load_skill_pages(self):
    """
    Updates UI to show skill trees in self.build
    """
    # space skills
    self.widgets.build['skill_desc']['space'].setPlainText(self.build['skill_desc']['space'])
    self.cache.skills['space_points_eng'] = 0
    self.cache.skills['space_points_sci'] = 0
    self.cache.skills['space_points_tac'] = 0
    self.cache.skills['space_points_rank'] = [0] * 5
    self.cache.skills['space_points_total'] = 0
    for career in ('eng', 'sci', 'tac'):
        for skill_id, (button, enable) in enumerate(zip(
                self.widgets.build['space_skills'][career], self.build['space_skills'][career])):
            if enable:
                button.set_overlay(self.cache.overlays.check)
                button.highlight = True
                self.cache.skills[f'space_points_{career}'] += 1
                self.cache.skills['space_points_rank'][int(skill_id / 6)] += 1
            else:
                button.clear_overlay()
                button.highlight = False
    self.cache.skills['space_points_total'] = sum(self.cache.skills['space_points_rank'])
    for career in ('eng', 'sci', 'tac'):
        skill_points = self.cache.skills[f'space_points_{career}']
        self.widgets.skill_counts_space[career].setText(str(skill_points))
        for unlock_id, unlock_choice in enumerate(self.build['skill_unlocks'][career]):
            set_skill_unlock_space(self, career, unlock_id, unlock_choice, skill_points)
        if skill_points > 24:
            skill_points = 24
        for i in range(skill_points):
            self.widgets.skill_bonus_bars[career][i].setChecked(True)
        for i in range(skill_points, 24, 1):
            self.widgets.skill_bonus_bars[career][i].setChecked(False)

    # ground skills
    self.widgets.build['skill_desc']['ground'].setPlainText(self.build['skill_desc']['ground'])
    self.cache.skills['ground_points_total'] = 0
    for skill_data, skill_buttons in zip(
            self.build['ground_skills'], self.widgets.build['ground_skills']):
        for enable, skill_button in zip(skill_data, skill_buttons):
            if enable:
                skill_button.set_overlay(self.cache.overlays.check)
                skill_button.highlight = True
                self.cache.skills['ground_points_total'] += 1
            else:
                skill_button.clear_overlay()
                skill_button.highlight = False
    self.widgets.skill_count_ground.setText(str(self.cache.skills['ground_points_total']))
    for i in range(self.cache.skills['ground_points_total']):
        self.widgets.skill_bonus_bars['ground'][i].setChecked(True)
    for i in range(self.cache.skills['ground_points_total'], 10, 1):
        self.widgets.skill_bonus_bars['ground'][i].setChecked(False)
    for unlock_id, unlock_choice in enumerate(self.build['skill_unlocks']['ground']):
        set_skill_unlock_ground(self, unlock_id, unlock_choice)


def get_boff_spec(self, seat_details: str) -> tuple[int, str, str]:
    """
    Returns rank, profession and specialization from cargo string

    Parameters:
    - :param seat_details: contains rank, profession and specialization:
    "<rank> <profession>-<specialization>"
    """
    if '-' in seat_details:
        rank_and_profession, spec = seat_details.split('-')
    else:
        rank_and_profession = seat_details
        spec = ''
    rank_name, _, profession = rank_and_profession.rpartition(' ')
    return (BOFF_RANKS[rank_name], profession, spec)


def align_space_frame(self, ship_data: dict, clear: bool = False):
    """
    Hides / shows the appropriate buttons of the ship build. Updates Boff stations.

    Parameters:
    - :param ship_data: ship specifications
    - :param clear: set to True to clear build
    """
    uni, eng, sci, tac, devices, starship_traits = get_variable_slot_counts(self, ship_data)

    # Equipment
    update_equipment_cat(self, 'fore_weapons', ship_data['fore'], clear)
    update_equipment_cat(self, 'aft_weapons', ship_data['aft'], clear, can_hide=True)
    update_equipment_cat(self, 'experimental', ship_data['experimental'], clear, can_hide=True)
    update_equipment_cat(self, 'devices', devices, clear)
    update_equipment_cat(self, 'hangars', ship_data['hangars'], clear, can_hide=True)
    update_equipment_cat(self, 'sec_def', ship_data['secdeflector'], clear, can_hide=True)
    if clear:
        self.widgets.build['space']['deflector'][0].clear()
        self.build['space']['deflector'][0] = ''
        self.widgets.build['space']['engines'][0].clear()
        self.build['space']['engines'][0] = ''
        self.widgets.build['space']['core'][0].clear()
        self.build['space']['core'][0] = ''
        self.widgets.build['space']['shield'][0].clear()
        self.build['space']['shield'][0] = ''
    update_equipment_cat(self, 'uni_consoles', uni, clear, can_hide=True)
    update_equipment_cat(self, 'eng_consoles', eng, clear, can_hide=True)
    update_equipment_cat(self, 'sci_consoles', sci, clear, can_hide=True)
    update_equipment_cat(self, 'tac_consoles', tac, clear, can_hide=True)

    # Starship Traits
    update_starship_traits(self, starship_traits, clear)

    # Boffs
    boff_specs = map(lambda s: get_boff_spec(self, s), ship_data['boffs'])
    for boff_num, boff_details in enumerate(sorted(boff_specs, reverse=True)):
        update_boff_seat(self, boff_num, *boff_details, clear)
    for boff_to_hide in range(boff_num + 1, 6):
        update_boff_seat(self, boff_to_hide, rank=0, profession='', clear=clear, hide_seat=True)


def get_variable_slot_counts(self, ship_data: dict):
    """
    returns the number of universal consoles, devices and starship traits the current build should
    have

    Parameters:
    - :param ship_data: ship specifications

    :return: 6-tuple containing universal consoles, engineering consoles, science consoles, \
        tactical consoles, devices, starship traits
    """
    if ship_data['name'] == '<Pick Ship>':
        uni_consoles = 3
        starship_traits = 7
        devices = 6
        eng_consoles = 5
        sci_consoles = 5
        tac_consoles = 5
    else:
        uni_consoles = 0
        starship_traits = 5
        devices = ship_data['devices']
        eng_consoles = ship_data['consoleseng']
        sci_consoles = ship_data['consolessci']
        tac_consoles = ship_data['consolestac']
        if 'Innovation Effects' in ship_data['abilities']:
            uni_consoles += 1
        elif ship_data['name'] == 'Federation Intel Holoship':
            uni_consoles += 1
        if '-X2' in self.build['space']['tier']:
            uni_consoles += 2
            starship_traits += 2
            devices += 2
        elif '-X' in self.build['space']['tier']:
            uni_consoles += 1
            starship_traits += 1
            devices += 1
        if self.build['space']['tier'].startswith(('T5-U', 'T5-X')):
            if ship_data['t5uconsole'] == 'eng':
                eng_consoles += 1
            elif ship_data['t5uconsole'] == 'sci':
                sci_consoles += 1
            elif ship_data['t5uconsole'] == 'tac':
                tac_consoles += 1
    return uni_consoles, eng_consoles, sci_consoles, tac_consoles, devices, starship_traits


def update_equipment_cat(
        self, build_key: str, target_quantity: int | None, clear: bool = False,
        can_hide: bool = False):
    """
    Shows/hides appropriate amount of buttons of the given category; updates build; space build only

    Parameters:
    - :param build_key: key to self.build and self.widgets
    - :param target_quantity: number of slots that should be available in this category
    - :param clear: True to clear build
    - :param can_hide: hides/shows category label when target_quantity is 0/None
    """
    if target_quantity is None or target_quantity == 0:
        target_quantity = 0
        self.widgets.build['space'][build_key + '_label'].hide()
    elif can_hide:
        self.widgets.build['space'][build_key + '_label'].show()
    buttons = self.widgets.build['space'][build_key]
    max_quantity = len(buttons)
    for show_index in range(target_quantity):
        buttons[show_index].show()
        if clear:
            buttons[show_index].clear()
            self.build['space'][build_key][show_index] = ''
    for hide_index in range(target_quantity, max_quantity):
        buttons[hide_index].clear()
        buttons[hide_index].hide()
        self.build['space'][build_key][hide_index] = None


def clear_equipment_cat(self, build_key: str):
    """
    Clears buttons and build; ground build only

    Parameters:
    - :param build_key: key to self.build and self.widgets
    """
    for subkey, button in enumerate(self.widgets.build['ground'][build_key]):
        button.clear()
        self.build['ground'][build_key][subkey] = ''


def update_starship_traits(self, target_quantity: int, clear: bool = False):
    """
    Shows/hides appropriate amount of starship trait buttons; updates `self.build`

    Parameters:
    - :param target_quantity: number of slots that should be available in this category
    - :param clear: True to clear build
    """
    buttons = self.widgets.build['space']['starship_traits']
    for show_index in range(target_quantity):
        buttons[show_index].show()
        if clear:
            buttons[show_index].clear()
            self.build['space']['starship_traits'][show_index] = ''
    for hide_index in range(target_quantity, 7):
        buttons[hide_index].clear()
        buttons[hide_index].hide()
        self.build['space']['starship_traits'][hide_index] = None


def update_boff_seat(
        self, boff_id: str, rank: int, profession: str, specialization: str = '',
        clear: bool = False, hide_seat: bool = False):
    """
    Shows/hides appropriate amount of buttons of the boff seat; updates build; space build only

    Parameters:
    - :param boff_id: boff number counted from the top/beginning
    - :param rank: number of slots that should be available in this category
    - :param profession: seat profession
    - :param specialization: seat specialization
    - :param clear: set to True to clear build
    - :param hide_seat: hides/shows seat label
    """
    buttons = self.widgets.build['space']['boffs'][boff_id]
    max_quantity = 4
    for show_index in range(rank):
        buttons[show_index].show()
        if clear:
            buttons[show_index].clear()
            self.build['space']['boffs'][boff_id][show_index] = ''
    for hide_index in range(rank, max_quantity):
        buttons[hide_index].clear()
        buttons[hide_index].hide()
        self.build['space']['boffs'][boff_id][hide_index] = None
    label = self.widgets.build['space']['boff_labels'][boff_id]
    label.clear()
    if hide_seat:
        label.hide()
    else:
        label.show()
        if specialization != '':
            spec_label = f' / {specialization}'
        else:
            spec_label = ''
        if profession == 'Universal':
            label_options = (
                f'Tactical{spec_label}',
                f'Science{spec_label}',
                f'Engineering{spec_label}'
            )
            label.setDisabled(False)
        else:
            label_options = (profession + spec_label,)
            label.setDisabled(True)
        label.addItems(label_options)
    if clear:
        default_profession = 'Tactical' if profession == 'Universal' else profession
        self.build['space']['boff_specs'][boff_id] = [default_profession, specialization]


def clear_boff_seat_ground(self, boff_id: int):
    """
    Resets boff seat.

    Parameters:
    - :param boff_id: boff number counted from the top/beginning
    """
    for subkey, button in enumerate(self.widgets.build['ground']['boffs'][boff_id]):
        button.clear()
        self.build['ground']['boffs'][boff_id][subkey] = ''
    self.widgets.build['ground']['boff_profs'][boff_id].setCurrentText('Tactical')
    self.build['ground']['boff_profs'][boff_id] = 'Tactical'
    self.widgets.build['ground']['boff_specs'][boff_id].setCurrentText('Command')
    self.build['ground']['boff_specs'][boff_id] = 'Command'


def load_equipment_cat(self, build_key: str, environment: str):
    """
    Updates equipment category buttons to show items from build.

    Parameters:
    - :param build_key: equipment category
    - :param environment: space/ground
    """
    for subkey, item in enumerate(self.build[environment][build_key]):
        if item is not None and item != '':
            slot_equipment_item(self, item, environment, build_key, subkey)
        else:
            self.widgets.build[environment][build_key][subkey].clear()


def load_trait_cat(self, build_key: str, environment: str):
    """
    Updates trait category buttons to show items from build.

    Parameters:
    - :param build_key: trait category
    - :param environment: space/ground
    """
    for subkey, item in enumerate(self.build[environment][build_key]):
        if item is not None and item != '':
            slot_trait_item(self, item, environment, build_key, subkey)
        else:
            self.widgets.build[environment][build_key][subkey].clear()


def load_boff_stations(self, environment: str):
    """
    Updates boff stations to show items from build

    Parameters:
    - :param environment: "space" / "ground"
    """
    if environment == 'space':
        for boff_id, boff_data in enumerate(self.build['space']['boffs']):
            boff_spec = self.build['space']['boff_specs'][boff_id]
            if boff_spec[1] == '':
                boff_text = boff_spec[0]
            else:
                boff_text = f'{boff_spec[0]} / {boff_spec[1]}'
            self.widgets.build['space']['boff_labels'][boff_id].setCurrentText(boff_text)
            for ability, slot in zip(boff_data, self.widgets.build['space']['boffs'][boff_id]):
                if ability is not None and ability != '':
                    tooltip = self.cache.boff_abilities['all'][ability['item']]
                    slot.set_item_full(image(self, ability['item']), None, tooltip)
                else:
                    slot.clear()
    elif environment == 'ground':
        for boff_id, boff_data in enumerate(self.build['ground']['boffs']):
            self.widgets.build['ground']['boff_profs'][boff_id].setCurrentText(
                    self.build['ground']['boff_profs'][boff_id])
            self.widgets.build['ground']['boff_specs'][boff_id].setCurrentText(
                    self.build['ground']['boff_specs'][boff_id])
            for ability, slot in zip(boff_data, self.widgets.build['ground']['boffs'][boff_id]):
                if ability is not None and ability != '':
                    tooltip = self.cache.boff_abilities['all'][ability['item']]
                    slot.set_item_full(image(self, ability['item']), None, tooltip)
                else:
                    slot.clear()


def slot_equipment_item(self, item: dict, environment: str, build_key: str, build_subkey: int):
    """
    Updates build and UI with item

    Parameters:
    - :param item: item to be slotted
    - :param environment: space/ground
    - :param build_key: key to self.build[environment]
    - :param build_subkey: index of the item within its build_key (category)
    """
    self.build[environment][build_key][build_subkey] = item
    item_image = image(self, item['item'])
    overlay = getattr(self.cache.overlays, item['rarity'].lower().replace(' ', ''))
    tooltip = add_equipment_tooltip_header(
            self, item, self.cache.equipment[build_key][item['item']]['tooltip'], build_key)
    self.widgets.build[environment][build_key][build_subkey].set_item_full(
            item_image, overlay, tooltip)


def slot_trait_item(self, item: dict, environment: str, build_key: str, build_subkey: int):
    """
    Updates build and UI with item

    Parameters:
    - :param item: item to be slotted
    - :param environment: space/ground
    - :param build_key: key to self.build[environment]
    - :param build_subkey: index of the item within its build_key (category)
    """
    self.build[environment][build_key][build_subkey] = item
    item_image = image(self, item['item'])
    self.widgets.build[environment][build_key][build_subkey].set_item_full(
            item_image, None, get_tooltip(self, item['item'], build_key, environment))


def set_skill_unlock_ground(self, id: int, state: int | None):
    """
    Sets unlock button to state and updates build

    Parameters:
    - :param id: id of the unlock, counted from the unlock with the lowest requirement
    - :param state: `0`, `1` set the button to the respective unlock, `None` clears
    """
    unlock_button = self.widgets.build['skill_unlocks']['ground'][id]
    if state == 0:
        unlock_button.set_item(
                self.cache.images['arrow-down'])
        unlock_button.tooltip = get_skill_unlock_tooltip_ground(self, id, 0)
        self.build['skill_unlocks']['ground'][id] = 0
        if not self.building:
            unlock_button.force_tooltip_update()
    elif state == 1:
        unlock_button.set_item(
                self.cache.images['arrow-up'])
        unlock_button.tooltip = get_skill_unlock_tooltip_ground(self, id, 1)
        self.build['skill_unlocks']['ground'][id] = 1
        if not self.building:
            unlock_button.force_tooltip_update()
    else:
        unlock_button.clear()
        self.build['skill_unlocks']['ground'][id] = None


def set_skill_unlock_space(
            self, career: str, id: int, state: int | None = None, points_spent: int = -1):
    """
    Sets unlock button to state and updates build

    Parameters:
    - :param career: "eng" / "sci" / "tac"
    - :param id: id of the unlock, counted from the unlock with the lowest requirement
    - :param state: `0`, `1` set the button to the respective unlock, `None` clears
    """
    unlock_button = self.widgets.build['skill_unlocks'][career][id]
    if id == 4:
        if points_spent > 27 and state == self.build['skill_unlocks'][career][id]:
            return
        if state is None:
            unlock_button.clear()
            self.build['skill_unlocks'][career][id] = None
        else:
            unlock_button.set_item(
                    self.cache.images[self.cache.skills['space_unlocks']['_icons'][career]])
            if points_spent == 24:
                unlock_button.tooltip = get_ultimate_skill_unlock_tooltip(self, career, -1, 0)
                self.build['skill_unlocks'][career][id] = -1
            elif points_spent == 25:
                unlock_button.tooltip = get_ultimate_skill_unlock_tooltip(self, career, state, 1)
                self.build['skill_unlocks'][career][id] = state
            elif points_spent == 26:
                unlock_button.tooltip = get_ultimate_skill_unlock_tooltip(self, career, state, 2)
                self.build['skill_unlocks'][career][id] = state
            else:
                unlock_button.tooltip = get_ultimate_skill_unlock_tooltip(self, career, 4, 3)
                self.build['skill_unlocks'][career][id] = 3
            if not self.building:
                unlock_button.force_tooltip_update()
    else:
        if state == 0:
            unlock_button.set_item(
                    self.cache.images['arrow-down'])
            unlock_button.tooltip = get_skill_unlock_tooltip_space(self, career, id, 0)
            self.build['skill_unlocks'][career][id] = 0
            if not self.building:
                unlock_button.force_tooltip_update()
        elif state == 1:
            unlock_button.set_item(
                    self.cache.images['arrow-up'])
            unlock_button.tooltip = get_skill_unlock_tooltip_space(self, career, id, 1)
            self.build['skill_unlocks'][career][id] = 1
            if not self.building:
                unlock_button.force_tooltip_update()
        else:
            unlock_button.clear()
            self.build['skill_unlocks'][career][id] = None


def clear_traits(self, environment: str = 'both'):
    """
    Clears traits from build and UI

    Parameters:
    - :param environment: environment to clear the traits from (space/ground/both)
    """
    if environment == 'space' or environment == 'both':
        for i, trait_button in enumerate(self.widgets.build['space']['traits']):
            trait_button.clear()
            self.build['space']['traits'][i] = ''
        for i, trait_button in enumerate(self.widgets.build['space']['starship_traits']):
            trait_button.clear()
            self.build['space']['starship_traits'][i] = ''
        for i, trait_button in enumerate(self.widgets.build['space']['rep_traits']):
            trait_button.clear()
            self.build['space']['rep_traits'][i] = ''
        for i, trait_button in enumerate(self.widgets.build['space']['active_rep_traits']):
            trait_button.clear()
            self.build['space']['active_rep_traits'][i] = ''
    if environment == 'ground' or environment == 'both':
        for i, trait_button in enumerate(self.widgets.build['ground']['traits']):
            trait_button.clear()
            self.build['ground']['traits'][i] = ''
        for i, trait_button in enumerate(self.widgets.build['ground']['rep_traits']):
            trait_button.clear()
            self.build['ground']['rep_traits'][i] = ''
        for i, trait_button in enumerate(self.widgets.build['ground']['active_rep_traits']):
            trait_button.clear()
            self.build['ground']['active_rep_traits'][i] = ''


def clear_captain(self):
    """
    Clears Captain information from build and UI
    """
    self.widgets.character['name'].clear()
    self.build['captain']['name'] = ''
    self.widgets.character['elite'].setCheckState(Qt.CheckState.Unchecked)
    self.build['captain']['elite'] = False
    self.widgets.character['career'].setCurrentText('')
    self.build['captain']['career'] = ''
    self.widgets.character['faction'].setCurrentText('')
    self.build['captain']['faction'] = ''
    self.widgets.character['species'].setCurrentText('')
    self.build['captain']['species'] = ''
    self.widgets.character['primary'].setCurrentText('')
    self.build['captain']['primary_spec'] = ''
    self.widgets.character['secondary'].setCurrentText('')
    self.build['captain']['secondary_spec'] = ''


def clear_ship(self):
    """
    Clears ship section of sidebar
    """
    self.widgets.ship['image'].set_image(self.cache.empty_image)
    self.widgets.ship['button'].setText('<Pick Ship>')
    self.build['space']['ship'] = '<Pick Ship>'
    self.widgets.ship['tier'].clear()
    self.widgets.ship['dc'].hide()
    self.widgets.ship['name'].setText('')
    self.build['space']['ship_name'] = ''
    self.widgets.ship['desc'].setPlainText('')
    self.build['space']['ship_desc'] = ''


def clear_ground_build(self):
    """
    Clears ground build
    """
    self.widgets.ground_desc.clear()
    self.build['ground']['ground_desc'] = ''
    clear_equipment_cat(self, 'kit_modules')
    clear_equipment_cat(self, 'weapons')
    clear_equipment_cat(self, 'ground_devices')
    clear_equipment_cat(self, 'kit')
    clear_equipment_cat(self, 'armor')
    clear_equipment_cat(self, 'ev_suit')
    clear_equipment_cat(self, 'personal_shield')
    clear_boff_seat_ground(self, 0)
    clear_boff_seat_ground(self, 1)
    clear_boff_seat_ground(self, 2)
    clear_boff_seat_ground(self, 3)
    clear_traits(self, 'ground')
    clear_doffs(self, 'ground')


def load_doffs(self, environment: str):
    """
    Updates UI to show doffs in self.build

    Parameters:
    - :param environment: "space" / "ground"
    """
    doff_zipper = zip(
            self.widgets.build[environment]['doffs_spec'],
            self.build[environment]['doffs_spec'],
            self.widgets.build[environment]['doffs_variant'],
            self.build[environment]['doffs_variant'])
    for spec_combo, spec, variant_combo, variant in doff_zipper:
        spec_combo.setCurrentText(spec)
        if spec != '':
            variants = getattr(self.cache, f'{environment}_doffs')[spec].keys()
            variant_combo.addItems({''} | variants)
            variant_combo.setCurrentText(variant)


def clear_doffs(self, environment: str = 'both'):
    """
    Clears doff frame(s)

    Parameters:
    - :param environment: "space" / "ground" / "both"
    """
    if environment == 'space' or environment == 'both':
        for i in range(6):
            self.widgets.build['space']['doffs_spec'][i].setCurrentText('')
            self.widgets.build['space']['doffs_variant'][i].clear()
            self.build['space']['doffs_spec'][i] = ''
            self.build['space']['doffs_variant'][i] = ''
    if environment == 'ground' or environment == 'both':
        for i in range(6):
            self.widgets.build['ground']['doffs_spec'][i].setCurrentText('')
            self.widgets.build['ground']['doffs_variant'][i].clear()
            self.build['ground']['doffs_spec'][i] = ''
            self.build['ground']['doffs_variant'][i] = ''
