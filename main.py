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
    
    def getTierOptions(self, tier):
        """Get possible tier options from ship tier string"""
        return ['T5', 'T5-U', 'T5-X'] if int(tier) == 5 else ['T6', 'T6-X'] if int(tier) == 6 else ['T'+tier]
    
    def setVarAndQuit(self, e, name, image, v, win):
        """Helper function to set variables from within UI callbacks"""
        v['item'] = name
        v['image'] = image
        win.destroy()
        
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
        equipment = self.searchHtmlTable(self.infoboxes, 'td.field_type', phrases)
        self.backend['cacheEquipment'][keyPhrase] = {self.sanitizeEquipmentName(item.find('td.field_name', first=True).text): item for item in equipment}
        if 'Hangar' in keyPhrase:
            self.backend['cacheEquipment'][keyPhrase] = {key:self.backend['cacheEquipment'][keyPhrase][key] for key in self.backend['cacheEquipment'][keyPhrase] if 'Hangar - Advanced' not in key and 'Hangar - Elite' not in key}

    def searchHtmlTable(self, html, field, phrases):
        """Return HTML table elements containing 1 or more phrases"""
        trs = html.find('tr')
        fields = [tr.find(field, first=True) for tr in trs]
        results = [tr for tr,field in zip(trs,fields) if isinstance(field, Element) and any(phrase in field.text for phrase in phrases)]
        return [] if isinstance(results, int) else results

    def fetchModifiers(self):
        """Fetch equipment modifiers"""
        if self.backend['modifiers'] is None:
            modPage = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Modifier", "modifiers").find("div.mw-parser-output", first=True).html
            mods = re.findall(r"(<td.*?>(<b>)*\[.*?\](</b>)*</td>)", modPage)
            self.backend['modifiers'] = list(set([re.sub(r"<.*?>",'',mod[0]) for mod in mods]))
        return self.backend['modifiers']
    
    def setListIndex(self, list, index, value):
        print(value)
        list[index] = value

    def imageFromInfoboxName(self, name, width=None, height=None):
        """Translate infobox name into wiki icon link"""
        width = self.itemBoxX if width is None else width
        height = self.itemBoxY if height is None else height
        try:
            return self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/"+name.replace(' ', '_')+"_icon.png", name,width,height)
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
                        'cacheEquipment': dict(), "shipHtml": None, 'modifiers': None
            }
        
    def clearFrame(self, frame):
        for widget in frame.winfo_children():
            widget.destroy()

    def applyContentFilter(self, content, filter):
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
        container.pack(fill=BOTH, expand=True)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side=RIGHT,fill=Y)
        i = 0
        for name,image in items_list:
            frame = Frame(scrollable_frame, relief='ridge', borderwidth=1)
            label = Label(frame, text=name, wraplength=120, justify=LEFT)
            label.grid(row=0, column=0, sticky='nsew')
            label.bind('<Button-1>', lambda e,name=name,image=image,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,image,v,win))
            label.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
            label = Label(frame, image=image)
            label.grid(row=0, column=1, sticky='nsew')
            label.bind('<Button-1>', lambda e,name=name,image=image,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,image,v,win))
            label.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
            frame.grid(row=i, column=0, sticky='nsew')
            frame.bind('<Button-1>', lambda e,name=name,image=image,v=itemVar,win=pickWindow:self.setVarAndQuit(e,name,image,v,win))
            frame.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
            content[name] = (frame, i, 0)
            i = i + 1
        pickWindow.grab_set()
        pickWindow.wait_window()
        return itemVar
    
    def shipItemLabelCallback(self, e, canvas, img, i, key, args):
        """Common callback for ship equipment labels"""
        self.precacheEquipment(args[0])
        itemVar = {"item":'',"image":self.emptyImage, "rarity": self.rarities[0], "modifiers":[None]}
        items_list = [ (item.replace(args[2], ''), self.imageFromInfoboxName(item)) for item in list(self.backend['cacheEquipment'][args[0]].keys())]
        item = self.pickerGui(args[1], itemVar, items_list, [self.setupSearchFrame, self.setupRarityFrame])
        if 'rarity' not in item:
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
            trs = self.traits.find('tr')
            traits = [e for e in trs if isinstance(e.find('td.field_chartype', first=True), Element) and 'char' in e.find('td.field_chartype', first=True).text]
            traits = [e for e in traits if isinstance(e.find('td.field_environment', first=True), Element) and 'space' in e.find('td.field_environment', first=True).text]
            traits = [e for e in traits if isinstance(e.find('td.field_type', first=True), Element) and (('reputation' in e.find('td.field_type', first=True).text) == args[0])]
            if args[0]:
                actives = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Category:Player_abilities", "player_abilities").links
                traits = [e for e in traits if isinstance(e.find('td.field_name', first=True), Element) and (('/wiki/Trait:_'+e.find('td.field_name', first=True).text.replace(' ','_') in list(actives)) == args[1])]
            items_list = [(trait.find('td.field_name', first=True).text.replace("Trait: ", ''), self.imageFromInfoboxName(trait.find('td.field_name', first=True).text.replace("Trait: ", ''),self.itemBoxX,self.itemBoxY)) for trait in traits]
        itemVar = self.getEmptyItem()
        item = self.pickerGui("Pick trait", itemVar, items_list, [self.setupSearchFrame])
        canvas.itemconfig(img[0],image=item['image'])
        self.build[key][i] = item['item'].replace("Trait: ", '')
        self.backend['i_'+key][i] = item['image']
        
    def boffLabelCallback(self, e, canvas, img, i, key, args):
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
            table = [header[1] for header in zip(l0, l1) if isinstance(header[0].find('#'+args[0].replace(' ','_')+'_Abilities', first=True), Element)]
            trs = trs + table[0].find('tr')
        skills = []
        for tr in trs:
            tds = tr.find('td')
            if len(tds)>0 and tds[args[2]+1].text.strip() != '':
                skills.append(tr)
        items_list = []
        for skill in skills:
            cname = skill.find('td', first=True).text.replace(':','')
            cimg = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/"+cname.replace(' ', '_')+"_icon_(Federation).png", cname,self.itemBoxX,self.itemBoxY)
            items_list.append((cname,cimg))
        itemVar = self.getEmptyItem()
        item = self.pickerGui("Pick Ability", itemVar, items_list, [self.setupSearchFrame])
        canvas.itemconfig(img,image=item['image'])
        self.build['boffs'][key][i] = item['item']
        self.backend['i_'+key][i] = item['image']
        
    def shipMenuCallback(self, *args):
        """Callback for ship selection menu"""
        if self.backend['ship'].get() == '':
            return
        self.build['ship'] = self.backend['ship'].get()
        self.backend['shipHtml'] = self.getShipFromName(self.r_ships, self.build['ship'])
        tier = self.backend['shipHtml'].find('td.field_tier', first=True).text
        self.clearFrame(self.shipTierFrame)
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
        
    def shipPickButtonCallback(self, *args):
        """Callback for ship picker button"""
        itemVar = self.getEmptyItem()
        items_list = [(name, self.emptyImage) for name in self.l_ship_names]
        item = self.pickerGui("Pick Starship", itemVar, items_list, [self.setupSearchFrame])
        self.shipButton.configure(text=item['item'])
        self.backend['ship'].set(item['item'])

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
        self.setupTraitFrame()

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

    def setupSearchFrame(self,frame,itemVar,content):
        topbarFrame = Frame(frame)
        searchText = StringVar()
        Label(topbarFrame, text="Search:").grid(row=0, column=0, sticky='nsew')
        Entry(topbarFrame, textvariable=searchText).grid(row=0, column=1, columnspan=5, sticky='nsew')
        searchText.trace_add('write', lambda v,i,m,content=content:self.applyContentFilter(content, searchText.get()))
        topbarFrame.pack()

    def setupRarityFrame(self,frame,itemVar,content):
        topbarFrame = Frame(frame)
        rarity = StringVar(value=self.rarities[0])
        rarityOption = OptionMenu(topbarFrame, rarity, *self.rarities)
        rarityOption.grid(row=0, column=0, sticky='nsw')
        modFrame = Frame(topbarFrame, bg='gray')
        modFrame.grid(row=1, column=0, sticky='nsew')
        rarity.trace_add('write', lambda v,i,m,frame=modFrame:self.setupModFrame(frame, rarity=rarity.get(), itemVar=itemVar))
        topbarFrame.pack()
            
    def labelBuildBlock(self, frame, name, row, key, n, callback, args=None):
        """Set up n-element line of ship equipment"""
        self.backend['i_'+key] = [None] * n
        label =  Label(frame, text=name)
        label.grid(row=row, column=0, sticky='nsew', pady=2)
        for i in range(n):
            image1=None
            if key in self.build and self.build[key][i] is not None:
                image0=self.imageFromInfoboxName(self.build[key][i]['item'])
                if 'rarity' in self.build[key][i]:
                    image1=self.imageFromInfoboxName(self.build[key][i]['rarity'])
                self.backend['i_'+key][i] = [image0, image1]
            else:
                image0=image1=self.emptyImage
            canvas = Canvas(frame, relief='groove', borderwidth=1, width=25, height=35)
            canvas.grid(row=row, column=i+1, sticky='nse', padx=2, pady=2)
            img0 = canvas.create_image(0,0, anchor="nw",image=image0)
            img1 = None if image1 is None else canvas.create_image(0,0, anchor="nw",image=image1)
            if (args is not None):
                canvas.bind('<Button-1>', lambda e,canvas=canvas,img=(img0, img1),i=i,args=args,key=key,callback=callback:callback(e,canvas,img,i,key,args))

    def setupShipBuildFrame(self, ship):
        """Set up UI frame containing ship equipment"""
        self.clearFrame(self.shipBuildFrame)
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
        self.labelBuildBlock(self.shipBuildFrame, "Fore Weapons", 0, 'foreWeapons', self.backend['shipForeWeapons'], self.shipItemLabelCallback, ["Ship Fore Weapon", "Pick Fore Weapon", ""])
        #todo ADD SECDEF
        self.labelBuildBlock(self.shipBuildFrame, "Deflector", 1, 'deflector', 1, self.shipItemLabelCallback, ["Ship Deflector Dish", "Pick Deflector", ""])
        self.labelBuildBlock(self.shipBuildFrame, "Engines", 2, 'engines', 1, self.shipItemLabelCallback, ["Impulse Engine", "Pick Engine", ""])
        self.labelBuildBlock(self.shipBuildFrame, "Core", 3, 'warpCore', 1, self.shipItemLabelCallback, ["Singularity Core" if "Warbird" in self.build['ship'] or "Aves" in self.build['ship'] else "Warp Core", "Pick Core", ""])
        self.labelBuildBlock(self.shipBuildFrame, "Shield", 4, 'shield' , 1, self.shipItemLabelCallback, ["Ship Shields", "Pick Shield", ""])
        self.labelBuildBlock(self.shipBuildFrame, "Aft Weapons", 5, 'aftWeapons', self.backend['shipAftWeapons'], self.shipItemLabelCallback, ["Ship Aft Weapon", "Pick aft weapon", ""])
        self.labelBuildBlock(self.shipBuildFrame, "Devices", 6, 'devices', self.backend['shipDevices'], self.shipItemLabelCallback, ["Ship Device", "Pick Device", ""])
        if self.backend['shipUniConsoles'] > 0:
            self.labelBuildBlock(self.shipBuildFrame, "Uni Consoles", 7, 'uniConsoles', self.backend['shipUniConsoles'], self.shipItemLabelCallback, ["Console", "Pick Uni Console", "Console - Universal - "])
        self.labelBuildBlock(self.shipBuildFrame, "Sci Consoles", 8, 'sciConsoles', self.backend['shipSciConsoles'], self.shipItemLabelCallback, ["Ship Science Console", "Pick Sci Console", "Console - Science - "])
        self.labelBuildBlock(self.shipBuildFrame, "Eng Consoles", 9, 'engConsoles', self.backend['shipEngConsoles'], self.shipItemLabelCallback, ["Ship Engineering Console", "Pick Eng Console", "Console - Engineering - "])
        self.labelBuildBlock(self.shipBuildFrame, "Tac Consoles", 10, 'tacConsoles', self.backend['shipTacConsoles'], self.shipItemLabelCallback, ["Ship Tactical Console", "Pick Tac Console", "Console - Tactical - "])
        if self.backend['shipHangars'] > 0:
            self.labelBuildBlock(self.shipBuildFrame, "Hangars", 11, 'hangars', self.backend['shipHangars'], self.shipItemLabelCallback, ["Hangar Bay", "Pick Hangar Pet", "Hangar - "])

    def setupTraitFrame(self):
        """Set up UI frame containing traits"""
        self.clearFrame(self.traitFrame)
        self.labelBuildBlock(self.traitFrame, "Personal", 0, 'personalSpaceTrait', 6 if ('Alien' in self.backend['species'].get()) else 5, self.traitLabelCallback, [False, False, False])
        self.labelBuildBlock(self.traitFrame, "Personal", 1, 'personalSpaceTrait2', 5, self.traitLabelCallback, [False, False, False])
        self.labelBuildBlock(self.traitFrame, "Starship", 2, 'starshipTrait', 5+(1 if '-X' in self.backend['tier'].get() else 0), self.traitLabelCallback, [False, False, True])
        self.labelBuildBlock(self.traitFrame, "SpaceRep", 3, 'spaceRepTrait', 5, self.traitLabelCallback, [True, False, False])
        self.labelBuildBlock(self.traitFrame, "Active", 4, 'activeRepTrait', 5, self.traitLabelCallback, [True, True, False])

    def setupBoffFrame(self, ship):
        """Set up UI frame containing boff skills"""
        self.clearFrame(self.boffFrame)
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
            bFrame = Frame(self.boffFrame, width=120, height=80, relief='ridge', borderwidth=1, bg='#a7a8a7')
            bFrame.grid(row=row,column=col, padx=10, pady=2, sticky='nsew')
            boffSan = boff.replace(' ','_')
            self.backend['i_'+boffSan] = [None] * rank
            row = row+1 if col == 1 else row
            col = 0 if col == 1 else 1
            specLabel = Label(bFrame, text=(spec if sspec is None else spec+' / '+sspec))
            specLabel.grid(row=0, column=0, sticky='nsew')
            bSubFrame = Frame(bFrame)
            bSubFrame.grid(row=1, column=0, sticky='nsew')
            for i in range(rank):
                if boffSan in self.build['boffs'] and self.build['boffs'][boffSan][i] is not None:
                    image=self.imageFromInfoboxName(self.build['boffs'][boffSan][i])
                    self.backend['i_'+boffSan][i] = image
                else:
                    image=self.emptyImage
                    self.build['boffs'][boffSan] = [None] * rank
                canvas = Canvas(bSubFrame, relief='groove', borderwidth=1, width=25, height=35)
                canvas.grid(row=1, column=i, sticky='ns', padx=2, pady=2)
                img0 = canvas.create_image(0,0, anchor="nw",image=image)
                canvas.bind('<Button-1>', lambda e,canvas=canvas,img=img0,i=i,args=[spec,sspec,i],key=boffSan,callback=self.boffLabelCallback:callback(e,canvas,img,i,key,args))
                
    def setupBuildFrames(self):
        """Set up all relevant build frames"""
        self.build['tier'] = self.backend['tier'].get()
        if self.backend['shipHtml'] is not None:
            self.setupShipBuildFrame(self.backend['shipHtml'])
            self.setupBoffFrame(self.backend['shipHtml'])
            self.setupTraitFrame()

    def setupModFrame(self, frame, rarity, itemVar):
        """Set up modifier frame in equipment picker"""
        self.clearFrame(frame)
        n = self.rarities.index(rarity)
        itemVar['rarity'] = rarity
        itemVar['modifiers'] = [None]*n
        mods = self.fetchModifiers()
        for i in range(n):
            v = StringVar()
            v.trace_add('write', lambda v0,v1,v2,i=i,itemVar=itemVar,v=v:self.setListIndex(itemVar['modifiers'],i,v.get()))
            OptionMenu(frame, v, *mods).grid(row=0, column=i, sticky='n')
            
    def setupInfoboxFrame(self, item, key):
        """Set up infobox frame with given item"""
        self.clearFrame(self.infoboxFrame)
        text = Text(self.infoboxFrame, height=25, width=30, font=('Helvetica', 10))
        text.pack(side="left", fill="both", expand=True)
        html = self.backend['cacheEquipment'][key][item['item']]
        text.insert(END, item['item']+' '+('' if item['modifiers'][0] is None else ''.join(item['modifiers']))+'\n')
        text.insert(END, item['rarity']+' '+ html.find('td.field_type', first=True).text.strip()+'\n')
        for i in range(1,9):
            for header in ['td.field_head','td.field_subhead','td.field_text']:
                t = html.find(header+str(i), first=True).text
                if t.strip() != '':
                    text.insert(END, t+'\n')

    def __init__(self):
        """Main setup function"""
        self.window = Tk()
        self.window.geometry('1280x650')
        self.window.title("STO Equipment and Trait Selector")
        self.session = HTMLSession()
        self.clearBuild()
        self.clearBackend()
        self.backend['career'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('career'))
        self.backend['species'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('species'))
        self.backend['specPrimary'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('specPrimary'))
        self.backend['specSecondary'].trace_add('write', lambda v,i,m:self.copyBackendToBuild('specSecondary'))
        self.backend['tier'].trace_add('write', lambda v,i,m:self.setupBuildFrames())
        self.backend["career"].set("Tactical")
        self.backend["species"].set("Alien")
        self.rarities = ["Common", "Uncommon", "Rare", "Very rare", "Ultra rare", "Epic"]

        self.emptyImage = self.fetchOrRequestImage("https://sto.fandom.com/wiki/Special:Filepath/Common_icon.png", "no_icon",self.itemBoxX,self.itemBoxY)
        self.infoboxes = self.fetchOrRequestHtml(SETS.item_query, "infoboxes")
        self.traits = self.fetchOrRequestHtml(SETS.trait_query, "traits")
        playerInfoFrame = Frame(self.window, relief='raised', borderwidth=2)
        playerInfoFrame.grid(column=0, row=0, sticky='nwse')
        Label(playerInfoFrame, text="Career: ").grid(column=0, row = 0, sticky='nsew')
        OptionMenu(playerInfoFrame, self.backend["career"], "Tactical", "Engineering", "Science").grid(column=1, row=0, sticky='nsew')
        Label(playerInfoFrame, text="Species: ").grid(column=0, row = 1, sticky='nsew')
        r_species = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Category:Player_races", "species")
        l_species_names = [e.text for e in r_species.find('#mw-pages .mw-category-group .to_hasTooltip') if 'Guide' not in e.text and 'Player' not in e.text]
        OptionMenu(playerInfoFrame, self.backend["species"], *l_species_names).grid(column=1, row=1, sticky='nsew')
        r_specs = self.fetchOrRequestHtml("https://sto.fandom.com/wiki/Category:Captain_specializations", "specs")
        self.specNames = [e.text.replace(' (specialization)', '').replace(' Officer', '').replace(' Operative', '') for e in r_specs.find('#mw-pages .mw-category-group .to_hasTooltip') if '(specialization)' in e.text]
        Label(playerInfoFrame, text="SpecPrimary: ").grid(column=0, row = 2, sticky='nsew')
        OptionMenu(playerInfoFrame, self.backend["specPrimary"], '', *self.specNames).grid(column=1, row=2, sticky='nsew')
        Label(playerInfoFrame, text="SpecSecondary: ").grid(column=0, row = 3, sticky='nsew')
        OptionMenu(playerInfoFrame, self.backend["specSecondary"], '', *self.specNames).grid(column=1, row=3, sticky='nsew')
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
        # shipMenu = OptionMenu(self.shipInfoFrame, self.backend["ship"], *self.l_ship_names)
        # shipMenu.grid(column=1, row=0, sticky='nwse')
        self.shipButton = Button(self.shipInfoFrame, text="<Pick>", command=self.shipPickButtonCallback)
        self.shipButton.grid(column=1, row=0, sticky='nwse')
        self.shipTierFrame = Frame(self.shipInfoFrame)
        self.shipTierFrame.grid(column=0, row=1, columnspan=2, sticky='nwse')
        self.shipLabel = Label(self.shipInfoFrame)
        self.shipLabel.grid(column=0, row=2, columnspan=2, sticky='nwse')

        self.backend['ship'].trace_add('write', self.shipMenuCallback)
        self.window.mainloop()

SETS()