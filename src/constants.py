from types import FunctionType, BuiltinFunctionType, MethodType

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSizePolicy

CALLABLE = (FunctionType, BuiltinFunctionType, MethodType)

SMINMIN = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
SMAXMAX = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
SMAXMIN = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum)
SMINMAX = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)

ATOP = Qt.AlignmentFlag.AlignTop
ABOTTOM = Qt.AlignmentFlag.AlignBottom
ARIGHT = Qt.AlignmentFlag.AlignRight
ALEFT = Qt.AlignmentFlag.AlignLeft
ACENTER = Qt.AlignmentFlag.AlignCenter
AVCENTER = Qt.AlignmentFlag.AlignVCenter
AHCENTER = Qt.AlignmentFlag.AlignHCenter

WIKI_URL = 'https://stowiki.net/wiki/'
WIKI_IMAGE_URL = WIKI_URL + 'Special:FilePath/'
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
    'environment,type,isunique,description&limit=2500&format=json'
)
STARSHIP_TRAIT_QUERY_URL = (
    WIKI_URL + 'Special:CargoExport?tables=StarshipTraits&fields=_pageName%3DPage,name,short,type,'
    'detailed,obtained,basic&limit=2500&format=json&where=name%20IS%20NOT%20NULL'
)
DOFF_QUERY_URL = (
    WIKI_URL + 'Special:CargoExport?tables=Specializations&fields=name=spec,_pageName,shipdutytype,'
    'department,description,white,green,blue,purple,violet,gold&limit=1000&offset=0&format=json'
)
TRAYSKILL_QUERY = (
    WIKI_URL + 'Special:CargoExport?tables=TraySkill&fields=_pageName,name,activation,affects,'
    'description,description_long,rank1rank,rank2rank,rank3rank,recharge_base,recharge_global,'
    'region,system,targets,type&limit=1000&offset=0&format=json'
)
MODIFIER_QUERY = (
    WIKI_URL + 'Special:CargoExport?tables=Modifiers&fields=_pageName,modifier,type,stats,'
    'available,isunique,info&format=json&limit=1000'
)

EQUIPMENT_TYPES = {
    'Body Armor': 'armor', 'EV Suit': 'ev', 'Experimental Weapon': 'experimental',
    'Ground Device': 'ground_devices', 'Ground Weapon': 'weapons', 'Hangar Bay': 'hangars',
    'Impulse Engine': 'engines', 'Kit': 'kit', 'Kit Module': 'module',
    'Personal Shield': 'personal_shield', 'Ship Aft Weapon': 'aft_weapons',
    'Ship Deflector Dish': 'deflector', 'Ship Device': 'devices',
    'Ship Engineering Console': 'eng_consoles', 'Ship Fore Weapon': 'fore_weapons',
    'Ship Science Console': 'sci_consoles', 'Ship Secondary Deflector': 'sec_def',
    'Ship Shields': 'shield', 'Ship Tactical Console': 'tac_consoles', 'Ship Weapon': 'ship_weapon',
    'Singularity Engine': 'core', 'Universal Console': 'uni_consoles', 'Warp Engine': 'core'
}

CAREERS = {'Tactical', 'Science', 'Engineering'}

FACTIONS = {'Federation', 'Klingon', 'Romulan', 'Dominion', 'TOS Federation', 'DSC Federation'}

SPECIES = {
    'Federation': {
        'Human', 'Andorian', 'Bajoran', 'Benzite', 'Betazoid', 'Bolian', 'Ferengi', 'Pakled',
        'Rigelian', 'Saurian', 'Tellarite', 'Trill', 'Vulcan', 'Alien'
    },
    'Klingon': {'Klingon', 'Gorn', 'Lethean', 'Nausicaan', 'Orion', 'Alien'},
    'Romulan': {'Romulan', 'Reman', 'Alien'},
    'Dominion': {"Jem'Hadar"},
    'TOS Federation': {'Human', 'Andorian', 'Tellarite', 'Vulcan'},
    'DSC Federation': {'Human', 'Vulcan', 'Alien'}
}

PRIMARY_SPECS = {'Command', 'Intelligence', 'Miracle Worker', 'Temporal', 'Pilot'}

SECONDARY_SPECS = {'Strategist', 'Constable', 'Commando'}

BOFF_URL = WIKI_URL + 'Bridge_officer_and_kit_abilities'

RARITIES = {
    'Common': 0,
    'Uncommon': 1,
    'Rare': 2,
    'Very Rare': 3,
    'Ultra Rare': 4,
    'Epic': 5
}

RARITY_COLORS = {
    'Common': '#eeeeee',
    'Uncommon': '#00cc00',
    'Rare': '#0099ff',
    'Very Rare': '#a245b9',
    'Ultra Rare': '#6d65bc',
    'Epic': '#ffd700'
}

MARKS = (
    'Mk I', 'Mk II', 'Mk III', 'Mk IV', 'MK V', 'MK VI', 'MK VII', 'MK VIII', 'MK IX', 'MK X',
    'Mk XI', 'Mk XII', 'Mk XIII', 'Mk XIV', 'Mk XV', '∞'
)

BOFF_RANKS = {
    'Commander': 4,
    'Lieutenant Commander': 3,
    'Lieutenant': 2,
    'Ensign': 1
}

SHIP_TEMPLATE = {
    'name': '<Pick Ship>',
    'boffs': [
        'Commander Universal-Miracle Worker',
        'Commander Universal-Command',
        'Commander Universal-Intelligence',
        'Commander Universal-Pilot',
        'Commander Universal-Temporal',
        'Commander Universal'
    ],
    'abilities': [
        'Innovation Effects'
    ],
    'fore': 5,
    'aft': 5,
    'devices': 6,
    'consolestac': 5,
    'consoleseng': 5,
    'consolessci': 5,
    'experimental': 1,
    'secdeflector': 1,
    'hangars': 2
}

# commented maps must be transferred manually
BUILD_CONVERSION = {
    'space': (
        ('activeRepTrait', 'active_rep_traits'),
        ('aftWeapons', 'aft_weapons'),
        ('warpCore', 'core'),
        ('devices', 'devices'),
        ('deflector', 'deflector'),
        # ('doffs', 'doffs'),
        ('engConsoles', 'eng_consoles'),
        ('engines', 'engines'),
        ('experimental', 'experimental'),
        ('foreWeapons', 'fore_weapons'),
        ('hangars', 'hangars'),
        ('spaceRepTrait', 'rep_traits'),
        ('sciConsoles', 'sci_consoles'),
        ('secdef', 'sec_def'),
        ('shield', 'shield'),
        ('ship', 'ship'),
        ('playerShipName', 'ship_name'),
        ('playerShipDesc', 'ship_desc'),
        ('starshipTrait', 'starship_traits'),
        ('tacConsoles', 'tac_consoles'),
        ('tier', 'tier'),
        # ('personalSpaceTrait', 'traits'),
        # ('personalSpaceTrait2', 'traits'),
        ('uniConsoles', 'uni_consoles')
    ),
    'ground': (
        ('groundActiveRepTrait', 'active_rep_traits'),
        ('groundArmor', 'armor'),
        ('groundDevices', 'devices'),
        ('groundEV', 'ev_suit'),
        ('groundKit', 'kit'),
        ('groundKitModules', 'kit_modules'),
        ('groundRepTrait', 'rep_traits'),
        ('groundShield', 'personal_shield'),
        # ('personalGroundTrait', 'traits'),
        # ('personalGroundTrait2', 'traits'),
        ('groundWeapons', 'weapons')
    ),
    'captain': (
        ('career', 'career'),
        ('eliteCaptain', 'elite'),
        ('specPrimary', 'primary_spec'),
        ('specSecondary', 'secondary_spec'),
        ('species', 'species')
    )
}
