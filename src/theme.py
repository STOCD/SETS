import copy

from PySide6.QtGui import QFont, QIcon

WEIGHT_CONVERSION = {
    'normal': QFont.Weight.Normal,
    'bold': QFont.Weight.Bold,
    'extrabold': QFont.Weight.ExtraBold,
    'medium': QFont.Weight.Medium
}


class ThemeOptions:
    """Contains Theme options affecting the UI, but not directly related to the style"""

    __slots__ = ('box_height', 'box_width', 'default_box_height', 'default_box_width')

    def __init__(self, initial_options: dict[str] = {}):
        """
        Parameters:
        - :param initial_options: options to use instead of defaults (optional)
        """
        self.box_height: float = 64.0
        self.box_width: float = 49.0
        self.default_box_height: float = 64.0
        self.default_box_width: float = 49.0
        if len(initial_options) > 0:
            for option_name in self.__slots__:
                if option_value := initial_options.get(option_name):
                    setattr(self, option_name, option_value)


class AppTheme:
    """Encapsulates theme functions and data."""

    def __init__(self, scale: float, theme_tree: dict[str] = {}, theme_options: dict[str] = {}):
        """
        Parameters:
        - :param scale: Used to adjust font sizes, margins, paddings, etc.
        - :param theme_tree: theme data to use instead of default theme
        - :param theme_tree: options that affect the UI, but are not directly related to the style
        """
        self.scale: float = scale
        self.icons: dict[str, QIcon] = dict()
        self.opt: ThemeOptions = ThemeOptions(theme_options)
        self.opt.box_height = self.opt.default_box_height * self.scale
        self.opt.box_width = self.opt.default_box_width * self.scale
        if len(theme_tree) > 0:
            self._theme_data: dict[str, dict] = theme_tree
        else:
            self._theme_data: dict[str, dict] = self.get_default_theme() 

    def __getitem__(self, key: str):
        return self._theme_data[key]

    def get_style(self, widget: str, override: dict[str] = {}) -> str:
        """
        Returns style sheet according to default style of widget with override style. Returns
        empty string if widget style is not defined in current theme.

        Parameters:
        - :param widget: name of the widget to grab the style for from the current theme
        - :param override: contains additional style or override style to replace the default \
        style with (optional)

        :return: str containing css style sheet
        """
        if widget in self._theme_data:
            if len(override) > 0:
                style = self.merge_style(self._theme_data[widget], override)
            else:
                style = self._theme_data[widget]
            return self.get_css(style)
        else:
            return ''

    def get_style_class(self, class_name: str, widget: str, override: dict[str] = {}) -> str:
        """
        Returns style sheet according to default style of widget with override style. Style only
        applies to `class_name`. Sub-controls (prefixed with `::`), pseudo-states (prefixed with
        `:`) and descendant selectors (prefixed with `~`) defined in current theme are formatted to
        only apply to the given `class_name`. Returns empty string with wdget style is not defined
        in current theme.

        Parameters:
        - :param class_name: name of the widget class to be styled
        - :param widget: name of the widget to grab the style for from the current theme; may be \
        empty string to only apply override styles
        - :param override: contains additional style or override style to replace the default \
        style with (optional)

        :return: str containing css style sheet
        """
        if widget == '':
            style = override
        elif widget in self._theme_data:
            if len(override) > 0:
                style: dict[str] = self.merge_style(self._theme_data[widget], override)
            else:
                style: dict[str] = self._theme_data[widget]
        else:
            return ''
        style_sheet = f'{class_name} {{{self.get_css(style)}}}'
        for prop, value in style.items():
            if prop.startswith(':'):
                style_sheet += f''' {class_name}{prop} {{{self.get_css(value)}}}'''
            elif prop.startswith('~'):
                style_sheet += f' {self.get_style_class(f"{class_name} {prop[1:]}", '', value)}'
        return style_sheet

    def merge_style(self, s1: dict[str], s2: dict[str]) -> dict[str]:
        """
        Returns new dictionary where the given styles are merged. Values in the second style take
        precedence. Up to one sub-dictionary is merged recursively.

        Parameters:
        - :param s1: Style-dict 1
        - :param s2: Style-dict 2

        :return: merged dictionary
        """
        result = copy.deepcopy(s1)
        for key, value in s2.items():
            if key in result.keys() and isinstance(result[key], dict) and isinstance(value, dict):
                result[key].update(value)
                continue
            result[key] = value
        return result

    def get_css(self, style: dict[str]) -> str:
        """
        Converts style dictionary into css style sheet. Values starting with `@` are treated as
        shortcuts and replaced with values from the `default` key of the current theme. Ignores
        property `font`, sub-controls (prefixed with `::`), pseudo-states (prefixed with
        `:`) and descendant selectors (prefixed with `~`).

        Parameters:
        - :param style: dictionary containg style to be converted to css

        :return: css style sheet
        """
        style_sheet = str()
        for prop, raw_value in style.items():
            if isinstance(raw_value, str) and raw_value.startswith('@'):
                prop_value = self._theme_data['defaults'][raw_value[1:]]
            else:
                prop_value = raw_value
            if prop.startswith(':') or prop.startswith('~') or prop == 'font':
                continue
            elif isinstance(prop_value, int):
                style_sheet += f'{prop}:{prop_value * self.scale}px;'
            elif isinstance(prop_value, tuple):
                scaled_values = map(lambda s: str(s * self.scale), prop_value)
                style_sheet += f'''{prop}:{'px '.join(scaled_values)}px;'''
            else:
                style_sheet += f'{prop}:{prop_value};'
        return style_sheet

    def get_font(self, widget: str, font_spec: tuple[str, int, str] | str = ()) -> QFont:
        """
        Returns QFont object with font specified in current theme or font_spec. Adds default
        fallback font families.

        Parameters:
        - :param widget: name of style to get font from
        - :param font_spec: font tuple consisting of family, size and weight OR font shortcut \
        (optional)

        :return: configured QFont object
        """
        try:
            if len(font_spec) != 3 and isinstance(font_spec, tuple):
                font_spec = self._theme_data[widget]['font']
            if isinstance(font_spec, str) and font_spec.startswith('@'):
                font = self._theme_data['defaults'][font_spec[1:]]
            else:
                font = font_spec
        except KeyError:
            font = self._theme_data['app']['font']
        font_family = (font[0], *self._theme_data['app']['font-fallback'])
        font_size = int(font[1] * self.scale)
        font_weight = WEIGHT_CONVERSION[font[2]]
        font = QFont(font_family, font_size, font_weight)
        font.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        return font

    def create_style_sheet(self, d: dict[str, dict]) -> str:
        """
        Creates Stylesheet from dictionary. Dictionary keys represent css selector. Ignores
        property `font`, sub-controls (prefixed with `::`), pseudo-states (prefixed with
        `:`) and descendant selectors (prefixed with `~`).

        Parameters:
        - :param d: style dictionary

        :return: string containing style sheet
        """
        style_sheet = str()
        for prop, prop_value in d.items():
            style_sheet += f'{prop} {{{self.get_css(prop_value)}}}'
        return style_sheet

    def get_default_theme(self) -> dict[str, dict]:
        """
        Returns default theme.
        """
        return {
            # general style
            'app': {
                'bg': '#1a1a1a',
                'fg': '#eeeeee',
                'sets': '#c59129',
                'font': ('Overpass', 11, 'normal'),
                'heading': ('Overpass', 14, 'bold'),
                'subhead': ('Overpass', 12, 'medium'),
                'font-fallback': ('Yu Gothic UI', 'Nirmala UI', 'Microsoft YaHei UI', 'sans-serif'),
                'frame_thickness': 8,
                # this styles every item of the given type
                'style': {
                    # scroll bar trough (invisible)
                    'QScrollBar': {
                        'background': 'none',
                        'border-style': 'none',
                        'border-radius': 0,
                        'margin': 0
                    },
                    'QScrollBar:vertical': {
                        'width': 8,
                    },
                    'QScrollBar:horizontal': {
                        'height': 8,
                    },
                    # space above and below the scrollbar handle
                    'QScrollBar::add-page, QScrollBar::sub-page': {
                        'background': 'none'
                    },
                    # scroll bar handle
                    'QScrollBar::handle': {
                        'background-color': 'rgba(100,100,100,.75)',
                        'border-radius': 4,
                        'border': 'none'
                    },
                    # scroll bar arrow buttons
                    'QScrollBar::add-line, QScrollBar::sub-line': {
                        'height': 0  # hiding the arrow buttons
                    }
                }
            },
            # shortcuts, @bg -> means bg in this sub-dictionary
            'defaults': {
                'bg': '#1a1a1a',  # background
                'mbg': '#242424',  # medium background
                'lbg': '#404040',  # light background
                'sets': '#c59129',  # accent
                'lsets': '#60c59129',  # light accent
                'font': ('Overpass', 11, 'normal'),
                'heading': ('Overpass', 14, 'bold'),
                'subhead': ('Overpass', 12, 'medium'),
                'small_text': ('Overpass', 10, 'normal'),
                'fg': '#eeeeee',  # foreground (usually text)
                'mfg': '#bbbbbb',  # medium foreground
                'bc': '#888888',  # border color
                'bw': 1,  # border width
                'br': 2,  # border radius
                'sep': 2,  # seperator -> width of major seperating lines
                'margin': 10,  # default margin between widgets
                'csp': 5,  # child spacing -> content margin
                'isp': 15,  # item spacing
            },
            # dark frame
            'frame': {
                'background-color': '@bg',
                'border-style': 'none',
                'margin': 0,
                'padding': 0
            },
            # medium frame
            'medium_frame': {
                'background-color': '@mbg',
                'margin': 0,
                'padding': 0
            },
            # light frame
            'light_frame': {
                'background': '@lbg',
                'margin': 0,
                'padding': 0
            },
            # default text (non-button, non-entry, non table)
            'label': {
                'color': '@fg',
                'margin': (3, 0, 3, 0),
                'qproperty-indent': '0',  # disables auto-indent
                'border-style': 'none',
                'font': '@font'
            },
            # default text (non-button, non-entry, non table)
            'hint_label': {
                'color': '@mfg',
                'margin': (3, 0, 3, 0),
                'qproperty-indent': '0',  # disables auto-indent
                'border-style': 'none',
                'font': '@font'
            },
            # heading label
            'label_heading': {
                'color': '@fg',
                'qproperty-indent': '0',
                'border-style': 'none',
                'font': '@heading'
            },
            # label for subheading
            'label_subhead': {
                'color': '@fg',
                'qproperty-indent': '0',
                'border-style': 'none',
                'margin-bottom': 3,
                'font': '@subhead'
            },
            # default button
            'button': {
                'background-color': 'none',
                'color': '@fg',
                'text-decoration': 'none',
                'border-width': '@bw',
                'border-style': 'solid',
                'border-color': '@sets',
                'margin': (3, 3, 3, 3),
                'padding': (2, 5, 0, 5),
                'font': ('Overpass', 13, 'medium'),
                ':hover': {
                    'border-color': '@bc'
                },
                ':disabled': {
                    'color': '@bc'
                },
                # Tooltip
                '~QToolTip': {
                    'background-color': '@mbg',
                    'border-style': 'solid',
                    'border-color': '@lbg',
                    'border-width': '@bw',
                    'padding': (0, 0, 0, 0),
                    'color': '@fg',
                    'font': 'Overpass'
                }
            },
            # heavy button
            'heavy_button': {
                'background-color': '@sets',
                'color': '@fg',
                'text-decoration': 'none',
                'border-width': '@bw',
                'border-style': 'solid',
                'border-color': '@sets',
                'margin': (3, 3, 3, 3),
                'padding': (2, 5, 0, 5),
                'font': ('Overpass', 13, 'bold'),
                ':hover': {
                    'background-color': '@mbg'
                },
                ':disabled': {
                    'color': '@bc'
                }
            },
            # build item button
            'item': {
                'background-color': '#242424',
                'border-width': 1,
                'border-color': '#888888',
                'border-highlight-color': '#ffd700'
            },
            # build item button
            'item_dark': {
                'background-color': '#1a1a1a',
                'border-width': 1,
                'border-color': '#404040',
            },
            # checkbox
            'checkbox': {
                '::indicator': {
                    'width': 16,
                    'height': 16,
                    'border-style': 'solid',
                    'border-width': '@bw',
                    'border-color': '@bc',
                    'background-color': '@lbg',
                },
                '::indicator:hover': {
                    'border-color': '@sets'
                },
                '::indicator:checked': {
                    'image': 'url(local/check.svg)'
                },
                '::indicator:unchecked': {
                    'image': 'url(local/uncheck.svg)',
                }
            },
            # holds sub-pages
            'tabber': {
                'background-color': 'none',
                'border': 'none',
                'margin': 0,
                'padding': 0,
                '::pane': {
                    'border': 'none',
                }
            },
            # default tabber buttons (hidden)
            'tabber_tab': {
                '::tab': {
                    'height': 0,
                    'width': 0
                }
            },
            # combo box
            'combobox': {
                'border-style': 'solid',
                'border-width': '@bw',
                'border-color': '@bc',
                'background-color': '@bg',
                'padding': (1, 5, 1, 5),
                'color': '@fg',
                'font': '@subhead',
                '::down-arrow': {
                    'image': 'url(local/thick-chevron-down.svg)',
                    'width': '@margin',
                },
                '::drop-down': {
                    'border-style': 'none',
                    'padding': (2, 2, 2, 2)
                },
                '~QAbstractItemView': {
                    'background-color': '@mbg',
                    'border-style': 'solid',
                    'border-color': '@bc',
                    'border-width': '@bw',
                    'border-radius': '@br',
                    'color': '@fg',
                    'outline': '0',
                    '::item': {
                        'border-width': '@bw',
                        'border-style': 'solid',
                        'border-color': '@mbg',
                    },
                    '::item:hover': {
                        'border-color': '@sets',
                    },
                }
            },
            # additional style for doff combobox
            'doff_combo': {
                'color': '@fg',
                'border-style': 'none',
                'border-width': 0,
                'margin': 0,
                'font': '@small_text'
            },
            # additional style for boff combobox
            'boff_combo': {
                'font': '@font',
                ':disabled': {
                    'border-color': '@bg',
                    'border-left-width': 0,
                    'padding-left': 0
                },
                '::down-arrow:disabled': {
                    'image': 'none',
                    'width': '@margin',
                },
            },
            # auto-completion popup of combobox
            'popup': {
                'background-color': '@mbg',
                'border-style': 'solid',
                'border-color': '@bc',
                'border-width': '@bw',
                'border-radius': '@br',
                'color': '@fg',
                'outline': '0',
                '::item': {
                    'border-width': '@bw',
                    'border-style': 'solid',
                    'border-color': '@mbg',
                },
                '::item:hover': {
                    'border-color': '@sets',
                },
            },
            # line of user-editable text
            'entry': {
                'background-color': '@mbg',
                'color': '@fg',
                'border-width': '@bw',
                'border-style': 'solid',
                'border-color': '@bc',
                'font': '@subhead',
                'selection-background-color': '@lsets',
                # cursor is inside the line
                ':focus': {
                    'border-color': '@sets'
                },
                ':hover': {
                    'background-color': '@lbg'
                }
            },
            # for item tooltips
            'infobox': {
                'background-color': '#000000',
                'border-style': 'none',
                'color': '@fg',
                # 'margin': 0,
                # 'padding': 0,
            },
            'infobox_frame': {
                'background-color': '#000000',
                'border-style': 'solid',
                'border-width': '@bw',
                'border-color': '@mbg',
                'border-radius': '@br',
                # 'margin': 0,
                # 'padding': '@sep',
            },
            # tooltip for TooltipLabel
            'label_tooltip': {
                'color': '@fg',
                'background-color': '@bg',
                'border-color': '@lbg',
                'border-radius': '@br',
                'border-style': 'solid',
                'border-width': '@bw',
                'font': '@font',
                'padding': 2,
                'qproperty-indent': '0',  # disables auto-indent
            },
            # for formatting tooltip text, will contain css from tooltip_def
            'tooltip': {},
            'tooltip_def': {
                'indent': {
                    'margin': (0, 0, 0, 20),
                },
                'ul': {
                    'margin': (0, 0, 0, 20),
                    '-qt-list-indent': '0',
                },
                'li': {
                    'margin-bottom': 1,
                },
                'boff_header': {
                    'color': '#42afca',
                    'font-size': 'large',
                    'font-weight': 'bold',
                    'margin': 0
                },
                'boff_subheader': {
                    'font-size': 10,
                    'margin': (0, 0, 20, 0)
                },
                'trait_header': {
                    'color': '#42afca',
                    'font-size': 'large',
                    'font-weight': 'bold',
                    'margin': 0,  # padding: 0
                },
                'trait_subheader': {
                    'color': '#42afca',
                    'font-size': 10,
                    'margin': (0, 0, 20, 0),
                },
                'equipment_name': {
                    'font-size': 'large',
                    'font-weight': 'bold',
                    'margin': 0
                },
                'equipment_type_subheader': {
                    'font-size': 10,
                    'margin': (0, 0, 20, 0),
                },
                'equipment_head': {
                    'color': '#42afca',
                    'font-size': 12,
                    'margin': (10, 0, 0, 0)
                },
                'equipment_subhead': {
                    'color': '#f4f400',
                    'font-size': 10,
                    'margin': 0
                },
                'equipment_who': {
                    'color': '#ff6347',
                    'font-size': 10,
                    'margin': (0, 0, 10, 0)
                },
                'skill_ultimate_name': {
                    'color': '#ffd700;',
                    'font-size': 12,
                    'margin': (10, 0, 0, 0)
                },
            },
            # picker window
            'picker': {
                'background-color': '@bg',
                'border-color': '@sets',
                'border-width': 3,
                'border-style': 'solid',
                'border-radius': '@br'
            },
            # list widget displaying items in picker
            'picker_list': {
                'background-color': '@bg',
                'color': '@fg',
                'border-style': 'none',
                'margin': 0,
                'font': '@font',
                'outline': '0',  # removes dotted line around clicked item
                '::item': {
                    'border-width': '@bw',
                    'border-style': 'solid',
                    'border-color': '@bg',
                },
                '::item:selected': {
                    'background-color': '@bg',
                    'border-width': '@bw',
                    'border-style': 'solid',
                    'border-color': '@bg',
                },
                # selected but not the last click of the user
                '::item:selected:!active': {
                    'color': '@fg'
                },
                '::item:hover': {
                    'background-color': '@lbg',
                },
                '~QScrollBar': {
                    'border-style': 'none',
                    'border': 'none',
                    'border-radius': 0
                }
            },
            # large text editor
            'textedit': {
                'background-color': '@mbg',
                'border-style': 'solid',
                'border-width': '@bw',
                'border-color': '@bc',
                'font': '@font',
                'color': '@fg',
                'padding': 3,
                'selection-background-color': '@lsets'
            },
            # context menu
            'context_menu': {
                'background-color': '@bg',
                'border-color': '@lbg',
                'border-width': '@bw',
                'border-style': 'solid',
                'border-radius': '@br',
                'padding': '@sep',
                '::item': {
                    'color': '@fg',
                    'font': '@font',
                    'border-color': '@bg',
                    'border-radius': 0,
                    'border-style': 'solid',
                    'border-width': '@bw',
                    'padding': (3, 3, 1, 10),
                },
                '::icon': {
                    'padding': (1, 1, 1, 10),
                },
                '::item:selected': {
                    'border-color': '@sets',
                },
                '::item:disabled': {
                    'color': '@mfg'
                },
                '::item:disabled:selected': {
                    'border-color': '@bg'
                }
            },
            # frame for duty officers
            'doff_frame': {
                'background-color': '@bg',
                'border-style': 'solid',
                'border-width': '@bw',
                'border-color': '@bc',
                'padding': 2
            },
            # segment of the bonus bar
            'bonus_bar': {
                ':disabled': {
                    'border-style': 'solid',
                    'border-top-style': 'none',
                    'border-bottom-style': 'none',
                    'border-width': '@bw',
                    'border-color': '@bc',
                    'background-color': '@bg',
                },
                ':checked': {
                    'background-color': '@sets'
                }
            },
            # label holding career / ground icon
            'unlock_label': {
                'border-style': 'none',
                'border-top-style': 'solid',
                'border-top-width': 1,
                'border-top-color': '@bc',
                'margin': (0, 0, 3, 0),
                'padding': (3, 10, 0, 10)
            },
            # horizontal seperator
            'hr': {
                'background-color': '@lbg',
                'border-style': 'none',
                'height': 1
            },
            # horizontal sliding selector
            'slider': {
                'font': ('Roboto Mono', 11, 'Normal'),
                'color': '@fg',
                '::groove:horizontal': {
                    'border-style': 'none',
                    'background-color': '@lbg',
                    'border-radius': '@bw',
                    'height': 3
                },
                '::handle:horizontal': {
                    'border-style': 'solid',
                    'border-width': '@bw',
                    'border-color': '@bc',
                    'background-color': '@bc',
                    'width': 6,
                    'margin-top': -7,
                    'margin-bottom': -7
                },
                '::handle:horizontal:hover': {
                    'border-color': '@sets'
                },
                '::handle:horizontal:pressed': {
                    'background-color': '#666666'
                },
            },
            # small window
            'dialog_window': {
                'background-color': '@sets'
            },
        }
