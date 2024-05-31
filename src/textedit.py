from re import sub as re_sub
from html import unescape


def dewikify(text: str, remove_formatting: bool = False) -> str:
    """
    Unescapes wiki formatting.

    Parameters:
    - :param text: text to dewikify
    - :param remove_formatting: set to True to remove all formatting tags (HTML and wiki markup)
    """
    if text is None or text == '':
        return ''
    text = unescape(unescape(text))
    # text = text.replace('&amp;', '&')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&#34;', '"')
    # text = text.replace('&#39;', "'")
    # text = text.replace('&#039;', "'")
    text = text.replace('&#91;', '[')
    text = text.replace('&#93;', ']')
    text = text.replace('&quot;', '"')
    # clean up wikitext
    text = text.replace('\x7f', '')
    # \u007f'&quot;`UNIQ--nowiki-00000000-QINU`&quot;'\u007f
    text = re_sub('\'"`UNIQ--nowiki-0000000.-QINU`"\'', '*', text)
    text = re_sub('\'"`UNIQ--nowiki-0000001.-QINU`"\'', '*', text)
    text = re_sub('\'"`UNIQ--nowiki-0000002.-QINU`"\'', '*', text)
    text = re_sub('\'"`UNIQ--nowiki-0000003.-QINU`"\'', '*', text)
    text = re_sub('\'"`UNIQ--nowiki-0000004.-QINU`"\'', '*', text)
    text = re_sub(r'\[\[(.*?\|)?(.*?)\]\]', r'\2', text)
    text = text.replace('[[', '')
    text = text.replace(']]', '')
    text = text.replace('{{lc: ', '').replace('{{lc:', '')
    text = text.replace('{{ucfirst: ', '').replace('{{ucfirst:', '')
    text = text.replace('{{', '').replace('}}', '')
    text = text.replace('&#42;', '*')
    text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
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
    name = re_sub(r'(∞.*)|(Mk X.*)|(\[.*].*)|(MK X.*)|(-S$)', '', name).strip()
    return name
