import copy

from PySide6.QtGui import QFont

WEIGHT_CONVERSION = {
    'normal': QFont.Weight.Normal,
    'bold': QFont.Weight.Bold,
    'extrabold': QFont.Weight.ExtraBold,
    'medium': QFont.Weight.Medium
}


def get_style(self, widget, override: dict = {}) -> str:
    """
    Returns style sheet according to default style of widget with override style.

    Parameters:
    - :param widget: None or str -> name of the widget style in self.theme (may be empty or None if
    only the style in override should be applied)
    - :param override: dict -> contains additional style (optional)

    :return: str containing css style sheet
    """
    if widget is None or widget == '':
        return get_css(self, override)
    elif widget != 'app' and widget != 'defaults' and widget != 's.c' and widget in self.theme:
        if len(override) > 0:
            style = merge_style(self, self.theme[widget], override)
        else:
            style = self.theme[widget]
        return get_css(self, style)


def get_style_class(self, class_name: str, widget, override={}) -> str:
    """
    Returns style sheet according to default style of widget with override style. Style only
    applies to class_name. Sub-controls, pseudo-states and descendant selectors (marked with "~")
    defined in self.theme and override are correctly handled.

    Parameters:
    - :param class_name: str -> name of the widget to be styled
    - :param widget: None or str -> name of the widget style in self.theme (may be empty or None if
    only the style in override should be applied)
    - :param override: dict -> contains additional style (optional)

    :return: str containing css style sheet
    """
    if widget is None or widget == '':
        style = override
    elif widget != 'app' and widget != 'defaults' and widget != 's.c' and widget in self.theme:
        if len(override) > 0:
            style = merge_style(self, self.theme[widget], override)
        else:
            style = self.theme[widget]
    else:
        raise KeyError(
                f'Parameter widget=`{widget}` must be None or key of self.theme '
                'except `app` or `defaults`.')
    main = f'{class_name} {{{get_css(self, style)}}}'
    for k, v in style.items():
        if k.startswith(':'):
            main += f''' {class_name}{k} {{{get_css(self, v)}}}'''
        elif k.startswith('~'):
            main += f' {get_style_class(self, f"{class_name} {k[1:]}", None, v)}'
    return main


def merge_style(self, s1: dict, s2: dict) -> dict:
    """
    Returns new dictionary where the given styles are merged.
    Up to one sub-dictionary is merged recursively.

    Parameters:
    - :param s1: Style-dict 1
    - :param s2: Style-dict 2

    :return: merged dictionary
    """
    result = copy.deepcopy(s1)
    for k, v in s2.items():
        if k in result.keys() and isinstance(result[k], dict) and isinstance(v, dict):
            result[k].update(v)
            continue
        result[k] = v
    return result


def get_css(self, style: dict) -> str:
    """
    Converts style dictionary into css style sheet. Escapes '@' - shortcuts with their respective
    values.
    """
    css = str()
    ui_scale = self.config['ui_scale']
    for key, val in style.items():
        if isinstance(val, str) and val.startswith('@'):
            v = self.theme['defaults'][val[1:]]
        else:
            v = val
        if key.startswith(':') or key.startswith('~') or key == 'font':
            continue
        elif isinstance(v, int):
            css += f'{key}:{v * ui_scale}px;'
        elif isinstance(v, tuple):
            css += f'''{key}:{'px '.join(map(lambda s: str(s * ui_scale), v))}px;'''
        else:
            css += f'{key}:{v};'
    return css


def theme_font(self, key, font_spec=()) -> QFont:
    """
    Returns QFont object with font specified in self.theme or font_spec. Adds default fallback font
    families.

    Parameters:
    - :param key: key in self.theme to access font tuple like: self.theme[key]['font']
    - :param font_spec: font tuple consisting of family, size and weight OR font shortcut (optional)

    :return: configured QFont object
    """
    try:
        if len(font_spec) != 3 and isinstance(font_spec, tuple):
            font_spec = self.theme[key]['font']
        if isinstance(font_spec, str) and font_spec.startswith('@'):
            font = self.theme['defaults'][font_spec[1:]]
        else:
            font = font_spec
    except KeyError:
        font = self.theme['app']['font']
    font_family = (font[0], *self.theme['app']['font-fallback'])
    font_size = int(font[1] * self.config['ui_scale'])
    try:
        font_weight = WEIGHT_CONVERSION[font[2]]
    except KeyError:
        font_weight = QFont.Weight.Normal
    return QFont(font_family, font_size, font_weight)


def create_style_sheet(self, d: dict) -> str:
    """
    Creates Stylesheet from dictionary. Dictionary keys represent css selector.

    Parameters:
    - :param d: dict -> style dictionary

    :return: string containing css sheet
    """
    style = str()
    for s, v in d.items():
        style += f'{s} {{{get_css(self, v)}}}'
    return style
