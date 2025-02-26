from .constants import BOFF_RANKS_MD, CAREER_ABBR
from .textedit import wiki_url
from .widgets import notempty


def create_md_table(self, table: list[list[str]], alignment: list = []) -> str:
    """
    Creates markdown-formatted table from two-dimensional list

    Parameters:
    - :param table: two-dimenional list representing the table
    - :param alignment: contains column alignment codes for the table
    """
    text = '|'.join(table[0]) + '\n'
    if len(alignment) == 0:
        text += '|'.join([':-'] * len(table[0])) + '\n'
    else:
        text += '|'.join(alignment) + '\n'
    for row in table[1:]:
        text += '|'.join(row) + '\n'
    return text


def md_equipment_table(
        self, environment: str, key: str, header: str, extra_cols: int = 1,
        single_line: bool = False) -> str:
    """
    Returns table segment of equipment table for markdown export.

    Parameters:
    - :param environment: "space" / "ground"
    - :param key: key to `self.build[environment]`
    - :param header: header text for section
    - :param extra_cols: how many empty cols should be added
    - :param single_line: whether the sections consists of a single line
    """
    section = [[f'**{header}**']]
    if single_line:
        item = self.build[environment][key][0]
        if item is not None and item != '':
            section[0].append(
                    f"[{item['item']} {item['mark']} {''.join(notempty(item['modifiers']))}]"
                    f"({wiki_url(self.cache.equipment[key][item['item']]['Page'])})")
        else:
            section[0].append('')
        section[0] += [''] * extra_cols
    else:
        category_items = self.build[environment][key]
        for i, item in enumerate(category_items):
            if item is None:
                if i == 0:
                    section[0] += [''] * (extra_cols + 1)
                continue
            if i > 0:
                section.append(['&nbsp;'])
            if item == '':
                section[-1] += [''] * (extra_cols + 1)
            else:
                section[-1].append(
                        f"[{item['item']} {item['mark']} {''.join(notempty(item['modifiers']))}]"
                        f"({wiki_url(self.cache.equipment[key][item['item']]['Page'])})")
                section[-1] += [''] * extra_cols
        section.append(['--------------', '--------------'] + [''] * extra_cols)
    return section


def md_boff_table(self, station: list, header: str, extra_cols: int = 1) -> list:
    """
    Returns table segment of bridge officer table for markdown export.

    Parameters:
    - :param station: boff station to convert
    - :param header: station name
    - :param extra_cols: how many empty cols should be added
    """
    section = [[f'**{header}**']]
    for i, ability in enumerate(station):
        if i > 0:
            section.append(['&nbsp;'])
        if ability == '':
            section[i] += [''] * (extra_cols + 1)
        elif ability is None:
            section.pop()
        else:
            section[i].append(f"[{ability['item']}]({wiki_url(ability['item'], 'Ability: ')})")
            section[i] += [''] * extra_cols
    section.append(['--------------', '--------------'] + [''] * extra_cols)
    return section


def md_skill_table_space(self, skills: list, offset: int) -> list:
    """
    Returns table segment (one rank) of space skills for markdown export.

    Parameters:
    - :param skills: contains all skill groups of one rank
    - :param offset: offset of the first skill node for indexing into `self.build`
    """
    section = [[], []]
    offsets = {'eng': offset, 'tac': offset, 'sci': offset}
    for skill in skills:
        if skill['grouping'] == 'column':
            section[0].append(f"[{skill['skill']}]({skill['link']})")
            unlocked_skills = ''
            if self.build['space_skills'][skill['career']][offsets[skill['career']]]:
                unlocked_skills += '[X] > '
            else:
                unlocked_skills += '[&nbsp;&nbsp;&nbsp;] > '
            if self.build['space_skills'][skill['career']][offsets[skill['career']] + 1]:
                unlocked_skills += '[X] > '
            else:
                unlocked_skills += '[&nbsp;&nbsp;&nbsp;] > '
            if self.build['space_skills'][skill['career']][offsets[skill['career']] + 2]:
                unlocked_skills += '[X]'
            else:
                unlocked_skills += '[&nbsp;&nbsp;&nbsp;]'
            section[1].append(unlocked_skills)
        elif skill['grouping'] == 'pair+1':
            section[0].append(skill['skill'][0])
            unlocked_skills = ''
            if self.build['space_skills'][skill['career']][offsets[skill['career']] + 1]:
                unlocked_skills += f"[[X]]({skill['link'][1]}) < "
            else:
                unlocked_skills += '[&nbsp;&nbsp;&nbsp;] < '
            if self.build['space_skills'][skill['career']][offsets[skill['career']]]:
                unlocked_skills += f"[[X]]({skill['link'][0]}) > "
            else:
                unlocked_skills += '[&nbsp;&nbsp;&nbsp;] > '
            if self.build['space_skills'][skill['career']][offsets[skill['career']] + 2]:
                unlocked_skills += f"[[X]]({skill['link'][2]})"
            else:
                unlocked_skills += '[&nbsp;&nbsp;&nbsp;]'
            section[1].append(unlocked_skills)
        elif skill['grouping'] == 'separate':
            section[0].append(f"[{skill['skill'][0]}]({skill['link']})")
            unlocked_skills = ''
            if self.build['space_skills'][skill['career']][offsets[skill['career']] + 1]:
                unlocked_skills += '[X] < '
            else:
                unlocked_skills += '[&nbsp;&nbsp;&nbsp;] < '
            if self.build['space_skills'][skill['career']][offsets[skill['career']]]:
                unlocked_skills += '[X] > '
            else:
                unlocked_skills += '[&nbsp;&nbsp;&nbsp;] > '
            if self.build['space_skills'][skill['career']][offsets[skill['career']] + 2]:
                unlocked_skills += '[X]'
            else:
                unlocked_skills += '[&nbsp;&nbsp;&nbsp;]'
            section[1].append(unlocked_skills)
        if len(section[0]) == 2 or len(section[0]) == 5:
            section[0].append('')
            section[1].append('')
        offsets[skill['career']] += 3
    return section


def get_build_markdown(self, environment: str, type_: str) -> str:
    """
    Converts part of build in self.build to markdown.

    Parameters:
    - :param environment: "space" / "ground"; determines which build environment is generated
    - :param type_: "build" / "skills"; determines whether build or skill tree is generated
    """
    if environment == 'space' and type_ == 'build':
        md = (
            f"# SPACE BUILD\n\n**Basic Information** | **Data** \n:--- | :--- \n"
            f"*Ship Name* | {self.build['space']['ship_name']} \n"
            f"*Ship Class* | {self.build['space']['ship']} \n"
            f"*Ship Tier* | {self.build['space']['tier']} \n"
            f"*Player Career* | {self.build['captain']['career']} \n"
            f"*Elite Captain* | {'✓' if self.build['captain']['elite'] else '✗'}\n"
            f"*Player Species* | {self.build['captain']['species']} \n"
            f"*Primary Specialization* | {self.build['captain']['primary_spec']} \n"
            f"*Secondary Specialization* | {self.build['captain']['secondary_spec']} \n\n\n"
        )
        if self.build['space']['ship_desc']:
            md += f"## Build Description\n\n{self.build['space']['ship_desc']}\n\n\n"

        md += '## Ship Equipment\n\n'
        equip_table = [['****Basic Information****', '****Component****', '****Notes****']]
        equip_table += md_equipment_table(self, 'space', 'fore_weapons', 'Fore Weapons')
        equip_table += md_equipment_table(self, 'space', 'aft_weapons', 'Aft Weapons')
        equip_table += md_equipment_table(self, 'space', 'deflector', 'Deflector', single_line=True)
        if self.build['space']['sec_def'][0]:
            equip_table += md_equipment_table(
                    self, 'space', 'sec_def', 'Secondary Deflector', single_line=True)
        equip_table += md_equipment_table(
                self, 'space', 'engines', 'Impulse Engines', single_line=True)
        equip_table += md_equipment_table(self, 'space', 'core', 'Warp', single_line=True)
        equip_table += md_equipment_table(self, 'space', 'shield', 'Shield', single_line=True)
        equip_table += md_equipment_table(self, 'space', 'devices', 'Devices')
        if self.build['space']['experimental'][0]:
            equip_table += md_equipment_table(
                    self, 'space', 'experimental', 'Experimental Weapon', single_line=True)
        if self.build['space']['hangars'][0] or self.build['space']['hangars'][1]:
            equip_table += md_equipment_table(self, 'space', 'hangars', 'Hangars')
        equip_table += md_equipment_table(self, 'space', 'uni_consoles', 'Universal Consoles')
        equip_table += md_equipment_table(self, 'space', 'eng_consoles', 'Engineering Consoles')
        equip_table += md_equipment_table(self, 'space', 'sci_consoles', 'Science Consoles')
        equip_table += md_equipment_table(self, 'space', 'tac_consoles', 'Tactical Consoles')
        md += create_md_table(self, equip_table)

        md += '\n\n\n## Bridge Officer Stations\n\n'
        boff_table = [['****Profession****', '****Power****', '****Notes****']]
        for specs, station in zip(self.build['space']['boff_specs'], self.build['space']['boffs']):
            if any(specs):
                station_name = BOFF_RANKS_MD[station.count(None)] + ' ' + specs[0]
                if specs[1] != '':
                    station_name += ' / ' + specs[1]
                boff_table += md_boff_table(self, station, station_name)
        md += create_md_table(self, boff_table)

        md += '\n\n\n## Traits\n\n'
        trait_table = [['****Starship Traits****', '****Notes****']]
        for trait in notempty(self.build['space']['starship_traits']):
            trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
        md += create_md_table(self, trait_table)
        md += '\n\n&#x200B;\n\n'
        trait_table = [['****Personal Space Traits****', '****Notes****']]
        for trait in notempty(self.build['space']['traits']):
            trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
        md += create_md_table(self, trait_table)
        md += '\n\n&#x200B;\n\n'
        trait_table = [['****Space Reputation Traits****', '****Notes****']]
        for trait in notempty(self.build['space']['rep_traits']):
            trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
        md += create_md_table(self, trait_table)
        md += '\n\n&#x200B;\n\n'
        trait_table = [['****Active Space Reputation Traits****', '****Notes****']]
        for trait in notempty(self.build['space']['active_rep_traits']):
            trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
        md += create_md_table(self, trait_table)

        md += '\n\n\n## Active Space Duty Officers\n\n'
        doff_table = [['****Specialization****', '****Power****', '****Notes****']]
        for spec, variant in zip(
                self.build['space']['doffs_spec'], self.build['space']['doffs_variant']):
            if spec != '':
                doff_table.append([f"[{spec}]({wiki_url(spec, 'Specialization: ')})", variant, ''])
        md += create_md_table(self, doff_table)
        return md
    elif environment == 'ground' and type_ == 'build':
        md = (
            f"# GROUND BUILD\n\n**Basic Information** | **Data** \n:--- | :--- \n"
            f"*Player Name* | {self.build['captain']['name']} \n"
            f"*Player Species* | {self.build['captain']['species']} \n"
            f"*Player Career* | {self.build['captain']['career']} \n"
            f"*Elite Captain* | {'✓' if self.build['captain']['elite'] else '✗'}\n"
            f"*Primary Specialization* | {self.build['captain']['primary_spec']} \n"
            f"*Secondary Specialization* | {self.build['captain']['secondary_spec']} \n\n\n"
        )
        if self.build['ground']['ground_desc'] != '':
            md += f"## Build Description\n\n{self.build['ground']['ground_desc']}\n\n\n"

        md += '## Personal Equipment\n\n'
        equip_table = [['&nbsp;', '****Component****', '****Notes****']]
        equip_table += md_equipment_table(self, 'ground', 'kit', 'Kit Frame', single_line=True)
        equip_table += md_equipment_table(self, 'ground', 'kit_modules', 'Kit Modules')
        equip_table += md_equipment_table(self, 'ground', 'armor', 'Body Armor', single_line=True)
        equip_table += md_equipment_table(self, 'ground', 'ev_suit', 'EV Suit', single_line=True)
        equip_table += md_equipment_table(
                self, 'ground', 'personal_shield', 'Personal Shield', single_line=True)
        equip_table += md_equipment_table(self, 'ground', 'weapons', 'Weapons')
        equip_table += md_equipment_table(self, 'ground', 'ground_devices', 'Devices')
        md += create_md_table(self, equip_table)

        md += '\n\n\n## Traits\n\n'
        trait_table = [['****Personal Ground Traits****', '****Notes****']]
        for trait in notempty(self.build['ground']['traits']):
            trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
        md += create_md_table(self, trait_table)
        md += '\n\n&#x200B;\n\n'
        trait_table = [['****Ground Reputation Traits****', '****Notes****']]
        for trait in notempty(self.build['ground']['rep_traits']):
            trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
        md += create_md_table(self, trait_table)
        md += '\n\n&#x200B;\n\n'
        trait_table = [['****Active Ground Reputation Traits****', '****Notes****']]
        for trait in notempty(self.build['ground']['active_rep_traits']):
            trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
        md += create_md_table(self, trait_table)

        md += '\n\n\n## Active Ground Duty Officers\n\n'
        doff_table = [['****Specialization****', '****Power****', '****Notes****']]
        for spec, variant in zip(
                self.build['ground']['doffs_spec'], self.build['ground']['doffs_variant']):
            if spec != '':
                doff_table.append([f"[{spec}]({wiki_url(spec, 'Specialization: ')})", variant, ''])
        md += create_md_table(self, doff_table)

        md += '\n\n\n## Away Team\n\n'
        boff_table = [['****Profession****', '****Power****', '****Notes****']]
        for profession, specialization, station in zip(
                self.build['ground']['boff_profs'], self.build['ground']['boff_specs'],
                self.build['ground']['boffs']):
            station_name = f"{profession} / {specialization}"
            boff_table += md_boff_table(self, station, station_name)
        md += create_md_table(self, boff_table)
        return md
    elif environment == 'space' and type_ == 'skills':
        md = '# Space Skills\n\n'
        skill_table = [[
            '****Engineering****', '', '',
            '****Science****', '', '',
            '****Tactical****', '&nbsp;'
        ]]
        offset = 0
        for rank_skills in self.cache.skills['space']:
            skill_table += md_skill_table_space(self, rank_skills, offset)
            skill_table.append(['&nbsp;'] + [''] * 6 + ['&nbsp;'])
            offset += 6
        md += create_md_table(self, skill_table, alignment=[':-:'] * 8)
        md += '\n\n&#x200B;\n\n'

        unlock_table = [
            [f"****[Unlocks]({wiki_url('Skill#Space_2')})****"] + [''] * 7 + ['&nbsp;']
        ]
        for career, career_name in CAREER_ABBR.items():
            row = [f"**{career_name}**"]
            for i, unlock_state in enumerate(self.build['skill_unlocks'][career]):
                if unlock_state is None:
                    row.append('')
                else:
                    unlock_slot = self.cache.skills['space_unlocks'][career][i]
                    if unlock_slot['points_required'] == 24:
                        skill_count = self.cache.skills[f"space_points_{career}"]
                        link = wiki_url(unlock_slot['name'], 'Ability: ')
                        if unlock_state is None:
                            row += ['', '', '', '&nbsp;']
                        elif unlock_state == -1:
                            row += [f"[{unlock_slot['name']}]({link})", '', '', '&nbsp;']
                        elif unlock_state == 3:
                            row += [
                                f"[{unlock_slot['name']}]({link})",
                                unlock_slot['options'][0]['name'],
                                unlock_slot['options'][1]['name'],
                                unlock_slot['options'][2]['name'],
                            ]
                        elif skill_count == 25:
                            row += [
                                f"[{unlock_slot['name']}]({link})",
                                unlock_slot['options'][unlock_state]['name']
                            ]
                        elif skill_count == 26:
                            row.append(f"[{unlock_slot['name']}]({link})")
                            enhancements = [
                                unlock_slot['options'][0]['name'],
                                unlock_slot['options'][1]['name'],
                                unlock_slot['options'][2]['name'],
                                '&nbsp;'
                            ]
                            enhancements.pop(unlock_state)
                            row += enhancements
                    else:
                        row.append(unlock_slot['nodes'][unlock_state]['name'])
            if row[-1] == '':
                row[-1] = '&nbsp;'
            unlock_table.append(row)
        md += create_md_table(self, unlock_table)
        return md
    elif environment == 'ground' and type_ == 'skills':
        md = '# Ground Skills\n\n'
        skill_table = [['****Skill****', '**I**', '**II**']]
        id_offset = 0
        for skill in self.cache.skills['ground']:
            row = [f"[{skill['nodes'][0]['name']}]({skill['link']})"]
            if self.build['ground_skills'][skill['tree']][id_offset]:
                row.append('[X]')
            else:
                row.append('[&nbsp;&nbsp;&nbsp;]')
            if self.build['ground_skills'][skill['tree']][id_offset + 1]:
                row.append('[X]')
            else:
                row.append('[&nbsp;&nbsp;&nbsp;]')
            skill_table.append(row)
            if skill['tree'] < 2 and id_offset == 4 or skill['tree'] >= 2 and id_offset == 2:
                id_offset = 0
            else:
                id_offset += 2
        md += create_md_table(self, skill_table, alignment=[':--', ':-:', ':-:'])
        md += '\n\n&#x200B;\n\n'

        unlock_table = [['', f"****[Unlocks]({wiki_url('Skill#Ground_2')})****", '']]
        for unlock, unlock_state in zip(
                self.cache.skills['ground_unlocks'], self.build['skill_unlocks']['ground']):
            if unlock_state is not None:
                unlock_table.append(['', unlock['nodes'][unlock_state]['name'], ''])
        md += create_md_table(self, unlock_table, alignment=['', ':-:', ''])
        return md
