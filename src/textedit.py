from re import sub as re_sub


def get_tooltip(self, name: str, type_: str, environment: str = 'space'):
    """
    """
    if type_ == 'rep_traits':
        return self.cache.traits[environment]['rep'][name]['tooltip']
    elif type_ == 'traits':
        return self.cache.traits[environment]['personal'][name]['tooltip']
    elif type_ == 'active_rep_traits':
        return self.cache.traits[environment]['active_rep'][name]['tooltip']
    elif type_ == 'starship_traits':
        return self.cache.starship_traits[name]['tooltip']
    else:
        return 'Something is wrong!'


# --------------------------------------------------------------------------------------------------
# static functions
# --------------------------------------------------------------------------------------------------


def create_equipment_tooltip(
        item: dict, head_style: str, subhead_style: str, who_style: str, tags) -> str:
    """
    """
    tooltip = ''
    if item['who'] is not None:
        tooltip += f"<p style='{who_style}'>{item['who']}</p>"
    for i in range(1, 10, 1):
        if item[f'head{i}'] is not None:
            tooltip += f"<p style='{head_style}'>{format_wikitext(dewikify(item[f'head{i}']))}</p>"
        if item[f'subhead{i}'] is not None:
            tooltip += (
                    f"<p style='{subhead_style}'>"
                    f"{format_wikitext(dewikify(item[f'subhead{i}']))}</p>")
        if item[f'text{i}'] is not None:
            tooltip += (
                    f"<p style='margin:0'>"
                    f"{parse_wikitext(dewikify(item[f'text{i}']), tags)}</p>")
    return tooltip


def create_trait_tooltip(
        name: str, description: str, type_: str, environment: str, head_style: str,
        subhead_style: str, tags) -> str:
    """
    """
    if type_ == 'personal':
        tooltip = (
                f"<p style='{head_style}'>{name}</p><p style='{subhead_style}'>"
                f"Personal {environment.capitalize()} Trait</p><p>"
                f"{parse_wikitext(dewikify(description), tags)}</p>")
    elif type_ == 'rep':
        tooltip = (
                f"<p style='{head_style}'>{name}</p><p style='{subhead_style}'>"
                f"{environment.capitalize()} Reputation Trait</p><p>"
                f"{parse_wikitext(dewikify(description), tags)}</p>")
    elif type_ == 'active_rep':
        tooltip = (
                f"<p style='{head_style}'>{name}</p><p style='{subhead_style}'>"
                f"Active {environment.capitalize()} Reputation Trait</p><p style='margin:0'>"
                f"{parse_wikitext(dewikify(description), tags)}</p>")
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
