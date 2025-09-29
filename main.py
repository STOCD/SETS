import os
import sys

from src import SETS


class Launcher():

    version = '2025.09b290'
    __version__ = '2.1'

    # holds the style of the app
    theme = {
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

    @staticmethod
    def base_path() -> str:
        """initialize the base path"""
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.abspath(os.path.dirname(__file__))
        return base_path

    @staticmethod
    def app_config() -> dict:
        config = {
            'settings_path': '.SETS_settings.ini',
            'config_folder_path': '.config',
            'config_subfolders': {
                'library': 'library',
                'cache': 'cache',
                'cargo': 'cargo',
                'images': 'images',
                'ship_images': 'ship_images',
                'backups': 'backups'
            },
            'autosave_filename': '.autosave.json',
            'box_width': 49,
            'box_height': 64,
            'link_website': 'https://stobuilds.com/apps/sets',
            'link_github': 'https://github.com/STOCD',
            'link_discord': 'https://discord.gg/kxwHxbsqzF',
            'link_downloads': 'https://github.com/STOCD/SETS/releases',
            'default_settings': {
                'ui_scale': 1.0,
                'default_mark': '',
                'default_rarity': 'Common',
                'picker_relative': 0,
                'default_save_format': 'JSON',
                'geometry': None
            }
        }
        return config

    @staticmethod
    def launch():
        args = {}
        exit_code = SETS(
                theme=Launcher.theme, args=args,
                path=Launcher.base_path(), config=Launcher.app_config(),
                versions=(Launcher.__version__, Launcher.version)).run()
        sys.exit(exit_code)


if __name__ == '__main__':
    Launcher.launch()
