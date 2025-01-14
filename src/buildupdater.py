from PySide6.QtCore import Qt

from .constants import BOFF_RANKS, SHIP_TEMPLATE
from .iofunc import get_ship_image, image
from .textedit import get_tooltip, add_equipment_tooltip_header
from .widgets import exec_in_thread


def load_build(self):
    """
    Updates UI to show the build currently in self.build
    """
    self.building = True
    # ship section
    ship = self.build['space']['ship']
    if ship == '<Pick Ship>':
        ship_data = SHIP_TEMPLATE
        self.widgets.ship['button'].setText('<Pick Ship>')
        self.widgets.ship['tier'].clear()
        self.widgets.ship['image'].set_image(self.cache.empty_image)
    elif ship != '':
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
    self.widgets.ship['name'].setText(self.build['space']['ship_name'])
    self.widgets.ship['desc'].setPlainText(self.build['space']['ship_desc'])

    # Character section
    self.widgets.character['name'].setText(self.build['captain']['name'])
    elite = Qt.CheckState.Checked if self.build['captain']['elite'] else Qt.CheckState.Unchecked
    self.widgets.character['elite'].setCheckState(elite)
    self.widgets.character['career'].setCurrentText(self.build['captain']['career'])
    species = self.build['captain']['species']
    self.widgets.character['faction'].setCurrentText(self.build['captain']['faction'])
    self.widgets.character['species'].setCurrentText(species)
    self.build['captain']['species'] = species
    self.widgets.character['primary'].setCurrentText(self.build['captain']['primary_spec'])
    self.widgets.character['secondary'].setCurrentText(self.build['captain']['secondary_spec'])

    # Space Build Section
    if ship != '':
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
    load_trait_cat(self, 'starship_traits', 'space')
    load_trait_cat(self, 'rep_traits', 'space')
    load_trait_cat(self, 'active_rep_traits', 'space')

    self.building = False
    self.autosave()


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
    # Equipment
    update_equipment_cat(self, 'fore_weapons', ship_data['fore'], clear)
    update_equipment_cat(self, 'aft_weapons', ship_data['aft'], clear, can_hide=True)
    update_equipment_cat(self, 'experimental', ship_data['experimental'], clear, can_hide=True)
    update_equipment_cat(self, 'devices', ship_data['devices'], clear)
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
    uni_consoles = 0
    if 'Innovation Effects' in ship_data['abilities']:
        uni_consoles += 1
    if '-X2' in self.build['space']['tier']:
        uni_consoles += 2
    elif '-X' in self.build['space']['tier']:
        uni_consoles += 1
    if ship_data['name'] == '<Pick Ship>':
        uni_consoles = 3
    update_equipment_cat(self, 'uni_consoles', uni_consoles, clear, can_hide=True)
    update_equipment_cat(self, 'eng_consoles', ship_data['consoleseng'], clear, can_hide=True)
    update_equipment_cat(self, 'sci_consoles', ship_data['consolessci'], clear, can_hide=True)
    update_equipment_cat(self, 'tac_consoles', ship_data['consolestac'], clear, can_hide=True)

    # Boffs
    boff_specs = map(lambda s: get_boff_spec(self, s), ship_data['boffs'])
    for boff_num, boff_details in enumerate(sorted(boff_specs, reverse=True)):
        update_boff_seat(self, boff_num, *boff_details, clear)
    for boff_to_hide in range(boff_num + 1, 6):
        update_boff_seat(self, boff_to_hide, rank=0, profession='', clear=clear, hide_seat=True)


def update_equipment_cat(
        self, build_key: str, target_quantity: int | None, clear: bool, can_hide: bool = False):
    """
    Shows/hides appropriate amount of buttons of the given category; updates build

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


def update_boff_seat(
        self, boff_id: str, rank: int, profession: str, specialization: str = '',
        clear: bool = False, hide_seat: bool = False):
    """
    Shows/hides appropriate amount of buttons of the boff seat; updates build

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
            specialization = f' / {specialization}'
        if profession == 'Universal':
            label_options = (
                f'Tactical{specialization}',
                f'Science{specialization}',
                f'Engineering{specialization}'
            )
            label.setDisabled(False)
        else:
            label_options = (profession + specialization,)
            label.setDisabled(True)
        label.addItems(label_options)
    if clear:
        default_profession = 'Tactical' if profession == 'Universal' else profession
        self.build['space']['boff_specs'][boff_id] = [default_profession, specialization]


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
    - :param environment: space/ground
    """
    if environment == 'space':
        for boff_id, boff_data in enumerate(self.build['space']['boffs']):
            boff_spec = self.build['space']['boff_specs'][boff_id]
            if boff_spec[1] == '':
                boff_text = boff_spec[0]
            else:
                boff_text = f'{boff_spec[0]} / {boff_spec[1]}'
            self.widgets.build['space']['boff_labels'][boff_id].setCurrentText(boff_text)
            for ability_num, ability in enumerate(boff_data):
                if ability is not None and ability != '':
                    tooltip = self.cache.boff_abilities['all'][ability['item']]
                    self.widgets.build['space']['boffs'][boff_id][ability_num].set_item_full(
                            image(self, ability['item']), None, tooltip)
                else:
                    self.widgets.build['space']['boffs'][boff_id][ability_num].clear()


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
    self.widgets.ship['name'].setText('')
    self.build['space']['ship_name'] = ''
    self.widgets.ship['desc'].setPlainText('')
    self.build['space']['ship_desc'] = ''
