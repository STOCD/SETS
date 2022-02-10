from textwrap import fill
from tkinter import *
from tkinter import filedialog
from tkinter import font
from requests.models import requote_uri
from requests_html import Element, HTMLSession, HTML
from PIL import Image, ImageTk, ImageGrab, PngImagePlugin
import os, requests, json, re, datetime, html, urllib.parse, ctypes, sys, argparse
import numpy as np

CLEANR = re.compile('<.*?>') 

"""This section will improve display, but may require sizing adjustments to activate"""
if sys.platform.startswith('win'):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2) # windows version >= 8.1
    except:
        ctypes.windll.user32.SetProcessDPIAware() # windows version <= 8.0
    
class SETS():
    """Main App Class"""

    #query for ship cargo table on the wiki
    ship_query = "https://sto.fandom.com/wiki/Special:CargoExport?tables=Ships&&fields=_pageName%3DPage%2Cname%3Dname%2Cimage%3Dimage%2Cfc%3Dfc%2Ctier%3Dtier%2Ctype__full%3Dtype%2Chull%3Dhull%2Chullmod%3Dhullmod%2Cshieldmod%3Dshieldmod%2Cturnrate%3Dturnrate%2Cimpulse%3Dimpulse%2Cinertia%3Dinertia%2Cpowerall%3Dpowerall%2Cpowerweapons%3Dpowerweapons%2Cpowershields%3Dpowershields%2Cpowerengines%3Dpowerengines%2Cpowerauxiliary%3Dpowerauxiliary%2Cpowerboost%3Dpowerboost%2Cboffs__full%3Dboffs%2Cfore%3Dfore%2Caft%3Daft%2Cequipcannons%3Dequipcannons%2Cdevices%3Ddevices%2Cconsolestac%3Dconsolestac%2Cconsoleseng%3Dconsoleseng%2Cconsolessci%3Dconsolessci%2Cuniconsole%3Duniconsole%2Ct5uconsole%3Dt5uconsole%2Cexperimental%3Dexperimental%2Csecdeflector%3Dsecdeflector%2Changars%3Dhangars%2Cabilities__full%3Dabilities%2Cdisplayprefix%3Ddisplayprefix%2Cdisplayclass%3Ddisplayclass%2Cdisplaytype%3Ddisplaytype%2Cfactionlede%3Dfactionlede&&order+by=`_pageName`%2C`name`%2C`image`%2C`fc`%2C`faction__full`&limit=2500&format=json"
    #query for ship equipment cargo table on the wiki
    item_query = 'https://sto.fandom.com/wiki/Special:CargoExport?tables=Infobox&&fields=_pageName%3DPage%2Cname%3Dname%2Crarity%3Drarity%2Ctype%3Dtype%2Cboundto%3Dboundto%2Cboundwhen%3Dboundwhen%2Cwho%3Dwho%2Chead1%3Dhead1%2Chead2%3Dhead2%2Chead3%3Dhead3%2Chead4%3Dhead4%2Chead5%3Dhead5%2Chead6%3Dhead6%2Chead7%3Dhead7%2Chead8%3Dhead8%2Chead9%3Dhead9%2Csubhead1%3Dsubhead1%2Csubhead2%3Dsubhead2%2Csubhead3%3Dsubhead3%2Csubhead4%3Dsubhead4%2Csubhead5%3Dsubhead5%2Csubhead6%3Dsubhead6%2Csubhead7%3Dsubhead7%2Csubhead8%3Dsubhead8%2Csubhead9%3Dsubhead9%2Ctext1%3Dtext1%2Ctext2%3Dtext2%2Ctext3%3Dtext3%2Ctext4%3Dtext4%2Ctext5%3Dtext5%2Ctext6%3Dtext6%2Ctext7%3Dtext7%2Ctext8%3Dtext8%2Ctext9%3Dtext9&&order+by=%60_pageName%60%2C%60name%60%2C%60rarity%60%2C%60type%60%2C%60boundto%60&limit=5000&format=json'
    #query for personal and reputation trait cargo table on the wiki
    trait_query = "https://sto.fandom.com/wiki/Special:CargoExport?tables=Traits&&fields=_pageName%3DPage%2Cname%3Dname%2Cchartype%3Dchartype%2Cenvironment%3Denvironment%2Ctype%3Dtype%2Cisunique%3Disunique%2Cmaster%3Dmaster%2Cdescription%3Ddescription%2Crequired__full%3Drequired%2Cpossible__full%3Dpossible&&order+by=%60_pageName%60%2C%60name%60%2C%60chartype%60%2C%60environment%60%2C%60type%60&limit=2500&format=json"
    ship_trait_query ="https://sto.fandom.com/wiki/Special:CargoExport?tables=Mastery&fields=Mastery._pageName,Mastery.trait,Mastery.traitdesc,Mastery.trait2,Mastery.traitdesc2,Mastery.trait3,Mastery.traitdesc3,Mastery.acctrait,Mastery.acctraitdesc&limit=1000&offset=0&format=json"
    #query for DOFF types and specializations
    doff_query =    "https://sto.fandom.com/wiki/Special:CargoExport?tables=Specializations&fields=Specializations.name,Specializations.shipdutytype,Specializations.department,Specializations.description,Specializations.powertype,Specializations.white,Specializations.green,Specializations.blue,Specializations.purple,Specializations.violet,Specializations.gold&order+by=Specializations.name&limit=1000&offset=0&format=json"

    itemBoxX = 25
    itemBoxY = 35

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

    def fetchOrRequestHtml(self, url, designation):
        """Request HTML document from web or fetch from local cache"""
        cache_base = "cache"
        if not os.path.exists(cache_base):
            os.makedirs(cache_base)
        filename = os.path.join(*filter(None, [cache_base, designation]))+".html"
        if os.path.exists(filename):
            modDate = os.path.getmtime(filename)
            interval = datetime.datetime.now() - datetime.datetime.fromtimestamp(modDate)
            if interval.days < 7:
                with open(filename, 'r', encoding='utf-8') as html_file:
                    s = html_file.read()
                    return HTML(html=s, url = 'https://sto.fandom.com/')
        r = self.session.get(url)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'w', encoding="utf-8") as html_file:
            html_file.write(r.text)
            self.logWrite('CACHE STORE: '+designation+' -- '+str(os.path.getsize(filename))+' bytes')
        return r.html

    def fetchOrRequestJson(self, url, designation):
        """Request HTML document from web or fetch from local cache specifically for JSON formats"""
        cache_base = "cache"
        if not os.path.exists(cache_base):
            os.makedirs(cache_base)
        filename = os.path.join(*filter(None, [cache_base, designation]))+".json"
        if os.path.exists(filename):
            modDate = os.path.getmtime(filename)
            interval = datetime.datetime.now() - datetime.datetime.fromtimestamp(modDate)
            if interval.days < 7:
                with open(filename, 'r', encoding='utf-8') as json_file:
                    json_data = json.load(json_file)
                    return json_data
        r = requests.get(url)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'w') as json_file:
            json.dump(r.json(),json_file)
            self.logWrite('CACHE STORE: '+designation+' -- '+str(os.path.getsize(filename))+' bytes')
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
    
    def fetchOrRequestImage(self, url, designation, width = None, height = None):
        """Request image from web or fetch from local cache"""
        cache_base = "images"
        designation.replace("/", "_") # Missed by the path sanitizer
        designation = self.filePathSanitize(designation) # Probably should move to pathvalidate library
        if not os.path.exists(cache_base):
            os.makedirs(cache_base)
        extension = "jpeg" if "jpeg" in url or "jpg" in url else "png"
        filename = os.path.join(*filter(None, [cache_base, designation]))+'.'+extension
        if os.path.exists(filename):
            image = Image.open(filename)
            if(width is not None):
                image = image.resize((width,height),Image.ANTIALIAS)
            return ImageTk.PhotoImage(image)
        if designation in self.imagesFail and self.imagesFail[designation]:
            # Previously failed this session, do not attempt download again until next run
            return self.emptyImage
        # No existing image, no record of failure -- attempt to download
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        self.logWrite('fetch : '+url, 1)
        img_request = requests.get(url)
        img_data = img_request.content
        self.logWrite('fetch : response:'+str(img_request.status_code)+' size:'+str(img_request.headers.get('Content-Length')), 1)
        if not img_request.ok:
            url2 = url.replace('Q%27s_Ornament%3A_', '')
            if "(Federation)" in url:
                url2 = re.sub('_\(Federation\)', '', url2)
            if url2 is not url:
                self.logWrite('fetch2: '+url2, 1)
                img_request = requests.get(url2)
                img_data = img_request.content
                self.logWrite('fetch2: response:'+str(img_request.status_code)+' size:'+str(img_request.headers.get('Content-Length')), 1)
        if not img_request.ok:
            # No response on icon grab, mark for no downlaad attempt till restart
            self.imagesFail[designation] = 1
            return self.emptyImage
        with open(filename, 'wb') as handler:
            handler.write(img_data)
        if os.path.exists(filename):
            logNote = str(os.path.getsize(filename))+' bytes'
        else:
            logNote = 'no file'
        self.logWrite('IMAGE STORE: '+filename+' -- '+logNote, 1)
        image = Image.open(filename)
        if(width is not None):
            image = image.resize((width,height),Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)

    def deWikify(self, textBlock, leaveHtml=False):
        textBlock = html.unescape(html.unescape(textBlock))
        if not leaveHtml:
            textBlock = re.sub(CLEANR, '', textBlock)
        textBlock.replace('&#34;', '"')
        textBlock.replace('&#39;', '\'')
        textBlock.replace('&#91;', '[')
        textBlock.replace('&#93;', ']')
        # clean up wikitext
        #self.logWrite(textBlock, 1)
        return textBlock
    
    def loadLocalImage(self, filename, width = None, height = None):
        """Request image from web or fetch from local cache"""
        cache_base = "local"
        if not os.path.exists(cache_base):
            os.makedirs(cache_base)
        filename = os.path.join(*filter(None, [cache_base, filename]))
        if os.path.exists(filename):
            image = Image.open(filename)
            if(width is not None):
                image = image.resize((width,height),Image.ANTIALIAS)
            return ImageTk.PhotoImage(image)
        return self.emptyImage

    def getShipFromName(self, requestHtml, shipName):
        """Find cargo table entry for given ship name"""
        for e in range(len(requestHtml)):
            if requestHtml[e]["Page"] == shipName:
                ship_list = requestHtml[e]
        return [] if isinstance(ship_list, int) else ship_list

    def getTierOptions(self, tier):
        """Get possible tier options from ship tier string"""
        return ['T5', 'T5-U', 'T5-X'] if int(tier) == 5 else ['T6', 'T6-X'] if int(tier) == 6 else ['T'+str(tier)]

    def setVarAndQuit(self, e, name, image, v, win):
        """Helper function to set variables from within UI callbacks"""
        v['item'] = name
        v['image'] = image
        win.destroy()

    def makeRedditTable(self, c0, c1, c2):
        result = '**{0}** | **{1}** | **{2}**\n'.format(c0[0],c1[0],c2[0])
        result = result + ":--- | :--- | :---\n"
        for i in range(1,len(c0)):
            c0[i] = c0[i] if c0[i] is not None else '&nbsp;'
            c1[i] = c1[i] if c1[i] is not None else '&nbsp;'
            c2[i] = c2[i] if c2[i] is not None else '&nbsp;'
            result = result + "{0} | {1}| {2}\n".format(c0[i],c1[i],c2[i])
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
        name = re.sub(r"(∞.*)|(Mk X.*)|(\[.*\].*)|(MK X.*)|(-S$)", '', name).strip()
        return name

    def logWriteCounter(self, title, body, count, tags=[]):
        logNote = ''
        if len(tags):
            for tag in tags:
                logNote = logNote + '{:>7}'.format('['+tag+']')
        self.logWrite('{:>12} {:>6} item count: {:>4} {:>6}'.format(title, body, str(count), logNote), 2)

    def precacheEquipment(self, keyPhrase):
        """Populate in-memory cache of ship equipment lists for faster loading"""
        if keyPhrase in self.backend['cacheEquipment']:
            return self.backend['cacheEquipment'][keyPhrase]
        phrases = [keyPhrase] + (["Ship Weapon"] if "Weapon" in keyPhrase and "Ship" in keyPhrase else ["Universal Console"] if "Console" in keyPhrase else [])
        if "Kit Frame" in keyPhrase:
            equipment = [item for item in self.infoboxes if "Kit" in item['type'] and not "Template Demo Kit" in item['type'] and not 'Module' in item['type']]
        else:
            equipment = self.searchJsonTable(self.infoboxes, "type", phrases)
        self.backend['cacheEquipment'][keyPhrase] = {self.sanitizeEquipmentName(equipment[item]["name"]): equipment[item] for item in range(len(equipment))}
        if 'Hangar' in keyPhrase:
            self.backend['cacheEquipment'][keyPhrase] = {key:self.backend['cacheEquipment'][keyPhrase][key] for key in self.backend['cacheEquipment'][keyPhrase] if 'Hangar - Advanced' not in key and 'Hangar - Elite' not in key}

        self.logWriteCounter('Equipment', '(json)', len(self.backend['cacheEquipment'][keyPhrase]), [keyPhrase])

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

    def fetchModifiers(self):
        """Fetch equipment modifiers"""
        if self.backend['modifiers'] is None:
            modPage = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Modifier", "modifiers").find("div.mw-parser-output", first=True).html
            mods = re.findall(r"(<td.*?>(<b>)*\[.*?\](</b>)*</td>)", modPage)
            self.backend['modifiers'] = list(set([re.sub(r"<.*?>",'',mod[0]) for mod in mods]))
        self.logWriteCounter('Modifiers', '(json)', len(self.backend['modifiers']))
        return self.backend['modifiers']
        
    def precacheShips(self):
        self.shipNames = [e["Page"] for e in self.r_ships]
        self.logWriteCounter('Ships', '(json)', len(self.shipNames), ['space'])

    def precacheDoffs(self, keyPhrase):
        """Populate in-memory cache of doff lists for faster loading"""
        if keyPhrase in self.backend['cacheDoffs']:
            return self.backend['cacheDoffs'][keyPhrase]
            
        phrases = [keyPhrase]
        doffMatches = self.searchJsonTable(self.doffs, "shipdutytype", phrases)

        self.backend['cacheDoffs'][keyPhrase] = {self.deWikify(doffMatches[item]['name'])+str(doffMatches[item]['powertype']): doffMatches[item] for item in range(len(doffMatches))}
        self.backend['cacheDoffNames'][keyPhrase] = {self.deWikify(doffMatches[item]['name']): '' for item in range(len(doffMatches))}
        self.logWriteCounter('DOFF', '(json)', len(self.backend['cacheDoffs'][keyPhrase]), [keyPhrase])
        self.logWriteCounter('DOFF names', '(json)', len(self.backend['cacheDoffNames'][keyPhrase]), [keyPhrase])

    def precacheShipTraitSingle(self, name, desc):
        if not name in self.backend['cacheShipTraits']:
            self.backend['cacheShipTraits'][name] = self.deWikify(desc)
            self.shipTraitsWithImages.append((name,self.imageFromInfoboxName(name)))
            self.logWrite('precacheShipTrait: '+name, 5)

    def precacheShipTraits(self):
        """Populate in-memory cache of ship traits for faster loading"""
        if 'cacheShipTraits' in self.backend and len(self.backend['cacheShipTraits']) > 0:
            return self.backend['cacheShipTraits']
            
        for item in list(self.shiptraits):
            if 'trait' in item and len(item['trait']):
                self.precacheShipTraitSingle(item['trait'], item['traitdesc'])
            if 'trait2' in item and len(item['trait2']):
                self.precacheShipTraitSingle(item['trait2'], item['traitdesc2'])
            if 'trait3' in item and len(item['trait3']):
                self.precacheShipTraitSingle(item['trait3'], item['traitdesc3'])
            if 'acctrait' in item and len(item['acctrait']):
                self.precacheShipTraitSingle(item['acctrait'], item['acctraitdesc'])

        for item in list(self.traits):
            if 'type' in item and item['type'].lower() == 'starship':
                self.precacheShipTraitSingle(item['name'], item['description'])

        self.logWriteCounter('Ship Trait', '(json)', len(self.backend['cacheShipTraits']), ['space'])
 
    def precacheTraitSingle(self, name, desc, environment, type):
        if type == 'recruit':
            return
        if type != 'reputation' and type != 'activereputation' and type != 'Starship':
            type = "personal"
            
        if not environment in self.backend['cacheTraits']:
            self.backend['cacheTraits'][environment] = dict()

        if not type in self.traitsWithImages:
            self.traitsWithImages[type] = dict()
        if not environment in self.traitsWithImages[type]:
            self.traitsWithImages[type][environment] = []
            
        if not name in self.backend['cacheTraits'][environment]:
            self.backend['cacheTraits'][environment][name] = self.deWikify(desc)

            self.traitsWithImages[type][environment].append((name,self.imageFromInfoboxName(name)))
            self.logWrite('precacheTrait: ['+type+']['+environment+'] -- '+name+' -- |'+str(len(desc))+'|', 4) 
        
    def precacheTraits(self):
        """Populate in-memory cache of traits for faster loading"""

        if 'cacheTraits' in self.backend and 'space' in self.backend['cacheTraits']:
            return self.backend['cacheTraits']
        
        for item in list(self.traits):
            if not 'chartype' in item or item['chartype'] != 'char':
                continue
            if 'type' in item and 'name' in item and 'description' in item and 'environment' in item:
                self.precacheTraitSingle(item['name'], item['description'], item['environment'], item['type'])
        
        for type in self.traitsWithImages:
            for environment in self.traitsWithImages[type]:
                self.logWriteCounter('Trait', '(json)', len(self.traitsWithImages[type][environment]), [environment, type])

    def setListIndex(self, list, index, value):
        print(value)
        list[index] = value

    def imageFromInfoboxName(self, name, width=None, height=None, suffix='_icon'):
        """Translate infobox name into wiki icon link"""
        width = self.itemBoxX if width is None else width
        height = self.itemBoxY if height is None else height
        try:
            return self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/"+urllib.parse.quote(html.unescape(name.replace(' ', '_')))+suffix+".png", name,width,height)
        except:
            return self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/Common_icon.png", "no_icon",width,height)

    def copyBackendToBuild(self, key):
        """Helper function to copy backend value to build dict"""
        self.build[key] = self.backend[key].get()

    def copyBuildToBackend(self, key):
        """Helper function to copy build value to backend dict"""
        if key in self.build:
            self.backend[key].set(self.build[key])

    def clearBuild(self):
        """Initialize new build state"""
        # VersionJSON Should be updated when JSON format changes, currently number-as-date-with-hour in UTC
        self.versionJSONminimum = 0
        self.versionJSON = 2022020203
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
            'career': 'Tactical',
            'species': 'Alien',
            'ship': '',
            'specPrimary': '',
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
            'eliteCaptain': 0,
            'doffs': {'space': [None] * 6 , 'ground': [None] * 6},
            'tags': dict(),
            'skills': [[], [], [], [], []]
        }

    def clearBackend(self):
        self.logWrite("=== clearBackend ===", 4)
        self.backend = {
                        "career": StringVar(self.window), "species": StringVar(self.window), "playerName": StringVar(self.window),
                        "specPrimary": StringVar(self.window), "specSecondary": StringVar(self.window),
                        "ship": StringVar(self.window), "tier": StringVar(self.window), "playerShipName": StringVar(self.window),
                        "playerShipDesc": StringVar(self.window), "playerDesc": StringVar(self.window),
                        'cacheEquipment': dict(), "shipHtml": None, 'modifiers': None, "shipHtmlFull": None, "eliteCaptain": IntVar(self.window), 'cacheDoffs': dict(), 'cacheDoffNames': dict(), 'cacheShipTraits': dict(), 'cacheTraits': dict(), 'cacheBoffAbilities': dict(), 'cacheBoffTooltips': dict(),
                        "skillLabels": dict(), 'skillNames': [[], [], [], [], []], 'skillCount': 0
            }
        self.traitsWithImages = dict()
        self.boffAbilitiesWithImages = dict()
        self.shipTraitsWithImages = []
        self.persistentToBackend()

    def hookBackend(self):
        self.backend['playerShipName'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('playerShipName'))
        self.backend['career'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('career'))
        self.backend['species'].trace_add('write', lambda v,i,m:self.speciesUpdateCallback())
        self.backend['specPrimary'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('specPrimary'))
        self.backend['specSecondary'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('specSecondary'))
        self.backend['tier'].trace_add('write', lambda v,i,m:self.setupSpaceBuildFrames())
        self.backend['eliteCaptain'].trace_add('write', lambda v,i,m:self.setupSpaceBuildFrames())
        self.backend['eliteCaptain'].trace_add('write', lambda v,i,m:self.setupGroundBuildFrames())
        self.backend['ship'].trace_add('write', self.shipMenuCallback)

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

    def pickerGui(self, title, itemVar, items_list, top_bar_functions=None):
        """Open a picker window"""
        pickWindow = Toplevel(self.window)
        pickWindow.title(title)
        windowheight = self.window.winfo_height() - 100
        windowwidth = int(self.window.winfo_width() / 6)
        if windowheight < 400:
            windowheight = 400
        if windowwidth < 240:
            windowwidth = 240
        pickWindow.geometry(str(windowwidth)+"x"+str(windowheight))
        origVar = dict()
        for key in itemVar:
            origVar[key] = itemVar[key]
        pickWindow.protocol('WM_DELETE_WINDOW', lambda:self.pickerCloseCallback(pickWindow,origVar,itemVar))
        container = Frame(pickWindow)
        content = dict()
        if top_bar_functions is not None:
            for func in top_bar_functions:
                func(container, itemVar, content)
        canvas = Canvas(container)
        scrollbar = Scrollbar(container, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        startY = canvas.yview()[0]
        container.bind("<<ResetScroll>>", lambda event: canvas.yview_moveto(startY))
        container.pack(fill=BOTH, expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side=RIGHT,fill=Y)

        clearSlotButton = Button(scrollable_frame, text='Clear Slot', padx=5, bg='#3a3a3a',fg='#b3b3b3')
        clearSlotButton.grid(row=0, column=0, sticky='nsew')
        clearSlotButton.bind('<Button-1>', lambda e,name='X',image=self.emptyImage,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,image,v,win))

        i = 1
        try:
            items_list.sort()
        except:
            self.logWrite('=== TRY_EXCEPT pickerGUI: item_list.sort() failed in '+title, 3)
        for name,image in items_list:
            frame = Frame(scrollable_frame, relief='ridge', borderwidth=1)
            label = Label(frame, image=image)
            label.grid(row=0, column=0, sticky='nsew')
            label.bind('<Button-1>', lambda e,name=name,image=image,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,image,v,win))
            label.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
            label = Label(frame, text=name, wraplength=windowwidth-40, justify=LEFT)
            label.grid(row=0, column=1, sticky='nsew')
            label.bind('<Button-1>', lambda e,name=name,image=image,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,image,v,win))
            label.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
            frame.grid(row=i, column=0, sticky='nsew')
            frame.bind('<Button-1>', lambda e,name=name,image=image,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,image,v,win))
            frame.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
            content[name] = (frame, i, 0)
            i = i + 1
        pickWindow.wait_visibility()    #Implemented for Linux
        pickWindow.grab_set()
        pickWindow.wait_window()
        return itemVar

    def pickerCloseCallback(self, window, origVar, currentVar):
        for key in origVar:
            currentVar[key] = origVar[key]
        window.destroy()

    def itemLabelCallback(self, e, canvas, img, i, key, args):
        """Common callback for ship equipment labels"""
        self.precacheEquipment(args[0])
        itemVar = {"item":'',"image":self.emptyImage, "rarity": self.persistent['rarityDefault'], "mark": self.persistent['markDefault'], "modifiers":['']}
        items_list = [ (item.replace(args[2], ''), self.imageFromInfoboxName(item)) for item in list(self.backend['cacheEquipment'][args[0]].keys())]
        item = self.pickerGui(args[1], itemVar, items_list, [self.setupSearchFrame, self.setupRarityFrame])
        if 'item' in item and len(item['item']):
            if item['item'] == 'X':
                item['item'] = ''
                canvas.itemconfig(img[0],image=self.emptyImage)
                canvas.itemconfig(img[1],image=self.emptyImage)
                self.build[key][i] = item
                self.backend['i_'+key][i] = [self.emptyImage, self.emptyImage]
            else:
                if 'rarity' in self.backend['cacheEquipment'][args[0]][item['item']]:
                    rarityDefaultItem = self.backend['cacheEquipment'][args[0]][item['item']]['rarity']
                else:
                    rarityDefaultItem = self.rarities[0]
                if 'rarity' not in item or item['item']=='' or item['rarity']=='':
                    item['rarity'] = rarityDefaultItem
                image1 = self.imageFromInfoboxName(item['rarity'])
                canvas.itemconfig(img[0],image=item['image'])
                canvas.itemconfig(img[1],image=image1)
                environment = 'space'
                if len(args) >= 4:
                    environment = args[3]
                canvas.bind('<Enter>', lambda e,item=item:self.setupInfoboxFrame(item, args[0], environment))
                self.build[key][i] = item
                self.backend['i_'+key][i] = [item['image'], image1]
                item.pop('image')

    def traitLabelCallback(self, e, canvas, img, i, key, args):
        """Common callback for all trait labels"""
        items_list=[]
        if args[2]:
            self.precacheShipTraits()
            items_list = self.shipTraitsWithImages
        elif 1:
            self.precacheTraits()
            traitType = "personal"
            if args[1]:
                traitType = "activereputation"
            elif args[0]:
                traitType = "reputation"
            items_list = self.traitsWithImages[traitType][args[3]]
            self.logWrite('traitLabelCallback: ['+traitType+']['+args[3]+']: '+str(len(items_list)), 4)
        else:
            #Remove this section on stable
            traits = [self.traits[e] for e in range(len(self.traits)) if "chartype" in self.traits[e] and self.traits[e]["chartype"] == "char"]
            traits = [traits[e] for e in range(len(traits)) if "environment" in traits[e] and traits[e]["environment"] == args[3]]
            traits = [traits[e] for e in range(len(traits)) if "type" in traits[e] and ("reputation" in traits[e]["type"]) == args[0]]
            traits = [traits[e] for e in range(len(traits)) if "type" in traits[e] and ("activereputation" in traits[e]["type"]) == args[1]]
            items_list = [(html.unescape(traits[e]["name"]), self.imageFromInfoboxName(traits[e]["name"],self.itemBoxX,self.itemBoxY)) for e in range(len(traits))]
        itemVar = self.getEmptyItem()
        item = self.pickerGui("Pick trait", itemVar, items_list, [self.setupSearchFrame])
        if 'item' in item and len(item['item']):
            if item['item'] == 'X':
                item['item'] = ''
                self.backend['i_'+item['item']+str(i)] = self.emptyImage
                canvas.itemconfig(img[0],image=self.emptyImage)
                self.build[key][i] = item
            else:
                if ('i_'+item['item']+str(i) not in self.backend):
                    self.backend['i_'+item['item']+str(i)] = item['image']
                canvas.itemconfig(img[0],image=self.backend['i_'+item['item']+str(i)])
                environment = 'space'
                if len(args) >= 4:
                    environment = args[3]
                canvas.bind('<Enter>', lambda e,item=item:self.setupInfoboxFrame(item, '', environment))
                item.pop('image')
                self.build[key][i] = item

    def precacheBoffAbilitiesSingle(self, name, environment, type, category, desc):
        # category is Tactical, Science, Engineer, Specs
        # type is the boff ability rank
        if not environment in self.backend['cacheBoffTooltips']:
            self.backend['cacheBoffTooltips'][environment] = dict()
        if not name in self.backend['cacheBoffTooltips'][environment]:
            # Longer descriptions stored only once
            self.backend['cacheBoffTooltips'][environment][name] = self.deWikify(desc)
        
        if not environment in self.backend['cacheBoffAbilities']:
            self.backend['cacheBoffAbilities'][environment] = dict()
        if not type in self.backend['cacheBoffAbilities'][environment]:
            self.backend['cacheBoffAbilities'][environment][type] = dict()

        if not environment in self.boffAbilitiesWithImages:
            self.boffAbilitiesWithImages[environment] = dict()
        if not category in self.boffAbilitiesWithImages[environment]:
            self.boffAbilitiesWithImages[environment][category] = dict()
        if not type in self.boffAbilitiesWithImages[environment][category]:
            self.boffAbilitiesWithImages[environment][category][type] = []
            
        if not name in self.backend['cacheBoffAbilities'][environment][type]:
            self.backend['cacheBoffAbilities'][environment][type][name] = 'yes'

            self.boffAbilitiesWithImages[environment][category][type].append((name,self.imageFromInfoboxName(name,self.itemBoxX,self.itemBoxY,'_icon_(Federation)')))
            self.logWrite('precacheBoffAbilitiesSingle: ['+environment+']['+category+']['+str(type)+'] -- '+name+' -- |'+str(len(desc))+'|', 4) 
        
    def precacheBoffAbilities(self):
        """Common callback for boff labels"""
        if 'cacheBoffAbilities' in self.backend and 'space' in self.backend['cacheBoffAbilities']:
            return self.backend['cacheBoffAbilities']
            
        boffAbilities = self.fetchOrRequestHtml(self.r_boffAbilities_source, "boff_abilities") 
        # Categories beyond tac/eng/sci should come from a json load when capt specs are converted
        boffCategories = ['Tactical', 'Engineering', 'Science', 'Intelligence', 'Command', 'Pilot', 'Temporal', 'Miracle Worker']
        boffRanks = [1, 2, 3, 4]
        boffEnvironments = ['space', 'ground']
        
        for environment in boffEnvironments:
            l0 = [h2 for h2 in boffAbilities.find('h2') if ' Abilities' in h2.html]
            if environment == 'ground':
                l0 = [l for l in l0 if "Pilot" not in l.text]
                l1 = boffAbilities.find('h2+h3+table+h3+table')
            else:
                l1 = boffAbilities.find('h2+h3+table')   
                
            #for rank in boffRanks:
            for category in boffCategories:
                table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#'+category.replace(' ','_')+'_Abilities', first=True), Element)]
                if not len(table):
                    continue
                trs = table[0].find('tr')
                
                skills = []
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
                            self.logWrite('precacheBoffAbilities______: ['+environment+']['+category+']['+str(rank1+i)+']: '+tds[3].text.strip(), 4)

        self.logWriteCounter('Boff ability', '(json)', len(self.backend['cacheBoffTooltips']['space']), ['space'])
        self.logWriteCounter('Boff ability', '(json)', len(self.backend['cacheBoffTooltips']['ground']), ['ground'])
        
    def boffLabelCallback(self, e, canvas, img, i, key, args, idx, environment='space'):
        """Common callback for boff labels"""
        self.precacheBoffAbilities()

        universalTypes = ['Tactical', 'Engineering', 'Science' ]
        items_list = []
        rank = args[2] + 1
        
        logNote = args[0]
        if args[1]:
            logNote = logNote + ", "+args[1]
        self.logWrite('spaceBoffcallback: ['+environment+']['+logNote+']['+str(args[2])+']', 3)

        if args[0] == 'universal':
            for specType in universalTypes:
                items_list = items_list + self.boffAbilitiesWithImages[environment][specType][rank]
        else:
            items_list = self.boffAbilitiesWithImages[environment][args[0]][rank]
        if args[1] is not None and args[1] != '':
            items_list = items_list + self.boffAbilitiesWithImages[environment][args[1]][rank]

        itemVar = self.getEmptyItem()
        item = self.pickerGui("Pick Ability", itemVar, items_list, [self.setupSearchFrame])
        if 'item' in item and len(item['item']):
            if item['item'] == 'X':
                item['item'] = ''
                self.backend['i_'+item['item']+str(i)] = self.emptyImage
                canvas.itemconfig(img,image=self.emptyImage)
                self.build['boffs'][key][i] = item
            else:
                if ('i_'+item['item']+str(i) not in self.backend):
                    self.backend['i_'+item['item']+str(i)] = item['image']
                canvas.itemconfig(img,image=self.backend['i_'+item['item']+str(i)])
                canvas.bind('<Enter>', lambda e,item=item:self.setupInfoboxFrame(item, '', environment))
                self.build['boffs'][key][i] = item['item']
                
        # ground used +'_'+str(i)

    def shipMenuCallback(self, *args):
        """Callback for ship selection menu"""
        if self.backend['ship'].get() == '':
            return
        self.build['ship'] = self.backend['ship'].get()
        self.backend['shipHtml'] = self.getShipFromName(self.r_ships, self.build['ship'])
        tier = self.backend['shipHtml']["tier"]
        self.clearFrame(self.shipTierFrame)
        self.setupTierFrame(tier)
        self.backend["tier"].set(self.getTierOptions(tier)[0])

    def shipPickButtonCallback(self, *args):
        """Callback for ship picker button"""
        itemVar = self.getEmptyItem()
        items_list = [(name, self.emptyImage) for name in self.shipNames]
        item = self.pickerGui("Pick Starship", itemVar, items_list, [self.setupSearchFrame])
        if 'item' in item and len(item['item']):
            if item['item'] == 'X':
                item['item'] = ''
                self.build['ship'] = item['item']
                self.backend['shipHtml'] = None
                self.shipLabel.configure(image=self.emptyImage)
                self.shipButton.configure(text=item['item'])
                self.backend['ship'].set(item['item'])
                self.setupSpaceBuildFrames()
            else:
                self.shipButton.configure(text=item['item'])
                self.backend['ship'].set(item['item'])
                self.setupSpaceBoffFrame(self.backend['shipHtml'])

    def importCallback(self, event=None):
        """Callback for import button"""
        inFilename = filedialog.askopenfilename(filetypes=[("JSON file", '*.json'),("PNG image","*.png"),("All Files","*.*")])
        self.importByFilename(inFilename)

    def importByFilename(self, inFilename, force=False):
        if not inFilename: return
        if inFilename.endswith('.png'):
            # image = Image.open(inFilename)
            # self.build = json.loads(image.text['build'])
            self.buildImport = json.loads(self.decodeBuildFromImage(inFilename))
        else:
            with open(inFilename, 'r') as inFile:
                self.buildImport = json.load(inFile)
        
        if 'versionJSON' not in self.buildImport and not force:
            self.logWrite(inFilename+' -- version mismatch: no version found (older format)')
            if self.persistent['forceJsonLoad']:
                self.importByFilename(inFilename, True)
        elif self.buildImport['versionJSON'] >= self.versionJSONminimum or force:
            logNote = ' (fields:['+str(len(self.buildImport))+'=>'+str(len(self.build))+']='
            self.build.update(self.buildImport)
            logNote = logNote+str(len(self.build))+' merged)'
            self.clearBackend()
            self.buildToBackendSeries()
            
            self.hookBackend()
            self.setupShipInfoFrame()
            if 'tier' in self.build and len(self.build['tier']) > 1:
                self.setupTierFrame(int(self.build['tier'][1]))
            self.shipButton.configure(text=self.build['ship'])
            self.setupSpaceBuildFrames()
            self.setupGroundBuildFrames()
            
            self.precacheShipTraits()
            self.precacheTraits()
            self.precacheBoffAbilities()
            
            if force:
                logNote=' (FORCE LOAD)'+logNote

            self.logWrite(inFilename+' -- template loaded'+logNote)
        else:
            self.logWrite(inFilename+' -- version mismatch: '+str(self.buildImport['versionJSON'])+' < '+str(self.versionJSON))
            self.importByFilename(inFilename, True)

    def exportCallback(self, event=None):
        """Callback for export button"""
        try:
            with filedialog.asksaveasfile(defaultextension=".json",filetypes=[("JSON file","*.json"),("All Files","*.*")]) as outFile:
                json.dump(self.build, outFile)
                self.logWrite(outFile.name+' -- saved')
        except AttributeError:
            pass

    def exportPngCallback(self, event=None):
        """Callback for export as png button"""
        # pixel correction
        self.window.update()

        screenTopLeftX = self.window.winfo_rootx()
        screenTopLeftY = self.window.winfo_rooty()
        screenBottomRightX = screenTopLeftX + self.window.winfo_width()
        screenBottomRightY = screenTopLeftY + self.window.winfo_height()
        image = ImageGrab.grab(bbox=(screenTopLeftX, screenTopLeftY, screenBottomRightX, screenBottomRightY))
        
        self.logWrite('Image size: '+str(image.size))

        outFilename = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG image","*.png"),("All Files","*.*")])
        if not outFilename: return
        image.save(outFilename, "PNG")
        self.encodeBuildInImage(outFilename, json.dumps(self.build), outFilename)
        self.logWrite(outFilename+' -- saved, Image size: '+str(image.size))

    def skillLabelCallback(self, skill, rank):
        rankReqs = [0, 5, 15, 25, 35]
        if(skill in self.build['skills'][rank]):
            if (rank < 4 and len(self.build['skills'][rank+1])>0):
                if self.backend['skillCount'] > rankReqs[rank+1]:
                    self.build['skills'][rank].remove(skill)
                    self.backend['skillLabels'][skill].configure(bg="gray")
                    self.backend['skillCount'] -= 1
                    if self.backend['skillCount'] < rankReqs[rank]:
                        for s in self.backend['skillNames'][rank]:
                            self.backend['skillLabels'][s].configure(bg="black")
            return
        if self.backend['skillCount'] < rankReqs[rank] or self.backend['skillCount'] == 46: return
        self.build['skills'][rank].append(skill)
        self.backend['skillLabels'][skill].configure(bg="yellow")
        self.backend['skillCount'] += 1
        if rank < 4 and self.backend['skillCount'] == rankReqs[rank+1]:
            for s in self.backend['skillNames'][rank+1]:
                self.backend['skillLabels'][s].configure(bg="grey")

    def redditExportDisplayGround(self, textframe):
        if self.build['eliteCaptain'] == 0:
            elite = "No"
        elif self.build['eliteCaptain'] == 1:
            elite = "Yes"
        else:
            elite = "You should not be seeing this... PANIC!"
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
                column0 = column0 + self.makeRedditColumn(["#"+str(int(groundboff[-1])+1)+": "+self.build['boffseats']['ground'][int(groundboff[-1])]+" / "+self.build['boffseats']['ground_spec'][int(groundboff[-1])]], len(self.build['boffs'][groundboff]))
                column1 = column1 + self.makeRedditColumn(self.build['boffs'][groundboff], len(self.build['boffs'][groundboff]))
        redditString = redditString + self.makeRedditTable(['**Profession**']+column0, ['**Power**']+column1, ['**Notes**']+[None]*len(column0))
        textframe.delete("1.0",END)
        textframe.insert(END, redditString)
    
    def redditExportDisplaySpace(self, textframe):
        if self.build['eliteCaptain'] == 0:
            elite = "No"
        elif self.build['eliteCaptain'] == 1:
            elite = "Yes"
        else:
            elite = "You should not be seeing this... PANIC!"
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
        textframe.delete("1.0",END)
        textframe.insert(END, redditString)

    def exportRedditCallback(self, event=None):
        phi = font.Font(family='Helvetica', size=12, weight='bold')
        redditWindow = Toplevel(self.window)
        redditText = Text(redditWindow)
        btfr = Frame(redditWindow)
        btfr.pack(side="top", fill="x")
        redditbtspace = Button(btfr,text="SPACE", font=phi,  bg="#6b6b6b",fg="white",command=lambda: self.redditExportDisplaySpace(redditText))
        redditbtground = Button(btfr, text="GROUND", font =phi, bg="#6b6b6b", fg="white",command=lambda: self.redditExportDisplayGround(redditText))
        redditbtspace.grid(row=0,column=0,sticky="nsew")
        redditbtground.grid(row=0,column=1,sticky="nsew")
        btfr.grid_columnconfigure(0,weight=1)
        btfr.grid_columnconfigure(1,weight=1)
        redditText.pack(fill=BOTH, expand=True)
        self.redditExportDisplaySpace(redditText)
        redditWindow.mainloop()

    def cacheInvalidateCallback(self, dir):
        for filename in os.listdir(dir):
            if not filename.endswith('.bak'):
                file_path = os.path.join(dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        if os.path.isfile(file_path+'.bak') or os.path.islink(file_path+'.bak'):
                            os.unlink(file_path+'.bak')
                        os.rename(file_path, file_path+'.bak')
                except Exception as e:
                    log.Write('Failed to delete %s. Reason: %s' % (file_path, e))

    def buildToBackendSeries(self):
        self.copyBuildToBackend('playerShipName')
        self.copyBuildToBackend('playerShipDesc')
        self.copyBuildToBackend('playerDesc')
        self.copyBuildToBackend('career')
        self.copyBuildToBackend('species')
        self.copyBuildToBackend('specPrimary')
        self.copyBuildToBackend('specSecondary')
        self.copyBuildToBackend('ship')
        self.copyBuildToBackend('tier')
        self.copyBuildToBackend('eliteCaptain')
        self.persistentToBackend()

    def clearBuildCallback(self, event=None):
        """Callback for the clear build button"""
        self.clearBuild()
        self.buildToBackendSeries()

        #self.backend['tier'].set('')
        self.backend['shipHtml'] = None
        self.setupShipInfoFrame()
        self.clearFrame(self.shipEquipmentFrame)
        self.clearFrame(self.shipBoffFrame)
        self.setupGroundBuildFrames()
        self.shipImg = self.emptyImage
        self.groundImg = self.emptyImage
        self.shipLabel.configure(image=self.shipImg)
        self.charLabel.configure(image=self.groundImg)

    def boffUniversalCallback(self, v, idx, key):
        self.build['boffseats'][key][idx] = v.get()

    def doffStripPrefix(self, textBlock, isSpace=True):
        textBlock = self.deWikify(textBlock)
        if (isSpace and textBlock.startswith('[SP]')) or (not isSpace and textBlock.startswith('[GR]')):
            return textBlock[len('[--]'):]
        return textBlock    
    
    def doffSpecCallback(self, om, v0, v1, row, isSpace=True):
        if self.backend['cacheDoffs'] is None:
            return
        self.build['doffs']['space' if isSpace else 'ground'][row] = {"name": "", "spec": v0.get(), "effect": ''}
        menu = om['menu']
        menu.delete(0, END)
        
        
        doff_desclist_space = sorted([self.doffStripPrefix(self.backend['cacheDoffs']['Space' if isSpace else 'Ground'][item]['description'], isSpace) for item in list(self.backend['cacheDoffs']['Space' if isSpace else 'Ground'].keys()) if v0.get() in item])
        
        for desc in doff_desclist_space:
            menu.add_command(label=desc, command=lambda v1=v1,value=desc: v1.set(value))

        self.setupDoffFrame(self.shipDoffFrame)
        self.setupDoffFrame(self.groundDoffFrame)

    def doffEffectCallback(self, om, v0, v1, row, isSpace=True):
        if self.backend['cacheDoffs'] is None:
            return
        self.build['doffs']['space' if isSpace else 'ground'][row]['effect'] = v1.get()
        self.setupDoffFrame(self.shipDoffFrame)
        self.setupDoffFrame(self.groundDoffFrame)

    def tagBoxCallback(self, var, text):
        self.build['tags'][text] = var.get()
        
    def eliteCaptainCallback(self):
        self.build['eliteCaptain'] = self.backend['eliteCaptain'].get()

    def markBoxCallback(self, itemVar, value):
        itemVar['mark'] = value

    def focusSpaceBuildFrameCallback(self):
        self.groundBuildFrame.pack_forget()
        self.skillTreeFrame.pack_forget()
        self.glossaryFrame.pack_forget()
        self.settingsFrame.pack_forget()
        self.spaceBuildFrame.pack(fill=BOTH, expand=True, padx=15)
        self.setupShipInfoFrame() #get updates from info changes
        self.shipLabel.configure(image=self.shipImg)
        if 'tier' in self.backend and len(self.backend['tier'].get()) > 0:
            self.setupJustTierFrame(int(self.backend['tier'].get()[1]))
        self.setupDoffFrame(self.shipDoffFrame)

    def focusGroundBuildFrameCallback(self):
        self.spaceBuildFrame.pack_forget()
        self.skillTreeFrame.pack_forget()
        self.glossaryFrame.pack_forget()
        self.settingsFrame.pack_forget()
        self.groundBuildFrame.pack(fill=BOTH, expand=True, padx=15)
        self.setupGroundInfoFrame() #get updates from info changes
        self.charLabel.configure(image=self.groundImg)
        self.setupDoffFrame(self.groundDoffFrame)

    def focusSkillTreeFrameCallback(self):
        self.spaceBuildFrame.pack_forget()
        self.groundBuildFrame.pack_forget()
        self.glossaryFrame.pack_forget()
        self.settingsFrame.pack_forget()
        self.skillTreeFrame.pack(fill=BOTH, expand=True, padx=15)

    def focusGlossaryFrameCallback(self):
        self.spaceBuildFrame.pack_forget()
        self.groundBuildFrame.pack_forget()
        self.skillTreeFrame.pack_forget()
        self.settingsFrame.pack_forget()
        self.glossaryFrame.pack(fill=BOTH, expand=True, padx=15)

    def focusSettingsFrameCallback(self):
        self.spaceBuildFrame.pack_forget()
        self.groundBuildFrame.pack_forget()
        self.skillTreeFrame.pack_forget()
        self.glossaryFrame.pack_forget()
        self.settingsFrame.pack(fill=BOTH, expand=True, padx=15)
        self.logDisplayUpdate()

    def speciesUpdateCallback(self):
        self.copyBackendToBuild('species')
        self.setupSpaceTraitFrame()
        self.setupGroundTraitFrame()

    def setupSearchFrame(self,frame,itemVar,content):
        topbarFrame = Frame(frame)
        searchText = StringVar()
        Label(topbarFrame, text="Search:").grid(row=0, column=0, sticky='nsew')
        searchEntry = Entry(topbarFrame, textvariable=searchText)
        searchEntry.grid(row=0, column=1, columnspan=5, sticky='nsew')
        searchEntry.focus_set()
        searchText.trace_add('write', lambda v,i,m,content=content,frame=frame:self.applyContentFilter(frame, content, searchText.get()))
        
        topbarFrame.pack()

    def setupRarityFrame(self,frame,itemVar,content):
        topbarFrame = Frame(frame)
        mark = StringVar()
        if 'markDefault' in self.persistent and self.persistent['markDefault'] is not None:
            self.logWrite('self.persistent["markDefault"]: '+self.persistent['markDefault'], 3)
            mark.set(self.persistent['markDefault'])
        markOption = OptionMenu(topbarFrame, mark, *self.marks)
        markOption.grid(row=0, column=0, sticky='nsw')
        rarity = StringVar(value=self.persistent['rarityDefault'])
        rarityOption = OptionMenu(topbarFrame, rarity, *self.rarities)
        rarityOption.grid(row=0, column=1, sticky='nsew')
        modFrame = Frame(topbarFrame, bg='gray')
        modFrame.grid(row=1, column=0, columnspan=2, sticky='nsew')
        mark.trace_add('write', lambda v,i,m:self.markBoxCallback(value=mark.get(), itemVar=itemVar))
        rarity.trace_add('write', lambda v,i,m,frame=modFrame:self.setupModFrame(frame, rarity=rarity.get(), itemVar=itemVar))
        topbarFrame.pack()

    def labelBuildBlock(self, frame, name, row, col, cspan, key, n, callback, args=None, disabledCount=0):
        """Set up n-element line of ship equipment"""
        self.backend['i_'+key] = [None] * n
        cFrame = Frame(frame, bg='#3a3a3a')
        cFrame.grid(row=row, column=col, columnspan=cspan, sticky='nsew', padx=10)
        lFrame = Frame(cFrame, bg='#3a3a3a')
        lFrame.pack(fill=BOTH, expand=True)
        label =  Label(lFrame, text=name, bg='#3a3a3a', fg='#ffffff', font=('Helvetica', 8))
        label.pack(side='left')
        iFrame = Frame(cFrame, bg='#3a3a3a')
        iFrame.pack(fill=BOTH, expand=True)
        disabledStart = n - disabledCount
        for i in range(n):
            image1=None
            if key in self.build and self.build[key][i] is not None and i < disabledStart:
                image0=self.imageFromInfoboxName(self.build[key][i]['item'])
                if 'rarity' in self.build[key][i]:
                    image1=self.imageFromInfoboxName(self.build[key][i]['rarity'])
                self.backend['i_'+key][i] = [image0, image1]
            else:
                image0=image1=self.emptyImage
            canvas = Canvas(iFrame, highlightthickness=0, borderwidth=0, width=25, height=35, bg='gray' if i < disabledStart else 'black')
            canvas.grid(row=row, column=i+1, sticky='nse', padx=(25 + 3 * 2) if i >= disabledStart else 2, pady=2)
            img0 = canvas.create_image(0,0, anchor="nw",image=image0)
            img1 = None if image1 is None else canvas.create_image(0,0, anchor="nw",image=image1)
            if i >= disabledStart:
                canvas.itemconfig(img0, state=DISABLED)
                canvas.itemconfig(img1, state=DISABLED)
            if (args is not None and i < disabledStart):
                environment = 'space'
                internalKey = ''
                if len(args) >= 4:
                    environment = args[3]
                if type(args[0]) is str:
                    internalKey = args[0]
                canvas.bind('<Button-1>', lambda e,canvas=canvas,img=(img0, img1),i=i,args=args,key=key,callback=callback:callback(e,canvas,img,i,key,args))
                canvas.bind('<Enter>', lambda e,item=self.build[key][i],internalKey=internalKey,environment=environment:self.setupInfoboxFrame(item, internalKey, environment))


    def setupShipBuildFrame(self, ship):
        """Set up UI frame containing ship equipment"""
        self.clearFrame(self.shipEquipmentFrame)
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
        self.labelBuildBlock(self.shipEquipmentFrame, "Fore Weapons", 0, 0, 1, 'foreWeapons', self.backend['shipForeWeapons'], self.itemLabelCallback, ["Ship Fore Weapon", "Pick Fore Weapon", ""])
        if ship["secdeflector"] == 1:
            self.labelBuildBlock(self.shipEquipmentFrame, "Secondary", 1, 1, 1, 'secdef', 1, self.itemLabelCallback, ["Ship Secondary Deflector", "Pick Secdef", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Deflector", 0, 1, 1, 'deflector', 1, self.itemLabelCallback, ["Ship Deflector Dish", "Pick Deflector", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Engines", 2, 1, 1, 'engines', 1, self.itemLabelCallback, ["Impulse Engine", "Pick Engine", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Core", 3, 1, 1, 'warpCore', 1, self.itemLabelCallback, ["Singularity Engine" if "Warbird" in self.build['ship'] or "Aves" in self.build['ship'] else "Warp ", "Pick Core", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Shield", 4, 1, 1, 'shield' , 1, self.itemLabelCallback, ["Ship Shields", "Pick Shield", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Aft Weapons", 1, 0, 1, 'aftWeapons', self.backend['shipAftWeapons'], self.itemLabelCallback, ["Ship Aft Weapon", "Pick aft weapon", ""])
        if ship["experimental"] == 1:
            self.labelBuildBlock(self.shipEquipmentFrame, "Experimental", 2, 0, 1, 'experimental', 1, self.itemLabelCallback, ["Experimental", "Pick Experimental Weapon", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Devices", 3, 0, 1, 'devices', self.backend['shipDevices'], self.itemLabelCallback, ["Ship Device", "Pick Device (S)", ""])
        if self.backend['shipUniConsoles'] > 0:
            self.labelBuildBlock(self.shipEquipmentFrame, "Uni Consoles", 3, 2, 1, 'uniConsoles', self.backend['shipUniConsoles'], self.itemLabelCallback, ["Console", "Pick Uni Console", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Sci Consoles", 2, 2, 1, 'sciConsoles', self.backend['shipSciConsoles'], self.itemLabelCallback, ["Ship Science Console", "Pick Sci Console", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Eng Consoles", 1, 2, 1, 'engConsoles', self.backend['shipEngConsoles'], self.itemLabelCallback, ["Ship Engineering Console", "Pick Eng Console", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Tac Consoles", 0, 2, 1, 'tacConsoles', self.backend['shipTacConsoles'], self.itemLabelCallback, ["Ship Tactical Console", "Pick Tac Console", ""])
        if self.backend['shipHangars'] > 0:
            self.labelBuildBlock(self.shipEquipmentFrame, "Hangars", 4, 0, 1, 'hangars', self.backend['shipHangars'], self.itemLabelCallback, ["Hangar Bay", "Pick Hangar Pet", ""])

    def setupCharBuildFrame(self):
        """Set up UI frame containing ship equipment"""
        self.clearFrame(self.groundEquipmentFrame)
        self.labelBuildBlock(self.groundEquipmentFrame, "Kit Modules", 0, 0, 5, 'groundKitModules', 6 if self.backend['eliteCaptain'].get() else 5, self.itemLabelCallback, ["Kit Module", "Pick Module", "", 'ground'])
        self.labelBuildBlock(self.groundEquipmentFrame, "Kit Frame", 0, 5, 1, 'groundKit', 1, self.itemLabelCallback, ["Kit Frame", "Pick Kit", "", 'ground'])
        self.labelBuildBlock(self.groundEquipmentFrame, "Armor", 1, 0, 1, 'groundArmor', 1, self.itemLabelCallback, ["Body Armor", "Pick Armor", "", 'ground'])
        self.labelBuildBlock(self.groundEquipmentFrame, "EV Suit", 1, 1, 1, 'groundEV', 1, self.itemLabelCallback, ["EV Suit", "Pick EV Suit", "", 'ground'])
        self.labelBuildBlock(self.groundEquipmentFrame, "Shield", 2, 0, 1, 'groundShield', 1, self.itemLabelCallback, ["Personal Shield", "Pick Shield (G)", "", 'ground'])
        self.labelBuildBlock(self.groundEquipmentFrame, "Weapons", 3, 0, 2, 'groundWeapons' , 2, self.itemLabelCallback, ["Ground Weapon", "Pick Weapon (G)", "", 'ground'])
        self.labelBuildBlock(self.groundEquipmentFrame, "Devices", 4, 0, 5, 'groundDevices', 5 if self.backend['eliteCaptain'].get() else 4, self.itemLabelCallback, ["Ground Device", "Pick Device (G)", "", 'ground'])

    def setupSkillMainFrame(self):
        self.clearFrame(self.skillMiddleFrame)
        if "skills" not in self.backend:
            with open("local/skills.json", "r") as f:
                self.backend["skills"] = json.load(f)
        skillTable = self.backend["skills"]["content"]
        i = 0
        for col in skillTable:
            self.groundMiddleFrame.grid_columnconfigure(i, weight=1, uniform="skillColSpace")
            i += 1
            colFrame = Frame(self.skillMiddleFrame)
            colFrame.pack(side='left', fill=BOTH, expand=True)
            for row in col:
                rowFrame = Frame(colFrame)
                rowFrame.pack()
                for cell in row:
                    image0=self.imageFromInfoboxName(cell['image'], width=25, height=35, suffix='')
                    self.backend['i_'+cell['name']] = image0
                    frame = Frame(rowFrame, bg='yellow')
                    frame.pack(side='left', anchor='center', pady=1, padx=1)
                    canvas = Canvas(frame, highlightthickness=0, borderwidth=3, relief='groove', width=25, height=35, bg= 'yellow' if cell['name'] in self.build['skills'][i-1] else ('black' if i != 1 else 'grey'))
                    canvas.pack()
                    canvas.create_image(0,0, anchor="nw",image=image0)
                    self.backend['skillLabels'][cell['name']] = canvas
                    self.backend['skillNames'][i-1].append(cell['name'])
                    canvas.bind('<Button-1>', lambda e,skill=cell['name'],rank=i-1:self.skillLabelCallback(skill, rank))

    def setupSpaceTraitFrame(self):
        """Set up UI frame containing traits"""
        self.clearFrame(self.shipTraitFrame)

        traitEliteCaptain = 1 if self.backend['eliteCaptain'].get() else 0
        traitAlien = 1 if 'Alien' in self.backend['species'].get() else 0
        self.labelBuildBlock(self.shipTraitFrame, "Personal", 0, 0, 1, 'personalSpaceTrait', 6 if traitEliteCaptain else 5, self.traitLabelCallback, [False, False, False, "space"])
        self.labelBuildBlock(self.shipTraitFrame, "Personal", 1, 0, 1, 'personalSpaceTrait2', 5, self.traitLabelCallback, [False, False, False, "space"], 1 if not traitAlien else 0)
        self.labelBuildBlock(self.shipTraitFrame, "Starship", 2, 0, 1, 'starshipTrait', 5+(1 if '-X' in self.backend['tier'].get() else 0), self.traitLabelCallback, [False, False, True, "space"])
        self.labelBuildBlock(self.shipTraitFrame, "SpaceRep", 3, 0, 1, 'spaceRepTrait', 5, self.traitLabelCallback, [True, False, False, "space"])
        self.labelBuildBlock(self.shipTraitFrame, "Active", 4, 0, 1, 'activeRepTrait', 5, self.traitLabelCallback, [True, True, False, "space"])

    def setupGroundTraitFrame(self):
        """Set up UI frame containing traits"""
        self.clearFrame(self.groundTraitFrame)

        traitEliteCaptain = 1 if self.backend['eliteCaptain'].get() else 0
        traitAlien = 1 if 'Alien' in self.backend['species'].get() else 0
        self.labelBuildBlock(self.groundTraitFrame, "Personal", 0, 0, 1, 'personalGroundTrait', 6 if traitEliteCaptain else 5, self.traitLabelCallback, [False, False, False, "ground"])
        self.labelBuildBlock(self.groundTraitFrame, "Personal", 1, 0, 1, 'personalGroundTrait2', 5, self.traitLabelCallback, [False, False, False, "ground"], 1 if not traitAlien else 0)
        self.labelBuildBlock(self.groundTraitFrame, "GroundRep", 3, 0, 1, 'groundRepTrait', 5, self.traitLabelCallback, [True, False, False, "ground"])
        self.labelBuildBlock(self.groundTraitFrame, "Active", 4, 0, 1, 'groundActiveRepTrait', 5, self.traitLabelCallback, [True, True, False, "ground"])

    def setupSpaceBoffFrame(self, ship):
        """Set up UI frame containing boff skills"""
        self.clearFrame(self.shipBoffFrame)
        environment = 'space'
        if not environment in self.build['boffseats']:
            self.build['boffseats'][environment] = [None] * 6
            
        if ship is None or not 'boffs' in ship:
            return
        
        idx = 0
        boffs = ship["boffs"]
        for boff in boffs:
            rank = 3 if "Lieutenant Commander" in boff else 2 if "Lieutenant" in boff else 4 if "Commander" in boff else 1
            boff = boff.replace('Lieutenant', '').replace('Commander', '').replace('Ensign', '').strip()
            spec = self.boffTitleToSpec(boff)
            sspec = None
            for s in self.specNames:
                if '-'+s in boff:
                    sspec = s
                    break
            if spec == 'Tactical' and rank == 3 and 'Science Destroyer' in self.build['ship']: #sci destroyers get tac mode turning lt cmdr to cmdr
                rank = 4
            bFrame = Frame(self.shipBoffFrame, width=120, height=80, bg='#3a3a3a')
            bFrame.pack(fill=BOTH, expand=True)
            boffSan = environment+'Boff_' + str(idx)
            self.backend['i_'+boffSan] = [None] * rank
            if spec != 'Universal' and spec != self.build['boffseats'][environment][idx]:
                self.build['boffs'][boffSan] = [None] * rank
            bSubFrame0 = Frame(bFrame, bg='#3a3a3a')
            bSubFrame0.pack(fill=BOTH)
            v = StringVar(self.window, value=boff)
            if spec == 'Universal':
                if self.build['boffseats'][environment][idx] is not None:
                    v.set(self.build['boffseats'][environment][idx])
                else:
                    v.set('Tactical')
                    self.build['boffseats'][environment][idx] = 'Tactical'
                specLabel0 = OptionMenu(bSubFrame0, v, 'Tactical', 'Engineering', 'Science')
                specLabel0.configure(bg='#3a3a3a', fg='#ffffff', font=('Helvetica', 10))
                specLabel0.pack(side='left')
                v.trace_add("write", lambda v,i,m,v0=v,idx=idx:self.boffUniversalCallback(v0, idx, environment))
                if sspec is not None:
                    specLabel1 = Label(bSubFrame0, text=' / '+sspec, bg='#3a3a3a', fg='#ffffff', font=('Helvetica', 10))
                    specLabel1.pack(side='left')
            else:
                specLabel0 = Label(bSubFrame0, text=(spec if sspec is None else spec+' / '+sspec), bg='#3a3a3a', fg='#ffffff', font=('Helvetica', 10))
                specLabel0.pack(side='left')
                self.build['boffseats'][environment][idx] = spec
            bSubFrame1 = Frame(bFrame, bg='#3a3a3a')
            bSubFrame1.pack(fill=BOTH)
            if boffSan in self.build['boffs']:
                boffExistingLen = len(self.build['boffs'][boffSan])
                if boffExistingLen < rank:
                    self.build['boffs'][boffSan].append([None] * (rank - boffExistingLen))
                elif boffExistingLen > rank:
                    self.build['boffs'][boffSan] = self.build['boffs'][boffSan][slice(rank)]
            for i in range(rank):
                if boffSan in self.build['boffs'] and self.build['boffs'][boffSan][i] is not None:
                    image=self.imageFromInfoboxName(self.build['boffs'][boffSan][i])
                    self.backend['i_'+boffSan][i] = image
                else:
                    image=self.emptyImage
                    self.build['boffs'][boffSan] = [None] * rank
                canvas = Canvas(bSubFrame1, highlightthickness=0, borderwidth=0, width=25, height=35, bg='gray')
                canvas.grid(row=1, column=i, sticky='ns', padx=2, pady=2)
                img0 = canvas.create_image(0,0, anchor="nw",image=image)
                canvas.bind('<Button-1>', lambda e,canvas=canvas,img=img0,i=i,spec=spec,sspec=sspec,key=boffSan,idx=idx,environment=environment,v=v,callback=self.boffLabelCallback:callback(e,canvas,img,i,key,[self.boffTitleToSpec(v.get()), sspec, i], idx, environment))
                canvas.bind('<Enter>', lambda e,item=self.build['boffs'][boffSan][i],environment=environment:self.setupInfoboxFrame(item, '', environment))
            idx = idx + 1

    def setupGroundBoffFrame(self):
        """Set up UI frame containing ground boff skills"""
        self.clearFrame(self.groundBoffFrame)
        environment = 'ground'
        if not environment in self.build['boffseats']:
            self.build['boffseats'][environment] = [None] * 4
        if not environment+'_spec' in self.build['boffseats']:
            self.build['boffseats'][environment+'_spec'] = [None] * 4
            
        idx = 0
        for i in range(4):
            bFrame = Frame(self.groundBoffFrame, width=120, height=80, bg='#3a3a3a')
            bFrame.pack(fill=BOTH, expand=True)
            boffSan = environment+'Boff'+'_'+str(idx)
            self.backend['i_'+boffSan] = [None] * 4
            bSubFrame0 = Frame(bFrame, bg='#3a3a3a')
            bSubFrame0.pack(fill=BOTH)
            
            v = StringVar(self.window, value='Tactical')
            if environment in self.build['boffseats'] and self.build['boffseats'][environment][idx] is not None:
                v.set(self.build['boffseats'][environment][idx])
            else:
                self.build['boffseats'][environment][idx] = v.get()
            specLabel0 = OptionMenu(bSubFrame0, v, 'Tactical', 'Engineering', 'Science')
            specLabel0.configure(bg='#3a3a3a', fg='#ffffff', font=('Helvetica', 10))
            specLabel0.pack(side='left')
            v.trace_add("write", lambda v,i,m,v0=v,idx=idx:self.boffUniversalCallback(v0, idx, environment))
            
            v2 = StringVar(self.window, value='')
            if environment+'_spec' in self.build['boffseats'] and self.build['boffseats'][environment+'_spec'][idx] is not None:
                v2.set(self.build['boffseats'][environment+'_spec'][idx])
            else:
                self.build['boffseats'][environment+'_spec'][idx] = v2.get()
            specLabel1 = OptionMenu(bSubFrame0, v2, *self.boffGroundSpecNames)
            specLabel1.configure(bg='#3a3a3a', fg='#ffffff', font=('Helvetica', 10))
            specLabel1.pack(side='left')
            v2.trace_add("write", lambda v2,i,m,v0=v2,idx=idx:self.boffUniversalCallback(v0, idx, environment+'_spec'))
            
            bSubFrame1 = Frame(bFrame, bg='#3a3a3a')
            bSubFrame1.pack(fill=BOTH)

            for i in range(4):
                if boffSan in self.build['boffs'] and self.build['boffs'][boffSan][i] is not None:
                    image=self.imageFromInfoboxName(self.build['boffs'][boffSan][i])
                    self.backend['i_'+boffSan][i] = image
                else:
                    image=self.emptyImage
                    self.build['boffs'][boffSan] = [None] * 4
                canvas = Canvas(bSubFrame1, highlightthickness=0, borderwidth=0, width=25, height=35, bg='gray')
                canvas.grid(row=1, column=i, sticky='ns', padx=2, pady=2)
                img0 = canvas.create_image(0,0, anchor="nw",image=image)
                canvas.bind('<Button-1>', lambda e,canvas=canvas,img=img0,i=i,key=boffSan,idx=idx,environment=environment,v=v,v2=v2,callback=self.boffLabelCallback:callback(e,canvas,img,i,key,[v.get(), v2.get(), i], idx, environment))
                canvas.bind('<Enter>', lambda e,item=self.build['boffs'][boffSan][i],environment=environment:self.setupInfoboxFrame(item, '', environment))
            idx = idx + 1

    def setupSpaceBuildFrames(self):
        """Set up all relevant space build frames"""
        self.build['tier'] = self.backend['tier'].get()
        if self.backend['shipHtml'] is not None:
            self.setupShipBuildFrame(self.backend['shipHtml'])
            self.setupSpaceBoffFrame(self.backend['shipHtml'])
        else:
            self.clearFrame(self.shipEquipmentFrame)
            self.clearFrame(self.shipBoffFrame)
            self.clearFrame(self.shipTierFrame)
        self.setupDoffFrame(self.shipDoffFrame)
        self.setupSpaceTraitFrame()
        self.clearInfoboxFrame('space')

    def setupGroundBuildFrames(self):
        """Set up all relevant build frames"""
        self.build['tier'] = self.backend['tier'].get()
        self.setupCharBuildFrame()
        self.setupGroundBoffFrame()
        self.setupDoffFrame(self.groundDoffFrame)
        self.setupGroundTraitFrame()
        self.clearInfoboxFrame('ground')

    def setupSkillBuildFrames(self):
        """Set up all relevant build frames"""
        self.setupSkillMainFrame()
        self.clearInfoboxFrame('skill')

    def setupModFrame(self, frame, rarity, itemVar):
        """Set up modifier frame in equipment picker"""
        self.clearFrame(frame)
        n = self.rarities.index(rarity)
        itemVar['rarity'] = rarity
        itemVar['modifiers'] = ['']*n
        mods = sorted(self.fetchModifiers())
        for i in range(n):
            v = StringVar()
            v.trace_add('write', lambda v0,v1,v2,i=i,itemVar=itemVar,v=v:self.setListIndex(itemVar['modifiers'],i,v.get()))
            OptionMenu(frame, v, *mods).grid(row=0, column=i, sticky='n')

    def clearInfoboxFrame(self, environment):
        self.setupInfoboxFrame(self.getEmptyItem(), '', environment)
        
    def setupInfoboxFrame(self, item, key, environment='space'):
        """Set up infobox frame with given item"""
        
        if environment == 'skill':
            frame = self.skillInfoboxFrame
        elif environment == 'ground':
            frame = self.groundInfoboxFrame
        else:
            frame = self.shipInfoboxFrame
            
        if 'item' in item:
            name = item['item']
        else:
            name = item
        
        self.logWrite('Infobox('+environment+'): '+name+' -- '+key, 4)
        if key is not None and key != '':
            self.precacheEquipment(key)
        
        self.clearFrame(frame)
        Label(frame, text="STATS & OTHER INFO").pack(fill="both", expand=True)
        text = Text(frame, height=25, width=30, font=('Helvetica', 10), bg='#3a3a3a', fg='#ffffff')
        text.pack(fill="both", expand=True, padx=2, pady=2)
        if name is None or name == '':
            return
        self.logWrite('item: '+name, 4)
        
        text.insert(END, name)
        if 'mark' in item and item['mark']:
            text.insert(END, ' '+item['mark'])
        if 'modifiers' in item and item['modifiers']:
            text.insert(END, ' '+('' if item['modifiers'][0] is None else ''.join(item['modifiers'])))
        text.insert(END, '\n')
        
        if 'tooltip' in item and item['tooltip']:
            text.insert(END, html['tooltip'])
            
        if name in self.backend['cacheShipTraits']:
            text.insert(END, self.backend['cacheShipTraits'][name])

        if environment in self.backend['cacheTraits'] and name in self.backend['cacheTraits'][environment]:
            text.insert(END, self.backend['cacheTraits'][environment][name])
            
        if environment in self.backend['cacheBoffTooltips'] and name in self.backend['cacheBoffTooltips'][environment]:
                text.insert(END, self.backend['cacheBoffTooltips'][environment][name])
                
        if key in self.backend['cacheEquipment'] and name in self.backend['cacheEquipment'][key]:
            # Show the infobox data from json
            html = self.backend['cacheEquipment'][key][name]

            if 'rarity' in item and item['rarity']:
                text.insert(END, item['rarity']+' ')
            if 'type' in html and html['type']:
                text.insert(END, html['type'])
            if ('rarity' in item and item['rarity']) or ('type' in html and html['type']):
                text.insert(END, '\n')

            for i in range(1,9):
                for header in ["head", "subhead", "text"]:
                    t = html[header+str(i)].replace(":",'').strip()
                    if t.strip() != '':
                        text.insert(END, t+'\n')
                        
        text.configure(state=DISABLED)

    def setupDoffFrame(self, frame):
        self.clearFrame(frame)
        mainFrame = Frame(frame, bg='#3a3a3a')
        mainFrame.pack(side='left', fill=BOTH, expand=True)
        spaceDoffFrame = Frame(mainFrame, bg='#3a3a3a', padx=10)
        spaceDoffFrame.pack(side='left', fill=BOTH, expand=True)
        groundDoffFrame = Frame(mainFrame, bg='#3a3a3a', padx=10)
        groundDoffFrame.pack(side='right', fill=BOTH, expand=True)
        
        self.precacheDoffs("Space")
        doff_list_space = sorted([self.deWikify(item) for item in list(self.backend['cacheDoffNames']['Space'].keys())])
        
        spaceDoffLabel = Label(spaceDoffFrame, text="SPACE DUTY OFFICERS", bg='#3a3a3a', fg='#ffffff')
        spaceDoffLabel.grid(row=0, column=0, columnspan=3, sticky='nsew')
        
        f = font.Font(family='Helvetica', size=9)
        for i in range(6):
            v0 = StringVar(self.window)
            v1 = StringVar(self.window)
            v2 = StringVar(self.window)
            m = OptionMenu(spaceDoffFrame, v0, 'NAME', *['A','B','C'])
            m.grid(row=i+1, column=0, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0, state=DISABLED)
            m = OptionMenu(spaceDoffFrame, v1, 'SPECIALIZATION', *doff_list_space)
            m.grid(row=i+1, column=1, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0)
            m = OptionMenu(spaceDoffFrame, v2, 'EFFECT\nOTHER', '')
            m.grid(row=i+1, column=2, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0, width=20,font=f, wraplength=280)
            if self.build['doffs']['space'][i] is not None:
                v0.set(self.build['doffs']['space'][i]['name'])
                v1.set(self.build['doffs']['space'][i]['spec'])
                v2.set(self.build['doffs']['space'][i]['effect'])
                m['menu'].delete(0, END)
                doff_desclist_space = sorted([self.doffStripPrefix(self.backend['cacheDoffs']['Space'][item]['description'], True) for item in list(self.backend['cacheDoffs']['Space'].keys()) if v1.get() in self.backend['cacheDoffs']['Space'][item]['name']])
        
                for desc in doff_desclist_space:
                    m['menu'].add_command(label=desc, command=lambda v2=v2,value=desc: v2.set(value))
                        
            v1.trace_add("write", lambda v,i,m,menu=m,v0=v1,v1=v2,row=i:self.doffSpecCallback(menu, v0,v1, row, True))
            v2.trace_add("write", lambda v,i,m,menu=m,v0=v1,v1=v2,row=i:self.doffEffectCallback(menu, v0,v1, row, True))

        spaceDoffFrame.grid_columnconfigure(2, weight=1, uniform="spaceDoffList")
        
        self.precacheDoffs("Ground")
        doff_list_ground = sorted([self.deWikify(item) for item in list(self.backend['cacheDoffNames']['Ground'].keys())])
        
        Label(groundDoffFrame, text="GROUND DUTY OFFICERS", bg='#3a3a3a', fg='#ffffff').grid(row=0, column=0,columnspan=3, sticky='nsew')
        for i in range(6):
            v0 = StringVar(self.window)
            v1 = StringVar(self.window)
            v2 = StringVar(self.window)
            m = OptionMenu(groundDoffFrame, v0, 'NAME', *['A','B','C'])
            m.grid(row=i+1, column=0, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0, state=DISABLED)
            m = OptionMenu(groundDoffFrame, v1, 'SPECIALIZATION', *doff_list_ground)
            m.grid(row=i+1, column=1, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0)
            m = OptionMenu(groundDoffFrame, v2, 'EFFECT\nOTHER', '')
            m.grid(row=i+1, column=2, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0, width=20, font=f, wraplength=280)
            if self.build['doffs']['ground'][i] is not None:
                v0.set(self.build['doffs']['ground'][i]['name'])
                v1.set(self.build['doffs']['ground'][i]['spec'])
                v2.set(self.build['doffs']['ground'][i]['effect'])
                m['menu'].delete(0, END)
                
                doff_desclist_ground = sorted([self.doffStripPrefix(self.backend['cacheDoffs']['Ground'][item]['description'], False) for item in list(self.backend['cacheDoffs']['Ground'].keys()) if v1.get() in self.backend['cacheDoffs']['Ground'][item]['name']])
        
                for desc in doff_desclist_ground:
                    m['menu'].add_command(label=desc, command=lambda v2=v2,value=desc: v2.set(value))

            v1.trace_add("write", lambda v,i,m,menu=m,v0=v1,v1=v2,row=i:self.doffSpecCallback(menu, v0,v1,row, False))
            v2.trace_add("write", lambda v,i,m,menu=m,v0=v1,v1=v2,row=i:self.doffEffectCallback(menu, v0,v1, row, False))

        groundDoffFrame.grid_columnconfigure(2, weight=1, uniform="groundDoffList")

    def setupLogoFrame(self):
        self.clearFrame(self.logoFrame)
        
        logoWidth = 1920
        logoHeight = 134
        maxWidth = self.window.winfo_screenwidth()
        if maxWidth > logoWidth:
            maxWidth = logoWidth
        self.images['logoImage'] = self.loadLocalImage("logo_bar.png", maxWidth, int(maxWidth/logoWidth * logoHeight))
        
        Label(self.logoFrame, image=self.images['logoImage'], borderwidth=0, highlightthickness=0).pack()

    def setupFooterFrame(self):
        self.footerFrame = Frame(self.containerFrame, bg='#c59129', height=20)
        footerLabelL = Label(self.footerFrame, textvariable=self.log, fg='#3a3a3a', bg='#c59129', anchor='w', font=('Helvetica', 8, 'bold'))
        footerLabelL.grid(row=0, column=0, sticky='w')
        footerLabelR = Label(self.footerFrame, textvariable=self.logmini, fg='#3a3a3a', bg='#c59129', anchor='e', font=('Helvetica', 8, 'bold'))
        footerLabelR.grid(row=0, column=1, sticky='e')
        self.footerFrame.grid_columnconfigure(0, weight=5, uniform="footerlabel")
        self.footerFrame.grid_columnconfigure(1, weight=1, uniform="footerlabel")
        self.footerFrame.pack(fill='both', side='bottom', expand=True)
        
        
    def lineTruncate(self, content, length=500):
        return '\n'.join(content.split('\n')[-1*length:])
        
    def setFooterFrame(self, leftnote, rightnote=None):
        """Set up footer frame with given item"""

        if not len(leftnote):
            self.log.set(self.log.get())
        else:
            self.log.set(leftnote)
            
        if not len(rightnote):
            self.logmini.set(self.logmini.get())
        else:
            self.logmini.set(rightnote)

        # Force update for assured data display
        #self.window.update()
        

    def setupMenuFrame(self):
        self.clearFrame(self.menuFrame)
        f = font.Font(family='Helvetica', size=12, weight='bold')
        buttonSpace = Button(self.menuFrame, text="SPACE", bg='#6b6b6b', fg='#ffffff', font=f, command=self.focusSpaceBuildFrameCallback)
        buttonSpace.grid(row=0, column=0, sticky='nsew')
        buttonGround = Button(self.menuFrame, text="GROUND", bg='#6b6b6b', fg='#ffffff', font=f, command=self.focusGroundBuildFrameCallback)
        buttonGround.grid(row=0, column=1, sticky='nsew')
        buttonSkill = Button(self.menuFrame, text="SKILL TREE", bg='#6b6b6b', fg='#ffffff', font=f, command=self.focusSkillTreeFrameCallback)
        buttonSkill.grid(row=0, column=2, sticky='nsew')
        buttonLibrary = Button(self.menuFrame, text="LIBRARY", bg='#6b6b6b', fg='#ffffff', font=f, command=self.focusGlossaryFrameCallback)
        buttonLibrary.grid(row=0, column=3, sticky='nsew')
        buttonSettings = Button(self.menuFrame, text="SETTINGS", bg='#6b6b6b', fg='#ffffff', font=f, command=self.focusSettingsFrameCallback)
        buttonSettings.grid(row=0, column=4, sticky='nsew')
        for i in range(5):
            self.menuFrame.grid_columnconfigure(i, weight=1, uniform="mainCol")

    def setupJustTierFrame(self, tier):
        Label(self.shipTierFrame, text="Tier:", fg='#3a3a3a', bg='#b3b3b3').grid(row=0, column=0, sticky='nsew')
        m = OptionMenu(self.shipTierFrame, self.backend["tier"], *self.getTierOptions(tier))
        m.grid(column=1, row=0, sticky='nsew', pady=5)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
        
    def setupTierFrame(self, tier):
        self.setupJustTierFrame(tier)
        self.backend['shipHtml'] = self.getShipFromName(self.r_ships, self.build['ship'])
        try:
            ship_image = self.backend['shipHtml']["image"]
            self.shipImg = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/"+ship_image.replace(' ','_'), self.build['ship'], 260, 146)
            self.shipLabel.configure(image=self.shipImg)
        except:
            self.shipImg = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/Federation_Emblem.png", "federation_emblem", 260, 146)
            self.shipLabel.configure(image=self.shipImg)

    def setupButtonExportImportFrame(self, frame):
        exportImportFrame = Frame(frame)
        exportImportFrame.pack(fill=BOTH, expand=True)
        buttonExport = Button(exportImportFrame, text='Export', bg='#3a3a3a',fg='#b3b3b3', command=self.exportCallback)
        buttonExport.pack(side='left', fill=BOTH, expand=True)
        buttonImport = Button(exportImportFrame, text='Import', bg='#3a3a3a',fg='#b3b3b3', command=self.importCallback)
        buttonImport.pack(side='left', fill=BOTH, expand=True)
        buttonClear = Button(exportImportFrame, text='Clear', bg='#3a3a3a',fg='#b3b3b3', command=self.clearBuildCallback)
        buttonClear.pack(side='left', fill=BOTH, expand=True)
        buttonExportPng = Button(exportImportFrame, text='Export .png', bg='#3a3a3a',fg='#b3b3b3', command=self.exportPngCallback)
        buttonExportPng.pack(side='left', fill=BOTH, expand=True)
        buttonExportReddit = Button(exportImportFrame, text='Export reddit', bg='#3a3a3a',fg='#b3b3b3', command=self.exportRedditCallback)
        buttonExportReddit.pack(side='left', fill=BOTH, expand=True)
    
    def setupTagsAndCharFrame(self, frame):
        tagsAndCharFrame = Frame(frame, bg='#b3b3b3')
        tagsAndCharFrame.pack(fill=X, expand=True, padx=2, side=BOTTOM)
        tagsAndCharFrame.grid_columnconfigure(0, weight=1)
        tagsAndCharFrame.grid_columnconfigure(1, weight=1)
        buildTagFrame = Frame(tagsAndCharFrame, bg='#b3b3b3')
        buildTagFrame.grid(row=0, column=0, sticky='sew')
        charInfoFrame = Frame(tagsAndCharFrame, bg='#b3b3b3')
        charInfoFrame.grid(row=0, column=1, sticky='sew')
        Label(buildTagFrame, text="BUILD TAGS", fg='#3a3a3a', bg='#b3b3b3').pack(fill=X, expand=False)
        for tag in ["DEW", "KINETIC", "EPG", "DEWSCI", "THEME"]:
            tagFrame = Frame(buildTagFrame, bg='#b3b3b3')
            tagFrame.pack(fill=X, expand=False)
            v = IntVar(self.window, value=(1 if tag in self.build['tags'] and self.build['tags'][tag] == 1 else 0))
            Checkbutton(tagFrame, variable=v, fg='#3a3a3a', bg='#b3b3b3').grid(row=0,column=0)
            v.trace_add("write", lambda v,i,m,var=v,text=tag:self.tagBoxCallback(var,text))
            Label(tagFrame, text=tag, fg='#3a3a3a', bg='#b3b3b3').grid(row=0,column=1)

        Label(charInfoFrame, text="Elite Captain", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = 0, sticky='e')
        m = Checkbutton(charInfoFrame, variable=self.backend["eliteCaptain"], fg='#3a3a3a', bg='#b3b3b3', command=self.eliteCaptainCallback)
        m.grid(column=1, row=0, sticky='swe', pady=2, padx=2)
        m.configure(fg='#3a3a3a', bg='#b3b3b3', borderwidth=0, highlightthickness=0)

        Label(charInfoFrame, text="Captain Career", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = 1, sticky='e')
        m = OptionMenu(charInfoFrame, self.backend["career"], "", "Tactical", "Engineering", "Science")
        m.grid(column=1, row=1, sticky='swe', pady=2, padx=2)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
        
        Label(charInfoFrame, text="Species", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = 2, sticky='e')
        m = OptionMenu(charInfoFrame, self.backend["species"], *self.speciesNames)
        m.grid(column=1, row=2, sticky='swe', pady=2, padx=2)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
        
        Label(charInfoFrame, text="Primary Spec", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = 3, sticky='e')
        m = OptionMenu(charInfoFrame, self.backend["specPrimary"], '', *self.specNames)
        m.grid(column=1, row=3, sticky='swe', pady=2, padx=2)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
        
        Label(charInfoFrame, text="Secondary Spec", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = 4, sticky='e')
        m = OptionMenu(charInfoFrame, self.backend["specSecondary"], '', *self.specNames)
        m.grid(column=1, row=4, sticky='swe', pady=2, padx=2)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
        
        charInfoFrame.grid_columnconfigure(1, weight=1, uniform="captColSpace")
        
    def updateShipDesc(self, event):
        self.build['playerShipDesc'] = self.shipDescText.get("1.0", END)
    
    def updatePlayerDesc(self, event):
        self.build['playerDesc'] = self.charDescText.get("1.0", END)
        
    def setupShipInfoFrame(self):
        self.clearFrame(self.shipInfoFrame)
        playerShipNameFrame = Frame(self.shipInfoFrame, bg='#b3b3b3')
        playerShipNameFrame.pack(fill=BOTH, expand=False)
        Label(playerShipNameFrame, text="SHIP NAME:", fg='#3a3a3a', bg='#b3b3b3').grid(row=0, column=0, sticky='nsew')
        Entry(playerShipNameFrame, textvariable=self.backend['playerShipName'], fg='#3a3a3a', bg='#b3b3b3', font=('Helvetica', 10, 'bold')).grid(row=0, column=1, sticky='nsew', ipady=5, pady=10)
        playerShipNameFrame.grid_columnconfigure(1, weight=1)
        
        self.setupButtonExportImportFrame(self.shipInfoFrame)
        
        shipLabelFrame = Frame(self.shipInfoFrame, bg='#b3b3b3')
        shipLabelFrame.pack(fill=BOTH, expand=True)
        self.shipLabel = Label(shipLabelFrame, fg='#3a3a3a', bg='#b3b3b3')
        self.shipLabel.pack(fill=BOTH, expand=True)
        shipNameFrame = Frame(self.shipInfoFrame, bg='#b3b3b3')
        shipNameFrame.pack(fill=BOTH, expand=True, padx=2)
        Label(shipNameFrame, text="Ship: ", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = 0, sticky='nwse')
        self.shipButton = Button(shipNameFrame, text="<Pick>", command=self.shipPickButtonCallback, bg='#b3b3b3', wraplength=280)
        self.shipButton.grid(column=1, row=0, sticky='nwse')
        shipNameFrame.grid_columnconfigure(1, weight=1)
        self.shipTierFrame = Frame(shipNameFrame, bg='#b3b3b3')
        self.shipTierFrame.grid(column=2, row=0, sticky='e')
        
        shipDescFrame = Frame(self.shipInfoFrame, bg='#b3b3b3')
        shipDescFrame.pack(fill=BOTH, expand=True, padx=2)
        Label(shipDescFrame, text="Desc:", fg='#3a3a3a', bg='#b3b3b3').grid(row=0, column=0, sticky='nw')
        # Hardcoded width due to issues with expansion, this should become dynamic here and in ground at some point
        self.shipDescText = Text(shipDescFrame, height=3, width=46, wrap=WORD, fg='#3a3a3a', bg='#b3b3b3', font=('Helvetica', 8, 'bold'))
        self.shipDescText.grid(row=0, column=1, sticky='nsw', pady=2, padx=2)
        self.shipDescText.bind('<KeyRelease>', self.updateShipDesc)
        if 'playerShipDesc' in self.build:
            self.shipDescText.delete(1.0, END)
            self.shipDescText.insert(1.0, self.build['playerShipDesc'])
        
        self.setupTagsAndCharFrame(self.shipInfoFrame)
        
        if self.build['ship'] is not None:
            self.shipButton.configure(text=self.build['ship'])

    def setupGroundInfoFrame(self):
        self.clearFrame(self.groundInfoFrame)
        playerGroundNameFrame = Frame(self.groundInfoFrame, bg='#b3b3b3')
        playerGroundNameFrame.pack(fill=BOTH, expand=False)
        Label(playerGroundNameFrame, text="PLAYER NAME:", fg='#3a3a3a', bg='#b3b3b3').grid(row=0, column=0, sticky='nsew')
        Entry(playerGroundNameFrame, textvariable=self.backend['playerName'], fg='#3a3a3a', bg='#b3b3b3', font=('Helvetica', 10, 'bold')).grid(row=0, column=1, sticky='nsew', ipady=5, pady=10)
        playerGroundNameFrame.grid_columnconfigure(1, weight=1)
        
        self.setupButtonExportImportFrame(self.groundInfoFrame)
        
        charLabelFrame = Frame(self.groundInfoFrame, bg='#b3b3b3')
        charLabelFrame.pack(fill=BOTH, expand=True)
        self.charLabel = Label(charLabelFrame, fg='#3a3a3a', bg='#b3b3b3', height=5)
        self.charLabel.pack(fill=BOTH, expand=True)
        
        charDescFrame = Frame(self.groundInfoFrame, bg='#b3b3b3')
        charDescFrame.pack(fill=BOTH, expand=True, padx=2)
        Label(charDescFrame, text="Desc (G):", fg='#3a3a3a', bg='#b3b3b3').grid(row=0, column=0, sticky='nw')
        self.charDescText = Text(charDescFrame, height=3, width=43, wrap=WORD, fg='#3a3a3a', bg='#b3b3b3', font=('Helvetica', 8, 'bold'))
        self.charDescText.grid(row=0, column=1, sticky='nsw', pady=2, padx=2)
        self.charDescText.bind('<KeyRelease>', self.updatePlayerDesc)
        if 'playerShipDesc' in self.build:
            self.charDescText.delete(1.0, END)
            self.charDescText.insert(1.0, self.build['playerDesc'])
        
        self.setupTagsAndCharFrame(self.groundInfoFrame)


    def setupSkillInfoFrame(self):
        self.clearFrame(self.skillInfoFrame)

    def setupSpaceBuildFrame(self):
        self.shipInfoFrame = Frame(self.spaceBuildFrame, bg='#b3b3b3')
        self.shipInfoFrame.grid(row=0,column=0,sticky='nsew',rowspan=2, pady=5)
        self.shipImg = self.emptyImage
        self.shipMiddleFrame = Frame(self.spaceBuildFrame, bg='#3a3a3a')
        self.shipMiddleFrame.grid(row=0,column=1,columnspan=3,sticky='nsew', pady=5)
        self.shipMiddleFrameUpper = Frame(self.shipMiddleFrame, bg='#3a3a3a')
        self.shipMiddleFrameUpper.grid(row=0,column=0,columnspan=3,sticky='nsew')
        self.shipEquipmentFrame = Frame(self.shipMiddleFrameUpper, bg='#3a3a3a')
        self.shipEquipmentFrame.pack(side='left', fill=BOTH, expand=True, padx=20)
        self.shipBoffFrame = Frame(self.shipMiddleFrameUpper, bg='#3a3a3a')
        self.shipBoffFrame.pack(side='left', fill=BOTH, expand=True)
        self.shipTraitFrame = Frame(self.shipMiddleFrameUpper, bg='#3a3a3a')
        self.shipTraitFrame.pack(side='left', fill=BOTH, expand=True)
        self.shipMiddleFrameLower = Frame(self.shipMiddleFrame, bg='#3a3a3a')
        self.shipMiddleFrameLower.grid(row=1,column=0,columnspan=3,sticky='nsew')
        self.shipDoffFrame = Frame(self.shipMiddleFrameLower, bg='#3a3a3a')
        self.shipDoffFrame.pack(fill=BOTH, expand=True, padx=20)
        self.shipInfoboxFrame = Frame(self.spaceBuildFrame, bg='#b3b3b3')
        self.shipInfoboxFrame.grid(row=0,column=4,rowspan=2,sticky='nsew', pady=5)
        for i in range(5):
            self.spaceBuildFrame.grid_columnconfigure(i, weight=1, uniform="mainColSpace")
        self.shipMiddleFrame.grid_columnconfigure(0, weight=1, uniform="secColSpace")
        self.shipMiddleFrame.grid_columnconfigure(1, weight=1, uniform="secColSpace")
        self.shipMiddleFrame.grid_columnconfigure(2, weight=1, uniform="secColSpace")
        self.shipMiddleFrameLower.grid_columnconfigure(0, weight=1, uniform="secColSpace2")

    def setupGroundBuildFrame(self):
        self.groundInfoFrame = Frame(self.groundBuildFrame, bg='#b3b3b3')
        self.groundInfoFrame.grid(row=0,column=0,sticky='nsew',rowspan=2, pady=5)
        self.groundImg = self.emptyImage
        self.groundMiddleFrame = Frame(self.groundBuildFrame, bg='#3a3a3a')
        self.groundMiddleFrame.grid(row=0,column=1,columnspan=3,sticky='nsew', pady=5)
        self.groundMiddleFrameUpper = Frame(self.groundMiddleFrame, bg='#3a3a3a')
        self.groundMiddleFrameUpper.grid(row=0,column=1,columnspan=3,sticky='nsew')
        self.groundEquipmentFrame = Frame(self.groundMiddleFrameUpper, bg='#3a3a3a')
        self.groundEquipmentFrame.pack(side='left', fill=BOTH, expand=True, padx=20)
        self.groundBoffFrame = Frame(self.groundMiddleFrameUpper, bg='#3a3a3a')
        self.groundBoffFrame.pack(side='left', fill=BOTH, expand=True)
        self.groundTraitFrame = Frame(self.groundMiddleFrameUpper, bg='#3a3a3a')
        self.groundTraitFrame.pack(side='left', fill=BOTH, expand=True)
        self.groundMiddleFrameLower = Frame(self.groundMiddleFrame, bg='#3a3a3a')
        self.groundMiddleFrameLower.grid(row=1,column=0,columnspan=5,sticky='nsew')
        self.groundDoffFrame = Frame(self.groundMiddleFrameLower, bg='#3a3a3a')
        self.groundDoffFrame.pack(fill=BOTH, expand=True, padx=20)
        self.groundInfoboxFrame = Frame(self.groundBuildFrame, bg='#b3b3b3')
        self.groundInfoboxFrame.grid(row=0,column=4,rowspan=2,sticky='nsew', pady=5)
        for i in range(5):
            self.groundBuildFrame.grid_columnconfigure(i, weight=1, uniform="mainColGround")
        self.groundMiddleFrame.grid_columnconfigure(0, weight=1, uniform="secColGround")
        self.groundMiddleFrame.grid_columnconfigure(1, weight=1, uniform="secColGround")
        self.groundMiddleFrame.grid_columnconfigure(2, weight=1, uniform="secColGround")
        self.groundMiddleFrameLower.grid_columnconfigure(0, weight=1, uniform="secColGround2")
        self.setupGroundBuildFrames()

    def setupSkillTreeFrame(self):
        self.skillInfoFrame = Frame(self.skillTreeFrame, bg='#b3b3b3')
        self.skillInfoFrame.grid(row=0,column=0,sticky='nsew',rowspan=2, pady=5)
        self.skillMiddleFrame = Frame(self.skillTreeFrame, bg='#3a3a3a')
        self.skillMiddleFrame.grid(row=0,column=1,columnspan=3,sticky='nsew', pady=5)
        self.skillInfoboxFrame = Frame(self.skillTreeFrame, bg='#b3b3b3')
        self.skillInfoboxFrame.grid(row=0,column=4,rowspan=2,sticky='nsew', pady=5)
        for i in range(5):
            self.skillTreeFrame.grid_columnconfigure(i, weight=1, uniform="mainColSkill")
        self.setupSkillBuildFrames()

    def setupLibraryFrame(self):
        pass #placeholder

    def setupSettingsFrame(self):
        self.settingsTopFrame = Frame(self.settingsFrame, bg='#b3b3b3')
        self.settingsTopFrame.pack(side='top', fill=BOTH, expand=True)
        self.settingsBottomFrame = Frame(self.settingsFrame, bg='#b3b3b3')
        self.settingsBottomFrame.pack(side='bottom', fill=BOTH, expand=True)
        
        self.settingsTopLeftFrame = Frame(self.settingsTopFrame, bg='#b3b3b3')
        self.settingsTopLeftFrame.grid(row=0,column=0,sticky='nsew', pady=5)
        self.settingsTopMiddleLeftFrame = Frame(self.settingsTopFrame, bg='#b3b3b3')
        self.settingsTopMiddleLeftFrame.grid(row=0,column=1,sticky='nsew', pady=5)
        self.settingsTopMiddleRightFrame = Frame(self.settingsTopFrame, bg='#b3b3b3')
        self.settingsTopMiddleRightFrame.grid(row=0,column=2,sticky='nsew', pady=5)
        self.settingsTopRightFrame = Frame(self.settingsTopFrame, bg='#b3b3b3')
        self.settingsTopRightFrame.grid(row=0,column=3,sticky='nsew', pady=5)
        
        self.settingsTopFrame.grid_columnconfigure(0, weight=6, uniform="settingsColSpace")
        self.settingsTopFrame.grid_columnconfigure(1, weight=2, uniform="settingsColSpace")
        self.settingsTopFrame.grid_columnconfigure(2, weight=1, uniform="settingsColSpace")
        self.settingsTopFrame.grid_columnconfigure(3, weight=2, uniform="settingsColSpace")
        
        self.logDisplay = Text(self.settingsTopLeftFrame, bg='#3a3a3a', fg='#ffffff', wrap=WORD, height=30, width=120)
        self.logDisplay.grid(row=0, column=0, columnspan=2, sticky="n")
        self.logDisplay.insert('0.0', self.logFull.get())
        
        label = Label(self.settingsTopMiddleLeftFrame, text='Default settings (auto-saved)', fg='#3a3a3a', bg='#b3b3b3', font=('Helvetica',14))
        label.grid(row=0, column=0, columnspan=2, sticky="n")
        label = Label(self.settingsTopMiddleLeftFrame, text='Mark', fg='#3a3a3a', bg='#b3b3b3')
        label.grid(row=1, column=0, sticky="e", pady=2, padx=2)
        mark = StringVar(value=self.persistent['markDefault'])
        markOption = OptionMenu(self.settingsTopMiddleLeftFrame, mark, *self.marks, command=self.persistentMark)
        markOption.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0, width=10)
        markOption.grid(row=1, column=1, sticky='nw', pady=2, padx=2)
        label = Label(self.settingsTopMiddleLeftFrame, text='Rarity', fg='#3a3a3a', bg='#b3b3b3')
        label.grid(row=2, column=0, sticky="e", pady=2, padx=2)
        rarity = StringVar(value=self.persistent['rarityDefault'])
        raritiesDefault = [""]+self.rarities
        rarityOption = OptionMenu(self.settingsTopMiddleLeftFrame, rarity, *raritiesDefault, command=self.persistentRarity)
        rarityOption.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0, width=10)
        rarityOption.grid(row=2, column=1, sticky='nw', pady=2, padx=2)
        
        label = Label(self.settingsTopRightFrame, text='Maintenance', fg='#3a3a3a', bg='#b3b3b3', font=('Helvetica',14))
        label.grid(row=0, column=0, columnspan=2, sticky="n")
        buttonInvalidateCache = Button(self.settingsTopRightFrame, text='Clear data cache (automatic download)', bg='#3a3a3a',fg='#b3b3b3')
        buttonInvalidateCache.grid(row=1, column=0, columnspan=2, sticky='nwe', pady=2, padx=2)
        buttonInvalidateCache.bind('<Button-1>', lambda e:self.cacheInvalidateCallback(dir="cache"))
        buttonInvalidateImages = Button(self.settingsTopRightFrame, text='VERY SLOW! Clear image cache (automatic download)', bg='#3a3a3a',fg='#b3b3b3')
        buttonInvalidateImages.grid(row=2, column=0, columnspan=2, sticky='nwe', pady=2, padx=2)
        buttonInvalidateImages.bind('<Button-1>', lambda e:self.cacheInvalidateCallback(dir="images"))
        buttonExportSettings = Button(self.settingsTopRightFrame, text='Export SETS manual settings', bg='#3a3a3a',fg='#b3b3b3', command=self.exportSettings)
        buttonExportSettings.grid(row=3, column=0, columnspan=2, sticky='nwe', pady=2, padx=2)

        label = Label(self.settingsTopRightFrame, text='Force out of date JSON loading', fg='#3a3a3a', bg='#b3b3b3')
        label.grid(row=4, column=0, sticky="e", pady=2, padx=2)        
        forceLoad = StringVar(value='Yes' if self.persistent['forceJsonLoad'] else 'No')
        forceLoadOptions = ["Yes", "No"]
        forceLoadOption = OptionMenu(self.settingsTopRightFrame, forceLoad, *forceLoadOptions, command=self.persistentForceLoad)
        forceLoadOption.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0, width=10)
        forceLoadOption.grid(row=4, column=1, sticky='nw', pady=2, padx=2)


    def setupUIScaling(self, scale):
         # pixel correction
        dpi = round(self.window.winfo_fpixels('1i'), 0)
        factor = ( dpi / 96 ) * scale
        self.window.call('tk', 'scaling', factor)
        
        self.logminiWrite('{:>4}dpi (x{:>4}) '.format(dpi, (factor * scale)))
        
    def logDisplayUpdate(self):
        self.logDisplay.delete('0.0', END)
        self.logDisplay.insert('0.0', self.logFull.get())
        self.logDisplay.yview_pickplace(END)
        
    def logFullWrite(self, notice):
        self.logFull.set(self.lineTruncate(self.logFull.get()+'\n'+notice))
    
    def logminiWrite(self, notice, level=0):
        if level == 0:
            self.setFooterFrame('', notice)
        if self.settings['debug'] > 0 and self.settings['debug'] >= level:
            sys.stderr.write('info: '+notice+'\n')
            
    def logWrite(self, notice, level=0):
        # Level 0: Default, always added to short log note frame on UI
        # Higher than 0 will not be added to short log note (but will be in the full log)
        # Log levels uses are just suggestions
        # Level 1: Track interactions - network interactions, configuration actions, file transactions
        # Level 2: unconfirmed feature spam -- chatty but not intended to fully retained long term
        # Level 3: minor detail spam -- any useful long-term diagnostics
        if level == 0:
            self.setFooterFrame(notice, '')
            self.logFullWrite(notice)
        if self.settings['debug'] > 0 and self.settings['debug'] >= level:
            sys.stderr.write(notice)
            sys.stderr.write('\n')
            self.logFullWrite(notice)

    def setupUIFrames(self):
        defaultFont = font.nametofont('TkDefaultFont')
        defaultFont.configure(family='Helvetica', size='10')

        self.containerFrame = Frame(self.window, bg='#c59129')
        self.containerFrame.pack(fill=BOTH, expand=True)
        self.logoFrame = Frame(self.containerFrame, bg='#c59129')
        self.logoFrame.pack(fill=X)
        self.menuFrame = Frame(self.containerFrame, bg='#c59129')
        self.menuFrame.pack(fill=X, padx=15)
        self.spaceBuildFrame = Frame(self.containerFrame, bg='#3a3a3a')
        self.groundBuildFrame = Frame(self.containerFrame, bg='#3a3a3a', height=600)
        self.skillTreeFrame = Frame(self.containerFrame, bg='#3a3a3a', height=600)
        self.glossaryFrame = Frame(self.containerFrame, bg='#3a3a3a', height=600)
        self.settingsFrame = Frame(self.containerFrame, bg='#3a3a3a', height=600)
        self.spaceBuildFrame.pack(fill=BOTH, expand=True, padx=15)
        self.setupFooterFrame()
        self.setupUIScaling(1)
        
        self.setupLogoFrame()
        self.setupMenuFrame()
        self.setupSpaceBuildFrame()
        self.setupGroundBuildFrame()
        self.setupSkillTreeFrame()
        self.setupLibraryFrame()
        self.setupSettingsFrame()
        self.setupShipInfoFrame()
        self.setupGroundInfoFrame()
        self.setupSkillInfoFrame()
        
        if self.args.file is not None and os.path.exists(self.args.file):
            self.importByFilename(self.args.file)
        else:
            self.templateFileLoad()
            
        self.setupSpaceBuildFrames()

    def argParserSetup(self):
        parser = argparse.ArgumentParser(description='A Star Trek Online build tool')
        parser.add_argument('--configfile', type=int, help='Set configuration file (must be .JSON)')
        parser.add_argument('--configfolder', type=int, help='Set configuration folder (contains config file, state file, default library location')
        parser.add_argument('--debug', type=int, help='Set debug level (default: 0)')
        parser.add_argument('--file', type=str, help='File to import on open')

        self.args = parser.parse_args()
        
        if self.args.debug is not None:
            self.settings['debug'] = self.args.debug
            self.logWrite('Debug set by arg: '+str(self.settings['debug']), 1)
            
        if self.args.configfile is not None:
            self.fileConfigName = self.args.configfile

        if self.args.configfolder is not None:
            self.folderConfigName = self.args.configfolder

    def configLocation(self):
        # This should probably be upgraded to use the appdirs module, adding rudimentary options for the moment
        system = sys.platform
        if os.path.exists(self.fileConfigName):
            # We already have a config file in the app home directory, use portable mode
            filePath=''
        elif os.path.exists(self.folderConfigName):
            filePath = os.path.join(self.folderConfigName, self.fileConfigName)
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
            
        if filePath != '' and not os.path.exists(filePath):
            self.logWrite('makedirs: '+filePath, 2)
            try:
                errMakeDirs = os.makedirs(filePath)
            except:
                self.logWrite(filePath+" -- makedirs failed", 2)
        
        return filePath

    def configFileLocation(self):
        filePath = self.configLocation()
        
        if os.path.exists(filePath):
            fileName = os.path.join(filePath, self.fileConfigName)
        else:
            fileName = self.fileConfigName
        
        return fileName
        
    def stateFileLocation(self):
        filePath = self.configLocation()
        
        if os.path.exists(filePath):
            fileName = os.path.join(filePath, self.fileStateName)
            if not os.path.exists(fileName):
                open(fileName, 'w').close()
        else:
            fileName = self.fileStateName
        
        return fileName
        
    def templateFileLocation(self):
        filePath = self.configLocation()
        
        if os.path.exists(filePath):
            fileName = os.path.join(filePath, self.settings['template'])
        else:
            fileName = self.settings['template']
        
        return fileName
    
    def configFileLoad(self):
        # Currently JSON, but ideally changed to a user-commentable format (YAML, TOML, etc)
        configFile = self.configFileLocation()
        if not os.path.exists(configFile):
            configFile = self.fileConfigName
            
        if os.path.exists(configFile) and os.path.getsize(configFile) > 0:
            self.logWrite(configFile+' -- config file found', 1)
            with open(configFile, 'r') as inFile:
                try:
                    settingsNew = json.load(inFile)
                    logNote = ' (fields:['+str(len(settingsNew))+'=>'+str(len(self.settings))+']='
                    self.settings.update(settingsNew)
                    logNote = logNote + str(len(self.settings)) + ')'
                    self.logWrite(configFile+' -- config file loaded' + logNote)
                except:
                    self.logWrite(configFile+' -- file load error')
                    
                if self.args.debug:
                    self.settings['debug'] = self.args.debug
                elif not 'debug' in self.settings or self.debugDefault > self.settings['debug']:
                    self.settings['debug'] = self.debugDefault
                self.logWrite('Debug level is: '+str(self.settings['debug']), 1)
        else:
            self.logWrite(configFile+' -- config file not found or zero size', 1)
            
    def stateFileLoad(self):
        # Currently JSON, but ideally changed to a user-commentable format (YAML, TOML, etc)
        configFile = self.stateFileLocation()
        if not os.path.exists(configFile):
            configFile = self.fileStateName
            
        if os.path.exists(configFile):
            self.logWrite(configFile+' -- state file found', 1)
            with open(configFile, 'r') as inFile:
                try:
                    persistentNew = json.load(inFile)
                except:
                    self.logWrite(configFile+' -- file load error')
                    return
                logNote = ' (fields:['+str(len(persistentNew))+'=>'+str(len(self.persistent))+']='
                self.persistent.update(persistentNew)
                logNote = logNote + str(len(self.persistent)) + ')'
                self.logWrite(configFile+' -- state file loaded' + logNote)
        else:
            self.logWrite(configFile+' -- state file NOT found', 1)
 
    def persistentToBackend(self):
        # Nothing yet
        return
    
    def persistentMark(self, choice):
        self.persistent['markDefault'] = choice
        self.stateSave()
        
    def persistentRarity(self, choice):
        self.persistent['rarityDefault'] = choice
        self.stateSave()
        
    def persistentForceLoad(self, choice):
        self.persistent['forceJsonLoad'] = 1 if choice=='Yes' else 0
        self.stateSave()
            
    def stateSave(self):
        configFile = self.stateFileLocation()
        if not os.path.exists(configFile):
            configFile = self.fileStateName
            
        try:
            with open(configFile, "w") as outFile:
                json.dump(self.persistent, outFile)
                self.logWrite(outFile.name+' -- saved as state file')
        except AttributeError:
            self.logWrite(outFile.name+' -- save failure')
            pass
            
    def templateFileLoad(self):
        configFile = self.templateFileLocation()
        if not os.path.exists(configFile):
            configFile = self.settings['template']
            
        if os.path.exists(configFile):
            self.logWrite(configFile+' -- template file found', 2)
            with open(configFile, 'r') as inFile:
                try:
                    self.importByFilename(configFile)
                except:
                    self.logWrite(configFile+' -- file load error')
        else:
            self.logWrite(configFile+' -- config file NOT found', 2)

    def resetPersistent(self):
        # self.persistent will be auto-saved and auto-loaded for persistent state data
        self.persistent = {
            'markDefault': '',
            'rarityDefault': '',
            'forceJsonLoad': 0
        }
    
    def resetSettings(self):
        # self.settings are optionally loaded from config, but manually edited or saved
        self.settings = {
            'debug': self.debugDefault,
            'template': '.template.json'
        }
    
    def initSettings(self):
        """Initialize session settings state"""
        self.fileDebug = '.debug'
        self.debugDefault = 1 if os.path.exists(self.fileDebug) else 0
        
        # log and logmini are the bottom text, logFull provides a history
        self.log = StringVar()
        self.logmini = StringVar()
        self.logFull = StringVar()
        
        self.fileStateName = '.state_SETS.json'
        self.resetPersistent()

        self.fileConfigName = '.config.json'
        self.folderConfigName = '.config'
        self.resetSettings()

        self.logWrite('CWD: '+os.getcwd(), 1)
        
    def exportSettings(self):
        try:
            with filedialog.asksaveasfile(defaultextension=".json",filetypes=[("JSON file","*.json"),("All Files","*.*")]) as outFile:
                json.dump(self.settings, outFile)
                self.logWrite(outFile.name+' -- saved as config file')
        except AttributeError:
            pass
    
    def __init__(self) -> None:
        """Main setup function"""

        self.window = Tk()
        # Debug, CLI args, and config file loading
        self.initSettings()
        self.argParserSetup()
        self.stateFileLoad()
        self.stateSave()
        self.configFileLoad()
        
        # self.window.geometry('1280x650')
        self.window.iconphoto(False, PhotoImage(file='local/icon.PNG'))
        self.window.title("STO Equipment and Trait Selector")
        self.session = HTMLSession()
        self.clearBuild()
        self.clearBackend()
        self.hookBackend()
        self.images = dict()
        self.imagesFail = dict()
        self.rarities = ["Common", "Uncommon", "Rare", "Very rare", "Ultra rare", "Epic"]
        self.marks = ["", "Mk I", "Mk II", "Mk III", "Mk IIII", "Mk V", "Mk VI", "Mk VII", "Mk VIII", "Mk IX", "Mk X", "Mk XI", "Mk XII", "∞", "Mk XIII", "Mk XIV", "Mk XV"]
        self.emptyImage = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/Common_icon.png", "no_icon",self.itemBoxX,self.itemBoxY)
        self.infoboxes = self.fetchOrRequestJson(SETS.item_query, "infoboxes")
        self.traits = self.fetchOrRequestJson(SETS.trait_query, "traits")
        self.shiptraits = self.fetchOrRequestJson(SETS.ship_trait_query, "starship_traits")
        self.doffs = self.fetchOrRequestJson(SETS.doff_query, "doffs")
        self.r_boffAbilities_source = "https://sto.fandom.com/wiki/Bridge_officer_and_kit_abilities"
        r_species = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Category:Player_races", "species")
        self.speciesNames = [e.text for e in r_species.find('#mw-pages .mw-category-group .to_hasTooltip') if 'Guide' not in e.text and 'Player' not in e.text]
        r_specs = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Category:Captain_specializations", "specs")
        self.specNames = [e.text.replace(' (specialization)', '').replace(' Officer', '').replace(' Operative', '') for e in r_specs.find('#mw-pages .mw-category-group .to_hasTooltip') if '(specialization)' in e.text]
        self.boffGroundSpecNames = [ele for ele in self.specNames if ele not in {"Commando", "Constable", "Strategist", "Pilot"}]
        self.r_ships = self.fetchOrRequestJson(SETS.ship_query, "ship_list")
        self.precacheShips()
        
        self.setupUIFrames()

    def run(self):
        self.window.mainloop()

SETS().run()
