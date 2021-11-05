from tkinter import *
from tkinter import filedialog
from requests_html import Element, HTMLSession, HTML
from PIL import Image, ImageTk, ImageGrab, PngImagePlugin
import os, requests, json, re

class SETS():
    """Main App Class"""

    #query for ship cargo table on the wiki
    ship_query = "https://sto.fandom.com/wiki/Special:CargoQuery?limit=2500&tables=Ships&fields=_pageName%3DPage%2Cname%3Dname%2Cimage%3Dimage%2Cfc%3Dfc%2Cfaction__full%3Dfaction%2Cfacsort%3Dfacsort%2Crank%3Drank%2Cranklevel%3Dranklevel%2Ctier%3Dtier%2Cupgradecost%3Dupgradecost%2Ctype__full%3Dtype%2Chull%3Dhull%2Chullmod%3Dhullmod%2Cshieldmod%3Dshieldmod%2Cturnrate%3Dturnrate%2Cimpulse%3Dimpulse%2Cinertia%3Dinertia%2Cpowerall%3Dpowerall%2Cpowerweapons%3Dpowerweapons%2Cpowershields%3Dpowershields%2Cpowerengines%3Dpowerengines%2Cpowerauxiliary%3Dpowerauxiliary%2Cpowerboost%3Dpowerboost%2Cboffs__full%3Dboffs%2Cfore%3Dfore%2Caft%3Daft%2Cequipcannons%3Dequipcannons%2Cdevices%3Ddevices%2Cconsolestac%3Dconsolestac%2Cconsoleseng%3Dconsoleseng%2Cconsolessci%3Dconsolessci%2Cuniconsole%3Duniconsole%2Ct5uconsole%3Dt5uconsole%2Changars%3Dhangars%2Ccost__full%3Dcost%2Cabilities__full%3Dabilities%2Cadmiraltyeng__full%3Dadmiraltyeng%2Cadmiraltytac__full%3Dadmiraltytac%2Cadmiraltysci__full%3Dadmiraltysci%2Cdisplayprefix%3Ddisplayprefix%2Cdisplayclass%3Ddisplayclass%2Cdisplaytype%3Ddisplaytype%2Cfactionlede%3Dfactionlede&max_display_chars=300"
    #query for ship equipment cargo table on the wiki
    item_query = 'https://sto.fandom.com/wiki/Special:CargoQuery?limit=5000&offset=0&tables=Infobox&fields=_pageName%3DPage%2Cname%3Dname%2Crarity%3Drarity%2Ctype%3Dtype%2Cboundto%3Dboundto%2Cboundwhen%3Dboundwhen%2Cwho%3Dwho%2Chead1%3Dhead1%2Chead2%3Dhead2%2Chead3%3Dhead3%2Chead4%3Dhead4%2Chead5%3Dhead5%2Chead6%3Dhead6%2Chead7%3Dhead7%2Chead8%3Dhead8%2Chead9%3Dhead9%2Csubhead1%3Dsubhead1%2Csubhead2%3Dsubhead2%2Csubhead3%3Dsubhead3%2Csubhead4%3Dsubhead4%2Csubhead5%3Dsubhead5%2Csubhead6%3Dsubhead6%2Csubhead7%3Dsubhead7%2Csubhead8%3Dsubhead8%2Csubhead9%3Dsubhead9%2Ctext1%3Dtext1%2Ctext2%3Dtext2%2Ctext3%3Dtext3%2Ctext4%3Dtext4%2Ctext5%3Dtext5%2Ctext6%3Dtext6%2Ctext7%3Dtext7%2Ctext8%3Dtext8%2Ctext9%3Dtext9&max_display_chars=300'
    #query for personal and reputation trait cargo table on the wiki
    trait_query = "https://sto.fandom.com/wiki/Special:CargoQuery?limit=2500&offset=0&tables=Traits&fields=_pageName%3DPage%2Cname%3Dname%2Cchartype%3Dchartype%2Cenvironment%3Denvironment%2Ctype%3Dtype%2Cisunique%3Disunique%2Cmaster%3Dmaster%2Cdescription%3Ddescription%2Crequired__full%3Drequired%2Cpossible__full%3Dpossible&max_display_chars=300"
    
    itemBoxX = 27
    itemBoxY = 37

    def fetchOrRequestHtml(self, url, designation):
        """Request HTML document from web or fetch from local cache"""
        cache_base = "cache"
        if not os.path.exists(cache_base):
            os.makedirs(cache_base)
        filename = os.path.join(*filter(None, [cache_base, designation]))+".html"
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as html_file:
                s = html_file.read()
                return HTML(html=s, url = 'https://sto.fandom.com/')
        r = self.session.get(url)
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))
        with open(filename, 'w', encoding="utf-8") as html_file:
            html_file.write(r.text)
        return r.html

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

    def getShipFromName(self, requestHtml, shipName):
        """Find cargo table entry for given ship name"""
        trs = requestHtml.find('tr')
        ship_list = [e for e in trs if isinstance(e.find('td.field_name', first=True), Element) and shipName in e.find('td.field_name', first=True).text]
        return [] if isinstance(ship_list, int) else ship_list[0]
    
    def shipItemLabelCallback(self, e, canvas, img0, img1, i, args, key):
        """Common callback for ship equipment labels"""
        item = self.pickEquipment(*args)
        image0 = self.imageFromInfoboxName(item['item'], self.itemBoxX, self.itemBoxY)
        image1 = self.imageFromInfoboxName(item['rarity'],self.itemBoxX,self.itemBoxY)
        canvas.itemconfig(img0,image=image0)
        canvas.itemconfig(img1,image=image1)
        self.build[key][i] = item
        self.backend['i_'+key][i] = [image0, image1]
            
    def shipBuildBlock(self, name, row, key, n, args=None):
        """Set up n-element line of ship equipment"""
        self.backend['i_'+key] = [None] * n
        label =  Label(self.shipBuildFrame, text=name)
        label.grid(row=row, column=0, sticky='nsew', padx=5, pady=2)
        for i in range(n):
            if key in self.build and self.build[key][i] is not None:
                image0=self.imageFromInfoboxName(self.build[key][i]['item'],self.itemBoxX,self.itemBoxY)
                image1=self.imageFromInfoboxName(self.build[key][i]['rarity'],self.itemBoxX,self.itemBoxY)
                self.backend['i_'+key][i] = [image0, image1]
            else:
                image0=image1=self.emptyImage
            canvas = Canvas(self.shipBuildFrame, relief='raised', borderwidth=1, width=27, height=37)
            canvas.grid(row=row, column=i+1, sticky='nse', padx=2, pady=2)
            img0 = canvas.create_image(0,0, anchor="nw",image=image0)
            img1 = canvas.create_image(0,0, anchor="nw",image=image1)
            if (args is not None):
                canvas.bind('<Button-1>', lambda e,canvas=canvas,img0=img0,img1=img1,i=i,args=args,key=key:self.shipItemLabelCallback(e,canvas,img0,img1,i,args,key))

    def shipBuildFrameSetup(self, ship):
        """Set up UI frame containing ship equipment"""
        for widget in self.shipBuildFrame.winfo_children():
            widget.destroy()
        self.backend['shipForeWeapons'] = int(ship.find('td.field_fore', first=True).text)
        self.backend['shipAftWeapons'] = int(ship.find('td.field_aft', first=True).text)
        self.backend['shipDevices'] = int(ship.find('td.field_devices', first=True).text)
        self.backend['shipTacConsoles'] = int(ship.find('td.field_consolestac', first=True).text)
        self.backend['shipEngConsoles'] = int(ship.find('td.field_consoleseng', first=True).text)
        self.backend['shipSciConsoles'] = int(ship.find('td.field_consolessci', first=True).text)
        self.backend['shipUniConsoles'] = 1 if '-Miracle Worker' in ship.find('td.field_boffs', first=True).text else 0
        self.backend['shipHangars'] = 0 if ship.find('td.field_hangars', first=True).text == '' else int(ship.find('td.field_hangars', first=True).text)
        if '-X' in self.backend['tier'].get():
            self.backend['shipUniConsoles'] = self.backend['shipUniConsoles'] + 1
            self.backend['shipDevices'] = self.backend['shipDevices'] + 1
        if 'T5-' in self.backend['tier'].get():
            t5console = ship.find('td.field_t5uconsole', first=True).text
            key = 'shipTacConsoles' if 'tac' in t5console else 'shipEngConsoles' if 'eng' in t5console else 'shipSciConsoles'
            self.backend[key] = self.backend[key] + 1
        self.shipBuildBlock("Fore Weapons", 0, 'foreWeapons', self.backend['shipForeWeapons'], ["Ship Fore Weapon", "Pick Fore Weapon", ""])
        #todo ADD SECDEF
        self.shipBuildBlock("Deflector", 1, 'deflector', 1, ["Ship Deflector Dish", "Pick Deflector", ""])
        self.shipBuildBlock("Engines", 2, 'engines', 1, ["Impulse Engine", "Pick Engine", ""])
        self.shipBuildBlock("Core", 3, 'warpCore', 1, ["Singularity Core" if "Warbird" in self.build['ship'] or "Aves" in self.build['ship'] else "Warp Core", "Pick Core", ""])
        self.shipBuildBlock("Shield", 4, 'shield' , 1, ["Ship Shields", "Pick Shield", ""])
        self.shipBuildBlock("Aft Weapons", 5, 'aftWeapons', self.backend['shipAftWeapons'], ["Ship Aft Weapon", "Pick aft weapon", ""])
        self.shipBuildBlock("Devices", 6, 'devices', self.backend['shipDevices'], ["Ship Device", "Pick Device", ""])
        if self.backend['shipUniConsoles'] > 0:
            self.shipBuildBlock("Uni Consoles", 7, 'uniConsoles', self.backend['shipUniConsoles'], ["Console", "Pick Uni Console", "Console - Universal - "])
        self.shipBuildBlock("Sci Consoles", 8, 'sciConsoles', self.backend['shipSciConsoles'], ["Ship Science Console", "Pick Sci Console", "Console - Science - "])
        self.shipBuildBlock("Eng Consoles", 9, 'engConsoles', self.backend['shipEngConsoles'], ["Ship Engineering Console", "Pick Eng Console", "Console - Engineering - "])
        self.shipBuildBlock("Tac Consoles", 10, 'tacConsoles', self.backend['shipTacConsoles'], ["Ship Tactical Console", "Pick Tac Console", "Console - Tactical - "])
        if self.backend['shipHangars'] > 0:
            self.shipBuildBlock("Hangars", 11, 'hangars', self.backend['shipHangars'], ["Hangar Bay", "Pick Hangar Pet", "Hangar - "])

    def traitLabelCallback(self, e, label, key, table, i, reputation=False, active=False, starship=False):
        """Common callback for all trait labels"""
        if starship:
            item = self.pickStarshipTrait()
            name = item.find('td', first=True).text
            image = self.imageFromInfoboxName(name, self.itemBoxX, self.itemBoxY)
        else:
            item = self.pickTrait(table, reputation, active)
            name = item.find('td.field_name', first=True).text.replace("Trait: ", '')
            image = self.imageFromInfoboxName(name, self.itemBoxX, self.itemBoxY)
        label.configure(image=image)
        self.build[key][i] = name
        self.backend['i_'+key][i] = image

    def traitBlock(self, name, row, key, n, args=None):
        """Set up n-element line of traits"""
        self.backend['i_'+key] = [None] * n
        label =  Label(self.traitFrame, text=name)
        label.grid(row=row, column=0, sticky='nsew', padx=5, pady=2)
        for i in range(n):
            if key in self.build and self.build[key][i] is not None:
                image=self.imageFromInfoboxName(self.build[key][i],self.itemBoxX,self.itemBoxY)
                self.backend['i_'+key][i] = image
            else:
                image=self.emptyImage
            label = Label(self.traitFrame, image=image, relief='raised', borderwidth=1)
            label.grid(row=row, column=i+1, sticky='nse', padx=2, pady=2)
            if (args is not None):
                label.bind('<Button-1>', lambda e,label=label,i=i,args=args,key=key:self.traitLabelCallback(e,label,key,self.traits,i,*args))

    def traitFrameSetup(self):
        """Set up UI frame containing traits"""
        for widget in self.traitFrame.winfo_children():
            widget.destroy()
        isAlien = 'Alien' in self.backend['species'].get()
        self.traitBlock("Personal", 0, 'personalSpaceTrait', 6 if isAlien else 5, [False])
        self.traitBlock("Personal", 1, 'personalSpaceTrait2', 5, [False])
        self.traitBlock("Starship", 2, 'starshipTrait', 5+(1 if '-X' in self.backend['tier'].get() else 0), [False, False, True])
        self.traitBlock("SpaceRep", 3, 'spaceRepTrait', 5, [True])
        self.traitBlock("Active", 4, 'activeRepTrait', 5, [True, True])
        
    def boffLabelCallback(self, e, label, i, key, spec, sspec, rank):
        """Common callback for boff labels"""
        item = self.pickBoffSkill(spec, sspec, rank)
        cname = item.find('td', first=True).text
        image = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/"+cname.replace(' ', '_')+"_icon_(Federation).png", cname, self.itemBoxX, self.itemBoxY)
        label.configure(image=image)
        self.build['boffs'][key][i] = cname
        self.backend['i_'+key][i] = image

    def boffFrameSetup(self, ship):
        """Set up UI frame containing boff skills"""
        for widget in self.boffFrame.winfo_children():
            widget.destroy()
        boffString = ship.find('td.field_boffs', first=True).html
        boffString = boffString.replace('<td class="field_boffs">', '').replace('</td>', '')
        boffs = [s.strip() for s in boffString.split('<span class="CargoDelimiter">•</span>')]
        col = 0
        row = 0
        for boff in boffs:
            rank = 3 if "Lieutenant Commander" in boff else 2 if "Lieutenant" in boff else 4 if "Commander" in boff else 1
            spec = "Tactical" if "Tactical" in boff else "Science" if 'Science' in boff else "Engineering" if "Engineering" in boff else "Universal"
            sspec = None
            for s in self.specNames:
                if '-'+s in boff:
                    sspec = s
                    break
            bFrame = Frame(self.boffFrame, width=120, height=80, bg='#a7a8a7')
            bFrame.grid(row=row,column=col, padx=10, pady=2, sticky='nsew')
            boffSan = boff.replace(' ','_')
            self.backend['i_'+boffSan] = [None] * rank
            row = row+1 if col == 1 else row
            col = 0 if col == 1 else 1
            specLabel = Label(bFrame, text=(spec if sspec is None else spec+' / '+sspec))
            specLabel.grid(row=0, column=0, columnspan=max(2, rank), sticky='nsew')
            skills = []
            for i in range(rank):
                if boffSan in self.build['boffs'] and self.build['boffs'][boffSan][i] is not None:
                    image=self.imageFromInfoboxName(self.build['boffs'][boffSan][i],self.itemBoxX,self.itemBoxY)
                    self.backend['i_'+boffSan][i] = image
                else:
                    image=self.emptyImage
                    self.build['boffs'][boffSan] = [None] * rank
                label = Label(bFrame, image=image)
                label.grid(row=1, column=i, sticky='nse', padx=5, pady=2)
                label.bind('<Button-1>', lambda e,label=label,i=i,key=boffSan,spec=spec,sspec=sspec,rank=rank:self.boffLabelCallback(e,label,i,key,spec,sspec,i))
                skills.append(label)
                
    def getTierOptions(self, tier):
        """Get possible tier options from ship tier string"""
        return ['T5', 'T5-U', 'T5-X'] if int(tier) == 5 else ['T6', 'T6-X'] if int(tier) == 6 else ['T'+tier]
    
    def setupBuildFrames(self):
        """Set up all relevant build frames"""
        self.build['tier'] = self.backend['tier'].get()
        if self.backend['shipHtml'] is not None:
            self.shipBuildFrameSetup(self.backend['shipHtml'])
            self.boffFrameSetup(self.backend['shipHtml'])
            self.traitFrameSetup()
        
    def shipMenuCallback(self, *args):
        """Callback for ship selection menu"""
        if self.backend['ship'].get() == '':
            return
        self.build['ship'] = self.backend['ship'].get()
        self.backend['shipHtml'] = self.getShipFromName(self.r_ships, self.build['ship'])
        tier = self.backend['shipHtml'].find('td.field_tier', first=True).text
        for widget in self.shipTierFrame.winfo_children():
            widget.destroy()
        Label(self.shipTierFrame, text="Tier:").grid(row=0, column=0, sticky='nsew')
        OptionMenu(self.shipTierFrame, self.backend["tier"], *self.getTierOptions(tier)).grid(column=1, row=0, sticky='nsew')
        ship_url = list(self.backend['shipHtml'].absolute_links)[0]
        r_sp = self.fetchOrRequestHtml(ship_url, self.build['ship'])
        try:
            ship_image = list(r_sp.find('div.mw-parser-output a.image img'))[1].attrs['data-image-name']
            self.shipImg = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/"+ship_image.replace(' ','_'), self.build['ship'], 260, 146)
            self.shipLabel.configure(image=self.shipImg)
        except:
            self.shipImg = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/Federation_Emblem.png", "federation_emblem", 260, 146)
            self.shipLabel.configure(image=self.shipImg)
        self.backend["tier"].set(self.getTierOptions(tier)[0])
    
    def searchHtmlTable(self, html, field, phrases):
        """Return HTML table elements containing 1 or more phrases"""
        trs = html.find('tr')
        fields = [tr.find(field, first=True) for tr in trs]
        results = [tr for tr,field in zip(trs,fields) if isinstance(field, Element) and any(phrase in field.text for phrase in phrases)]
        return [] if isinstance(results, int) else results

    def setVarAndQuit(self, e, name, v, win):
        """Helper function to set variables from within UI callbacks"""
        v.append(name)
        win.destroy()

    def fetchModifiers(self):
        """Fetch equipment modifiers"""
        modPage = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Modifier", "modifiers").find("div.mw-parser-output", first=True).html
        mods = re.findall(r"(<td.*?>(<b>)*\[.*?\](</b>)*</td>)", modPage)
        return list(set([re.sub(r"<.*?>",'',mod[0]) for mod in mods]))

    def setupModFrame(self, frame, rarity):
        """Set up modifier frame in equipment picker"""
        for widget in frame.winfo_children():
            widget.destroy()
        n = self.rarities.index(rarity)
        self.backend['modifiers'] = []
        mods = self.fetchModifiers()
        for i in range(n):
            v = StringVar()
            OptionMenu(frame, v, *mods).grid(row=0, column=i, sticky='n')
            self.backend['modifiers'].append(v)
            
    def setupInfoboxFrame(self, item):
        """Set up infobox frame with given item"""
        for widget in self.infoboxFrame.winfo_children():
            widget.destroy()
        text = Text(self.infoboxFrame, height=25, width=50)
        text.pack(side="left", fill="both", expand=True)
            
    def sanitizeEquipmentName(self, name):
        """Strip irreleant bits of equipment name for easier icon matching"""
        return re.sub(r"(∞.*)|(Mk X.*)|(\[.*\].*)|(MK X.*)|(-S$)", '', name).strip()

    def precacheEquipment(self, keyPhrase):
        """Populate in-memory cache of ship equipment lists for faster loading"""
        if keyPhrase in self.backend['cacheEquipment']:
            return self.backend['cacheEquipment'][keyPhrase]
        phrases = [keyPhrase] + (["Ship Weapon"] if "Weapon" in keyPhrase else ["Universal Console"] if "Console" in keyPhrase else [])
        equipment = self.searchHtmlTable(self.infoboxes, 'td.field_type', phrases)
        self.backend['cacheEquipment'][keyPhrase] = [self.sanitizeEquipmentName(item.find('td.field_name', first=True).text) for item in equipment]
        if 'Hangar' in keyPhrase:
            self.backend['cacheEquipment'][keyPhrase] = [hangar for hangar in self.backend['cacheEquipment'][keyPhrase] if 'Hangar - Advanced' not in hangar and 'Hangar - Elite' not in hangar]
        # if 'Shield' in keyPhrase:
        #     self.backend['cacheEquipment'][keyPhrase].append('Tillys Review-Pending Modified Shield')
        if 'Deflector' in keyPhrase:
            self.backend['cacheEquipment'][keyPhrase].append('Elite Fleet Preservation Protomatter Deflector Array')

    def pickEquipment(self, keyPhrase, title, nullPhrase):
        """Open the ship equipment picker window"""
        pickWindow = Toplevel(self.window)
        pickWindow.title(title)
        container = Frame(pickWindow)
        topbarFrame = Frame(container)
        self.backend['modifiers'] = []
        rarity = StringVar()
        rarityOption = OptionMenu(topbarFrame, rarity, *self.rarities)
        rarityOption.grid(row=0, column=0, sticky='nsew')
        modFrame = Frame(topbarFrame, bg='gray')
        modFrame.grid(row=0, column=1, sticky='nsew')
        rarity.trace('w', lambda v,i,m,frame=modFrame:self.setupModFrame(frame, rarity=rarity.get()))
        topbarFrame.pack()
        canvas = Canvas(container)
        scrollbar = Scrollbar(container, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind_all('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        container.pack()
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side=RIGHT,fill=Y)
        self.precacheEquipment(keyPhrase)
        itemVar = []
        images = []
        for item in self.backend['cacheEquipment'][keyPhrase]:
            cname = item.replace(nullPhrase, '')
            cimg = self.imageFromInfoboxName(item, self.itemBoxX, self.itemBoxY)
            images.append(cimg)
            frame = Frame(scrollable_frame, relief='raised', borderwidth=1)
            label = Label(frame, text=cname, wraplength=120, justify=LEFT)
            label.grid(row=0, column=0)
            label.bind('<Button-1>', lambda e,name=item,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
            label = Label(frame, image=cimg)
            label.grid(row=0, column=1)
            label.bind('<Button-1>', lambda e,name=item,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
            frame.pack(fill=BOTH, expand=True)
            frame.bind('<Button-1>', lambda e,name=item,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
        pickWindow.grab_set()
        pickWindow.wait_window()
        return {'item':itemVar[0], 'rarity': rarity.get(), 'mods': [mod.get() for mod in self.backend['modifiers']]}

    def pickTrait(self, table, reputation=False, active=False):
        """Open the personal/reputation trait picker window"""
        pickWindow = Toplevel(self.window)
        pickWindow.title("Pick trait")
        container = Frame(pickWindow)
        canvas = Canvas(container)
        scrollbar = Scrollbar(container, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind_all('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        container.pack()
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side=RIGHT,fill=Y)
        trs = table.find('tr')
        traits = [e for e in trs if isinstance(e.find('td.field_chartype', first=True), Element) and 'char' in e.find('td.field_chartype', first=True).text]
        traits = [e for e in traits if isinstance(e.find('td.field_environment', first=True), Element) and 'space' in e.find('td.field_environment', first=True).text]
        traits = [e for e in traits if isinstance(e.find('td.field_type', first=True), Element) and (('reputation' in e.find('td.field_type', first=True).text) == reputation)]
        if reputation:
            actives = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Category:Player_abilities", "player_abilities").links
            traits = [e for e in traits if isinstance(e.find('td.field_name', first=True), Element) and (('/wiki/Trait:_'+e.find('td.field_name', first=True).text.replace(' ','_') in list(actives)) == active)]
        if isinstance(traits, int):
            pickWindow.destroy()
            return 
        traitVar = []
        images = []
        for trait in traits:
            cname = trait.find('td.field_name', first=True).text.replace("Trait: ", '')
            cimg = self.imageFromInfoboxName(cname,self.itemBoxX,self.itemBoxY)
            images.append(cimg)
            frame = Frame(scrollable_frame, relief='raised', borderwidth=1)
            label = Label(frame, text=cname)
            label.grid(row=0, column=0)
            label.bind('<Button-1>', lambda e,name=trait,v=traitVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
            label = Label(frame, image=cimg)
            label.grid(row=0, column=1)
            label.bind('<Button-1>', lambda e,name=trait,v=traitVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
            frame.pack(fill=BOTH, expand=True)
            frame.bind('<Button-1>', lambda e,name=trait,v=traitVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
        pickWindow.grab_set()
        pickWindow.wait_window()
        return traitVar[0]

    def pickStarshipTrait(self):
        """Open the starship trait picker window"""
        pickWindow = Toplevel(self.window)
        pickWindow.title("Pick trait")
        container = Frame(pickWindow)
        canvas = Canvas(container)
        scrollbar = Scrollbar(container, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind_all('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        container.pack()
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side=RIGHT,fill=Y)
        traits = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Starship_traits", "starship_traits").find('tr')[1:]
        traitVar = []
        images = []
        for trait in traits:
            tds = trait.find('td')
            if tds is None or len(tds)<1:
                continue
            cname = tds[0].text
            cimg = self.imageFromInfoboxName(cname,self.itemBoxX,self.itemBoxY)
            images.append(cimg)
            frame = Frame(scrollable_frame, relief='raised', borderwidth=1)
            label = Label(frame, text=cname)
            label.grid(row=0, column=0)
            label.bind('<Button-1>', lambda e,name=trait,v=traitVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
            label = Label(frame, image=cimg)
            label.grid(row=0, column=1)
            label.bind('<Button-1>', lambda e,name=trait,v=traitVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
            frame.pack(fill=BOTH, expand=True)
            frame.bind('<Button-1>', lambda e,name=trait,v=traitVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
        pickWindow.grab_set()
        pickWindow.wait_window()
        return traitVar[0]

    def pickBoffSkill(self, spec, sspec, rank):
        """Open the boff skill picker window"""
        pickWindow = Toplevel(self.window)
        pickWindow.title("Pick Ability")
        container = Frame(pickWindow)
        canvas = Canvas(container)
        scrollbar = Scrollbar(container, orient=VERTICAL, command=canvas.yview)
        scrollable_frame = Frame(canvas)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind_all('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        container.pack()
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side=RIGHT,fill=Y)
        self.boffAbilities = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Bridge_officer_and_kit_abilities", "boff_abilities")
        l0 = [h2 for h2 in self.boffAbilities.find('h2') if ' Abilities' in h2.html]
        l1 = self.boffAbilities.find('h2+h3+table')
        if 'Universal' in spec:
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#Tactical_Abilities', first=True), Element)]
            trs = table[0].find('tr')
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#Engineering_Abilities', first=True), Element)]
            trs = trs + table[0].find('tr')
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#Science_Abilities', first=True), Element)]
            trs = trs + table[0].find('tr')
        else:
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#'+spec.replace(' ','_')+'_Abilities', first=True), Element)]
            trs = table[0].find('tr')
        if sspec is not None:
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#'+sspec.replace(' ','_')+'_Abilities', first=True), Element)]
            trs = trs + table[0].find('tr')
        skills = []
        for tr in trs:
            tds = tr.find('td')
            if len(tds)>0 and tds[rank+1].text.strip() != '':
                skills.append(tr)
        skillVar = []
        images = []
        for skill in skills:
            cname = skill.find('td', first=True).text.replace(':','')
            cimg = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/"+cname.replace(' ', '_')+"_icon_(Federation).png", cname,self.itemBoxX,self.itemBoxY)
            images.append(cimg)
            frame = Frame(scrollable_frame, relief='raised', borderwidth=1)
            label = Label(frame, text=cname)
            label.grid(row=0, column=0)
            label.bind('<Button-1>', lambda e,name=skill,v=skillVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
            label = Label(frame, image=cimg)
            label.grid(row=0, column=1)
            label.bind('<Button-1>', lambda e,name=skill,v=skillVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
            frame.pack(fill=BOTH, expand=True)
            frame.bind('<Button-1>', lambda e,name=skill,v=skillVar,win=pickWindow:self.setVarAndQuit(e,name,v,win))
        pickWindow.grab_set()
        pickWindow.wait_window()
        return skillVar[0]

    def imageFromInfoboxName(self, name, width=None, height=None):
        """Translate infobox name into wiki icon link"""
        try:
            return self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/"+name.replace(' ', '_')+"_icon.png", name,width,height)
        except:
            return self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/Common_icon.png", "no_icon",width,height)


    def importCallback(self, event):
        """Callback for import button"""
        inFilename = filedialog.askopenfilename(filetypes=[("JSON file", '*.json'),("PNG image","*.png"),("All Files","*.*")])
        if inFilename.endswith('.png'):
            image = Image.open(inFilename)
            self.build = json.loads(image.text['build'])
        else:
            with open(inFilename, 'r') as inFile:
                self.build = json.load(inFile)
        self.copyBuildToBackend('career')
        self.copyBuildToBackend('species')
        self.copyBuildToBackend('specPrimary')
        self.copyBuildToBackend('specSecondary')
        self.copyBuildToBackend('ship')
        self.copyBuildToBackend('tier')
        self.traitFrameSetup()

    def exportCallback(self, event):
        """Callback for export button"""
        with filedialog.asksaveasfile() as outFile:
            json.dump(self.build, outFile)
            
    def exportPngCallback(self, event):
        """Callback for export as png button"""
        image = ImageGrab.grab(bbox=(self.window.winfo_rootx(), self.window.winfo_rooty(), self.window.winfo_width(), self.window.winfo_height()))
        outFilename = filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG image","*.png"),("All Files","*.*")])
        info = PngImagePlugin.PngInfo()
        info.add_text('build', json.dumps(self.build))
        image.save(outFilename, "PNG", pnginfo=info)

    def copyBackendToBuild(self, key):
        """Helper function to copy backend value to build dict"""
        self.build[key] = self.backend[key].get()
    def copyBuildToBackend(self, key):
        """Helper function to copy build value to backend dict"""
        self.backend[key].set(self.build[key])

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
        for frame in [self.shipBuildFrame, self.traitFrame, self.boffFrame, self.doffFrame]:
            for widget in frame.winfo_children():
                widget.destroy()
        self.shipImg = self.emptyImage
        self.shipLabel.configure(image=self.shipImg)

    def clearBuild(self):
        """Initialize new build state"""
        self.build = {
            "boffs": dict(), 'activeRepTrait': [None] * 5, 'spaceRepTrait': [None] * 5,
            'personalSpaceTrait': [None] * 6, 'personalSpaceTrait2': [None] * 5,
            'starshipTrait': [None] * 6, 'tacConsoles': [None] * 5,
            'sciConsoles': [None] * 5, 'engConsoles': [None] * 5, 'devices': [None] * 5,
            'aftWeapons': [None] * 5, 'foreWeapons': [None] * 5, 'hangars': [None] * 2,
            'deflector': [None], 'engines': [None], 'warpCore': [None], 'shield': [None],
            'career': 'Tactical', 'species': 'Alien', 'ship': '', 'specPrimary': '', 
            'specSecondary': '', "tier": ''
        }
    
    def clearBackend(self):
        self.backend = { 
                        "career": StringVar(self.window), "species": StringVar(self.window), 
                        "specPrimary": StringVar(self.window), "specSecondary": StringVar(self.window), 
                        "ship": StringVar(self.window), "tier": StringVar(self.window), 
                        'cacheEquipment': dict(), "shipHtml": None
            }

    def __init__(self):
        """Main setup function"""
        self.window = Tk()
        self.window.geometry('1200x650')
        self.window.title("STO Equipment and Trait Selector")
        self.window.wm_attributes('-transparentcolor', 'magenta')
        self.session = HTMLSession()
        self.clearBuild()
        self.clearBackend()
        self.backend['career'].trace('w', lambda v,i,m:self.copyBackendToBuild('career'))
        self.backend['species'].trace('w', lambda v,i,m:self.copyBackendToBuild('species'))
        self.backend['specPrimary'].trace('w', lambda v,i,m:self.copyBackendToBuild('specPrimary'))
        self.backend['specSecondary'].trace('w', lambda v,i,m:self.copyBackendToBuild('specSecondary'))
        self.backend['tier'].trace('w', lambda v,i,m:self.setupBuildFrames())
        self.backend["career"].set("Tactical")
        self.backend["species"].set("Alien")
        self.rarities = ["Common", "Uncommon", "Rare", "Very rare", "Ultra rare", "Epic"]

        self.emptyImage = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/Common_icon.png", "no_icon",self.itemBoxX,self.itemBoxY)
        self.infoboxes = self.fetchOrRequestHtml(SETS.item_query, "infoboxes")
        self.traits = self.fetchOrRequestHtml(SETS.trait_query, "traits")
        playerInfoFrame = Frame(self.window, relief='raised', borderwidth=2)
        playerInfoFrame.grid(column=0, row=0, sticky='nwse')
        labelCareer = Label(playerInfoFrame, text="Career: ").grid(column=0, row = 0, sticky='nsew')
        careerMenu = OptionMenu(playerInfoFrame, self.backend["career"], "Tactical", "Engineering", "Science").grid(column=1, row=0, sticky='nsew')
        labelSpecies = Label(playerInfoFrame, text="Species: ").grid(column=0, row = 1, sticky='nsew')
        r_species = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Category:Player_races", "species")
        l_species_names = [e.text for e in r_species.find('#mw-pages .mw-category-group .to_hasTooltip') if 'Guide' not in e.text and 'Player' not in e.text]
        speciesMenu = OptionMenu(playerInfoFrame, self.backend["species"], *l_species_names).grid(column=1, row=1, sticky='nsew')
        r_specs = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Category:Captain_specializations", "specs")
        self.specNames = [e.text.replace(' (specialization)', '').replace(' Officer', '').replace(' Operative', '') for e in r_specs.find('#mw-pages .mw-category-group .to_hasTooltip') if '(specialization)' in e.text]
        labelSpecPrimary = Label(playerInfoFrame, text="SpecPrimary: ").grid(column=0, row = 2, sticky='nsew')
        specPrimaryMenu = OptionMenu(playerInfoFrame, self.backend["specPrimary"], '', *self.specNames).grid(column=1, row=2, sticky='nsew')
        labelSpecSecondary = Label(playerInfoFrame, text="SpecSecondary: ").grid(column=0, row = 3, sticky='nsew')
        specSecondaryMenu = OptionMenu(playerInfoFrame, self.backend["specSecondary"], '', *self.specNames).grid(column=1, row=3, sticky='nsew')
        exportImportFrame = Frame(playerInfoFrame)
        exportImportFrame.grid(column=0, row=4, columnspan=2, sticky='nsew')
        buttonExport = Button(exportImportFrame, text='Export')
        buttonExport.grid(column=0, row=0, sticky='nsew')
        buttonExport.bind('<Button-1>', self.exportCallback)
        buttonImport = Button(exportImportFrame, text='Import')
        buttonImport.grid(column=1, row=0, sticky='nsew')
        buttonImport.bind('<Button-1>', self.importCallback)
        buttonClear = Button(exportImportFrame, text='Clear')
        buttonClear.grid(column=2, row=0, sticky='nsew')
        buttonClear.bind('<Button-1>', self.clearBuildCallback)
        buttonExportPng = Button(exportImportFrame, text='Export .png')
        buttonExportPng.grid(column=3, row=0, sticky='nsew')
        buttonExportPng.bind('<Button-1>', self.exportPngCallback)


        self.shipInfoFrame = Frame(self.window, relief='raised', borderwidth=2)
        self.shipInfoFrame.grid(column=0, row=1, sticky='nwse')
        self.shipBuildFrame = Frame(self.window, bg='#a7a8a7', relief='raised', borderwidth=2)
        self.shipBuildFrame.grid(column=1, row=0, rowspan=2, sticky='nwse')
        self.traitFrame = Frame(self.window, bg='#a7a8a7', relief='raised', borderwidth=2)
        self.traitFrame.grid(column=2, row=0, sticky='nwse')
        self.boffFrame = Frame(self.window, bg='#a7a8a7', relief='raised', borderwidth=2)
        self.boffFrame.grid(column=2, row=1, sticky='nwse')
        
        self.doffFrame = Frame(self.window, bg='#a7a8a7', relief='raised', borderwidth=2)
        self.doffFrame.grid(column=3, row=0, sticky='nwse')
        self.infoboxFrame = Frame(self.window, bg='#a7a8a7', relief='raised', borderwidth=2)
        self.infoboxFrame.grid(column=3, row=1, sticky='nwse')

        self.r_ships = self.fetchOrRequestHtml(SETS.ship_query, "ship_list")
        self.l_ship_names = [e.text for e in self.r_ships.find("td.field_name")]
        self.backend["ship"].set(self.l_ship_names[0])
        labelShip = Label(self.shipInfoFrame, text="Ship: ")
        labelShip.grid(column=0, row = 0, sticky='nwse')
        shipMenu = OptionMenu(self.shipInfoFrame, self.backend["ship"], *self.l_ship_names)
        shipMenu.grid(column=1, row=0, sticky='nwse')
        self.shipTierFrame = Frame(self.shipInfoFrame)
        self.shipTierFrame.grid(column=0, row=1, columnspan=2, sticky='nwse')
        self.shipLabel = Label(self.shipInfoFrame)
        self.shipLabel.grid(column=0, row=2, columnspan=2, sticky='nwse')

        self.backend['ship'].trace('w', self.shipMenuCallback)
        self.traitFrameSetup()
        self.window.mainloop()

SETS()