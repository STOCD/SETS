from re import sub as re_sub

from .constants import CAREER_ABBR, RARITY_COLORS, SKILL_PREFIXES, WIKI_URL
from .theme import TooltipCSS


def add_equipment_tooltip_header(
        item: dict[str, str], item_data: dict[str], tooltip_styles: TooltipCSS) -> str:
    """
    Adds equipment header including name, mark, modifiers, rarity and item type to the tooltip body
    and returns the complete tooltip.

    Parameters:
    - :param item: item to create the tooltip for
    - :param item_data: cargo data for the item
    - :param tooltip_styles: used to style the tooltip
    """
    rarity_color = f'color:{RARITY_COLORS[item['rarity']]};'
    head_style = tooltip_styles.equipment_name + rarity_color
    subhead_style = tooltip_styles.equipment_type_subheader + rarity_color
    item_title = item['item']
    if item['mark'] != '' and item['mark'] is not None:
        item_title += ' ' + item['mark']
    mods = ' '.join(mod for mod in item['modifiers'] if mod != '' and mod is not None)
    if mods != '':
        item_title += ' ' + mods
    tooltip = (
        f"<p style='{head_style}'>{item_title}</p><p style='{subhead_style}'>"
        f"{item['rarity']} {item_data['type']}</p>")
    return tooltip + item_data['tooltip']


def format_skill_tooltip(
        skill_name: str, skill_data: dict, node_index: int, environment: str,
        tooltip_styles: TooltipCSS) -> str:
    """
    Formats skill tooltip

    Parameters:
    - :param skill_name: name of the skill (without prefix)
    - :param skill_data: contains skill details
    - :param node_index: index of the node within the skill group
    - :param environment: "space" / "ground"
    - :param tooltip_styles: used to style the tooltip
    """
    head_style = f"{tooltip_styles.equipment_name}color:#ffd700;"
    subhead_style = f"{tooltip_styles.equipment_type_subheader}color:#ffd700;"
    if environment == 'space':
        if skill_data['grouping'] == 'column':
            prefix = SKILL_PREFIXES[node_index]
            global_description = skill_data['gdesc']
        elif skill_data['grouping'] == 'pair+1':
            if node_index == 1:
                prefix = 'Improved '
            else:
                prefix = ''
            global_description = skill_data['gdesc'][node_index]
        else:
            prefix = ''
            global_description = skill_data['gdesc'][node_index]
        return (
            f"<p style='{head_style}'>{prefix}{skill_name}</p><p style='{subhead_style}'>"
            f"{CAREER_ABBR[skill_data['career']]} {environment.capitalize()} Skill</p>"
            f"<p>{global_description}</p><p>{skill_data['nodes'][node_index]['desc']}</p>")
    elif environment == 'ground':
        return (
            f"<p style='{head_style}'>{skill_name}</p><p style='{subhead_style}'>"
            f"Ground Skill</p>"
            f"<p>{skill_data['gdesc']}</p><p>{skill_data['nodes'][node_index]['desc']}</p>")


def get_ultimate_skill_unlock_tooltip(
        unlock: dict[str], unlock_choice: int, enhancements: int, tooltip_styles: TooltipCSS):
    """
    Formats tooltip for ultimate skill unlock.

    Parameters:
    - :param unlock: contains unlock metadata and tooltips
    - :param unlock_choice: selected enhancement (`-1` for no unlock)
    - :param enhancements: number of enhancements
    - :param tooltips_styles: used to style the tooltip
    """
    enhancement_style = tooltip_styles.skill_ultimate_name
    tooltip = (
        f"<p style='{tooltip_styles.equipment_name}color:#ffd700;'>{unlock['name']}</p>"
        f"<p style='{tooltip_styles.equipment_type_subheader}color:#ffd700;'>Space Skill</p>"
        f"<p>{unlock['desc']}</p>")
    if enhancements == 1:
        tooltip += (
            f"<p style='{enhancement_style}'>{unlock['options'][unlock_choice]['name']}</p>"
            f"<p>{unlock['options'][unlock_choice]['desc']}</p>")
    elif enhancements == 2:
        e1 = (unlock_choice - 1) % 3
        e2 = (unlock_choice + 1) % 3
        tooltip += (
            f"<p style='{enhancement_style}'>{unlock['options'][e1]['name']}</p>"
            f"<p>{unlock['options'][e1]['desc']}</p>"
            f"<p style='{enhancement_style}'>{unlock['options'][e2]['name']}</p>"
            f"<p>{unlock['options'][e2]['desc']}</p>")
    elif enhancements != 0:
        for i in range(3):
            tooltip += (
                f"<p style='{enhancement_style}'>{unlock['options'][i]['name']}</p>"
                f"<p>{unlock['options'][i]['desc']}</p>")
    return tooltip


def create_equipment_tooltip(item: dict, tooltip_style: TooltipCSS) -> str:
    """
    Creates tooltip for equipment from raw item data.

    Parameters:
    - :param item: item data (from cargo table)
    - :param tooltip_style: object containing style data
    """
    tooltip = ''
    if item['who'] is not None:
        tooltip += f"<p style='{tooltip_style.equipment_who}'>{item['who']}</p>"
    for i in range(1, 10, 1):
        if item[f'head{i}'] is not None:
            tooltip += (
                f"<p style='{tooltip_style.equipment_head}'>"
                f"{format_wikitext(dewikify(item[f'head{i}']))}</p>")
        if item[f'subhead{i}'] is not None:
            tooltip += (
                f"<p style='{tooltip_style.equipment_subhead}'>"
                f"{format_wikitext(dewikify(item[f'subhead{i}']))}</p>")
        if item[f'text{i}'] is not None:
            tooltip += (
                f"<p style='margin:0'>"
                f"{parse_wikitext(dewikify(item[f'text{i}']), tooltip_style)}</p>")
    return tooltip


def create_trait_tooltip(
        name: str, description: str, type_: str, environment: str,
        styles: TooltipCSS) -> str:
    """
    Creates tooltip for trait from trait description.

    Parameters:
    - :param name: name of the trait
    - :param description: description of the trait
    - :param type_: type of the trait; one of "traits", "rep_traits", "active_rep_traits"
    - :param environment: "space" / "ground"
    - :param styles: object containing style data
    """
    if type_ == 'traits':
        tooltip = (
            f"<p style='{styles.trait_header}'>{name}</p><p style='{styles.trait_subheader}'>"
            f"Personal {environment.capitalize()} Trait</p><p>"
            f"{parse_wikitext(dewikify(description), styles)}</p>")
    elif type_ == 'rep_traits':
        tooltip = (
            f"<p style='{styles.trait_header}'>{name}</p><p style='{styles.trait_subheader}'>"
            f"{environment.capitalize()} Reputation Trait</p><p>"
            f"{parse_wikitext(dewikify(description), styles)}</p>")
    elif type_ == 'active_rep_traits':
        tooltip = (
            f"<p style='{styles.trait_header}'>{name}</p><p style='{styles.trait_subheader}'>"
            f"Active {environment.capitalize()} Reputation Trait</p><p style='margin:0'>"
            f"{parse_wikitext(dewikify(description), styles)}</p>")
    else:
        tooltip = ''
    return tooltip


def parse_wikitext(text: str, tags) -> str:
    """
    Converts wikitext lists and indentation into the html subset Qt uses. Also converts inline
    formatting

    Parameters:
    - :param text: contains the text to be formatted
    - :param tags: namedtuple with elements ul, li, indent containing css style of tags
    """
    if text is None:
        return ''
    text = text.replace('\n: *', '\n**')
    text = text.replace(':*', '**')
    html = ''
    ul_tag = f"<ul style='{tags.ul}'>"
    in_list = 0
    for textblock in text.splitlines():
        if textblock.startswith(':'):
            if in_list != 0:
                html += '</ul>' * in_list
            html += f"<p style='{tags.indent}'>{textblock[1:]}</p>"
        elif textblock.startswith('*'):
            if textblock.startswith('***') and in_list < 3:
                html += ul_tag * (3 - in_list)
                in_list = 3
            elif textblock.startswith('**'):
                if in_list < 2:
                    html += ul_tag * (2 - in_list)
                elif in_list == 3:
                    html += '</ul>'
                in_list = 2
            else:
                if in_list == 0:
                    html += ul_tag
                else:
                    html += '</ul>' * (in_list - 1)
                in_list = 1
            html += f"<li style='{tags.li}'>{textblock[in_list:]}</li>"
        else:
            if in_list != 0:
                html += '</ul>' * in_list
            if html.endswith('>') or len(html) == 0:
                html += textblock
            else:
                html += f"<br>{textblock}"
    if in_list != 0:
        html += '</ul>' * in_list

    return format_wikitext(html)


def format_wikitext(text: str) -> str:
    """
    Converts inline formatting from wikitext to html
    """
    bolditalic_html = ''
    splitted = text.split("'''''")
    for i in range(0, len(splitted) - 2, 2):
        bolditalic_html += f"{splitted[i]}<b><i>{splitted[i + 1]}</i></b>"
    bolditalic_html += splitted[-1]
    bold = ''
    splitted = bolditalic_html.split("'''")
    for i in range(0, len(splitted) - 2, 2):
        bold += f"{splitted[i]}<b>{splitted[i + 1]}</b>"
    bold += splitted[-1]
    italic = ''
    splitted = bold.split("''")
    for i in range(0, len(splitted) - 2, 2):
        italic += f"{splitted[i]}<i>{splitted[i + 1]}</i>"
    italic += splitted[-1]
    return italic


def dewikify(text: str, remove_formatting: bool = False) -> str:
    """
    Unescapes wiki formatting.

    Parameters:
    - :param text: text to dewikify
    - :param remove_formatting: set to True to remove all formatting tags (HTML and wiki markup)
    """
    if text is None or text == '':
        return ''
    # text = unescape(unescape(text))
    # text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&#34;', '"')
    # text = text.replace('&#39;', "'")
    # text = text.replace('&#039;', "'")
    text = text.replace('&#91;', '[')
    text = text.replace('&#93;', ']')
    text = text.replace('&quot;', '"')
    # \u007f'&quot;`UNIQ--nowiki-00000000-QINU`&quot;'\u007f
    if '\u007f' in text:
        text = re_sub('\u007f\'"`UNIQ--nowiki-[A-Z0-9]*?-QINU`"\'\u007f', '*', text)
        text = text.replace('\u007f', '')
    if '[[' in text:
        text = re_sub(r'\[\[(.*?\|)?(.*?)\]\]', r'\2', text)
    text = text.replace('[[', '').replace(']]', '')
    text = text.replace('{{lc: ', '').replace('{{lc:', '')
    text = text.replace('{{ucfirst: ', '').replace('{{ucfirst:', '')
    text = text.replace('{{', '').replace('}}', '')
    text = text.replace('&#42;', '*')
    # text = text.replace('\n', '<br>')
    # text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    if remove_formatting:
        text = re_sub('<.*?>', '', text)
        text = text.replace("'", '')
    return text


def compensate_json(text: str) -> str:
    """
    Unescapes known HTML entities in json text.

    Parameters:
    - :param text: text to compensate
    """
    text = text.replace('&amp;', '&')
    text = text.replace('&#039;', "'")
    text = text.replace('&#39;', "'")
    return text


def sanitize_equipment_name(name: str) -> str:
    """
    Cleans equipment name.

    Parameters:
    - :param name: name to clean
    """
    name = name.replace('&quot;', '"')
    name = name.replace('&#34;', '"')
    if '∞' in name:
        name, _ = name.split('∞', 1)
    if 'Mk X' in name:
        name, _ = name.split('Mk X', 1)
    if 'MK X' in name:
        name, _ = name.split('MK X', 1)
    if '[' in name:
        name, _ = name.split('[', 1)
    if name[-2:] == '-S':
        name = name[:-2]
    return name.strip()


def wiki_url(page_name: str, prefix: str = ''):
    return (WIKI_URL + prefix + page_name).replace(' ', '_')


def format_path(path: str):
    if len(path) < 2:
        return path
    path = path.replace(chr(92), '/')
    if path[1] == ':' and path[0] >= 'a' and path[0] <= 'z':
        path = path[0].capitalize() + path[1:]
    return path
