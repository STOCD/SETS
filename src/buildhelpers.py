from .constants import BOFF_RANKS, BUILD_VERSION


def empty_build(build_type: str = 'full') -> dict[str, int | dict[str]]:
    """
    Creates empty build and returns it.

    Parameters:
    - :param build_type: `build` -> space and ground build; `skills` -> space and ground skills;
        `full` -> space and ground build and skills
    """
    # None means not available on the build; empty string means empty slot
    new_build = {
        '_version': BUILD_VERSION,
        'space': {
            'active_rep_traits': [None] * 5,
            'aft_weapons': [None] * 5,
            'boffs': [[None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4, [None] * 4],
            'boff_specs': [['Tactical', 'Temporal'], ['Tactical', 'Pilot'],
                           ['Tactical', 'Miracle Worker'], ['Tactical', 'Intelligence'],
                           ['Tactical', 'Command'], ['Tactical', None]],
            'core': [''],
            'deflector': [''],
            'devices': [None] * 6,
            'doffs_spec': [''] * 6,
            'doffs_variant': [''] * 6,
            'eng_consoles': [None] * 5,
            'engines': [''],
            'experimental': [None],
            'fore_weapons': [None] * 5,
            'hangars': [None] * 2,
            'rep_traits': [None] * 5,
            'sci_consoles': [None] * 5,
            'sec_def': [None],
            'shield': [''],
            'ship': '',
            'ship_name': '',
            'ship_desc': '',
            'starship_traits': [None] * 7,
            'tac_consoles': [None] * 5,
            'tier': '',
            'traits': ['', '', '', '', '', '', '', '', '', None, None, ''],
            'uni_consoles': [None] * 3,
        },
        'ground': {
            'active_rep_traits': [None] * 5,
            'armor': [''],
            'boffs': [[''] * 4, [''] * 4, [''] * 4, [''] * 4],
            'boff_profs': ['Tactical'] * 4,
            'boff_specs': ['Command'] * 4,
            'ground_desc': '',
            'ground_devices': ['', '', '', '', None],
            'doffs_spec': [''] * 6,
            'doffs_variant': [''] * 6,
            'ev_suit': [''],
            'kit': [''],
            'kit_modules': ['', '', '', '', '', None],
            'rep_traits': [''] * 5,
            'personal_shield': [''],
            'traits': ['', '', '', '', '', '', '', '', '', None, None, ''],
            'weapons': [''] * 2,
        },
        'captain': {
            'career': '',
            'elite': False,
            'faction': '',
            'name': '',
            'primary_spec': '',
            'secondary_spec': '',
            'species': '',
        },
    }

    new_skills = {
        '_version': BUILD_VERSION,
        'space_skills': {
            'eng': [False] * 30,
            'sci': [False] * 30,
            'tac': [False] * 30,
        },
        'skill_unlocks': {
            'eng': [None] * 5,
            'sci': [None] * 5,
            'tac': [None] * 5,
            'ground': [None] * 5
        },
        'ground_skills': [
            [False] * 6,
            [False] * 6,
            [False] * 4,
            [False] * 4
        ],
        'skill_desc': {
            'space': '',
            'ground': ''
        }
    }

    if build_type == 'build':
        return new_build
    elif build_type == 'full':
        new_build.update(new_skills)
        return new_build
    elif build_type == 'skills':
        return new_skills


def get_variable_slot_counts(ship_data: dict[str], ship_tier: str) -> tuple[int]:
    """
    returns the number of universal consoles, devices and starship traits the given ship build
    should have

    Parameters:
    - :param ship_data: ship specifications
    - :param ship_tier: selected ship tier

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
        if '-X2' in ship_tier:
            uni_consoles += 2
            starship_traits += 2
            devices += 2
        elif '-X' in ship_tier:
            uni_consoles += 1
            starship_traits += 1
            devices += 1
        if ship_tier.startswith(('T5-U', 'T5-X')):
            if ship_data['t5uconsole'] == 'eng':
                eng_consoles += 1
            elif ship_data['t5uconsole'] == 'sci':
                sci_consoles += 1
            elif ship_data['t5uconsole'] == 'tac':
                tac_consoles += 1
    return uni_consoles, eng_consoles, sci_consoles, tac_consoles, devices, starship_traits


def parse_boff_stations(stations: list[str]) -> list[tuple[int, str, str]]:
    """
    Returns rank, profession and specialization from cargo string

    Parameters:
    - :param stations: list of strings containing rank, profession and specialization:
    "<rank> <profession>-<specialization>"
    """
    parsed_stations = list()
    for station in stations:
        if station == '':
            continue
        if '-' in station:
            rank_and_profession, spec = station.split('-')
        else:
            rank_and_profession = station
            spec = ''
        rank_name, _, profession = rank_and_profession.rpartition(' ')
        parsed_stations.append((BOFF_RANKS[rank_name.strip()], profession.strip(), spec.strip()))
    return parsed_stations
