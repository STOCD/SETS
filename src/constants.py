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
    'environment,type,isunique,master,description&limit=2500&format=json'
)
STARSHIP_TRAIT_QUERY_URL = (
    WIKI_URL + 'Special:CargoExport?tables=StarshipTraits&fields=_pageName,name,short,type,'
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
FACTION_QUERY = (
    WIKI_URL + 'Special:CargoExport?tables=Faction&fields=playability,name,faction,traits'
    '&limit=1000&offset=0&format=json&where=playability%20IS%20NOT%20NULL'
)

EQUIPMENT_TYPES = {
    'Body Armor', 'EV Suit', 'Experimental Weapon', 'Ground Device', 'Ground Weapon', 'Hangar Bay',
    'Impulse Engine', 'Impulse Engine', 'Kit', 'Kit Module', 'Personal Shield', 'Ship Aft Weapon',
    'Ship Deflector Dish', 'Ship Device', 'Ship Engineering Console', 'Ship Fore Weapon',
    'Ship Science Console', 'Ship Secondary Deflector', 'Ship Shields', 'Ship Tactical Console',
    'Ship Weapon', 'Singularity Engine', 'Universal Console', 'Warp Engine'
}

CAREERS = {'Tactical', 'Science', 'Engineering'}

FACTIONS = {'Federation', 'Klingon', 'Romulan', 'Dominion', 'TOS Federation', 'DSC Federation'}

PRIMARY_SPECS = {'Command', 'Intelligence', 'Miracle Worker', 'Temporal', 'Pilot'}

SECONDARY_SPECS = {'Strategist', 'Constable', 'Commando'}

BOFF_URL = WIKI_URL + 'Bridge_officer_and_kit_abilities'
