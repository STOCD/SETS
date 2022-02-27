from textwrap import fill
from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter.ttk import Progressbar
from requests.models import requote_uri
from requests_html import Element, HTMLSession, HTML
from PIL import Image, ImageTk, ImageGrab, PngImagePlugin
import os, requests, json, re, datetime, html, urllib.parse, ctypes, sys, argparse, time
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
    
    itemBoxX = 32 #25
    itemBoxY = 42 #33
    imageBoxX = 260
    imageBoxY = 146
    windowHeightDefault = 659 #634
    windowWidthDefault = 1920
    windowHeight = windowHeightDefault
    windowWidth = windowWidthDefault
    logoHeight = 134
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
        if local: cache_base = self.settings['folder']['local']
        else: cache_base = self.getFolderLocation('cache')
        override_base = self.getFolderLocation('override')
        if not os.path.exists(cache_base):
            return
            
        filename = os.path.join(*filter(None, [cache_base, designation]))+".json"
        filenameOverride = os.path.join(*filter(None, [override_base, designation]))+".json"
        if os.path.exists(filenameOverride):
            filename = filenameOverride
            
        if os.path.exists(filename):
            modDate = os.path.getmtime(filename)
            interval = datetime.datetime.now() - datetime.datetime.fromtimestamp(modDate)
            if interval.days < 7 or local:
                with open(filename, 'r', encoding='utf-8') as json_file:
                    json_data = json.load(json_file)
                    return json_data
            if interval.days >= 7: self.clearCacheFolder(designation+".json")
        elif local:
            return
        
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
        
    def imageResizeDimensions(self, imagewidth, imageheight, width, height):
        #deprecated
        aspectOld = round(imagewidth / imageheight, 2)
        aspectNew = round(width / height, 2)
        
        if width <= 100 or height <= 100:
            # Don't alter small icons
            pass
        elif aspectOld != aspectNew:
            newWidth = int(imagewidth / (imageheight / height))
        else:
            # matching aspects
            pass

        if width >= 100: self.logWrite("==={:4}->{:4} x {:4}->{:4} [{:4}->{:4}=={:4}]".format(imagewidth, width, imageheight, height, aspectOld, aspectNew, round(width / height, 2)), 2)
        return (width, height)
        
    def progressBarUpdate(self, weight=1):
        # weight denotes how much progress that item is
        try:
            self.footerProgressBarUpdates += weight
            self.footerProgressBar.step()
            # modulo to reduce time / flashing UI spent on updating
            if self.footerProgressBarUpdates % self.updateOnStep == 0 or self.footerProgressBarUpdates % self.updateOnStep + weight > self.updateOnHeavyStep:
                self.requestWindowUpdate('footerProgressBar')
        except:
            # Can have no footer yet in some early states
            pass
            
    def progressBarStop(self):
        self.footerProgressBarUpdates = 0
        self.footerProgressBar.stop()
        self.requestWindowUpdate('footerProgressBar')
        
    def progressBarStart(self):
        self.footerProgressBarUpdates = 0
        self.footerProgressBar.start()
    
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
        text = re.sub('\-([a-z])', self.titleCaseRegexpText, text)
        return text
    
    def fetchImage(self, url):
        today = datetime.date.today()
        if not self.args.allfetch and url in self.persistent['imagesFail'] and self.persistent['imagesFail'][url]:
            daysSinceFail = today - datetime.date.fromisoformat(self.persistent['imagesFail'][url])
            if daysSinceFail.days <= self.daysDelayBeforeReattempt:
                # Previously failed, do not attempt download again until next reattempt days have passed
                return None
            
        img_request = requests.get(url)
        self.logWriteTransaction('fetchImage', 'download', str(img_request.headers.get('Content-Length')), url, 1, [str(img_request.status_code)])
        
        if not img_request.ok:
            # No response on icon grab, mark for no downlaad attempt till restart
            self.persistent['imagesFail'][url] = today.isoformat()
            self.stateSave(quiet=True)
            return None

        return img_request.content
 
    
    def fetchOrRequestImage(self, url, designation, width = None, height = None, faction = None, forceAspect = False):
        """Request image from web or fetch from local cache"""
        cache_base = self.getFolderLocation('images')
        override_base = self.getFolderLocation('override')
        if not os.path.exists(cache_base):
            return
            
        self.logWriteTransaction('Image File', 'try', '----', url, 5, [designation, faction, forceAspect])
        image_data = None
        designation.replace("/", "_") # Missed by the path sanitizer
        designation = self.filePathSanitize(designation) # Probably should move to pathvalidate library
        factionCode = factionCodeDefault = '_(Federation)'
        if faction is not None and self.persistent['useFactionSpecificIcons']:
            if 'faction' in self.build['captain'] and self.build['captain']['faction'] != '':
                factionCode = '_('+self.build['captain']['faction']+')'
                
        extension = "jpeg" if url.endswith("jpeg") or url.endswith("jpg") else "png"
        fileextension = '.'+extension
        filename = filenameDefault = filenameNoFaction = os.path.join(*filter(None, [cache_base, designation]))+fileextension
        filenameOverride = os.path.join(*filter(None, [override_base, designation]))+fileextension
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
            
        if os.path.exists(filename):
            self.progressBarUpdate()  
        elif not self.args.nofetch:
            image_data = self.fetchImage(url)
            
            if image_data is None:
                url2 = self.iconNameCleanup(url)
                image_data = self.fetchImage(url2) if url2 != url else image_data

            if image_data is None:
                if factionCode in url:
                    url3 = re.sub(factionCode, factionCodeDefault, url)
                    filenameExisting = filenameNoFaction
                else:
                    url3 = re.sub('_icon', '_icon{}'.format(factionCode), url)
                    filenameExisting = filenameDefault
                    
                if not os.path.exists(filenameExisting):
                    image_data = self.fetchImage(url3) if url3 != url and url3 != url2 else image_data
                
                    if image_data is None:
                        url4 = self.iconNameCleanup(url3)
                        image_data = self.fetchImage(url4) if url4 != url3 and url4 != url and url4 != url2 else image_data
                    
        if os.path.exists(filenameExisting):
            self.progressBarUpdate(self.updateOnHeavyStep / 2)
            self.persistent['imagesFactionAliases'][filename] = filenameExisting
            self.logWriteTransaction('Image File', 'alias', '----', filename, 3, [filenameExisting])
            self.stateSave(quiet=True)
            filename = filenameExisting
            
        if image_data is not None:
            self.progressBarUpdate(self.updateOnHeavyStep)
            with open(filename, 'wb') as handler:
                handler.write(image_data)
            self.logWriteTransaction('Image File', 'write', len(str(os.path.getsize(filename))) if os.path.exists(filename) else '----', filename, 1)
        elif not os.path.exists(filename):
            self.progressBarUpdate(self.updateOnHeavyStep / 4)
            return self.emptyImage
  
        image = Image.open(filename)
        if(width is not None):
            #curwidth, curheight = image.size
            #resizeOptions = self.imageResizeDimensions(curwidth, curheight, width, height)
            if forceAspect: image = image.resize(resizeOptions,Image.ANTIALIAS)
            else: image.thumbnail((width, height), resample=Image.LANCZOS)
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
        textBlock = re.sub('\'"`UNIQ--nowiki-0000000.-QINU`"\'', '\*', textBlock)
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

    def precachePreload(self, limited=False):
        self.logWriteBreak('precachePreload START')
        self.precacheDownloads()
        self.precacheShips()
        self.precacheTemplates()
        if not limited:
            self.precacheBoffAbilities()
            self.precacheTraits()
            self.precacheShipTraits()
            self.precacheDoffs("Space")
            self.precacheDoffs("Ground")
            self.precacheModifiers()
            self.precacheReputations()
            self.precacheFactions()
            self.precacheSkills()
            self.precacheSpaceSkills()
        self.logWriteBreak('precachePreload END')

    def precacheIconCleanup(self):
        #preliminary gathering for self-cleaning icon folder
        #equipment = self.searchJsonTable(self.infoboxes, "type", phrases)
        boffIcons = self.cache['boffTooltips']['space'].keys()
        boffIcons += self.cache['boffTooltips']['ground'].keys()
    
    def precacheEquipment(self, keyPhrase):
        """Populate in-memory cache of ship equipment lists for faster loading"""  
        if not keyPhrase or keyPhrase in self.cache['equipment']:
            return
        self.progressBarStart()
        
        additionalPhrases = []
        if 'Weapon' in keyPhrase and 'Ship' in keyPhrase: additionalPhrases = ['Ship Weapon']
        elif 'Console' in keyPhrase: additionalPhrases = ['Universal Console']            

        phrases = [keyPhrase] + additionalPhrases
        
        if "Kit Frame" in keyPhrase:
            equipment = [item for item in self.infoboxes if "Kit" in item['type'] and not "Template Demo Kit" in item['type'] and not 'Module' in item['type']]
        else:
            equipment = self.searchJsonTable(self.infoboxes, "type", phrases)
            
        self.cache['equipment'][keyPhrase] = {self.sanitizeEquipmentName(equipment[item]["name"]): equipment[item] for item in range(len(equipment))}
        
        if 'Hangar' in keyPhrase:
            self.cache['equipment'][keyPhrase] = {key:self.cache['equipment'][keyPhrase][key] for key in self.cache['equipment'][keyPhrase] if 'Hangar - Advanced' not in key and 'Hangar - Elite' not in key}

        self.logWriteCounter('Equipment', '(json)', len(self.cache['equipment'][keyPhrase]), [keyPhrase])
        self.progressBarStop()

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
        mods = re.findall(r"(<td.*?>(<b>)*\[.*?\](</b>)*</td>)", modPage)
        self.cache['modifiers'] = list(set([re.sub(r"<.*?>",'',mod[0]) for mod in mods]))
        self.logWriteCounter('Modifiers', '(json)', len(self.cache['modifiers'])) 
        
    def precacheShips(self):
        self.shipNames = [e["Page"] for e in self.ships]
        self.logWriteCounter('Ships', '(json)', len(self.shipNames), ['space'])
        
    def predownloadGearImages(self):
        pass
        
    def predownloadShipImages(self):
        for e in self.ships:
            self.fetchOrRequestImage(self.wikiImages+e['image'].replace(' ','_'), e['Page'], self.shipImageWidth, self.shipImageHeight)
        
    def precacheSpaceSkills(self):
        if 'spaceSkills' in self.cache and len(self.cache['spaceSkills']) > 0:
            return
            
        self.cache['spaceSkills'] = self.fetchOrRequestJson('', 'space_skills', local=True)
        self.logWriteCounter('spaceSkills', '(json)', len(self.cache['spaceSkills']))

    def precacheGroundSkills(self):
        if 'groundSkills' in self.cache and len(self.cache['groundSkills']) > 0:
            return
            
        self.cache['groundSkills'] = self.fetchOrRequestJson('', 'ground_skills', local=True)
        self.logWriteCounter('groundSkills', '(json)', len(self.cache['groundSkills']))
        
    def precacheSkills(self):
        if 'skills' in self.cache and len(self.cache['skills']) > 0:
            return
            
        self.cache['skills'] = self.fetchOrRequestJson('', 'skills', local=True)
        self.logWriteCounter('Skills', '(json)', len(self.cache['skills']['content']))

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
        # self.faction[#][...] -- name, playability, faction // status, traits, allegiance?
        # prep self.cache['factions'][dict()]
        pass
        
    def precacheReputations(self):
        if 'specsPrimary' in self.cache and len(self.cache['specsPrimary']) > 0:
            return
        self.progressBarStart()
        
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
        self.progressBarStop()

    def precacheShipTraitSingle(self, name, desc):
        name = self.deWikify(name)
        if not 'cache' in self.cache['shipTraitsWithImages']:
            self.cache['shipTraitsWithImages']['cache'] = []
        
        if not name in self.cache['shipTraits']:
            self.cache['shipTraits'][name] = self.deWikify(desc, leaveHTML=True)
            self.cache['shipTraitsWithImages']['cache'].append((name,self.imageFromInfoboxName(name)))
            self.logWriteSimple('precacheShipTrait', '', 5, tags=[name])

    def precacheShipTraits(self):
        """Populate in-memory cache of ship traits for faster loading"""
        if 'shipTraits' in self.cache and len(self.cache['shipTraits']) > 0:
            return self.cache['shipTraits']
        self.progressBarStart()
            
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

        self.logWriteCounter('Ship Trait', '(json)', len(self.cache['shipTraits']), ['space'])
        self.progressBarStop()
 
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
        
    def precacheTraits(self):
        """Populate in-memory cache of traits for faster loading"""
        if 'traits' in self.cache and 'space' in self.cache['traits']:
            return self.cache['traits']
        self.progressBarStart()
        
        for item in list(self.traits):
            if not 'chartype' in item or item['chartype'] != 'char':
                continue
            if 'type' in item and 'name' in item and 'description' in item and 'environment' in item:
                self.precacheTraitSingle(item['name'], item['description'], item['environment'], item['type'])
        
        for type in self.cache['traitsWithImages']:
            for environment in self.cache['traitsWithImages'][type]:
                self.logWriteCounter('Trait', '(json)', len(self.cache['traitsWithImages'][type][environment]), [environment, type])
        self.progressBarStop()

    def setListIndex(self, list, index, value):
        list[index] = value

    def imageFromInfoboxName(self, name, width=None, height=None, suffix='_icon', faction=None, forceAspect = False):
        """Translate infobox name into wiki icon link"""
        width = self.itemBoxX if width is None else width
        height = self.itemBoxY if height is None else height

        #Aeon timeships provide list to name var -- try/except until time to fix
        try:
            image = self.fetchOrRequestImage(self.wikiImages+urllib.parse.quote(html.unescape(name.replace(' ', '_')))+suffix+".png", name, width, height, faction, forceAspect=forceAspect)
            if image is None: self.logWrite("==={} NONE".format(name), 4)
            elif image == self.emptyImage: self.logWrite("==={} EMPTY".format(name), 4)
            else: self.logWrite("==={} {}x{}".format(name, image.width(), image.height()), 4)
            return image
        except:
            return self.fetchOrRequestImage(self.wikiImages+"Common_icon.png", "no_icon",width,height)

    def resetAfterImport(self):
        self.skillCount('space')
        self.skillCount('ground')
        
        self.logWriteSimple('Skill count', 'import', 3, [self.backend['skillCount']['space'], self.backend['skillCount']['ground']])
        
    def skillCount(self, environment):
        self.backend['skillCount'][environment]
        for name in self.build['skilltree'][environment]:
            if self.build['skilltree'][environment][name]: self.backend['skillCount'][environment] += 1
    
    def copyBackendToBuild(self, key, key2=None):
        """Helper function to copy backend value to build dict"""
        if key in self.backend and key2 == None:
            self.build[key] = self.backend[key].get()
        elif key2 in self.backend[key]:
            self.build[key][key2] = self.backend[key][key2].get()

    def copyBuildToBackendBoolean(self, key, key2=None):
        """Helper function to copy build value to backend dict"""
        if key in self.build and key2 == None:
            self.backend[key].set(1 if self.build[key] else 0)
        elif key2 in self.build[key]:
            self.backend[key][key2].set(1 if self.build[key][key2] else 0)
            
    def copyBuildToBackend(self, key, key2=None):
        """Helper function to copy build value to backend dict"""
        if key in self.build and key2 == None:
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
        self.factionNames = [ 'Federation', 'Dominion', 'Klingon', 'Romulan', 'TOS Federation' ]
        self.exportOptions = [ 'PNG', 'Json' ]
        self.boffSortOptions = [ 'release', 'ranks', 'spec', 'spec2' ]
        self.consoleSortOptions = [ 'tesu', 'uets', 'utse', 'uest' ]
        
        # self.persistent will be auto-saved and auto-loaded for persistent state data
        self.persistent = {
            'forceJsonLoad': 0,
            'noPreCache': 0,
            'uiScale': 1,
            'imagesFactionAliases': dict(),
            'imagesFail': dict(),
            'markDefault': '',
            'rarityDefault': self.rarities[0],
            'factionDefault': self.factionNames[0],
            'exportDefault': self.exportOptions[0],
            'boffSort': self.boffSortOptions[0],
            'boffSort2': self.boffSortOptions[0],
            'consoleSort': self.consoleSortOptions[0],
            'keepTemplateOnShipClear': 0,
            'keepTemplateOnShipChange': 0,
            'pickerSpawnUnderMouse': 1,
            'useFactionSpecificIcons': 0,
            'useExperimentalTooltip': 0,
        }
    
    def resetSettings(self):
        # self.settings are optionally loaded from config, but manually edited or saved
        self.settings = {
            'debug': self.debugDefault,
            'template': '.template',
            'skills':   'skills.json',
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
        
    def clearBuild(self):
        """Initialize new build state"""
        # VersionJSON Should be updated when JSON format changes, currently number-as-date-with-hour in UTC
        self.versionJSONminimum = 0
        self.versionJSON = 2022020203
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
            'skilltree': { 'space': dict(), 'ground': dict() },
        }

    def resetCache(self, text = None):
        if text is not None:
            if text in self.cache and text != 'modifiers':
                self.cache[text] = dict()
                if text+"WithImages" in self.cache:
                    self.cache[text+"WithImages"] = dict()
        else:
            self.cache = {
                'equipment': dict(),
                'doffs': dict(),
                'doffNames': dict(),
                'shipTraits': dict(),
                'shipTraitsWithImages': dict(),
                'traits': dict(),
                'traitsWithImages': dict(),
                'boffAbilities': dict(),
                'boffAbilitiesWithImages': dict(),
                'boffTooltips': dict(),
                'specsPrimary': dict(),
                'specsSecondary': dict(),
                'specsGroundBoff': dict(),
                'skills': dict(),
                'spaceSkills': dict(),
                'groundSkills': dict(),
                'factions': dict(),
                'modifiers': None,
            }
    
    def resetBackend(self, rebuild=False):
        self.logWriteBreak('clearBackend')
        self.updateImageLabelSize(source='clearBackend')
        self.backend = {
                'images': dict(),
                'captain': {'faction' : StringVar(self.window)},
                'career': StringVar(self.window),
                'species': StringVar(self.window),
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
            }
        self.persistentToBackend()
        if rebuild: self.buildToBackendSeries()
        self.hookBackend()

    def hookBackend(self):
        self.backend['playerShipName'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('playerShipName'))
        self.backend['captain']['faction'].trace_add('write', lambda v,i,m:self.captainFactionCallback())
        self.backend['career'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('career'))
        self.backend['species'].trace_add('write', lambda v,i,m:self.speciesUpdateCallback())
        self.backend['specPrimary'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('specPrimary'))
        self.backend['specSecondary'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('specSecondary'))
        self.backend['tier'].trace_add('write', lambda v,i,m:self.setupCurrentBuildFrames('space'))
        self.backend['eliteCaptain'].trace_add('write', lambda v,i,m:self.setupCurrentBuildFrames())
        self.backend['ship'].trace_add('write', self.shipMenuCallback)

    def captainFactionCallback(self):
        self.copyBackendToBuild('captain', 'faction')
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

    def pickerLocation(self, x, y, height):
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        if x is None or y is None:
            x = self.window.winfo_pointerx()
            y = self.window.winfo_pointery()
            
        if self.persistent['pickerSpawnUnderMouse'] and x is not None and y is not None:
            self.logWrite("pickerGUI position update: x{},y{}".format(str(x), str(y)), 2)
        else:
            x = self.windowXCache
            y = self.windowYCache
            
        if height < screen_height and (y + height) > screen_height:
            y = screen_height - height
        positionWindow = "+"+str(x)+"+"+str(y)
        
        return positionWindow
    
    def windowAddScrollbar(self, parentFrame, canvas):
        scrollbar = Scrollbar(parentFrame, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        startY = canvas.yview()[0]
        parentFrame.bind("<<ResetScroll>>", lambda event: canvas.yview_moveto(startY))
        parentFrame.pack(fill=BOTH, expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side=RIGHT,fill=Y)
        
        return scrollable_frame
        
    def restrictItemsList(self, items_list, tagsForRequirement = []):
        # Infobox 'who' denotes restrictions [for future imlementation]
        
        return items_list
        
    def pickerGui(self, title, itemVar, items_list, top_bar_functions=None, x=None, y=None):
        """Open a picker window"""
        pickWindow = Toplevel(self.window)
        pickWindow.resizable(False,True) #vertical resize only
        pickWindow.transient(self.window)
        pickWindow.title(title)
        
        (windowwidth,windowheight) = self.pickerDimensions()
        sizeWindow = '{}x{}'.format(windowwidth, windowheight)
        pickWindow.geometry(sizeWindow+self.pickerLocation(x, y, windowheight))
        
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
        scrollable_frame = self.windowAddScrollbar(container, canvas)
        
        try:
            items_list.sort()
        except:
            self.logWriteSimple('pickerGUI', 'TRY_EXCEPT', 1, tags=['item_list.sort() failed in '+title])

        i = 0
        clearSlotButton = Button(scrollable_frame, text='Clear Slot', padx=5, bg='#3a3a3a',fg='#b3b3b3')
        clearSlotButton.grid(row=0, column=0, sticky='nsew')
        clearSlotButton.bind('<Button-1>', lambda e,name='X',image=self.emptyImage,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,image,v,win))
        i += 1
        for name,image in items_list:
            frame = Frame(scrollable_frame, relief='ridge', borderwidth=1)
            for col in range(3):
                if col == 0: label = Label(frame, image=image)
                elif col == 1: label = Label(frame, text=name, wraplength=windowwidth-40, justify=LEFT)
                subFrame = frame
                    
                if col < 2: 
                    subFrame = label
                    subFrame.grid(row=0, column=col, sticky='nsew')
                else:
                    subFrame = frame
                    subFrame.grid(row=i, column=0, sticky='nsew')
                    
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
            pass
        except:
            pass
        
    def logWindowCreate(self):
        self.makeSubWindow(title='Log Viewer', type='log')
        
    def windowDimensions(self):
        #self.window.update()
        windowheight = self.windowHeight - self.logoHeight - 45
        windowwidth = self.windowWidth
        
        return (windowwidth,windowheight)

    def windowLocationCentered(self, x, y):
        #positionWindow = '+{}+{}'.format(self.windowXCache, self.windowYCache)

        if x is not None and y is not None:
            positionWindow = '+{}+{}'.format(x, y)
        else: 
            positionWindow = '+{}+{}'.format(self.windowXCache, self.windowYCache + self.logoHeight + 35 )
            self.logWrite("subWindow position update: x{},y{}".format(str(x), str(y)), 2)

        return positionWindow
        
    def makeSubWindow(self, title, type, x=None, y=None, windowWidth=None, noclose=False):
        """Open a new window"""
        self.requestWindowUpdate()
        if windowWidth is None: windowWidth = self.windowWidth
        subWindow = Toplevel(self.window)
        if noclose:
            subWindow.overrideredirect(1) #no window elements, must implement close window in window first
        else:
            subWindow.resizable(False,False)
            subWindow.transient(self.window)

        subWindow.title(title)
        
        (windowwidth,windowheight) = self.windowDimensions()
        sizeWindow = '{}x{}'.format(windowwidth, windowheight)
        subWindow.geometry(sizeWindow+self.windowLocationCentered(x, y))
       
        subWindow.protocol('WM_DELETE_WINDOW', lambda:self.windowCloseCallback(subWindow))
        
        container = Frame(subWindow)
        container.configure(bg='#b3b3b3')
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        topFrame = Frame(subWindow, width=windowWidth)
        topFrame.grid(row=0, column=0, sticky='nsew', padx=1, pady=1)
        mainFrame = Frame(subWindow)
        mainFrame.grid(row=1, column=0, sticky='nsew', padx=1, pady=1)
        
        if noclose:
            optionFrame = Button(topFrame, text='Close', command=lambda:self.windowCloseCallback(subWindow))
            optionFrame.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0, width=10)
            optionFrame.grid(row=0, column=0, sticky='e')
            
        if type == 'log':
            scrollbar = Scrollbar(mainFrame)
            scrollbar.pack(side=RIGHT, fill=Y)
            self.logDisplay = Text(mainFrame, bg='#3a3a3a', fg='#ffffff', wrap=WORD, height=30, width=110, font=('TkFixedFont', 10))
            self.logDisplay.pack(side=LEFT, fill=BOTH, expand=True)
            self.logDisplay.insert('0.0', self.logFull.get())
            scrollbar.config(command=self.logDisplay.yview)
            self.logDisplay.config(yscrollcommand=scrollbar.set)
            self.logDisplayUpdate()
            
        subWindow.title('{}'.format(title))
        subWindow.wait_visibility()    #Implemented for Linux
        subWindow.grab_set()
        subWindow.wait_window()

    def itemLabelCallback(self, e, canvas, img, i, key, args):
        """Common callback for ship equipment labels"""
        self.precacheEquipment(args[0])
        itemVar = {"item":'',"image":self.emptyImage, "rarity": self.persistent['rarityDefault'], "mark": self.persistent['markDefault'], "modifiers":['']}
        items_list = [ (item.replace(args[2], ''), self.imageFromInfoboxName(item)) for item in list(self.cache['equipment'][args[0]].keys())]
        items_list = self.restrictItemsList(items_list) # Most restrictions should come from the ship
        item = self.pickerGui(args[1], itemVar, items_list, [self.setupSearchFrame, self.setupRarityFrame], self.window.winfo_pointerx(), self.window.winfo_pointery())
        if 'item' in item and len(item['item']):
            if item['item'] == 'X':
                item['item'] = ''
                canvas.itemconfig(img[0],image=self.emptyImage)
                canvas.itemconfig(img[1],image=self.emptyImage)
                self.build[key][i] = item
                self.backend['images'][key][i] = [self.emptyImage, self.emptyImage]
            else:
                if 'rarity' in self.cache['equipment'][args[0]][item['item']]:
                    rarityDefaultItem = self.cache['equipment'][args[0]][item['item']]['rarity']
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
                canvas.bind('<Enter>', lambda e,item=item:self.setupInfoboxFrameSplitter(item, args[0], environment))
                self.build[key][i] = item
                self.backend['images'][key][i] = [item['image'], image1]
                item.pop('image')

    def traitLabelCallback(self, e, canvas, img, i, key, args):
        """Common callback for all trait labels"""
        items_list=[]
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
            
        items_list = self.restrictItemsList(items_list) # What restrictions exist for traits?

        itemVar = self.getEmptyItem()
        item = self.pickerGui("Pick trait", itemVar, items_list, [self.setupSearchFrame])
        if 'item' in item and len(item['item']):
            if item['item'] == 'X':
                item['item'] = ''
                self.backend['images'][item['item']+str(i)] = self.emptyImage
                canvas.itemconfig(img[0],image=self.emptyImage)
                self.build[key][i] = item
            else:
                if item['item']+str(i) not in self.backend['images']:
                    self.backend['images'][item['item']+str(i)] = item['image']
                canvas.itemconfig(img[0],image=self.backend['images'][item['item']+str(i)])
                environment = 'space'
                if len(args) >= 4:
                    environment = args[3]
                canvas.bind('<Enter>', lambda e,item=item:self.setupInfoboxFrameSplitter(item, '', environment))
                item.pop('image')
                self.build[key][i] = item

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
        
    def precacheBoffAbilities(self):
        """Common callback for boff labels"""
        if 'boffAbilities' in self.cache and 'space' in self.cache['boffAbilities'] and 'ground' in self.cache['boffAbilities']:
            return
        self.progressBarStart()
        
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
        self.progressBarStop()
        
    def boffLabelCallback(self, e, canvas, img, i, key, args):
        """Common callback for boff labels"""
        self.precacheBoffAbilities()
        environment = args[3] if args is not None and len(args) >= 4 else 'space'

        items_list = []
        rank = i + 1
        
        logNote = args[0]
        if args[1]:
            logNote = logNote + ', '+args[1]
        self.logWriteSimple('spaceBoffLabel', 'Callback', 3, tags=[environment, logNote, str(args[2])])

        if args[0] == 'universal':
            for specType in self.universalTypes:
                items_list = items_list + self.cache['boffAbilitiesWithImages'][environment][specType][rank]
        else:
            items_list = self.cache['boffAbilitiesWithImages'][environment][args[0]][rank]
        if args[1] is not None and args[1] != '':
            items_list = items_list + self.cache['boffAbilitiesWithImages'][environment][args[1]][rank]
            
        items_list = self.restrictItemsList(items_list) # need to send boffseat spec/spec2

        itemVar = self.getEmptyItem()
        item = self.pickerGui('Pick Ability', itemVar, items_list, [self.setupSearchFrame])
        backendKey = item['item']+str(i)
        if not backendKey in self.backend['images']: self.backend['images'][backendKey] = None
        if 'item' in item and len(item['item']):
            if item['item'] == 'X':
                item['item'] = ''
                self.backend['images'][backendKey] = self.emptyImage
                canvas.itemconfig(img,image=self.emptyImage)
                self.build['boffs'][key][i] = item
            else:
                #if item['item']+str(i) not in self.backend['images']:
                self.backend['images'][backendKey] = item['image']
                canvas.itemconfig(img,image=self.backend['images'][item['item']+str(i)])
                canvas.bind('<Enter>', lambda e,item=item:self.setupInfoboxFrameSplitter(item, '', environment))
                self.build['boffs'][key][i] = item['item']
                
        # ground used +'_'+str(i)

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
                
    def importCallback(self, event=None):
        """Callback for import button"""
        initialDir = self.getFolderLocation('library')
        inFilename = filedialog.askopenfilename(filetypes=[('SETS files', '*.json *.png'),('JSON files', '*.json'),('PNG image','*.png'),('All Files','*.*')], initialdir=initialDir)
        self.importByFilename(inFilename)
            
    def importByFilename(self, inFilename, force=False):
        if not inFilename: return
        
        self.requestWindowUpdateHold(30) # Still requires tuning
        if inFilename.lower().endswith('.png'):
            # image = Image.open(inFilename)
            # self.build = json.loads(image.text['build'])
            try:
                self.buildImport = json.loads(self.decodeBuildFromImage(inFilename))
            except:
                self.logWriteTransaction('Template File', 'PNG load complaint', '', inFilename, 0)
        else:
            with open(inFilename, 'r') as inFile:
                try:
                    self.buildImport = json.load(inFile)
                except:
                    self.logWriteTransaction('Template File', 'load complaint', '', inFilename, 0)
        
        if 'versionJSON' not in self.buildImport and not force:
            self.logWriteTransaction('Template File', 'version missing', '', inFilename, 0)
            if self.persistent['forceJsonLoad']:
                return self.importByFilename(inFilename, True)
        elif self.buildImport['versionJSON'] >= self.versionJSONminimum or force:
            self.logWriteBreak('IMPORT PROCESSING START')
            logNote = ' (fields:['+str(len(self.buildImport))+'=>'+str(len(self.build))+']='
            self.build.update(self.buildImport)
            logNote = logNote+str(len(self.build))+' merged)'

            self.resetBackend(rebuild=True)
            self.resetBuildFrames()

            self.setupCurrentBuildFrames()

            if force:
                logNote=' (FORCE LOAD)'+logNote

            self.logWriteTransaction('Template File', 'loaded', '', inFilename, 0, [logNote])

            self.resetAfterImport()
            self.logWriteBreak('IMPORT PROCESSING END')
            return True
        else:
            self.logWriteTransaction('Template File', 'version mismatch', '', inFilename, 0, [str(self.buildImport['versionJSON'])+' < '+str(self.versionJSONminimum)])
            if self.persistent['forceJsonLoad']:
                return self.importByFilename(inFilename, True)
            else:
                return False

    def filenameDefault(self):
        name = self.build['playerShipName'] if 'playerShipName' in self.build else ''
        type = self.build['ship'] if 'ship' in self.build else ''
        
        if name and type: filename = "{} ({})".format(name, type)
        elif name: filename = name
        elif type: filename = type
        else: filename = ''
        
        return filename
        
    def exportCallback(self, event=None):
        """Callback for export as png button"""
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
        if not outFilename: return
        justFile, chosenExtension = os.path.splitext(outFilename)
        if chosenExtension.lower() == '.json':
            try:
                outFile = open(outFilename, 'w')
                json.dump(self.build, outFile)
            except AttributeError:
                pass
        else:
            image.save(outFilename, chosenExtension.strip('.'))
            self.encodeBuildInImage(outFilename, json.dumps(self.build), outFilename)
        
        self.logWriteTransaction('Export build', chosenExtension, str(os.path.getsize(outFilename)), outFilename, 0, [str(image.size) if chosenExtension.lower() == '.png' else None])
        
    def skillAllowed(self, rank, row, col, environment):
        if environment == 'ground':
            maxSkills = 10 # Could be set by captain rank/level
            rankReqs = [0, 0]
            name = self.skillGetGroundNode(rank, row, col, type='name')
            split = False
            plusOne = self.skillGetGroundNode(rank, row, col+1, type='name')
            plusTwo = self.skillGetGroundNode(rank, row, col+2, type='name')
            minusOne = self.skillGetGroundNode(rank, row, col-1, type='name')
            minusTwo = self.skillGetGroundNode(rank, row, col-2, type='name')
        else:
            maxSkills = 46 # Could be set by captain rank/level
            rankReqs = { 'lieutenant': 0, 'lieutenant commander': 5, 'commander': 15, 'captain': 25, 'admiral': 35 }
            name = self.skillSpaceGetFieldNode(rank, row, col, type='name')
            split = self.skillSpaceGetFieldSkill(rank, row, '', type='linear')
            plusOne = self.skillSpaceGetFieldNode(rank, row, col+1, type='name')
            plusTwo = self.skillSpaceGetFieldNode(rank, row, col+2, type='name')
            minusOne = self.skillSpaceGetFieldNode(rank, row, col-1, type='name')
            minusTwo = self.skillSpaceGetFieldNode(rank, row, col-2, type='name')
        # col is the position-in-chain
       
        #if environment == 'ground': return True
        self.logWriteSimple('skillAllowed', environment, 3, [name])
        if not name in self.build['skilltree'][environment]: self.build['skilltree'][environment][name] = False
        enabled = self.build['skilltree'][environment][name]
        child = self.build['skilltree'][environment][plusOne] if plusOne and col < 2 else False
        child2 = self.build['skilltree'][environment][plusTwo] if plusTwo and col < 1 else False
        parent = self.build['skilltree'][environment][minusOne] if minusOne and col > 0 else True
        parent2 = self.build['skilltree'][environment][minusTwo] if minusTwo and col > 1 else True
        
        if enabled: # Can we turn this off?
            # If this takes us below our current rank, are there skills above this rank?
            
            # Do we have requiredby that are True?
            if child2: return False
            if not ( col == 1 and split ):
                if child: return False
                
        else: # Can we turn this on?
            # Can we activate that rank?
            if self.backend['skillCount'][environment] < rankReqs[rank]: return False
            if self.backend['skillCount'][environment] + 1 > maxSkills: return False
            # Is our required already True?
            if not parent2: return False
            if not ( col == 2 and split ):
                if not parent: return False
            
        return True
        
    def skillButtonChildUpdate(self, rank, row, col, environment='space'):
        # Change disable status of children based on selection change
        
        return
        
    def skillLabelCallback(self, e, canvas, img, i, key, args, environment='space'):
        rank, row, col, drawEnvironment = args
        if environment == 'ground': name = self.skillGetGroundNode(rank, row, col, type='name')
        else: name = self.skillSpaceGetFieldNode(rank, row, col, type='name')
        backendName = name

        if not self.skillAllowed(rank, row, col, environment): return # Check for requirements before enable
        
        self.build['skilltree'][environment][name] = not self.build['skilltree'][environment][name]
        
        if self.build['skilltree'][environment][name]:
            countChange = 1
            image1 = self.epicImage
            canvas.configure(bg='yellow', relief='groove')
        else:
            countChange = -1
            image1 = self.emptyImage
            canvas.configure(bg='grey', relief='raised')
            
        self.backend['skillCount'][environment] += countChange
        self.backend['images'][backendName] = [self.backend['images'][backendName][0], image1]
        canvas.itemconfig(img[1],image=image1)
        
        self.skillButtonChildUpdate(rank, row, col, environment)
        
    def skillGroundLabelCallback(self, e, canvas, img, i, key, args, environment='ground'): 
        self.skillLabelCallback(e, canvas, img, i, key, args, environment)
    
        return
        # Original actions below, prune once new functions stable
        rankReqs = [0, 5, 15, 25, 35]
        if(skill in self.build['skills'][rank]):
            if (rank < 4 and len(self.build['skills'][rank+1])>0):
                if self.backend['skillCount'] > rankReqs[rank+1]:
                    self.build['skills'][rank].remove(skill)
                    self.backend['skillLabels'][skill].configure(bg='gray')
                    self.backend['skillCount'] -= 1
                    if self.backend['skillCount'] < rankReqs[rank]:
                        for s in self.backend['skillNames'][rank]:
                            self.backend['skillLabels'][s].configure(bg='black')
            return
        if self.backend['skillCount'] < rankReqs[rank] or self.backend['skillCount'] == 46: return
        self.build['skills'][rank].append(skill)
        self.backend['skillLabels'][skill].configure(bg='yellow')
        self.backend['skillCount'] += 1
        if rank < 4 and self.backend['skillCount'] == rankReqs[rank+1]:
            for s in self.backend['skillNames'][rank+1]:
                self.backend['skillLabels'][s].configure(bg='grey')

    def redditExportDisplayGround(self, textframe):
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
                column0 = column0 + self.makeRedditColumn(["#"+str(int(groundboff[-1])+1)+": "+self.build['boffseats']['ground'][int(groundboff[-1])]+" / "+self.build['boffseats']['ground_spec'][int(groundboff[-1])]], len(self.build['boffs'][groundboff]))
                column1 = column1 + self.makeRedditColumn(self.build['boffs'][groundboff], len(self.build['boffs'][groundboff]))
        redditString = redditString + self.makeRedditTable(['**Profession**']+column0, ['**Power**']+column1, ['**Notes**']+[None]*len(column0))
        textframe.delete("1.0",END)
        textframe.insert(END, redditString)
    
    def redditExportDisplaySpace(self, textframe):
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
        textframe.delete('1.0',END)
        textframe.insert(END, redditString)

    def exportRedditCallback(self, event=None):
        phi = font.Font(family='Helvetica', size=12, weight='bold')
        redditWindow = Toplevel(self.window)
        redditText = Text(redditWindow)
        btfr = Frame(redditWindow)
        btfr.pack(side='top', fill='x')
        redditbtspace = Button(btfr,text="SPACE", font=phi,  bg="#6b6b6b",fg="white",command=lambda: self.redditExportDisplaySpace(redditText))
        redditbtground = Button(btfr, text="GROUND", font =phi, bg="#6b6b6b", fg="white",command=lambda: self.redditExportDisplayGround(redditText))
        redditbtspace.grid(row=0,column=0,sticky="nsew")
        redditbtground.grid(row=0,column=1,sticky="nsew")
        btfr.grid_columnconfigure(0,weight=1)
        btfr.grid_columnconfigure(1,weight=1)
        redditText.pack(fill=BOTH, expand=True)
        self.redditExportDisplaySpace(redditText)
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
                    log.Write('Failed to delete %s. Reason: %s' % (file_path, e))
        #self.precachePreload()
            
    def clearImagesFolder(self):
        dir = self.getFolderLocation('images')
        for filename in os.listdir(dir):
            file_path = os.path.join(dir, filename)
            try:
                os.unlink(file_path)
            except Exception as e:
                log.Write('Failed to delete %s. Reason: %s' % (file_path, e))
                    
    def settingsButtonCallback(self, type):
        self.logWriteSimple("settingsButtonCallback", '', 2, [type])
        
        if type == 'clearcache': self.clearCacheFolder()
        elif type == 'clearimages': self.clearImagesFolder()
        elif type == 'clearfactionImages':
            self.persistent['imagesFactionAliases'] = dict()
            self.stateSave()
        elif type == 'clearmemcache':
            self.resetCache()
            self.requestWindowUpdateHold(0)
            self.precachePreload()
        elif type == 'cacheSave': self.cacheSave()
        elif type == 'openLog': self.logWindowCreate()
        elif type == 'predownloadShipImages': self.predownloadShipImages()
        elif type == 'predownloadGearImages': self.predownloadGearImages()
        elif type == 'backupCache':
            # Backup state file
            # Backup caches (leave as current as well)
            # make a duplicate/compressed image archive folder?
            # make a duplicate/compressed library archive folder?  Just template?
            pass
                        
    def buildToBackendSeries(self):
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
        self.persistentToBackend()

    def clearBuildCallback(self, event=None):
        """Callback for the clear build button"""
        self.clearBuild()
        self.clearing = 1
        self.buildToBackendSeries()

        #self.backend['tier'].set('')
        self.backend['shipHtml'] = None
        self.shipImg = self.getEmptyFactionImage()
        self.groundImg = self.getEmptyFactionImage()
        self.setShipImage(self.shipImg)
        self.setCharImage(self.groundImg)

        self.resetBuildFrames()

        self.clearing = 0
        self.setupCurrentBuildFrames()

    def getEmptyFactionImage(self, faction=None):
        if faction is None:
            faction = self.persistent['factionDefault'].lower() if 'factionDefault' in self.persistent else 'federation'
        
        if faction in self.emptyImageFaction: return self.emptyImageFaction[faction]
        else: return self.emptyImage
    
    def boffUniversalCallback(self, v, idx, key):
        self.build['boffseats'][key][idx] = v.get()

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

    def doffEffectCallback(self, om, v0, v1, row, isSpace=True):
        if self.cache['doffs'] is None:
            return
        self.build['doffs']['space' if isSpace else 'ground'][row]['effect'] = v1.get()
        self.setupDoffFrame(self.shipDoffFrame)
        self.setupDoffFrame(self.groundDoffFrame)

    def tagBoxCallback(self, var, text):
        self.build['tags'][text] = var.get()
        
    def eliteCaptainCallback(self):
        self.build['eliteCaptain'] = bool(self.backend['eliteCaptain'].get())

    def markBoxCallback(self, itemVar, value):
        itemVar['mark'] = value

    def currentFrameRefresh(self):
        pass
        
    
    def currentFrameUpdateTo(self, frame=None, first=False):
        try:
            preHeight = self.currentFrame.winfo_height()
            preWidth = self.currentFrame.winfo_width()
        except:
            preHeight = 0
            preWidth = 0
        self.currentFrame = frame
        postHeight = self.currentFrame.winfo_height()
        postWidth = self.currentFrame.winfo_width()
        
        self.framePriorheight = postHeight if first else preHeight
        self.framePriorwidth = postWidth if first else preWidth
        
        logNote1 = 'Height Change: {:>4}->{:>4}'.format(preHeight, postHeight) if postHeight != preHeight else ''
        logNote2 = 'Width Change: {:>4}->{:>4}'.format(preWidth, postWidth) if postWidth != preWidth else ''
        if logNote1 or logNote2: self.logWrite('FRAME {:>26}{:>26}'.format(logNote1, logNote2), 3)
        
    def focusFrameCallback(self, type='space', init=False):
        if type is None: type = 'space'
        if type == 'ground' or type == 'space':
            self.updateImageLabelSize(source='focus'+type.title()+'BuildFrameCallback')
    
        if type == 'ground': self.currentFrameUpdateTo(self.groundBuildFrame)
        elif type == 'skill': self.currentFrameUpdateTo(self.skillTreeFrame)
        elif type == 'library': self.currentFrameUpdateTo(self.libraryFrame)
        elif type == 'settings': self.currentFrameUpdateTo(self.settingsFrame)
        elif type == 'space': self.currentFrameUpdateTo(self.spaceBuildFrame)
        else: return
        
        self.groundBuildFrame.pack_forget() if type != 'ground' else None
        self.skillTreeFrame.pack_forget() if type != 'skill' else None
        self.libraryFrame.pack_forget() if type != 'library' else None
        self.settingsFrame.pack_forget() if type != 'settings' else None
        self.spaceBuildFrame.pack_forget() if type != 'space' else None

        self.currentFrame.pack(fill=BOTH, expand=True, padx=15)
        #self.currentFrame.place(height = self.framePriorheight) # Supposed to maintain frame height, may need grid
        
        if type == 'skill': self.setupCurrentSkillBuildFrames('space')

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
    
    def setupCurrentBuildFrames(self, environment=None):
        if not self.clearing:
            if environment == 'space' or environment == None: self.setupSpaceBuildFrames()
            if environment == 'ground' or environment == None: self.setupGroundBuildFrames()
            if environment == 'skill' or environment == None: self.setupCurrentSkillBuildFrames()
            
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
            self.logWriteSimple('self.persistent', 'markDefault', 3, tags=[self.persistent['markDefault']])
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
        if 'rarity' in itemVar and itemVar['rarity']:
            self.setupModFrame(modFrame, rarity=itemVar['rarity'], itemVar=itemVar)
        elif 'rarityDefault' in self.persistent and self.persistent['rarityDefault']:
            self.setupModFrame(modFrame, rarity=self.persistent['rarityDefault'], itemVar=itemVar)

    def labelBuildBlock(self, frame, name, row, col, cspan, key, n, callback, args=None, disabledCount=0):
        """Set up n-element line of ship equipment"""
        self.backend['images'][key] = [None] * n
        
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
            disabled = i >= disabledStart
            bg ='gray' if not disabled else 'black'
            padx = (25 + 3 * 2) if disabled else 2

            self.createButton(iFrame, bg=bg, row=row, column=i+1, padx=padx, disabled=disabled, key=key, i=i, callback=callback, args=args)
                
                
    def createButton(self, parentFrame, key, i=0, groupKey=None, callback=None, name=None, row=0, column=0, columnspan=1, rowspan=1, highlightthickness=0, highlightbackground='grey', borderwidth=0, width=None, height=None, bg='gray', padx=2, pady=2, image0Name=None, image1Name=None, image0=None, image1=None, disabled=False, args=None, sticky='nse', relief=FLAT, tooltip=None, anchor='center', faction=False, suffix=''):
        """ Button building (including click and tooltip binds) """
        # self.build[key][buildSubKey] is the build code for callback updating and image identification
        # self.backend['images'][backendKey][#] is the location for (img,img)
        # args [array] contains variable infomation used for callback updating
        # internalKey is the cache sub-group (for equipment cache sub-groups)
        
        if width is None: width = self.itemBoxX
        if height is None: height = self.itemBoxY

        buildSubKey = name if name is not None else i
        backendKey = name if name is not None else key

        if name is not None: item = name
        elif groupKey is not None: name = item = self.build[groupKey][key][buildSubKey]
        else: item = self.build[key][buildSubKey]
        
        self.logWriteSimple('createButton', '', 4, [name, key, buildSubKey, backendKey, i, row, column])
        
        if type(item) is dict and item is not None:
            if image0Name is None and 'item' in item: image0Name = item['item']
            else: image0Name = item
            if image1Name is None and 'rarity' in item: image1Name = item['rarity']
            
        if not disabled:
            if image0 is None: image0=self.imageFromInfoboxName(image0Name, suffix=suffix, faction=faction) if image0Name is not None else self.emptyImage
            if image1 is None: image1=self.imageFromInfoboxName(image1Name, suffix=suffix, faction=faction) if image1Name is not None else self.emptyImage
            if not backendKey in self.backend['images']: self.backend['images'][backendKey] = [None, None]
            if name == 'blank': pass #no backend/image
            elif name: self.backend['images'][name] = [image0, image1]
            else: self.backend['images'][backendKey][i] = [image0, image1]
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
            environment = args[3] if args is not None and len(args) >= 4 else 'space'
            internalKey = args[0] if args is not None and type(args[0]) is str else ''
            if callback is not None: canvas.bind('<Button-1>', lambda e,canvas=canvas,img=(img0, img1),i=buildSubKey,args=args,key=key,callback=callback:callback(e,canvas,img,i,key,args))
            if name != 'blank':
                canvas.bind('<Enter>', lambda e,item=item,internalKey=internalKey,environment=environment,tooltip=tooltip:self.setupInfoboxFrameSplitter(item, internalKey, environment, tooltip))
        
        return canvas, img0, img1

    def setupShipGearFrame(self, ship):
        """Set up UI frame containing ship equipment"""
        
        outerFrame = self.shipEquipmentFrame
        outerFrame.grid_rowconfigure(0, weight=1, uniform='shipFrameFullRowSpace')
        outerFrame.grid_columnconfigure(0, weight=1, uniform='shipFrameFullColSpace')
        self.clearFrame(outerFrame)
        
        parentFrame = Frame(outerFrame, bg='#3a3a3a')
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
        
        parentFrame = Frame(outerFrame, bg='#3a3a3a')
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
        
        parentFrame = Frame(outerFrame, bg='#3a3a3a')
        parentFrame.grid(row=0, column=0, sticky='', padx=1, pady=1)
        
        self.labelBuildBlock(parentFrame, "Kit Modules", 0, 0, 5, 'groundKitModules', 6 if self.backend['eliteCaptain'].get() else 5, self.itemLabelCallback, ["Kit Module", "Pick Module", "", 'ground'])
        self.labelBuildBlock(parentFrame, "Kit Frame", 0, 5, 1, 'groundKit', 1, self.itemLabelCallback, ["Kit Frame", "Pick Kit", "", 'ground'])
        self.labelBuildBlock(parentFrame, "Armor", 1, 0, 1, 'groundArmor', 1, self.itemLabelCallback, ["Body Armor", "Pick Armor", "", 'ground'])
        self.labelBuildBlock(parentFrame, "EV Suit", 1, 1, 1, 'groundEV', 1, self.itemLabelCallback, ["EV Suit", "Pick EV Suit", "", 'ground'])
        self.labelBuildBlock(parentFrame, "Shield", 2, 0, 1, 'groundShield', 1, self.itemLabelCallback, ["Personal Shield", "Pick Shield (G)", "", 'ground'])
        self.labelBuildBlock(parentFrame, "Weapons", 3, 0, 2, 'groundWeapons' , 2, self.itemLabelCallback, ["Ground Weapon", "Pick Weapon (G)", "", 'ground'])
        self.labelBuildBlock(parentFrame, "Devices", 4, 0, 5, 'groundDevices', 5 if self.backend['eliteCaptain'].get() else 4, self.itemLabelCallback, ["Ground Device", "Pick Device (G)", "", 'ground'])
                
    def skillGetGroundNode(self, rank, row, col, type='name'):
        if 'content' in self.cache['skills']:
            # needs to be smarter than 'try'
            try:
                if type in self.cache['groundSkills']['content'][rank][row][col]:
                    return self.cache['groundSkills']['content'][rank][row][col][type]
            except:
                return ''
            
        return ''

    def skillSpaceGetFieldNode(self, rankName, row, col, type='name'):
        if self.cache['spaceSkills']:
            try:
                if type in self.cache['spaceSkills'][rankName][row]['nodes'][col]:
                    result = self.cache['spaceSkills'][rankName][row]['nodes'][col][type]
            except:
                result = ''
        #self.logWriteSimple('Skill', 'Node', 3, [rankName, row, col, type, result])
        return result
        
    def skillSpaceGetFieldSkill(self, rankName, row, col, type='name'):
        if self.cache['spaceSkills']:
            try:
                if type in self.cache['spaceSkills'][rankName][row]:
                    result = self.cache['spaceSkills'][rankName][row][type]
            except:
                result = ''
        #self.logWriteSimple('Skill', 'Core', 3, [rankName, row, col, type, self.cache['spaceSkills'][rankName][row][type]])
        return result

    def setupSkillBuildFrames(self, environment=None):
        self.precacheSkills()
        if not 'content' in self.cache['skills']: return

        self.requestWindowUpdateHold(30) # Still requires tuning
        
        if environment is None or environment == 'space':
            parentFrame = self.skillSpaceBuildFrame
            self.clearFrame(parentFrame)
            self.setupSpaceSkillTreeFrame(parentFrame, 'space')
            self.setupSkillBonusFrame(parentFrame, 'space')
        
        if environment is None or environment == 'ground':
            parentFrame = self.skillGroundBuildFrame
            self.clearFrame(parentFrame)
            self.setupGroundSkillTreeFrame(parentFrame, 'ground')
            self.setupSkillBonusFrame(parentFrame, 'ground')
         
        #self.clearInfoboxFrame('skill')
        
    def setupGroundSkillTreeFrame(self, parentFrame, environment='ground'):
        self.precacheGroundSkills()
        frame = Frame(parentFrame, bg='#3a3a3a')
        frame.grid(row=0, column=0, sticky='n', padx=1, pady=1)
        parentFrame.grid_rowconfigure(0, weight=1, uniform='skillFrameFullRow'+environment)
        parentFrame.grid_columnconfigure(0, weight=1, uniform='skillFrameFullCol'+environment)
        
        rankColumns = 4
        for row in range(8):
            frame.grid_rowconfigure(row, weight=1, uniform='skillFrameRow'+environment)
            for rank in range(rankColumns):
                for col in range(4):
                    rowspan = 1
                    sticky = ''
                    
                    self.setupSkillButton(frame, rank, '', rankColumns, row, col, rowspan, environment, sticky=sticky)
        
    def setupSpaceSkillTreeFrame(self, parentFrame, environment='space'):
        self.precacheSpaceSkills()
        frame = Frame(parentFrame, bg='#3a3a3a')
        frame.grid(row=0, column=0, sticky='ns', padx=1, pady=1)
        parentFrame.grid_rowconfigure(0, weight=1, uniform='skillFrameFullRow'+environment)
        parentFrame.grid_columnconfigure(0, weight=1, uniform='skillFrameFullCol'+environment)
        

        rankColumns = 4
        frame.grid_rowconfigure(0, weight=0, uniform='skillFrameRow'+environment)
        for row in range(6):
            rowGroup = "0" if row == 0 else ''
            frame.grid_rowconfigure((row*2)+1, weight=1, uniform='skillFrameRow'+environment+rowGroup)
            frame.grid_rowconfigure((row*2)+2, weight=1, uniform='skillFrameRow'+environment+rowGroup)
            rank = -1
            for rankName in self.cache['spaceSkills']:
                rank += 1
                dependencySplit = self.skillSpaceGetFieldSkill(rankName, row, 0, type='linear')
                if row == 0:
                    l = Label(frame, text=rankName.title().replace(' ', '\n'), bg='#3a3a3a', fg='#ffffff', font=font.Font(family='Helvetica', size=12, weight='bold'))
                    l.grid(row=row, column=rank*rankColumns, columnspan=3, sticky='s', pady=1)
                for col in range(rankColumns):
                    rowspan = 2
                    sticky = sticky2 = ''
                    if dependencySplit and col == 1: 
                        rowspan = 1
                        sticky = 's'
                        sticky2 = 'n'
                    if dependencySplit and col == 2: col = 3
                    
                    self.setupSkillButton(frame, rank, rankName, rankColumns, row, col, rowspan, environment, sticky=sticky, rowShift=1)
                    if dependencySplit and col == 1:
                        self.setupSkillButton(frame, rank, rankName, rankColumns, row, col+1, rowspan, environment, sticky=sticky2, colShift=-1, rowShift=2)
        
    def setupSkillButton(self, frame, rank, rankName, rankColumns, row, col, rowspan, environment, sticky='', colShift=0, rowShift=0):
        rowspanMaster = 2
        colActual = ((rank*rankColumns)+col) + colShift
        rowActual = (row * rowspanMaster)+rowShift
        padxCanvas = (2,2)
        padyCanvas = (3,0) if rowActual % 2 != 0 else (0,3)
        frame.grid_columnconfigure(colActual, weight=2 if col == 3 else 1, uniform='skillFrameCol'+environment+str(rank))
        if environment == 'space': name = self.skillSpaceGetFieldNode(rankName, row, col, type='name')
        elif environment == 'ground': name = self.skillGetGroundNode(rank, row, col, type='name')
        backendName = name
        args = [rankName if environment=='space' else rank, row, col, 'skill']
        #self.logWriteSimple('SkillButton', 'create', 2, [rank, row, col, environment, name])
        if not environment in self.build['skilltree']: self.build['skilltree'][environment] = dict()

        if name and col != 3:
            if environment == 'space':
                imagename = self.skillSpaceGetFieldNode(rankName, row, col, type='image')
                desc = self.skillSpaceGetFieldNode(rankName, row, col, type='desc')
                callback = self.skillLabelCallback
            elif environment == 'ground':
                imagename = self.skillGetGroundNode(rank, row, col, type='image')
                desc = self.skillGetGroundNode(rank, row, col, type='desc')
                callback = self.skillGroundLabelCallback
        
            if not name in self.build['skilltree'][environment]: self.build['skilltree'][environment][name] = False
            if not backendName in self.backend['images']: self.backend['images'][backendName] = [ ]
            bg = 'yellow' if name in self.build['skilltree'][environment] and self.build['skilltree'][environment][name] else 'grey'
            if self.build['skilltree'][environment][name]:
                relief = 'raised'
                image1 = self.epicImage
            else:
                relief = 'groove'
                image1 = None
            self.createButton(frame, 'skilltree', callback=callback, row=rowActual, rowspan=rowspan, column=colActual, borderwidth=1, bg=bg, image0Name=imagename, image1=image1, sticky=sticky, relief=relief, padx=padxCanvas, pady=padyCanvas, args=args, name=name, tooltip=desc, anchor='center')
        else:
            self.createButton(frame, '', row=rowActual, rowspan=rowspan, column=colActual, borderwidth=1, bg='#3a3a3a', image0=self.emptyImage, sticky='ns', padx=padxCanvas, pady=padyCanvas, args=args, name='blank', anchor='center')
                        
    def setupSkillBonusFrame(self, parentFrame, environment='space'):
        frame = Frame(parentFrame, bg='#3a3a3a')
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
                args = [None, row, col, 'skill']

                self.createButton(frame, '', row=row, column=colActual, borderwidth=1, bg='#3a3a3a', image0=self.emptyImage, sticky='n', padx=padxCanvas, pady=padyCanvas, args=args, name='blank', anchor='center')

    def setupSpaceTraitFrame(self):
        """Set up UI frame containing traits"""
        outerFrame = self.shipTraitFrame
        outerFrame.grid_rowconfigure(0, weight=1, uniform='shiptraitFrameFullRowSpace')
        outerFrame.grid_columnconfigure(0, weight=1, uniform='shiptraitFrameFullColSpace')
        self.clearFrame(outerFrame)
        
        parentFrame = Frame(outerFrame, bg='#3a3a3a')
        parentFrame.grid(row=0, column=0, sticky='', padx=1, pady=1)

        traitEliteCaptain = 1 if self.backend['eliteCaptain'].get() else 0
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
        
        parentFrame = Frame(outerFrame, bg='#3a3a3a')
        parentFrame.grid(row=0, column=0, sticky='', padx=1, pady=1)

        traitEliteCaptain = 1 if self.backend['eliteCaptain'].get() else 0
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
        
        parentFrame = Frame(outerFrame, bg='#3a3a3a')
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

            bFrame = Frame(parentFrame, width=120, height=80, bg='#3a3a3a')
            bFrame.pack(fill=BOTH, expand=True)
            bSubFrame0 = Frame(bFrame, bg='#3a3a3a')
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
            specLabel0.configure(bg='#3a3a3a', fg='#ffffff', font=('Helvetica', 10), highlightthickness=0)
            specLabel0.pack(side='left')
            
            if environment == 'ground' or (sspec is not None and sspec != ''):
                if environment == 'ground':                    
                    specLabel1 = OptionMenu(bSubFrame0, v2, *sorted(self.cache['specsGroundBoff']))
                    specLabel1.configure(pady=2)
                else:
                    specLabel1 = Label(bSubFrame0, text='/  '+sspec)
                specLabel1.configure(bg='#3a3a3a', fg='#ffffff', font=('Helvetica', 10), highlightthickness=0)
                specLabel1.pack(side='left')
                
            bSubFrame1 = Frame(bFrame, bg='#3a3a3a')
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
                if boffSan in self.build['boffs'] and self.build['boffs'][boffSan][j] is not None:
                    image=self.imageFromInfoboxName(self.build['boffs'][boffSan][j], faction = 1)
                    self.backend['images'][boffSan][j] = image
                else:
                    image=self.emptyImage
                    self.build['boffs'][boffSan] = [None] * rank

                if 0: # migration to createButton
                    row=1
                    #anchor="nw"
                    args = [ self.boffTitleToSpec(v.get()), v2.get(), i, environment ]
                    key = boffSan

                    canvas, img0, img1 = self.createButton(bSubFrame1, row=row, column=j, groupKey='boffs', key=key, i=j, callback=self.boffLabelCallback, args=args, faction = 1, suffix=False)
                else: # prune once above stable
                    canvas = Canvas(bSubFrame1, highlightthickness=0, borderwidth=0, width=self.itemBoxX, height=self.itemBoxY, bg='gray')
                    canvas.grid(row=1, column=j, sticky='ns', padx=2, pady=2)
                    img0 = canvas.create_image(0,0, anchor="nw",image=image)
                    canvas.bind('<Button-1>', lambda e,canvas=canvas,img=img0,i=j,key=boffSan,environment=environment,v=v,v2=v2,callback=self.boffLabelCallback:callback(e,canvas,img,i,key,[self.boffTitleToSpec(v.get()), v2.get(), i, environment]))
                    canvas.bind('<Enter>', lambda e,item=self.build['boffs'][boffSan][j],environment=environment:self.setupInfoboxFrameSplitter(item, '', environment))


    def setupSpaceBuildFrames(self):
        """Set up all relevant space build frames"""
        self.build['tier'] = self.backend['tier'].get()
        if self.backend['shipHtml'] is not None or self.persistent['keepTemplateOnShipClear']:
            self.setupDoffFrame(self.shipDoffFrame)
            self.setupShipGearFrame(self.backend['shipHtml'])
            self.setupBoffFrame('space', self.backend['shipHtml'])
            self.setupSpaceTraitFrame()
        else:
            self.clearFrame(self.shipEquipmentFrame)
            self.clearFrame(self.shipConsoleFrame)
            self.clearFrame(self.shipBoffFrame)
            self.clearFrame(self.shipTierFrame)
            self.clearFrame(self.shipDoffFrame)
            self.clearFrame(self.shipTraitFrame)

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
        if not len(itemVar['modifiers']):
            itemVar['modifiers'] = ['']*n
            
        mods = sorted(self.cache['modifiers'])
        for i in range(n):
            v = StringVar()
            if i < len(itemVar['modifiers']):
                v.set(itemVar['modifiers'][i])
            v.trace_add('write', lambda v0,v1,v2,i=i,itemVar=itemVar,v=v:self.setListIndex(itemVar['modifiers'],i,v.get()))
            OptionMenu(frame, v, *mods).grid(row=0, column=i, sticky='n')

    def getURL(self, name):
        return self.wikihttp + name
        
    def clearInfoboxFrame(self, environment):
        self.setupInfoboxFrameSplitter(self.getEmptyItem(), '', environment)
        
    def setupInfoboxFrameSplitter(self, item, key, environment='space', tooltip=None):
        if self.persistent['useExperimentalTooltip']: self.setupInfoboxFrame(item, key, environment, tooltip)
        else: self.setupInfoboxFrameStatic(item, key, environment, tooltip)
    
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
                            currentlength = currentlength - width
                        if currentlength + font.Font(family=pfamily, size=psize, weight=pweight).measure(" ") > width:
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
            elif identifier == "personaltrait":
                hgt = lines+1
            elif identifier == "boff":
                hgt = lines+1
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
        return text
        
    def insertInfoboxParagraph(self, inframe: Frame, ptext: str, pfamily, pcolor, psize, pweight, gridrow, framewidth): #returns text string that has to be placed a level above (for recursion)
        """Inserts Infobox paragraph into a frame"""
        mainframe = Frame(inframe, bg="#090b0d", highlightthickness=0, highlightcolor='#090b0d')
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
                elif "\n" in ptext[:occs[0]] :
                    end = ptext.find("\n")
                else:
                    for j in range(0, len(occs)):
                        if "\n" in ptext[:occs[j]].replace("\n:",""):
                            end = ptext.find("\n", occs[j]+1)
                            break
                    if end==0:
                        if "\n" in ptext.replace("\n:","").strip():
                            end = ptext.find("\n", occs[len(occs)-1]+1)
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
                        end = ptext.find("\n", occs[k], occs[k+1])
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
                elif "\n" in ptext[:occs[0]] :
                    end = ptext.find("\n")
                else:
                    for j in range(0, len(occs)-1):
                        if "\n" in ptext[occs[j]+1:occs[j+1]].replace("\n*",""):
                            end = ptext.find("\n", occs[j], occs[j+1])
                            break
                    if end==0:
                        if "\n" in ptext.replace("\n*",""):
                            end = ptext.find("\n", occs[len(occs)-1] if occs != [] else len(ptext)-1)
                        else:
                            end=-2
                if end == -2:
                    passtext = ptext.replace("\n*", "\n• ").replace("*","• ")
                else:
                    passtext = ptext[0:end+1].replace("\n*","\n• ").replace("*","• ")
                    inserttext2 = ptext[end+2:]
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
            maintext = Text(mainframe, bg='#090b0d', fg=pcolor, wrap=WORD, highlightthickness=0, highlightcolor='#090b0d', relief="flat", font=(pfamily, psize, pweight), height=self.getDH(framewidth, inserttext1, pfamily, psize, pweight))
            maintext.grid(row=rowinsert,column=0)
            mainframe.rowconfigure(rowinsert, weight=0)
            mainframe.rowconfigure(rowinsert+1, weight=0)
            inframe.update()
            mainframe.columnconfigure(0, weight=1)
            mainframe.columnconfigure(1, weight=1)
            maintext.insert(END, inserttext1)
            maintext.configure(state=DISABLED)
            rowinsert = rowinsert+1
        if not passtext == "":
            lineframe = Frame(mainframe, bg="#090b0d", highlightthickness=0, highlightcolor='#090b0d')
            lineframe.grid(row=rowinsert, column=0, sticky="nsew")
            mainframe.rowconfigure(rowinsert, weight=0)
            mainframe.rowconfigure(rowinsert+1, weight=0)
            mainframe.columnconfigure(0, weight=1)
            mainframe.columnconfigure(1, weight=1)
            lineframe.rowconfigure(0, weight=0)
            lineframe.columnconfigure(0, weight=1, minsize=12)
            lineframe.columnconfigure(1, weight=7)
            lineframe.columnconfigure(2, weight=1)
            daughterframe = Frame(lineframe, bg="#090b0d", highlightcolor="#090b0d", highlightthickness=0)
            daughterframe.grid(row=0, column=1, sticky="nsew")
            self.insertInfoboxParagraph(daughterframe, passtext, pfamily, pcolor, psize, pweight, 0, framewidth-12)
            rowinsert = rowinsert + 1
        if not inserttext2 == "":
            lineframe = Frame(mainframe, bg="#090b0d", highlightthickness=0, highlightcolor='#090b0d')
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
            self.logWriteSimple('InfoboxFail', environment, 4, tags=["NO NAME", key])
            return
        self.logWriteSimple('Infobox', environment, 4, tags=[name, key])
        if self.displayedInfoboxItem == name:
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

        if key is not None and key != '':
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
        
        Label(frame, text="Stats & Other Info", highlightbackground="grey", highlightthickness=1).pack(fill=X, expand=False, side=TOP)
        mtfr = Frame(frame, bg="#090b0d", highlightthickness=0, highlightcolor='#090b0d')
        mtfr.pack(fill="both",expand=False,side=TOP)
        text = Text(mtfr, font=('Helvetica', 10), bg='#090b0d', fg='#ffffff', wrap=WORD, highlightthickness=0, highlightcolor='#090b0d', relief="flat", height=3.5)
        
        text.tag_configure('head', foreground='#42afca', font=('Helvetica', 12, 'bold' ))
        text.tag_configure('name', foreground=raritycolor, font=('Helvetica', 15, 'bold'))
        text.tag_configure('rarity', foreground=raritycolor, font=('Helvetica', 10))
        text.tag_configure('subhead', foreground='#f4f400', font=('Helvetica', 10, 'bold' )) 
        text.tag_configure('starshipTraitHead', foreground='#42afca', font=('Helvetica', 15, 'bold' ))
        text.tag_configure('boffhead', foreground="#42afca", font=('Helvetica', 15, 'bold'))
        
        
        text.grid(row=0, column=0)
        mtfr.rowconfigure(0, weight=0)
        mtfr.rowconfigure(2, weight=0, minsize=8)
        mtfr.rowconfigure(1, weight=0)
        mtfr.rowconfigure(3, weight=1)
        mtfr.columnconfigure(0, weight=1)
        mtfr.columnconfigure(1, weight=1)

        printed = bool(False)

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
                whotext = Text(mtfr, font=('Helvetica', 10), bg='#090b0d', fg='#ff6347', wrap=WORD, highlightthickness=0, highlightcolor='#090b0d', relief="flat", height=self.getDH(mtfr.winfo_width(), html['who'], "Helvetica", 10, "normal"))
                whotext.grid(row=1, column=0)
                whotext.insert(END, html["who"])
                whotext.configure(state=DISABLED)
            Frame(mtfr, background='#090b0d', highlightthickness=0, highlightcolor='#090b0d').grid(row=2,column=0,sticky="nsew")
            contentframe = Frame(mtfr, bg="#090b0d", highlightthickness=0, highlightcolor='#090b0d')
            contentframe.grid(row=3, column=0, sticky="nsew")
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
            printed = True
        
        if (name in self.cache['shipTraits'])and not printed:
            text.insert(END, name+"\n", 'starshipTraitHead')
            text.insert(END, "Starship Trait\n", 'head')
            text.insert(END, "Placeholder for obtain information", "subhead")
            text.update()
            text.configure(height=self.getDH(text.winfo_width(), name+"\n"+"StarshipTrait\n"+"Placeholder for obtain information", "Helvetica", 15, "bold", "traithead"))
            Frame(mtfr, background='#090b0d', highlightthickness=0, highlightcolor='#090b0d').grid(row=2,column=0,sticky="nsew")
            contentframe = Frame(mtfr, bg="#090b0d", highlightthickness=0, highlightcolor='#090b0d')
            contentframe.grid(row=3, column=0, sticky="nsew")
            self.insertInfoboxParagraph(contentframe, self.compensateInfoboxString(self.cache['shipTraits'][name].strip()), "Helvetiva", "#ffffff", 10, "normal", 0, text.winfo_width())
            printed = True

        if (environment in self.cache['traits'] and name in self.cache['traits'][environment]) and not printed:
            text.insert(END, name+"\n", 'starshipTraitHead')
            text.update()
            text.configure(height=self.getDH(text.winfo_width(), name, "Helvetica", 15, "bold", "personaltrait"))
            contentframe = Frame(mtfr, bg="#090b0d", highlightthickness=0, highlightcolor='#090b0d')
            contentframe.grid(row=2, column=0, sticky="nsew")
            self.insertInfoboxParagraph(contentframe, self.compensateInfoboxString(self.cache['traits'][environment][name].strip()), "Helvetiva", "#ffffff", 10, "normal", 0, text.winfo_width())
            printed = True

        if (environment in self.cache['boffTooltips'] and name in self.cache['boffTooltips'][environment]) and not printed:
            text.insert(END, name, 'boffhead')
            text.update()
            text.configure(height=self.getDH(text.winfo_width(), name, "Helvetica", 15, "bold", "boff"))
            contentframe = Frame(mtfr, bg="#090b0d", highlightthickness=0, highlightcolor='#090b0d')
            contentframe.grid(row=2, column=0, sticky="nsew")
            self.insertInfoboxParagraph(contentframe, self.compensateInfoboxString(self.cache['boffTooltips'][environment][name].strip()), "Helvetiva", "#ffffff", 10, "normal", 0, text.winfo_width())
            printed = True

        text.configure(state=DISABLED)
        frame.pack_propagate(True)


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
        
        Label(frame, text="Stats & Other Info", highlightbackground="grey", highlightthickness=1).pack(fill=X, expand=False, side=TOP)
        text = Text(frame, height=height, width=width, font=('Helvetica', 10), bg='#090b0d', fg='#ffffff', wrap=WORD)
        text.tag_configure('name', foreground=raritycolor, font=('Helvetica', 15, 'bold'))
        text.tag_configure('rarity', foreground=raritycolor, font=('Helvetica', 10))
        text.tag_configure('head', foreground='#42afca', font=('Helvetica', 12, 'bold' ))
        text.tag_configure('subhead', foreground='#f4f400', font=('Helvetica', 10, 'bold' ))
        text.tag_configure('who', foreground='#ff6347', font=('Helvetica', 10, 'bold' ))
        text.tag_configure('distance', foreground='#000000', font=('Helvetica', 4))
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
        
    def setupDoffListFrame(self, frame, environment='space'):
        doffEnvironment = environment.title()
        isSpace = False if environment == 'ground' else True
        self.precacheDoffs(doffEnvironment)
        doff_list = sorted([self.deWikify(item) for item in list(self.cache['doffNames'][doffEnvironment].keys())])

        DoffFrame = Frame(frame, bg='#b3b3b3', padx=5, pady=3)
        DoffFrame.pack(side='left' if environment == 'ground' else 'left', fill=Y, expand=True)
        DoffFrame.grid_columnconfigure(2, weight=1, uniform=environment+'ColDoffList')
        #DoffFrame.grid_columnconfigure(1, weight=1, uniform=environment+'ColDoffList')
        #DoffFrame.grid_columnconfigure(2, weight=2, uniform=environment+'ColDoffList')
        
        DoffLabel = Label(DoffFrame, text=environment.upper()+" DUTY OFFICERS", bg='#3a3a3a', fg='#ffffff', width=60)
        DoffLabel.grid(row=0, column=0, columnspan=3, sticky='nsew')
        
        f = font.Font(family='Helvetica', size=9)
        for i in range(6):
            v0 = StringVar(self.window)
            v1 = StringVar(self.window)
            v2 = StringVar(self.window)
            #m = OptionMenu(DoffFrame, v0, 'NAME', *['A','B','C'])
            #m.grid(row=i+1, column=0, sticky='nsew')
            #m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0, state=DISABLED)
            m = OptionMenu(DoffFrame, v1, 'SPECIALIZATION', *doff_list)
            m.grid(row=i+1, column=1, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0, width=23)
            m = OptionMenu(DoffFrame, v2, 'EFFECT\nOTHER', '')
            m.grid(row=i+1, column=2, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0,font=f, wraplength=340)
            
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
        mainFrame = Frame(frame, bg='#3a3a3a')
        mainFrame.pack(side='bottom', fill=BOTH, expand=True, pady=(5,0))
        
        self.setupDoffListFrame(mainFrame, 'space')
        DoffBreak = Frame(mainFrame, bg='#3a3a3a', width=10)
        DoffBreak.pack(side='left')
        DoffBreakLabel = Label(DoffBreak, text='', bg='#3a3a3a', fg='#ffffff')
        DoffBreakLabel.grid(row=0, column=0, sticky='nsew')
        self.setupDoffListFrame(mainFrame, 'ground')

    def setupLogoFrame(self):
        self.clearFrame(self.logoFrame)
        
        #maxWidth = self.window.winfo_screenwidth()
        #if maxWidth > self.windowWidth:
            #maxWidth = self.windowWidth
        self.images['logoImage'] = self.loadLocalImage("logo_bar.png", width=self.windowWidthDefault, height=self.logoHeight)
        
        Label(self.logoFrame, image=self.images['logoImage'], borderwidth=0, highlightthickness=0).pack()

    def setupFooterFrame(self):
        self.footerFrame = Frame(self.containerFrame, bg='#c59129', height=20)
        self.footerFrame.pack(fill='both', side='bottom', expand=False)
        f = font=('Helvetica', 9)
        f2 = font=('Helvetica', 10, 'bold')
        
        self.footerFrameL = Frame(self.footerFrame, bg='#c59129')
        self.footerFrameL.grid(row=0, column=0, sticky='w')
        footerLabelL = Label(self.footerFrameL, textvariable=self.log, fg='#3a3a3a', bg='#c59129', anchor='w', font=f)
        footerLabelL.grid(row=0, column=0, sticky='w')

        self.footerFrameM = Frame(self.footerFrame, bg='#c59129')
        self.footerFrameM.grid(row=0, column=1, sticky='ew')
        self.footerFrameM.grid_columnconfigure(0, weight=1, uniform="footerlabel")
        self.footerProgressBar = Progressbar(self.footerFrameM, orient='horizontal', mode='indeterminate', length=120)
        self.footerProgressBar.grid(row=0, column=0, sticky='ew')
        
        self.footerFrameR = Frame(self.footerFrame, bg='#c59129')
        self.footerFrameR.grid(row=0, column=2, sticky='e')
        footerLabelR = Label(self.footerFrameR, textvariable=self.logmini, fg='#3a3a3a', bg='#c59129', anchor='e', font=f2)
        footerLabelR.grid(row=0, column=0, sticky='e')
        
        self.footerFrame.grid_columnconfigure(0, weight=2, uniform="footerlabel")
        self.footerFrame.grid_columnconfigure(1, weight=1, uniform="footerlabel")
        self.footerFrame.grid_columnconfigure(2, weight=2, uniform="footerlabel")

        
    def lineTruncate(self, content, length=500):
        return '\n'.join(content.split('\n')[-1*length:])
        
    def setFooterFrame(self, leftnote, rightnote=None):
        """Set up footer frame with given item"""
        leftnote = leftnote[:150]
        rightnote = rightnote[:60]

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
            'Space Skill Tree'             : {'type' : 'buttonblock', 'varName' : 'spaceSkillButton', 'callback' : self.focusSpaceSkillBuildFrameCallback, 'colWeight' : 1},
            'Ground Skill Tree'            : {'type' : 'buttonblock', 'varName' : 'groundSkillButton', 'callback' : self.focusGroundSkillBuildFrameCallback, 'colWeight' : 1},
        }
        
        self.createItemBlock(parentFrame, theme=settingsMenuSkill, shape='row', elements=1)


    def setupMenuFrame(self):
        self.clearFrame(self.menuFrame)
        
        settingsMenuTop = {
            'SPACE'             : {'type' : 'buttonblock', 'varName' : 'spaceButton', 'callback' : self.focusSpaceBuildFrameCallback},
            'GROUND'            : {'type' : 'buttonblock', 'varName' : 'groundButton', 'callback' : self.focusGroundBuildFrameCallback},
            'SKILL TREE'        : {'type' : 'buttonblock', 'varName' : 'skillButton', 'callback' : self.focusSkillTreeFrameCallback},
        }
        
        col = 0
        exportImportFrame = Frame(self.menuFrame, bg='#3a3a3a')
        exportImportFrame.grid(row=0, column=col, sticky='nsew')
        self.setupButtonExportImportFrame(exportImportFrame)
        col += 1
        
        self.createItemBlock(self.menuFrame, row=0, col=col, theme=settingsMenuTop, shape='row', elements=1, bg='#6b6b6b', fg='#ffffff', fontDefault={'size':12,'weight':'bold'})
        col += 3

        buttonSettings = Frame(self.menuFrame, bg='#3a3a3a')
        buttonSettings.grid(row=0, column=col, sticky='nsew')
        self.setupButtonSettingsFrame(buttonSettings)
        col += 1
        for i in range(5):
            self.menuFrame.grid_columnconfigure(i, weight=1, uniform="mainCol")


    def setupButtonExportImportFrame(self, parentFrame):
        self.clearFrame(parentFrame)
        
        settingsMenuExport = {
            'Export\nFull'  : { 'type' : 'buttonblock', 'varName' : 'exportFullButton', 'callback' : self.exportCallback},
            'Export\nreddit': { 'type' : 'buttonblock', 'varName' : 'exportRedditButton', 'callback' : self.exportRedditCallback},
            'Import'        : { 'type' : 'buttonblock', 'varName' : 'importButton', 'callback' : self.importCallback},
        }
        
        self.createItemBlock(parentFrame, theme=settingsMenuExport, shape='row', elements=1)

        
    def setupButtonSettingsFrame(self, parentFrame):
        self.clearFrame(parentFrame)
        
        settingsMenuSettings = {
            'Clear'     : { 'type' : 'buttonblock', 'varName' : 'clearButton', 'callback' : self.clearBuildCallback},
            'LIBRARY'   : { 'type' : 'buttonblock', 'varName' : 'libraryButton', 'callback' : self.focusLibraryFrameCallback},
            'SETTINGS'  : { 'type' : 'buttonblock', 'varName' : 'settingsButton', 'callback' : self.focusSettingsFrameCallback},
        }
        
        self.createItemBlock(parentFrame, theme=settingsMenuSettings, shape='row', elements=1)
        
        
    def setupTierFrame(self, tier):
        f = font.Font(family='Helvetica', size=9)
        l = Label(self.shipTierFrame, text="Tier:", fg='#3a3a3a', bg='#b3b3b3', font=f)
        l.grid(row=0, column=0, sticky='nsew')
        l.configure(borderwidth=0, highlightthickness=0)
        m = OptionMenu(self.shipTierFrame, self.backend["tier"], *self.getTierOptions(tier))
        m.grid(column=1, row=0, sticky='swe', pady=2, padx=2)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0, font=f)
        
        
    def setupShipImageFrame(self):
        try:
            self.backend['shipHtml'] = self.getShipFromName(self.ships, self.build['ship'])
            ship_image = self.backend['shipHtml']['image']
            self.shipImg = self.fetchOrRequestImage(self.wikiImages+ship_image.replace(' ','_'), self.build['ship'], self.shipImageWidth, self.shipImageHeight)
        except:
            self.shipImg = self.getEmptyFactionImage()
        self.setShipImage(self.shipImg)

    def setupTagsFrame(self, buildTagFrame, environment='space'):
        if environment != 'ground':
            self.shipTierFrame = Frame(buildTagFrame, bg='#b3b3b3')
            self.shipTierFrame.pack(fill=X, expand=False)
            
        #Label(buildTagFrame, text="BUILD TAGS", fg='#3a3a3a', bg='#b3b3b3').pack(fill=X, expand=False)
        for tag in ["DEW", "KINETIC", "EPG", "DEWSCI", "THEME"]:
            tagFrame = Frame(buildTagFrame, bg='#b3b3b3')
            tagFrame.pack(fill=X, expand=False)
            v = IntVar(self.window, value=(1 if tag in self.build['tags'] and self.build['tags'][tag] == 1 else 0))
            Checkbutton(tagFrame, variable=v, fg='#3a3a3a', bg='#b3b3b3').grid(row=0,column=0)
            v.trace_add("write", lambda v,i,m,var=v,text=tag:self.tagBoxCallback(var,text))
            Label(tagFrame, text=tag, fg='#3a3a3a', bg='#b3b3b3').grid(row=0,column=1)
        
    def setupCaptainFrame(self, charInfoFrame, environment='space'):
        self.precacheReputations()
        row = 0
        Label(charInfoFrame, text="Elite Captain", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = row, sticky='e')
        m = Checkbutton(charInfoFrame, variable=self.backend["eliteCaptain"], fg='#3a3a3a', bg='#b3b3b3', command=self.eliteCaptainCallback)
        m.grid(column=1, row=row, sticky='w', pady=2, padx=2)
        m.configure(fg='#3a3a3a', bg='#b3b3b3', borderwidth=0, highlightthickness=0)
        if environment == 'space':
            self.shipTierFrame = Frame(charInfoFrame, bg='#b3b3b3')
            self.shipTierFrame.grid(column=3, row=row, columnspan=1, sticky='swe')

        row += 1
        Label(charInfoFrame, text="Captain Career", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = row, sticky='e')
        m = OptionMenu(charInfoFrame, self.backend["career"], "", "Tactical", "Engineering", "Science")
        m.grid(column=1, row=row, columnspan=3,  sticky='swe', pady=2, padx=2)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
 
        row += 1       
        Label(charInfoFrame, text="Species", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = row, sticky='e')
        m = OptionMenu(charInfoFrame, self.backend["species"], *self.speciesNames)
        m.grid(column=1, row=row, columnspan=3,  sticky='swe', pady=2, padx=2)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
 
        row += 1
        myFactionNames = self.factionNames
        Label(charInfoFrame, text="Faction", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = row, sticky='e')
        m = OptionMenu(charInfoFrame, self.backend['captain']['faction'], *myFactionNames)
        m.grid(column=1, row=row, columnspan=3,  sticky='swe', pady=2, padx=2)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)

        row += 1 
        Label(charInfoFrame, text="Primary Spec", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = row, sticky='e')
        m = OptionMenu(charInfoFrame, self.backend["specPrimary"], '', *sorted(self.cache['specsPrimary']))
        m.grid(column=1, row=row, columnspan=3,  sticky='swe', pady=2, padx=2)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)

        row += 1
        Label(charInfoFrame, text="Secondary Spec", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = row, sticky='e')
        m = OptionMenu(charInfoFrame, self.backend["specSecondary"], '', *sorted(self.cache['specsSecondary']))
        m.grid(column=1, row=row, columnspan=3,  sticky='swe', pady=2, padx=2)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
        
        charInfoFrame.grid_columnconfigure(1, weight=1, uniform="captColSpace")
        
    def updateShipDesc(self, event):
        self.build['playerShipDesc'] = self.shipDescText.get("1.0", END)
    
    def updatePlayerDesc(self, event):
        self.build['playerDesc'] = self.charDescText.get("1.0", END)
        
    def updateWindowSize(self):
        self.windowWidth = self.window.winfo_width()
        self.windowHeight = self.window.winfo_height()
        self.windowXCache = self.window.winfo_x()
        self.windowYCache = self.window.winfo_y()
    
    def updateImageLabelSize(self, frame=None, source=''):
        if frame is None:
            try:
                frame = self.shipImageLabel
            except:
                pass
        if frame is not None:
            frame.update()
            width = frame.winfo_width()
            height = frame.winfo_height()
            if width > self.imageBoxX and height > self.imageBoxY:
                resizeShip = True if width > (self.shipImageWidth + 20) or height > self.shipImageHeight + 20 else False

                self.shipImageWidth  = width-1
                self.shipImageHeight = height-7
                if resizeShip and self.shipImageResizeCount < 3: 
                    self.setupShipImageFrame()
                    self.shipImageResizeCount += 1
        else:
            self.shipImageWidth  = self.imageBoxX
            self.shipImageHeight = self.imageBoxY
        self.logWriteSimple('ImageLabel', 'size', 3, ['{}x{}'.format(self.shipImageWidth,self.shipImageHeight), source] )
        #if source == 'focusSpaceBuildFrameCallback':
            #self.logWriteSimple('ImageLabel-ground', 'size', 3, ['{}x{}'.format(self.charImageLabel.winfo_width(),self.charImageLabel.winfo_height())])
        
    def setShipImage(self, suppliedImage=None):
        if suppliedImage is None: suppliedImage = self.getEmptyFactionImage()
        if suppliedImage == self.getEmptyFactionImage(): bgColor = '#3a3a3a'
        else: bgColor = '#000000'
        
        if 1:
            self.shipImageLabel.configure(image=suppliedImage, bg=bgColor)
        else:
            # future canvas conversion
            image1 = self.imageFromInfoboxName('Epic') if 'tier' in self.build and self.build['tier'] == "T6-X" else self.emptyImage
            self.shipImagecanvas.itemconfig(self.shipImage0,image=suppliedImage)
            self.shipImagecanvas.itemconfig(self.shipImage1,image=image1)   
            self.shipImagecanvas.configure(bg=bgColor, highlightthickness=0)

    def setCharImage(self, suppliedImage=None):
        if suppliedImage is None: suppliedImage = self.getEmptyFactionImage()
        if suppliedImage == self.getEmptyFactionImage(): bgColor = '#3a3a3a'
        else: bgColor = '#000000'
        
        if 1:
            self.charImageLabel.configure(image=suppliedImage, bg=bgColor)
        else:
            # future canvas conversion
            image1 = self.imageFromInfoboxName('Epic') if 'eliteCaptain' in self.build and self.build['eliteCaptain'] else self.emptyImage
            self.charImagecanvas.itemconfig(self.charImage0,image=suppliedImage)
            self.charImagecanvas.itemconfig(self.charImage0,image=image1)   
            self.charImagecanvas.configure(bg=bgColor, highlightthickness=0)
            
    def setupInfoFrame(self, environment='space'):
        if environment == 'ground': parentFrame = self.groundInfoFrame
        elif environment == 'skill': parentFrame = self.skillInfoFrame
        else: parentFrame = self.shipInfoFrame

        self.clearFrame(parentFrame)
        
        #exportImportFrame = Frame(parentFrame, bg='#3a3a3a')
        #exportImportFrame.pack(fill=X, expand=True)
        #self.setupButtonExportImportFrame(exportImportFrame)
        
        LabelFrame = Frame(parentFrame, bg='#3a3a3a')
        LabelFrame.pack(fill=BOTH, expand=True, side=TOP)
        if 1:
            imageLabel = Label(LabelFrame, fg='#3a3a3a', bg='#3a3a3a', highlightbackground="black", highlightthickness=1)
            if environment == 'ground': self.charImageLabel = imageLabel
            elif environment == 'skill': self.skillImageLabel = imageLabel
            else: self.shipImageLabel = imageLabel
            imageLabel.pack(fill=BOTH, expand=True)
            imageLabel.configure(image=self.getEmptyFactionImage())
        else:  #canvas conversion tests
            imageCanvas = Canvas(LabelFrame, highlightthickness=1, borderwidth=0, bg='#3a3a3a', highlightbackground="black")
            imageCanvas.grid(row=0, column=0, sticky='nse')
            LabelFrame.grid_columnconfigure(0, weight=1)
            img0 = imageCanvas.create_image(imageCanvas.winfo_width() / 2,imageCanvas.winfo_height() / 2, anchor="center",image=self.getEmptyFactionImage())
            img1 = imageCanvas.create_image(0,0, anchor="nw",image=self.emptyImage)
            if environment == 'ground':
                self.charImagecanvas = imageCanvas
                self.charImage0 = img0
                self.charImage1 = img1
            else:
                self.shipImagecanvas = imageCanvas
                self.shipImage0 = img0
                self.shipImage1 = img1
                    
        if environment != 'skill':
            NameFrame = Frame(parentFrame, bg='#b3b3b3')
            NameFrame.grid_columnconfigure(1, weight=1)
            
            row = 0
            if environment == 'space':
                Label(NameFrame, text="Ship: ", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = row, sticky='w')
                self.shipButton = Button(NameFrame, text="<Pick>", command=self.shipPickButtonCallback, bg='#b3b3b3', wraplength=270)
                self.shipButton.grid(column=1, row=row, sticky='nwse')
                row += 1
       
            Label(NameFrame, text="{} Name:".format('Ship' if environment == 'space' else 'Toon'), fg='#3a3a3a', bg='#b3b3b3').grid(row=row, column=0, sticky='w')
            Entry(NameFrame, textvariable=self.backend['player{}Name'.format('Ship' if environment == 'space' else '')], fg='#3a3a3a', bg='#b3b3b3', font=('Helvetica', 10, 'bold')).grid(row=row, column=1, sticky='nsew', ipady=5, pady=5)
            row += 1
            # end of not-skill items
           
        ExtraFrame = Frame(parentFrame, bg='#b3b3b3')
        ExtraFrame.pack(fill=X, expand=True, padx=0, pady=0, side=BOTTOM)
        CharFrame = Frame(parentFrame, bg='#b3b3b3')
        CharFrame.pack(fill=X, expand=False, padx=2, side=BOTTOM)
        CharFrame.grid_columnconfigure(0, weight=1)
        charInfoFrame = Frame(CharFrame, bg='#b3b3b3')
        charInfoFrame.grid(row=0, column=0, columnspan=2, sticky='ew')
        self.setupCaptainFrame(CharFrame, environment)   
        if environment == 'skill':
            ExtraFrame = Frame(parentFrame, bg='#b3b3b3')
            ExtraFrame.pack(fill=X, expand=True, padx=0, pady=0, side=BOTTOM)
        
        if environment != 'skill': NameFrame.pack(fill=X, expand=False, padx=(0,5), pady=(5,0), side=BOTTOM)
        
        if environment == 'space':
            if self.build['ship'] is not None: self.shipButton.configure(text=self.build['ship'])
            if 'tier' in self.build and len(self.build['tier']) > 1:
                self.setupTierFrame(int(self.build['tier'][1]))
                self.setupShipImageFrame()
                pass
                
    def setupDescFrame(self, environment='space'):
        if environment == 'skill':
            self.setupDescEnvironmentFrame(environment='space', destination='skill')
            self.setupDescEnvironmentFrame(environment='ground', destination='skill', row=2)
        else: self.setupDescEnvironmentFrame(environment=environment)
    
    def setupDescEnvironmentFrame(self, environment='space', destination=None, row=0):
        if destination is not None: parentFrame = self.skillDescFrame
        elif environment == 'space': parentFrame = self.shipDescFrame
        elif environment == 'ground': parentFrame = self.groundDescFrame
        else: return
        
        if row == 0: self.clearFrame(parentFrame)
        parentFrame.grid_columnconfigure(0, weight=1)

        label = Label(parentFrame, text="Build Description ({}):".format(environment.title()), fg='#3a3a3a', bg='#b3b3b3')
        label.grid(row=row, column=0, sticky='nw')
        # Hardcoded width due to issues with expansion, this should become dynamic here and in ground at some point
        descText = Text(parentFrame, height=3, width=20, wrap=WORD, fg='#3a3a3a', bg='#b3b3b3', font=('Helvetica', 8, 'bold'))
        descText.grid(row=row+1, column=0, sticky='nsew', padx=5, pady=2)
        
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
        
        middleFrameUpper = Frame(parentFrame, bg='#3a3a3a')
        middleFrameUpper.grid(row=0,column=0,columnspan=3,sticky='nsew')
        middleFrameUpper.grid_rowconfigure(0, weight=1, uniform="secRow"+environment)
        middleFrameUpper.grid_columnconfigure(0, weight=1, uniform="secCol"+environment)
        middleFrameUpper.grid_columnconfigure(1, weight=1, uniform="secCol"+environment)
        middleFrameUpper.grid_columnconfigure(2, weight=1, uniform="secCol"+environment)
        
        col = 0
        equipmentFrame = Frame(middleFrameUpper, bg='#3a3a3a')
        equipmentFrame.grid(row=0,column=col,sticky='nsew')
        #equipmentFrame.pack(side='left', fill=BOTH, expand=True, padx=20)
        col += 1
        if environment == 'space':
            middleFrameUpper.grid_columnconfigure(3, weight=1, uniform="secCol"+environment)
            consoleFrame = Frame(middleFrameUpper, bg='#3a3a3a')
            consoleFrame.grid(row=0,column=col,sticky='nsew')
            col += 1
        boffFrame = Frame(middleFrameUpper, bg='#3a3a3a')
        boffFrame.grid(row=0,column=col,sticky='nsew')
        col += 1
        traitFrame = Frame(middleFrameUpper, bg='#3a3a3a')
        traitFrame.grid(row=0,column=col,sticky='nsew')
        col += 1
        
        middleFrameLower = Frame(parentFrame, bg='#3a3a3a')
        middleFrameLower.grid(row=1,column=0,columnspan=3,sticky='nsew')
        middleFrameLower.grid_columnconfigure(0, weight=1, uniform="secCol2"+environment)
        doffFrame = Frame(middleFrameLower, bg='#3a3a3a')
        doffFrame.pack(fill=BOTH, expand=True, padx=15, side=BOTTOM)
        
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
        
        parentFrame.grid_rowconfigure(0, weight=1, uniform="mainRow"+environment)
        for i in range(4):
            parentFrame.grid_columnconfigure(i, weight=5, uniform="mainCol"+environment)
        parentFrame.grid_columnconfigure(4, weight=5, uniform="mainCol"+environment)
        
        infoFrame = Frame(parentFrame, bg='#b3b3b3', highlightbackground="grey", highlightthickness=1)
        infoFrame.grid(row=0,column=0,sticky='nsew',rowspan=2, padx=(2,0), pady=(2,2))

        middleFrame = Frame(parentFrame, bg='#3a3a3a')
        middleFrame.grid(row=0,column=1,columnspan=3,sticky='nsew', pady=5)
        if environment == 'skill':
            middleFrame.grid_rowconfigure(1, weight=1)
            middleFrame.grid_columnconfigure(0, weight=1)
            
            middleFrameUpper = Frame(middleFrame, bg='#3a3a3a')
            middleFrameUpper.grid(row=0,column=0,sticky='nsew')
            self.setupSkillMenuFrame(middleFrameUpper)
            
            middleFrameLower = Frame(middleFrame, bg='#3a3a3a')
            middleFrameLower.grid(row=1,column=0,sticky='nsew')
            middleFrameLower.grid_rowconfigure(1, weight=1)
            middleFrameLower.grid_columnconfigure(0, weight=1)

            self.skillSpaceBuildFrame = Frame(middleFrameLower, bg='#3a3a3a')
            self.skillGroundBuildFrame = Frame(middleFrameLower, bg='#3a3a3a')
            self.focusSkillBuildFrameCallback('space', init=True)
        if environment == 'space' or environment == 'ground':
            self.setupInitialBuildGearFrame(middleFrame, environment=environment)
            
        infoBoxOuterFrame = Frame(parentFrame, bg='#b3b3b3', highlightbackground="grey", highlightthickness=1)
        infoBoxOuterFrame.grid(row=0,column=4,rowspan=2,sticky='nsew', padx=(2,0), pady=(2,2))
        
        buildTagFrame = Frame(infoBoxOuterFrame, bg='#b3b3b3')
        buildTagFrame.pack(fill=X, expand=False, side=BOTTOM)

        descFrame = Frame(infoBoxOuterFrame, bg='#b3b3b3')
        descFrame.pack(fill=X, expand=False, side=BOTTOM)
        
        infoboxFrame = Frame(infoBoxOuterFrame, bg='#b3b3b3', highlightbackground="grey", highlightthickness=1)
        infoboxFrame.pack(fill=BOTH, expand=False, side=TOP)
                
        if environment == 'skill':
            self.skillInfoFrame = infoFrame
            self.skillInfoboxFrame = infoboxFrame
            self.skillDescFrame = descFrame
            self.skillImg = self.getEmptyFactionImage()
        elif environment == 'ground':
            self.groundInfoFrame = infoFrame
            self.groundInfoboxFrame = infoboxFrame
            self.groundDescFrame = descFrame
            self.groundImg = self.getEmptyFactionImage()
        else:
            self.shipInfoFrame = infoFrame
            self.shipInfoboxFrame = infoboxFrame
            self.shipDescFrame = descFrame
            self.shipImg = self.getEmptyFactionImage()
            
        self.setupTagsFrame(buildTagFrame, environment)


    def setupLibraryFrame(self):
        pass #placeholder

    def setupSettingsFrame(self):
        settingsTopFrame = Frame(self.settingsFrame, bg='#b3b3b3')
        settingsTopFrame.pack(side='top', fill=BOTH, expand=True)
        settingsBottomFrame = Frame(self.settingsFrame, bg='#b3b3b3')
        settingsBottomFrame.pack(side='bottom', fill=BOTH, expand=True)
        
        settingsTopLeftFrame = Frame(settingsTopFrame, bg='#b3b3b3')
        settingsTopLeftFrame.grid(row=0,column=0,sticky='nsew', pady=5)
        settingsTopMiddleLeftFrame = Frame(settingsTopFrame, bg='#b3b3b3')
        settingsTopMiddleLeftFrame.grid(row=0,column=1,sticky='nsew', pady=5)
        settingsTopMiddleRightFrame = Frame(settingsTopFrame, bg='#b3b3b3')
        settingsTopMiddleRightFrame.grid(row=0,column=2,sticky='nsew', pady=5)
        settingsTopRightFrame = Frame(settingsTopFrame, bg='#b3b3b3')
        settingsTopRightFrame.grid(row=0,column=3,sticky='nsew', pady=5)
        
        settingsTopFrame.grid_columnconfigure(0, weight=2, uniform="settingsColSpace")
        settingsTopFrame.grid_columnconfigure(1, weight=2, uniform="settingsColSpace")
        settingsTopFrame.grid_columnconfigure(2, weight=2, uniform="settingsColSpace")
        settingsTopFrame.grid_columnconfigure(3, weight=2, uniform="settingsColSpace")
        
        #label = Label(settingsTopLeftFrame, text="Log (mousewheel to scroll):", fg='#3a3a3a', bg='#b3b3b3')
        #label.grid(row=0, column=0, sticky='nw')
        #self.logDisplay = Text(settingsTopLeftFrame, bg='#3a3a3a', fg='#ffffff', wrap=WORD, height=30, width=110, font=('TkFixedFont', 10))
        #self.logDisplay.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)
        #self.logDisplay.insert('0.0', self.logFull.get())

        settingsDefaults = {
            'Defaults (auto-saved):'     : { 'col' : 1, 'type': 'title'},
            'Mark'                       : { 'col' : 2, 'type' : 'menu', 'varName' : 'markDefault' },
            'Rarity'                     : { 'col' : 2, 'type' : 'menu', 'varName' : 'rarityDefault' },
            'Faction'                    : { 'col' : 2, 'type' : 'menu', 'varName' : 'factionDefault' },

        }
        self.createItemBlock(settingsTopMiddleLeftFrame, theme=settingsDefaults)

        settingsTheme = {
            'Theme Settings (auto-saved):'          : { 'col' : 1, 'type': 'title'},
            'UI Scale (restart app for changes)'    : { 'col' : 2, 'type' : 'scale', 'varName' : 'uiScale' },
            'blank1'                                : { 'col' : 1, 'type' : 'blank' },
            'Use experimental tooltips'             : { 'col' : 2, 'type' : 'menu', 'varName' : 'useExperimentalTooltip', 'boolean' : True },
            'blank2'                                : { 'col' : 1, 'type' : 'blank' },
            'Export default'                        : { 'col' : 2, 'type' : 'menu', 'varName' : 'exportDefault' },
            'Picker window spawn under mouse'       : { 'col' : 2, 'type' : 'menu', 'varName' : 'pickerSpawnUnderMouse', 'boolean' : True },
            'Keep template when clearing ship'      : { 'col' : 2, 'type' : 'menu', 'varName' : 'keepTemplateOnShipClear', 'boolean' : True },
            'Keep build when changing ships'        : { 'col' : 2, 'type' : 'menu', 'varName' : 'keepTemplateOnShipChange', 'boolean' : True },
            'blank3'                                : { 'col' : 1, 'type' : 'blank' },
            'Sort Options:'                         : { 'col' : 1 },
            'BOFF Sort 1st'                         : { 'col' : 2, 'type' : 'menu', 'varName' : 'boffSort' },
            'BOFF Sort 2nd'                         : { 'col' : 2, 'type' : 'menu', 'varName' : 'boffSort2' },
            'Console Sort'                          : { 'col' : 2, 'type' : 'menu', 'varName' : 'consoleSort' },

        }
        self.createItemBlock(settingsTopMiddleRightFrame, theme=settingsTheme)

        settingsMaintenance = {
            'Maintenance (auto-saved):'             : { 'col' : 1, 'type': 'title'},
            'Open Log'                              : { 'col' : 2, 'type' : 'button', 'varName' : 'openLog' },
            'blank1'                                : { 'col' : 1, 'type' : 'blank' },
            'Force out of date JSON loading'        : { 'col' : 2, 'type' : 'menu', 'varName' : 'forceJsonLoad', 'boolean' : True},
            'Disabled precache at startup'          : { 'col' : 2, 'type' : 'menu', 'varName' : 'noPreCache', 'boolean' : True},
            'Use faction-specific icons (experimental)' : { 'col' : 2, 'type' : 'menu', 'varName' : 'useFactionSpecificIcons', 'boolean' : True },
            'blank2'                                : { 'col' : 1, 'type' : 'blank' },
#            'Export SETS manual settings'           : { 'col' : 2, 'type' : 'button', 'varName' : 'exportConfigFile' },
            'Backup current caches/settings'        : { 'col' : 2, 'type' : 'button', 'varName' : 'backupCache' },
            'Clear data cache folder (Fast)'        : { 'col' : 2, 'type' : 'button', 'varName' : 'clearcache' },
            'blank3'                                : { 'col' : 1, 'type' : 'blank' },
            'Check for new faction icons (Slow)'    : { 'col' : 2, 'type' : 'button', 'varName' : 'clearfactionImages' },
            'Reset memory cache (Slow)'             : { 'col' : 2, 'type' : 'button', 'varName' : 'clearmemcache' },
            'Clear image cache (VERY SLOW!)'        : { 'col' : 2, 'type' : 'button', 'varName' : 'clearimages' },
            'Download ship images (VERY SLOW!)'     : { 'col' : 2, 'type' : 'button', 'varName' : 'predownloadShipImages' },
#            'Download gear images (VERY SLOW!)'     : { 'col' : 2, 'type' : 'button', 'varName' : 'predownloadGearImages' },
#            'Save cache binaries (TEST)'            : { 'col' : 2, 'type' : 'button', 'varName' : 'cacheSave' },


        }
        self.createItemBlock(settingsTopRightFrame, theme=settingsMaintenance)

    def persistentSet(self, choice, varName, isBoolean=False):
        if varName is None or varName == '':
            return
        self.logWrite('==={} = {} [{}]'.format(varName, choice, isBoolean))
        if isBoolean: self.persistent[varName] = 1 if choice=='Yes' else 0
        elif varName == 'uiScale': self.persistent[varName] = float(choice)
        else: self.persistent[varName] = choice
        
        self.logWriteSimple("self.persistent", varName, 2, [choice, self.persistent[varName]])
        self.stateSave()
        
        if varName == 'consoleSort':
            # Need to hook the ship frame to take sub-frame updates
            pass
        elif varName == 'boffSort' or varName == 'boffSort2': self.setupBoffFrame('space', self.backend['shipHtml'])
        elif varName == 'uiScale':
            # Need to hook rescaling
            pass
        
    def createItemBlock(self, parentFrame, theme=None, shape='col', elements=2, callback=None, row=0, col=0, padx=2, pady=2, fg='#b3b3b3', bg='#3a3a3a', sticky=None, fontDefault=None, rowWeight=None, colWeight=None):
        if theme is None or not len(theme): return
        
        i = 0 # count of keys processed
        for title in theme.keys():
            type = theme[title]['type'] if 'type' in theme[title] else ''
            tag = theme[title]['tag'] if 'tag' in theme[title] else ''
            isButton = True if type == 'button' or type == 'buttonblock' else False
            
            varName = theme[title]['varName'] if 'varName' in theme[title] else ''
            isBoolean = True if 'boolean' in theme[title] and theme[title]['boolean'] else False
            callback = theme[title]['callback'] if 'callback' in theme[title] else callback

            columns = theme[title]['col'] if 'col' in theme[title] else 1
            if 'fg' in theme[title]: fg=theme[title]['fg'] 
            if 'bg' in theme[title]: bg=theme[title]['bg']
            labelfg=theme[title]['labelfg'] if 'labelfg' in theme[title] else '#3a3a3a'
            labelbg=theme[title]['labelbg'] if 'labelbg' in theme[title] else '#b3b3b3'
            colOption = 0 if isButton else 1
            spanOption = elements if isButton else 1
            stickyOption = 'nw'
            if type == 'button': stickyOption = 'nwe'
            if type == 'buttonblock':
                stickyOption = 'nsew'
                padx = 0
                pady = 0
                rowWeight = 1
                colWeight = 1
            if sticky is not None: stickyOption = sticky
            if 'sticky' in theme[title]: stickyOption = theme[title]['sticky']
            if 'padx' in theme[title]: padx=theme[title]['padx']
            if 'pady' in theme[title]: pady=theme[title]['pady']
            if 'rowWeight' in theme[title]: rowWeight=theme[title]['rowWeight']
            if 'colWeight' in theme[title]: colWeight=theme[title]['colWeight']
            
            fontData = { 'family' : 'Helvetica', 'size' : 10, 'weight' : ''}
            fontLabel = { 'family' : 'Helvetica', 'size' : 12, 'weight' : ''}
            if type == 'title': fontLabel.update({'size': 14, 'weight': 'bold'})
            if fontDefault is not None: fontData.update(fontDefault)
            
            f = font.Font(family=fontLabel['family'], size=fontLabel['size'], weight=fontLabel['weight']) if fontLabel['weight'] else font.Font(family=fontLabel['family'], size=fontLabel['size'])
            f2 = font.Font(family=fontData['family'], size=fontData['size'], weight=fontData['weight']) if fontData['weight'] else font.Font(family=fontData['family'], size=fontData['size'])

            if columns > 1 and varName == '': continue
            #self.logWrite("==={}: {}/{}".format(title, varName, type), 2)
            rowCurrent = (i * elements) if shape == 'col' else 0
            rowCurrent += row
            colStart = (i * elements) if shape == 'row' else 0
            colStart += col
            useLabel = True if type == 'label' or type == 'blank' or type == 'title' or (not isButton and columns > 1) else False
            
            if useLabel:
                spanLabel = 1 + (elements - columns)
                stickyLabel = 'ew' if spanLabel > 1 else 'e'
                if type == 'title': stickylabel = 'n'
                label = Label(parentFrame, text='' if type == 'blank' else title, fg=labelfg, bg=labelbg, font=f)
                label.grid(row=rowCurrent, column=colStart, columnspan=spanLabel, sticky=stickyLabel, pady=pady, padx=padx)

            if type == 'menu':
                if isBoolean:  settingVar = StringVar(value='Yes' if self.persistent[varName] else 'No')
                else: settingVar = StringVar(value=self.persistent[varName] if varName in self.persistent else '')
                # Integrate these into the theme, or *assignment in if phase
                if varName == 'markDefault': settingOptions = self.marks
                elif varName == 'rarityDefault': settingOptions = ['']+self.rarities
                elif varName == 'factionDefault': settingOptions = self.factionNames
                elif varName == 'boffSort': settingOptions = self.boffSortOptions
                elif varName == 'boffSort2': settingOptions = self.boffSortOptions
                elif varName == 'consoleSort': settingOptions = self.consoleSortOptions
                elif varName == 'exportDefault': settingOptions = self.exportOptions
                elif isBoolean: settingOptions = self.yesNo

                if callback is None: optionFrame = OptionMenu(parentFrame, settingVar, *settingOptions, command=lambda choice,varName=varName,isBoolean=isBoolean:self.persistentSet(choice, varName=varName, isBoolean=isBoolean))
                else: optionFrame = OptionMenu(parentFrame, settingVar, *settingOptions, command=callback)
            elif type == 'scale':
                settingVar = DoubleVar(value=self.persistent[varName] if varName in self.persistent else 1)
                if varName == 'uiScale': self.uiScaleSetting = settingVar
                # range/resolution from theme in future
                if callback is None: optionFrame = Scale(parentFrame, from_=0.5, to=2.0, digits=2, resolution=0.1, orient='horizontal', variable=settingVar, command=lambda choice,varName=varName:self.persistentSet(choice, varName=varName))
                else: optionFrame = Scale(parentFrame, from_=0.5, to=2.0, digits=2, resolution=0.1, orient='horizontal', variable=settingVar, command=callback)
            elif isButton:
                if callback is None: optionFrame = Button(parentFrame, text=title, fg=fg, bg=bg, command=lambda varName=varName:self.settingsButtonCallback(type=varName))
                else: optionFrame = Button(parentFrame, text=title, fg=fg, bg=bg, command=callback)
            else:
                type = 'blank'

            if type != 'blank':
                if type == 'buttonblock': optionFrame.configure(bg=bg,fg=fg,font=f2)
                else: optionFrame.configure(bg=bg,fg=fg, borderwidth=0, highlightthickness=0, width=9)
                optionFrame.grid(row=rowCurrent, column=colStart+colOption, columnspan=spanOption, sticky=stickyOption, pady=pady, padx=padx)
                if rowWeight is not None: parentFrame.grid_rowconfigure(rowCurrent, weight=rowWeight)
                if colWeight is not None: parentFrame.grid_columnconfigure(colStart+colOption, weight=colWeight)
                
            i += 1

    def setupUIScaling(self,event=None):
        # Partially effect, some errors in the log formatting
        scale = 1.0
        if 'uiScale' in self.persistent:
            scale = float(self.persistent['uiScale'])
            
         # pixel correction
        factor = ( self.dpi / 96 ) * scale
        self.window.call('tk', 'scaling', factor)
        self.itemBoxX = self.itemBoxX * scale
        self.itemBoxY = self.itemBoxY * scale
        self.logminiWrite('{:>4}dpi (x{:>0.2}) '.format(self.dpi, (factor * scale)))


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
    
    def logWriteBreak(self, title, level=1):
        self.logWrite('=== {:>1} ==='.format(title.upper()), level)
    
    def logTagClean(self, tag):
        return '{}'.format(tag).strip()
        
    def logWriteSimple(self, title, body, level=1, tags=[]):
        logNote = ''
        if len(tags):
            for tag in tags:
                logNote = logNote + '[{:>1}]'.format(self.logTagClean(tag))
        self.logWrite('{:>12} {:>13}: {:>6}'.format(title, body, logNote), level)
        
    def logWriteTransaction(self, title, body, count, path, level=1, tags=[]):
        logNote = ''
        if len(tags):
            for tag in tags:
                logNote = logNote + '[{:>1}]'.format(self.logTagClean(tag))
        self.logWrite('{:>12} {:>12}: {:>6} {:>1} {:>6}'.format(title, body, str(count), path, logNote), level)
        
    def logWriteCounter(self, title, body, count, tags=[]):
        logNote = ''
        if len(tags):
            for tag in tags:
                logNote = logNote + '[{:>9}]'.format(self.logTagClean(tag))
        self.logWrite('{:>12} {:>6} count: {:>6} {:>6}'.format(title, body, str(count), logNote), 2)
        
    def logWrite(self, notice, level=0):
        # Level 0: Default, always added to short log note frame on UI
        # Higher than 0 will not be added to short log note (but will be in the full log)
        # Log levels uses are just suggestions
        # Level 1: Track interactions - network interactions, configuration actions, file transactions
        # Level 2: unconfirmed feature spam -- chatty but not intended to fully retained long term
        # Level 3+: minor detail spam -- any useful long-term diagnostic, the more spammy, the higher
        if level == 0:
            self.setFooterFrame(notice, '')
            self.logFullWrite(notice)
        if self.settings['debug'] > 0 and self.settings['debug'] >= level:
            sys.stderr.write(notice)
            sys.stderr.write('\n')
            self.logFullWrite(notice)

    def requestWindowUpdateHold(self, count=50):
        self.updateOnHeavyStep = 50
        
        if count == 0:
            self.updateOnStep = 1
            if 'updates' in self.windowUpdate:
                self.logWrite('=== hold ended @ {}'.format(str(self.windowUpdate['updates'])), 2)
        else:
            self.updateOnStep = self.updateOnHeavyStep
        self.windowUpdate['hold'] = count
        
    def requestWindowUpdate(self, type=''):
        if not 'updates' in self.windowUpdate:
            self.windowUpdate = { 'updates': 0, 'lastupdate': 0, 'hold': 0 }
            
        self.windowUpdate['updates'] += 1
        
        # runaway check
        if self.windowUpdate['updates'] % 1000 == 0:
            self.logWriteBreak("self.window.update({}): {:4}".format(type, str(self.windowUpdate['updates'])), 1)
            
        if type == 'force':
            self.window.update()
        elif self.windowUpdate['hold']:
            # a hold has been called (contains number of updates to wait)
            self.windowUpdate['hold'] -= 1
            return
        elif(type == "footerProgressBar"):
            # not certain this is any different from self.window.update()
            self.footerProgressBar.update()
        elif not type:
            self.window.update()
        else:
            return
            
        self.updateWindowSize()
        
    def resetBuildFrames(self, types=['skill', 'ground', 'space']):
        for type in types:
            self.setupInfoFrame(type)
            self.setupDescFrame(type)
    
    def setupUIFrames(self):
        defaultFont = font.nametofont('TkDefaultFont')
        defaultFont.configure(family='Helvetica', size='10')
        self.footerProgressBarUpdates = 0
        self.dpi = round(self.window.winfo_fpixels('1i'), 0)
        self.setupUIScaling()

        self.containerFrame = Frame(self.window, bg='#c59129')
        self.containerFrame.pack(fill=BOTH, expand=True)
        self.logoFrame = Frame(self.containerFrame, bg='#c59129')
        self.logoFrame.pack(fill=X)
        self.menuFrame = Frame(self.containerFrame, bg='#c59129')
        self.menuFrame.pack(fill=X, padx=15)
        self.verticalFrame = Frame(self.containerFrame, bg='#c59129', height=self.windowHeightDefault)
        self.verticalFrame.pack(fill='none', side='left')
        self.spaceBuildFrame = Frame(self.containerFrame, bg='#3a3a3a')
        self.groundBuildFrame = Frame(self.containerFrame, bg='#3a3a3a')
        self.skillTreeFrame = Frame(self.containerFrame, bg='#3a3a3a')
        self.libraryFrame = Frame(self.containerFrame, bg='#3a3a3a')
        self.settingsFrame = Frame(self.containerFrame, bg='#3a3a3a')
        
        #self.spaceBuildFrame.pack(fill=BOTH, expand=True, padx=15)
        self.focusFrameCallback(type=self.args.startuptab, init=True)

        self.setupFooterFrame()
        self.setupLogoFrame()
        self.setupMenuFrame()
        self.requestWindowUpdate() #cannot force
        #self.currentFrameUpdateTo(self.spaceBuildFrame, first=True)
        self.precachePreload(limited=(self.args.nocache or self.persistent['noPreCache']))
        
        self.setupLibraryFrame()
        self.setupSettingsFrame()
        for type in ['skill', 'ground', 'space']:
            self.setupInitialBuildFrames(type)

        if not self.templateFileLoad():
            self.setupCurrentBuildFrames()
            self.resetBuildFrames()
            
        self.updateImageLabelSize(source='setupUIFrames')
        
        #if self.args.startuptab is not None: self.focusFrameCallback(self.args.startuptab)

    def argParserSetup(self):
        parser = argparse.ArgumentParser(description='A Star Trek Online build tool')
        parser.add_argument('--configfile', type=int, help='Set configuration file (must be .JSON)')
        parser.add_argument('--configfolder', type=int, help='Set configuration folder (contains config file, state file, default library location')
        parser.add_argument('--debug', type=int, help='Set debug level (default: 0)')
        parser.add_argument('--file', type=str, help='File to import on open')
        parser.add_argument('--nofetch', type=str, help='Do not fetch new images')
        parser.add_argument('--allfetch', type=str, help='Retry images every load')
        parser.add_argument('--nocache', type=str, help='Do not precache at start')
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
                os.MakeDirs = os.makedirs(filePath)
                self.logWriteTransaction('makedirs', 'written', '', filePath, 1)
            except:
                self.logWriteTransaction('makedirs', 'failed', '', filePath, 1)
    
    def getFolderLocation(self, subfolder=None):
        filePath = self.configFolderLocation()

        if subfolder == 'images' and os.path.exists(self.settings['folder']['images']):
            # use appdir cache if it already exists /legacy
            filePath = self.settings['folder']['images']
        else:
            if subfolder is not None and subfolder in self.settings['folder']:
                filePath = os.path.join(filePath, self.settings['folder'][subfolder])
            self.makeFilenamePath(filePath)

        if not os.path.exists ( filePath ):
            filePath = ''
            if subfolder in self.settings['folder']:
                filePath = self.settings['folder'][subfolder]

        return filePath
            
    def stateFileLocation(self):
        filePath = self.configFolderLocation()
        
        if os.path.exists(filePath):
            fileName = os.path.join(filePath, self.fileStateName)
            if not os.path.exists(fileName):
                open(fileName, 'w').close()
        else:
            fileName = self.fileStateName
        
        return fileName
        
    def cacheFileLocation(self):
        filePath = self.configFolderLocation()
        
        if os.path.exists(filePath):
            fileName = os.path.join(filePath, '.cache_SETS.json')
            if not os.path.exists(fileName):
                open(fileName, 'w').close()
        else:
            fileName = '.cache_SETS.json'
        
        return fileName
        
    def templateFileLocation(self):
        filePath = self.configFolderLocation()
        
        if os.path.exists(filePath):
            fileName = os.path.join(filePath, self.settings['template'])
        else:
            fileName = self.settings['template']
        
        if os.path.exists(fileName+'.json'): fileName += '.json'
        else: fileName += '.png'
        
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

                if self.args.debug is not None:
                    self.settings['debug'] = self.args.debug
                    self.logWriteSimple('Debug', 'set by arg', 1, tags=[str(self.settings['debug'])])
                elif not 'debug' in self.settings or self.debugDefault > self.settings['debug']:
                    self.settings['debug'] = self.debugDefault
                    self.logWriteSimple('Debug', 'set from default', 1, tags=[str(self.settings['debug'])])
                else:
                    self.logWriteSimple('Debug', 'set in config', 1, tags=[str(self.settings['debug'])])
        else:
            self.logWriteTransaction('Config File', 'not found or zero size', '', configFile, 0)
            
    def stateFileLoad(self):
        # Currently JSON, but ideally changed to a user-commentable format (YAML, TOML, etc)
        configFile = self.stateFileLocation()
        if not os.path.exists(configFile):
            configFile = self.fileStateName
            
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
            
    def skillFileLoad(self):
        # Currently JSON, but ideally changed to a user-commentable format (YAML, TOML, etc)
        configFile = self.stateFileLocation()
        if not os.path.exists(configFile):
            configFile = self.fileStateName
            
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
 
    def persistentToBackend(self):
        # Nothing yet
        return
            
    def stateSave(self, quiet=False):
        configFile = self.stateFileLocation()
        if not os.path.exists(configFile):
            configFile = self.fileStateName
            
        try:
            with open(configFile, "w") as outFile:
                json.dump(self.persistent, outFile)
                self.logWriteTransaction('State File', 'saved', '', outFile.name, 5 if quiet else 1)
        except AttributeError:
            self.logWriteTransaction('State File', 'save error', '', outFile.name, 1)
            pass
            
    def cacheSave(self, quiet=False):
        configFile = self.cacheFileLocation()
        if not os.path.exists(configFile):
            configFile = self.fileStateName
            
        try:
            with open(configFile, "w") as outFile:
                json.dump(self.cache, outFile)
                self.logWriteTransaction('Cache File', 'saved', '', outFile.name, 5 if quiet else 1)
        except AttributeError:
            self.logWriteTransaction('Cache File', 'save error', '', outFile.name, 1)
            pass
            
    def templateFileLoad(self):
        configFile = self.templateFileLocation()
        if not os.path.exists(configFile): configFile = self.settings['template']
        if self.args.file is not None and os.path.exists(self.args.file): configFile = self.args.file
            
        if os.path.exists(configFile):
            self.logWriteTransaction('Template File', 'found', '', configFile, 1)
            with open(configFile, 'r') as inFile:
                return self.importByFilename(configFile)

        else:
            self.logWriteTransaction('Template File', 'not found', '', configFile, 0)
        return False
    
    def initSettings(self):
        """Initialize session settings state"""
        self.fileDebug = '.debug'
        self.debugDefault = 1 if os.path.exists(self.fileDebug) else 0
        
        # log and logmini are the bottom text, logFull provides a history
        self.log = StringVar()
        self.logmini = StringVar()
        self.logFull = StringVar()
        
        self.resetPersistent()
        self.resetSettings()

        self.logWriteBreak("logStart")
        self.logWriteSimple('CWD', '', 1, tags=[os.getcwd()])
        
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
        self.emptyImageFaction['federation'] = self.fetchOrRequestImage(self.wikiImages+"Federation_Emblem.png", "federation_emblem", self.shipImageWidth, self.shipImageHeight)
        self.emptyImageFaction['tos federation'] = self.fetchOrRequestImage(self.wikiImages+"TOS_Federation_Emblem.png", "tos_federation_emblem", self.shipImageWidth, self.shipImageHeight)
        self.emptyImageFaction['klingon'] = self.fetchOrRequestImage(self.wikiImages+"Klingon_Empire_Emblem.png", "klingon_emblem", self.shipImageWidth, self.shipImageHeight)
        self.emptyImageFaction['romulan'] = self.fetchOrRequestImage(self.wikiImages+"Romulan_Republic_Emblem.png", "romulan_emblem", self.shipImageWidth, self.shipImageHeight)
        self.emptyImageFaction['dominion'] = self.fetchOrRequestImage(self.wikiImages+"Dominion_Emblem.png", "dominion_emblem", self.shipImageWidth, self.shipImageHeight)
        
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
        
        r_species = self.fetchOrRequestHtml(self.wikihttp+"Category:Player_races", "species")
        self.speciesNames = [e.text for e in r_species.find('#mw-pages .mw-category-group .to_hasTooltip') if 'Guide' not in e.text and 'Player' not in e.text]

    
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
        self.windowUpdate = dict()
        self.requestWindowUpdateHold(0)
        self.updateWindowSize()
        self.window.iconphoto(False, PhotoImage(file='local/icon.PNG'))
        self.window.title("STO Equipment and Trait Selector")
        self.session = HTMLSession()
        self.clearBuild()
        self.resetCache()
        self.resetBackend()
        self.images = dict()
        self.setupEmptyImages()
        self.precacheDownloads()
        
        self.setupUIFrames()

    def run(self):
        self.window.mainloop()

SETS().run()
