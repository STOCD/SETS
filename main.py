# from textwrap import fill
from asyncio import subprocess
from tkinter import *
from tkinter import filedialog
from tkinter import font
import tkinter
from tkinter import messagebox
from tkinter.ttk import Progressbar
from requests_html import Element, HTMLSession, HTML
from PIL import Image, ImageTk, ImageGrab
import os, requests, json, re, datetime, html, urllib.parse, ctypes, sys, argparse, platform, uuid
import webbrowser
import numpy as np

if platform.system() == 'Darwin':
    from tkmacosx import Button
else:
    from tkinter import Button

CLEANR = re.compile('<.*?>')

"""This section will improve display, but may require sizing adjustments to activate"""
if sys.platform.startswith('win'):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # windows version >= 8.1
    except:
        ctypes.windll.user32.SetProcessDPIAware() # windows version <= 8.0

class HoverButton(Button):
    def __init__(self, master, **kw):
        Button.__init__(self,master=master,**kw)
        self.defaultBackground = self["background"]
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground

class SETS():
    """Main App Class"""
    version = '20220324a_beta'

    daysDelayBeforeReattempt = 7

    #base URI
    wikihttp = 'https://sto.fandom.com/wiki/'
    wikiImages = wikihttp+'Special:Filepath/'

    #query for ship cargo table on the wiki
    ship_query = wikihttp+"Special:CargoExport?tables=Ships&&fields=_pageName%3DPage%2Cname%3Dname%2Cimage%3Dimage%2Cfc%3Dfc%2Ctier%3Dtier%2Ctype__full%3Dtype%2Chull%3Dhull%2Chullmod%3Dhullmod%2Cshieldmod%3Dshieldmod%2Cturnrate%3Dturnrate%2Cimpulse%3Dimpulse%2Cinertia%3Dinertia%2Cpowerall%3Dpowerall%2Cpowerweapons%3Dpowerweapons%2Cpowershields%3Dpowershields%2Cpowerengines%3Dpowerengines%2Cpowerauxiliary%3Dpowerauxiliary%2Cpowerboost%3Dpowerboost%2Cboffs__full%3Dboffs%2Cfore%3Dfore%2Caft%3Daft%2Cequipcannons%3Dequipcannons%2Cdevices%3Ddevices%2Cconsolestac%3Dconsolestac%2Cconsoleseng%3Dconsoleseng%2Cconsolessci%3Dconsolessci%2Cuniconsole%3Duniconsole%2Ct5uconsole%3Dt5uconsole%2Cexperimental%3Dexperimental%2Csecdeflector%3Dsecdeflector%2Changars%3Dhangars%2Cabilities__full%3Dabilities%2Cdisplayprefix%3Ddisplayprefix%2Cdisplayclass%3Ddisplayclass%2Cdisplaytype%3Ddisplaytype%2Cfactionlede%3Dfactionlede&&order+by=`_pageName`%2C`name`%2C`image`%2C`fc`%2C`faction__full`&limit=2500&format=json"
    #query for ship equipment cargo table on the wiki
    item_query = wikihttp+'Special:CargoExport?tables=Infobox&&fields=_pageName%3DPage%2Cname%3Dname%2Crarity%3Drarity%2Ctype%3Dtype%2Cboundto%3Dboundto%2Cboundwhen%3Dboundwhen%2Cwho%3Dwho%2Chead1%3Dhead1%2Chead2%3Dhead2%2Chead3%3Dhead3%2Chead4%3Dhead4%2Chead5%3Dhead5%2Chead6%3Dhead6%2Chead7%3Dhead7%2Chead8%3Dhead8%2Chead9%3Dhead9%2Csubhead1%3Dsubhead1%2Csubhead2%3Dsubhead2%2Csubhead3%3Dsubhead3%2Csubhead4%3Dsubhead4%2Csubhead5%3Dsubhead5%2Csubhead6%3Dsubhead6%2Csubhead7%3Dsubhead7%2Csubhead8%3Dsubhead8%2Csubhead9%3Dsubhead9%2Ctext1%3Dtext1%2Ctext2%3Dtext2%2Ctext3%3Dtext3%2Ctext4%3Dtext4%2Ctext5%3Dtext5%2Ctext6%3Dtext6%2Ctext7%3Dtext7%2Ctext8%3Dtext8%2Ctext9%3Dtext9&&order+by=%60_pageName%60%2C%60name%60%2C%60rarity%60%2C%60type%60%2C%60boundto%60&limit=5000&format=json'
    #query for personal and reputation trait cargo table on the wiki
    trait_query = wikihttp+"Special:CargoExport?tables=Traits&&fields=_pageName%3DPage%2Cname%3Dname%2Cchartype%3Dchartype%2Cenvironment%3Denvironment%2Ctype%3Dtype%2Cisunique%3Disunique%2Cmaster%3Dmaster%2Cdescription%3Ddescription%2Crequired__full%3Drequired%2Cpossible__full%3Dpossible&&order+by=%60_pageName%60%2C%60name%60%2C%60chartype%60%2C%60environment%60%2C%60type%60&limit=2500&format=json"
    ship_trait_query = wikihttp+"Special:CargoExport?tables=Mastery&fields=Mastery._pageName,Mastery.trait,Mastery.traitdesc,Mastery.trait2,Mastery.traitdesc2,Mastery.trait3,Mastery.traitdesc3,Mastery.acctrait,Mastery.acctraitdesc&limit=1000&offset=0&format=json"
    #query for DOFF types and specializations
    doff_query = wikihttp+"Special:CargoExport?tables=Specializations&fields=Specializations.name,Specializations.shipdutytype,Specializations.department,Specializations.description,Specializations.powertype,Specializations.white,Specializations.green,Specializations.blue,Specializations.purple,Specializations.violet,Specializations.gold&order+by=Specializations.name&limit=1000&offset=0&format=json"
    #query for Specializations and Reps
    reputation_query = wikihttp+'Special:CargoExport?tables=Reputation&fields=Reputation.name,Reputation.environment,Reputation.boff,Reputation.color1,Reputation.color2,Reputation.description,Reputation.icon,Reputation.link,Reputation.released,Reputation.secondary&order+by=Reputation.boff&limit=1000&offset=0&format=json'
    #query for Boffskills
    trayskill_query = wikihttp+"Special:CargoExport?tables=TraySkill&fields=TraySkill._pageName,TraySkill.name,TraySkill.activation,TraySkill.affects,TraySkill.description,TraySkill.description_long,TraySkill.rank1rank,TraySkill.rank2rank,TraySkill.rank3rank,TraySkill.recharge_base,TraySkill.recharge_global,TraySkill.region,TraySkill.system,TraySkill.targets,TraySkill.type&order+by=TraySkill.name&limit=1000&offset=0&format=json"
    faction_query = wikihttp+"Special:CargoExport?tables=Faction&fields=Faction.playability,Faction.name,Faction._pageName,Faction.allegiance,Faction.faction,Faction.imagepeople,Faction.origin,Faction.quadrant,Faction.status,Faction.traits&limit=1000&offset=0&format=json"

    #to prevent Infobox from loading the same element twice in a row
    displayedInfoboxItem = str()

    #available specializations and their respective starship traits
    specializations = {"Constable": "Arrest",
                       "Command Officer": "Command Frequency",
                       "Commando": "Demolition Teams",
                       "Miracle Worker": "Going the Extra Mile",
                       "Temporal Operative": "Non-Linear Progression",
                       "Pilot": "Pedal to the Metal",
                       "Intelligence Officer": "Predictive Algorithms",
                       "Strategist": "Unconventional Tactics"}
    
    #available recruits and their respective starship traits
    recruits = {"Klingon Recruit": "Hunter's Instinct",
                "Delta Recruit": "Temporal Insight",
                "Temporal Agent": "Critical Systems"}

    # Needs fonts, padx, pady, possibly others
    theme = theme_default = {
        'name': 'SETS_default',
        'app': {
            'bg': '#c59129',  # self.theme['app']['bg']
            'fg': '#3a3a3a',  # self.theme['app']['fg']
            'hover': '#a3a3a3',  # self.theme['app']['hover']
            'font': {  # self.theme['app']['font_object']
                'family': 'Helvetica',
                'size': 10,
                'weight': '',
            },
        },
        'frame': {
            'bg': '#3a3a3a',  # self.theme['frame']['bg']
            'fg': '#b3b3b3',  # self.theme['frame']['fg']
        },
        'frame_medium': {
            'bg': '#b3b3b3',  # self.theme['frame_medium']['bg']
            'fg': '#3a3a3a',  # self.theme['frame_medium']['fg']
            'hover': '#555555',  # self.theme['frame_medium']['hover']
            'hlbg': 'grey',  # self.theme['frame_medium']['hlbg']  # highlightbackground
            'hlthick': 1,  # self.theme['frame_medium']['hlthick']  # highlightthickness
        },
        'frame_light': {
            'bg': '#b3b3b3',  # self.theme['frame_light']['bg']
            'fg': '#3a3a3a',  # self.theme['frame_light']['fg']
        },
        'button_heavy': {
            'bg': '#6b6b6b',  # self.theme['button_heavy']['bg']
            'fg': '#ffffff',  # self.theme['button_heavy']['fg']
            'hover': '#bbbbbb',  # self.theme['button_heavy']['hover']
            'font': {  # self.theme['button_heavy']['font_object']
                'size': 12,
                'weight': 'bold',
            },
        },
        'button_medium': {
            'bg': '#6b6b6b',  # self.theme['button_medium']['bg']
            'fg': '#dddddd',  # self.theme['button_medium']['fg']
            'hover': '#bbbbbb',  # self.theme['button_medium']['hover']
            'font': {  # self.theme['button_medium']['font_object']
            },
        },
        'button': {
            'bg': '#3a3a3a',  # self.theme['button']['bg']
            'fg': '#b3b3b3',  # self.theme['button']['fg']
            'hover': '#555555',    # self.theme['button']['hover']
        },
        'label': {
            'bg': '#b3b3b3',  # self.theme['label']['bg']
            'fg': '#3a3a3a',  # self.theme['label']['fg']
            'font': {  # self.theme['app']['font_object']
                'size': 12,
            },
        },
        'space': {
            'bg': '#000000',  # self.theme['label']['bg']
            'fg': '#3a3a3a',  # self.theme['label']['fg']
        },
        'title1': {
            'font': {  # self.theme['title1']['font_object']
                'size': 14,
                'weight': 'bold',
            },
        },
        'title2': {
            'font': {  # self.theme['title2']['font_object']
                'size': 12,
                'weight': 'bold',
            },
        },
        'text_highlight': {
            'font': {  # self.theme['text_highlight']['font_object']
                'size': 10,
                'weight': 'bold',
            },
        },
        'text_contrast': {
            'font': {  # self.theme['text_contrast']['font_object']
                'size': 10,
                'weight': 'italic',
            },
        },
        'text_small': {
            'font': {  # self.theme['text_small']['font_object']
                'size': 8,
            },
        },
        'text_tiny': {
            'font': {  # self.theme['text_small']['font_object']
                'size': 8,
                'weight': 'bold',
            },
        },
        'text_log': {
            'font': {  # self.theme['text_small']['font_object']
                'family': 'Courier',
                'size': 10,
            },
        },
        'entry': {  # Entry and Text widgets
            'bg': '#b3b3b3',  # self.theme['entry']['bg']
            'fg': '#3a3a3a',  # self.theme['entry']['fg']
        },
        'entry_dark': {
            'bg': '#3a3a3a',  # self.theme['entry_dark']['bg']
            'fg': '#ffffff',  # self.theme['entry_dark']['fg']
        },
        'tooltip': {
            'bg': '#090b0d',  # self.theme['tooltip']['bg']
            'fg': '#ffffff',  # self.theme['tooltip']['fg']
            'highlight': '#090b0d',  # self.theme['tooltip']['highlight']
            'relief': 'flat',  # self.theme['tooltip']['relief']
            # Tags
            'head1': {'fg': '#42afca'},  # self.theme['tooltip']['head1']['fg']
            'head': {'fg': '#42afca'},  # self.theme['tooltip']['head']['fg']
            'subhead': {'fg':  '#f4f400'},  # self.theme['tooltip']['subhead']['fg']
            'who': {'fg':  '#ff6347'},  # self.theme['tooltip']['who']['fg']
            'distance': {'fg':  '#000000'},  # self.theme['tooltip']['distance']['fg']
        },
        'tooltip_head': {
            'font': {  # self.theme['tooltip_head']['font_object']
                'size': 12,
                'weight': 'bold',
            },
        },
        'tooltip_subhead': {
            'font': {  # self.theme['tooltip_subhead']['font_object']
                'size': 10,
                'weight': 'bold',
            },
        },
        'tooltip_name': {
            'font': {  # self.theme['tooltip_name']['font_object']
                'size': 15,
                'weight': 'bold',
            },
        },
        'tooltip_body': {
            'font': {  # self.theme['tooltip_body']['font_object']
                'size': 10,
            },
        },
        'tooltip_distance': {
            'font': {  # self.theme['tooltip_distance']['font_object']
                'size': 4,
            },
        },
        'icon_off': {
            'bg': 'grey',  # self.theme['icon_off']['bg']
            'fg': '#ffffff',  # self.theme['icon_off']['fg']
            'hlbg': 'grey',  # self.theme['icon_off']['hlbg']  # highlightbackground
            'hlthick': 0,  # self.theme['icon_off']['hlthick']  # highlightthickness
            'relief': 'raised',  # self.theme['icon_off']['relief']
        },
        'icon_on': {
            'bg': 'yellow',  # self.theme['icon_on']['bg']
            'fg': '#ffffff',  # self.theme['icon_on']['fg']
            'relief': 'groove',  # self.theme['icon_on']['relief']
        },
    }

    def encodeBuildInImage(self, src, message, dest):
        img = Image.open(src, 'r')
        width, height = img.size
        array = np.array(list(img.getdata()))
        if img.mode == 'RGB':
            n = 3
        elif img.mode == 'RGBA':
            n = 4
        total_pixels = array.size//n
        message += "$t3g0"
        b_message = ''.join([format(ord(i), "08b") for i in message])
        req_pixels = len(b_message)
        if req_pixels <= total_pixels:
            index=0
            for p in range(total_pixels):
                for q in range(0, 3):
                    if index < req_pixels:
                        array[p][q] = int(bin(array[p][q])[2:9] + b_message[index], 2)
                        index += 1
            array=array.reshape(height, width, n)
            enc_img = Image.fromarray(array.astype('uint8'), img.mode)
            enc_img.save(dest)

    def decodeBuildFromImage(self, src):
        img = Image.open(src, 'r')
        array = np.array(list(img.getdata()))
        if img.mode == 'RGB':
            n = 3
        elif img.mode == 'RGBA':
            n = 4
        total_pixels = array.size//n
        hidden_bits = ""
        for p in range(total_pixels):
            if p % 5000 == 0:
                self.progressBarUpdate()
            for q in range(0, 3):
                hidden_bits += (bin(array[p][q])[2:][-1])
        hidden_bits = [hidden_bits[i:i+8] for i in range(0, len(hidden_bits), 8)]
        message = ""
        for i in range(len(hidden_bits)):
            if message[-5:] == "$t3g0":
                break
            else:
                message += chr(int(hidden_bits[i], 2))
        return message[:-5]

    def openURL(self, url):
        try:
            webbrowser.open(url, new=2, autoraise=True)
            """
            if platform.system() == "Windows":
                os.startfile(url)
            elif platform.system() == "Darwin":
                subprocess.Popen(['open', url])
            elif platform.system() == "Linux":
                subprocess.Popen(['xdg-open', url])
            else:
                messagebox.showinfo(message="You'll find more information on the STO - Fandom WIKI: "+url)
            """
        except:
            messagebox.showinfo(message="You'll find more information on the STO - Fandom WIKI: "+url)
    
    def openWikiPage(self, pagename):
        url = "https://sto.fandom.com/wiki/"+pagename.replace(" ", "_")
        self.openURL(url)

    def fetchOrRequestHtml(self, url, designation):
        """Request HTML document from web or fetch from local cache"""
        cache_base = self.getFolderLocation('cache')
        override_base = self.getFolderLocation('override')
        if not os.path.exists(cache_base):
            return

        filename = os.path.join(*filter(None, [cache_base, designation]))+".html"
        filenameOverride = os.path.join(*filter(None, [override_base, designation]))+".html"
        if os.path.exists(filenameOverride):
            filename = filenameOverride

        if os.path.exists(filename):
            modDate = os.path.getmtime(filename)
            interval = datetime.datetime.now() - datetime.datetime.fromtimestamp(modDate)
            if interval.days < self.daysDelayBeforeReattempt:
                with open(filename, 'r', encoding='utf-8') as html_file:
                    s = html_file.read()
                    return HTML(html=s, url = 'https://sto.fandom.com/')
        r = self.session.get(url)
        self.makeFilenamePath(os.path.dirname(filename))
        with open(filename, 'w', encoding="utf-8") as html_file:
            html_file.write(r.text)
            self.logWriteTransaction('Cache File (html)', 'stored', str(os.path.getsize(filename)), designation, 1)

        return r.html

    def fetchOrRequestJson(self, url, designation, local=False):
        """Request HTML document from web or fetch from local cache specifically for JSON formats"""
        cache_base = self.resource_path(self.settings['folder']['local']) if local else self.getFolderLocation('cache')
        override_base = self.getFolderLocation('override')
        if not os.path.exists(cache_base):
            return

        filenameOverride = os.path.join(*filter(None, [override_base, designation]))+".json"
        if os.path.exists(filenameOverride):
            filename = filenameOverride
        else:
            filename = os.path.join(*filter(None, [cache_base, designation])) + ".json"

        if os.path.exists(filename):
            modDate = os.path.getmtime(filename)
            interval = datetime.datetime.now() - datetime.datetime.fromtimestamp(modDate)
            if interval.days < 7 or local:
                with open(filename, 'r', encoding='utf-8') as json_file:
                    json_data = json.load(json_file)
                    self.logWriteTransaction('Cache File (json)', 'read', str(os.path.getsize(filename)), designation, 1)
                    return json_data
            if interval.days >= 7:
                self.clearCacheFolder(designation+".json")
        elif not local:
            r = requests.get(url)
            self.makeFilenamePath(os.path.dirname(filename))
            with open(filename, 'w') as json_file:
                json.dump(r.json(),json_file)
                self.logWriteTransaction('Cache File (json)', 'stored', str(os.path.getsize(filename)), designation, 1)
            return r.json()

    def filePathSanitize(self, txt, chr_set='printable'):
        """Converts txt to a valid filename.

        Args:
            txt: The str to convert.
            chr_set:
                'printable':    Any printable character except those disallowed on Windows/*nix.
                'extended':     'printable' + extended ASCII character codes 128-255
                'universal':    For almost *any* file system. '-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        """

        FILLER = '-'
        MAX_LEN = 255  # Maximum length of filename is 255 bytes in Windows and some *nix flavors.

        # Step 1: Remove excluded characters.
        BLACK_LIST = set(chr(127) + r'<>:"/\|?*')                           # 127 is unprintable, the rest are illegal in Windows.
        white_lists = {
            'universal': {'-.0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'},
            'printable': {chr(x) for x in range(32, 127)} - BLACK_LIST,     # 0-32, 127 are unprintable,
            'extended' : {chr(x) for x in range(32, 256)} - BLACK_LIST,
        }
        white_list = white_lists[chr_set]
        result = ''.join(x
                         if x in white_list else FILLER
                         for x in txt)

        # Step 2: Device names, '.', and '..' are invalid filenames in Windows.
        DEVICE_NAMES = 'CON,PRN,AUX,NUL,COM1,COM2,COM3,COM4,' \
                       'COM5,COM6,COM7,COM8,COM9,LPT1,LPT2,' \
                       'LPT3,LPT4,LPT5,LPT6,LPT7,LPT8,LPT9,' \
                       'CONIN$,CONOUT$,..,.'.split()  # This list is an O(n) operation.
        if result in DEVICE_NAMES:
            result = f'-{result}-'

        # Step 3: Truncate long files while preserving the file extension.
        if len(result) > MAX_LEN:
            if '.' in txt:
                result, _, ext = result.rpartition('.')
                ext = '.' + ext
            else:
                ext = ''
            result = result[:MAX_LEN - len(ext)] + ext

        # Step 4: Windows does not allow filenames to end with '.' or ' ' or begin with ' '.
        result = re.sub(r"[. ]$", FILLER, result)
        result = re.sub(r"^ ", FILLER, result)

        return result

    def titleCaseRegexpText(self, matchobj):
        return matchobj.group(0).title()

    def lowerCaseRegexpText(self, matchobj):
        return matchobj.group(0).lower()


    def iconNameCleanup(self, text):
        text = text.replace('Q%27s_Ornament%3A_', '')
        # Much of this can be removed if the wiki templates have their lowercase forces removed
        text = re.sub('_From_', '_from_', text)
        text = re.sub('_For_', '_for_', text)
        text = re.sub('_The_', '_the_', text)
        text = re.sub('_And_', '_and_', text)
        text = re.sub('/[Ss]if', '/SIF', text)
        text = re.sub('nos_', 'noS_', text)
        text = re.sub('rihan', 'Rihan', text)
        text = re.sub('_(\w{1,2})_', self.lowerCaseRegexpText, text)
        text = re.sub('-([a-z])', self.titleCaseRegexpText, text)
        return text

    def fetchImage(self, url, designation):
        today = datetime.date.today()
        if not self.args.allfetch and url in self.persistent['imagesFail'] and self.persistent['imagesFail'][url]:
            daysSinceFail = today - datetime.date.fromisoformat(self.persistent['imagesFail'][url])
            if daysSinceFail.days <= self.daysDelayBeforeReattempt:
                # Previously failed, do not attempt download again until next reattempt days have passed
                return None

        self.progressBarUpdate(text=designation)
        img_request = requests.get(url)
        self.logWriteTransaction('fetchImage', 'download', str(img_request.headers.get('Content-Length')), url, 1, [str(img_request.status_code), designation])

        if not img_request.ok:
            # No response on icon grab, mark for no downlaad attempt till restart
            self.persistent['imagesFail'][url] = today.isoformat()
            self.auto_save(quiet=True)
            return None

        self.persistent['imagesFail'][url] = ''
        self.auto_save()

        return img_request.content

    def filepath_sanitizer(self, path):
        (path_only, name) = os.path.split(path)
        name = self.filename_sanitizer(name)
        path_converted = os.path.join(path_only, name)

        return path_converted

    def filename_sanitizer(self, name):
        name_only, chosenExtension = os.path.splitext(name)

        name_only = name_only.replace('/', '_')  # Missed by the path sanitizer
        name_only = self.filePathSanitize(name_only)  # Probably should move to pathvalidate library
        name_only = name_only.replace('\\\\', '_')  # Missed by the path sanitizer
        name_only = name_only.replace('.', '')  # Missed by the path sanitizer

        name_converted = '{}{}'.format(name_only, chosenExtension)

        self.logWriteSimple('sanitize', 'name', 6, [name, '=>', name_converted])

        return name_converted

    def fetchOrRequestImage(self, url, designation, width = None, height = None, faction = None, forceAspect = False):
        """Request image from web or fetch from local cache"""
        cache_base = self.getFolderLocation('images')
        if not os.path.exists(cache_base):
            return

        self.logWriteTransaction('Image File', 'try', '----', url, 5, [designation, faction, forceAspect])
        image_data = None
        designation = self.filename_sanitizer(designation)

        factionCode = factionCodeDefault = '_(Federation)'
        if faction is not None and self.persistent['useFactionSpecificIcons']:
            if 'faction' in self.build['captain'] and self.build['captain']['faction'] != '':
                factionCode = '_('+self.build['captain']['faction']+')'

        extension = "jpeg" if url.endswith("jpeg") or url.endswith("jpg") else "png"
        fileextension = '.'+extension
        filename = filenameDefault = filenameNoFaction = os.path.join(*filter(None, [cache_base, designation]))+fileextension
        override_base = self.getFolderLocation('override')
        internal_base = self.resource_path(self.settings['folder']['images'])
        filenameOverride = os.path.join(*filter(None, [override_base, designation]))+fileextension
        filenameInternal = os.path.join(*filter(None, [internal_base, designation]))+fileextension
        filenameExisting = ''

        if faction is not None and faction != False and '_icon' in url and not '_icon_(' in url:
            url = re.sub('_icon', '_icon{}'.format(factionCode), url)
            if factionCode != factionCodeDefault:
                # Don't alter filename for default faction
                filename = re.sub(fileextension, '{}{}'.format(factionCode, fileextension), filename)
                filenameDefault = re.sub(fileextension, '{}{}'.format(factionCodeDefault, fileextension), filename)

        if filename in self.persistent['imagesFactionAliases']:
            filename = self.persistent['imagesFactionAliases'][filename]

        if os.path.exists(filenameOverride):
            filename = filenameOverride
        elif not os.path.exists(filename) and os.path.exists(filenameInternal):
            filename = filenameInternal

        if os.path.exists(filename):
            self.progressBarUpdate()
        elif not self.args.nofetch:
            image_data = self.fetchImage(url, designation)

            if image_data is None:
                url2 = self.iconNameCleanup(url)
                image_data = self.fetchImage(url2, designation) if url2 != url else image_data

            if image_data is None:
                if factionCode in url:
                    url3 = re.sub(factionCode, factionCodeDefault, url)
                    filenameExisting = filenameNoFaction
                else:
                    url3 = re.sub('_icon', '_icon{}'.format(factionCode), url)
                    filenameExisting = filenameDefault

                if not os.path.exists(filenameExisting):
                    image_data = self.fetchImage(url3, designation) if url3 != url and url3 != url2 else image_data

                    if image_data is None:
                        url4 = self.iconNameCleanup(url3)
                        image_data = self.fetchImage(url4, designation) if url4 != url3 and url4 != url and url4 != url2 else image_data

        if os.path.exists(filenameExisting):
            self.progressBarUpdate(int(self.updateOnHeavyStep / 2))
            self.persistent['imagesFactionAliases'][filename] = filenameExisting
            self.logWriteTransaction('Image File', 'alias', '----', filename, 3, [filenameExisting])
            self.auto_save(quiet=True)
            filename = filenameExisting

        if image_data is not None:
            self.progressBarUpdate(self.updateOnHeavyStep)
            with open(filename, 'wb') as handler:
                handler.write(image_data)
            self.logWriteTransaction('Image File', 'write', len(str(os.path.getsize(filename))) if os.path.exists(filename) else '----', filename, 1)
        elif not os.path.exists(filename):
            self.progressBarUpdate(int(self.updateOnHeavyStep / 4))
            return self.emptyImage

        image = Image.open(filename)
        if(width is not None):
            if forceAspect:
                image = image.resize((width, height), Image.ANTIALIAS)
            else:
                image.thumbnail((width, height), resample=Image.LANCZOS)
        self.logWriteTransaction('Image File', 'read', str(os.path.getsize(filename)), filename, 4, image.size)
        return ImageTk.PhotoImage(image)

    def deHTML(self, textBlock, leaveHTML=False):
        textBlock = html.unescape(html.unescape(textBlock)) # Twice because the wiki overlaps some

        if not leaveHTML: textBlock = re.sub(CLEANR, '', textBlock)

        return textBlock

    def deWikify(self, textBlock, leaveHTML=False):
        textBlock = self.deHTML(textBlock, leaveHTML) # required first-- the below are *secondary* filters due to wiki formatting
        textBlock = textBlock.replace('&lt;',"<")
        textBlock = textBlock.replace('&gt;',">")
        textBlock = textBlock.replace('&#34;', '"')
        textBlock = textBlock.replace('&#39;', '\'')
        textBlock = textBlock.replace('&#91;', '[')
        textBlock = textBlock.replace('&#93;', ']')
        textBlock = textBlock.replace('&quot;', '\"')
        # clean up wikitext
        textBlock = textBlock.replace('\x7f', '')
        # \u007f'&quot;`UNIQ--nowiki-00000000-QINU`&quot;'\u007f
        textBlock = re.sub('\'"`UNIQ--nowiki-0000000.-QINU`"\'', '*', textBlock)
        textBlock = re.sub('\'"`UNIQ--nowiki-0000001.-QINU`"\'', '*', textBlock)
        textBlock = re.sub('\'"`UNIQ--nowiki-0000002.-QINU`"\'', '*', textBlock)
        textBlock = re.sub('\'"`UNIQ--nowiki-0000003.-QINU`"\'', '*', textBlock)
        textBlock = re.sub('\'"`UNIQ--nowiki-0000004.-QINU`"\'', '*', textBlock)
        if "[[" and "|" in textBlock:
            while "[[" and "|" in textBlock:
                start = textBlock.find("[[")
                end = textBlock.find("|")
                textBlock = textBlock[:start] + textBlock[end+1:]
        textBlock = textBlock.replace('[[', '')
        textBlock = textBlock.replace(']]', '')
        textBlock = textBlock.replace("{{lc: ","").replace("{{lc:","")
        textBlock = textBlock.replace("{{ucfirst: ","").replace("{{ucfirst:","")
        textBlock = textBlock.replace("{{","").replace("}}","")
        textBlock = textBlock.replace("&amp;", "&")
        textBlock = textBlock.replace("&#42;","*")
        return textBlock

    def loadLocalImage(self, filename, width = None, height = None, forceAspect=False):
        """Request image from web or fetch from local cache"""
        cache_base = self.settings['folder']['local']
        cache_base = self.resource_path(cache_base)
        self.makeFilenamePath(cache_base)
        filename = os.path.join(*filter(None, [cache_base, filename]))
        if os.path.exists(filename):
            image = Image.open(filename)
            #self.logWrite('==={}x{} [{}]'.format(width, height, filename), 2)
            if(width is not None):
                if forceAspect: image = image.resize((width,height),Image.ANTIALIAS)
                else: image.thumbnail((width, height), resample=Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        return self.emptyImage

    def getShipFromName(self, shipJson, shipName):
        """Find cargo table entry for given ship name"""
        ship_list = []
        for e in range(len(shipJson)):
            if shipJson[e]["Page"] == shipName:
                ship_list = shipJson[e]
        return ship_list

    def getTierOptions(self, tier):
        """Get possible tier options from ship tier string"""
        return ['T5', 'T5-U', 'T5-X'] if int(tier) == 5 else ['T6', 'T6-X'] if int(tier) == 6 else ['T'+str(tier)]

    def setVarAndQuit(self, e, name, image, v, win):
        """Helper function to set variables from within UI callbacks"""
        v['item'] = name
        v['image'] = image
        win.destroy()

    def makeRedditTable(self, c0, c1, c2, c3:list = [], alignment:list = [":---", ":---", ":---"]):
        if c3 != []:
            result = '**{0}** | **{1}** | **{2}** | **{3}**\n'.format(c0[0],c1[0],c2[0],c3[0])
            result = result + "{0} | {1} | {2} | {3}\n".format(alignment[0], alignment[1], alignment[2], alignment[3])
            for i in range(1,len(c0)):
                c0[i] = c0[i] if c0[i] is not None else '&nbsp;'
                c1[i] = c1[i] if c1[i] is not None else '&nbsp;'
                c2[i] = c2[i] if c2[i] is not None else '&nbsp;'
                c3[i] = c3[i] if c3[i] is not None else '&nbsp;'
                result = result + "{0} | {1} | {2} | {3}\n".format(c0[i],c1[i],c2[i],c3[i])
            return result
        result = '**{0}** | **{1}** | **{2}**\n'.format(c0[0],c1[0],c2[0])
        result = result + "{1} | {1} | {2}\n".format(alignment[0], alignment[1], alignment[2])
        for i in range(1,len(c0)):
            c0[i] = c0[i] if c0[i] is not None else '&nbsp;'
            c1[i] = c1[i] if c1[i] is not None else '&nbsp;'
            c2[i] = c2[i] if c2[i] is not None else '&nbsp;'
            result = result + "{0} | {1} | {2}\n".format(c0[i],c1[i],c2[i])
        return result

    def makeRedditColumn(self, c0, length):
        return c0+['&nbsp;']*(length-len(c0))+['--------------']

    def preformatRedditEquipment(self, key,len):
        return ["{0} {1} {2}".format(item['item'], item['mark'], ''.join(item['modifiers'])) for item in self.build[key] if item is not None][:len]

    def getEmptyItem(self):
        return {"item": "", "image": self.emptyImage}

    def sanitizeEquipmentName(self, name):
        """Strip irreleant bits of equipment name for easier icon matching"""
        name = self.deWikify(name)
        name = re.sub(r"(∞.*)|(Mk X.*)|(\[.*].*)|(MK X.*)|(-S$)", '', name).strip()
        return name

    def precachePreload(self, limited=False):
        self.logWriteBreak('precachePreload START')
        self.perf('downloads');self.precacheDownloads();self.perf('downloads', 'stop')
        self.perf('cache-ships');self.precacheShips();self.perf('cache-ships', 'stop')
        self.perf('cache-templates');self.precacheTemplates();self.perf('cache-templates', 'stop')
        self.perf('cache-doffspace');self.precacheDoffs("Space");self.perf('cache-doffspace', 'stop')
        self.perf('cache-doffground');self.precacheDoffs("Ground");self.perf('cache-doffground', 'stop')
        self.perf('cache-mods');self.precacheModifiers();self.perf('cache-mods', 'stop')
        self.perf('cache-reps');self.precacheReputations();self.perf('cache-reps', 'stop')
        self.perf('cache-factions');self.precacheFactions();self.perf('cache-factions', 'stop')
        self.perf('cache-skills');self.precacheSkills();self.perf('cache-skills', 'stop')

        # Image list builders are slower

        self.perf('cache-boffabilities');self.precacheBoffAbilities(limited=limited);self.perf('cache-boffabilities', 'stop')
        self.perf('cache-traits');self.precacheTraits(limited=limited);self.perf('cache-traits', 'stop')
        self.perf('cache-shiptraits');self.precacheShipTraits(limited=limited);self.perf('cache-shiptraits', 'stop')
        self.perf('cache-equipment');self.precache_equipment_all(limited=limited);self.perf('cache-equipment', 'stop')
        # Add the known equipment series [optional?]
        self.logWriteBreak('precachePreload END')

    def precache_equipment_all(self, limited=False):
        equipment_types = [
            'Ship Fore Weapon', 'Ship Aft Weapon', 'Ship Device', 'Hangar Bay', 'Experimental',
            'Ship Deflector Dish', 'Ship Secondary Deflector', 'Impulse Engine', 'Warp', 'Singularity', 'Ship Shields',
            'Console', 'Ship Tactical Console', 'Ship Science Console', 'Ship Engineering Console',
            'Kit Module', 'Kit Frame', 'Body Armor', 'EV Suit', 'Personal Shield', 'Ground Weapon', 'Ground Device',
        ]
        if not limited:
            for type in equipment_types:
                self.precacheEquipment(type)
        return

    def precacheIconCleanup(self):
        #preliminary gathering for self-cleaning icon folder
        #equipment = self.searchJsonTable(self.infoboxes, "type", phrases)
        boffIcons = self.cache['boffTooltips']['space'].keys()
        boffIcons += self.cache['boffTooltips']['ground'].keys()


    def precacheEquipmentSingle(self, name, keyPhrase, item):
        name = self.sanitizeEquipmentName(name)
        if 'Hangar - Advanced' in name or 'Hangar - Elite' in name:
            return

        if not keyPhrase in self.cache['equipment']:
            self.cache['equipment'][keyPhrase] = {}
            self.cache['equipmentWithImages'][keyPhrase] = []

        if not name in self.cache['equipment'][keyPhrase]:
            self.cache['equipment'][keyPhrase][name] = item
            self.cache['equipmentWithImages'][keyPhrase].append((name, self.imageFromInfoboxName(name)))


    def precacheEquipment(self, keyPhrase):
        """Populate in-memory cache of ship equipment lists for faster loading"""
        if not keyPhrase or keyPhrase in self.cache['equipment']:
            return

        additionalPhrases = []
        if 'Weapon' in keyPhrase and 'Ship' in keyPhrase: additionalPhrases = ['Ship Weapon']
        elif 'Console' in keyPhrase: additionalPhrases = ['Universal Console']

        phrases = [keyPhrase] + additionalPhrases

        if "Kit Frame" in keyPhrase:
            equipment = [item for item in self.infoboxes if "Kit" in item['type'] and not "Template Demo Kit" in item['type'] and not 'Module' in item['type']]
        else:
            equipment = self.searchJsonTable(self.infoboxes, "type", phrases)

        for item in range(len(equipment)):
            self.precacheEquipmentSingle(equipment[item]['name'], keyPhrase, equipment[item])

        """ Prune below when precacheEquipmentSingle is stable
        self.cache['equipment'][keyPhrase] = {self.sanitizeEquipmentName(equipment[item]["name"]): equipment[item] for item in range(len(equipment))}

        if 'Hangar' in keyPhrase:
            self.cache['equipment'][keyPhrase] = {key:self.cache['equipment'][keyPhrase][key] for key in self.cache['equipment'][keyPhrase] if 'Hangar - Advanced' not in key and 'Hangar - Elite' not in key}
        """

        self.logWriteCounter('Equipment', '(json)', len(self.cache['equipment'][keyPhrase]) if keyPhrase in self.cache['equipment'] else 0, [keyPhrase])

    def searchHtmlTable(self, html, field, phrases):
        """Return HTML table elements containing 1 or more phrases"""
        trs = html.find('tr')
        fields = [tr.find(field, first=True) for tr in trs]
        results = [tr for tr,field in zip(trs,fields) if isinstance(field, Element) and any(phrase in field.text for phrase in phrases)]
        return [] if isinstance(results, int) else results

    def searchJsonTable(self, html, field, phrases):
        """Return Json table elements containing 1 or more phrases"""
        results = []
        for e in range(len(html)):
            if field in html[e]:
                for phrase in phrases:
                    if phrase in html[e][field]:
                        results.append(html[e])
        return [] if isinstance(results, int) else results

    def precacheModifiers(self):
        """Fetch equipment modifiers"""
        if 'modifiers' in self.cache and self.cache['modifiers'] is not None and len(self.cache['modifiers']) > 0:
            return

        modPage = self.fetchOrRequestHtml(self.wikihttp+"Modifier", "modifiers").find("div.mw-parser-output", first=True).html
        mods = re.findall(r"(<td.*?>(<b>)*\[.*?](</b>)*</td>)", modPage)
        self.cache['modifiers'] = list(set([re.sub(r"<.*?>",'',mod[0]) for mod in mods]))
        self.logWriteCounter('Modifiers', '(json)', len(self.cache['modifiers']))

    def precacheShips(self):
        self.shipNames = [e["Page"] for e in self.ships]
        self.logWriteCounter('Ships', '(json)', len(self.shipNames), ['space'])

    def predownloadGearImages(self):
        pass

    def predownloadShipImages(self):
        for e in self.ships:
            self.fetchOrRequestImage(self.wikiImages+e['image'].replace(' ','_'), e['Page'], self.imageBoxX, self.imageBoxY)

    def precacheSpaceSkills(self):
        if 'space' in self.cache['skills'] and len(self.cache['skills']['space']) > 0:
            return

        skills = self.fetchOrRequestJson('', 'space_skills', local=True)

        if "space" in skills:
            self.cache['skills']['space'] = skills["space"]
            self.logWriteCounter('space skills', '(json)', len(self.cache['skills']['space']))

    def precacheGroundSkills(self):
        if 'ground' in self.cache['skills'] and len(self.cache['skills']['ground']) > 0:
            return

        skills = self.fetchOrRequestJson('', 'ground_skills', local=True) 

        if "ground" in skills:
            self.cache['skills']['ground'] = skills['ground']
            self.logWriteCounter('ground skills', '(json)', len(self.cache['skills']['ground']))

    def precacheSkills(self, environment=None):
        if environment == 'space' or environment is None:
            self.precacheSpaceSkills()

        if environment == 'ground' or environment is None:
            self.precacheGroundSkills()

    def precacheDoffs(self, keyPhrase):
        """Populate in-memory cache of doff lists for faster loading"""
        if keyPhrase in self.cache['doffs']:
            return self.cache['doffs'][keyPhrase]

        phrases = [keyPhrase]
        doffMatches = self.searchJsonTable(self.doffs, "shipdutytype", phrases)

        self.cache['doffs'][keyPhrase] = {self.deWikify(doffMatches[item]['name'])+str(doffMatches[item]['powertype']): doffMatches[item] for item in range(len(doffMatches))}
        self.cache['doffNames'][keyPhrase] = {self.deWikify(doffMatches[item]['name']): '' for item in range(len(doffMatches))}
        self.logWriteCounter('DOFF', '(json)', len(self.cache['doffs'][keyPhrase]), [keyPhrase])
        self.logWriteCounter('DOFF names', '(json)', len(self.cache['doffNames'][keyPhrase]), [keyPhrase])

    def precacheFactions(self):
        if 'factions' in self.cache and len(self.cache['factions']) > 0: return

        self.speciesNames = { 'all': [] }
        for faction in self.factionNames:
            self.speciesNames[faction] = []

        for i in range(len(self.factions)):
            name = self.factions[i]['name'] if 'name' in self.factions[i] else ''
            playDetail = self.factions[i]['playability'].lower() if 'playability' in self.factions[i] else ''
            traits = self.factions[i]['traits'] if 'traits' in self.factions[i] else ''

            # Must handle multiple factions, liberated borg needs to create four entries
            # Discovery as separate Faction?
            if 'starfleet]]' in playDetail: self.speciesNames['Federation'] += name
            if 'dsc]]' in playDetail: self.speciesNames['DSC Federation'] += name
            if 'kdf]]' in playDetail: self.speciesNames['Klingon'] += name
            if 'tos]]' in playDetail: self.speciesNames['TOS Federation'] += name
            if playDetail.startswith('dominion '): self.speciesNames['Dominion'] += name

            if 'rom]]' in playDetail or 'Playable captains with Romulan Republic' in playDetail: self.speciesNames['Romulan'] += name

            if len(name) and len(playDetail) and not 'officer only' in playDetail and not 'officers only' in playDetail and not 'officer]] only' in playDetail and not 'none' in playDetail:
                self.cache['factions'][name] = traits
                self.speciesNames['all'] += [name]

        self.speciesNames['all'] = sorted(self.speciesNames['all'])
        for faction in self.factionNames: self.speciesNames[faction] = sorted(self.speciesNames[faction])
        self.logWriteCounter('Factions', '(json)', len(self.cache['factions']))

    def precacheReputations(self):
        if 'specsPrimary' in self.cache and len(self.cache['specsPrimary']) > 0:
            return

        for item in list(self.reputations):
            name = self.deWikify(item['name']) if 'name' in item and item['name'] else ''
            name = re.sub(' Operative', '', name)
            name = re.sub(' Officer', '', name)
            # keep Miracle Worker currently
            environment = item['environment'] if 'environment' in item else ''
            description = self.deWikify(item['description'], leaveHTML=True) if 'description' in item else ''
            if not name:
                # other reps
                pass
            elif len(environment) and not name in self.cache['specsSecondary'] and not name in self.cache['specsGroundBoff']:
                if environment == 'space' or environment == 'both':
                    self.cache['specsSecondary'][name] = description
                    if not 'secondary' in item or item['secondary'] != 'yes':
                        self.cache['specsPrimary'][name] = description
                if 'boff' in item and item['boff'] == 'yes' and (environment == "ground" or environment == "both"):
                    self.cache['specsGroundBoff'][self.deWikify(name)] = self.deWikify(description, leaveHTML=True)

        self.logWriteCounter('Specs', '(json)', len(self.cache['specsPrimary']))
        self.logWriteCounter('Specs2', '(json)', len(self.cache['specsSecondary']))
        self.logWriteCounter('Specs-Ground', '(json)', len(self.cache['specsGroundBoff']))

    def precacheShipTraitSingle(self, name, desc, item):
        name = self.deWikify(name)
        if not 'cache' in self.cache['shipTraitsWithImages']:
            self.cache['shipTraitsWithImages']['cache'] = []

        if not name in self.cache['shipTraits']:
            self.cache['shipTraits'][name] = self.deWikify(desc, leaveHTML=True)
            self.cache['shipTraitsWithImages']['cache'].append((name,self.imageFromInfoboxName(name)))
            self.logWriteSimple('precacheShipTrait', '', 5, tags=[name])
        
        if not name in self.cache['shipTraitsFull']:
            if "_pageName" in item:
                obt = "T5" if item['traitdesc'] == desc or item['traitdesc2'] == desc or item['traitdesc3'] == desc else "T6"
                self.cache['shipTraitsFull'][name] = {"ship":item["_pageName"], "desc": self.deWikify(desc, leaveHTML=True), "image": self.imageFromInfoboxName(name), "link": "https://sto.fandom.com/wiki/"+item["_pageName"].replace(" ", "_"), "obtained": obt }
            elif "Page" in item and "name" in item:
                if item["name"] in ["Arrest", "Command Frequency", "Demolition Teams", "Going the Extra Mile", "Non-Linear Progression", "Pedal to the Metal", "Predictive Algorithms", "Unconventional Tactics"]:
                    obt = "spec"
                    for spec in self.specializations:
                        if self.specializations[spec] == item["name"]:
                            nm = spec
                            break
                elif item["name"] in ["Critical Systems", "Hunter's Instinct", "Temporal Insight"]:
                    obt = "recr"
                    for recr in self.recruits:
                        if self.recruits[recr] == item["name"]:
                            nm = recr
                            break
                else:
                    obt = "box"
                    nm = ""
                self.cache['shipTraitsFull'][name] = {"ship":nm, "desc": self.deWikify(desc, leaveHTML=True), "image": self.imageFromInfoboxName(name), "link": "https://sto.fandom.com/wiki/"+item["Page"].replace(" ", "_"), "obtained": obt }


    def precacheShipTraits(self, limited=False):
        """Populate in-memory cache of ship traits for faster loading"""
        if 'shipTraits' in self.cache and len(self.cache['shipTraits']) > 0:
            return self.cache['shipTraits']

        for item in list(self.shiptraits):
            if 'trait' in item and len(item['trait']):
                self.precacheShipTraitSingle(item['trait'], item['traitdesc'], item)
            if 'trait2' in item and len(item['trait2']):
                self.precacheShipTraitSingle(item['trait2'], item['traitdesc2'], item)
            if 'trait3' in item and len(item['trait3']):
                self.precacheShipTraitSingle(item['trait3'], item['traitdesc3'], item)
            if 'acctrait' in item and len(item['acctrait']):
                self.precacheShipTraitSingle(item['acctrait'], item['acctraitdesc'], item)

        for item in list(self.traits):
            if 'type' in item and item['type'].lower() == 'starship':
                self.precacheShipTraitSingle(item['name'], item['description'], item)

        self.logWriteCounter('Ship Trait', '(json)', len(self.cache['shipTraits']), ['space'])

    def precacheTraitSingle(self, name, desc, environment, type):
        name = self.deWikify(name)
        if type == 'recruit':
            return
        if type != 'reputation' and type != 'activereputation' and type != 'Starship':
            type = "personal"

        if not environment in self.cache['traits']:
            self.cache['traits'][environment] = dict()

        if not type in self.cache['traitsWithImages']:
            self.cache['traitsWithImages'][type] = dict()
        if not environment in self.cache['traitsWithImages'][type]:
            self.cache['traitsWithImages'][type][environment] = []

        if not name in self.cache['traits'][environment]:
            self.cache['traits'][environment][name] = self.deWikify(desc, leaveHTML=True)

            self.cache['traitsWithImages'][type][environment].append((name,self.imageFromInfoboxName(name)))
            self.logWriteSimple('precacheTrait', '', 4, tags=[type, environment, name, '|'+str(len(desc))+'|'])

    def precacheTraits(self, limited=False):
        """Populate in-memory cache of traits for faster loading"""
        if 'traits' in self.cache and 'space' in self.cache['traits']:
            return self.cache['traits']

        for item in list(self.traits):
            if not 'chartype' in item or item['chartype'] != 'char':
                continue
            if 'type' in item and 'name' in item and 'description' in item and 'environment' in item:
                self.precacheTraitSingle(item['name'], item['description'], item['environment'], item['type'])

        for type in self.cache['traitsWithImages']:
            for environment in self.cache['traitsWithImages'][type]:
                self.logWriteCounter('Trait', '(json)', len(self.cache['traitsWithImages'][type][environment]), [environment, type])

    def setListIndex(self, list, index, value):
        list[index] = value

    def uri_sanitize_stowiki(self, name):
        name = name.replace(' ', '_')
        name = name.replace('/', '_')
        name = html.unescape(name)
        name = urllib.parse.quote(name)
        return name

    def imageFromInfoboxName(self, name, width=None, height=None, suffix='_icon', faction=None, forceAspect = False):
        """Translate infobox name into wiki icon link"""
        width = self.itemBoxX if width is None else width
        height = self.itemBoxY if height is None else height

        try:
            image = self.fetchOrRequestImage(self.wikiImages+self.uri_sanitize_stowiki(name)+suffix+".png", name, width, height, faction, forceAspect=forceAspect)
            if image is None:
                self.logWriteSimple('fromInfoboxName', 'NONE', 4)
            elif image == self.emptyImage:
                self.logWriteSimple('fromInfoboxName', 'EMPTY', 4)
            else:
                self.logWriteSimple('fromInfoboxName', name, 4, [image.width(), image.height()])
            return image
        except:
            self.logWriteSimple('fromInfoboxName', 'FAIL', 4)
            return self.fetchOrRequestImage(self.wikiImages+"Common_icon.png", "no_icon",width,height)

    def resetAfterImport(self):
        self.skillCount('space')
        self.skillCount('ground')

        self.logWriteSimple('Skill count', 'import', 3, [self.backend['skillCount']['space']['sum'], self.backend['skillCount']['ground']["sum"]])

    def getSkillnodeByName(self, name: str, pkey=""):
            skillnode = None
            skillindex = -1
            skillrank = ""
            if pkey == "": keylist = ["lieutenant", "lieutenant commander", "commander", "captain", "admiral"]
            else: keylist = [pkey]
            for key in keylist:
                for j in range(0,6):
                    skillname = self.cache['skills']['space'][key][j]['skill']
                    if isinstance(skillname, str) and skillname == name[:-2]:
                        skillnode = self.cache['skills']['space'][key][j]
                        skillrank = key
                        break
                    elif isinstance(skillname, list) and (name in skillname or name[:-2] in skillname):
                        skillnode = self.cache['skills']['space'][key][j]
                        skillrank = key
                        for k in range(0, len(skillnode['skill'])):
                            if skillnode['skill'][k]==name or skillnode['skill'][k]==name[:-2]:
                                skillindex=k
                                break
                if skillnode != None:
                    break
            return [skillnode, skillindex, skillrank]

    def skillCount(self, environment):
        self.backend['skillCount'][environment] = dict()
        self.backend['skillCount'][environment]['sum'] = 0
        lskills = self.build['skilltree'][environment]
        for rank in ['lieutenant', 'lieutenant commander', 'commander', 'captain', 'admiral']:
            self.backend['skillCount'][environment][rank] = 0
            for name in lskills:
                snode, sindex, srank = self.getSkillnodeByName(name, rank)
                if self.build['skilltree'][environment][name] and snode != None: 
                    self.backend['skillCount'][environment]["sum"] += 1
                    if environment == "space":
                        self.backend['skillCount'][environment][rank] +=1

    def copyBackendToBuild(self, key, key2=None):
        """Helper function to copy backend value to build dict"""
        if key in self.backend and key2 is None:
            self.build[key] = self.backend[key].get()
        elif key2 in self.backend[key]:
            self.build[key][key2] = self.backend[key][key2].get()
        self.auto_save_queue()

    def copyBuildToBackendBoolean(self, key, key2=None):
        """Helper function to copy build value to backend dict"""
        if key in self.build and key2 is None:
            self.backend[key].set(1 if self.build[key] else 0)
        elif key2 in self.build[key]:
            self.backend[key][key2].set(1 if self.build[key][key2] else 0)

    def copyBuildToBackend(self, key, key2=None):
        """Helper function to copy build value to backend dict"""
        if key in self.build and key2 is None:
            self.backend[key].set(self.build[key])
        elif key2 in self.build[key]:
            self.backend[key][key2].set(self.build[key][key2])

    def precacheTemplates(self):
        self.shipTemplate = {
            'name': 'Template',
            'image': 'none',
            'tier': 6,
            'fore': 5,
            'aft': 4,
            'equipcannons': 1,
            'devices': 4,
            'consolestac': 5,
            'consolessci': 5,
            'consoleseng': 5,
            'experimental': 1,
            'secdeflector': 1,
            'hangars': 2,
            'abilities': [ 'Innovation Effects' ],
            'boffs': [ 'Commander Universal-Miracle Worker', 'Lieutenant Commander Universal-Command', 'Lieutenant Commander Universal-Temporal Operative', 'Lieutenant Universal-Intelligence', 'Ensign Universal-Pilot' ]
        }

    def resetPersistent(self):
        # related constants not sourced externally yet
        self.fileStateName = '.state_SETS.json'
        self.fileConfigName = '.config.json'

        self.yesNo = ["Yes", "No"]
        self.universalTypes = ['Tactical', 'Engineering', 'Science' ]
        self.marks = ['', 'Mk I', 'Mk II', 'Mk III', 'Mk IIII', 'Mk V', 'Mk VI', 'Mk VII', 'Mk VIII', 'Mk IX', 'Mk X', 'Mk XI', 'Mk XII', '∞', 'Mk XIII', 'Mk XIV', 'Mk XV']
        self.rarities = ['Common', 'Uncommon', 'Rare', 'Very rare', 'Ultra rare', 'Epic']
        self.factionNames = [ 'Federation', 'Dominion', 'DSC Federation', 'Klingon', 'Romulan', 'TOS Federation' ]
        self.exportOptions = [ 'PNG', 'Json' ]
        self.boffSortOptions = [ 'release', 'ranks', 'spec', 'spec2' ]
        self.consoleSortOptions = [ 'tesu', 'uets', 'utse', 'uest' ]
        self.options_tags = ["Concept", "First Tests", "Optimization Phase", "Finished Build"]

        # self.persistent will be auto-saved and auto-loaded for persistent state data
        self.persistent = {
            'forceJsonLoad': 0,
            'fast_start': 0,
            'uiScale': 1,
            'geometry': '',
            'tooltipDelay': 2,
            'imagesFactionAliases': dict(),
            'imagesFail': dict(),
            'markDefault': '',
            'rarityDefault': self.rarities[0],
            'factionDefault': self.factionNames[0],
            'exportDefault': self.exportOptions[0],
            'boffSort': self.boffSortOptions[0],
            'boffSort2': self.boffSortOptions[0],
            'consoleSort': self.consoleSortOptions[0],
            'keepTemplateOnShipClear': 1,
            'keepTemplateOnShipChange': 0,
            'pickerSpawnUnderMouse': 1,
            'useFactionSpecificIcons': 0,
            'useAlternateTooltip': 0,
            'autosave': 1,
            'autosave_delay': 750,  # ms
            'versioning': 0,
            'perf': dict(),
            'tags': {
                'maindamage':{
                    'energy':0, 'kinetic':0, 'exotic':0, 'drain':0
                }, 
                'energytype':{
                    'phaser':0, 'disruptor':0, 'plasma':0, 'polaron':0, 'Tetryon':0, 'antiproton':0
                },
                'weapontype':{
                    'cannon':0, 'beam':0, 'mine':0, 'torpedo':0, 'sia':0, 'dsd':0, 'console-spam':0
                },
                'state':0,
                'role':{
                    'dps':0, 'heavytank':0, 'debufftank':0, 'nanny':0, 'off-meta':0, 'theme':0
                }
            }
        }

    def get_debug_default(self):
        self.fileDebug = '.debug'
        self.fileDebug = self.fileDebug
        self.debugDefault = 0
        if os.path.exists(self.fileDebug):
            self.debugDefault = 1
            with open(self.fileDebug) as f:
                entry = f.readline()
                try:
                    entry = int(entry)
                except Exception:
                    entry = 0
                if entry > 0:
                    self.debugDefault = entry
                    self.log_write_stderr('debug set from file: {}'.format(self.debugDefault))
                else:
                    self.log_write_stderr('debug file found: {} [{}]'.format(self.debugDefault, entry))

    def get_debug_current(self):
        if self.args.debug is not None:
            self.settings['debug'] = self.args.debug
            self.logWriteSimple('Debug', 'set by arg', 1, tags=[str(self.settings['debug'])])
        elif not 'debug' in self.settings or self.debugDefault > self.settings['debug']:
            self.settings['debug'] = self.debugDefault
            self.logWriteSimple('Debug', 'set from default', 1, tags=[str(self.settings['debug'])])
        else:
            self.logWriteSimple('Debug', 'set in config', 1, tags=[str(self.settings['debug'])])

    def resetInternals(self):
        self.get_debug_default()

        # log and logmini are the bottom text, logFull provides a history
        self.log = StringVar()
        self.logmini = StringVar()
        self.logFull = StringVar()

        self.autosaving = False

        self.perf_store = dict()
        self.windowUpdate = dict()
        self.reset_tooltip_tracking()
        self.images = dict()

    def reset_tooltip_tracking(self):
        self.tooltip_tracking = dict()

    def resetSettings(self):
        # self.settings are optionally loaded from config, but manually edited or saved
        self.settings = {
            'debug': self.debugDefault,
            'template': '.template',
            'autosave': '.autosave.json',
            'cache': '.cache_SETS.json',
            'skills':   'skills.json',
            'perf_to_retain': 50,
            'folder': {
                'config' : '.config',
                'cache' : 'cache',
                'images' : 'images',
                'custom' : 'images_custom',
                'override' : 'override',
                'local' : 'local',
                'library' : 'library',
                'backups' : 'backups',
            }
        }

    def resetBuild(self, type=None):
        """Initialize new build state"""
        # VersionJSON Should be updated when JSON format changes, currently number-as-date-with-hour in UTC
        self.versionJSONminimum = 0
        self.versionJSON = 2022022811
        self.clearing = False
        self.shipImageResizeCount = 0
        self.build = {
            'versionJSON': self.versionJSON,
            'boffs': dict(),
            'boffseats': dict(),
            'activeRepTrait': [None] * 5,
            'spaceRepTrait': [None] * 5,
            'personalSpaceTrait': [None] * 6,
            'personalSpaceTrait2': [None] * 6,
            'starshipTrait': [None] * 6,
            'uniConsoles': [None] * 5,
            'tacConsoles': [None] * 5,
            'sciConsoles': [None] * 5,
            'engConsoles': [None] * 5,
            'devices': [None] * 5,
            'aftWeapons': [None] * 5,
            'foreWeapons': [None] * 5,
            'hangars': [None] * 2,
            'deflector': [None],
            'engines': [None],
            'warpCore': [None],
            'shield': [None],
            'captain': {'faction' : '' },
            'career': '',
            'species': '',
            'ship': '',
            'specPrimary': '',
            'playerHandle': '',
            'playerShipName': '',
            'playerShipDesc': '',
            'playerDesc': '',
            'specSecondary': '',
            'tier': '',
            'secdef': [None],
            'experimental': [None],
            'personalGroundTrait': [None] * 6,
            'personalGroundTrait2': [None] * 6,
            'groundActiveRepTrait': [None] * 5,
            'groundRepTrait': [None] * 5,
            'groundKitModules': [None] * 6,
            'groundKit': [None],
            'groundArmor': [None],
            'groundEV': [None],
            'groundShield': [None],
            'groundWeapons': [None] * 2,
            'groundDevices': [None] * 5,
            'eliteCaptain': False,
            'doffs': {'space': [None] * 6 , 'ground': [None] * 6},
            'tags': dict(),
        }

        self.reset_skill_build(init=True)


    def reset_skill_build(self, init=False):
        build_skill = {
            'skilltree': {'space': dict(), 'ground': dict()},
        }
        if not init:
            self.clearing = 1
        self.build.update(build_skill)
        if not init:
            self.skillCount('space')
            self.skillCount('ground')
            self.clearing = 0
            self.setupCurrentBuildFrames('skill')
            self.auto_save_queue()

    def resetCache(self, text = None):
        if text is not None:
            if text in self.cache and text != 'modifiers':
                self.cache[text] = dict()
                if text+"WithImages" in self.cache:
                    self.cache[text+"WithImages"] = dict()
        else:
            self.cache = {
                'equipment': dict(),
                'equipmentWithImages': dict(),
                'doffs': dict(),
                'doffNames': dict(),
                'shipTraits': dict(),
                'shipTraitsWithImages': dict(),
                'shipTraitsFull': dict(),
                'traits': dict(),
                'traitsWithImages': dict(),
                'boffAbilities': dict(),
                'boffAbilitiesWithImages': dict(),
                'boffTooltips': dict(),
                'specsPrimary': dict(),
                'specsSecondary': dict(),
                'specsGroundBoff': dict(),
                'skills': {'space': dict(), 'ground': dict()},
                'factions': dict(),
                'modifiers': None,
            }

    def resetBackend(self, rebuild=False):
        self.logWriteBreak('clearBackend')
        self.backend = {
                'images': dict(),
                'captain': {'faction' : StringVar(self.window)},
                'career': StringVar(self.window),
                'species': StringVar(self.window),
                'playerHandle': StringVar(self.window),
                'playerName': StringVar(self.window),
                'specPrimary': StringVar(self.window),
                'specSecondary': StringVar(self.window),
                'ship': StringVar(self.window),
                'tier': StringVar(self.window),
                'playerShipName': StringVar(self.window),
                'playerShipDesc': StringVar(self.window),
                'playerDesc': StringVar(self.window),
                'shipHtml': None,
                'shipHtmlFull': None,
                'eliteCaptain': IntVar(self.window),
                'skillLabels': dict(),
                'skillNames': [[], [], [], [], []],
                'skillCount': { 'space': 0, 'ground': 0 },
                'tags': dict()
            }
        if rebuild: self.buildToBackendSeries()
        self.hookBackend()

    def hookBackend(self):
        self.backend['playerHandle'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('playerHandle'))
        self.backend['playerShipName'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('playerShipName'))
        self.backend['playerName'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('playerName'))
        self.backend['captain']['faction'].trace_add('write', lambda v,i,m:self.captainFactionCallback())
        self.backend['career'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('career'))
        self.backend['species'].trace_add('write', lambda v,i,m:self.speciesUpdateCallback())
        self.backend['specPrimary'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('specPrimary'))
        self.backend['specSecondary'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('specSecondary'))
        self.backend['tier'].trace_add('write', lambda v,i,m:self.setupCurrentBuildFrames('space'))
        self.backend['eliteCaptain'].trace_add('write', lambda v,i,m:self.clean_backend_elitecaptain())
        self.backend['ship'].trace_add('write', self.shipMenuCallback)


    def clean_backend_elitecaptain(self):
        pass


    def captainFactionCallback(self):
        self.copyBackendToBuild('captain', 'faction')
        if self.persistent['useFactionSpecificIcons']:
            if not self.clearing:
                self.resetCache('boffAbilities')
                self.precacheBoffAbilities()
            self.setupCurrentBuildFrames()


    def boffTitleToSpec(self, title):
        return  "Tactical" if "Tactical" in title else "Science" if 'Science' in title else "Engineering" if "Engineering" in title else "Universal"

    def clearFrame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def applyContentFilter(self, frame, content, filter):
        frame.event_generate('<<ResetScroll>>')
        for key in content.keys():
            if re.search(filter, key, re.IGNORECASE):
                content[key][0].grid(row=content[key][1], column=content[key][2], sticky='nsew')
            else:
                content[key][0].grid_forget()

    def pickerDimensions(self):
        #self.window.update()
        windowheight = self.windowHeight
        windowwidth = int(self.windowWidth / 6)
        if windowheight < 400: windowheight = 400
        if windowwidth < 240: windowwidth = 240

        return (windowwidth,windowheight)

    def pickerLocation(self, width=0, height=0, x=None, y=None, anchor="nw"):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        if x is not None and y is not None:
            pass  # Leave manual locations
        else :
            if self.persistent['pickerSpawnUnderMouse']:
                x = self.window.winfo_pointerx()
                y = self.window.winfo_pointery()
                self.logWrite("Window position update: x{},y{}".format(str(x), str(y)), 2)
            else:
                if anchor == 'ne' or anchor == 'nw':
                    y = self.window_topleft_y
                if anchor == 'se' or anchor == 'sw':
                    y = self.window_topleft_y + self.windowHeight - height
                if anchor == 'nw' or anchor == 'sw':
                    x = self.window_topleft_x
                if anchor == 'ne' or anchor == 'se':
                    x = self.window_topleft_x + self.windowWidth - width


        if height is not None and height < screen_height and (y + height) > screen_height:
            y = screen_height - height
        positionWindow = "+"+str(x)+"+"+str(y)

        return positionWindow

    def updateScrollFrame(self, event, canvas, scroll_frame_window, pickWindow):
        canvas.itemconfig(scroll_frame_window, width=event.width)

    def windowAddScrollbar(self, parentFrame, pickWindow):
        canvas = Canvas(parentFrame)
        canvas.grid(row=0, column=0, sticky='nsew')
        parentFrame.grid_columnconfigure(0, weight=1)
        parentFrame.grid_rowconfigure(0, weight=1)
        scrollbar = Scrollbar(parentFrame, orient=VERTICAL, command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky='nsew')

        scrollable_frame = Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        scroll_frame_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        #canvas.bind('<Configure>', lambda e: self.updateScrollFrame(e, canvas, scroll_frame_window, pickWindow))
        startY = canvas.yview()[0]
        parentFrame.bind("<<ResetScroll>>", lambda event: canvas.yview_moveto(startY))

        return (canvas, scrollable_frame)

    def restrictItemsList(self, items_list, tagsForRequirement = None):
        # Infobox 'who' denotes restrictions [for future imlementation]

        return items_list

    def pickerGui(self, title, itemVar, items_list, top_bar_functions=None, x=None, y=None):
        """Open a picker window"""
        pickWindow = Toplevel(self.window)
        pickWindow.resizable(True,True) #vertical resize only
        pickWindow.transient(self.window)
        pickWindow.title(title)

        (windowwidth,windowheight) = self.pickerDimensions()
        sizeWindow = '{}x{}'.format(windowwidth, windowheight)
        pickWindow.geometry(sizeWindow+self.pickerLocation(windowheight))
        #pickWindow.minsize(windowwidth, windowheight)

        origVar = dict()
        for key in itemVar:
            origVar[key] = itemVar[key]
        pickWindow.protocol('WM_DELETE_WINDOW', lambda:self.pickerCloseCallback(pickWindow,origVar,itemVar))

        container = Frame(pickWindow)
        content = dict()
        if top_bar_functions is not None:
            for func in top_bar_functions:
                func(container, itemVar, content)
        self.setupClearSlotFrame(container, itemVar, pickWindow)
        container.pack(fill=X, expand=False)

        container2 = Frame(pickWindow)
        container2.pack(fill=BOTH, expand=True)
        (canvas, scrollable_frame) = self.windowAddScrollbar(container2, pickWindow)

        try:
            items_list.sort()
        except:
            self.logWriteSimple('pickerGUI', 'TRY_EXCEPT', 1, tags=['item_list.sort() failed in '+title])

        i = 0
        for name,image in items_list:
            frame = Frame(scrollable_frame, relief='ridge', borderwidth=1)
            for col in range(3):
                if col < 2:
                    if col == 0:
                        subFrame = Label(frame, image=image)
                    else:
                        subFrame = Label(frame, text=name, justify=LEFT, wraplength=255)
                    subFrame.grid(row=0, column=col, sticky='nsew')
                else:
                    frame.grid(row=i, column=0, sticky='nsew', padx=(2,5))

                subFrame.bind('<Button-1>', lambda e,name=name,image=image,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,image,v,win))
                subFrame.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

            content[name] = (frame, i, 0)
            i += 1

        pickWindow.title('{} ({} options)'.format(title, i-1))
        pickWindow.wait_visibility()    #Implemented for Linux
        pickWindow.grab_set()
        pickWindow.wait_window()
        return itemVar

    def pickerCloseCallback(self, window, origVar, currentVar):
        for key in origVar:
            currentVar[key] = origVar[key]

        self.windowCloseCallback(window)

    def windowCloseCallback(self, window):
        try:
            window.destroy()
        except:
            pass

    def logWindowCreate(self):
        self.makeSubWindow(title='Log Viewer', type='log')

    def windowDimensions(self):
        #self.window.update()
        windowheight = self.windowActiveHeight - self.logoHeight - 45
        windowwidth = self.windowWidth

        return (windowwidth,windowheight)

    def subWindowLocationCentered(self, x, y, type=None):
        self_bar_height = self.windowBarHeight if type != 'splash' else 0
        if self.factor != 1:
            splash_adjust_x = 8 if type == 'splash' else 0
            splash_adjust_y = 3 if type == 'splash' else 0
        else:
            splash_adjust_x = 6 if type == 'splash' else 0
            splash_adjust_y = -5 if type == 'splash' else 0

        if x is None:
            x = self.window_topleft_x + splash_adjust_x
        if y is None:
            y = self.window_topleft_y + self.windowBarHeight + self.logoHeight + splash_adjust_y

        sizeWindow = '{}x{}'.format(self.windowWidth+3, self.windowHeight - 20 - (self_bar_height + self.logoHeight))
        positionWindow = '+{}+{}'.format(x, y)

        self.logWrite("subWindow position: {}".format(sizeWindow+positionWindow), 2)
        return sizeWindow+positionWindow

    def makeSubWindow(self, title, type, x=None, y=None, windowWidth=None, close=True):
        """Open a new window"""
        self.requestWindowUpdate()
        if windowWidth is None:
            windowWidth = self.windowWidth

        subWindow = Toplevel(self.window)
        subWindow.configure(bg=self.theme['frame']['bg'])
        subWindow.title(title)
        if type == 'splash':
            subWindow.overrideredirect(True)  # No window elements, must implement close window or bring it down manually
        else:
            subWindow.resizable(False,False)
            subWindow.transient(self.window)
        subWindow.geometry(self.subWindowLocationCentered(x, y, type))

        subWindow.protocol('WM_DELETE_WINDOW', lambda:self.windowCloseCallback(subWindow))
        subWindow.grid_columnconfigure(0, weight=1)
        topFrame = Frame(subWindow, width=windowWidth, bg=self.theme['frame']['bg'])
        topFrame.grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        if close and type == 'splash':
            optionFrame = HoverButton(topFrame, text='Close', command=lambda:self.windowCloseCallback(subWindow))
            optionFrame.configure(bg=self.theme['button']['bg'],fg=self.theme['button']['fg'], borderwidth=0, width=10)
            optionFrame.grid(row=0, column=0, sticky='ew')
            topFrame.grid_rowconfigure(0, minsize=10)
            topFrame.grid_columnconfigure(0, weight=1)
        mainFrame = Frame(subWindow, bg=self.theme['frame']['bg'])
        mainFrame.grid(row=1, column=0, sticky='nsew', padx=1, pady=1)
        subWindow.grid_rowconfigure(1, weight=1)

        if type == 'splash':
            self.splash_window_interior(mainFrame)
        if type == 'log':
            self.log_window_interior(mainFrame)

        subWindow.title('{}'.format(title))
        subWindow.wait_visibility()    #Implemented for Linux
        subWindow.grab_set()
        subWindow.update()
        if not type == 'splash' or close:
            subWindow.wait_window()

        return subWindow


    def log_window_interior(self, parentFrame):
        scrollbar = Scrollbar(parentFrame)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.logDisplay = Text(parentFrame, bg=self.theme['entry_dark']['bg'], fg=self.theme['entry_dark']['fg'],
                               wrap=WORD, height=30, width=110, font=self.font_tuple_create('text_log'))
        self.logDisplay.pack(side=LEFT, fill=BOTH, expand=True)
        self.logDisplay.insert('0.0', self.logFull.get())
        scrollbar.config(command=self.logDisplay.yview)
        self.logDisplay.config(yscrollcommand=scrollbar.set)
        self.logDisplayUpdate()


    def splash_window_interior(self, parentFrame):
        OuterFrame = Frame(parentFrame, bg=self.theme['frame']['bg'])
        OuterFrame.grid(row=0, column=0)
        parentFrame.grid_rowconfigure(0, weight=1)
        parentFrame.grid_columnconfigure(0, weight=1)
        OuterFrame.grid_columnconfigure(0, weight=0, minsize=self.splash_image_w)
        OuterFrame.grid_rowconfigure(0, weight=0, minsize=self.splash_image_h+25)

        imageLabel = Canvas(OuterFrame, bg=self.theme['button']['bg'])
        imageLabel.configure(borderwidth=0, highlightthickness=0)
        imageLabel.create_image(self.splash_image_w / 2, self.splash_image_h / 2, anchor="center", image=self.images['splash_image'])
        imageLabel.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)

        self.splashProgressBar = Progressbar(OuterFrame, orient='horizontal', mode='indeterminate', length=self.splash_image_w)
        self.splashProgressBar.grid(row=0, column=0, sticky='sw')

        self.splashText = StringVar()
        label = Label(OuterFrame, height=4, textvariable=self.splashText, bg=self.theme['frame']['bg'], fg=self.theme['frame']['fg'], wraplength=400)
        label.grid(row=1, column=0, sticky='n')
        label.grid(row=1, column=0, sticky='n')

    def itemLabelCallback(self, e, canvas, img, i, key, args):
        """Common callback for ship equipment labels"""
        self.precacheEquipment(args[0])
        itemVar = {"item":'',"image":self.emptyImage, "rarity": self.persistent['rarityDefault'], "mark": self.persistent['markDefault'], "modifiers":['']}

        # items_list = [ (item.replace(args[2], ''), self.imageFromInfoboxName(item)) for item in list(self.cache['equipment'][args[0]].keys())]
        items_list = self.cache['equipmentWithImages'][args[0]]
        items_list = self.restrictItemsList(items_list)  # Most restrictions should come from the ship

        self.picker_getresult(canvas, img, i, key, args, items_list, item_initial=itemVar, type='item', title='Pick', extra_frames=[self.setupRarityFrame])


    def traitLabelCallback(self, e, canvas, img, i, key, args):
        """Common callback for all trait labels"""
        items_list=None
        if args[2]:
            self.precacheShipTraits()
            items_list = self.cache['shipTraitsWithImages']['cache']
        else:
            self.precacheTraits()
            traitType = "personal"
            if args[1]:
                traitType = "activereputation"
            elif args[0]:
                traitType = "reputation"
            items_list = self.cache['traitsWithImages'][traitType][args[3]]
            self.logWriteSimple('traitLabelCallback', '', 4, tags=[traitType, args[3], str(len(items_list))])

        items_list = self.restrictItemsList(items_list)  # What restrictions exist for traits?
        self.picker_getresult(canvas, img, i, key, args, items_list, type='trait', title='Pick trait')

    def picker_getresult(self, canvas, img, i, key, args, items_list, item_initial=None, type=None, title='Pick', extra_frames=None):
        tooltip_uuid = self.uuid_assign_for_tooltip()
        item_var = item_initial if item_initial is not None else self.getEmptyItem()
        additional = [self.setupSearchFrame]
        if extra_frames:
            additional += extra_frames
        self.tooltip_tracking['X'] = True
        item = self.pickerGui(title, item_var, items_list, additional)
        self.tooltip_tracking['X'] = False
        if 'item' in item and len(item['item']):
            name = item['item']
            if name == 'X':  # Clear slot
                canvas.itemconfig(img[0],image=self.emptyImage)
                canvas.itemconfig(img[1],image=self.emptyImage)
                if type == 'boffs':
                    self.build['boffs'][key][i] = ''
                else:
                    self.build[key][i] = None
            else:
                backend_key = '{}_{}'.format(name, i)
                self.backend['images'][backend_key] = item['image']  # index needed for item duplicate display
                canvas.itemconfig(img[0], image=item['image'])

                if type == 'item':
                    group_key = args[0]
                    if 'rarity' in self.cache['equipment'][group_key][name]:
                        rarityDefaultItem = self.cache['equipment'][group_key][name]['rarity']
                    else:
                        rarityDefaultItem = self.rarities[0]

                    if 'rarity' not in item or item['item'] == '' or item['rarity'] == '':
                        item['rarity'] = rarityDefaultItem

                    image1 = self.imageFromInfoboxName(item['rarity'])
                    self.backend['images'][backend_key+item['rarity']] = image1
                    canvas.itemconfig(img[1], image=image1)
                else:
                    group_key = ''

                environment = args[3] if args is not None and len(args) >= 4 else 'space'
                canvas.bind('<Enter>', lambda e,tooltip_uuid=tooltip_uuid,item=item:self.setupInfoboxFrameTooltipDraw(tooltip_uuid, item, group_key, environment))
                canvas.bind('<Leave>', lambda e,tooltip_uuid=tooltip_uuid: self.setupInfoboxFrameLeave(tooltip_uuid))
                item.pop('image')
                if type == 'boffs':
                    self.build['boffs'][key][i] = name
                else:
                    self.build[key][i] = item
            self.auto_save_queue()

    def font_dict_create(self, name):
        (family, size, weight) = self.font_tuple_create(name)
        return {'family': family, 'size': size, 'weight': weight}

    def font_tuple_create(self, name):
        font_family = self.theme[name]['font']['family'] if 'family' in self.theme[name]['font'] else self.theme['app']['font']['family']
        font_size = self.theme[name]['font']['size'] if 'size' in self.theme[name]['font'] else self.theme['app']['font']['size']
        font_weight = self.theme[name]['font']['weight'] if 'weight' in self.theme[name]['font'] else self.theme['app']['font']['weight']
        return (font_family, font_size, font_weight)

    def font_tuple_merge(self, name, family=None, size=None, weight=None):
        tuple_build = self.font.tuple.create(name)
        if family is not None:
            tuple_build[0] = family
        if size is not None:
            tuple_build[1] = size
        if weight is not None:
            tuple_build[2] = weight

        return (family, size, weight)

    def precache_theme_fonts(self):
        i = 0
        for key in self.theme:
            if not 'font' in self.theme[key]:
                continue
            else:
                i += 1
                font_tuple = self.font_tuple_create(key)
                self.theme[key]['font_object'] = font.Font(font=font_tuple)

        self.logWriteCounter('precache_theme_fonts', '(json)', i, [self.theme['name']])

    def precacheBoffAbilitiesSingle(self, name, environment, type, category, desc):
        # category is Tactical, Science, Engineer, Specs
        # type is the boff ability rank
        name = self.deWikify(name)
        if not environment in self.cache['boffTooltips']:
            self.cache['boffTooltips'][environment] = dict()
        if not name in self.cache['boffTooltips'][environment]:
            # Longer descriptions stored only once
            self.cache['boffTooltips'][environment][name] = self.deWikify(desc, leaveHTML=True)

        if not environment in self.cache['boffAbilities']:
            self.cache['boffAbilities'][environment] = dict()
        if not type in self.cache['boffAbilities'][environment]:
            self.cache['boffAbilities'][environment][type] = dict()

        if not environment in self.cache['boffAbilitiesWithImages']:
            self.cache['boffAbilitiesWithImages'][environment] = dict()
        if not category in self.cache['boffAbilitiesWithImages'][environment]:
            self.cache['boffAbilitiesWithImages'][environment][category] = dict()
        if not type in self.cache['boffAbilitiesWithImages'][environment][category]:
            self.cache['boffAbilitiesWithImages'][environment][category][type] = []

        if not name in self.cache['boffAbilities'][environment][type]:
            self.cache['boffAbilities'][environment][type][name] = 'yes'

            self.cache['boffAbilitiesWithImages'][environment][category][type].append((name,self.imageFromInfoboxName(name, faction = 1)))

            self.logWriteSimple('precacheBoffAbilities', 'Single', 4, tags=[environment, category, str(type), name, '|'+str(len(desc))+'|'])

    def precacheBoffAbilities(self, limited=False):
        """Common callback for boff labels"""
        if 'boffAbilities' in self.cache and 'space' in self.cache['boffAbilities'] and 'ground' in self.cache['boffAbilities']:
            return

        # Categories beyond tac/eng/sci should come from a json load when capt specs are converted
        boffCategories = ['Tactical', 'Engineering', 'Science', 'Intelligence', 'Command', 'Pilot', 'Temporal', 'Miracle Worker']
        boffRanks = [1, 2, 3, 4]
        boffEnvironments = ['space', 'ground']

        for environment in boffEnvironments:
            l0 = [h2 for h2 in self.r_boffAbilities.find('h2') if ' Abilities' in h2.html]
            if environment == 'ground':
                l0 = [l for l in l0 if "Pilot" not in l.text]
                l1 = self.r_boffAbilities.find('h2+h3+table+h3+table')
            else:
                l1 = self.r_boffAbilities.find('h2+h3+table')

            for category in boffCategories:
                table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#'+category.replace(' ','_')+'_Abilities', first=True), Element)]
                if not len(table):
                    continue
                trs = table[0].find('tr')
                for tr in trs:
                    tds = tr.find('td')
                    rank1 = 1
                    for i in [0, 1, 2]:
                        if len(tds)>0 and tds[rank1+i].text.strip() != '':
                            cname = tds[0].text.strip()
                            desc = tds[5].text.strip()
                            if desc == 'III':
                                desc = tds[6].text.strip()
                            self.precacheBoffAbilitiesSingle(cname, environment, rank1+i, category, desc)
                            if i == 2 and tds[rank1+i].text.strip() in ['I', 'II']:
                                self.precacheBoffAbilitiesSingle(cname, environment, rank1+i+1, category, desc)
                            self.logWriteSimple('precacheBoffAbilities', '', 4, tags=[environment, category, str(rank1+i)])

        self.logWriteCounter('Boff ability', '(json)', len(self.cache['boffTooltips']['space']), ['space'])
        self.logWriteCounter('Boff ability', '(json)', len(self.cache['boffTooltips']['ground']), ['ground'])

    def boffLabelCallback(self, e, canvas, img, i, key, args):
        """Common callback for boff labels"""
        self.precacheBoffAbilities()

        spec = self.boffTitleToSpec(args[0].get()) if args[0] else ''
        spec2 = args[1].get() if args[1] else ''
        # args[2] is the same as i
        environment = args[3] if args is not None and len(args) >= 4 else 'space'

        items_list = []
        rank = i + 1

        self.logWriteSimple('spaceBoffLabel', 'Callback', 3, tags=[environment, spec, spec2, i, key])

        if spec == 'universal':
            for specType in self.universalTypes:
                items_list = items_list + self.cache['boffAbilitiesWithImages'][environment][specType][rank]
        else:
            items_list = self.cache['boffAbilitiesWithImages'][environment][spec][rank]
        if spec2 is not None and spec2 != '':
            items_list = items_list + self.cache['boffAbilitiesWithImages'][environment][spec2][rank]

        items_list = self.restrictItemsList(items_list) # need to send boffseat spec/spec2
        self.picker_getresult(canvas, img, i, key, args, items_list, type='boffs', title='Pick ability')


    def uuid_assign_for_tooltip(self):
        return str(uuid.uuid4())

    def shipMenuCallback(self, *args):
        """Callback for ship selection menu"""
        if self.backend['ship'].get() == '':
            return
        self.build['ship'] = self.backend['ship'].get()
        self.backend['shipHtml'] = self.getShipFromName(self.ships, self.build['ship'])
        tier = self.backend['shipHtml']['tier']

        self.clearFrame(self.shipTierFrame)
        self.setupTierFrame(tier)
        self.setupShipImageFrame()
        self.backend['tier'].set(self.getTierOptions(tier)[0])
        self.auto_save_queue()

    def shipPickButtonCallback(self, *args):
        """Callback for ship picker button"""
        itemVar = self.getEmptyItem()
        items_list = [(name, '') for name in self.shipNames]
        # restrict by faction if not KDF unlocked?
        item = self.pickerGui('Pick Starship', itemVar, items_list, [self.setupSearchFrame])
        if 'item' in item and len(item['item']):
            self.resetShipSettings()
            if item['item'] == 'X':
                item['item'] = ''
                self.build['ship'] = item['item']
                self.backend['shipHtml'] = None
                self.setShipImage()
                self.shipButton.configure(text=item['item'])
                self.backend['ship'].set(item['item'])
                self.setupCurrentBuildFrames('space')
            else:
                self.shipButton.configure(text=item['item'])
                self.backend['ship'].set(item['item'])
                self.setupBoffFrame('space', self.backend['shipHtml'])
            self.auto_save_queue()

    def importCallback(self, event=None):
        """Callback for import button"""
        if self.in_splash():
            return
        initialDir = self.getFolderLocation('library')
        inFilename = filedialog.askopenfilename(filetypes=[('SETS files', '*.json *.png'),('JSON files', '*.json'),('PNG image','*.png'),('All Files','*.*')], initialdir=initialDir)
        self.importByFilename(inFilename)

    def get_display_window(self, title, text):
        w = Toplevel(self.window, bg=self.theme['app']['bg'])
        w.title(title)
        w.geometry('{}x{}'.format(int(self.windowWidth / 2), self.windowHeight))
        f = Frame(w, bg=self.theme['app']['fg'])
        f.pack(fill=BOTH, expand=True, padx=15, pady=15)
        t = Text(f, bg=self.theme["app"]["fg"], fg="#ffffff", relief="flat")
        t.pack(fill=BOTH, expand=True)

        t.configure(state=NORMAL)
        t.delete('1.0',END)
        t.insert(END, text)
        t.configure(state=DISABLED)
        w.mainloop()

    def merge_file_create(self):
        eol = '\r\n'
        name = 'Merge file'
        initialDir = self.getFolderLocation('library')
        inFilename = filedialog.askopenfilename(filetypes=[('SETS merge files', '*.txt'),('All Files','*.*')], initialdir=initialDir)
        if not inFilename or not os.path.exists(inFilename) or not os.path.getsize(inFilename):
            return False

        self.makeSplash()
        with open(inFilename, 'r') as inFile:
            self.logWriteTransaction(name, 'loaded', '', inFilename, 1)
            self.logWriteBreak('MERGE PROCESSING START')
            data = inFile.read()
            data = re.sub('"""[^"]*"""', '', data) # Clear file comments
            data = self.merge_walk(data, self.build)
            data = re.sub('{{.[^}]*}}[\r\n]+', '', data, re.M)  # Clear unused merge entries
            data = re.sub('{{.[^}]*}}', '', data)  # Clear unused merge entries
            self.logWriteBreak('MERGE PROCESSING END')
        self.closeSplash()

        self.get_display_window('Merge export', data)

    def merge_walk(self, data, tree, tag_pre=''):
        self.logWriteSimple('merge', '', 2, [tag_pre])
        eol = '\n'
        full_list = ''
        if isinstance(tree, dict):
            for subtype in tree:
                tag = '{}{}'.format(tag_pre, subtype.upper())
                data = data.replace('{{{{{}}}}}'.format(tag), '{}'.format(tree[subtype]))
                full_list_item = self.merge_list(tree[subtype])
                full_list += '{}{}:{}'.format(eol if full_list else '', subtype, full_list_item) if full_list_item else ''
                data = self.merge_walk(data, tree[subtype], tag + ':')
            data = data.replace('{{{{{}*}}}}'.format(tag_pre, '*'), full_list)
        elif isinstance(tree, list):
            for i in range(len(tree)):
                tag = '{}{}'.format(tag_pre, i)
                data = data.replace('{{{{{}}}}}'.format(tag), '{}'.format(tree[i]))
                full_list_item = self.merge_list(tree[i])
                full_list += '{}{}:{}'.format(eol if full_list else '', i+1, full_list_item) if full_list_item else ''
                data = self.merge_walk(data, tree[i], tag + ':')
            data = data.replace('{{{{{}*}}}}'.format(tag_pre, '*'), full_list)
        elif tag_pre:
            tag = '{}'.format(tag_pre)
            data = data.replace('{{{{{}}}}}'.format(tag), '{}'.format(tree))

        return data

    def merge_list(self, tree):
        if isinstance(tree, dict) and 'item' in tree:
            tree = tree['item']

        if tree is None:
            tree = ''

        return '{}'.format(tree)

    def importByFilename(self, inFilename, force=False, autosave=False):
        if not inFilename or not os.path.exists(inFilename) or not os.path.getsize(inFilename):
            return False
        self.logWriteBreak('IMPORT START')
        name = '{} file'.format('Autosave' if autosave else 'Template')
        self.makeSplash()
        if inFilename.lower().endswith('.png'):
            # image = Image.open(inFilename)
            # self.build = json.loads(image.text['build'])
            try:
                self.buildImport = json.loads(self.decodeBuildFromImage(inFilename))
            except:
                self.logWriteTransaction(name, 'PNG load error', '', inFilename, 0)
                self.removeSplashWindow()
                return
        else:
            with open(inFilename, 'r') as inFile:
                try:
                    self.buildImport = json.load(inFile)
                except:
                    self.logWriteTransaction(name, 'load complaint', '', inFilename, 0)

        if self.persistent['versioning'] and isinstance(self.buildImport, dict):
            self.buildImport = [self.buildImport]

        if isinstance(self.buildImport, list) and self.buildImport:
            buildRevisionCurrent = self.buildImport[-1]
        else:
            buildRevisionCurrent = self.buildImport

        if not force and 'versionJSON' not in buildRevisionCurrent:
            result = False
            self.logWriteTransaction(name, 'version missing', '', inFilename, 0)
        elif not force and buildRevisionCurrent['versionJSON'] < self.versionJSONminimum:
            result = False
            self.logWriteTransaction(name, 'version mismatch', '', inFilename, 0, [str(buildRevisionCurrent['versionJSON'])+' < '+str(self.versionJSONminimum)])
        else:
            result = True
            self.logWriteBreak('IMPORT PROCESSING START')
            logNote = '{} (fields:[{}=>{}]='.format(' (FORCE LOAD)' if force else '', len(buildRevisionCurrent), len(self.build))
            self.build.update(buildRevisionCurrent)
            logNote = logNote+'{} merged'.format(len(self.build))

            self.resetBackend(rebuild=True)
            self.resetBuildFrames()
            self.setupCurrentBuildFrames()
            self.resetAfterImport()

            self.logWriteTransaction(name, 'loaded', '', inFilename, 0, [logNote])
            self.logWriteBreak('IMPORT PROCESSING END')

        self.closeSplash()
        if not result and self.persistent['forceJsonLoad']:
            return self.importByFilename(inFilename, True)
        else:
            return result

    def filenameDefault(self):
        name = self.build['playerShipName'] if 'playerShipName' in self.build else ''
        type = self.build['ship'] if 'ship' in self.build else ''

        if name and type: filename = "{} ({})".format(name, type)
        elif name: filename = name
        elif type: filename = type
        else: filename = ''

        filename = self.filename_sanitizer(filename)

        return filename

    def in_splash(self):
        return self.visible_window == 'splash'

    def exportCallback(self, event=None):
        """Callback for export as png button"""
        if self.in_splash():
            return
        # pixel correction
        self.requestWindowUpdate('force')

        screenTopLeftX = self.window.winfo_rootx()
        screenTopLeftY = self.window.winfo_rooty()
        screenBottomRightX = screenTopLeftX + self.window.winfo_width()
        screenBottomRightY = screenTopLeftY + self.window.winfo_height()
        image = ImageGrab.grab(bbox=(screenTopLeftX, screenTopLeftY, screenBottomRightX, screenBottomRightY))

        initialDir = self.getFolderLocation('library')
        filetypesOptions = [('PNG image','*.png'),('JSON file', '*.json'),('All Files','*.*')]
        defaultExtensionOption = 'png'
        if self.persistent['exportDefault'].lower() == 'json':
            filetypesOptions = [('JSON file', '*.json'),('PNG image','*.png'),('All Files','*.*')]
            defaultExtensionOption = 'json'
            #self.logWrite('==={}'.format(self.persistent['exportDefault'].lower()), 2)

        outFilename = filedialog.asksaveasfilename(defaultextension='.'+defaultExtensionOption,filetypes=filetypesOptions, initialfile=self.filenameDefault(), initialdir=initialDir)
        if not outFilename:
            return

        outFilename = self.filepath_sanitizer(outFilename)
        name_only, chosenExtension = os.path.splitext(outFilename)

        self.update_build_master()
        if chosenExtension.lower() == '.json':
            try:
                outFile = open(outFilename, 'w')
                json.dump(self.buildImport, outFile)
            except AttributeError:
                pass
        else:
            image.save(outFilename, chosenExtension.strip('.'))
            self.encodeBuildInImage(outFilename, json.dumps(self.buildImport), outFilename)

        self.logWriteTransaction('Export build', chosenExtension, str(os.path.getsize(outFilename)), outFilename, 0, [str(image.size) if chosenExtension.lower() == '.png' else None])

    def update_build_master(self):
        if self.persistent['versioning']:
            if self.build != self.buildImport[-1]:
                self.logWriteSimple('update_build_master', 'extend', 2, [len(self.buildImport)])
                self.buildImport = self.buildImport[-5:] + [self.build]
        else:
            self.buildImport = self.build

    def skillValidDeselect(self, name, environment, rank):
        """Checks whether deselecting a skill would cause the skill tree to be invalid."""
        if name in self.build['skilltree'][environment] and self.build["skilltree"][environment][name]:
            if environment == "space":
                rankRequirements = { '0': 'lieutenant','lieutenant':'0', '5' : 'lieutenant commander', 'lieutenant commander': '5', '15' : 'commander','commander':'15', '25' : 'captain', 'captain': '25', '35' : 'admiral', 'admiral': '35'}
                sktr = dict(self.backend['skillCount'][environment])
                sktr['sum'] = sktr['sum']-1
                sktr[rank] = sktr[rank]-1
                li = list()
                subsum = sktr['lieutenant']
                for rsk in ['lieutenant commander', 'commander', 'captain', 'admiral']:
                    if (int(rankRequirements[rsk])) <= subsum:
                        li.append(True)
                    else:
                        if sktr[rsk] == 0:
                            li.append(True)
                        else:
                            li.append(False)
                    subsum += sktr[rsk]
                if False in li:
                    return False
                else:
                    return True

            elif environment == "ground":
                return True
        else:
            return True

    def skillAllowed(self, skill_id, environment):
        (rank, row, col) = skill_id
        name = self.skillGetFieldNode(environment, (rank, row, col), type='name')
        plusOne = self.skillGetFieldNode(environment, (rank, row, col+1), type='name')
        plusTwo = self.skillGetFieldNode(environment, (rank, row, col+2), type='name')
        minusOne = self.skillGetFieldNode(environment, (rank, row, col-1), type='name')
        minusTwo = self.skillGetFieldNode(environment, (rank, row, col-2), type='name')
        if environment == 'ground':
            maxSkills = 10 # Could be set by captain rank/level
            rankReqs = [0, 0]
            split = False
        else:
            maxSkills = 46 # Could be set by captain rank/level
            rankReqs = { 'lieutenant': 0, 'lieutenant commander': 5, 'commander': 15, 'captain': 25, 'admiral': 35 }
            split = self.skillGetFieldSkill(environment, (rank, row, None), type='linear')
        # col is the position-in-chain

        #if environment == 'ground': return True
        self.logWriteSimple('skillAllowed', environment, 3, [name, self.backend['skillCount'][environment]["sum"]])
        if not name in self.build['skilltree'][environment]: self.build['skilltree'][environment][name] = False
        enabled = self.build['skilltree'][environment][name]
        child = self.build['skilltree'][environment][plusOne] if plusOne and col < 2 else False
        child2 = self.build['skilltree'][environment][plusTwo] if plusTwo and col < 1 else False
        parent = self.build['skilltree'][environment][minusOne] if minusOne and col > 0 else True
        parent2 = self.build['skilltree'][environment][minusTwo] if minusTwo and col > 1 else True

        if enabled:  # Can we turn this off?
            # If this takes us below our current rank, are there skills above this rank?

            # Do we have requiredby that are True?
            if child2:
                return False
            if not (col == 1 and split):
                if child:
                    return False

        else:  # Can we turn this on?
            # Can we activate that rank?
            if environment == 'space':
                if self.backend['skillCount'][environment]["sum"] < rankReqs[rank]:
                    return False
            if self.backend['skillCount'][environment]["sum"] + 1 > maxSkills:
                return False
            # Is our required already True?
            if not parent2:
                return False
            if not (col == 2 and split):
                if not parent:
                    return False

        return True

    def skillButtonChildUpdate(self, skill_id, environment='space'):
        # Change disable status of children based on selection change

        return

    def get_theme_skill_icon(self, status):
        # Image, bg, relief
        if status:
            return (self.epicImage,
                    self.theme['icon_on']['bg'],
                    self.theme['icon_on']['relief']
                    )
        else:
            return (self.emptyImage,
                    self.theme['icon_off']['bg'],
                    self.theme['icon_off']['relief']
                    )

    def skillLabelCallback(self, e, canvas, img, i, key, args, environment='space'):
        skill_id, drawEnvironment = args
        (rank, row, col) = skill_id
        name = self.skillGetFieldNode(environment, skill_id, type='name')
        backendName = name

        if not self.skillAllowed(skill_id, environment):
            return # Check for requirements before enable
        if environment == 'space' and not self.skillValidDeselect(name, environment, rank):
            return # Check whether deselecting the skill would cause the skill tree to be invalid

        self.build['skilltree'][environment][name] = not self.build['skilltree'][environment][name]
        (image1, bg, relief) = self.get_theme_skill_icon(self.build['skilltree'][environment][name])
        canvas.configure(bg=bg, relief=relief)

        countChange = 1 if self.build['skilltree'][environment][name] else -1
        self.backend['skillCount'][environment]["sum"] += countChange
        if environment == "space":
            self.backend['skillCount'][environment][rank] += countChange
        self.backend['images'][backendName] = [self.backend['images'][backendName][0], image1]

        canvas.itemconfig(img[1],image=image1)

        self.skillButtonChildUpdate(skill_id, environment)
        self.auto_save_queue()

    def skillGroundLabelCallback(self, e, canvas, img, i, key, args, environment='ground'):
        self.skillLabelCallback(e, canvas, img, i, key, args, environment)

        return

    def redditExportDisplayGroundSkills(self, textframe: Text):
        textframe.configure(state=NORMAL)
        textframe.delete("1.0", END)
        textframe.insert(END, "TBD")
        textframe.configure(state=DISABLED)

    def redditExportDisplaySpaceSkills(self, textframe: Text):
        if not len(self.build["skilltree"]["space"]) == 90:
            return
        redditstring = "## **<u>Space Skills</u>**\n\n"
        column0 = list()
        column1 = list()
        column2 = list()
        column3 = list()
        for rank in self.cache['skills']['space']:
            for skill in self.cache['skills']['space'][rank]:
                if skill["linear"] == 0:
                    column0 = column0 + self.makeRedditColumn(["[**{0}**]({1})".format(skill["skill"], skill["link"])], 1)
                    column1 = column1 + self.makeRedditColumn(["**x**"] if self.build["skilltree"]["space"][skill["skill"]+" 1"]==True else [None], 1)
                    column2 = column2 + self.makeRedditColumn(["**x**"] if self.build["skilltree"]["space"][skill["skill"]+" 2"]==True else [None], 1)
                    column3 = column3 + self.makeRedditColumn(["**x**"] if self.build["skilltree"]["space"][skill["skill"]+" 3"]==True else [None], 1)
                else:
                    column0 = column0 + ["&nbsp;"]
                    column0 = column0 + self.makeRedditColumn(["[**{0}**]({1})".format(skill["skill"][0], skill["link"] if isinstance(skill["link"], str) else skill["link"][0])], 1)
                    if skill["linear"] == 1:
                        column1 = column1 + ["[{0}]({1})".format(skill["skill"][0], skill["link"][0])]
                        column1 = column1 + self.makeRedditColumn(["**x**"] if self.build["skilltree"]["space"][skill["skill"][0]+" 1"]==True else [None], 1)
                        column2 = column2 + ["[{0}]({1})".format("Improved "+skill["skill"][0], skill["link"][0])]
                        column2 = column2 + self.makeRedditColumn(["**x**"] if self.build["skilltree"]["space"][skill["skill"][0]+" 2"]==True else [None], 1)
                        column3 = column3 + ["[{0}]({1})".format(skill["skill"][1], skill["link"][1])]
                        column3 = column3 + self.makeRedditColumn(["**x**"] if self.build["skilltree"]["space"][skill["skill"][1]]==True else [None], 1)
                    elif skill["linear"] ==2:
                        column1 = column1 + ["[{0}]({1})".format(skill["skill"][0], skill["link"])]
                        column1 = column1 + self.makeRedditColumn(["**x**"] if self.build["skilltree"]["space"][skill["skill"][0]]==True else [None], 1)
                        column2 = column2 + ["[{0}]({1})".format(skill["skill"][1], skill["link"])]
                        column2 = column2 + self.makeRedditColumn(["**x**"] if self.build["skilltree"]["space"][skill["skill"][1]]==True else [None], 1)
                        column3 = column3 + ["[{0}]({1})".format(skill["skill"][2], skill["link"])]
                        column3 = column3 + self.makeRedditColumn(["**x**"] if self.build["skilltree"]["space"][skill["skill"][2]]==True else [None], 1) 
        redditstring = redditstring + self.makeRedditTable(['&nbsp;']+column0, ['**Base:**']+column1, ['**Improved:**']+column2, ['**Advanced:**']+column3, [":---",":-:",":-:",":-:"])
        textframe.configure(state=NORMAL)
        textframe.delete("1.0", END)
        textframe.insert(END, redditstring)
        textframe.configure(state=DISABLED)

    def redditExportDisplayGround(self, textframe:Text):
        if not self.build['eliteCaptain']:
            elite = 'No'
        elif self.build['eliteCaptain']:
            elite = 'Yes'
        else:
            elite = 'You should not be seeing this... PANIC!'
        redditString = "## **<u>Ground</u>**\n\n**Basic Information** | **Data** \n:--- | :--- \n*Player Name* | {0} \n*Player Species* | {1} \n*Player Career* | {2} \n*Elite Captain* | {3} \n*Primary Specialization* | {4} \n*Secondary Specialization* | {5}\n\n\n".format(self.backend['playerName'].get(), self.build['species'], self.build['career'], elite, self.build['specPrimary'], self.build['specSecondary'], self.build['playerDesc'])
        if self.build['playerDesc'] != '':
            redditString = redditString + "## Build Description\n\n{0}\n\n\n".format(self.build['playerDesc'])
        redditString = redditString +  "## Personal Equipment\n\n"
        column0 = (self.makeRedditColumn(["**Kit:**"],1)+
                   self.makeRedditColumn(["**Body Armor:**"],1)+
                   self.makeRedditColumn(["**EV Suit:**"],1)+
                   self.makeRedditColumn(["**Shields:**"],1)+
                   self.makeRedditColumn(["**Weapons:**"],2)+
                   self.makeRedditColumn(["**Devices:**"],5))
        column1 =(self.makeRedditColumn(self.preformatRedditEquipment('groundKit',1),1)+
                  self.makeRedditColumn(self.preformatRedditEquipment('groundArmor',1),1)+
                  self.makeRedditColumn(self.preformatRedditEquipment('groundEV',1),1)+
                  self.makeRedditColumn(self.preformatRedditEquipment('groundShield',1),1)+
                  self.makeRedditColumn(self.preformatRedditEquipment('groundWeapons',2),2)+
                  self.makeRedditColumn(self.preformatRedditEquipment('groundDevices',5),5))
        redditString = redditString + self.makeRedditTable(['&nbsp;']+column0, ['**Component**']+column1, ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n\n## Kit Modules\n\n"
        column0 = self.makeRedditColumn(self.preformatRedditEquipment('groundKitModules',6),6)
        redditString = redditString + self.makeRedditTable(['**Name**']+column0, ['**Description**']+[None]*len(column0), ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n\n## Traits\n\n"
        column0 = self.makeRedditColumn([trait['item'] for trait in self.build['personalGroundTrait'] if trait is not None] +
                                        [trait['item'] for trait in self.build['personalGroundTrait2'] if trait is not None], 11)
        redditString = redditString + self.makeRedditTable(['**Personal Ground Traits**']+column0, ['**Description**']+[None]*len(column0), ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n"
        column0 = self.makeRedditColumn([trait['item'] for trait in self.build['groundRepTrait'] if trait is not None], 5)
        redditString = redditString + self.makeRedditTable(['**Ground Reputation Traits**']+column0, ['**Description**']+[None]*len(column0), ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n"
        column0 = self.makeRedditColumn([trait['item'] for trait in self.build['groundActiveRepTrait'] if trait is not None], 5)
        redditString = redditString + self.makeRedditTable(['**Active Ground Reputation Traits**']+column0, ['**Description**']+[None]*len(column0), ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n## Active Ground Duty Officers\n\n"
        column0 = self.makeRedditColumn([self.build['doffs']['ground'][i-1]['spec'] for i in range(1,7) if self.build['doffs']['ground'][i-1] is not None], 6)
        column1 = self.makeRedditColumn([self.build['doffs']['ground'][i-1]['effect'] for i in range(1,7) if self.build['doffs']['ground'][i-1] is not None], 6)
        redditString = redditString + self.makeRedditTable(['**Specialization**']+column0, ['**Power**']+column1, ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n\n## Away Team\n\n"
        column0 = []
        column1 = []
        for groundboff in self.build['boffs'].keys():
            if "groundboff" in groundboff.lower():
                column0 = column0 + self.makeRedditColumn(["#{}: {} / {}".format(str(int(groundboff[-1])+1), self.build['boffseats']['ground'][int(groundboff[-1])],self.build['boffseats']['ground_spec'][int(groundboff[-1])])], len(self.build['boffs'][groundboff]))
                column1 = column1 + self.makeRedditColumn(self.build['boffs'][groundboff], len(self.build['boffs'][groundboff]))
        redditString = redditString + self.makeRedditTable(['**Profession**']+column0, ['**Power**']+column1, ['**Notes**']+[None]*len(column0))
        textframe.configure(state=NORMAL)
        textframe.delete("1.0",END)
        textframe.insert(END, redditString)
        textframe.configure(state=DISABLED)

    def redditExportDisplaySpace(self, textframe: Text):
        if not self.build['eliteCaptain']:
            elite = 'No'
        elif self.build['eliteCaptain']:
            elite = 'Yes'
        else:
            elite = 'You should not be seeing this... PANIC!'
        redditString = "## **<u>SPACE</u>**\n\n**Basic Information** | **Data** \n:--- | :--- \n*Ship Name* | {0} \n*Ship Class* | {1} \n*Ship Tier* | {2} \n*Player Career* | {3} \n*Elite Captain* | {4} \n*Primary Specialization* | {5} \n*Secondary Specialization* | {6}\n\n\n".format(self.backend["playerShipName"].get(), self.build['ship'], self.build['tier'], self.build['career'], elite, self.build['specPrimary'], self.build['specSecondary'])
        if self.build['playerShipDesc'] != '':
            redditString = redditString + "## Build Description\n\n{0}\n\n\n".format(self.build['playerShipDesc'])
        redditString = redditString + "## Ship Equipment\n\n"
        deviceBlanks = [None] * 6
        column0 = (self.makeRedditColumn(["**Fore Weapons:**"], self.backend['shipForeWeapons']) +
                   self.makeRedditColumn(["**Aft Weapons:**"], self.backend['shipAftWeapons']) +
                   self.makeRedditColumn(["**Deflector**", "**Impulse Engines**", "**Warp Core**", "**Shields**", "**Devices**"] + deviceBlanks[0:(self.backend['shipDevices']-1)] + (["**Secondary Deflector**"] if self.build['secdef'][0] is not None else ['&nbsp;']) + (["**Experimental Weapon**"] if self.build['experimental'][0] is not None else ['&nbsp;']), 7+max(self.backend['shipDevices']-1, 1)) +
                   self.makeRedditColumn(["**Engineering Consoles:**"], self.backend['shipEngConsoles']) +
                   self.makeRedditColumn(["**Science Consoles:**"], self.backend['shipSciConsoles']) +
                   self.makeRedditColumn(["**Tactical Consoles:**"], self.backend['shipTacConsoles']) +
                   self.makeRedditColumn(["**Universal Consoles:**"], self.backend['shipUniConsoles']))
        column1 = (self.makeRedditColumn(self.preformatRedditEquipment('foreWeapons', self.backend['shipForeWeapons']), self.backend['shipForeWeapons']) +
                   self.makeRedditColumn(self.preformatRedditEquipment('aftWeapons', self.backend['shipAftWeapons']), self.backend['shipAftWeapons']) +
                   self.makeRedditColumn(self.preformatRedditEquipment('deflector', 1) +
                                         self.preformatRedditEquipment('engines', 1) +
                                         self.preformatRedditEquipment('warpCore', 1) +
                                         self.preformatRedditEquipment('shield', 1) +
                                         self.preformatRedditEquipment('devices', self.backend['shipDevices']) +
                                         self.preformatRedditEquipment('secdef', 1 if self.build['secdef'][0] is not None else 0) +
                                         self.preformatRedditEquipment('experimental', 1 if self.build['experimental'][0] is not None else 0), 7+max(self.backend['shipDevices']-1, 1)) +
                   self.makeRedditColumn(self.preformatRedditEquipment('engConsoles', self.backend['shipEngConsoles']), self.backend['shipEngConsoles']) +
                   self.makeRedditColumn(self.preformatRedditEquipment('sciConsoles', self.backend['shipSciConsoles']), self.backend['shipSciConsoles']) +
                   self.makeRedditColumn(self.preformatRedditEquipment('tacConsoles', self.backend['shipTacConsoles']), self.backend['shipTacConsoles']) +
                   self.makeRedditColumn(self.preformatRedditEquipment('uniConsoles', self.backend['shipUniConsoles']), max(self.backend['shipUniConsoles'], 1)))
        redditString = redditString + self.makeRedditTable(['**Basic Information**']+column0, ['**Component**']+column1, ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n\n## Bridge Officer Stations\n\n"
        column0 = []
        column1 = []
        for spaceboff in self.build['boffs'].keys():
            if "spaceboff" in spaceboff.lower():
                column0 = column0 + self.makeRedditColumn([self.backend['shipHtml']['boffs'][int(spaceboff[-1])].replace("-", " / ")], len(self.build['boffs'][spaceboff]))
                column1 = column1 + self.makeRedditColumn(self.build['boffs'][spaceboff], len(self.build['boffs'][spaceboff]))
        redditString = redditString + self.makeRedditTable(['**Profession**']+column0, ['**Power**']+column1, ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n\n## Active Space Duty Officers\n\n"
        column0 = self.makeRedditColumn([self.build['doffs']['space'][i-1]['spec'] for i in range(1,7) if self.build['doffs']['space'][i-1] is not None], 6)
        column1 = self.makeRedditColumn([self.build['doffs']['space'][i-1]['effect'] for i in range(1,7) if self.build['doffs']['space'][i-1] is not None], 6)
        redditString = redditString + self.makeRedditTable(['**Specialization**']+column0, ['**Power**']+column1, ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n\n##    Traits\n\n"
        column0 = self.makeRedditColumn([trait['item'] for trait in self.build['personalSpaceTrait'] if trait is not None] +
                                        [trait['item'] for trait in self.build['personalSpaceTrait2'] if trait is not None], 11)
        redditString = redditString + self.makeRedditTable(['**Personal Space Traits**']+column0, ['**Description**']+[None]*len(column0), ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n"
        column0 = self.makeRedditColumn([trait['item'] for trait in self.build['starshipTrait'] if trait is not None], 6)
        redditString = redditString + self.makeRedditTable(['**Starship Traits**']+column0, ['**Description**']+[None]*len(column0), ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n"
        column0 = self.makeRedditColumn([trait['item'] for trait in self.build['spaceRepTrait'] if trait is not None], 5)
        redditString = redditString + self.makeRedditTable(['**Space Reputation Traits**']+column0, ['**Description**']+[None]*len(column0), ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n"
        column0 = self.makeRedditColumn([trait['item'] for trait in self.build['activeRepTrait'] if trait is not None], 5)
        redditString = redditString + self.makeRedditTable(['**Active Space Reputation Traits**']+column0, ['**Description**']+[None]*len(column0), ['**Notes**']+[None]*len(column0))
        textframe.configure(state=NORMAL)
        textframe.delete('1.0',END)
        textframe.insert(END, redditString)
        textframe.configure(state=DISABLED)

    def exportRedditCallback(self, event=None):
        if self.in_splash():
            return
        redditWindow = Toplevel(self.window, bg=self.theme["app"]["bg"])
        borderframe = Frame(redditWindow, bg=self.theme["app"]["fg"])
        borderframe.pack(fill=BOTH, expand=True, padx=15, pady=15)
        redditText = Text(borderframe, bg=self.theme["app"]["fg"], fg="#ffffff", relief="flat")
        btfr = Frame(borderframe)
        btfr.pack(side='top', fill='x')
        redditbtspace = HoverButton(btfr,text="SPACE", font=self.theme['button_medium']['font_object'],  bg=self.theme['button_medium']['bg'],fg=self.theme['button_medium']['fg'], activebackground=self.theme['button_medium']['hover'], padx = 0, command=lambda: self.redditExportDisplaySpace(redditText))
        redditbtground = HoverButton(btfr, text="GROUND", font =self.theme['button_medium']['font_object'], bg=self.theme['button_medium']['bg'], fg=self.theme['button_medium']['fg'], activebackground=self.theme['button_medium']['hover'],padx = 0, command=lambda: self.redditExportDisplayGround(redditText))
        redditbtsskill = HoverButton(btfr, text="SPACE SKILLS", font =self.theme['button_medium']['font_object'], bg=self.theme['button_medium']['bg'], fg=self.theme['button_medium']['fg'], activebackground=self.theme['button_medium']['hover'],padx = 0, command=lambda: self.redditExportDisplaySpaceSkills(redditText))
        redditbtgskill = HoverButton(btfr, text="GROUND SKILLS", font =self.theme['button_medium']['font_object'], bg=self.theme['button_medium']['bg'], fg=self.theme['button_medium']['fg'], activebackground=self.theme['button_medium']['hover'], padx= 0, command=lambda: self.redditExportDisplayGroundSkills(redditText))
        redditbtspace.grid(row=0,column=0,sticky="nsew")
        redditbtground.grid(row=0,column=1,sticky="nsew")
        redditbtsskill.grid(row=0, column=2, sticky="nsew")
        redditbtgskill.grid(row=0, column=3, sticky="nsew")
        for i in range(0, 4):
            btfr.grid_columnconfigure(i,weight=1)
        redditText.pack(fill=BOTH, expand=True)
        self.redditExportDisplaySpace(redditText)
        redditWindow.title("Reddit Export")
        redditWindow.mainloop()

    def clearCacheFolder(self, file=None):
        dir = self.getFolderLocation('cache')
        dirBak = self.getFolderLocation('backups')
        for filename in os.listdir(dir):
            if filename == file or filename.endswith('.json') or filename.endswith('.html'):
                file_path = os.path.join(dir, filename)
                backup_path = os.path.join(dirBak, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        if os.path.isfile(backup_path) or os.path.islink(backup_path):
                            os.unlink(backup_path)
                        os.rename(file_path, backup_path)
                except Exception as e:
                    self.logWrite('Failed to delete %s. Reason: %s' % (file_path, e), 2)
        #self.precachePreload()

    def clearImagesFolder(self):
        dir = self.getFolderLocation('images')
        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)
            try:
                os.unlink(file_path)
            except Exception as e:
                self.logWrite('Failed to delete %s. Reason: %s' % (file_path, e), 2)

    def settingsMenuCallback(self, choice, type):
        if self.in_splash():
            return

    def settingsButtonCallback(self, type):
        self.logWriteSimple("settingsButtonCallback", '', 2, [type])

        if type == 'clearcache':
            self.clearCacheFolder()
        elif type == 'clearimages':
            self.clearImagesFolder()
        elif type == 'clearfactionImages':
            self.persistent['imagesFactionAliases'] = dict()
            self.auto_save()
        elif type == 'clearmemcache':
            self.resetCache()
            self.requestWindowUpdateHold(0)
            self.precachePreload()
        elif type == 'cacheSave':
            self.save_json(self.getFileLocation('cache'), self.cache, 'Cache file', quiet=False)
        elif type == 'openLog':
            self.logWindowCreate()
        elif type == 'openSplash':
            self.updateWindowSize()
            self.makeSplashWindow(close=True)
        elif type == 'predownloadShipImages':
            self.predownloadShipImages()
        elif type == 'predownloadGearImages':
            self.predownloadGearImages()
        elif type == 'savePositionOnly' or type == 'savePosition':
            self.logWriteSimple(type, 'attributes', 2, [*self.window.attributes(), self.window.state()])
            if (self.window.attributes('-fullscreen')):
                self.persistent['geometry'] = '-fullscreen'
            elif (self.window.state() == 'zoomed'):
                self.persistent['geometry'] = 'zoomed'
            elif type == 'savePositionOnly':
                self.persistent['geometry'] = self.window.geometry()
            else:
                self.persistent['geometry'] = '+{}+{}'.format(self.window.winfo_x(), self.window.winfo_y())
            self.auto_save()
        elif type == 'resetPosition':
                self.persistent['geometry'] = ''
                self.auto_save()
                # self.updateWindowSize()
                self.setupGeometry()
        elif type == 'merge_file_create':
            self.merge_file_create()
        elif type == 'backupCache':
            # Backup state file
            # Backup caches (leave as current as well)
            # make a duplicate/compressed image archive folder?
            # make a duplicate/compressed library archive folder?  Just template?
            pass

    def buildToBackendSeries(self):
        self.copyBuildToBackend('playerHandle')
        self.copyBuildToBackend('playerShipName')
        self.copyBuildToBackend('playerShipDesc')
        self.copyBuildToBackend('playerDesc')
        self.copyBuildToBackend('captain', 'faction')
        self.copyBuildToBackend('career')
        self.copyBuildToBackend('species')
        self.copyBuildToBackend('specPrimary')
        self.copyBuildToBackend('specSecondary')
        self.copyBuildToBackend('ship')
        self.copyBuildToBackend('tier')
        self.copyBuildToBackendBoolean('eliteCaptain')

    def clearBuildCallback(self, event=None, type=None):
        """Callback for the clear build button"""
        self.resetBuild(type)
        self.clearing = 1

        self.buildToBackendSeries()
        #self.reset_skill_build(init=True)
        #self.backend['tier'].set('')
        self.backend['shipHtml'] = None
        self.shipImg = self.getEmptyFactionImage()
        self.groundImg = self.getEmptyFactionImage()
        self.setShipImage(self.shipImg)
        self.setCharImage(self.groundImg)

        self.resetBuildFrames()

        self.clearing = 0
        self.setupCurrentBuildFrames()
        self.auto_save_queue()

    def getEmptyFactionImage(self, faction=None):
        if faction is None:
            faction = self.persistent['factionDefault'].lower() if 'factionDefault' in self.persistent else 'federation'

        if faction in self.emptyImageFaction: return self.emptyImageFaction[faction]
        else: return self.emptyImage

    def boffUniversalCallback(self, v, idx, key):
        self.build['boffseats'][key][idx] = v.get()
        self.auto_save_queue()

    def doffStripPrefix(self, textBlock, isSpace=True):
        textBlock = self.deWikify(textBlock)
        if (isSpace and textBlock.startswith('[SP]')) or (not isSpace and textBlock.startswith('[GR]')):
            return textBlock[len('[--]'):]
        return textBlock

    def doffSpecCallback(self, om, v0, v1, row, isSpace=True):
        if self.cache['doffs'] is None:
            return
        self.build['doffs']['space' if isSpace else 'ground'][row] = {"name": "", "spec": v0.get(), "effect": ''}
        menu = om['menu']
        menu.delete(0, END)


        doff_desclist_space = sorted([self.doffStripPrefix(self.cache['doffs']['Space' if isSpace else 'Ground'][item]['description'], isSpace) for item in list(self.cache['doffs']['Space' if isSpace else 'Ground'].keys()) if v0.get() in item])

        for desc in doff_desclist_space:
            menu.add_command(label=desc, command=lambda v1=v1,value=desc: v1.set(value))

        self.setupDoffFrame(self.shipDoffFrame)
        self.setupDoffFrame(self.groundDoffFrame)
        self.auto_save_queue()

    def doffEffectCallback(self, om, v0, v1, row, isSpace=True):
        if self.cache['doffs'] is None:
            return
        self.build['doffs']['space' if isSpace else 'ground'][row]['effect'] = v1.get()
        self.setupDoffFrame(self.shipDoffFrame)
        self.setupDoffFrame(self.groundDoffFrame)
        self.auto_save_queue()

    def tagBoxCallback(self, var, text):
        self.build['tags'][text] = var.get()
        self.auto_save_queue()

    def eliteCaptainCallback(self, event=None):
        self.build['eliteCaptain'] = bool(self.backend['eliteCaptain'].get())
        self.setupCurrentBuildFrames()
        self.auto_save_queue()

    def markBoxCallback(self, itemVar, value):
        itemVar['mark'] = value

    def currentFrameRefresh(self):
        pass


    def currentFrameUpdateTo(self, frame=None, first=False):
        self.currentFrame = frame


    def focusFrameCallback(self, type='space', init=False):
        if self.in_splash() and type != 'return':
            return
        if type is None:
            type = 'space'

        self.reset_tooltip_tracking()
        previous = self.visible_window
        if self.visible_window != 'splash':
            self.visible_window_previous = previous
        if type == 'return':
            type = self.visible_window_previous

        self.visible_window = type
        self.logWriteSimple('focus', type, 3, [self.visible_window, self.visible_window_previous])

        if type == 'ground': self.currentFrameUpdateTo(self.groundBuildFrame)
        elif type == 'skill': self.currentFrameUpdateTo(self.skillTreeFrame)
        elif type == 'library': self.currentFrameUpdateTo(self.libraryFrame)
        elif type == 'settings': self.currentFrameUpdateTo(self.settingsFrame)
        elif type == 'space': self.currentFrameUpdateTo(self.spaceBuildFrame)
        elif type == 'splash': self.currentFrameUpdateTo(self.splashFrame)
        else: return

        self.groundBuildFrame.pack_forget() if type != 'ground' else None
        self.skillTreeFrame.pack_forget() if type != 'skill' else None
        self.libraryFrame.pack_forget() if type != 'library' else None
        self.settingsFrame.pack_forget() if type != 'settings' else None
        self.spaceBuildFrame.pack_forget() if type != 'space' else None
        if type != 'splash':
            self.splashFrame.pack_forget()

        self.currentFrame.pack(fill=BOTH, expand=True, padx=15)
        #self.currentFrame.place(height = self.framePriorheight) # Supposed to maintain frame height, may need grid
        if not init and type != 'splash':
            self.clearInfoboxFrame(type)

        if type == 'skill':
            self.setupCurrentSkillBuildFrames('space')

    # Could be removed with lambdas in the original command=
    def focusSpaceBuildFrameCallback(self): self.focusFrameCallback('space')
    def focusGroundBuildFrameCallback(self): self.focusFrameCallback('ground')
    def focusSkillTreeFrameCallback(self): self.focusFrameCallback('skill')
    def focusLibraryFrameCallback(self): self.focusFrameCallback('library')
    def focusSettingsFrameCallback(self): self.focusFrameCallback('settings')

    def focusSpaceSkillBuildFrameCallback(self): self.focusSkillBuildFrameCallback('space')
    def focusGroundSkillBuildFrameCallback(self): self.focusSkillBuildFrameCallback('ground')

    def focusSkillBuildFrameCallback(self, type='space', init=False):

        if type == 'ground': self.currentSkillFrame = self.skillGroundBuildFrame
        elif type == 'space': self.currentSkillFrame = self.skillSpaceBuildFrame
        else: return

        self.skillGroundBuildFrame.pack_forget() if type != 'ground' else None
        self.skillSpaceBuildFrame.pack_forget() if type != 'space' else None

        self.currentSkillFrame.pack(fill=BOTH, expand=True, padx=15)

        self.setupCurrentSkillBuildFrames(type) #here or in the main button callback?

    def setupCurrentBuildTagFrames(self, environment=None):
        if not self.clearing:
            if environment == 'space' or environment is None:
                self.updateTagsFrame('space')
            if environment == 'ground' or environment is None:
                self.updateTagsFrame('ground')
            if environment == 'skill' or environment is None:
                self.updateTagsFrame('skill')

    def setupCurrentBuildFrames(self, environment=None):
        if not self.clearing:
            self.setupCurrentBuildTagFrames(environment)
            if environment == 'space' or environment is None:
                self.setupSpaceBuildFrames()
            if environment == 'ground' or environment is None:
                self.setupGroundBuildFrames()
            if environment == 'skill' or environment is None:
                self.setupCurrentSkillBuildFrames()

    def setupCurrentSkillBuildFrames(self, environment=None):
        if not self.clearing:
            if environment is None: self.setupSkillBuildFrames()
            if environment == 'space': self.setupSkillBuildFrames('space')
            if environment == 'ground': self.setupSkillBuildFrames('ground')


    def setupCurrentTraitFrame(self):
        if not self.clearing:
            self.setupSpaceTraitFrame()
            self.setupGroundTraitFrame()

    def speciesUpdateCallback(self):
        self.copyBackendToBuild('species')
        self.setupCurrentTraitFrame()

    def setupClearSlotFrame(self, frame, itemVar, pickWindow):
        topbarFrame = Frame(frame)
        clearSlotButton = HoverButton(topbarFrame, text='Clear Slot', padx=5, bg=self.theme['button']['bg'], fg=self.theme['button']['fg'], activebackground=self.theme['button']['hover'])
        clearSlotButton.grid(row=0, column=0, sticky='nsew', padx=(10,15), pady=5)
        clearSlotButton.bind('<Button-1>', lambda e,name='X',image=self.emptyImage,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,image,v,win))
        topbarFrame.grid_columnconfigure(0, weight=1)
        topbarFrame.pack(fill=X, expand=False, side=TOP)

    def setupSearchFrame(self,frame,itemVar,content):
        topbarFrame = Frame(frame)
        searchText = StringVar()
        Label(topbarFrame, text="Search:").grid(row=0, column=0, sticky='w', padx=(25,2))
        searchEntry = Entry(topbarFrame, textvariable=searchText)
        searchEntry.grid(row=0, column=1, columnspan=5, sticky='nsew', padx=(2,40), ipady=3, pady=(5,2))
        topbarFrame.grid_columnconfigure(1, weight=1)
        searchEntry.focus_set()
        searchText.trace_add('write', lambda v,i,m,content=content,frame=frame:self.applyContentFilter(frame, content, searchText.get()))
        topbarFrame.pack(fill=BOTH, expand=False, side=TOP)

    def setupRarityFrame(self,frame,itemVar,content):
        topbarFrame = Frame(frame)
        mark = StringVar()
        if 'markDefault' in self.persistent and self.persistent['markDefault'] is not None:
            mark.set(self.persistent['markDefault'])
        topbarFrame.grid_columnconfigure(0, weight=2, uniform='setupRarityFrameColumns')
        topbarFrame.grid_columnconfigure(1, weight=1, uniform='setupRarityFrameColumns')
        topbarFrame.grid_columnconfigure(2, weight=2, uniform='setupRarityFrameColumns')
        markOption = OptionMenu(topbarFrame, mark, *self.marks)
        markOption.grid(row=0, column=0, sticky='nsew')
        rarity = StringVar(value=self.persistent['rarityDefault'])
        rarityOption = OptionMenu(topbarFrame, rarity, *self.rarities)
        rarityOption.grid(row=0, column=2, sticky='nsew')
        modFrame = Frame(topbarFrame)
        modFrame.grid(row=1, column=0, columnspan=3, sticky='nsew')
        mark.trace_add('write', lambda v,i,m:self.markBoxCallback(value=mark.get(), itemVar=itemVar))
        rarity.trace_add('write', lambda v,i,m,frame=modFrame:self.setupModFrame(frame, rarity=rarity.get(), itemVar=itemVar))
        topbarFrame.pack(side=TOP)
        if 'rarity' in itemVar and itemVar['rarity']:
            self.setupModFrame(modFrame, rarity=itemVar['rarity'], itemVar=itemVar)
        elif 'rarityDefault' in self.persistent and self.persistent['rarityDefault']:
            self.setupModFrame(modFrame, rarity=self.persistent['rarityDefault'], itemVar=itemVar)

    def labelBuildBlock(self, frame, name, row, col, cspan, key, n, callback, args=None, disabledCount=0):
        """Set up n-element line of ship equipment"""
        self.backend['images'][key] = [None] * n

        cFrame = Frame(frame, bg=self.theme['frame']['bg'])
        cFrame.grid(row=row, column=col, columnspan=cspan, sticky='nsew', padx=10)

        lFrame = Frame(cFrame, bg=self.theme['frame']['bg'])
        lFrame.pack(fill=BOTH, expand=True)
        label =  Label(lFrame, text=name, bg=self.theme['entry_dark']['bg'], fg=self.theme['entry_dark']['fg'])
        label.pack(side='left')
        iFrame = Frame(cFrame, bg=self.theme['frame']['bg'])
        iFrame.pack(fill=BOTH, expand=True)

        disabledStart = n - disabledCount
        for i in range(n):
            disabled = i >= disabledStart
            bg ='gray' if not disabled else 'black'
            padx = (25 + 3 * 2) if disabled else 2

            self.createButton(iFrame, bg=bg, row=row, column=i+1, padx=padx, disabled=disabled, key=key, i=i, callback=callback, args=args)


    def createButton(self, parentFrame, key, i=0, groupKey=None, callback=None, name=None, row=0, column=0, columnspan=1, rowspan=1, highlightthickness=theme['icon_off']['hlthick'], highlightbackground=theme['icon_off']['hlbg'], borderwidth=0, width=None, height=None, bg=theme['icon_off']['bg'], padx=2, pady=2, image0Name=None, image1Name=None, image0=None, image1=None, disabled=False, args=None, sticky='nse', relief=FLAT, tooltip=None, anchor='center', faction=False, suffix=''):
        """ Button building (including click and tooltip binds) """
        # self.build[key][buildSubKey] is the build code for callback updating and image identification
        # self.backend['images'][backendKey][#] is the location for (img,img)
        # args [array] contains variable infomation used for callback updating
        # internalKey is the cache sub-group (for equipment cache sub-groups)

        if width is None:
            width = self.itemBoxX
        if height is None:
            height = self.itemBoxY

        buildSubKey = name if name is not None else i
        backendKey = name if name is not None else key

        if name is not None:
            item = name
        elif groupKey is not None:
            item = self.build[groupKey][key][buildSubKey]
        else:
            item = self.build[key][buildSubKey]

        self.logWriteSimple('createButton', '', 5, [name, key, buildSubKey, backendKey, i, row, column])

        if type(item) is dict and item is not None:
            if image0Name is None and 'item' in item:
                image0Name = item['item']
            else:
                image0Name = item
            if image1Name is None and 'rarity' in item:
                image1Name = item['rarity']

        if not disabled:
            if image0 is None:
                image0=self.imageFromInfoboxName(image0Name, suffix=suffix, faction=faction) if image0Name is not None else self.emptyImage
            if image1 is None:
                image1=self.imageFromInfoboxName(image1Name, suffix=suffix, faction=faction) if image1Name is not None else self.emptyImage

            if name == 'blank':
                pass  # no backend/image
            elif name:
                self.backend['images'][name] = [image0, image1]
            else:
                if not backendKey in self.backend['images']:
                    self.backend['images'][backendKey] = [None] * 4
                self.backend['images'][backendKey][i] = [image0, image1]
        else:
            image0 = image0 if image0 is not None else self.emptyImage
            image1 = image1 if image1 is not None else self.emptyImage

        canvas = Canvas(parentFrame, highlightthickness=highlightthickness, highlightbackground=highlightbackground, borderwidth=borderwidth, width=width, height=height, bg=bg, relief=relief)
        canvas.grid(row=row, column=column, columnspan=columnspan, rowspan=rowspan, sticky=sticky, padx=padx, pady=pady)
        anchorWidth = width / 2 if anchor == 'center' else 0
        anchorHeight = height / 2 if anchor == 'center' else 0
        img0 = canvas.create_image(anchorWidth, anchorHeight, anchor=anchor, image=image0)
        img1 = None if image1 is None else canvas.create_image(anchorWidth, anchorHeight, anchor=anchor, image=image1)

        if disabled:
            canvas.itemconfig(img0, state=DISABLED)
            canvas.itemconfig(img1, state=DISABLED)
        else:
            tooltip_uuid = self.uuid_assign_for_tooltip()
            environment = args[-1] if args is not None and len(args) >= 2 else 'space'
            internalKey = args[0] if args is not None and type(args[0]) is str else ''
            if environment == 'skill':
                internalKey = args[0]

            if callback is not None:
                canvas.bind('<Button-1>', lambda e,canvas=canvas,img=(img0, img1),i=buildSubKey,args=args,key=key,callback=callback:callback(e,canvas,img,i,key,args))
            if name != 'blank':
                canvas.bind('<Enter>', lambda e,tooltip_uuid=tooltip_uuid,item=item,internalKey=internalKey,environment=environment,tooltip=tooltip:self.setupInfoboxFrameTooltipDraw(tooltip_uuid, item, internalKey, environment, tooltip))
                canvas.bind('<Leave>', lambda e,tooltip_uuid=tooltip_uuid:self.setupInfoboxFrameLeave(tooltip_uuid))

        return canvas, img0, img1

    def setupShipGearFrame(self, ship):
        """Set up UI frame containing ship equipment"""

        outerFrame = self.shipEquipmentFrame
        outerFrame.grid_rowconfigure(0, weight=1, uniform='shipFrameFullRowSpace')
        outerFrame.grid_columnconfigure(0, weight=1, uniform='shipFrameFullColSpace')
        self.clearFrame(outerFrame)

        parentFrame = Frame(outerFrame, bg=self.theme['frame']['bg'])
        parentFrame.grid(row=0, column=0, sticky='', padx=1, pady=1)

        if ship is None: ship = self.shipTemplate

        self.backend['shipForeWeapons'] = int(ship["fore"])
        self.backend['shipAftWeapons'] = int(ship["aft"])
        self.backend['shipDevices'] = int(ship["devices"])
        self.backend['shipTacConsoles'] = int(ship["consolestac"])
        self.backend['shipEngConsoles'] = int(ship["consoleseng"])
        self.backend['shipSciConsoles'] = int(ship["consolessci"])
        self.backend['shipUniConsoles'] = 1 if 'Innovation Effects' in ship["abilities"] else 0
        self.backend['shipHangars'] = 0 if ship["hangars"] == '' else int(ship["hangars"])
        if '-X' in self.backend['tier'].get():
            self.backend['shipUniConsoles'] = self.backend['shipUniConsoles'] + 1
            self.backend['shipDevices'] = self.backend['shipDevices'] + 1
        if 'T5-' in self.backend['tier'].get():
            t5console = ship["t5uconsole"]
            key = 'shipTacConsoles' if 'tac' in t5console else 'shipEngConsoles' if 'eng' in t5console else 'shipSciConsoles'
            self.backend[key] = self.backend[key] + 1

        self.labelBuildBlock(parentFrame, "Fore Weapons", 0, 0, 1, 'foreWeapons', self.backend['shipForeWeapons'], self.itemLabelCallback, ["Ship Fore Weapon", "Pick Fore Weapon", ""])
        if ship["secdeflector"] == 1:
            self.labelBuildBlock(parentFrame, "Secondary", 1, 1, 1, 'secdef', 1, self.itemLabelCallback, ["Ship Secondary Deflector", "Pick Secdef", ""])
        self.labelBuildBlock(parentFrame, "Deflector", 0, 1, 1, 'deflector', 1, self.itemLabelCallback, ["Ship Deflector Dish", "Pick Deflector", ""])
        self.labelBuildBlock(parentFrame, "Engines", 2, 1, 1, 'engines', 1, self.itemLabelCallback, ["Impulse Engine", "Pick Engine", ""])
        self.labelBuildBlock(parentFrame, "Core", 3, 1, 1, 'warpCore', 1, self.itemLabelCallback, ["Singularity Engine" if "Warbird" in self.build['ship'] or "Aves" in self.build['ship'] else "Warp ", "Pick Core", ""])
        self.labelBuildBlock(parentFrame, "Shield", 4, 1, 1, 'shield' , 1, self.itemLabelCallback, ["Ship Shields", "Pick Shield", ""])
        self.labelBuildBlock(parentFrame, "Aft Weapons", 1, 0, 1, 'aftWeapons', self.backend['shipAftWeapons'], self.itemLabelCallback, ["Ship Aft Weapon", "Pick aft weapon", ""])
        if ship["experimental"] == 1:
            self.labelBuildBlock(parentFrame, "Experimental", 2, 0, 1, 'experimental', 1, self.itemLabelCallback, ["Experimental", "Pick Experimental Weapon", ""])
        self.labelBuildBlock(parentFrame, "Devices", 3, 0, 1, 'devices', self.backend['shipDevices'], self.itemLabelCallback, ["Ship Device", "Pick Device (S)", ""])

        self.setupShipConsoleFrame()

    def setupShipConsoleFrame(self):
        outerFrame = self.shipConsoleFrame
        outerFrame.grid_rowconfigure(0, weight=1, uniform='shipConsoleFrameFullRowSpace')
        outerFrame.grid_columnconfigure(0, weight=1, uniform='shipConsoleFrameFullColSpace')
        self.clearFrame(outerFrame)

        parentFrame = Frame(outerFrame, bg=self.theme['frame']['bg'])
        parentFrame.grid(row=0, column=0, sticky='', padx=1, pady=1)

        consoleOptions = ['tac', 'eng', 'sci', 'uni']
        consoleTypes = ['Ship Tactical Console', 'Ship Engineering Console', 'Ship Science Console', 'Console']
        if self.persistent['consoleSort'] == 'uets':
            consoleOrder = [3,1,0,2]
        elif self.persistent['consoleSort'] == 'utse':
            consoleOrder = [3,0,2,1]
        elif self.persistent['consoleSort'] == 'uest':
            consoleOrder = [3,1,2,0]
        else:
            consoleOrder = [0,1,2,3]

        row = 0
        for i in consoleOrder:
            optTitle = consoleOptions[i].title()
            optFull = consoleTypes[i]
            optBackend = 'ship{}Consoles'.format(optTitle)
            optCount = self.backend[optBackend] if optBackend in self.backend else 0
            if optCount:
                self.labelBuildBlock(parentFrame, optTitle+' Consoles', row, 2, 1, consoleOptions[i]+'Consoles', self.backend[optBackend], self.itemLabelCallback, [optFull, 'Pick '+optTitle+' Console', ''])
                row += 1

        if self.backend['shipHangars'] > 0:
            self.labelBuildBlock(parentFrame, "Hangars", 4, 0, 1, 'hangars', self.backend['shipHangars'], self.itemLabelCallback, ["Hangar Bay", "Pick Hangar Pet", ""])

    def setupGroundGearFrame(self):
        """Set up UI frame containing ship equipment"""
        outerFrame = self.groundEquipmentFrame
        outerFrame.grid_rowconfigure(0, weight=1, uniform='shiptraitFrameFullRowSpace')
        outerFrame.grid_columnconfigure(0, weight=1, uniform='shiptraitFrameFullColSpace')
        self.clearFrame(outerFrame)

        parentFrame = Frame(outerFrame, bg=self.theme['frame']['bg'])
        parentFrame.grid(row=0, column=0, sticky='', padx=1, pady=1)

        self.labelBuildBlock(parentFrame, "Kit Modules", 0, 0, 5, 'groundKitModules', 6 if self.build['eliteCaptain'] else 5, self.itemLabelCallback, ["Kit Module", "Pick Module", "", 'ground'])
        self.labelBuildBlock(parentFrame, "Kit Frame", 0, 5, 1, 'groundKit', 1, self.itemLabelCallback, ["Kit Frame", "Pick Kit", "", 'ground'])
        self.labelBuildBlock(parentFrame, "Armor", 1, 0, 1, 'groundArmor', 1, self.itemLabelCallback, ["Body Armor", "Pick Armor", "", 'ground'])
        self.labelBuildBlock(parentFrame, "EV Suit", 1, 1, 1, 'groundEV', 1, self.itemLabelCallback, ["EV Suit", "Pick EV Suit", "", 'ground'])
        self.labelBuildBlock(parentFrame, "Shield", 2, 0, 1, 'groundShield', 1, self.itemLabelCallback, ["Personal Shield", "Pick Shield (G)", "", 'ground'])
        self.labelBuildBlock(parentFrame, "Weapons", 3, 0, 2, 'groundWeapons' , 2, self.itemLabelCallback, ["Ground Weapon", "Pick Weapon (G)", "", 'ground'])
        self.labelBuildBlock(parentFrame, "Devices", 4, 0, 5, 'groundDevices', 5 if self.build['eliteCaptain'] else 4, self.itemLabelCallback, ["Ground Device", "Pick Device (G)", "", 'ground'])

    def skillGetFieldNode(self, environment, skill_id, type='name'):
        (rank, row, col) = skill_id
        result = ''
        if self.cache['skills'][environment]:
            tree = self.cache['skills'][environment][rank] if environment == 'space' else self.cache['skills'][environment]
            try:
                result = tree[row]['nodes'][col][type]
            except:
                pass
        self.logWriteSimple('get', 'skillnode', 5, [environment, rank if environment == 'space' else '', row, 'nodes', col, type, '=', result])
        return result

    def skillGetFieldSkill(self, environment, skill_id, type='name'):
        result = ''
        if len(skill_id) != 3:
            return result
        (rank, row, col) = skill_id
        if rank is None:
            environment = 'ground'

        if self.cache['skills'][environment]:
            tree = self.cache['skills'][environment][rank] if environment == 'space' else self.cache['skills'][environment]
            try:
                if type in tree[row]:
                    result = tree[row][type]
            except:
                pass
        self.logWriteSimple('get', 'skillfield', 5, [environment, rank, row, type, result])
        return result

    def setupSkillBuildFrames(self, environment=None):
        if environment is None or environment == 'space':
            parentFrame = self.skillSpaceBuildFrame
            self.clearFrame(parentFrame)
            self.setup_skill_tree_frame(parentFrame, 'space')
            self.setupSkillBonusFrame(parentFrame, 'space')

        if environment is None or environment == 'ground':
            parentFrame = self.skillGroundBuildFrame
            self.clearFrame(parentFrame)
            self.setup_skill_tree_frame(parentFrame, 'ground')
            self.setupSkillBonusFrame(parentFrame, 'ground')

        # self.clearInfoboxFrame('skill')

    def setup_skill_tree_frame(self, parentFrame, environment='space'):
        self.precacheSkills(environment)
        if not self.cache['skills'][environment]:
            return

        frame = Frame(parentFrame, bg=self.theme['frame']['bg'])
        frame.grid(row=0, column=0, sticky='ns', padx=1, pady=1)
        parentFrame.grid_rowconfigure(0, weight=1, uniform='skillFrameFullRow'+environment)
        parentFrame.grid_columnconfigure(0, weight=1, uniform='skillFrameFullCol'+environment)

        rankRows = 8 if environment == 'ground' else 6
        ranks = [None, None] if environment == 'ground' else self.cache['skills'][environment]
        frame.grid_rowconfigure(0, weight=0, uniform='skillFrameRow'+environment)
        for row in range(rankRows):
            if environment == 'ground':
                frame.grid_rowconfigure(row, weight=1, uniform='skillFrameRow' + environment)
            else:
                rowGroup = "0" if row == 0 else ''
                frame.grid_rowconfigure((row * 2) + 1, weight=1, uniform='skillFrameRow' + environment + rowGroup)
                frame.grid_rowconfigure((row * 2) + 2, weight=1, uniform='skillFrameRow' + environment + rowGroup)
            rank = -1
            for rankName in ranks:
                rank += 1
                if environment == 'ground':
                    self.setup_skill_group_ground(frame, environment, rankName, row, rank)
                else:
                    self.setup_skill_group_space(frame, environment, rankName, row, rank)

    def setup_skill_group_ground(self, frame, environment, rankName, row, rank):
        rankColumns = 5

        for col in range(rankColumns):
            if row > 5:
                continue
            row_item = ((rank * 6) + row)
            col_item = col
            row_actual = (row + 1) if rank else row
            col_actual = ((rank * rankColumns) + col)
            split_row = self.skillGetFieldSkill(environment, (rankName, row_item, None), type='side')
            sticky = ''
            if split_row:
                if col == 0:
                    continue
                col_item -= 1
                if split_row == 'r':
                    sticky = 's'
                else:
                    sticky = 'n'

            skill_id = (rankName, row_item, col_item)

            name = self.skillGetFieldNode(environment, skill_id)
            # self.logWriteSimple('skill', 'ground', 2, [environment, rank, row_item, col_item, row_actual, col_actual, split_row, name])
            self.setupSkillButton(frame, rank, skill_id, col_item, row_actual, col_actual, environment, sticky=sticky)

    def setup_skill_group_space(self, frame, environment, rankName, row, rank):
        rankColumns = 4
        split_row = self.skillGetFieldSkill(environment, (rankName, row, None), type='linear')
        if row == 0:
            l = Label(frame, text=rankName.title().replace(' ', '\n'), bg=self.theme['entry_dark']['bg'], fg=self.theme['entry_dark']['fg'], font=self.theme['title2']['font_object'])
            l.grid(row=row, column=rank*rankColumns, columnspan=3, sticky='s', pady=1)
        for col in range(rankColumns):
            rowspan = 2
            sticky = sticky2 = ''
            if split_row and col == 1:
                rowspan = 1
                sticky = 's'
                sticky2 = 'n'
            if split_row and col == 2: col = 3
            rowspanMaster = 2
            col_actual = ((rank * rankColumns) + col)
            row_actual = (row * rowspanMaster) + 1
            skill_id = (rankName, row, col)

            self.setupSkillButton(frame, rank, skill_id, col, row_actual, col_actual, environment, rowspan=rowspan, sticky=sticky)
            if split_row and col == 1:
                row_actual = (row * rowspanMaster) + 2
                skill_id = (rankName, row, col+1)
                self.setupSkillButton(frame, rank, skill_id, col+1, row_actual, col_actual, environment, rowspan=rowspan, sticky=sticky2)

    def setupSkillButton(self, frame, rank, skill_id, col, row_actual, col_actual, environment, rowspan=1, sticky=''):
        padxCanvas = (2,2)
        padyCanvas = (3,0) if row_actual % 2 != 0 else (0, 3)
        frame.grid_columnconfigure(col_actual, weight=2 if col == 3 else 1, uniform='skillFrameCol' + environment + str(rank))
        name = self.skillGetFieldNode(environment, skill_id, type='name')

        backendName = name
        args = [skill_id, 'skill']
        self.logWriteSimple('SkillButton', 'create', 5, [skill_id, environment, name])
        if not environment in self.build['skilltree']: self.build['skilltree'][environment] = dict()

        if name and col != 3:
            imagename = self.skillGetFieldNode(environment, skill_id, type='image')
            desc = self.skillGetFieldNode(environment, skill_id, type='desc')
            callback = self.skillGroundLabelCallback if environment == 'ground' else self.skillLabelCallback

            if not name in self.build['skilltree'][environment]:
                self.build['skilltree'][environment][name] = False
            if not backendName in self.backend['images']:
                self.backend['images'][backendName] = [ ]

            (image1, bg, relief) = self.get_theme_skill_icon(self.build['skilltree'][environment][name])

            self.createButton(frame, 'skilltree', callback=callback, row=row_actual, rowspan=rowspan, column=col_actual, borderwidth=1, bg=bg, image0Name=imagename, image1=image1, sticky=sticky, relief=relief, padx=padxCanvas, pady=padyCanvas, args=args, name=name, tooltip=desc, anchor='center')
        else:
            self.createButton(frame, '', row=row_actual, rowspan=rowspan, column=col_actual, borderwidth=1, bg=self.theme['button']['bg'], image0=self.emptyImage, sticky='ns', padx=padxCanvas, pady=padyCanvas, args=args, name='blank', anchor='center')

    def setupSkillBonusFrame(self, parentFrame, environment='space'):
        frame = Frame(parentFrame, bg=self.theme['frame']['bg'])
        frame.grid(row=0, column=1, sticky='ns', padx=1, pady=1)
        parentFrame.grid_rowconfigure(0, weight=1, uniform='skillBonusFrameFullRowSpace')
        parentFrame.grid_columnconfigure(0, weight=1, uniform='skillBonusFrameFullColSpace')

        padxCanvas = (2,2)
        padyCanvas = (1,1)
        for row in range(11):
            frame.grid_rowconfigure(row, weight=1, uniform='skillBonusFrameRowSpace')
            for col in range(4):
                colActual = col
                frame.grid_columnconfigure(colActual, weight=2 if col == 3 else 1, uniform='skillBonusFrameColSpace'+str(col))
                args = [(None, row, col), 'skill']

                self.createButton(frame, '', row=row, column=colActual, borderwidth=1, bg=self.theme['button']['bg'], image0=self.emptyImage, sticky='n', padx=padxCanvas, pady=padyCanvas, args=args, name='blank', anchor='center')

    def setupSpaceTraitFrame(self):
        """Set up UI frame containing traits"""
        outerFrame = self.shipTraitFrame
        outerFrame.grid_rowconfigure(0, weight=1, uniform='shiptraitFrameFullRowSpace')
        outerFrame.grid_columnconfigure(0, weight=1, uniform='shiptraitFrameFullColSpace')
        self.clearFrame(outerFrame)

        parentFrame = Frame(outerFrame, bg=self.theme['frame']['bg'])
        parentFrame.grid(row=0, column=0, sticky='', padx=1, pady=1)

        traitEliteCaptain = 1 if self.build['eliteCaptain'] else 0
        traitAlien = 1 if 'Alien' in self.backend['species'].get() else 0
        self.labelBuildBlock(parentFrame, "Personal", 0, 0, 1, 'personalSpaceTrait', 6 if traitEliteCaptain else 5, self.traitLabelCallback, [False, False, False, "space"])
        self.labelBuildBlock(parentFrame, "Personal", 1, 0, 1, 'personalSpaceTrait2', 5, self.traitLabelCallback, [False, False, False, "space"], 1 if not traitAlien else 0)
        self.labelBuildBlock(parentFrame, "Starship", 2, 0, 1, 'starshipTrait', 5+(1 if '-X' in self.backend['tier'].get() else 0), self.traitLabelCallback, [False, False, True, "space"])
        self.labelBuildBlock(parentFrame, "SpaceRep", 3, 0, 1, 'spaceRepTrait', 5, self.traitLabelCallback, [True, False, False, "space"])
        self.labelBuildBlock(parentFrame, "Active", 4, 0, 1, 'activeRepTrait', 5, self.traitLabelCallback, [True, True, False, "space"])

    def setupGroundTraitFrame(self):
        """Set up UI frame containing traits"""
        outerFrame = self.groundTraitFrame
        outerFrame.grid_rowconfigure(0, weight=1, uniform='shiptraitFrameFullRowSpace')
        outerFrame.grid_columnconfigure(0, weight=1, uniform='shiptraitFrameFullColSpace')
        self.clearFrame(outerFrame)

        parentFrame = Frame(outerFrame, bg=self.theme['frame']['bg'])
        parentFrame.grid(row=0, column=0, sticky='', padx=1, pady=1)

        traitEliteCaptain = 1 if self.build['eliteCaptain'] else 0
        traitAlien = 1 if 'Alien' in self.backend['species'].get() else 0
        self.labelBuildBlock(parentFrame, "Personal", 0, 0, 1, 'personalGroundTrait', 6 if traitEliteCaptain else 5, self.traitLabelCallback, [False, False, False, "ground"])
        self.labelBuildBlock(parentFrame, "Personal", 1, 0, 1, 'personalGroundTrait2', 5, self.traitLabelCallback, [False, False, False, "ground"], 1 if not traitAlien else 0)
        self.labelBuildBlock(parentFrame, "GroundRep", 3, 0, 1, 'groundRepTrait', 5, self.traitLabelCallback, [True, False, False, "ground"])
        self.labelBuildBlock(parentFrame, "Active", 4, 0, 1, 'groundActiveRepTrait', 5, self.traitLabelCallback, [True, True, False, "ground"])

    def resetShipSettings(self):
        # on ship change / removal
        # Clear specs so we don't gather specs as we change
        self.build['boffseats']['space_spec'] = [None] * 6
        self.shipImageResizeCount = 0

        if not self.persistent['keepTemplateOnShipChange']:
            self.build['playerShipName'] = ''
            self.copyBuildToBackend('playerShipName')
            self.build['playerShipDesc'] = ''
            self.resetBuildFrames(types=['space'])

    def sortedBoffs2(self, ranks, specs, spec2s, environment, i):
        if environment == 'space' and self.persistent['boffSort2'] == 'ranks':
            subSort = ranks[i]
        elif environment == 'space' and self.persistent['boffSort2'] == 'spec':
            subSort = specs[i]
        elif environment == 'space' and self.persistent['boffSort2'] == 'spec2':
            subSort = spec2s[i] if spec2s else 'z' #sort empties downwards
        else:
            subSort = i

        return subSort

    def sortedBoffs(self, ranks, specs, spec2s, environment):
        rangeRanks = range(len(ranks))
        if environment == 'space' and self.persistent['boffSort'] == 'ranks':
            sortedRange = sorted(rangeRanks, reverse=True, key=lambda i,ranks=ranks,specs=specs,spec2s=spec2s: ( ranks[i], self.sortedBoffs2(ranks, specs, spec2s, environment, i)))
        elif environment == 'space' and self.persistent['boffSort'] == 'spec':
            sortedRange = sorted(rangeRanks, reverse=True, key=lambda i,ranks=ranks,specs=specs,spec2s=spec2s: ( specs[i], self.sortedBoffs2(ranks, specs, spec2s, environment, i)))
        elif environment == 'space' and self.persistent['boffSort'] == 'spec2':
            sortedRange = sorted(rangeRanks, reverse=True, key=lambda i,ranks=ranks,specs=specs,spec2s=spec2s: ( 1 if len(spec2s[i]) else 0, self.sortedBoffs2(ranks, specs, spec2s, environment, i)))
        else:
            sortedRange = rangeRanks

        return sortedRange

    def setupBoffFrame(self, environment='space', ship=None):
        """Set up UI frame containing boff skills"""
        self.precacheReputations()
        if ship is None: ship = self.shipTemplate

        outerFrame = self.groundBoffFrame if environment == 'ground' else self.shipBoffFrame
        outerFrame.grid_rowconfigure(0, weight=1, uniform='shiptraitFrameFullRowSpace')
        outerFrame.grid_columnconfigure(0, weight=1, uniform='shiptraitFrameFullColSpace')
        self.clearFrame(outerFrame)

        parentFrame = Frame(outerFrame, bg=self.theme['frame']['bg'])
        parentFrame.grid(row=0, column=0, sticky='', padx=1, pady=1)

        seats = 6 if environment == 'space' else 4
        if not environment in self.build['boffseats']: self.build['boffseats'][environment] = [None] * seats
        if not environment+'_spec' in self.build['boffseats']: self.build['boffseats'][environment+'_spec'] = [None] * seats


        if environment == 'ground':
            boffs = ['Tactical'] * seats
            boffranks = [4] * seats
            boffsspecs = [''] * seats
            boffspecs = [''] * seats
        else:
            if ship is None or not 'boffs' in ship: return
            else: boffs = ship["boffs"]
            seats = len(boffs)
            boffranks = [4] * seats
            boffsspecs = [''] * seats
            boffspecs = [''] * seats
            for i in range(len(boffs)):
                boffranks[i] = 3 if "Lieutenant Commander" in boffs[i] else 2 if "Lieutenant" in boffs[i] else 4 if "Commander" in boffs[i] else 1
                for s in self.cache['specsPrimary']:
                    if '-'+s in boffs[i]:
                        boffsspecs[i] = s
                        break
                boffspecs[i] = self.boffTitleToSpec(boffs[i].replace('Lieutenant', '').replace('Commander', '').replace('Ensign', '').strip())

        for i in self.sortedBoffs(boffranks, boffspecs, boffsspecs, environment):
            boff = boffs[i]
            boffSan = environment+'Boff_' + str(i)

            if environment == 'ground':
                rank = seats
                spec = boff
                sspec = None
            else:
                rank = boffranks[i]
                spec = boffspecs[i]
                sspec = boffsspecs[i]

                if spec == 'Tactical' and rank == 3 and 'Science Destroyer' in self.build['ship']: #sci destroyers get tac mode turning lt cmdr to cmdr
                    rank = 4

            bFrame = Frame(parentFrame, width=120, height=80, bg=self.theme['frame']['bg'])
            bFrame.pack(fill=BOTH, expand=True)
            bSubFrame0 = Frame(bFrame, bg=self.theme['frame']['bg'])
            bSubFrame0.pack(fill=BOTH, pady=(2,0))

            self.backend['images'][boffSan] = [None] * rank

            if spec != 'Universal' and spec != self.build['boffseats'][environment][i]:
                #wipe skills of the changed spec here, keep the secondary spec
                #self.build['boffs'][boffSan] = [None] * rank
                pass

            if environment == 'space' and spec != 'Universal':
                self.build['boffseats'][environment][i] = spec
                self.build['boffseats'][environment+'_spec'][i] = sspec
            else:
                if self.build['boffseats'][environment][i] is None: self.build['boffseats'][environment][i] = 'Science'
                if self.build['boffseats'][environment+"_spec"][i] is None: self.build['boffseats'][environment+"_spec"][i] = sspec

            v = StringVar(self.window, value=self.build['boffseats'][environment][i])
            v2 = StringVar(self.window, value=self.build['boffseats'][environment+'_spec'][i])
            v.trace_add("write", lambda v,i,m,v0=v,idx=i:self.boffUniversalCallback(v0, idx, environment))
            v2.trace_add("write", lambda v2,i,m,v0=v2,idx=i:self.boffUniversalCallback(v0, idx, environment+'_spec'))

            if environment == 'space' and spec != 'Universal':
                specLabel0 = Label(bSubFrame0, text=spec)
            else:
                specLabel0 = OptionMenu(bSubFrame0, v, 'Tactical', 'Engineering', 'Science')
                specLabel0.configure(pady=2)
            specLabel0.configure(bg=self.theme['entry_dark']['bg'], fg=self.theme['entry_dark']['fg'], highlightthickness=0)
            specLabel0.pack(side='left')

            if environment == 'ground' or (sspec is not None and sspec != ''):
                if environment == 'ground':
                    specLabel1 = OptionMenu(bSubFrame0, v2, *['']+sorted(self.cache['specsGroundBoff']))
                    specLabel1.configure(pady=2)
                else:
                    specLabel1 = Label(bSubFrame0, text='/  '+sspec)
                specLabel1.configure(bg=self.theme['entry_dark']['bg'], fg=self.theme['entry_dark']['fg'], highlightthickness=0)
                specLabel1.pack(side='left')

            bSubFrame1 = Frame(bFrame, bg=self.theme['frame']['bg'])
            bSubFrame1.pack(fill=BOTH)

            if boffSan in self.build['boffs']:
                boffExistingLen = len(self.build['boffs'][boffSan])
                changeCount = rank - boffExistingLen
                if boffExistingLen < rank:
                    for add in range(changeCount):
                        self.build['boffs'][boffSan].append([None])
                elif boffExistingLen > rank:
                    self.build['boffs'][boffSan] = self.build['boffs'][boffSan][slice(rank)]

                if rank != len(self.build['boffs'][boffSan]):
                    self.logWrite('--- {} {}{}{}->{}{}{}'.format('boff seat change error: ', boffExistingLen, '+' if changeCount > 0 else '', changeCount, rank, '!=' , str(len(self.build['boffs'][boffSan]))), 1)

            for j in range(rank):
                tooltip_uuid = self.uuid_assign_for_tooltip()
                if boffSan in self.build['boffs'] and self.build['boffs'][boffSan][j] is not None:
                    image=self.imageFromInfoboxName(self.build['boffs'][boffSan][j], faction = 1)
                    self.backend['images'][boffSan][j] = image
                else:
                    image=self.emptyImage
                    self.build['boffs'][boffSan] = [None] * rank

                args = [v, v2, i, environment]
                canvas, img0, img1 = self.createButton(bSubFrame1, key=boffSan, row=1, column=j, groupKey='boffs', i=j, callback=self.boffLabelCallback, args=args, faction=True, suffix=False, image0=self.backend['images'][boffSan][j])

    def setupSpaceBuildFrames(self):
        """Set up all relevant space build frames"""
        self.build['tier'] = self.backend['tier'].get()
        if self.backend['shipHtml'] is not None or self.persistent['keepTemplateOnShipClear']:
            self.setupDoffFrame(self.shipDoffFrame)
            self.setupShipGearFrame(self.backend['shipHtml'])
            self.setupBoffFrame('space', self.backend['shipHtml'])
            self.setupSpaceTraitFrame()
        else:
            try:
                for fr in [self.shipEquipmentFrame, self.shipConsoleFrame, self.shipBoffFrame, self.shipTierFrame, self.shipDoffFrame, self.shipTraitFrame]:
                    self.clearFrame(fr)
            except AttributeError:
                pass

        self.clearInfoboxFrame('space')
        self.requestWindowUpdate('force')

    def setupGroundBuildFrames(self):
        """Set up all relevant build frames"""
        self.build['tier'] = self.backend['tier'].get()
        self.setupDoffFrame(self.groundDoffFrame)
        self.setupGroundGearFrame()
        self.setupBoffFrame('ground')
        self.setupGroundTraitFrame()
        self.clearInfoboxFrame('ground')

    def setupModFrame(self, frame, rarity, itemVar):
        """Set up modifier frame in equipment picker"""
        self.precacheModifiers()
        self.clearFrame(frame)
        n = self.rarities.index(rarity)
        itemVar['rarity'] = rarity
        if not len(itemVar['modifiers']) == n:
            itemVar['modifiers'] = ['']*n

        mods = sorted(self.cache['modifiers'])
        for i in range(n):
            v = StringVar()
            if i < len(itemVar['modifiers']):
                v.set(itemVar['modifiers'][i])
            v.trace_add('write', lambda v0,v1,v2,i=i,itemVar=itemVar,v=v:self.setListIndex(itemVar['modifiers'],i,v.get()))
            OptionMenu(frame, v, *mods).grid(row=0, column=i, sticky='new')
            frame.grid_columnconfigure(i, weight=1, uniform='setupModFrame')

    def getURL(self, name):
        return self.wikihttp + name

    def clearInfoboxFrame(self, environment):
        """Empty the tooltip"""
        self.setupInfoboxFrameTooltipDraw(None, self.getEmptyItem(), '', environment)

    def setupInfoboxFrameTooltipDraw(self, ui_key, item, key, environment='space', tooltip=None):
        """Tooltip mouse-enter -- initiate the delayed call"""
        self.logWriteSimple('Tooltip', 'enter', 4, [ui_key, item, key, environment, tooltip])
        if ui_key:
            self.tooltip_tracking[ui_key] = True
            #self.setupInfoboxFrameMaster(ui_key, item, key, environment, tooltip)
            self.window.after(self.persistent['tooltipDelay'], lambda item=item, key=key, environment=environment, tooltip=tooltip: self.setupInfoboxFrameMaster(ui_key, item, key, environment, tooltip))
        else:
            # No ui_key is instant tooltip update
            self.setupInfoboxFrameMaster(None, item, key, environment, tooltip)

    def setupInfoboxFrameMaster(self, ui_key, item, key, environment, tooltip):
        """Actually draw the tooltip if ui_key is None or still true"""
        if ('X' in self.tooltip_tracking and self.tooltip_tracking['X']) or\
                ('hold' in self.tooltip_tracking and self.tooltip_tracking['hold']):
            self.logWriteSimple('tooltip', 'IGNORED', 3)
            # Would it be good to re-initiate a .after call?
            return
        if ui_key is None or (ui_key in self.tooltip_tracking and self.tooltip_tracking[ui_key]):
            self.tooltip_tracking[ui_key] = False
            self.tooltip_tracking['hold'] = True
            if not self.persistent['useAlternateTooltip']:
                self.setupInfoboxFrame(item, key, environment, tooltip)
            else:
                self.setupInfoboxFrameStatic(item, key, environment, tooltip)
            self.tooltip_tracking['hold'] = False

    def setupInfoboxFrameLeave(self, ui_key):
        """Tooltip mouse-exit -- deactivate any pending tooltip"""
        #self.logWriteSimple('Tooltip', 'exit', 2, [ui_key])
        self.tooltip_tracking[ui_key] = False

    def getDisplayedTextHeight(self, width, pString: str, pfamily, psize, pweight, identifier=""):
        """{ Call as self.getDH(Parameters) }
        Returns the height that the text inside the Widget occupies. Value is given in lines (This number may be higher than the actual number of lines to compensate
        for different heights of different fonts), returns -1 if text is empty; Parameters: width: Width of the text widget; pString: Text to be measured; pfamily: Font Family of the inserted text; psize: Font size of the
        inserted Text; pweight: Font weight of the inserted text; identifier: identifier to adjust height for special cases [may be left empty]"""
        if pString != "" and pString is not None:
            lines = 1
            lin = pString.split("\n")
            while lin[-1] == "" or lin[-1] is None: del lin[-1]
            for i in range(0, len(lin)):
                if not lin[i] == "":
                    words = lin[i].split(" ")
                    while words[-1] =="": del words[-1]
                    while " " in words: words.remove(" ")
                    while ""  in words: words.remove("")
                    currentlength = 0.0
                    for content in words:
                        currentlength = currentlength + font.Font(family=pfamily, size=psize, weight=pweight).measure(content)
                        if currentlength > width:
                            lines = lines+1
                            currentlength = font.Font(family=pfamily, size=psize, weight=pweight).measure(content)
                        if currentlength + font.Font(family=pfamily, size=psize, weight=pweight).measure(" ") >= width:
                            lines = lines+1
                            currentlength=0
                        else:
                            currentlength = currentlength + font.Font(family=pfamily, size=psize, weight=pweight).measure(" ")
                lines = lines+1
            lines = lines-1
            hgt=1
            if identifier == "equipmenthead":                                             #This structure compensates for the different height of different text size
                if lines==1:                                                              #If a text format has no respective if statement, the functions returns 1. For Equipment field "Head" there is no if statement, because I never saw more than 1 line
                    hgt=2.5
                elif lines==2:
                    hgt=3.5
                elif lines ==3:
                    hgt=5.5
                else:
                    hgt=lines+2.5
            elif identifier == "traithead":
                if lines == 3:
                    hgt = 3.5
                elif lines == 4:
                    hgt = 5
                else:
                    hgt = lines
            elif identifier == "personaltrait":
                hgt = lines+1
            elif identifier == "boff":
                hgt = lines+1
            elif identifier == "skill":
                if lines == 1:
                    hgt = 3.5
                elif lines == 2:
                    hgt = 5.5
            elif identifier == "":
                hgt=lines
            return hgt
        else:
            return -1


    getDH = getDisplayedTextHeight

    def compensateInfoboxString(self, text):
        text = self.deWikify(text, leaveHTML=True)
        text = text.replace("<p>","")
        text = text.replace('<br>\n', '\n')
        text = text.replace('<br/>\n', '\n')
        text = text.replace('<br />\n', '\n')
        text = text.replace('<br>', '\n')
        text = text.replace('<br/>', '\n')
        text = text.replace('<br />', '\n')
        text = text.replace('<hr/>', "\n––––––––––––––––––––––––––––––\n")
        text = text.replace('<hr>', "\n––––––––––––––––––––––––––––––\n")
        text = text.replace('<hr />', "\n––––––––––––––––––––––––––––––\n")
        text = text.replace('<li> ', '\n*')
        text = text.replace(' <li>', '\n*')
        text = text.replace('<li>', '\n*')
        text = text.replace(" *", "*")
        text = text.replace("<small>", "")
        text = text.replace("</small>", "")
        text = text.replace("<sub>", "")
        text = text.replace("</sub>", "")
        text = text.replace("<sup>", "")
        text = text.replace("</sup>", "")
        color = list()
        t=text
        while '<font color=' in t:
            if len(color) > 0:
                color.append(text.find('<font color=', color[-1]+7))
                color.append(text.find("</font>", color[-1]))
            else:
                color.append(text.find("<font color="))
                color.append(text.find("</font>"))
            t = t[color[-1]:]
        while len(color)>0:
            try: 
                text = text[:color[-1]]+text[color[-1]+7:]
            except IndexError:
                text = text[:color[-1]]
            try:
                text = text[:color[-2]]+text[text.find(">", color[-2])+1:]
            except IndexError:
                text = text[:color[-2]]
            try:
                del color[-1]
                del color[-1]
            except IndexError:
                pass

        return text

    def formattedInsert(self, ptext: str, pfamily, psize, pweight):
        if not "''" in ptext and not "<" in ptext:
            self.insert(END, ptext)
            return

        def subtr(li: list, index):
            try:
                del li[0]
                del li[0]
            except:
                return list()
            for element in range(0, len(li)):
                li[element] = li[element]-index
            return li

        t = ptext
        bolditalic = list()
        while "'''''" in t:
            if len(bolditalic) > 0:
                bolditalic.append(ptext.find("'''''", bolditalic[-1]+5))
            else:
                bolditalic.append(ptext.find("'''''"))
            t = ptext[bolditalic[-1]+5:]
        t = ptext.replace("'''''", "|||||")
        bold = list()
        while "'''" in t:
            if len(bold) > 0:
                bold.append(ptext.replace("'''''", "|||||").find("'''", bold[-1]+3))
            else:
                bold.append(ptext.replace("'''''", "|||||").find("'''"))
            t = ptext[bold[-1]+3:].replace("'''''","|||||")
        t = ptext.replace("'''''", "|||||").replace("'''","|||")
        italic = list()
        while "''" in t:
            if len(italic) > 0:
                italic.append(ptext.replace("'''''", "|||||").replace("'''", "|||").find("''", italic[-1]+2))
            else:
                italic.append(ptext.replace("'''''", "|||||").replace("'''", "|||").find("''"))
            t = ptext[italic[-1]+2:].replace("'''''","|||||").replace("'''","|||")
        bold2 = list()
        t = ptext
        while "<b>" in t:
            if len(bold2) > 0:
                bold2.append(ptext.find("<b>", bold2[-1]+4))
                bold2.append(ptext.find("</b>", bold2[-1]))
            else:
                bold2.append(ptext.find("<b>"))
                bold2.append(ptext.find("</b>"))
            t = ptext[bold2[-1]+4:]
        underlined = list()
        t = ptext
        while "<u>" in t:
            if len(underlined) > 0:
                underlined.append(ptext.find("<u>", underlined[-1]+4))
                underlined.append(ptext.find("</u>", underlined[-1]))
            else:
                underlined.append(ptext.find("<u>"))
                underlined.append(ptext.find("</u>"))
            t = ptext[underlined[-1]+4:]
        l = bolditalic + bold + italic + bold2 + underlined 
        l.sort()
        self.tag_configure('bolditalic', font=(pfamily, psize, "bold", "italic"))
        self.tag_configure('bold', font=(pfamily, psize, "bold"))
        self.tag_configure('italic', font=(pfamily, psize, pweight, "italic"))
        self.tag_configure('underlined', underline=True, font=(pfamily, psize, pweight))
        if len(l) > 0:
            passtext = ptext
            while len(l)>0:
                i1 = l[0]
                i2: int
                if len(bolditalic) > 0 and i1 == bolditalic[0]:
                    i2 = bolditalic[1]
                    self.insert(END, passtext[:i1])
                    self.insert(END, passtext[i1+5:i2], "bolditalic")
                    passtext = passtext[i2+5:]
                    l = subtr(l, i2+5)
                    bolditalic = subtr(bolditalic, i2+5)
                    bold = subtr(bold, i2+5)
                    italic = subtr(italic, i2+5)
                    bold2 = subtr(bold2, i2+5)
                    underlined = subtr(underlined, i2+5)
                elif len(bold) > 0 and i1 == bold[0]:
                    i2 = bold[1]
                    self.insert(END, passtext[:i1])
                    self.insert(END, passtext[i1+3:i2], "bold")
                    passtext = passtext[i2+3:]
                    l = subtr(l, i2+3)
                    bolditalic = subtr(bolditalic, i2+3)
                    bold = subtr(bold, i2+3)
                    italic = subtr(italic, i2+3)
                    bold2 = subtr(bold2, i2+3)
                    underlined = subtr(underlined, i2+3)
                elif len(italic) > 0 and i1 == italic[0] :
                    i2 = italic[1]
                    self.insert(END, passtext[:i1])
                    self.insert(END, passtext[i1+2:i2], "italic")
                    passtext = passtext[i2+2:]
                    l = subtr(l, i2+2)
                    bolditalic = subtr(bolditalic, i2+2)
                    bold = subtr(bold, i2+2)
                    italic = subtr(italic, i2+2)
                    bold2 = subtr(bold2, i2+2)
                    underlined = subtr(underlined, i2+2)
                elif len(bold2) > 0 and i1 == bold2[0]:
                    i2 = bold2[1]
                    self.insert(END, passtext[:i1])
                    self.insert(END, passtext[i1+3:i2], "bold")
                    passtext = passtext[i2+4:]
                    l = subtr(l, i2+4)
                    bolditalic = subtr(bolditalic, i2+4)
                    bold = subtr(bold, i2+4)
                    italic = subtr(italic, i2+4)
                    bold2 = subtr(bold2, i2+4)
                    underlined = subtr(underlined, i2+4)
                elif len(underlined) > 0 and i1 == underlined[0] :
                    i2 = underlined[1]
                    self.insert(END, passtext[:i1])
                    self.insert(END, passtext[i1+3:i2], "underlined")
                    passtext = passtext[i2+4:]
                    l = subtr(l, i2+4)
                    bolditalic = subtr(bolditalic, i2+4)
                    bold = subtr(bold, i2+4)
                    italic = subtr(italic, i2+4)
                    bold2 = subtr(bold2, i2+4)
                    underlined = subtr(underlined, i2+4)
            self.insert(END, passtext)
        else:
            self.insert(END, ptext)
            
    
    tkinter.Text.formattedInsert = formattedInsert

    def insertInfoboxParagraph(self, inframe: Frame, ptext: str, pfamily, pcolor, psize, pweight, gridrow, framewidth):
        """Inserts Infobox paragraph into a frame"""
        mainframe = Frame(inframe, bg=self.theme['tooltip']['bg'], highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'])
        mainframe.grid(row=gridrow,column=0, sticky="nsew")
        inframe.rowconfigure(gridrow, weight=0)
        inframe.rowconfigure(gridrow+1, weight=1)
        inframe.columnconfigure(0, weight=1)
        inframe.columnconfigure(1, weight=1)
        ptext = ptext.strip()
        if ("\n:" in ptext or ptext.startswith(":")) and not ptext.startswith("*") and not ptext.startswith("<ul>"):
            inserttext1 = ""
            inserttext2 = ""
            passtext = ""
            occs = [i.start() for i in re.finditer('\n:', ptext)]
            if ptext.startswith(":"):
                end=0
                if occs == []:
                    end = -2
                elif "\n" in ptext[:occs[0]-1]:
                    end = ptext.find("\n")
                else:
                    if len(occs)==1:
                        if "\n" in ptext[:occs[0]]:
                            end=ptext.find("\n")
                    else:
                        for j in range(0, len(occs)-1):
                            if "\n" in ptext[occs[j]+1:occs[j+1]].replace("\n:",""):
                                end = ptext.find("\n", occs[j]+1,occs[j+1])
                                break
                    if end==0:
                        if "\n" in ptext.replace("\n:","").strip():
                            end = ptext.find("\n", occs[len(occs)-1]+1 if occs != [] else 0)
                        else:
                            end=-2
                if end == -2:

                    passtext = ptext[1:].replace("\n:", "\n")
                else:
                    passtext = ptext[1:end].replace("\n:","\n")
                    inserttext2 = ptext[end+1:]
            else:
                start = occs[0]
                end = 0
                for k in range(0, len(occs)-1):
                    if "\n" in ptext[occs[k]+1:occs[k+1]]:
                        end = ptext.find("\n", occs[k]+1, occs[k+1])
                        break
                if end == 0:
                    if "\n" in ptext[occs[len(occs)-1]+1:]:
                        end = ptext.find("\n", occs[len(occs)-1]+1)
                    else:
                        end=-2
                inserttext1 = ptext[:start]
                if end == -2:
                    passtext = ptext[start+2:].replace("\n:", "\n")
                else:
                    passtext = ptext[start+2:end].replace("\n:", "\n")
                    inserttext2 = ptext[end+1:]
        elif ("<ul>" in ptext or ptext.startswith("<ul>")) and not ptext.startswith("*"):
            inserttext1 = ""
            inserttext2 = ""
            passtext = ""
            occs = [i.start() for i in re.finditer('<ul>', ptext)]
            occs2 = [i.start() for i in re.finditer('</ul>', ptext)]
            if ptext.startswith("<ul>"):
                end = 0
                if len(occs)>1:
                    if len(occs2)==0:
                        end = -2
                    elif occs[0]<occs2[0] and occs2[0]<occs[1]:
                        end = ptext.find("</ul>")
                    else:
                        c = int(0)
                        while occs[c]<occs2[0]:
                            if (c+1)<len(occs): c = c+1
                            else: break
                        try:
                            end = occs[c]
                        except IndexError:
                            end = -2
                else:
                    if "</ul>" in ptext: end = ptext.find("</ul>")
                    else: end = -2
                if end != -2:
                    passtext = ptext[:end]
                    inserttext2 = ptext[end+5:]
                else: passtext=ptext[4:]
            else:
                start = occs[0]
                end = 0
                inserttext1 = ptext[:start]
                if len(occs)>1:
                    if len(occs2) == 0:
                        end=-2
                    elif occs[0]<occs2[0] and occs2[0]<occs[1]:
                        end = ptext.find("</ul>")
                    else:
                        c = int(0)
                        while occs[c]<occs2[0]:
                            if (c+1)<len(occs): c = c+1
                            else: break
                        try:
                            end = occs[c]
                        except IndexError:
                            end = -2
                else:
                    if "</ul>" in ptext: end = ptext.find("</ul>")
                    else: end = -2
                if end != -2:
                    passtext = ptext[start+4:end]
                    inserttext2 = ptext[end+5:]
                else: passtext=ptext[start:]
        elif "\n*" in ptext or ptext.startswith("*"):
            inserttext1 = ""
            inserttext2 = ""
            passtext = ""
            occs = [i.start() for i in re.finditer('\n\*', ptext)]
            if ptext.startswith("*"):
                end=0
                if occs == []:
                    end = len(ptext)-1
                elif "\n" in ptext[:occs[0]-1] :
                    end = ptext.find("\n")
                else:
                    if len(occs)==1:
                        if "\n" in ptext[:occs[0]]:
                            end=ptext.find("\n")
                    else:
                        for j in range(0, len(occs)-1):
                            if "\n" in ptext[occs[j]+1:occs[j+1]].replace("\n*",""):
                                end = ptext.find("\n", occs[j]+1, occs[j+1])
                                break
                    if end==0:
                        if "\n" in ptext.replace("\n*",""):
                            end = ptext.find("\n", occs[len(occs)-1]+1 if occs != [] else 0)
                        else:
                            end=-2
                if end == -2:
                    passtext = ptext.replace("\n*", "\n• ").replace("*","• ")
                else:
                    passtext = ptext[0:end+1].replace("\n*","\n• ").replace("*","• ")
                    inserttext2 = ptext[end+1:]
            else:
                start = occs[0]
                end = 0
                for k in range(0, len(occs)-1):
                    if "\n" in ptext[occs[k]+1:occs[k+1]]:
                        end = ptext.find("\n", occs[k]+1)
                        break
                if end == 0:
                    if "\n" in ptext[occs[len(occs)-1]+2:]:
                        end = ptext.find("\n", occs[len(occs)-1]+2)
                    else:
                        end=-2
                inserttext1 = ptext[:start]
                if end == -2:
                    passtext = ptext[start+1:].replace("\n*", "\n• ").replace("*","• ")
                else:
                    passtext = ptext[start+1:end].replace("\n*", "\n• ").replace("*","• ")
                    inserttext2 = ptext[end+1:]
        elif (not ("\n:" or "*" or "<ul>" or "<li>") in ptext) and not ptext.startswith(":"):
            inserttext1 = ptext
            inserttext2 = ""
            passtext = ""
        rowinsert=0
        if not inserttext1 == "":
            maintext = Text(mainframe, bg=self.theme['tooltip']['bg'], fg=pcolor, wrap=WORD, highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'], relief=self.theme['tooltip']['relief'], font=(pfamily, psize, pweight), height=self.getDH(framewidth, inserttext1, pfamily, psize, pweight))
            maintext.grid(row=rowinsert,column=0)
            mainframe.rowconfigure(rowinsert, weight=0)
            mainframe.rowconfigure(rowinsert+1, weight=0)
            inframe.update()
            mainframe.columnconfigure(0, weight=1)
            mainframe.columnconfigure(1, weight=1)
            maintext.formattedInsert(inserttext1, pfamily, psize, pweight)
            maintext.configure(state=DISABLED)
            rowinsert = rowinsert+1
        if not passtext == "":
            lineframe = Frame(mainframe, bg=self.theme['tooltip']['bg'], highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'])
            lineframe.grid(row=rowinsert, column=0, sticky="nsew")
            mainframe.rowconfigure(rowinsert, weight=0)
            mainframe.rowconfigure(rowinsert+1, weight=0)
            mainframe.columnconfigure(0, weight=1)
            mainframe.columnconfigure(1, weight=1)
            lineframe.rowconfigure(0, weight=0)
            lineframe.columnconfigure(0, weight=1, minsize=12)
            lineframe.columnconfigure(1, weight=7)
            lineframe.columnconfigure(2, weight=1)
            daughterframe = Frame(lineframe, bg=self.theme['tooltip']['bg'], highlightcolor=self.theme['tooltip']['highlight'], highlightthickness=0)
            daughterframe.grid(row=0, column=1, sticky="nsew")
            self.insertInfoboxParagraph(daughterframe, passtext, pfamily, pcolor, psize, pweight, 0, framewidth-12)
            rowinsert = rowinsert + 1
        if not inserttext2 == "":
            lineframe = Frame(mainframe, bg=self.theme['tooltip']['bg'], highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'])
            lineframe.grid(row=rowinsert, column=0, sticky="nsew")
            mainframe.rowconfigure(rowinsert, weight=0)
            mainframe.rowconfigure(rowinsert+1, weight=0)
            mainframe.columnconfigure(0, weight=1)
            mainframe.columnconfigure(1, weight=1)
            self.insertInfoboxParagraph(lineframe, inserttext2, pfamily, pcolor, psize, pweight, 0, framewidth)



    def setupInfoboxFrame(self, item, key, environment='space', tooltip=None): #qwer <- thats for me to get here quickly lol
        """Set up infobox frame with given item"""
        if item is not None and 'item' in item:
            name = item['item']
        elif isinstance(item, str):
            name = item
        else:
            self.logWriteSimple('InfoboxEmpty', environment, 3, tags=["NO NAME", key])
            return
        self.logWriteSimple('Infobox', environment, 4, tags=[name, key, item])
        if name != '' and self.displayedInfoboxItem == name:
            self.logWriteSimple('Infobox', 'displayed', 2, [environment])
            return
        self.displayedInfoboxItem = name

        if environment == 'skill':
            frame = self.skillInfoboxFrame
        elif environment == 'ground':
            frame = self.groundInfoboxFrame
        else:
            frame = self.shipInfoboxFrame
        frame.configure(highlightthickness=0)
        frame.pack_propagate(False)
        if environment != 'skill' and key is not None and key != '':
            self.precacheEquipment(key)

        raritycolor = '#ffffff'
        if 'rarity' in item:
            if item["rarity"].lower() == "epic":
                raritycolor = '#ffd700'
            elif item["rarity"].lower() == "ultra rare":
                raritycolor = "#6d65bc"
            elif item["rarity"].lower() == "very rare":
                raritycolor = "#a245b9"
            elif item["rarity"].lower() == "rare":
                raritycolor = "#0099ff"
            elif item["rarity"].lower() == "uncommon":
                raritycolor = "#00cc00"

        self.clearFrame(frame)

        mainbutton = HoverButton(frame, text="Stats & Other Info", highlightbackground=self.theme['tooltip']['bg'],  highlightthickness=1, activebackground=self.theme['button_heavy']['hover'])
        mainbutton.pack(fill=X, expand=False, side=TOP)
        mtfr = Frame(frame, bg=self.theme['tooltip']['bg'], highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'])
        mtfr.pack(fill="both",expand=False,side=TOP)
        text = Text(mtfr, bg=self.theme['tooltip']['bg'], fg=self.theme['tooltip']['fg'], wrap=WORD, highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'], relief=self.theme['tooltip']['relief'], height=3.5)

        skillcolor_by_career = {'tac': '#c83924', 'eng': '#c59129', 'sci': '#1265a3'}
        skillcolor = "pink"
        if environment == 'skill' and isinstance(key, tuple):
            (skill_rank, skill_row, skillindex) = key
            skill_environment = 'ground' if skill_rank is None else 'space'
            skill_career = self.skillGetFieldSkill(skill_environment, key, 'career')
            skillcolor = skillcolor_by_career[skill_career] if skill_career in skillcolor_by_career else self.theme['tooltip']['subhead']['fg']

        text.tag_configure('head', foreground=self.theme['tooltip']['head']['fg'], font=self.font_tuple_create('tooltip_head'))
        text.tag_configure('name', foreground=raritycolor, font=self.font_tuple_create('tooltip_name'))
        text.tag_configure('rarity', foreground=raritycolor, font=self.font_tuple_create('tooltip_body'))
        text.tag_configure('subhead', foreground=self.theme['tooltip']['subhead']['fg'], font=self.font_tuple_create('tooltip_subhead'))
        text.tag_configure('starshipTraitHead', foreground=self.theme['tooltip']['head1']['fg'], font=self.font_tuple_create('tooltip_head'))
        text.tag_configure('skillhead', foreground=skillcolor, font=self.font_tuple_create('tooltip_name'))
        text.tag_configure('skillsub', foreground=skillcolor, font=self.font_tuple_create('tooltip_head'))


        text.grid(row=0, column=0)
        mtfr.rowconfigure(0, weight=0)
        mtfr.rowconfigure(2, weight=0, minsize=8)
        mtfr.rowconfigure(1, weight=0)
        mtfr.rowconfigure(3, weight=1)
        mtfr.columnconfigure(0, weight=1)
        mtfr.columnconfigure(1, weight=1)

        printed = bool(False)
        if name == '':
                return

        if key in self.cache['equipment'] and name in self.cache['equipment'][key]:
            text.insert(END, name, 'name')
            mkt = False
            modt = False
            if 'mark' in item and item['mark']:
                text.insert(END, ' '+item['mark'], 'name')
                mkt = True
            if 'modifiers' in item and item['modifiers']:
                text.insert(END, ' '+('' if item['modifiers'][0] is None else ' '.join(item['modifiers'])), 'name')
                modt = True
            text.update()
            if mkt and not modt:
                lines = self.getDH(text.winfo_width(), name+' '+item['mark'], "Helvetica", 15, "bold", "equipmenthead")
            elif not mkt and modt:
                lines = self.getDH(text.winfo_width(), name+' '+('' if item['modifiers'][0] is None else ' '.join(item['modifiers'])), "Helvetica", 15, "bold", "equipmenthead")
            elif mkt and modt:
                lines = self.getDH(text.winfo_width(), name+' '+item['mark']+' '+('' if item['modifiers'][0] is None else ' '.join(item['modifiers'])), "Helvetica", 15, "bold", "equipmenthead")
            elif not mkt and not modt:
                lines = self.getDH(text.winfo_width(), name, "Helvetica", 15, "bold")
            text.configure(height=lines)
            html = self.cache['equipment'][key][name]
            if 'rarity' in item and item['rarity']:
                text.insert(END, '\n'+item['rarity']+' ', 'rarity')
                if 'type' in html and html['type']:
                    text.insert(END, html['type'], 'rarity')
            if html['who'] != "":
                mtfr.update()
                whotext = Text(mtfr, bg=self.theme['tooltip']['bg'], fg=self.theme['tooltip']['who']['fg'], wrap=WORD, highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'], relief=self.theme['tooltip']['relief'], height=self.getDH(mtfr.winfo_width(), html['who'], "Helvetica", 10, "normal"))
                whotext.grid(row=1, column=0)
                whotext.insert(END, html["who"])
                whotext.configure(state=DISABLED)
            Frame(mtfr, background=self.theme['tooltip']['bg'], highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight']).grid(row=2,column=0,sticky="nsew")
            contentframe = Frame(mtfr, bg=self.theme['tooltip']['bg'], highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'])
            contentframe.grid(row=3, column=0, sticky="nsew")
            contentframe.grid_propagate(False)
            insertinrow = 0
            for i in range(1,9):
                t = html["head"+str(i)].strip()
                if t.strip() != "":
                    self.insertInfoboxParagraph(contentframe, self.compensateInfoboxString(t.strip()), "Helvetica", "#42afca", 12, "bold", insertinrow, text.winfo_width())
                    insertinrow = insertinrow+1
                t = html["subhead"+str(i)].strip()
                if t.strip() != "":
                    self.insertInfoboxParagraph(contentframe, self.compensateInfoboxString(t.strip()), "Helvetica", "#f4f400", 10, "bold", insertinrow, text.winfo_width())
                    insertinrow = insertinrow+1
                t = html["text"+str(i)].strip()
                if t.strip() != "":
                    self.insertInfoboxParagraph(contentframe, self.compensateInfoboxString(t.strip()), "Helvetica", "#ffffff", 10, "normal", insertinrow, text.winfo_width())
                    insertinrow = insertinrow+1
            mainbutton.configure(command=lambda p = html['Page']: self.openWikiPage(p))
            contentframe.grid_propagate(True)
            printed = True

        if (name in self.cache['shipTraits'])and not printed:
            text.insert(END, name+"\n", 'starshipTraitHead')
            text.insert(END, "Starship Trait\n", 'head')
            if self.cache['shipTraitsFull'][name]["obtained"] == "T5" or self.cache['shipTraitsFull'][name]["obtained"] == "T6":
                obtaintext = "This Starship Trait can be obtained from the "+self.cache['shipTraitsFull'][name]["obtained"]+" Mastery of the "+self.cache['shipTraitsFull'][name]["ship"] 
            elif self.cache['shipTraitsFull'][name]["obtained"] == "spec":
                obtaintext = "This Starship Trait can be obtained from the Captain Specialization system by completing the "+self.cache['shipTraitsFull'][name]["ship"]+" specialization."
            elif self.cache['shipTraitsFull'][name]["obtained"] == "recr":
                obtaintext = 'This Starship Trait can be obtained from a "'+self.cache['shipTraitsFull'][name]["ship"]+'" character.'
            else:
                obtaintext = "This Starship Trait is obtained from a reward pack."
            text.insert(END, obtaintext, "subhead")
            text.update()
            text.configure(height=self.getDH(text.winfo_width(), name+"\n"+"StarshipTrait\n"+obtaintext, "Helvetica", 15, "bold", "traithead"))
            Frame(mtfr, background=self.theme['tooltip']['bg'], highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight']).grid(row=2,column=0,sticky="nsew")
            contentframe = Frame(mtfr, bg=self.theme['tooltip']['bg'], highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'])
            contentframe.grid(row=3, column=0, sticky="nsew")
            contentframe.grid_propagate(False)
            self.insertInfoboxParagraph(contentframe, self.compensateInfoboxString(self.cache['shipTraits'][name].strip()), "Helvetiva", "#ffffff", 10, "normal", 0, text.winfo_width())
            contentframe.grid_propagate(True)
            mainbutton.configure(command=lambda url = self.cache['shipTraitsFull'][name]['link']: self.openURL(url))
            printed = True

        if (environment in self.cache['traits'] and name in self.cache['traits'][environment]) and not printed:
            text.insert(END, name+"\n", 'starshipTraitHead')
            text.update()
            text.configure(height=self.getDH(text.winfo_width(), name, "Helvetica", 15, "bold", "personaltrait"))
            contentframe = Frame(mtfr, bg=self.theme['tooltip']['bg'], highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'])
            contentframe.grid(row=2, column=0, sticky="nsew")
            contentframe.grid_propagate(False)
            self.insertInfoboxParagraph(contentframe, self.compensateInfoboxString(self.cache['traits'][environment][name].strip()), "Helvetiva", "#ffffff", 10, "normal", 0, text.winfo_width())
            contentframe.grid_propagate(True)
            mainbutton.configure(command=lambda p = "Trait: "+ name: self.openWikiPage(p))
            printed = True

        if (environment in self.cache['boffTooltips'] and name in self.cache['boffTooltips'][environment]) and not printed:
            text.insert(END, name, 'starshipTraitHead')
            text.update()
            text.configure(height=self.getDH(text.winfo_width(), name, "Helvetica", 15, "bold", "boff"))
            contentframe = Frame(mtfr, bg=self.theme['tooltip']['bg'], highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'])
            contentframe.grid(row=2, column=0, sticky="nsew")
            contentframe.grid_propagate(False)
            self.insertInfoboxParagraph(contentframe, self.compensateInfoboxString(self.cache['boffTooltips'][environment][name].strip()), "Helvetiva", "#ffffff", 10, "normal", 0, text.winfo_width())
            contentframe.grid_propagate(True)
            mainbutton.configure(command=lambda p = "Ability: "+ name: self.openWikiPage(p))
            printed = True

        if environment == "skill" and isinstance(key, tuple):
            skillcareer_by_career = {'tac': 'Tactical', 'eng': 'Engineering', 'sci': 'Science'}

            skillprofession = skillcareer_by_career[skill_career]+' ' if skill_career in skillcareer_by_career else ''
            skill_linear = self.skillGetFieldSkill(skill_environment, key, 'linear')
            skill_skill = self.skillGetFieldSkill(skill_environment, key, 'skill')
            skill_gdesc = self.skillGetFieldSkill(skill_environment, key, 'gdesc')
            skill_desc = self.skillGetFieldNode(skill_environment, key, 'desc')
            skill_link = self.skillGetFieldSkill(skill_environment, key, 'link')

            if not skill_linear:
                skill_linear = 0
            if not skill_skill:
                skill_skill = name
            skill_name_last_word = name.split()[-1]
            if skill_name_last_word == '3':
                skill_level = 'Advanced '
            elif skill_name_last_word == '2':
                skill_level = 'Improved '
            else:
                skill_level = ''

            if skill_linear > 0:
                skill_gdesc = skill_gdesc[skillindex] if len(skill_gdesc) >= skillindex else ''
                skill_skill = skill_skill[skillindex] if len(skill_skill) >= skillindex else ''
                skill_link = skill_link[skillindex] if len(skill_link) >= skillindex else ''

            text.insert(END, skill_level+skill_skill, 'skillhead')

            text.insert(END, '\n'+skillprofession+skill_environment.title()+' Skill\n'+name.title(), 'skillsub')
            text.update()
            if self.build['skilltree'][skill_environment][name]:
                text.insert(END, "\nSkill is active!", "subhead")
                text.configure(height=self.getDH(text.winfo_width(),name.title(), "Helvetica", 15, "bold","skill")+1)
            else:
                text.configure(height=self.getDH(text.winfo_width(),name, "Helvetica", 15, "bold","skill"))
            contentframe = Frame(mtfr, bg=self.theme['tooltip']['bg'], highlightthickness=0, highlightcolor=self.theme['tooltip']['highlight'])
            contentframe.grid(row=2, column=0, sticky="nsew")
            contentframe.grid_propagate(False)
            self.insertInfoboxParagraph(contentframe, self.compensateInfoboxString(skill_gdesc+"<hr>"+skill_desc.strip()), "Helvetica", "#ffffff", 10, "normal", 0, text.winfo_width())
            contentframe.grid_propagate(True)
            mainbutton.configure(command=lambda url = skill_link: self.openURL(url))
            printed=True

        text.configure(state=DISABLED)
        #frame.pack_propagate(True) Preset width means we don't need to turn this back on


    def setupInfoboxFrameStatic(self, item, key, environment='space', tooltip=None):
        """Set up infobox frame with given item"""
        # Retain until experimental version is stable

        if environment == 'skill':
            frame = self.skillInfoboxFrame
        elif environment == 'ground':
            frame = self.groundInfoboxFrame
        else:
            frame = self.shipInfoboxFrame

        if item is not None and 'item' in item:
            name = item['item']
        elif isinstance(item, str):
            name = item
        else:
            self.logWriteSimple('InfoboxFail', environment, 4, tags=["NO NAME", key])
            return
        self.logWriteSimple('Infobox', environment, 4, tags=[name, key])

        if key is not None and key != '' and environment != 'skill':
            self.precacheEquipment(key)

        raritycolor = '#ffffff'
        if 'rarity' in item:
            if item["rarity"].lower() == "epic":
                raritycolor = '#ffd700'
            elif item["rarity"].lower() == "ultra rare":
                raritycolor = "#6d65bc"
            elif item["rarity"].lower() == "very rare":
                raritycolor = "#a245b9"
            elif item["rarity"].lower() == "rare":
                raritycolor = "#0099ff"
            elif item["rarity"].lower() == "uncommon":
                raritycolor = "#00cc00"

        self.clearFrame(frame)
        height = 25
        width = 15
        if environment != 'skill': width += 25
        if environment == 'skill': height -= 5

        Label(frame, text="Stats & Other Info", highlightbackground=self.theme['frame_medium']['hlbg'], highlightthickness=self.theme['frame_medium']['hlthick']).pack(fill=X, expand=False, side=TOP)
        text = Text(frame, height=height, width=width, bg=self.theme['tooltip']['bg'], fg=self.theme['tooltip']['fg'], wrap=WORD)
        text.tag_configure('name', foreground=raritycolor, font=self.font_tuple_create('tooltip_name'))
        text.tag_configure('rarity', foreground=raritycolor, font=self.font_tuple_create('tooltip_body'))
        text.tag_configure('head', foreground=self.theme['tooltip']['head']['fg'], font=self.font_tuple_create('tooltip_head'))
        text.tag_configure('subhead', foreground=self.theme['tooltip']['subhead']['fg'], font=self.font_tuple_create('tooltip_subhead'))
        text.tag_configure('who', foreground=self.theme['tooltip']['who']['fg'], font=self.font_tuple_create('tooltip_subhead'))
        text.tag_configure('distance', foreground=self.theme['tooltip']['distance']['fg'], font=self.font_tuple_create('tooltip_distance'))
        text.pack(fill="both", expand=True, padx=2, pady=2, side=BOTTOM)
        if name is None or name == '':
            return

        text.insert(END, name, 'name')
        if 'mark' in item and item['mark']:
            text.insert(END, ' '+item['mark'], 'name')
        if 'modifiers' in item and item['modifiers']:
            text.insert(END, ' '+('' if item['modifiers'][0] is None else ' '.join(item['modifiers'])), 'name')
        text.insert(END, '\n')

        #if 'tooltip' in item and item['tooltip']:
        #    text.insert(END, html['tooltip'])

        if name in self.cache['shipTraits']:
            text.insert(END, self.cache['shipTraits'][name])

        if tooltip is not None: text.insert(END, tooltip)

        if environment in self.cache['traits'] and name in self.cache['traits'][environment]:
            text.insert(END, self.cache['traits'][environment][name])

        if environment in self.cache['boffTooltips'] and name in self.cache['boffTooltips'][environment]:
                text.insert(END, self.cache['boffTooltips'][environment][name])

        if key in self.cache['equipment'] and name in self.cache['equipment'][key]:
            # Show the infobox data from json
            html = self.cache['equipment'][key][name]

            if 'rarity' in item and item['rarity']:
                text.insert(END, item['rarity']+' ', 'rarity')
            if 'type' in html and html['type']:
                text.insert(END, html['type'], 'rarity')
            if ('rarity' in item and item['rarity']) or ('type' in html and html['type']):
                text.insert(END, '\n')
            text.insert(END, '\n\n', 'distance')

            for i in range(1,9):
                t = html["head"+str(i)].replace("*","  • ").strip()
                if t.strip() != '':
                    text.insert(END, self.deHTML(self.compensateInfoboxString(t))+'\n','head')
                    text.insert(END, '\n', 'distance')
                t = html["subhead"+str(i)].replace("*","  • ").strip()
                if t.strip() != '':
                    text.insert(END, self.deHTML(self.compensateInfoboxString(t))+'\n', 'subhead')
                    text.insert(END, '\n', 'distance')
                t = html["text"+str(i)].replace("*","  • ").strip()
                if t.strip() != '':
                    text.insert(END, self.deHTML(self.compensateInfoboxString(t))+'\n')
                    text.insert(END, '\n', 'distance')


        text.configure(state=DISABLED)


    def radiobuttonVarUpdateCallbackToggle(self, varObj, choice):
        """Insert the radio setting -- typically used from the frame to widen the click zone"""
        varObj.set(choice)


    def checkbuttonVarUpdateCallbackToggle(self, varObj):
        """Toggle the checkbox setting -- typically used from the frame to widen the click zone"""
        current = not(varObj.get())
        varObj.set(current)


    def checkbuttonVarUpdateCallback(self, var, masterkey, key="", text=""):
        """Updates self.build[masterkey][key][text] to var; masterkey, key and text determine the level and identifier the var is inserted, allowing for 3-level depth at maximum. key and text can be left empty is not needed"""
        if masterkey not in self.build:
            return
        if key != "" and text !="":
            self.build[masterkey][key+"|"+text] = var
        elif key != "" and text=="":
            self.build[masterkey][key] = var
        elif key == "" and text == "":
            self.build[masterkey] = var
        self.setupCurrentBuildTagFrames()
        self.logWriteSimple('checkbuttonCallback', var, 2, [masterkey, key, text])
        self.auto_save_queue()
    
    def checkbuttonBuildBlock(self, window, frame: Frame, values, bg, fg, masterkey: str, key = str(""), geomanager="grid", orientation=HORIZONTAL, rowoffset=0, columnoffset=0,  alignment=TOP):
        """Inserts a series of Checkbuttons either horizontally or vertically, either row for row in the grid of the parent frame or packed into the parent
        frame on the given side. Parameters:
        window: Toplevel or Tkinter window mainlooping; 
        frame: the parent frame that the checkboxes get inserted to (must be managed by the geomanager stated in parameter geomanager); 
        values: list or dictionary containing the individual checkbuttons texts, each entry has to have a correspondence inside the dictionary the checkbuttons values will be saved to; 
        bg: background for text and checkboxes; fg: text color; masterkey: first-level identifier of the corresponding dictionary; 
        key: second-level identifier of the corresponding dictionary; 
        geomanager: which geomanager manages frame; 
        orientation: orientation of checkbutton sequence; 
        rowoffset / columnoffset: if frame is managed by grid, then they determine the cell the first checkbutton will be inserted, subsequent Checkbuttons will be insertet left / below it; 
        alignment: if frame is managed by pack, then the Checkbuttons will be aligned at that side inside the frame
        
        The method returns the number of checkbuttons inserted"""
        if geomanager == "grid":
            topframe = frame
            insertrow = rowoffset
            insertcolumn = columnoffset
        elif geomanager == "pack":
            topframe = Frame(frame, bg=bg, highlightthickness=0)
            topframe.pack(side=alignment, fill=BOTH)
            insertrow = 0
            insertcolumn = 0
        else: return
        count = 0 
        for t in values:
            itemframe = Frame(topframe, highlightthickness=0, bg=bg)
            if orientation==HORIZONTAL: 
                topframe.columnconfigure(insertcolumn, weight=1)
                itemframe.grid(row=insertrow, column=insertcolumn, padx=16, sticky="n")
                insertcolumn +=1
            elif orientation==VERTICAL: 
                topframe.rowconfigure(insertrow, weight=1)
                itemframe.grid(row=insertrow, column=insertcolumn, padx=16, sticky="w")
                insertrow +=1
            lvar = -1
            if key != "":
                if key+"|"+t.lower() in self.build[masterkey]:
                    lvar = self.build[masterkey][key+"|"+t.lower()]
            elif key == "":
                if t.lower() in self.build[masterkey]:
                    lvar = self.build[masterkey][t.lower()]
            if lvar == -1: lvar = 0
            v = IntVar(window, value=lvar)
            Checkbutton(itemframe, bg=bg, fg = "#000000", variable=v, activebackground=bg).pack(side=LEFT, ipadx=1, padx=0)
            v.trace_add("write", lambda c1, c2, c3, var=v, text=t, k=key, m=masterkey: self.checkbuttonVarUpdateCallback(var.get(), m, k, text))
            l = Label(itemframe, fg=fg, bg=bg, text=t.capitalize(), font=(self.theme["app"]["font"]["family"],self.theme["app"]["font"]["size"],"bold"))
            l.pack(side=LEFT, ipadx=0, padx=0)

            l.bind("<Button-1>", lambda e, var=v: self.checkbuttonVarUpdateCallbackToggle(var))
            count +=1
        return count
        

    def buildTagCallback(self):
        tagwindow = Toplevel(self.window, bg=self.theme['app']["bg"])
        tagwindow.resizable(False, False)
        tagwindow.transient(self.window)
        #tagwindow.attributes('-topmost', 1)
        tagwindow.title("Build Tags")

        cfr = Frame(tagwindow, bg=self.theme['app']["fg"])
        cfr.pack(expand=True, padx=15, pady=15, fill=BOTH)

        roleframe = Frame(cfr, highlightthickness=0, bg=self.theme['app']["fg"])
        roleframe.grid(row=0, column=0, columnspan=4, sticky="nsew")
        Label(roleframe, text="Role:", fg=self.theme['label']['bg'], bg=self.theme['app']['fg'], font=("Helvetica", self.theme['button_heavy']['font']['size'], self.theme['button_heavy']['font']['weight'])).grid(row=0, column=0, columnspan=6, sticky="new")
        self.checkbuttonBuildBlock(tagwindow, roleframe, self.persistent['tags']['role'], self.theme['app']['fg'], "#ffffff", "tags", "role", "grid", HORIZONTAL, 1)
        Frame(cfr, highlightthickness=0, bg=self.theme['app']["fg"]).grid(row=1, column=0, columnspan=4)
        cfr.rowconfigure(1, minsize=12)

        mdmgfr = Frame(cfr, highlightthickness=0,  bg=self.theme['app']["fg"])
        mdmgfr.grid(row=2, column=0, sticky="nsew", columnspan=4)
        Frame(cfr, highlightthickness=0, bg=self.theme['app']["fg"]).grid(row=3, column=0, columnspan=4)
        cfr.rowconfigure(3, minsize=12)
        Label(mdmgfr, text="Main Damage Type:", fg=self.theme['label']['bg'], bg=self.theme['app']['fg'],font=("Helvetica", self.theme['button_heavy']['font']['size'],self.theme['button_heavy']['font']['weight'])).grid(row=0, column=0, columnspan=5, sticky="new")
        self.checkbuttonBuildBlock(tagwindow, mdmgfr, self.persistent['tags']['maindamage'], self.theme['app']['fg'], "#ffffff", "tags", "maindamage", "grid", HORIZONTAL, 1)
        
        etypefr = Frame(cfr, highlightthickness=0, bg=self.theme['app']["fg"])
        etypefr.grid(row=4, column=0, sticky="n")
        cfr.columnconfigure(0, weight=1)
        Frame(cfr, highlightthickness=0, bg=self.theme['app']["fg"]).grid(row=5, column=0, columnspan=4)
        cfr.rowconfigure(5, minsize=12)
        Label(etypefr, text="Damage Type:", fg=self.theme['label']['bg'], bg=self.theme['app']['fg'],font=("Helvetica", self.theme['button_heavy']['font']['size'],self.theme['button_heavy']['font']['weight'])).grid(row=0, column=0, sticky="new")
        self.checkbuttonBuildBlock(tagwindow, etypefr, self.persistent['tags']['energytype'], self.theme['app']['fg'], "#ffffff", "tags", "energytype", "grid", VERTICAL, 1)
        
        wtypefr = Frame(cfr, highlightthickness=0,  bg=self.theme['app']["fg"])
        wtypefr.grid(row=4, column=1, sticky="n")
        cfr.columnconfigure(1, weight=1)
        Label(wtypefr, text="Weapons Type:", fg=self.theme['label']['bg'], bg=self.theme['app']['fg'],font=("Helvetica", self.theme['button_heavy']['font']['size'],self.theme['button_heavy']['font']['weight'])).grid(row=0, column=0, sticky="new")
        self.checkbuttonBuildBlock(tagwindow, wtypefr, self.persistent['tags']['weapontype'], self.theme['app']['fg'], "#ffffff", "tags", "weapontype", "grid", VERTICAL, 1)

        stypefr = Frame(cfr, highlightthickness=0, bg=self.theme['app']["fg"])
        stypefr.grid(row=4, column=2, sticky="n")
        cfr.columnconfigure(2, weight=1)
        Label(stypefr, text="State of the Build", fg=self.theme['label']['bg'], bg=self.theme['app']['fg'],font=("Helvetica", self.theme['button_heavy']['font']['size'],self.theme['button_heavy']['font']['weight'])).grid(row=0, column=0, sticky="new")
        i = 1
        if "state" in self.build["tags"]:
            lvar = self.build["tags"]["state"]
        else:
            lvar = 0
        tagvar = IntVar(tagwindow, value=lvar)

        for tag in self.options_tags:
            itemframe = Frame(stypefr, highlightthickness=0, bg=self.theme['app']['fg'])
            itemframe.grid(row=i, column=0, padx=16, sticky="w")
            selection_number = i-1
            Radiobutton(itemframe, bg=self.theme['app']['fg'], fg = "#000000", variable=tagvar, value=selection_number, activebackground=self.theme['app']['fg']).pack(side=LEFT, ipadx=1, padx=0)
            l = Label(itemframe, fg="#ffffff", bg=self.theme['app']['fg'], text=tag, font=(self.theme["app"]["font"]["family"],self.theme["app"]["font"]["size"],"bold"))
            l.pack(side=LEFT, ipadx=0, padx=0)
            l.bind("<Button-1>", lambda e, var=tagvar,choice=selection_number: self.radiobuttonVarUpdateCallbackToggle(var, choice))

            i += 1
        tagvar.trace_add("write", lambda c1, c2, c3, var=tagvar, k="state", m="tags": self.checkbuttonVarUpdateCallback(var.get(), m, k))

        tagwindow.wait_visibility()
        tagwindow.grab_set()
        tagwindow.update()
        tagwindow.geometry(self.pickerLocation(width=tagwindow.winfo_width(), height=tagwindow.winfo_height(), anchor='sw'))
        tagwindow.wait_window()


    def setupDoffListFrame(self, frame, environment='space'):
        doffEnvironment = environment.title()
        isSpace = False if environment == 'ground' else True
        self.precacheDoffs(doffEnvironment)
        doff_list = sorted([self.deWikify(item) for item in list(self.cache['doffNames'][doffEnvironment].keys())])

        DoffFrame = Frame(frame, bg=self.theme['frame_light']['bg'], padx=5, pady=3)
        DoffFrame.pack(side=LEFT, fill=Y, expand=True)
        DoffFrame.grid_columnconfigure(2, weight=1, uniform=environment+'ColDoffList')

        DoffLabel = Label(DoffFrame, text=environment.title()+" Duty Officers", bg=self.theme['entry_dark']['bg'], fg=self.theme['entry_dark']['fg'], width=60)
        DoffLabel.grid(row=0, column=0, columnspan=3, sticky='nsew')

        for i in range(6):
            v0 = StringVar(self.window)
            v1 = StringVar(self.window)
            v2 = StringVar(self.window)
            #m = OptionMenu(DoffFrame, v0, 'NAME', *['A','B','C'])
            #m.grid(row=i+1, column=0, sticky='nsew')
            #m.configure(bg=self.theme['frame_light']['bg'],fg=self.theme['frame_light']['fg'], borderwidth=0, highlightthickness=0, state=DISABLED)
            m = OptionMenu(DoffFrame, v1, 'SPECIALIZATION', *doff_list)
            m.grid(row=i+1, column=1, sticky='nsew')
            m.configure(bg=self.theme['frame_light']['bg'],fg=self.theme['frame_light']['fg'], borderwidth=0, highlightthickness=0, width=23)
            m = OptionMenu(DoffFrame, v2, 'EFFECT\nOTHER', '')
            m.grid(row=i+1, column=2, sticky='nsew')
            m.configure(bg=self.theme['frame_light']['bg'],fg=self.theme['frame_light']['fg'], borderwidth=0, highlightthickness=0,font=self.theme['text_small']['font_object'], wraplength=340)
            #DoffFrame.grid_rowconfigure(i+1, weight=1, uniform='doffFrameListRow{}'.format(i+1))
            if self.build['doffs'][environment][i] is not None:
                v0.set(self.build['doffs'][environment][i]['name'])
                v1.set(self.build['doffs'][environment][i]['spec'])
                v2.set(self.doffSpecClean(self.build['doffs'][environment][i]['effect']))
                m['menu'].delete(0, END)
                doff_desclist = sorted([self.doffStripPrefix(self.cache['doffs'][doffEnvironment][item]['description'], isSpace) for item in list(self.cache['doffs'][doffEnvironment].keys()) if v1.get() in self.cache['doffs'][doffEnvironment][item]['name']])

                for desc in doff_desclist:
                    m['menu'].add_command(label=desc, command=lambda v2=v2,value=desc: v2.set(value))

            v1.trace_add("write", lambda v,i,m,menu=m,v0=v1,v1=v2,row=i:self.doffSpecCallback(menu, v0, v1, row, isSpace))
            v2.trace_add("write", lambda v,i,m,menu=m,v0=v1,v1=v2,row=i:self.doffEffectCallback(menu, v0, v1, row, isSpace))

    def doffSpecClean(self, text):
        text = text.replace('; ', '\n')
        text = text.replace(' + ', '\n')
        text = text.replace('+ ', '\n')
        return text

    def setupDoffFrame(self, frame):
        self.clearFrame(frame)
        mainFrame = Frame(frame, bg=self.theme['frame']['bg'])
        mainFrame.pack(side='bottom', fill=BOTH, expand=True, pady=(5,0))

        self.setupDoffListFrame(mainFrame, 'space')
        DoffBreak = Frame(mainFrame, bg=self.theme['entry_dark']['bg'], width=10)
        DoffBreak.pack(side='left')
        self.setupDoffListFrame(mainFrame, 'ground')

    def setupLogoFrame(self):
        self.clearFrame(self.logoFrame)

        #maxWidth = self.window.winfo_screenwidth()
        #if maxWidth > self.windowWidth:
            #maxWidth = self.windowWidth
        self.images['logoImage'] = self.loadLocalImage("logo_bar.png", width=self.windowWidth, height=self.logoHeight)

        Label(self.logoFrame, image=self.images['logoImage'], borderwidth=0, highlightthickness=0).pack()

    def setupFooterFrame(self):
        self.footerFrame = Frame(self.containerFrame, bg=self.theme['app']['bg'], height=20)
        self.footerFrame.pack(fill='both', side='bottom', expand=False)

        self.footerFrameL = Frame(self.footerFrame, bg=self.theme['app']['bg'])
        self.footerFrameL.grid(row=0, column=0, sticky='w')
        footerLabelL = Label(self.footerFrameL, textvariable=self.log, fg=self.theme['app']['fg'], bg=self.theme['app']['bg'], anchor='w', font=self.font_tuple_create('text_small'))
        footerLabelL.grid(row=0, column=0, sticky='w')

        self.footerFrameR = Frame(self.footerFrame, bg=self.theme['app']['bg'])
        self.footerFrameR.grid(row=0, column=1, sticky='e')
        footerLabelR = Label(self.footerFrameR, textvariable=self.logmini, fg=self.theme['app']['fg'], bg=self.theme['app']['bg'], anchor='e', font=self.font_tuple_create('text_highlight'))
        footerLabelR.grid(row=0, column=0, sticky='e')

        self.footerFrame.grid_columnconfigure(0, weight=2, uniform="footerlabel")
        self.footerFrame.grid_columnconfigure(1, weight=2, uniform="footerlabel")


    def lineTruncate(self, content, length=500):
        return '\n'.join(content.split('\n')[-1*length:])

    def setFooterFrame(self, leftnote, rightnote=None):
        """Set up footer frame with given item"""
        leftnote = leftnote[:200]
        rightnote = rightnote[:150]

        if not len(leftnote):
            self.log.set(self.log.get())
        else:
            self.log.set(leftnote)

        if not len(rightnote):
            self.logmini.set(self.logmini.get())
        else:
            self.logmini.set(rightnote)


    def setupSkillMenuFrame(self, parentFrame):
        self.clearFrame(parentFrame)

        settingsMenuSkill = {
            'Space Skill Tree'             : {'type' : 'button_block', 'var_name' : 'spaceSkillButton', 'callback' : self.focusSpaceSkillBuildFrameCallback, 'colWeight' : 1},
            'Ground Skill Tree'            : {'type' : 'button_block', 'var_name' : 'groundSkillButton', 'callback' : self.focusGroundSkillBuildFrameCallback, 'colWeight' : 1},
        }

        self.create_item_block(parentFrame, theme=settingsMenuSkill, shape='row', elements=1)

    def menu_clear_callback(self, choice):
        if self.in_splash():
            return
        self.logWriteSimple('menu', 'clear', 2, [choice])
        if choice == 'Clear all':
            self.clearBuildCallback()
        elif choice == 'Clear skills':
            self.reset_skill_build()

    def setupMenuFrame(self):
        self.clearFrame(self.menuFrame)
        col = 0

        exportImportFrame = Frame(self.menuFrame, bg=self.theme['frame']['bg'])
        exportImportFrame.grid(row=0, column=col, sticky='nsew')
        settingsMenuExport = {
            'default': {'bg': self.theme['button_medium']['bg'], 'fg': self.theme['button_medium']['fg'], 'font_data': self.font_tuple_create('button_medium')},
            'Save': {'type': 'button_block', 'var_name': 'exportFullButton', 'callback': self.exportCallback},
            'Open': {'type': 'button_block', 'var_name': 'importButton', 'callback': self.importCallback},
            'Clear...': {'type': 'menu', 'var_name': 'clearButton', 'setting_options': ['Clear all', 'Clear skills'], 'callback': 'menu_clear_callback'},
        }
        self.create_item_block(exportImportFrame, theme=settingsMenuExport, shape='row', elements=1)
        col += 1

        settingsMenuTop = {
            'default': {'bg': self.theme['button_heavy']['bg'], 'fg': self.theme['button_heavy']['fg'], 'font_data': self.font_tuple_create('button_heavy')},
            'SPACE': {'type': 'button_block', 'var_name': 'spaceButton', 'callback': self.focusSpaceBuildFrameCallback},
            'GROUND': {'type': 'button_block', 'var_name': 'groundButton', 'callback': self.focusGroundBuildFrameCallback},
            'SKILL TREE': {'type': 'button_block', 'var_name': 'skillButton', 'callback': self.focusSkillTreeFrameCallback},
        }
        self.create_item_block(self.menuFrame, row=0, col=col, theme=settingsMenuTop, shape='row', elements=1)
        col += 3

        buttonSettings = Frame(self.menuFrame, bg=self.theme['frame']['bg'])
        buttonSettings.grid(row=0, column=col, sticky='nsew')
        settingsMenuSettings = {
            'default': {'bg': self.theme['button_medium']['bg'], 'fg': self.theme['button_medium']['fg'], 'font_data': self.font_tuple_create('button_medium')},
            'Export reddit': {'type': 'button_block', 'var_name': 'exportRedditButton', 'callback': self.exportRedditCallback},
            'Library'   : { 'type' : 'button_block', 'var_name' : 'libraryButton', 'callback' : self.focusLibraryFrameCallback},
            'Settings'  : { 'type' : 'button_block', 'var_name' : 'settingsButton', 'callback' : self.focusSettingsFrameCallback, 'image': self.three_bars},
        }

        self.create_item_block(buttonSettings, theme=settingsMenuSettings, shape='row', elements=1)
        col += 1

        for i in range(5):
            self.menuFrame.grid_columnconfigure(i, weight=1, uniform="mainCol")


    def setupTierFrame(self, tier):
        #l = Label(self.shipTierFrame, text="Tier:", fg=self.theme['label']['fg'], bg=self.theme['label']['bg'], font=self.theme['text_small']['font_object'])
        #l.grid(row=0, column=0, sticky='nsew')
        #l.configure(borderwidth=0, highlightthickness=0)
        tier_list = self.getTierOptions(tier)
        if len(tier_list) > 1:
            m = OptionMenu(self.shipTierFrame, self.backend["tier"], *tier_list)
        else:
            m = Label(self.shipTierFrame, text=tier_list[0], justify=LEFT)

        m.grid(column=1, row=0, sticky='swe', pady=(1,0), padx=(1,0))
        m.configure(width=6, height=1, bg=self.theme['button']['bg'],fg=self.theme['button']['fg'], borderwidth=0, highlightthickness=0, font=self.theme['text_small']['font_object'])


    def setupShipImageFrame(self):
        try:
            self.backend['shipHtml'] = self.getShipFromName(self.ships, self.build['ship'])
            ship_image = self.backend['shipHtml']['image'].replace(' ','_')
            self.shipImg = self.fetchOrRequestImage(self.wikiImages+ship_image, self.build['ship'], self.imageBoxX, self.imageBoxY)
        except:
            self.shipImg = self.getEmptyFactionImage()
        self.setShipImage(self.shipImg)

    def setupTagsFrame(self, parent_frame, environment='space'):
        b = HoverButton(parent_frame, text="Build Tags", fg=self.theme['button_heavy']['fg'], bg=self.theme['button_heavy']['bg'], activebackground=self.theme['button_heavy']['hover'], font=self.font_tuple_create('button_heavy'), command=lambda: self.buildTagCallback())
        b.pack(fill=X, side=TOP)
        f = Frame(parent_frame, bg=self.theme['frame']['bg'])
        f.pack(fill=BOTH, side=TOP)

        if environment == 'skill':
            self.skillBuildTagFrame = f
        elif environment == 'ground':
            self.groundBuildTagFrame = f
        else:
            self.shipBuildTagFrame = f

        self.updateTagsFrame(environment)


    def updateTagsFrame(self, environment='space'):
        if environment == 'skill':
            parent_frame = self.skillBuildTagFrame
        elif environment == 'ground':
            parent_frame = self.groundBuildTagFrame
        else:
            parent_frame = self.shipBuildTagFrame

        self.clearFrame(parent_frame)
        for i in range(4):
            parent_frame.grid_columnconfigure(i, weight=1, uniform='tagViewCol')

        # Columns to gather in -- should be more programmatic
        grid_width = 4
        tag_group = {
            'maindamage': 1,
            'energytype': 3,
            'weapontype': 2,
            'state': 0,
            'role': 0,
        }

        tag_grid = [1] * grid_width
        for tag in sorted(self.build['tags']):
            if tag != 'state' and not self.build['tags'][tag]:
                continue

            tags = tag.split('|')
            group_tag = tags[0].lower()
            group_col = tag_group[group_tag] if group_tag in tag_group else (grid_width - 1)
            if tag == 'state':
                column = 0
                row = 0
                columnspan = grid_width
                pad_y = 5
                font_theme = 'text_contrast'
            else:
                column = group_col
                columnspan = 1
                row = tag_grid[group_col]; tag_grid[group_col] += 1
                pad_y = 0
                font_theme = 'app'

            display_tag = tags[-1].title() if tag != 'state' else self.options_tags[self.build['tags'][tag]]

            l = Label(parent_frame, text=display_tag, fg=self.theme['frame']['fg'], bg=self.theme['frame']['bg'], font=self.font_tuple_create(font_theme))
            l.grid(row=row, column=column, columnspan=columnspan, pady=pad_y)


    def setupCaptainFrame(self, charInfoFrame, environment='space'):
        self.precacheFactions()
        self.precacheReputations()
        row = 0

        Label(charInfoFrame, text="Elite Captain", fg=self.theme['label']['fg'], bg=self.theme['label']['bg']).grid(column=0, row = row, sticky='e')
        m = Checkbutton(charInfoFrame, variable=self.backend["eliteCaptain"], fg=self.theme['label']['fg'], bg=self.theme['label']['bg'], command=self.eliteCaptainCallback)
        m.grid(column=1, row=row, sticky='w', pady=2, padx=2)
        m.configure(fg=self.theme['label']['fg'], bg=self.theme['label']['bg'], borderwidth=0, highlightthickness=0)
        row += 1

        captainSettingsDefaults = {
            'default': {'store': 'backend', 'sticky': 'nsew'},
            # 'Elite Captain': {'col': 2, 'type': 'optionmenu', 'var_name': 'eliteCaptain', 'boolean': True, 'callback': self.eliteCaptainCallback},
            'Captain Career': {'col': 2, 'type': 'optionmenu', 'var_name': 'career', 'setting_options': ['', 'Tactical', 'Engineering', 'Science']},
            'Faction': {'col': 2, 'type': 'optionmenu', 'var_name': 'captain', 'var_sub_name': 'faction', 'setting_options': self.factionNames},
            'Species': {'col': 2, 'type': 'optionmenu', 'var_name': 'species', 'setting_options': self.speciesNames['all']},
            'Primary Spec': {'col': 2, 'type': 'optionmenu', 'var_name': 'specPrimary', 'setting_options': sorted(self.cache['specsPrimary'])},
            'Secondary Spec': {'col': 2, 'type': 'optionmenu', 'var_name': 'specSecondary', 'setting_options': sorted(self.cache['specsSecondary'])},
        }
        self.create_item_block(charInfoFrame, theme=captainSettingsDefaults, row=row)

        charInfoFrame.grid_columnconfigure(1, weight=1, uniform="captColSpace")

    def updateShipDesc(self, event):
        self.build['playerShipDesc'] = self.shipDescText.get("1.0", END)
        self.auto_save_queue()

    def updatePlayerDesc(self, event):
        self.build['playerDesc'] = self.charDescText.get("1.0", END)
        self.auto_save_queue()

    def setShipImage(self, suppliedImage=None):
        if suppliedImage is None: suppliedImage = self.getEmptyFactionImage()
        if suppliedImage == self.getEmptyFactionImage(): bgColor = self.theme['button']['bg']
        else: bgColor = self.theme['space']['bg']

        image1 = self.imageFromInfoboxName('Epic') if 'tier' in self.build and self.build['tier'] == "T6-X" else self.emptyImage

        self.ship_image_canvas.itemconfig(self.ship_image,image=suppliedImage)
        self.ship_image_canvas.configure(bg=bgColor)

    def setCharImage(self, suppliedImage=None):
        if suppliedImage is None: suppliedImage = self.getEmptyFactionImage()
        if suppliedImage == self.getEmptyFactionImage(): bgColor = self.theme['button']['bg']
        else: bgColor = self.theme['space']['bg']

        self.ground_image_canvas.itemconfig(self.ground_image,image=suppliedImage)
        self.ground_image_canvas.configure(bg=bgColor)

        self.skill_image_canvas.itemconfig(self.skill_image,image=suppliedImage)
        self.skill_image_canvas.configure(bg=bgColor)

    def setupInfoFrame(self, environment='space'):
        if environment == 'ground': parentFrame = self.groundInfoFrame
        elif environment == 'skill': parentFrame = self.skillInfoFrame
        else: parentFrame = self.shipInfoFrame

        self.clearFrame(parentFrame)

        LabelFrame = Frame(parentFrame, bg=self.theme['frame']['bg'])
        LabelFrame.pack(fill=X, expand=False, anchor="n", side=TOP)

        imageLabel = Canvas(LabelFrame, bg=self.theme['button']['bg'], borderwidth=0, highlightbackground='black', highlightthickness=3)
        img0 = imageLabel.create_image(self.imageBoxX / 2, self.imageBoxY / 2, anchor="center", image=self.getEmptyFactionImage())
        #img1 = imageLabel.create_image(imageBoxX / 2, imageBoxY / 2, anchor="center", image=self.emptyImage)
        if environment == 'ground':
            self.ground_image_canvas = imageLabel
            self.ground_image = img0
        elif environment == 'skill':
            self.skill_image_canvas = imageLabel
            self.skill_image = img0
        else:
            self.ship_image_canvas = imageLabel
            self.ship_image = img0

        imageLabel.grid(row=0, column=0, sticky='nsew')
        LabelFrame.grid_columnconfigure(0, weight=0, minsize=self.imageBoxX)
        LabelFrame.grid_rowconfigure(0, weight=0, minsize=self.imageBoxY)

        if environment != 'skill':
            NameFrame = Frame(parentFrame, bg=self.theme['frame_medium']['bg'])
            NameFrame.pack(fill=X, expand=False, padx=(0, 5), pady=(5, 0), side=TOP)
            NameFrame.grid_columnconfigure(1, weight=1)

            row = 0
            if environment == 'space':
                self.shipTierFrame = Frame(LabelFrame, bg=self.theme['frame_medium']['bg'])
                self.shipTierFrame.grid(column=0, row=row, sticky='se')
                row += 1
                labelFrame = Label(NameFrame, text="Ship: ", fg=self.theme['label']['fg'], bg=self.theme['label']['bg'])
                labelFrame.grid(column=0, row = row, sticky='w', pady=(1,0))
                self.shipButton = HoverButton(NameFrame, text="<Pick>", command=self.shipPickButtonCallback, bg=self.theme['frame_medium']['bg'], wraplength=270, activebackground=self.theme['frame_medium']['hover'])
                self.shipButton.grid(column=1, row=row, sticky='nwse')
                row += 1

            labelFrame = Label(NameFrame, text="{} Name:".format('Ship' if environment == 'space' else 'Toon'), fg=self.theme['label']['fg'], bg=self.theme['label']['bg'])
            labelFrame.grid(row=row, column=0, sticky='w')
            entryFrame = Entry(NameFrame, textvariable=self.backend['player{}Name'.format('Ship' if environment == 'space' else '')], fg=self.theme['label']['fg'], bg=self.theme['label']['bg'], font=self.font_tuple_create('text_highlight'))
            entryFrame.grid(row=row, column=1, sticky='nsew', ipadx=2, ipady=5, pady=5)
            row += 1
            # end of not-skill items


        #ExtraFrame = Frame(parentFrame, bg=self.theme['frame_medium']['bg'])
        #ExtraFrame.pack(fill=X, expand=True, padx=0, pady=0, side=TOP)
        descFrame = Frame(parentFrame, bg=self.theme['frame_medium']['bg'])
        descFrame.pack(fill=BOTH, expand=True, side=TOP)
        #ExtraFrame = Frame(parentFrame, bg=self.theme['frame_medium']['bg'])
        #ExtraFrame.pack(fill=X, expand=True, padx=0, pady=0, side=TOP)

        ExtraFrame = Frame(parentFrame, bg=self.theme['frame_medium']['bg'])
        ExtraFrame.pack(fill=X, expand=False, padx=0, pady=0, side=BOTTOM)
        CharFrame = Frame(parentFrame, bg=self.theme['frame_medium']['bg'])
        CharFrame.pack(fill=X, expand=False, padx=2, side=BOTTOM)
        CharFrame.grid_columnconfigure(0, weight=1)
        charInfoFrame = Frame(CharFrame, bg=self.theme['frame_medium']['bg'])
        charInfoFrame.grid(row=0, column=0, columnspan=2, sticky='ew')
        self.setupCaptainFrame(CharFrame, environment)

        if environment == 'skill':
            self.skillDescFrame = descFrame
        elif environment == 'ground':
            self.groundDescFrame = descFrame
        elif environment == 'space':
            self.shipDescFrame = descFrame
            if self.build['ship'] is not None: self.shipButton.configure(text=self.build['ship'])
            if 'tier' in self.build and len(self.build['tier']) > 1:
                self.setupTierFrame(int(self.build['tier'][1]))
                self.setupShipImageFrame()
                pass

    def setupHandleFrame(self, environment='space'):
        if environment == 'skill':
                self.setupPlayerHandleFrame(self.skillHandleFrame)
        elif environment == 'ground':
            self.setupPlayerHandleFrame(self.groundHandleFrame)
        else:
            self.setupPlayerHandleFrame(self.shipHandleFrame)


    def setupDescFrame(self, environment='space'):
        if environment == 'skill':
            self.setupDescEnvironmentFrame(environment='space', destination='skill')
            self.setupDescEnvironmentFrame(environment='ground', destination='skill', row=2)
        else: self.setupDescEnvironmentFrame(environment=environment)

    def setupPlayerHandleFrame(self, parentFrame, row=0):
        parentFrame.grid_columnconfigure(0, weight=1)

        frame = Frame(parentFrame, bg=self.theme['frame']['bg'])
        frame.grid(row=0, column=0, sticky='nsew')
        frame.columnconfigure(1, weight=1)
        label = Label(frame, text="Player Handle: ", fg=self.theme['frame']['fg'], bg=self.theme['frame']['bg'])
        label.grid(row=0, column=0, sticky='w')
        entry = Entry(frame, textvariable=self.backend['playerHandle'], fg=self.theme['frame']['fg'], bg=self.theme['frame']['bg'], font=self.font_tuple_create('text_highlight'), justify='center')
        entry.grid(row=0, column=1, sticky='nsew', ipady=5, pady=5, padx=5)
        row += 1


    def setupDescEnvironmentFrame(self, environment='space', destination=None, row=0):
        if destination is not None: parentFrame = self.skillDescFrame
        elif environment == 'space': parentFrame = self.shipDescFrame
        elif environment == 'ground': parentFrame = self.groundDescFrame
        else: return

        if row == 0: self.clearFrame(parentFrame)
        parentFrame.grid_columnconfigure(0, weight=1)

        label = Label(parentFrame, text="Description ({}):".format(environment.title()), fg=self.theme['label']['fg'], bg=self.theme['label']['bg'])
        label.grid(row=row, column=0, sticky='nw', pady=(5,2))
        descText = Text(parentFrame, height=3, width=20, wrap=WORD, fg=self.theme['entry']['fg'], bg=self.theme['entry']['bg'], font=self.font_tuple_create('text_tiny'))
        descText.grid(row=row+1, column=0, sticky='nsew', padx=(7,7), pady=(2,5))
        parentFrame.grid_rowconfigure(row+1, weight=1)

        if destination is None:
            if environment != 'space': self.charDescText = descText
            else: self.shipDescText = descText

        descText.bind('<KeyRelease>', self.updateShipDesc if environment == 'space' else self.updatePlayerDesc)
        if 'player{}Desc'.format('Ship' if environment == 'space' else '') in self.build:
            descText.delete(1.0, END)
            descText.insert(1.0, self.build['player{}Desc'.format('Ship' if environment == 'space' else '')])

    def setupInitialBuildGearFrame(self, parentFrame, environment='space'):
        parentFrame.grid_columnconfigure(0, weight=1, uniform="middleCol"+environment)
        parentFrame.grid_rowconfigure(0, weight=3, uniform="middleRow"+environment)
        parentFrame.grid_rowconfigure(1, weight=2, uniform="middleRow"+environment)

        middleFrameUpper = Frame(parentFrame, bg=self.theme['frame']['bg'])
        middleFrameUpper.grid(row=0,column=0,columnspan=3,sticky='nsew')
        middleFrameUpper.grid_rowconfigure(0, weight=1, uniform="secRow"+environment)
        middleFrameUpper.grid_columnconfigure(0, weight=1, uniform="secCol"+environment)
        middleFrameUpper.grid_columnconfigure(1, weight=1, uniform="secCol"+environment)
        middleFrameUpper.grid_columnconfigure(2, weight=1, uniform="secCol"+environment)

        col = 0
        equipmentFrame = Frame(middleFrameUpper, bg=self.theme['frame']['bg'])
        equipmentFrame.grid(row=0,column=col,sticky='nsew')
        #equipmentFrame.pack(side='left', fill=BOTH, expand=True, padx=20)
        col += 1
        if environment == 'space':
            middleFrameUpper.grid_columnconfigure(3, weight=1, uniform="secCol"+environment)
            consoleFrame = Frame(middleFrameUpper, bg=self.theme['frame']['bg'])
            consoleFrame.grid(row=0,column=col,sticky='nsew')
            col += 1
        boffFrame = Frame(middleFrameUpper, bg=self.theme['frame']['bg'])
        boffFrame.grid(row=0,column=col,sticky='nsew')
        col += 1
        traitFrame = Frame(middleFrameUpper, bg=self.theme['frame']['bg'])
        traitFrame.grid(row=0,column=col,sticky='nsew')
        col += 1

        middleFrameLower = Frame(parentFrame, bg=self.theme['frame']['bg'])
        middleFrameLower.grid(row=1,column=0,columnspan=3,sticky='nsew')
        middleFrameLower.grid_columnconfigure(0, weight=1, uniform="secCol2"+environment)
        doffFrame = Frame(middleFrameLower, bg=self.theme['frame']['bg'])
        doffFrame.pack(fill=BOTH, expand=False, padx=15, side=BOTTOM)

        if environment == 'ground':
            self.groundEquipmentFrame = equipmentFrame
            self.groundBoffFrame = boffFrame
            self.groundTraitFrame = traitFrame
            self.groundDoffFrame = doffFrame
        else:
            self.shipEquipmentFrame = equipmentFrame
            self.shipConsoleFrame = consoleFrame
            self.shipBoffFrame = boffFrame
            self.shipTraitFrame = traitFrame
            self.shipDoffFrame = doffFrame


    def setupInitialBuildFrames(self, environment='space'):
        if environment == 'skill': parentFrame = self.skillTreeFrame
        elif environment == 'ground': parentFrame = self.groundBuildFrame
        else: parentFrame = self.spaceBuildFrame

        parentFrame.grid_propagate(False)
        parentFrame.grid_rowconfigure(0, weight=1, uniform="mainRow"+environment)
        for i in range(5):
            if i == 0 or i == 4:
                parentFrame.grid_columnconfigure(i, weight=0, minsize=self.window_outside_frame_minimum)
            else:
                parentFrame.grid_columnconfigure(i, weight=5, uniform="mainCol"+environment)

        infoFrame = Frame(parentFrame, bg=self.theme['frame_medium']['bg'], highlightbackground=self.theme['frame_medium']['hlbg'], highlightthickness=self.theme['frame_medium']['hlthick'])
        infoFrame.grid(row=0,column=0,sticky='nsew', padx=(2,0), pady=(2,2))

        middleFrame = Frame(parentFrame, bg=self.theme['frame']['bg'])
        middleFrame.grid(row=0,column=1,columnspan=3,sticky='nsew', pady=5)
        if environment == 'skill':
            middleFrame.grid_rowconfigure(1, weight=1)
            middleFrame.grid_columnconfigure(0, weight=1)

            middleFrameUpper = Frame(middleFrame, bg=self.theme['frame']['bg'])
            middleFrameUpper.grid(row=0,column=0,sticky='nsew')
            self.setupSkillMenuFrame(middleFrameUpper)

            middleFrameLower = Frame(middleFrame, bg=self.theme['frame']['bg'])
            middleFrameLower.grid(row=1,column=0,sticky='nsew')
            middleFrameLower.grid_rowconfigure(1, weight=1)
            middleFrameLower.grid_columnconfigure(0, weight=1)

            self.skillSpaceBuildFrame = Frame(middleFrameLower, bg=self.theme['frame']['bg'])
            self.skillGroundBuildFrame = Frame(middleFrameLower, bg=self.theme['frame']['bg'])
            self.focusSkillBuildFrameCallback('space', init=True)
        if environment == 'space' or environment == 'ground':
            self.setupInitialBuildGearFrame(middleFrame, environment=environment)

        infoBoxOuterFrame = Frame(parentFrame, bg=self.theme['frame_medium']['bg'], highlightbackground=self.theme['frame_medium']['hlbg'] , highlightthickness=self.theme['frame_medium']['hlthick'])
        infoBoxOuterFrame.grid(row=0,column=4,sticky='nsew', padx=(2,0), pady=(2,2))

        buildTagFrame = Frame(infoBoxOuterFrame, bg=self.theme['frame_medium']['bg'])
        buildTagFrame.pack(fill=X, expand=False, side=BOTTOM)

        handleFrame = Frame(infoBoxOuterFrame, bg=self.theme['button_heavy']['bg'])
        handleFrame.pack(fill=X, expand=False, side=TOP)
        self.setupPlayerHandleFrame(handleFrame)

        infoboxFrame = Frame(infoBoxOuterFrame, bg=self.theme['tooltip']['bg'])
        infoboxFrame.pack(fill=BOTH, expand=True, side=TOP)

        if environment == 'skill':
            self.skillInfoFrame = infoFrame
            self.skillInfoboxFrame = infoboxFrame
            self.skillHandleFrame = handleFrame
            self.skillImg = self.getEmptyFactionImage()
        elif environment == 'ground':
            self.groundInfoFrame = infoFrame
            self.groundInfoboxFrame = infoboxFrame
            self.groundHandleFrame = handleFrame
            self.groundImg = self.getEmptyFactionImage()
        else:
            self.shipInfoFrame = infoFrame
            self.shipInfoboxFrame = infoboxFrame
            self.shipHandleFrame = handleFrame
            self.shipImg = self.getEmptyFactionImage()

        self.setupTagsFrame(buildTagFrame, environment)


    def setupLibraryFrame(self):
        pass #placeholder

    def setupSettingsFrame(self):
        settingsTopFrame = Frame(self.settingsFrame, bg=self.theme['frame_medium']['bg'])
        settingsTopFrame.pack(side='top', fill=BOTH, expand=True)
        settingsBottomFrame = Frame(self.settingsFrame, bg=self.theme['frame_medium']['bg'])
        settingsBottomFrame.pack(side='bottom', fill=BOTH, expand=True)

        settingsTopLeftFrame = Frame(settingsTopFrame, bg=self.theme['frame_medium']['bg'])
        settingsTopLeftFrame.grid(row=0,column=0,sticky='nsew', pady=5)
        settingsTopMiddleLeftFrame = Frame(settingsTopFrame, bg=self.theme['frame_medium']['bg'])
        settingsTopMiddleLeftFrame.grid(row=0,column=1,sticky='nsew', pady=5)
        settingsTopMiddleRightFrame = Frame(settingsTopFrame, bg=self.theme['frame_medium']['bg'])
        settingsTopMiddleRightFrame.grid(row=0,column=2,sticky='nsew', pady=5)
        settingsTopRightFrame = Frame(settingsTopFrame, bg=self.theme['frame_medium']['bg'])
        settingsTopRightFrame.grid(row=0,column=3,sticky='nsew', pady=5)

        settingsTopFrame.grid_columnconfigure(0, weight=2, uniform="settingsColSpace")
        settingsTopFrame.grid_columnconfigure(1, weight=2, uniform="settingsColSpace")
        settingsTopFrame.grid_columnconfigure(2, weight=2, uniform="settingsColSpace")
        settingsTopFrame.grid_columnconfigure(3, weight=2, uniform="settingsColSpace")

        settingsDefaults = {
            'Defaults (auto-saved):'     : { 'col' : 1, 'type': 'title'},
            'Mark'                       : { 'col' : 2, 'type' : 'optionmenu', 'var_name' : 'markDefault', 'setting_options': self.marks},
            'Rarity'                     : { 'col' : 2, 'type' : 'optionmenu', 'var_name' : 'rarityDefault', 'setting_options': [''] + self.rarities},
            'Faction'                    : { 'col' : 2, 'type' : 'optionmenu', 'var_name' : 'factionDefault', 'setting_options': self.factionNames},
            'blank1': {'col': 1, 'type': 'blank'},
            'Merge Export': {'col': 2, 'type': 'button', 'var_name': 'merge_file_create'},

        }
        self.create_item_block(settingsTopMiddleLeftFrame, theme=settingsDefaults)

        settingsTheme = {
            'Theme Settings (auto-saved):'          : { 'col' : 1, 'type': 'title'},
            'UI Scale (restart app for changes)'    : { 'col' : 2, 'type' : 'scale', 'var_name' : 'uiScale' },
            'blank1'                                : { 'col' : 1, 'type' : 'blank' },
            'Export default'                        : { 'col' : 2, 'type' : 'optionmenu', 'var_name' : 'exportDefault', 'setting_options': self.exportOptions },
            'Picker window spawn under mouse'       : { 'col' : 2, 'type' : 'optionmenu', 'var_name' : 'pickerSpawnUnderMouse', 'boolean' : True },
            'Keep template when clearing ship'      : { 'col' : 2, 'type' : 'optionmenu', 'var_name' : 'keepTemplateOnShipClear', 'boolean' : True },
            'Keep build when changing ships'        : { 'col' : 2, 'type' : 'optionmenu', 'var_name' : 'keepTemplateOnShipChange', 'boolean' : True },
            'blank3'                                : { 'col' : 1, 'type' : 'blank' },
            'Sort Options:'                         : { 'col' : 1 },
            'BOFF Sort 1st'                         : { 'col' : 2, 'type' : 'optionmenu', 'var_name' : 'boffSort', 'setting_options': self.boffSortOptions },
            'BOFF Sort 2nd'                         : { 'col' : 2, 'type' : 'optionmenu', 'var_name' : 'boffSort2', 'setting_options': self.boffSortOptions },
            'Console Sort'                          : { 'col' : 2, 'type' : 'optionmenu', 'var_name' : 'consoleSort', 'setting_options': self.consoleSortOptions },
            'blank4': {'col': 1, 'type': 'blank'},
            'Save current window position': {'col': 2, 'type': 'button', 'var_name': 'savePositionOnly'},
            'Save current window size+position': {'col': 2, 'type': 'button', 'var_name': 'savePosition'},
            'Reset to default window size/position': {'col': 2, 'type': 'button', 'var_name': 'resetPosition'},
        }
        self.create_item_block(settingsTopMiddleRightFrame, theme=settingsTheme)

        settingsMaintenance = {
            'Maintenance (auto-saved):'             : {'col': 1, 'type': 'title'},
            'Open Log'                              : {'col': 2, 'type': 'button', 'var_name': 'openLog'},
            'Open Splash Window': {'col': 2, 'type': 'button', 'var_name': 'openSplash'},
            'blank1'                                : {'col': 1, 'type': 'blank'},
            'Auto-save build': {'col': 2, 'type': 'optionmenu', 'var_name': 'autosave', 'boolean': True},
            'In-file versions': {'col': 2, 'type': 'optionmenu', 'var_name': 'versioning', 'boolean': True},
            'Force out of date JSON loading'        : {'col': 2, 'type': 'optionmenu', 'var_name': 'forceJsonLoad', 'boolean': True},
            'Fast start (experimental)'          : {'col': 2, 'type': 'optionmenu', 'var_name': 'fast_start', 'boolean': True},
            'Use faction-specific icons (experimental)': {'col': 2, 'type': 'optionmenu', 'var_name': 'useFactionSpecificIcons', 'boolean': True},
            'blank2'                                : {'col': 1, 'type': 'blank'},
            'Create SETS manual settings file': {'col' : 2, 'type': 'button', 'var_name': 'exportConfigFile'},
            'Backup current caches/settings'        : {'col': 2, 'type': 'button', 'var_name': 'backupCache'},
            'blank3': {'col': 1, 'type': 'blank'},
            'Clear data cache folder (Fast)'        : { 'col' : 2, 'type' : 'button', 'var_name' : 'clearcache' },
            'blank4'                                : { 'col' : 1, 'type' : 'blank' },
            'Check for new faction icons (Slow)'    : { 'col' : 2, 'type' : 'button', 'var_name' : 'clearfactionImages' },
            'Reset memory cache (Slow)'             : { 'col' : 2, 'type' : 'button', 'var_name' : 'clearmemcache' },
            'Clear image cache (VERY SLOW!)'        : { 'col' : 2, 'type' : 'button', 'var_name' : 'clearimages' },
            'Download ship images (VERY SLOW!)'     : { 'col' : 2, 'type' : 'button', 'var_name' : 'predownloadShipImages' },
#            'Download gear images (VERY SLOW!)'     : { 'col' : 2, 'type' : 'button', 'var_name' : 'predownloadGearImages' },
#            'Save cache binaries (TEST)'            : { 'col' : 2, 'type' : 'button', 'var_name' : 'cacheSave' },
        }
        self.create_item_block(settingsTopRightFrame, theme=settingsMaintenance)

    def persistentSet(self, choice, var_name, isBoolean=False):
        if var_name is None or var_name == '':
            return

        self.logWriteSimple("self.persistent", '', 2,
                            [var_name, '{}->{}'.format(self.persistent[var_name], choice, 'bool' if isBoolean else '')])

        if isBoolean:
            self.persistent[var_name] = True if choice and choice != 'No' else False
        elif var_name == 'uiScale':
            self.persistent[var_name] = float(choice)
        else:
            self.persistent[var_name] = choice

        self.auto_save()

        if var_name == 'consoleSort':
            # Need to hook the ship frame to take sub-frame updates
            pass
        elif var_name == 'boffSort' or var_name == 'boffSort2':
            self.setupBoffFrame('space', self.backend['shipHtml'])
        elif var_name == 'uiScale':
            self.updateWindowSize(caller='persistentSet-uiScale')
            pass


    def create_item_get_var(self, var_name, store='persistent', fallback=None, boolean=False, boolean_options=None):
        if store == 'build':
            default = self.build[var_name].get() if var_name in self.build else fallback
        else:
            default = self.persistent[var_name] if var_name in self.persistent else fallback
        if boolean:
            if boolean_options is None:
                default = True if default else False
            else:
                default = boolean_options[1] if default else boolean_options[0]
        return default


    def create_item_set_var(self, data, var_name, var_sub_name=None, store='persistent', boolean=False):
        self.logWriteSimple('create_item_set_var', '', 2, [data, var_name, var_sub_name, store, boolean])
        if store == 'backend':
            if boolean:
                data = True if data else False
            if var_name in self.backend:
                if var_sub_name is not None:
                    if var_sub_name in self.backend[var_name]:
                        self.backend[var_name][var_sub_name].set(data)
                else:
                    self.backend[var_name].set(data)
        else:
            self.persistentSet(data, var_name=var_name, isBoolean=boolean)
        self.auto_save_queue()


    def create_item_block(self, parent_frame, theme=None, shape='col', elements=2, row=0, col=0):
        if theme is None or not len(theme):
            return

        item_block_default = {
            'fg': self.theme['button']['fg'],
            'label_fg': self.theme['label']['fg'],
            'bg': self.theme['button']['bg'],
            'abg': self.theme['button']['hover'],
            'label_bg': self.theme['label']['bg'],
            'pad_x': 2,
            'pad_y': 2,
            'highlightthickness': 0,
            'highlightbackground': self.theme['frame']['bg'],
            'sticky': 'nw',
            'font_data': self.font_tuple_create('app'),
            'font_label': self.font_tuple_create('label'),
            'row_weight': 0,
            'col_weight': 0,
            'col': 1,
            'type': 'blank',
            'var_name': None,
            'var_sub_name': None,
            'setting_options': self.yesNo,
            'boolean': False,
            'callback': None,
            'store': 'persistent',
            'image': None,
        }
        default = {**item_block_default, **theme['default']} if 'default' in theme else {**item_block_default}

        i = -1  # count of keys processed
        for title in theme.keys():
            item_theme = {**default, **theme[title]}
            if title == 'default' or \
                    (item_theme['col'] > 1 and not item_theme['var_name']):
                continue
            i += 1
            is_button = True if item_theme['type'] == 'button' or item_theme['type'] == 'button_block' else False
            is_label = True if item_theme['type'] == 'label' or item_theme['type'] == 'blank' or item_theme['type'] == 'title' else False
            create_label = True if is_label or (not is_button and item_theme['col'] > 1) else False

            if item_theme['type'] == 'title':
                item_theme['font_label'] = self.font_tuple_create('title1')
            if item_theme['type'] == 'button':
                item_theme['sticky'] = theme[title]['sticky'] if 'sticky' in theme[title] else 'nwe'
            if item_theme['type'] == 'button_block' or item_theme['type'] == 'optionmenu_block' or item_theme['type'] == 'menu':
                item_theme['sticky'] = theme[title]['sticky'] if 'sticky' in theme[title] else 'nsew'
                item_theme['pad_x'] = theme[title]['pad_x'] if 'pad_x' in theme[title] else 0
                item_theme['pad_y'] = theme[title]['pad_y'] if 'pad_y' in theme[title] else 0
                item_theme['row_weight'] = theme[title]['row_weight'] if 'row_weight' in theme[title] else 1
                item_theme['col_weight'] = theme[title]['col_weight'] if 'col_weight' in theme[title] else 1

            if item_theme['callback'] is None:
                if is_button:
                    item_theme['callback'] = lambda var_name=item_theme['var_name']: self.settingsButtonCallback(type=var_name)
                elif item_theme['type'] == 'optionmenu_block':
                    item_theme['callback'] = lambda choice, var_name=item_theme['var_name']: self.settingsMenuCallback(choice, type=var_name)
                elif item_theme['type'] == 'optionmenu' or item_theme['type'] == 'scale':
                    item_theme['callback'] = lambda choice, var_name=item_theme['var_name'], var_sub_name = item_theme['var_sub_name'], isBoolean=item_theme['boolean'], store=item_theme['store']:self.create_item_set_var(choice, var_name=var_name, var_sub_name=var_sub_name, store=store, boolean=isBoolean)

            row_current = (i * elements) + row if shape == 'col' else row
            col_start = (i * elements) + col if shape == 'row' else col

            if create_label:
                span_label = 1 + (elements - item_theme['col'])
                sticky_label = 'ew' if span_label > 1 else 'e'
                if item_theme['type'] == 'title':
                    sticky_label = 'n'
                label = Label(parent_frame, text='' if item_theme['type'] == 'blank' else title)
                label.configure(fg=item_theme['label_fg'], bg=item_theme['label_bg'], font=font.Font(font=item_theme['font_label']))
                label.grid(row=row_current, column=col_start, columnspan=span_label, sticky=sticky_label, pady=item_theme['pad_y'], padx=item_theme['pad_x'])

            setting_var = ''
            if item_theme['type'] == 'optionmenu' or item_theme['type'] == 'optionmenu_block':
                if item_theme['store'] == 'backend':
                    if item_theme['var_sub_name']:
                        setting_var = self.backend[item_theme['var_name']][item_theme['var_sub_name']]
                    else:
                        setting_var = self.backend[item_theme['var_name']]
                    if item_theme['boolean']:
                        current_as_boolean = bool(setting_var.get())
                        if setting_var.get() != current_as_boolean:
                            setting_var.set(current_as_boolean)
                else:
                    if item_theme['type'] == 'optionmenu_block':
                        setting_data = title
                    elif item_theme['boolean']:
                        setting_data = self.create_item_get_var(item_theme['var_name'], store=item_theme['store'], fallback=False, boolean=True, boolean_options=['No', 'Yes'])
                    else:
                        setting_data = self.create_item_get_var(item_theme['var_name'], store=item_theme['store'], fallback='')

                    setting_var = StringVar(value=setting_data)
                option_frame = OptionMenu(parent_frame, setting_var, *item_theme['setting_options'], command=item_theme['callback'])
            elif item_theme['type'] == 'menu':
                option_frame = Menubutton(parent_frame, text=title, relief='raised')
                option_menu = Menu(option_frame, tearoff=False)
                option_frame['menu'] = option_menu
                for sub_menu in item_theme['setting_options']:
                    sub_command = lambda choice=sub_menu: getattr(self, item_theme['callback'])(choice)
                    option_menu.add_command(label=sub_menu, command=sub_command)
            elif item_theme['type'] == 'scale':
                setting_data = self.create_item_get_var(item_theme['var_name'], store=item_theme['store'], fallback=1.0)
                setting_var = DoubleVar(value=setting_data)
                option_frame = Scale(parent_frame, from_=0.5, to=2.0, digits=2, resolution=0.1, orient='horizontal', variable=setting_var)
                option_frame.configure(command=item_theme['callback'])
            elif is_button:
                option_frame = HoverButton(parent_frame, text=title, fg=item_theme['fg'], bg=item_theme['bg'], activebackground=item_theme['abg'])
                if item_theme['image'] is not None:
                    option_frame.configure(image=item_theme['image'])
                option_frame.configure(command=item_theme['callback'])
            else:
                continue

            if item_theme['type'] != 'blank':
                option_frame.configure(bg=item_theme['bg'], fg=item_theme['fg'])
                option_frame.configure(highlightthickness=item_theme['highlightthickness'], highlightbackground=item_theme['highlightbackground'])
                if item_theme['type'] == 'button_block' or item_theme['type'] == 'optionmenu_block' or item_theme['type'] == 'menu':
                    option_frame.configure(font=font.Font(font=item_theme['font_data']))
                else:
                    option_frame.configure(borderwidth=0, highlightthickness=0, width=9)

                self.build_vars[item_theme['var_name']] = setting_var
                col_option = 0 if is_button or item_theme['type'] == 'optionmenu_block' or item_theme['type'] == 'menu' else 1
                span_option = elements if is_button else 1
                option_frame.grid(row=row_current, column=col_start+col_option, columnspan=span_option, sticky=item_theme['sticky'], pady=item_theme['pad_y'], padx=item_theme['pad_x'])
                parent_frame.grid_rowconfigure(row_current, weight=item_theme['row_weight'])
                parent_frame.grid_columnconfigure(col_start + col_option, weight=item_theme['col_weight'])
                self.logWriteSimple('create', 'item', 5, [row_current, col_start+col_option, span_option, title, item_theme['var_name'], item_theme['type']])


    def logDisplayUpdate(self):
        self.logDisplay.delete('0.0', END)
        self.logDisplay.insert('0.0', self.logFull.get())
        self.logDisplay.yview_pickplace(END)

    def logFullWrite(self, notice, log_only=False):
        self.logFull.set(self.lineTruncate(self.logFull.get()+'\n'+notice))
        if not log_only:
            self.progressBarUpdate(text=notice)

    def logminiWrite(self, notice, level=0):
        if level == 0:
            self.setFooterFrame('', notice)
        if self.settings['debug'] > 0 and self.settings['debug'] >= level:
            self.log_write_stderr('info: '+notice)

    def logWriteBreak(self, title, level=1):
        self.logWrite('=== {:>1} ==='.format(title.upper()), level)

    def logTagClean(self, tag):
        return '{}'.format(tag).strip()

    def logWritePerf(self, title, level=3, run='', tags=None):
        logNote = ''
        if tags:
            for tag in tags:
                logNote = logNote + '[{:>1}]'.format(self.logTagClean(tag))
        self.logWrite('{:16} {:15} {}'.format('{}'.format(run), title, logNote), level, log_only=True)

    def logWriteSimple(self, title, body, level=1, tags=None):
        logNote = ''
        if tags:
            for tag in tags:
                logNote = logNote + '[{:>1}]'.format(self.logTagClean(tag))
        self.logWrite('{:>12} {:>13}: {:>6}'.format(title, body, logNote), level)

    def logWriteTransaction(self, title, body, count, path, level=1, tags=None):
        logNote = ''
        if tags:
            for tag in tags:
                logNote = logNote + '[{:>1}]'.format(self.logTagClean(tag))
        self.logWrite('{:>12} {:>12}: {:>6} {:>1} {:>6}'.format(title, body, str(count), path, logNote), level)

    def logWriteCounter(self, title, body, count, tags=None):
        logNote = ''
        if tags:
            for tag in tags:
                logNote = logNote + '[{:>9}]'.format(self.logTagClean(tag))
        self.logWrite('{:>12} {:>6} count: {:>6} {:>6}'.format(title, body, str(count), logNote), 2)

    def logWrite(self, notice, level=0, log_only=False):
        # Level 0: Default, always added to short log note frame on UI
        # Higher than 0 will not be added to short log note (but will be in the full log)
        # Log levels uses are just suggestions
        # Level 1: Track interactions - network interactions, configuration actions, file transactions
        # Level 2: unconfirmed feature spam -- chatty but not intended to fully retained long term
        # Level 3+: minor detail spam -- any useful long-term diagnostic, the more spammy, the higher
        if level == 0:
            self.setFooterFrame(notice, '')
            self.logFullWrite(notice, log_only=log_only)
        if self.settings['debug'] > 0 and self.settings['debug'] >= level:
            self.log_write_stderr(notice)
            self.logFullWrite(notice, log_only=log_only)

    def log_write_stderr(self, text):
        now = datetime.datetime.now()
        sys.stderr.write('{}: '.format(now))
        sys.stderr.write('{}'.format(text))
        sys.stderr.write('\n')

    def requestWindowUpdateHold(self, count=50):
        if count == 0:
            self.updateOnStep = 5
        else:
            self.updateOnStep = self.updateOnHeavyStep
        self.windowUpdate['hold'] = count

    def requestWindowUpdate(self, type=''):
        if not 'updates' in self.windowUpdate:
            self.windowUpdate = { 'updates': 0, 'requests': 0, 'hold': 0 }
        self.windowUpdate['requests'] += 1

        if type == 'force':
            self.window.update()
            self.windowUpdate['updates'] += 1
        elif self.windowUpdate['hold']:
            # a hold has been called (contains number of updates to wait)
            self.windowUpdate['hold'] -= 1
            return
        elif type == "footerProgressBar":
            self.splashProgressBar.update()
            self.windowUpdate['updates'] += 1
        elif not type:
            self.window.update()
            self.windowUpdate['updates'] += 1
        else:
            return

        # runaway check
        if self.windowUpdate['updates'] % 500 == 0:
            self.logWriteBreak("self.window.update({}): {:4}".format(type, str(self.windowUpdate['updates'])), 3)


    def resetBuildFrames(self, types=None):
        if types is None:
            types = ['skill', 'ground', 'space']
        for type in types:
            self.setupInfoFrame(type)
            self.setupDescFrame(type)
            self.setupHandleFrame(type)
            self.updateTagsFrame(type)

    def setupUIFrames(self):
        defaultFont = font.nametofont('TkDefaultFont')
        defaultFont.configure(family=self.theme['app']['font']['family'], size=self.theme['app']['font']['size'])

        self.containerFrame = Frame(self.window, bg=self.theme['app']['bg'])
        self.containerFrame.pack(fill=BOTH, expand=True)
        self.logoFrame = Frame(self.containerFrame, bg=self.theme['app']['bg'])
        self.logoFrame.pack(fill=X)
        self.menuFrame = Frame(self.containerFrame, bg=self.theme['app']['bg'])
        self.menuFrame.pack(fill=X, padx=15)
        self.verticalFrame = Frame(self.containerFrame, bg=self.theme['app']['bg'], height=self.windowActiveHeight)
        self.verticalFrame.pack(fill='none', side='left')  # Minimum height frame

        # Interior, tabbed frames
        self.spaceBuildFrame = Frame(self.containerFrame, bg=self.theme['frame']['bg'])
        self.groundBuildFrame = Frame(self.containerFrame, bg=self.theme['frame']['bg'])
        self.skillTreeFrame = Frame(self.containerFrame, bg=self.theme['frame']['bg'])
        self.libraryFrame = Frame(self.containerFrame, bg=self.theme['frame']['bg'])
        self.settingsFrame = Frame(self.containerFrame, bg=self.theme['frame']['bg'])
        self.splashFrame = Frame(self.containerFrame, bg=self.theme['frame']['bg'])

        self.focusFrameCallback(type='splash', init=True)
        self.makeSplash()

        self.setupFooterFrame()
        self.setupLogoFrame()
        self.setupMenuFrame()
        self.requestWindowUpdate() #cannot force
        self.precachePreload(limited=(self.args.faststart or self.persistent['fast_start']))

        self.setupLibraryFrame()
        self.setupSettingsFrame()
        for type in ['skill', 'ground', 'space']:
            self.logWriteBreak('Build: {}'.format(type))
            self.setupInitialBuildFrames(type)

        if not self.build_auto_load():
            self.logWriteBreak('Build Frames (no initial load)')
            self.setupCurrentBuildFrames()
            self.resetBuildFrames()
            self.closeSplash()

        self.focusFrameCallback(type=self.args.startuptab)
        self.containerFrame.pack_propagate(False)

    def argParserSetup(self):
        parser = argparse.ArgumentParser(description='A Star Trek Online build tool')
        parser.add_argument('--configfile', type=int, help='Set configuration file (must be .JSON)')
        parser.add_argument('--configfolder', type=int, help='Set configuration folder (contains config file, state file, default library location')
        parser.add_argument('--debug', type=int, help='Set debug level (default: 0)')
        parser.add_argument('--file', type=str, help='File to import on open')
        parser.add_argument('--nofetch', type=str, help='Do not fetch new images')
        parser.add_argument('--allfetch', type=str, help='Retry images every load')
        parser.add_argument('--faststart', type=str, help='EXPERIMENTAL -- skip some items at app load')
        parser.add_argument('--startuptab', type=str, help='space, ground, skill, settings [space is default]')

        self.args = parser.parse_args()

        if self.args.debug is not None:
            self.settings['debug'] = self.args.debug
            self.logWriteSimple('Debug', 'set by arg', 1, tags=[str(self.settings['debug'])])

        if self.args.configfile is not None:
            self.fileConfigName = self.args.configfile

        if self.args.configfolder is not None:
            self.settings['folder']['config'] = self.args.configfolder

    def configFolderLocation(self):
        # This should probably be upgraded to use the appdirs module, adding rudimentary options for the moment
        system = sys.platform
        if os.path.exists(self.settings['folder']['config']):
            # We already have a config folder in the app home directory, use portable mode
            filePath = self.settings['folder']['config']
        elif os.path.exists(self.fileConfigName):
            # We already have a config file in the app home directory, use portable mode
            filePath=''
        elif system == 'win32':
            # (onedrive or documents -- Python intercepts AppData)
            filePathOnedrive = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Documents')
            filePathOnedriveSETS = os.path.join(os.path.expanduser('~'), 'OneDrive', 'Documents', 'SETS')
            filePathDocumentsSETS = os.path.join(os.path.expanduser('~'), 'Documents', 'SETS')
            if sys.getwindowsversion().major < 6:
                # earlier than WinvVista,7+
                filePath = filePathDocumentsSETS
            else:
                # WinVista,7+
                if os.path.exists(filePathOnedrive):
                    filePath = filePathOnedriveSETS
                else:
                    filePath = filePathDocumentsSETS
        elif system == 'darwin':
            # OSX
            filePath = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'SETS')
        else:
            # Unix
            filePath = os.path.join(os.path.expanduser('~'), '.config', 'SETS')

        self.makeFilenamePath(filePath)

        return filePath

    def configFileLocation(self):
        filePath = self.configFolderLocation()

        if os.path.exists(filePath):
            fileName = os.path.join(filePath, self.fileConfigName)
        else:
            fileName = self.fileConfigName

        return fileName

    def makeFilenamePath(self, filePath):
        if not os.path.exists(filePath):
            try:
                os.makedirs(filePath)
                self.logWriteTransaction('makedirs', 'written', '', filePath, 1)
            except:
                self.logWriteTransaction('makedirs', 'failed', '', filePath, 1)

    def getFolderLocation(self, subfolder=None):
        filePath = self.configFolderLocation()

        if subfolder is not None and subfolder in self.settings['folder']:
            filePath = os.path.join(filePath, self.settings['folder'][subfolder])
        self.makeFilenamePath(filePath)

        if not os.path.exists(filePath):
            filePath = ''
            if subfolder in self.settings['folder']:
                filePath = self.settings['folder'][subfolder]

        return filePath


    def getFileLocation(self, type):
        fileArgs = None
        touch_on_access = False
        filePath = self.configFolderLocation()
        fileBase = self.settings[type] if type in self.settings else ''
        if type == 'autosave':
            filePath = self.getFolderLocation('library')
            touch_on_access = True
        elif type == 'state':
            fileBase = self.fileStateName
            touch_on_access = True
        elif type == 'template':
            filePath = self.getFolderLocation('library')
            fileArgs = self.args.file
        elif type == 'cache':
            touch_on_access = True
        else:
            # Invalid option
            return

        if fileArgs is not None and os.path.exists(fileArgs):
            fileName = fileArgs
        else:
            if os.path.exists(filePath):
                fileName = os.path.join(filePath, fileBase)
                if touch_on_access and not os.path.exists(fileName):
                    open(fileName, 'w').close()

            if not os.path.exists(filePath):
                fileName = fileBase

        if type == 'template':
            fileName += '.png' if os.path.exists(fileName+'.png') else '.json'

        return fileName


    def configFileLoad(self):
        # Currently JSON, but ideally changed to a user-commentable format (YAML, TOML, etc)
        configFile = self.configFileLocation()
        if not os.path.exists(configFile):
            configFile = self.fileConfigName

        if os.path.exists(configFile) and os.path.getsize(configFile) > 0:
            self.logWriteTransaction('Config File', 'found', '', configFile, 1)
            with open(configFile, 'r') as inFile:
                try:
                    settingsNew = json.load(inFile)
                    logNote = ' (fields:['+str(len(settingsNew))+'=>'+str(len(self.settings))+']='
                    self.settings.update(settingsNew)
                    logNote = logNote + str(len(self.settings)) + ')'
                    self.logWriteTransaction('Config File', 'loaded', '', configFile, 0, [logNote])
                except:
                    self.logWriteTransaction('Config File', 'load error', '', configFile, 0)

                self.get_debug_current()
        else:
            self.logWriteTransaction('Config File', 'not found or zero size', '', configFile, 0)

    def stateFileLoad(self, init=False):
        # Currently JSON, but ideally changed to a user-commentable format (YAML, TOML, etc)
        configFile = self.getFileLocation('state')

        if os.path.exists(configFile):
            self.logWriteTransaction('State File', 'found', '', configFile, 1)
            with open(configFile, 'r') as inFile:
                try:
                    persistentNew = json.load(inFile)
                except:
                    self.logWriteTransaction('State File', 'load error', '', configFile, 1)
                    return
                logNote = ' (fields:['+str(len(persistentNew))+'=>'+str(len(self.persistent))+']='
                self.persistent.update(persistentNew)
                logNote = logNote + str(len(self.persistent)) + ')'
                self.logWriteTransaction('State File', 'loaded', '', configFile, 0, [logNote])
        else:
            self.logWriteTransaction('State File', 'not found', '', configFile, 1)

        if init:
            self.auto_save()

    def auto_save_queue(self):
        if self.autosaving:
            return

        self.autosaving = True
        self.window.after(self.persistent['autosave_delay'], self.auto_save, 'template')

    def auto_save(self, type='state', quiet=False):
        self.autosaving = True
        if type == 'state' or type == 'all':
            self.save_json(self.getFileLocation('state'), self.persistent, 'State file', quiet)

        if self.persistent['autosave'] and \
                (type == 'template' or type == 'all'):
            # merge partially with update_build_master
            if self.persistent['versioning']:
                if self.buildImport[-1] == self.build:
                    export = self.buildImport
                else:
                    export = self.buildImport + [self.build]
            else:
                export = self.build
            self.save_json(self.getFileLocation('autosave'), export, 'Auto save file', quiet)
        self.autosaving = False

    def save_json(self, file, tree, title, quiet=False):
        try:
            with open(file, "w") as outFile:
                json.dump(tree, outFile)
                self.logWriteTransaction(title, 'saved', '', outFile.name, 5 if quiet else 1)
        except AttributeError:
            self.logWriteTransaction(title, 'save error', '', outFile.name, 1)
            pass

    def build_auto_load(self):
        configFile = self.getFileLocation('autosave')
        autosave_exists = os.path.exists(configFile)
        if autosave_exists:
            autosave_result = self.importByFilename(configFile, autosave=True)
        if not autosave_exists or not autosave_result:
            autosave_result = self.importByFilename(self.getFileLocation('template'))

        return autosave_result

    def init_splash(self):
        self.images['splash_image'] = self.loadLocalImage('sets_loading.PNG', width=self.splashBoxX, height=self.splashBoxY)
        self.splash_image_w = self.images['splash_image'].width()
        self.splash_image_h = self.images['splash_image'].height()

    def init_settings(self):
        """Initialize session settings state"""
        self.session = HTMLSession()
        self.resetInternals()
        self.resetSettings()

        self.splashWindow = None
        self.splashProgressBar = None
        self.splashProgressBarUpdates = 0
        self.splashText = ''
        self.updateOnHeavyStep = 50
        self.logWriteBreak("logStart")
        self.logWriteSimple('CWD', '', 1, tags=[os.getcwd()])
        self.visible_window = 'space'
        self.visible_window_previous = 'space'
        self.build_vars = dict()

        self.resetPersistent()
        self.resetBuild()
        self.resetCache()
        self.resetBackend()


    def exportSettings(self):
        try:
            with filedialog.asksaveasfile(defaultextension=".json",filetypes=[("JSON file","*.json"),("All Files","*.*")]) as outFile:
                json.dump(self.settings, outFile)
                self.logWriteTransaction('Config File', 'saved', os.path.getsize(outFile.name), outFile.name, 0)
        except AttributeError:
            pass

    def setupEmptyImages(self):
        self.emptyImageFaction = dict()
        self.emptyImage = self.fetchOrRequestImage(self.wikiImages+"Common_icon.png", "no_icon")
        self.epicImage = self.fetchOrRequestImage(self.wikiImages+"Epic.png", "Epic")
        self.three_bars = self.loadLocalImage('hamburger_icon.png', width=self.itemBoxX, height=self.itemBoxY_default / 2)

        width = self.imageBoxX * 2 / 3
        height = self.imageBoxY * 2 / 3
        self.emptyImageFaction['federation'] = self.fetchOrRequestImage(self.wikiImages+"Federation_Emblem.png", "federation_emblem", width, height)
        self.emptyImageFaction['tos federation'] = self.fetchOrRequestImage(self.wikiImages+"TOS_Federation_Emblem.png", "tos_federation_emblem", width, height)
        self.emptyImageFaction['klingon'] = self.fetchOrRequestImage(self.wikiImages+"Klingon_Empire_Emblem.png", "klingon_emblem", width, height)
        self.emptyImageFaction['romulan'] = self.fetchOrRequestImage(self.wikiImages+"Romulan_Republic_Emblem.png", "romulan_emblem", width, height)
        self.emptyImageFaction['dominion'] = self.fetchOrRequestImage(self.wikiImages+"Dominion_Emblem.png", "dominion_emblem", width, height)

    def precacheDownloads(self):
        self.infoboxes = self.fetchOrRequestJson(SETS.item_query, "infoboxes")
        self.traits = self.fetchOrRequestJson(SETS.trait_query, "traits")
        self.shiptraits = self.fetchOrRequestJson(SETS.ship_trait_query, "starship_traits")
        self.doffs = self.fetchOrRequestJson(SETS.doff_query, "doffs")
        self.ships = self.fetchOrRequestJson(SETS.ship_query, "ship_list")
        self.reputations = self.fetchOrRequestJson(SETS.reputation_query, "reputations")
        self.trayskills = self.fetchOrRequestJson(SETS.trayskill_query, "trayskills")
        self.factions = self.fetchOrRequestJson(SETS.faction_query, "factions")

        self.r_boffAbilities = self.fetchOrRequestHtml(self.wikihttp+"Bridge_officer_and_kit_abilities", "boff_abilities")

        #r_species = self.fetchOrRequestHtml(self.wikihttp+"Category:Player_races", "species")
        #self.speciesNames = [e.text for e in r_species.find('#mw-pages .mw-category-group .to_hasTooltip') if 'Guide' not in e.text and 'Player' not in e.text]


    def setupGeometry(self, default=False):
        # Check that it's not off-screen?
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        if self.windowWidth + self.window_topleft_x > screen_width:
            self.window_topleft_x = 0
        if self.windowHeight + self.window_topleft_y > screen_height:
            self.window_topleft_y = 0

        if not default and 'geometry' in self.persistent and self.persistent['geometry']:
                if self.persistent['geometry'] == '-fullscreen':
                    self.window.attributes(self.persistent['geometry'], True)
                    self.updateWindowSize(caller='setupGeometry', no_geometry=True)
                elif self.persistent['geometry'] == 'zoomed':
                    self.window.state(self.persistent['geometry'])
                else:
                    self.window.geometry(self.persistent['geometry'])
        else:
                self.window.geometry("{}x{}+{}+{}".format(self.windowWidth, self.windowHeight, self.window_topleft_x, self.window_topleft_y))


    def perf(self, name, type='start', loud=False):
        now = datetime.datetime.now()
        if not name in self.perf_store:
            self.perf_store[name] = dict()

        if not name in self.persistent['perf']:
            self.persistent['perf'][name] = []
        if isinstance(self.persistent['perf'][name], dict):
            self.persistent['perf'][name] = []

        self.perf_store[name][type] = now

        if type == 'stop':
            if not 'start' in self.perf_store[name]:
                self.perf_store[name]['start'] = now
            start = self.perf_store[name]['start']
            run = now - start
            perf_slice = slice(-1 * self.settings['perf_to_retain'], None)
            self.persistent['perf'][name][perf_slice] += ['{}'.format(run)]

            if loud:
                self.logWritePerf(name, run=run, tags=[type, now])
            else:
                self.logWritePerf(name, run=run)
            return run
        else:
            if loud:
                self.logWritePerf(name, tags=[type, now])
            return now

    def makeSplash(self, close=False):
        self.focusFrameCallback(type='splash')
        self.splash_window_interior(self.splashFrame)
        self.requestWindowUpdate(type='force')
        if not close:
            self.perf('splash')
            self.requestWindowUpdateHold(0)
            self.splashProgressBarUpdates = 0
            self.splashProgressBar.start()

    def closeSplash(self):
        self.focusFrameCallback(type='return')

    def makeSplashWindow(self, close=False):
        if self.splashWindow is not None:
            try:
                self.splashWindow.focus_set()
                return
            except:
                self.splashWindow = None

        if self.splashWindow is None:
            self.splashWindow = self.makeSubWindow('Sets ({})'.format(self.version), 'splash', close=close)

        if not close:
            self.perf('splash')
            self.requestWindowUpdateHold(0)
            self.splashProgressBarUpdates = 0
            self.splashProgressBar.start()


    def removeSplashWindow(self):
        if self.splashWindow is not None:
            self.splashWindow.destroy()
            self.perf('splash', 'stop')
            self.splashWindow = None
            self.splashProgressBar = None


    def progressBarUpdate(self, weight=1, text=None):
        # weight denotes how much progress that item is
        if self.splashProgressBar is None or self.visible_window != 'splash':
            return
        max_weight = 5
        if weight > max_weight:
            weight = max_weight
        self.splashProgressBarUpdates += weight

        # modulo to reduce time / flashing UI spent on updating
        if text is not None:
            self.splashText.set(text[:300])
        if self.splashProgressBarUpdates % self.updateOnStep == 0 or self.splashProgressBarUpdates % self.updateOnStep + weight > self.updateOnHeavyStep:
            self.splashProgressBar.step(weight)
            self.requestWindowUpdate()
            pass

    def setupUIScaling(self,event=None):
        scale = float(self.persistent['uiScale']) if 'uiScale' in self.persistent else 1.0
        screen_width = self.window.winfo_screenwidth()
        if screen_width < self.windowWidth:
            scale = float('{:.2f}'.format(screen_width / self.windowWidth))
            self.logWriteSimple('setupUIScaling', 'scale change', 1, '{}'.format(scale))
        self.factor = ( self.dpi / 96 )  # May need to be / 72, but the current framing doesn't work at /72 yet.

        if self.factor != 1:  # If the framing gets fixed at /72, this should be remove-able
            scale *= self.factor
            self.window.call('tk', 'scaling', scale)  # Should already be factor modified, so we have to keep the factor
        else:
            # If dpi / framing are adjusted, this should happen with a scaling adjustment
            self.itemBoxX = self.itemBoxX_default * scale
            self.itemBoxY = self.itemBoxY_default * scale

        self.os_system = platform.system()
        self.os_release = platform.release()
        if self.os_system == 'Windows' and self.os_release == 10 and sys.getwindowsversion().build >= 22000:
            self.os_release = 11

        self.logminiWrite('{} | {} {} @ {}x{} | {}x{} (x{}) {}dpi'.format(self.version, self.os_system, self.os_release, self.window.winfo_screenwidth(), self.window.winfo_screenheight(), self.windowWidth, self.windowHeight, scale, self.dpi))


    def updateWindowSize(self, caller='', init=False, no_geometry=False):
        if init:
            self.itemBoxX = self.itemBoxX_default = 32
            self.itemBoxY = self.itemBoxY_default = 42
            self.window_topleft_x = self.window_topleft_x_default = 100  # Window top left corner
            self.window_topleft_y = self.window_topleft_y_default = 100
            self.dpi = round(self.window.winfo_fpixels('1i'), 0)

            self.windowBarHeight = 34
            self.logoHeight = 134
            self.otherHeight = 13  # button bar, anything else?
            self.windowWidth = self.windowWidthDefault = 1920
            self.windowHeight = self.windowHeightDefault = 840
            self.window.minsize(int(self.windowWidth * 2 / 3),int(self.windowHeight * 2 / 3))
        else:
            previous_width = self.windowWidth
            previous_height = self.windowHeight
            previous_active_height = self.windowActiveHeight
            previous_x = self.window_topleft_x
            previous_y = self.window_topleft_y
            self.windowWidth = self.window.winfo_width()
            self.windowHeight = self.window.winfo_height()
            self.window_topleft_x = self.window.winfo_x()
            self.window_topleft_y = self.window.winfo_y()

        self.windowActiveHeight = self.windowHeight - (self.windowBarHeight + self.logoHeight + self.otherHeight)
        self.window_outside_frame_minimum = int((self.windowWidth - 100) / 5)
        self.imageBoxX = self.window_outside_frame_minimum
        self.imageBoxY = int(self.window_outside_frame_minimum * 7 / 10)

        self.splashBoxX = self.windowWidth * 2 / 3
        self.splashBoxY = self.windowActiveHeight * 2 / 3

        self.setupUIScaling()
        if not no_geometry:
            self.setupGeometry()

        if init:
            return

        if previous_width != self.windowWidth or \
                previous_height != self.windowHeight or \
                previous_active_height != self.windowActiveHeight or \
                previous_x != self.window_topleft_x or \
                previous_y != self.window_topleft_y:
             self.logWriteSimple('***WINDOW CHANGE', '{}x{}'.format(self.windowWidth, self.windowHeight), 2,
                        [self.windowActiveHeight, self.window_topleft_x, self.window_topleft_y, caller])

    def resource_path(self, relative_path, quiet=True):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.abspath(__file__))

        full_path = os.path.join(base_path, relative_path)
        if not quiet:
            self.log_write_stderr('Local path: {}'.format(full_path))
        return full_path

    def init_window(self):
        self.window = Tk()
        self.window.iconphoto(False, PhotoImage(file=self.resource_path('local/icon.PNG', quiet=False)))
        self.window.title("STO Equipment and Trait Selector")

    def __init__(self) -> None:
        """Main setup function"""
        self.init_window()
        self.init_settings()

        self.logWriteBreak('CONFIG')
        self.argParserSetup()  # First for location overrides
        self.stateFileLoad(init=True)
        self.configFileLoad()  # Third to override persistent
        self.precache_theme_fonts()  # Fourth in case of new theme from configs
        self.updateWindowSize(init=True)

        self.logWriteBreak('PREP')
        self.init_splash()
        self.logWriteSimple('CWD', '', 1, tags=[os.getcwd()])
        self.setupEmptyImages()
        # self.precacheDownloads()

        self.logWriteBreak('UI BUILD')
        self.setupUIFrames()

    def run(self):
        self.window.mainloop()

SETS().run()
