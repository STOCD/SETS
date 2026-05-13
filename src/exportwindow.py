from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import QApplication, QDialog, QPlainTextEdit, QWidget

from .buildmanager import BuildManager
from .cargomanager import CargoManager
from .constants import AHCENTER, ALEFT, ATOP, BOFF_RANKS_MD, CAREER_ABBR, SMINMAX, SMINMIN
from .textedit import wiki_url
from .theme import AppTheme
from .widgetbuilder import create_button_series2, create_frame2, create_label2
from .widgets import notempty, VBoxLayout


class ExportWindow(QDialog):
    """
    Holds Export Window
    """
    def __init__(
            self, theme: AppTheme, parent_window: QWidget, build: BuildManager,
            cargo: CargoManager):
        super().__init__(parent=parent_window)
        self._window: QWidget = parent_window
        self._build: BuildManager = build
        self._cargo: CargoManager = cargo
        thick = theme['app']['frame_thickness'] * theme.scale
        dialog_layout = VBoxLayout(margins=thick)
        main_frame = create_frame2(theme, size_policy=SMINMIN)
        dialog_layout.addWidget(main_frame)
        main_layout = VBoxLayout(margins=thick, spacing=thick)
        content_frame = create_frame2(theme, size_policy=SMINMIN)
        content_layout = VBoxLayout(spacing=thick)
        content_layout.setAlignment(ATOP)

        header_label = create_label2(theme, 'Markdown Export:', 'label_heading')
        content_layout.addWidget(header_label, alignment=ALEFT)
        self._md_textedit = QPlainTextEdit()
        button_def = {
            'default': {'margin-top': 0},
            'Space Build': {
                'callback': lambda: self.update_export('space', 'build')
            },
            'Ground Build': {
                'callback': lambda: self.update_export('ground', 'build')
            },
            'Space Skills': {
                'callback': lambda: self.update_export('space', 'skills')
            },
            'Ground Skills': {
                'callback': lambda: self.update_export('ground', 'skills')
            },
        }
        top_buttons = create_button_series2(theme, button_def)
        top_buttons.setAlignment(AHCENTER)
        content_layout.addLayout(top_buttons)
        self._md_textedit.setSizePolicy(SMINMIN)
        self._md_textedit.setStyleSheet(theme.get_style_class('QPlainTextEdit', 'textedit'))
        self._md_textedit.setFont(theme.get_font('textedit'))
        self._md_textedit.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        content_layout.addWidget(self._md_textedit, stretch=1)
        content_frame.setLayout(content_layout)
        main_layout.addWidget(content_frame, stretch=1)

        separator = create_frame2(theme, style='light_frame', size_policy=SMINMAX)
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)
        footer_button_def = {
            'Copy': {'callback': self.copy_current_markdown},
            'Close': {'callback': lambda: self.done(0)}
        }
        footer_buttons = create_button_series2(theme, footer_button_def)
        footer_buttons.setAlignment(AHCENTER)
        main_layout.addLayout(footer_buttons)
        main_frame.setLayout(main_layout)

        self.setLayout(dialog_layout)
        self.setWindowTitle('SETS - Markdown Export')
        self.setStyleSheet(theme.get_style('dialog_window'))

    def invoke(self):
        """
        Shows Export Window.
        """
        window_rect = self._window.geometry()
        self.setGeometry(
            window_rect.x() + window_rect.width() * 0.25,
            window_rect.y() + window_rect.height() * 0.25,
            window_rect.width() * 0.5,
            window_rect.height() * 0.5)
        self.update_export('space', 'build')
        self.open()

    def update_export(self, environment: str, type_: str):
        """
        Updates text output area with newly generated markdown output.

        Parameters:
        - :param environment: `space` or `ground`
        - :param type_: `build` or `skills`
        """
        self._md_textedit.setPlainText(self.get_build_markdown(environment, type_))

    def copy_current_markdown(self):
        """
        Copies currently displayed mardown to application clipboard.
        """
        QApplication.clipboard().setText(self._md_textedit.toPlainText())

    def create_md_table(self, table: list[list[str]], alignment: list = []) -> str:
        """
        Creates markdown-formatted table from two-dimensional list

        Parameters:
        - :param table: two-dimenional list representing the table
        - :param alignment: contains column alignment codes for the table
        """
        text = '|'.join(table[0]) + '\n'
        if len(alignment) == 0:
            text += '|'.join([':--'] * len(table[0])) + '\n'
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
            item = self._build[environment][key][0]
            if item is not None and item != '':
                section[0].append(
                    f"[{item['item']} {item['mark']} {''.join(notempty(item['modifiers']))}]"
                    f"({wiki_url(self._cargo.equipment[key][item['item']]['Page'])})")
            else:
                section[0].append('')
            section[0] += [''] * extra_cols
        else:
            category_items = self._build[environment][key]
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
                        f"({wiki_url(self._cargo.equipment[key][item['item']]['Page'])})")
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
                if self._build['space_skills'][skill['career']][offsets[skill['career']]]:
                    unlocked_skills += '[X] > '
                else:
                    unlocked_skills += '[&nbsp;&nbsp;&nbsp;] > '
                if self._build['space_skills'][skill['career']][offsets[skill['career']] + 1]:
                    unlocked_skills += '[X] > '
                else:
                    unlocked_skills += '[&nbsp;&nbsp;&nbsp;] > '
                if self._build['space_skills'][skill['career']][offsets[skill['career']] + 2]:
                    unlocked_skills += '[X]'
                else:
                    unlocked_skills += '[&nbsp;&nbsp;&nbsp;]'
                section[1].append(unlocked_skills)
            elif skill['grouping'] == 'pair+1':
                section[0].append(skill['skill'][0])
                unlocked_skills = ''
                if self._build['space_skills'][skill['career']][offsets[skill['career']] + 1]:
                    unlocked_skills += f"[[X]]({skill['link'][1]}) < "
                else:
                    unlocked_skills += '[&nbsp;&nbsp;&nbsp;] < '
                if self._build['space_skills'][skill['career']][offsets[skill['career']]]:
                    unlocked_skills += f"[[X]]({skill['link'][0]}) > "
                else:
                    unlocked_skills += '[&nbsp;&nbsp;&nbsp;] > '
                if self._build['space_skills'][skill['career']][offsets[skill['career']] + 2]:
                    unlocked_skills += f"[[X]]({skill['link'][2]})"
                else:
                    unlocked_skills += '[&nbsp;&nbsp;&nbsp;]'
                section[1].append(unlocked_skills)
            elif skill['grouping'] == 'separate':
                section[0].append(f"[{skill['skill'][0]}]({skill['link']})")
                unlocked_skills = ''
                if self._build['space_skills'][skill['career']][offsets[skill['career']] + 1]:
                    unlocked_skills += '[X] < '
                else:
                    unlocked_skills += '[&nbsp;&nbsp;&nbsp;] < '
                if self._build['space_skills'][skill['career']][offsets[skill['career']]]:
                    unlocked_skills += '[X] > '
                else:
                    unlocked_skills += '[&nbsp;&nbsp;&nbsp;] > '
                if self._build['space_skills'][skill['career']][offsets[skill['career']] + 2]:
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
                f"*Ship Name* | {self._build['space']['ship_name']} \n"
                f"*Ship Class* | {self._build['space']['ship']} \n"
                f"*Ship Tier* | {self._build['space']['tier']} \n"
                f"*Player Career* | {self._build['captain']['career']} \n"
                f"*Elite Captain* | {'✓' if self._build['captain']['elite'] else '✗'}\n"
                f"*Player Species* | {self._build['captain']['species']} \n"
                f"*Primary Specialization* | {self._build['captain']['primary_spec']} \n"
                f"*Secondary Specialization* | {self._build['captain']['secondary_spec']} \n\n\n"
            )
            if self._build['space']['ship_desc']:
                md += f"## Build Description\n\n{self._build['space']['ship_desc']}\n\n\n"

            md += '## Ship Equipment\n\n'
            equip_table = [['**Basic Information**', '**Component**', '**Notes**']]
            equip_table += self.md_equipment_table('space', 'fore_weapons', 'Fore Weapons')
            equip_table += self.md_equipment_table('space', 'aft_weapons', 'Aft Weapons')
            equip_table += self.md_equipment_table(
                'space', 'deflector', 'Deflector', single_line=True)
            if self._build['space']['sec_def'][0]:
                equip_table += self.md_equipment_table(
                    'space', 'sec_def', 'Secondary Deflector', single_line=True)
            equip_table += self.md_equipment_table(
                    'space', 'engines', 'Impulse Engines', single_line=True)
            equip_table += self.md_equipment_table('space', 'core', 'Warp', single_line=True)
            equip_table += self.md_equipment_table('space', 'shield', 'Shield', single_line=True)
            equip_table += self.md_equipment_table('space', 'devices', 'Devices')
            if self._build['space']['experimental'][0]:
                equip_table += self.md_equipment_table(
                        'space', 'experimental', 'Experimental Weapon', single_line=True)
            if self._build['space']['hangars'][0] or self._build['space']['hangars'][1]:
                equip_table += self.md_equipment_table('space', 'hangars', 'Hangars')
            equip_table += self.md_equipment_table('space', 'uni_consoles', 'Universal Consoles')
            equip_table += self.md_equipment_table('space', 'eng_consoles', 'Engineering Consoles')
            equip_table += self.md_equipment_table('space', 'sci_consoles', 'Science Consoles')
            equip_table += self.md_equipment_table('space', 'tac_consoles', 'Tactical Consoles')
            md += self.create_md_table(equip_table)

            md += '\n\n\n## Bridge Officer Stations\n\n'
            boff_table = [['**Profession**', '**Power**', '**Notes**']]
            for specs, station in zip(
                    self._build['space']['boff_specs'], self._build['space']['boffs']):
                if any(specs):
                    station_name = BOFF_RANKS_MD[station.count(None)] + ' ' + specs[0]
                    if specs[1] != '':
                        station_name += ' / ' + specs[1]
                    boff_table += self.md_boff_table(station, station_name)
            md += self.create_md_table(boff_table)

            md += '\n\n\n## Traits\n\n'
            trait_table = [['**Starship Traits**', '**Notes**']]
            for trait in notempty(self._build['space']['starship_traits']):
                trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
            md += self.create_md_table(trait_table)
            md += '\n\n&#x200B;\n\n'
            trait_table = [['**Personal Space Traits**', '**Notes**']]
            for trait in notempty(self._build['space']['traits']):
                trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
            md += self.create_md_table(trait_table)
            md += '\n\n&#x200B;\n\n'
            trait_table = [['**Space Reputation Traits**', '**Notes**']]
            for trait in notempty(self._build['space']['rep_traits']):
                trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
            md += self.create_md_table(trait_table)
            md += '\n\n&#x200B;\n\n'
            trait_table = [['**Active Space Reputation Traits**', '**Notes**']]
            for trait in notempty(self._build['space']['active_rep_traits']):
                trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
            md += self.create_md_table(trait_table)

            md += '\n\n\n## Active Space Duty Officers\n\n'
            doff_table = [['**Specialization**', '**Power**', '**Notes**']]
            for spec, variant in zip(
                    self._build['space']['doffs_spec'], self._build['space']['doffs_variant']):
                if spec != '':
                    doff_table.append(
                        [f"[{spec}]({wiki_url(spec, 'Specialization: ')})", variant, ''])
            md += self.create_md_table(doff_table)
            return md
        elif environment == 'ground' and type_ == 'build':
            md = (
                f"# GROUND BUILD\n\n**Basic Information** | **Data** \n:--- | :--- \n"
                f"*Player Name* | {self._build['captain']['name']} \n"
                f"*Player Species* | {self._build['captain']['species']} \n"
                f"*Player Career* | {self._build['captain']['career']} \n"
                f"*Elite Captain* | {'✓' if self._build['captain']['elite'] else '✗'}\n"
                f"*Primary Specialization* | {self._build['captain']['primary_spec']} \n"
                f"*Secondary Specialization* | {self._build['captain']['secondary_spec']} \n\n\n"
            )
            if self._build['ground']['ground_desc'] != '':
                md += f"## Build Description\n\n{self._build['ground']['ground_desc']}\n\n\n"

            md += '## Personal Equipment\n\n'
            equip_table = [['&nbsp;', '**Component**', '**Notes**']]
            equip_table += self.md_equipment_table('ground', 'kit', 'Kit Frame', single_line=True)
            equip_table += self.md_equipment_table('ground', 'kit_modules', 'Kit Modules')
            equip_table += self.md_equipment_table(
                'ground', 'armor', 'Body Armor', single_line=True)
            equip_table += self.md_equipment_table('ground', 'ev_suit', 'EV Suit', single_line=True)
            equip_table += self.md_equipment_table(
                'ground', 'personal_shield', 'Personal Shield', single_line=True)
            equip_table += self.md_equipment_table('ground', 'weapons', 'Weapons')
            equip_table += self.md_equipment_table('ground', 'ground_devices', 'Devices')
            md += self.create_md_table(equip_table)

            md += '\n\n\n## Traits\n\n'
            trait_table = [['**Personal Ground Traits**', '**Notes**']]
            for trait in notempty(self._build['ground']['traits']):
                trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
            md += self.create_md_table(trait_table)
            md += '\n\n&#x200B;\n\n'
            trait_table = [['**Ground Reputation Traits**', '**Notes**']]
            for trait in notempty(self._build['ground']['rep_traits']):
                trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
            md += self.create_md_table(trait_table)
            md += '\n\n&#x200B;\n\n'
            trait_table = [['**Active Ground Reputation Traits**', '**Notes**']]
            for trait in notempty(self._build['ground']['active_rep_traits']):
                trait_table.append([f"[{trait['item']}]({wiki_url(trait['item'], 'Trait: ')})", ''])
            md += self.create_md_table(trait_table)

            md += '\n\n\n## Active Ground Duty Officers\n\n'
            doff_table = [['**Specialization**', '**Power**', '**Notes**']]
            for spec, variant in zip(
                    self._build['ground']['doffs_spec'], self._build['ground']['doffs_variant']):
                if spec != '':
                    doff_table.append(
                        [f"[{spec}]({wiki_url(spec, 'Specialization: ')})", variant, ''])
            md += self.create_md_table(doff_table)

            md += '\n\n\n## Away Team\n\n'
            boff_table = [['**Profession**', '**Power**', '**Notes**']]
            for profession, specialization, station in zip(
                    self._build['ground']['boff_profs'], self._build['ground']['boff_specs'],
                    self._build['ground']['boffs']):
                station_name = f"{profession} / {specialization}"
                boff_table += self.md_boff_table(station, station_name)
            md += self.create_md_table(boff_table)
            return md
        elif environment == 'space' and type_ == 'skills':
            md = '# Space Skills\n\n'
            skill_table = [[
                '**Engineering**', '', '',
                '**Science**', '', '',
                '**Tactical**', '&nbsp;'
            ]]
            offset = 0
            for rank_skills in self._cargo.skills['space']:
                skill_table += self.md_skill_table_space(rank_skills, offset)
                skill_table.append(['&nbsp;'] + [''] * 6 + ['&nbsp;'])
                offset += 6
            md += self.create_md_table(skill_table, alignment=[':-:'] * 8)
            md += '\n\n&#x200B;\n\n'

            unlock_table = [
                [f"**[Unlocks]({wiki_url('Skill#Space_2')})**"] + [''] * 7 + ['&nbsp;']
            ]
            for career, career_name in CAREER_ABBR.items():
                row = [f"**{career_name}**"]
                for i, unlock_state in enumerate(self._build['skill_unlocks'][career]):
                    if unlock_state is None:
                        row.append('')
                    else:
                        unlock_slot = self._cargo.skills['space_unlocks'][career][i]
                        if unlock_slot['points_required'] == 24:
                            skill_count = self._build._skill_state[f"space_points_{career}"]
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
            md += self.create_md_table(unlock_table)
            return md
        elif environment == 'ground' and type_ == 'skills':
            md = '# Ground Skills\n\n'
            skill_table = [['**Skill**', '**I**', '**II**']]
            id_offset = 0
            for skill in self._cargo.skills['ground']:
                row = [f"[{skill['nodes'][0]['name']}]({skill['link']})"]
                if self._build['ground_skills'][skill['tree']][id_offset]:
                    row.append('[X]')
                else:
                    row.append('[&nbsp;&nbsp;&nbsp;]')
                if self._build['ground_skills'][skill['tree']][id_offset + 1]:
                    row.append('[X]')
                else:
                    row.append('[&nbsp;&nbsp;&nbsp;]')
                skill_table.append(row)
                if skill['tree'] < 2 and id_offset == 4 or skill['tree'] >= 2 and id_offset == 2:
                    id_offset = 0
                else:
                    id_offset += 2
            md += self.create_md_table(skill_table, alignment=[':--', ':-:', ':-:'])
            md += '\n\n&#x200B;\n\n'

            unlock_table = [['', f"**[Unlocks]({wiki_url('Skill#Ground_2')})**", '']]
            for unlock, unlock_state in zip(
                    self._cargo.skills['ground_unlocks'], self._build['skill_unlocks']['ground']):
                if unlock_state is not None:
                    unlock_table.append(['', unlock['nodes'][unlock_state]['name'], ''])
            md += self.create_md_table(unlock_table, alignment=['', ':-:', ''])
            return md
