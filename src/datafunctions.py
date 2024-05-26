from datetime import datetime
from json import JSONDecodeError
import os
from requests.exceptions import JSONDecodeError as RequestsJSONDecodeError
import sys

from .callbacks import enter_splash, exit_splash, splash_text
from .iofunc import fetch_json, load_json, store_json


WIKI_URL = 'https://stowiki.net/wiki/'
SHIP_QUERY_URL = (
    WIKI_URL + 'Special:CargoExport?tables=Ships&fields=_pageName%3DPage,name,image,fc,tier,'
    'type,hull,hullmod,shieldmod,turnrate,impulse,inertia,powerall,powerweapons,powershields,'
    'powerengines,powerauxiliary,powerboost,boffs,fore,aft,equipcannons,devices,consolestac,'
    'consoleseng,consolessci,uniconsole,t5uconsole,experimental,secdeflector,hangars,abilities,'
    'displayprefix,displayclass,displaytype,factionlede&limit=2500&format=json'
)
ITEM_QUERY_URL = (
    WIKI_URL + 'Special:CargoExport?tables=Infobox&fields=_pageName%3DPage,name,rarity,type,'
    'boundto,boundwhen,who,head1,head2,head3,head4,head5,head6,head7,head8,head9,subhead1,subhead2,'
    'subhead3,subhead4,subhead5,subhead6,subhead7,subhead8,subhead9,text1,text2,text3,text4,text5,'
    'text6,text7,text8,text9&limit=5000&format=json'
)
TRAIT_QUERY_URL = (
    WIKI_URL + 'Special:CargoExport?tables=Traits&fields=_pageName%3DPage,name,chartype,'
    'environment,type,isunique,master,description&limit=2500&format=json'
)
STARSHIP_TRAIT_QUERY_URL = (
    WIKI_URL + 'Special:CargoExport?tables=StarshipTraits&fields=_pageName,name,short,type,'
    'detailed,obtained,basic&limit=2500&format=json&where=name%20IS%20NOT%20NULL'
)
DOFF_QUERY_URL = (
    WIKI_URL + 'Special:CargoExport?tables=Specializations&fields=name,_pageName,shipdutytype,'
    'department,description,powertype,white,green,blue,purple,violet,gold&limit=1000&offset=0'
    '&format=json'
)
TRAYSKILL_QUERY = (
    WIKI_URL + 'Special:CargoExport?tables=TraySkill&fields=_pageName,name,activation,affects,'
    'description,description_long,rank1rank,rank2rank,rank3rank,recharge_base,recharge_global,'
    'region,system,targets,type&limit=1000&offset=0&format=json'
)

EQUIPMENT_TYPES = {
    'Body Armor', 'EV Suit', 'Experimental Weapon', 'Ground Device', 'Ground Weapon', 'Hangar Bay',
    'Impulse Engine', 'Impulse Engine', 'Kit', 'Kit Module', 'Personal Shield', 'Ship Aft Weapon',
    'Ship Deflector Dish', 'Ship Device', 'Ship Engineering Console', 'Ship Fore Weapon',
    'Ship Science Console', 'Ship Secondary Deflector', 'Ship Shields', 'Ship Tactical Console',
    'Ship Weapon', 'Singularity Engine', 'Universal Console', 'Warp Engine'
}


def load_cargo_data(self):
    """
    Loads cargo data for all cargo tables and puts them into variables.
    """
    enter_splash(self)
    splash_text(self, 'Loading: Starships')
    ship_cargo_data = get_cargo_data(self, 'ship_list.json', SHIP_QUERY_URL)
    self.cache.ships = {ship['Page']: ship for ship in ship_cargo_data}
    splash_text(self, 'Loading: Equipment')
    equipment_cargo_data = get_cargo_data(self, 'equipment.json', ITEM_QUERY_URL)
    for item in equipment_cargo_data:
        if item['type'] in EQUIPMENT_TYPES:
            self.cache.equipment[item['type']][item['name']] = item
    splash_text(self, 'Loading: Traits')
    trait_cargo_data = get_cargo_data(self, 'traits.json', TRAIT_QUERY_URL)
    for trait in trait_cargo_data:
        if trait['chartype'] == 'char':
            if trait['type'] == 'reputation':
                trait_type = 'rep'
            elif trait['type'] == 'activereputation':
                trait_type = 'active_rep'
            else:
                trait_type = 'personal'
            try:
                self.cache.traits[trait['environment']][trait_type][trait['name']] = trait
            except KeyError:
                pass
    splash_text(self, 'Loading: Starship Traits')
    shiptrait_cargo_data = get_cargo_data(self, 'starship_traits.json', STARSHIP_TRAIT_QUERY_URL)
    self.cache.starship_traits = {ship_trait['name'] for ship_trait in shiptrait_cargo_data}
    splash_text(self, 'Loading: Duty Officers')
    exit_splash(self)


def get_cargo_data(self, filename: str, url: str, ignore_cache_age=False) -> dict | list:
    """
    Retrieves cargo data for specific table. Downloads cargo data from wiki if cache is empty.
    Updates cache.

    Parameters:
    - :param filename: filename of cache file
    - :param url: url to cargo table
    - :param ignore_cache_age: True if cache of any age should be accepted
    """
    filepath = f"{self.config['config_subfolders']['cache']}\\{filename}"
    cargo_data = None

    # try loading from cache
    if os.path.exists(filepath) and os.path.isfile(filepath):
        last_modified = os.path.getmtime(filepath)
        if (datetime.now() - datetime.fromtimestamp(last_modified)).days < 7 or ignore_cache_age:
            try:
                return load_json(filepath)
            except JSONDecodeError:
                backup_filepath = f"{self.config['config_subfolders']['backups']}\\{filename}"
                if os.path.exists(backup_filepath) and os.path.isfile(backup_filepath):
                    try:
                        cargo_data = load_json(backup_filepath)
                        store_json(cargo_data, filepath)
                        return cargo_data
                    except JSONDecodeError:
                        pass

    # download cargo data if loading from cache failed or data should be updated
    try:
        cargo_data = fetch_json(url)
        store_json(cargo_data, filepath)
        return cargo_data
    except RequestsJSONDecodeError:
        if ignore_cache_age:
            sys.stderr.write(f'[Error] Cargo table could not be retrieved ({filename})\n')
            sys.exit(1)
        else:
            return get_cargo_data(self, filename, url, ignore_cache_age=True)
