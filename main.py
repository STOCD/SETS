from tkinter import *
from tkinter import filedialog
from tkinter import font
from requests_html import Element, HTMLSession, HTML
from PIL import Image, ImageTk, ImageGrab, PngImagePlugin
import os, requests, json, re, datetime

class SETS():
    """Main App Class"""

    #query for ship cargo table on the wiki
    ship_query = "https://sto.fandom.com/wiki/Special:CargoExport?tables=Ships&&fields=_pageName%3DPage%2Cname%3Dname%2Cimage%3Dimage%2Cfc%3Dfc%2Ctier%3Dtier%2Ctype__full%3Dtype%2Chull%3Dhull%2Chullmod%3Dhullmod%2Cshieldmod%3Dshieldmod%2Cturnrate%3Dturnrate%2Cimpulse%3Dimpulse%2Cinertia%3Dinertia%2Cpowerall%3Dpowerall%2Cpowerweapons%3Dpowerweapons%2Cpowershields%3Dpowershields%2Cpowerengines%3Dpowerengines%2Cpowerauxiliary%3Dpowerauxiliary%2Cpowerboost%3Dpowerboost%2Cboffs__full%3Dboffs%2Cfore%3Dfore%2Caft%3Daft%2Cequipcannons%3Dequipcannons%2Cdevices%3Ddevices%2Cconsolestac%3Dconsolestac%2Cconsoleseng%3Dconsoleseng%2Cconsolessci%3Dconsolessci%2Cuniconsole%3Duniconsole%2Ct5uconsole%3Dt5uconsole%2Cexperimental%3Dexperimental%2Csecdeflector%3Dsecdeflector%2Changars%3Dhangars%2Cabilities__full%3Dabilities%2Cdisplayprefix%3Ddisplayprefix%2Cdisplayclass%3Ddisplayclass%2Cdisplaytype%3Ddisplaytype%2Cfactionlede%3Dfactionlede&&order+by=`_pageName`%2C`name`%2C`image`%2C`fc`%2C`faction__full`&limit=2500&format=json"
    #query for ship equipment cargo table on the wiki
    item_query = 'https://sto.fandom.com/wiki/Special:CargoExport?tables=Infobox&&fields=_pageName%3DPage%2Cname%3Dname%2Crarity%3Drarity%2Ctype%3Dtype%2Cboundto%3Dboundto%2Cboundwhen%3Dboundwhen%2Cwho%3Dwho%2Chead1%3Dhead1%2Chead2%3Dhead2%2Chead3%3Dhead3%2Chead4%3Dhead4%2Chead5%3Dhead5%2Chead6%3Dhead6%2Chead7%3Dhead7%2Chead8%3Dhead8%2Chead9%3Dhead9%2Csubhead1%3Dsubhead1%2Csubhead2%3Dsubhead2%2Csubhead3%3Dsubhead3%2Csubhead4%3Dsubhead4%2Csubhead5%3Dsubhead5%2Csubhead6%3Dsubhead6%2Csubhead7%3Dsubhead7%2Csubhead8%3Dsubhead8%2Csubhead9%3Dsubhead9%2Ctext1%3Dtext1%2Ctext2%3Dtext2%2Ctext3%3Dtext3%2Ctext4%3Dtext4%2Ctext5%3Dtext5%2Ctext6%3Dtext6%2Ctext7%3Dtext7%2Ctext8%3Dtext8%2Ctext9%3Dtext9&&order+by=%60_pageName%60%2C%60name%60%2C%60rarity%60%2C%60type%60%2C%60boundto%60&limit=5000&format=json'
    #query for personal and reputation trait cargo table on the wiki
    trait_query = "https://sto.fandom.com/wiki/Special:CargoExport?tables=Traits&&fields=_pageName%3DPage%2Cname%3Dname%2Cchartype%3Dchartype%2Cenvironment%3Denvironment%2Ctype%3Dtype%2Cisunique%3Disunique%2Cmaster%3Dmaster%2Cdescription%3Ddescription%2Crequired__full%3Drequired%2Cpossible__full%3Dpossible&&order+by=%60_pageName%60%2C%60name%60%2C%60chartype%60%2C%60environment%60%2C%60type%60&limit=2500&format=json"

    itemBoxX = 27
    itemBoxY = 37

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
        return r.json()

    def fetchOrRequestImage(self, url, designation, width = None, height = None):
        """Request image from web or fetch from local cache"""
        cache_base = "images"
        if not os.path.exists(cache_base):
            os.makedirs(cache_base)
        extension = "jpeg" if "jpeg" in url or "jpg" in url else "png"
        filename = os.path.join(*filter(None, [cache_base, designation]))+'.'+extension
        if os.path.exists(filename):
            image = Image.open(filename)
            if(width is not None):
                image = image.resize((width,height),Image.ANTIALIAS)
            return ImageTk.PhotoImage(image)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        img_data = requests.get(url).content
        with open(filename, 'wb') as handler:
            handler.write(img_data)
        image = Image.open(filename)
        if(width is not None):
            image = image.resize((width,height),Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)

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
        return re.sub(r"(∞.*)|(Mk X.*)|(\[.*\].*)|(MK X.*)|(-S$)", '', name).strip()

    def precacheEquipment(self, keyPhrase):
        """Populate in-memory cache of ship equipment lists for faster loading"""
        if keyPhrase in self.backend['cacheEquipment']:
            return self.backend['cacheEquipment'][keyPhrase]
        phrases = [keyPhrase] + (["Ship Weapon"] if "Weapon" in keyPhrase else ["Universal Console"] if "Console" in keyPhrase else [])
        equipment = self.searchJsonTable(self.infoboxes, "type", phrases)
        self.backend['cacheEquipment'][keyPhrase] = {self.sanitizeEquipmentName(equipment[item]["name"]): equipment[item] for item in range(len(equipment))}
        if 'Hangar' in keyPhrase:
            self.backend['cacheEquipment'][keyPhrase] = {key:self.backend['cacheEquipment'][keyPhrase][key] for key in self.backend['cacheEquipment'][keyPhrase] if 'Hangar - Advanced' not in key and 'Hangar - Elite' not in key}

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
        return self.backend['modifiers']

    def fetchDoffs(self):
        if self.backend['doffs'] is not None:
            return self.backend['doffs']
        specPage = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Duty_officer#Specializations", "doffs")
        trs = specPage.find('tr')
        doffs = []
        for tr in trs:
            t = tr.text
            if '[SP]' in t or '[GR]' in t:
                doffs.append(tr)
        spaceDoffs = []
        groundDoffs = []
        for tr in doffs:
            tds = tr.find('td')
            if len(tds)<2:
                continue
            spec = tds[0].text
            for li in tds[1].find('li'):
                if '[SP]' in li.text:
                    spaceDoffs.append((spec, li.text.replace('[SP]','')))
                if '[GR]' in li.text:
                    groundDoffs.append((spec, li.text.replace('[GR]','')))
        self.backend['doffs'] = (spaceDoffs,groundDoffs)
        return self.backend['doffs']

    def setListIndex(self, list, index, value):
        print(value)
        list[index] = value

    def imageFromInfoboxName(self, name, width=None, height=None, suffix=''):
        """Translate infobox name into wiki icon link"""
        width = self.itemBoxX if width is None else width
        height = self.itemBoxY if height is None else height
        try:
            return self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/"+name.replace(' ', '_')+"_icon"+suffix+".png", name,width,height)
        except:
            return self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/Common_icon.png", "no_icon",width,height)

    def copyBackendToBuild(self, key):
        """Helper function to copy backend value to build dict"""
        self.build[key] = self.backend[key].get()

    def copyBuildToBackend(self, key):
        """Helper function to copy build value to backend dict"""
        self.backend[key].set(self.build[key])

    def clearBuild(self):
        """Initialize new build state"""
        self.build = {
            "boffs": dict(), 'activeRepTrait': [None] * 5, 'spaceRepTrait': [None] * 5,
            'personalSpaceTrait': [None] * 6, 'personalSpaceTrait2': [None] * 5,
            'starshipTrait': [None] * 6, 'uniConsoles': [None] * 5, 'tacConsoles': [None] * 5,
            'sciConsoles': [None] * 5, 'engConsoles': [None] * 5, 'devices': [None] * 5,
            'aftWeapons': [None] * 5, 'foreWeapons': [None] * 5, 'hangars': [None] * 2,
            'deflector': [None], 'engines': [None], 'warpCore': [None], 'shield': [None],
            'career': 'Tactical', 'species': 'Alien', 'ship': '', 'specPrimary': '',
            'specSecondary': '', "tier": '', 'secdef': [None], 'experimental': [None],
            'doffs': {'space': [None]*6 , 'ground': [None]*6}, "tags": dict()
        }

    def clearBackend(self):
        self.backend = {
                        "career": StringVar(self.window), "species": StringVar(self.window),
                        "specPrimary": StringVar(self.window), "specSecondary": StringVar(self.window),
                        "ship": StringVar(self.window), "tier": StringVar(self.window), "playerShipName": StringVar(self.window),
                        'cacheEquipment': dict(), "shipHtml": None, 'modifiers': None, "shipHtmlFull": None, "doffs": None
            }

    def hookBackend(self):
        self.backend['career'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('career'))
        self.backend['species'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('species'))
        self.backend['specPrimary'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('specPrimary'))
        self.backend['specSecondary'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('specSecondary'))
        self.backend['tier'].trace_add('write', lambda v,i,m:self.setupBuildFrames())
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
        pickWindow.geometry("240x400")
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
        i = 0
        for name,image in items_list:
            frame = Frame(scrollable_frame, relief='ridge', borderwidth=1)
            label = Label(frame, image=image)
            label.grid(row=0, column=0, sticky='nsew')
            label.bind('<Button-1>', lambda e,name=name,image=image,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,image,v,win))
            label.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
            label = Label(frame, text=name, wraplength=200, justify=LEFT)
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

    def shipItemLabelCallback(self, e, canvas, img, i, key, args):
        """Common callback for ship equipment labels"""
        self.precacheEquipment(args[0])
        itemVar = {"item":'',"image":self.emptyImage, "rarity": self.rarities[0], "mark": "Mk XII", "modifiers":['']}
        items_list = [ (item.replace(args[2], ''), self.imageFromInfoboxName(item)) for item in list(self.backend['cacheEquipment'][args[0]].keys())]
        item = self.pickerGui(args[1], itemVar, items_list, [self.setupSearchFrame, self.setupRarityFrame])
        if 'rarity' not in item or item['item']=='':
            item['rarity'] = self.rarities[0]
        image1 = self.imageFromInfoboxName(item['rarity'])
        canvas.itemconfig(img[0],image=item['image'])
        canvas.itemconfig(img[1],image=image1)
        canvas.bind('<Enter>', lambda e,item=item:self.setupInfoboxFrame(item, args[0]))
        self.build[key][i] = item
        self.backend['i_'+key][i] = [item['image'], image1]
        item.pop('image')

    def traitLabelCallback(self, e, canvas, img, i, key, args):
        """Common callback for all trait labels"""
        items_list=[]
        if args[2]:
            traits = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Starship_traits", "starship_traits").find('tr')[1:]
            for trait in traits:
                tds = trait.find('td')
                if tds is None or len(tds)<1:
                    continue
                cname = tds[0].text
                cimg = self.imageFromInfoboxName(cname)
                items_list.append((cname,cimg))
        else:
            traits = [self.traits[e] for e in range(len(self.traits)) if "chartype" in self.traits[e] and self.traits[e]["chartype"] == "char"]
            traits = [traits[e] for e in range(len(traits)) if "environment" in traits[e] and traits[e]["environment"] == "space"]
            traits = [traits[e] for e in range(len(traits)) if "type" in traits[e] and (traits[e]["type"] == "reputation") == args[1]]
            if args[0]:
                actives = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Category:Player_abilities", "player_abilities").links
                traits = [traits[e] for e in range(len(traits)) if "name" in traits[e] and (('/wiki/Trait:_'+traits[e]["name"]).replace(' ','_') in list(actives)) == args[1]]
            items_list = [(traits[e]["name"], self.imageFromInfoboxName(traits[e]["name"],self.itemBoxX,self.itemBoxY)) for e in range(len(traits))]
        itemVar = self.getEmptyItem()
        item = self.pickerGui("Pick trait", itemVar, items_list, [self.setupSearchFrame])
        canvas.itemconfig(img[0],image=item['image'])
        self.build[key][i] = item
        self.backend['i_'+key][i] = item['image']
        item.pop('image')

    def boffLabelCallback(self, e, canvas, img, i, key, args, idx):
        """Common callback for boff labels"""
        boffAbilities = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Bridge_officer_and_kit_abilities", "boff_abilities")
        l0 = [h2 for h2 in boffAbilities.find('h2') if ' Abilities' in h2.html]
        l1 = boffAbilities.find('h2+h3+table')
        if 'Universal' in args[0]:
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#Tactical_Abilities', first=True), Element)]
            trs = table[0].find('tr')
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#Engineering_Abilities', first=True), Element)]
            trs = trs + table[0].find('tr')
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#Science_Abilities', first=True), Element)]
            trs = trs + table[0].find('tr')
        else:
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#'+args[0].replace(' ','_')+'_Abilities', first=True), Element)]
            trs = table[0].find('tr')
        if args[1] is not None:
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#'+args[1].replace(' ','_')+'_Abilities', first=True), Element)]
            trs = trs + table[0].find('tr')
        skills = []
        for tr in trs:
            tds = tr.find('td')
            if len(tds)>0 and tds[args[2]+1].text.strip() != '':
                skills.append(tr)
        items_list = []
        for skill in skills:
            cname = skill.find('td', first=True).text.replace(':','')
            cimg = self.imageFromInfoboxName(cname,self.itemBoxX,self.itemBoxY,'_(Federation)')
            items_list.append((cname,cimg))
        itemVar = self.getEmptyItem()
        item = self.pickerGui("Pick Ability", itemVar, items_list, [self.setupSearchFrame])
        canvas.itemconfig(img,image=item['image'])
        self.build['boffs'][key][i] = item['item']
        self.backend['i_'+key+'_'+str(idx)][i] = item['image']

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
        self.shipButton.configure(text=item['item'])
        self.backend['ship'].set(item['item'])

    def importCallback(self, event):
        """Callback for import button"""
        inFilename = filedialog.askopenfilename(filetypes=[("JSON file", '*.json'),("PNG image","*.png"),("All Files","*.*")])
        if not inFilename: return
        if inFilename.endswith('.png'):
            image = Image.open(inFilename)
            self.build = json.loads(image.text['build'])
        else:
            with open(inFilename, 'r') as inFile:
                self.build = json.load(inFile)
        self.clearBackend()
        self.copyBuildToBackend('career')
        self.copyBuildToBackend('species')
        self.copyBuildToBackend('specPrimary')
        self.copyBuildToBackend('specSecondary')
        self.copyBuildToBackend('ship')
        self.copyBuildToBackend('tier')
        self.hookBackend()
        self.setupShipInfoFrame()
        self.setupTierFrame(int(self.build['tier'][1]))
        self.shipButton.configure(text=self.build['ship'])
        self.setupBuildFrames()

    def exportCallback(self, event):
        """Callback for export button"""
        try:
            with filedialog.asksaveasfile(defaultextension=".json",filetypes=[("JSON file","*.json"),("All Files","*.*")]) as outFile:
                json.dump(self.build, outFile)
        except AttributeError:
            pass

    def exportPngCallback(self, event):
        """Callback for export as png button"""
        image = ImageGrab.grab(bbox=(self.window.winfo_rootx(), self.window.winfo_rooty(), self.window.winfo_width(), self.window.winfo_height()))
        outFilename = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG image","*.png"),("All Files","*.*")])
        if not outFilename: return
        info = PngImagePlugin.PngInfo()
        info.add_text('build', json.dumps(self.build))
        image.save(outFilename, "PNG", pnginfo=info)

    def exportRedditCallback(self, event):
        redditString = "**Basic Information** | **Data** \n:--- | :--- \n*Ship Name* | {0} \n*Ship Class* | {1} \n\n\n".format(self.backend["playerShipName"].get(), self.build['ship'])
        column0 = (self.makeRedditColumn(["**Fore Weapons:**"], self.backend['shipForeWeapons']) +
                   self.makeRedditColumn(["**Aft Weapons:**"], self.backend['shipAftWeapons']) +
                   self.makeRedditColumn(["**Deflector**", "**Impulse Engines**", "**Warp Core**", "**Shields**", "**Devices**"] + (["**Secondary Deflector**"] if
                                         self.build['secdef'][0] is not None else ['&nbsp;']) + (["**Experimental Weapon**"] if self.build['experimental'][0] is not None else ['&nbsp;']),
                                         7+max(self.backend['shipDevices']-1, 1)) +
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
        redditString = redditString + "\n\n### Officers and Crew\n\n"
        column0 = []
        column1 = []
        for boff in self.build['boffs'].keys():
            column0 = column0 + self.makeRedditColumn([boff.replace("_"," ")], len(self.build['boffs'][boff]))
            column1 = column1 + self.makeRedditColumn(self.build['boffs'][boff], len(self.build['boffs'][boff]))
        redditString = redditString + self.makeRedditTable(['**Bridge Officer Information**']+column0, ['**Power**']+column1, ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n"
        column0 = list(range(1,7))
        column1 = self.makeRedditColumn([self.build['doffs']['space'][i-1]['spec'] for i in column0 if self.build['doffs']['space'][i-1] is not None], 6)
        column2 = self.makeRedditColumn([self.build['doffs']['space'][i-1]['effect'] for i in column0 if self.build['doffs']['space'][i-1] is not None], 6)
        redditString = redditString + self.makeRedditTable(['**Bridge Officer Information**']+column0, ['**Power**']+column1, ['**Notes**']+column2)
        redditString = redditString + "\n\n##    Traits\n\n"
        column0 = self.makeRedditColumn([trait['item'] for trait in self.build['personalSpaceTrait'] if trait is not None] +
                                        [trait['item'] for trait in self.build['personalSpaceTrait2'] if trait is not None], 11)
        redditString = redditString + self.makeRedditTable(['**Personal Space Traits**']+column0, ['**Description**']+[None]*len(column0), ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n"
        column0 = self.makeRedditColumn([trait['item'] for trait in self.build['spaceRepTrait'] if trait is not None], 5)
        redditString = redditString + self.makeRedditTable(['**Space Reputation Traits**']+column0, ['**Description**']+[None]*len(column0), ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n"
        column0 = self.makeRedditColumn([trait['item'] for trait in self.build['starshipTrait'] if trait is not None], 6)
        redditString = redditString + self.makeRedditTable(['**Starship Traits**']+column0, ['**Description**']+[None]*len(column0), ['**Notes**']+[None]*len(column0))
        redditString = redditString + "\n\n"
        redditWindow = Toplevel(self.window)
        redditText = Text(redditWindow)
        redditText.pack(fill=BOTH, expand=True)
        redditText.insert(END, redditString)

    def cacheInvalidateCallback(self, event):
        for filename in os.listdir("cache"):
            file_path = os.path.join("cache", filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

    def clearBuildCallback(self, event):
        """Callback for the clear build button"""
        self.clearBuild()
        self.copyBuildToBackend('career')
        self.copyBuildToBackend('species')
        self.copyBuildToBackend('specPrimary')
        self.copyBuildToBackend('specSecondary')
        self.copyBuildToBackend('ship')
        self.backend['tier'].set('')
        self.backend['shipHtml'] = None
        self.setupShipInfoFrame()
        self.shipImg = self.emptyImage
        self.shipLabel.configure(image=self.shipImg)

    def doffSpecCallback(self, om, v0, v1, row, isSpace=True):
        if self.backend['doffs'] is None:
            return
        self.build['doffs']['space' if isSpace else 'groud'][row] = {"name": "", "spec": v0.get(), "effect": ''}
        menu = om['menu']
        menu.delete(0, END)
        for power in self.backend['doffs'][0 if isSpace else 1]:
            if v0.get() in power[0]:
                menu.add_command(label=power[1], command=lambda value=power[1]: v1.set(value))

    def doffEffectCallback(self, om, v0, v1, row, isSpace=True):
        if self.backend['doffs'] is None:
            return
        self.build['doffs']['space' if isSpace else 'groud'][row]['effect'] = v1.get()

    def tagBoxCallback(self, var, text):
        self.build['tags'][text] = var.get()

    def markBoxCallback(self, itemVar, value):
        itemVar['mark'] = value

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
        markOption = OptionMenu(topbarFrame, mark, "Mk I", "Mk II", "Mk III", "Mk IIII", "Mk V", "Mk VI", "Mk VII", "Mk VIII", "Mk IX", "Mk X", "Mk XI", "Mk XII", "Mk XIII", "Mk XIV", "Mk XV")
        markOption.grid(row=0, column=0, sticky='nsw')
        rarity = StringVar(value=self.rarities[0])
        rarityOption = OptionMenu(topbarFrame, rarity, *self.rarities)
        rarityOption.grid(row=0, column=1, sticky='nsw')
        modFrame = Frame(topbarFrame, bg='gray')
        modFrame.grid(row=1, column=0, sticky='nsew')
        mark.trace_add('write', lambda v,i,m:self.markBoxCallback(value=mark.get(), itemVar=itemVar))
        rarity.trace_add('write', lambda v,i,m,frame=modFrame:self.setupModFrame(frame, rarity=rarity.get(), itemVar=itemVar))
        topbarFrame.pack()

    def labelBuildBlock(self, frame, name, row, col, cspan, key, n, callback, args=None):
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
        for i in range(n):
            image1=None
            if key in self.build and self.build[key][i] is not None:
                image0=self.imageFromInfoboxName(self.build[key][i]['item'])
                if 'rarity' in self.build[key][i]:
                    image1=self.imageFromInfoboxName(self.build[key][i]['rarity'])
                self.backend['i_'+key][i] = [image0, image1]
            else:
                image0=image1=self.emptyImage
            canvas = Canvas(iFrame, highlightthickness=0, borderwidth=0, width=25, height=35, bg='gray')
            canvas.grid(row=row, column=i+1, sticky='nse', padx=2, pady=2)
            img0 = canvas.create_image(0,0, anchor="nw",image=image0)
            img1 = None if image1 is None else canvas.create_image(0,0, anchor="nw",image=image1)
            if (args is not None):
                canvas.bind('<Button-1>', lambda e,canvas=canvas,img=(img0, img1),i=i,args=args,key=key,callback=callback:callback(e,canvas,img,i,key,args))

    def setupShipBuildFrame(self, ship):
        """Set up UI frame containing ship equipment"""
        self.clearFrame(self.shipEquipmentFrame)
        self.backend['shipForeWeapons'] = int(ship["fore"])
        self.backend['shipAftWeapons'] = int(ship["aft"])
        self.backend['shipDevices'] = int(ship["devices"])
        self.backend['shipTacConsoles'] = int(ship["consolestac"])
        self.backend['shipEngConsoles'] = int(ship["consoleseng"])
        self.backend['shipSciConsoles'] = int(ship["consolessci"])
        self.backend['shipUniConsoles'] = 1 if '-Miracle Worker' in ship["boffs"][0] else 0
        self.backend['shipHangars'] = 0 if ship["hangars"] == '' else int(ship["hangars"])
        if '-X' in self.backend['tier'].get():
            self.backend['shipUniConsoles'] = self.backend['shipUniConsoles'] + 1
            self.backend['shipDevices'] = self.backend['shipDevices'] + 1
        if 'T5-' in self.backend['tier'].get():
            t5console = ship["t5uconsole"]
            key = 'shipTacConsoles' if 'tac' in t5console else 'shipEngConsoles' if 'eng' in t5console else 'shipSciConsoles'
            self.backend[key] = self.backend[key] + 1
        self.labelBuildBlock(self.shipEquipmentFrame, "Fore Weapons", 0, 0, 1, 'foreWeapons', self.backend['shipForeWeapons'], self.shipItemLabelCallback, ["Ship Fore Weapon", "Pick Fore Weapon", ""])
        if ship["secdeflector"] == 1:
            self.labelBuildBlock(self.shipEquipmentFrame, "Secondary", 1, 1, 1, 'secdef', 1, self.shipItemLabelCallback, ["Ship Secondary Deflector", "Pick Secdef", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Deflector", 0, 1, 1, 'deflector', 1, self.shipItemLabelCallback, ["Ship Deflector Dish", "Pick Deflector", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Engines", 2, 1, 1, 'engines', 1, self.shipItemLabelCallback, ["Impulse Engine", "Pick Engine", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Core", 3, 1, 1, 'warpCore', 1, self.shipItemLabelCallback, ["Singularity Core" if "Warbird" in self.build['ship'] or "Aves" in self.build['ship'] else "Warp Core", "Pick Core", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Shield", 4, 1, 1, 'shield' , 1, self.shipItemLabelCallback, ["Ship Shields", "Pick Shield", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Aft Weapons", 1, 0, 1, 'aftWeapons', self.backend['shipAftWeapons'], self.shipItemLabelCallback, ["Ship Aft Weapon", "Pick aft weapon", ""])
        if ship["experimental"] == 1:
            self.labelBuildBlock(self.shipEquipmentFrame, "Experimental", 2, 0, 1, 'experimental', 1, self.shipItemLabelCallback, ["Experimental", "Pick Experimental Weapon", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Devices", 3, 0, 1, 'devices', self.backend['shipDevices'], self.shipItemLabelCallback, ["Ship Device", "Pick Device", ""])
        if self.backend['shipUniConsoles'] > 0:
            self.labelBuildBlock(self.shipEquipmentFrame, "Uni Consoles", 3, 2, 1, 'uniConsoles', self.backend['shipUniConsoles'], self.shipItemLabelCallback, ["Console", "Pick Uni Console", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Sci Consoles", 2, 2, 1, 'sciConsoles', self.backend['shipSciConsoles'], self.shipItemLabelCallback, ["Ship Science Console", "Pick Sci Console", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Eng Consoles", 1, 2, 1, 'engConsoles', self.backend['shipEngConsoles'], self.shipItemLabelCallback, ["Ship Engineering Console", "Pick Eng Console", ""])
        self.labelBuildBlock(self.shipEquipmentFrame, "Tac Consoles", 0, 2, 1, 'tacConsoles', self.backend['shipTacConsoles'], self.shipItemLabelCallback, ["Ship Tactical Console", "Pick Tac Console", ""])
        if self.backend['shipHangars'] > 0:
            self.labelBuildBlock(self.shipEquipmentFrame, "Hangars", 4, 0, 1, 'hangars', self.backend['shipHangars'], self.shipItemLabelCallback, ["Hangar Bay", "Pick Hangar Pet", ""])

    def setupTraitFrame(self):
        """Set up UI frame containing traits"""
        self.clearFrame(self.shipTraitFrame)
        self.labelBuildBlock(self.shipTraitFrame, "Personal", 0, 0, 1, 'personalSpaceTrait', 6 if ('Alien' in self.backend['species'].get()) else 5, self.traitLabelCallback, [False, False, False])
        self.labelBuildBlock(self.shipTraitFrame, "Personal", 1, 0, 1, 'personalSpaceTrait2', 5, self.traitLabelCallback, [False, False, False])
        self.labelBuildBlock(self.shipTraitFrame, "Starship", 2, 0, 1, 'starshipTrait', 5+(1 if '-X' in self.backend['tier'].get() else 0), self.traitLabelCallback, [False, False, True])
        self.labelBuildBlock(self.shipTraitFrame, "SpaceRep", 3, 0, 1, 'spaceRepTrait', 5, self.traitLabelCallback, [True, False, False])
        self.labelBuildBlock(self.shipTraitFrame, "Active", 4, 0, 1, 'activeRepTrait', 5, self.traitLabelCallback, [True, True, False])

    def setupBoffFrame(self, ship):
        """Set up UI frame containing boff skills"""
        self.clearFrame(self.shipBoffFrame)
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
            boffSan = boff.replace(' ','_')
            self.backend['i_'+boffSan+'_'+str(idx)] = [None] * rank
            bSubFrame0 = Frame(bFrame, bg='#3a3a3a')
            bSubFrame0.pack(fill=BOTH)
            v = StringVar(self.window, value=boff)
            if spec == 'Universal':
                v.set(boff.replace('Universal', 'Tactical'))
                specLabel0 = OptionMenu(bSubFrame0, v, boff.replace('Universal', 'Tactical'), boff.replace('Universal', 'Engineering'), boff.replace('Universal', 'Science'))
                specLabel0.configure(bg='#3a3a3a', fg='#ffffff', font=('Helvetica', 10))
                specLabel0.pack(side='left')
            else:
                specLabel0 = Label(bSubFrame0, text=(spec if sspec is None else spec+' / '+sspec), bg='#3a3a3a', fg='#ffffff', font=('Helvetica', 10))
                specLabel0.pack(side='left')
            bSubFrame1 = Frame(bFrame, bg='#3a3a3a')
            bSubFrame1.pack(fill=BOTH)
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
                canvas.bind('<Button-1>', lambda e,canvas=canvas,img=img0,i=i,spec=spec,sspec=sspec,key=boffSan,idx=idx,v=v,callback=self.boffLabelCallback:callback(e,canvas,img,i,key,[self.boffTitleToSpec(v.get()), sspec, i], idx))
            idx = idx + 1

    def setupBuildFrames(self):
        """Set up all relevant build frames"""
        self.build['tier'] = self.backend['tier'].get()
        if self.backend['shipHtml'] is not None:
            self.setupShipBuildFrame(self.backend['shipHtml'])
            self.setupBoffFrame(self.backend['shipHtml'])
            self.setupDoffFrame()
            self.setupTraitFrame()
            self.setupInfoboxFrame(self.getEmptyItem(),'')

    def setupModFrame(self, frame, rarity, itemVar):
        """Set up modifier frame in equipment picker"""
        self.clearFrame(frame)
        n = self.rarities.index(rarity)
        itemVar['rarity'] = rarity
        itemVar['modifiers'] = ['']*n
        mods = self.fetchModifiers()
        for i in range(n):
            v = StringVar()
            v.trace_add('write', lambda v0,v1,v2,i=i,itemVar=itemVar,v=v:self.setListIndex(itemVar['modifiers'],i,v.get()))
            OptionMenu(frame, v, *mods).grid(row=0, column=i, sticky='n')

    def setupInfoboxFrame(self, item, key):
        """Set up infobox frame with given item"""
        self.clearFrame(self.shipInfoboxFrame)
        Label(self.shipInfoboxFrame, text="STATS & OTHER INFO").pack(fill="both", expand=True)
        text = Text(self.shipInfoboxFrame, height=25, width=30, font=('Helvetica', 10), bg='#3a3a3a', fg='#ffffff')
        text.pack(fill="both", expand=True, padx=2, pady=2)
        if item['item'] == '':
            return
        html = self.backend['cacheEquipment'][key][item['item']]
        text.insert(END, item['item']+' '+item['mark']+' '+('' if item['modifiers'][0] is None else ''.join(item['modifiers']))+'\n')
        text.insert(END, item['rarity']+' '+ html["type"]+'\n')
        for i in range(1,9):
            for header in ["head", "subhead", "text"]:
                t = html[header+str(i)].replace(":",'').strip()
                if t.strip() != '':
                    text.insert(END, t+'\n')
        text.configure(state=DISABLED)

    def setupDoffFrame(self):
        self.clearFrame(self.shipDoffFrame)
        mainFrame = Frame(self.shipDoffFrame, bg='#3a3a3a')
        mainFrame.pack(side='left')
        spaceDoffFrame = Frame(mainFrame, bg='#3a3a3a')
        spaceDoffFrame.pack(side='left', fill=BOTH, expand=True)
        groundDoffFrame = Frame(mainFrame, bg='#3a3a3a')
        groundDoffFrame.pack(side='left', fill=BOTH, expand=True)
        Label(spaceDoffFrame, text="SPACE DUTY OFFICERS", bg='#3a3a3a', fg='#ffffff').grid(row=0, column=0,columnspan=3, sticky='nsew')
        space,ground = self.fetchDoffs()
        for i in range(6):
            v0 = StringVar(self.window)
            v1 = StringVar(self.window)
            v2 = StringVar(self.window)
            m = OptionMenu(spaceDoffFrame, v0, 'NAME', *['A','B','C'])
            m.grid(row=i+1, column=0, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0, state=DISABLED)
            m = OptionMenu(spaceDoffFrame, v1, 'SPECIALIZATION', *list(set([doff[0] for doff in space])))
            m.grid(row=i+1, column=1, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0)
            m = OptionMenu(spaceDoffFrame, v2, 'EFFECT\nOTHER', '')
            m.grid(row=i+1, column=2, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0, width=20)
            if self.build['doffs']['space'][i] is not None:
                v0.set(self.build['doffs']['space'][i]['name'])
                v1.set(self.build['doffs']['space'][i]['spec'])
                v2.set(self.build['doffs']['space'][i]['effect'])
            v1.trace_add("write", lambda v,i,m,menu=m,v0=v1,v1=v2,row=i:self.doffSpecCallback(menu, v0,v1, row, True))
            v2.trace_add("write", lambda v,i,m,menu=m,v0=v1,v1=v2,row=i:self.doffEffectCallback(menu, v0,v1, row, True))
        Label(groundDoffFrame, text="GROUND DUTY OFFICERS", bg='#3a3a3a', fg='#ffffff').grid(row=0, column=0,columnspan=3, sticky='nsew')
        for i in range(6):
            v0 = StringVar(self.window)
            v1 = StringVar(self.window)
            v2 = StringVar(self.window)
            m = OptionMenu(groundDoffFrame, v0, 'NAME', *['A','B','C'])
            m.grid(row=i+1, column=0, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0, state=DISABLED)
            m = OptionMenu(groundDoffFrame, v1, 'SPECIALIZATION', *list(set([doff[0] for doff in ground])))
            m.grid(row=i+1, column=1, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0)
            m = OptionMenu(groundDoffFrame, v2, 'EFFECT\nOTHER', '')
            m.grid(row=i+1, column=2, sticky='nsew')
            m.configure(bg='#b3b3b3',fg='#ffffff', borderwidth=0, highlightthickness=0, width=20)
            if self.build['doffs']['ground'][i] is not None:
                v0.set(self.build['doffs']['space'][i]['name'])
                v1.set(self.build['doffs']['space'][i]['spec'])
                v2.set(self.build['doffs']['space'][i]['effect'])
            v1.trace_add("write", lambda v,i,m,menu=m,v0=v1,v1=v2,row=i:self.doffSpecCallback(menu, v0,v1,row, False))
            v2.trace_add("write", lambda v,i,m,menu=m,v0=v1,v1=v2,row=i:self.doffEffectCallback(menu, v0,v1, row, False))

    def setupLogoFrame(self):
        self.clearFrame(self.logoFrame)
        self.images['logoImage'] = self.loadLocalImage("logo_bar.png", self.window.winfo_screenwidth(), int(self.window.winfo_screenwidth()/1920 * 134))
        Label(self.logoFrame, image=self.images['logoImage'], borderwidth=0, highlightthickness=0).pack()

    def setupMenuFrame(self):
        self.clearFrame(self.menuFrame)
        f = font.Font(family='Helvetica', size=12, weight='bold')
        buttonSpace = Button(self.menuFrame, text="SPACE", bg='#6b6b6b', fg='#ffffff', font=f)
        buttonSpace.grid(row=0, column=0, sticky='nsew')
        buttonGround = Button(self.menuFrame, text="GROUND", bg='#6b6b6b', fg='#ffffff', font=f)
        buttonGround.grid(row=0, column=1, sticky='nsew')
        buttonSkill = Button(self.menuFrame, text="SKILL TREE", bg='#6b6b6b', fg='#ffffff', font=f)
        buttonSkill.grid(row=0, column=2, sticky='nsew')
        buttonLibrary = Button(self.menuFrame, text="LIBRARY", bg='#6b6b6b', fg='#ffffff', font=f)
        buttonLibrary.grid(row=0, column=3, sticky='nsew')
        buttonSettings = Button(self.menuFrame, text="SETTINGS", bg='#6b6b6b', fg='#ffffff', font=f)
        buttonSettings.grid(row=0, column=4, sticky='nsew')
        for i in range(5):
            self.menuFrame.grid_columnconfigure(i, weight=1, uniform="mainCol")

    def setupTierFrame(self, tier):
        Label(self.shipTierFrame, text="Tier:", fg='#3a3a3a', bg='#b3b3b3').grid(row=0, column=0, sticky='nsew')
        m = OptionMenu(self.shipTierFrame, self.backend["tier"], *self.getTierOptions(tier))
        m.grid(column=1, row=0, sticky='nsew', pady=5)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
        self.backend['shipHtml'] = self.getShipFromName(self.r_ships, self.build['ship'])
        try:
            ship_image = self.backend['shipHtml']["image"]
            self.shipImg = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/"+ship_image.replace(' ','_'), self.build['ship'], 260, 146)
            self.shipLabel.configure(image=self.shipImg)
        except:
            self.shipImg = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/Federation_Emblem.png", "federation_emblem", 260, 146)
            self.shipLabel.configure(image=self.shipImg)

    def setupShipInfoFrame(self):
        self.clearFrame(self.shipInfoFrame)
        playerShipNameFrame = Frame(self.shipInfoFrame, bg='#b3b3b3')
        playerShipNameFrame.pack(fill=BOTH, expand=True)
        Label(playerShipNameFrame, text="SHIP NAME:", fg='#3a3a3a', bg='#b3b3b3').grid(row=0, column=0, sticky='nsew')
        Entry(playerShipNameFrame, textvariable=self.backend['playerShipName'], fg='#3a3a3a', bg='#b3b3b3').grid(row=0, column=1, sticky='nsew')
        playerShipNameFrame.grid_columnconfigure(1, weight=1)
        exportImportFrame = Frame(self.shipInfoFrame)
        exportImportFrame.pack(fill=BOTH, expand=True)
        buttonExport = Button(exportImportFrame, text='Export', bg='#3a3a3a',fg='#b3b3b3')
        buttonExport.pack(side='left', fill=BOTH, expand=True)
        buttonExport.bind('<Button-1>', self.exportCallback)
        buttonImport = Button(exportImportFrame, text='Import', bg='#3a3a3a',fg='#b3b3b3')
        buttonImport.pack(side='left', fill=BOTH, expand=True)
        buttonImport.bind('<Button-1>', self.importCallback)
        buttonClear = Button(exportImportFrame, text='Clear', bg='#3a3a3a',fg='#b3b3b3')
        buttonClear.pack(side='left', fill=BOTH, expand=True)
        buttonClear.bind('<Button-1>', self.clearBuildCallback)
        buttonExportPng = Button(exportImportFrame, text='Export .png', bg='#3a3a3a',fg='#b3b3b3')
        buttonExportPng.pack(side='left', fill=BOTH, expand=True)
        buttonExportPng.bind('<Button-1>', self.exportPngCallback)
        buttonExportReddit = Button(exportImportFrame, text='Export reddit', bg='#3a3a3a',fg='#b3b3b3')
        buttonExportReddit.pack(side='left', fill=BOTH, expand=True)
        buttonExportReddit.bind('<Button-1>', self.exportRedditCallback)
        buttonInvalidateCache = Button(exportImportFrame, text='Invalidate cache', bg='#3a3a3a',fg='#b3b3b3')
        buttonInvalidateCache.pack(side='left', fill=BOTH, expand=True)
        buttonInvalidateCache.bind('<Button-1>', self.cacheInvalidateCallback)
        shipLabelFrame = Frame(self.shipInfoFrame, bg='#b3b3b3')
        shipLabelFrame.pack(fill=BOTH, expand=True)
        self.shipLabel = Label(shipLabelFrame, fg='#3a3a3a', bg='#b3b3b3')
        self.shipLabel.pack(fill=BOTH, expand=True)
        shipNameFrame = Frame(self.shipInfoFrame, bg='#b3b3b3')
        shipNameFrame.pack(fill=BOTH, expand=True, padx=2)
        Label(shipNameFrame, text="Ship: ", fg='#3a3a3a', bg='#b3b3b3').grid(column=0, row = 0, sticky='nwse')
        self.shipButton = Button(shipNameFrame, text="<Pick>", command=self.shipPickButtonCallback, bg='#b3b3b3')
        self.shipButton.grid(column=1, row=0, sticky='nwse')
        shipNameFrame.grid_columnconfigure(1, weight=1)
        self.shipTierFrame = Frame(self.shipInfoFrame, bg='#b3b3b3')
        self.shipTierFrame.pack(fill=BOTH, expand=True, padx=2)
        tagsAndCharFrame = Frame(self.shipInfoFrame, bg='#b3b3b3')
        tagsAndCharFrame.pack(fill=BOTH, expand=True, padx=2)
        tagsAndCharFrame.grid_columnconfigure(0, weight=1)
        tagsAndCharFrame.grid_columnconfigure(1, weight=1)
        buildTagFrame = Frame(tagsAndCharFrame, bg='#b3b3b3')
        buildTagFrame.grid(row=0, column=0, sticky='nsew')
        charInfoFrame = Frame(tagsAndCharFrame, bg='#b3b3b3')
        charInfoFrame.grid(row=0, column=1, sticky='nsew')
        Label(buildTagFrame, text="BUILD TAGS", fg='#3a3a3a', bg='#b3b3b3').pack(fill=BOTH, expand=True)
        for tag in ["DEW", "KINETIC", "EPG", "DEWSCI", "THEME"]:
            tagFrame = Frame(buildTagFrame, bg='#b3b3b3')
            tagFrame.pack(fill=BOTH, expand=True)
            v = IntVar(self.window, value=(1 if tag in self.build['tags'] and self.build['tags'][tag] == 1 else 0))
            Checkbutton(tagFrame, variable=v, fg='#3a3a3a', bg='#b3b3b3').grid(row=0,column=0)
            v.trace_add("write", lambda v,i,m,var=v,text=tag:self.tagBoxCallback(var,text))
            Label(tagFrame, text=tag, fg='#3a3a3a', bg='#b3b3b3').grid(row=0,column=1)
        Label(charInfoFrame, text="CAPTAIN CAREER", fg='#3a3a3a', bg='#b3b3b3').pack(fill=BOTH, expand=True)
        m = OptionMenu(charInfoFrame, self.backend["career"], "", "Tactical", "Engineering", "Science")
        m.pack(fill=BOTH, expand=True)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
        Label(charInfoFrame, text="SPECIES", fg='#3a3a3a', bg='#b3b3b3').pack(fill=BOTH, expand=True)
        m = OptionMenu(charInfoFrame, self.backend["species"], *self.speciesNames)
        m.pack(fill=BOTH, expand=True)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
        Label(charInfoFrame, text="PRIMARY SPEC", fg='#3a3a3a', bg='#b3b3b3').pack(fill=BOTH, expand=True)
        m = OptionMenu(charInfoFrame, self.backend["specPrimary"], '', *self.specNames)
        m.pack(fill=BOTH, expand=True)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)
        Label(charInfoFrame, text="SECONDARY SPEC", fg='#3a3a3a', bg='#b3b3b3').pack(fill=BOTH, expand=True)
        m = OptionMenu(charInfoFrame, self.backend["specSecondary"], '', *self.specNames)
        m.pack(fill=BOTH, expand=True, pady=2)
        m.configure(bg='#3a3a3a',fg='#b3b3b3', borderwidth=0, highlightthickness=0)


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
        self.spaceBuildFrame.pack(fill=BOTH, expand=True, padx=15)

        self.shipInfoFrame = Frame(self.spaceBuildFrame, bg='#b3b3b3')
        self.shipInfoFrame.grid(row=0,column=0,sticky='nsew',rowspan=2, pady=5)
        self.shipMiddleFrame = Frame(self.spaceBuildFrame, bg='#3a3a3a')
        self.shipMiddleFrame.grid(row=0,column=1,columnspan=3,sticky='nsew', pady=5)
        self.shipMiddleFrameUpper = Frame(self.shipMiddleFrame, bg='#3a3a3a')
        self.shipMiddleFrameUpper.grid(row=0,column=1,columnspan=3,sticky='nsew')
        self.shipEquipmentFrame = Frame(self.shipMiddleFrameUpper, bg='#3a3a3a')
        self.shipEquipmentFrame.pack(side='left', fill=BOTH, expand=True, padx=20)
        self.shipBoffFrame = Frame(self.shipMiddleFrameUpper, bg='#3a3a3a')
        self.shipBoffFrame.pack(side='left', fill=BOTH, expand=True)
        self.shipTraitFrame = Frame(self.shipMiddleFrameUpper, bg='#3a3a3a')
        self.shipTraitFrame.pack(side='left', fill=BOTH, expand=True)
        self.shipMiddleFrameLower = Frame(self.shipMiddleFrame, bg='#3a3a3a')
        self.shipMiddleFrameLower.grid(row=1,column=1,columnspan=3,sticky='nsew')
        self.shipDoffFrame = Frame(self.shipMiddleFrameLower, bg='#3a3a3a')
        self.shipDoffFrame.pack(fill=BOTH, expand=True, padx=20)
        self.shipInfoboxFrame = Frame(self.spaceBuildFrame, bg='#b3b3b3')
        self.shipInfoboxFrame.grid(row=0,column=4,rowspan=2,sticky='nsew', pady=5)
        for i in range(5):
            self.spaceBuildFrame.grid_columnconfigure(i, weight=1, uniform="mainCol")
        self.shipMiddleFrame.grid_columnconfigure(0, weight=1, uniform="secCol")
        self.shipMiddleFrame.grid_columnconfigure(1, weight=1, uniform="secCol")
        self.shipMiddleFrame.grid_columnconfigure(2, weight=1, uniform="secCol")

        self.setupLogoFrame()
        self.setupMenuFrame()
        self.setupShipInfoFrame()

    def __init__(self) -> None:
        """Main setup function"""
        self.window = Tk()
        # self.window.geometry('1280x650')
        self.window.title("STO Equipment and Trait Selector")
        self.session = HTMLSession()
        self.clearBuild()
        self.clearBackend()
        self.hookBackend()
        self.images = dict()
        self.rarities = ["Common", "Uncommon", "Rare", "Very rare", "Ultra rare", "Epic"]
        self.emptyImage = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/Common_icon.png", "no_icon",self.itemBoxX,self.itemBoxY)
        self.infoboxes = self.fetchOrRequestJson(SETS.item_query, "infoboxes")
        self.traits = self.fetchOrRequestJson(SETS.trait_query, "traits")
        r_species = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Category:Player_races", "species")
        self.speciesNames = [e.text for e in r_species.find('#mw-pages .mw-category-group .to_hasTooltip') if 'Guide' not in e.text and 'Player' not in e.text]
        r_specs = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Category:Captain_specializations", "specs")
        self.specNames = [e.text.replace(' (specialization)', '').replace(' Officer', '').replace(' Operative', '') for e in r_specs.find('#mw-pages .mw-category-group .to_hasTooltip') if '(specialization)' in e.text]
        self.r_ships = self.fetchOrRequestJson(SETS.ship_query, "ship_list")
        self.shipNames = [e["Page"] for e in self.r_ships]


        self.setupUIFrames()

    def run(self):
        self.window.mainloop()

SETS().run()
