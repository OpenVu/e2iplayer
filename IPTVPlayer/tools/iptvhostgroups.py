# -*- coding: utf-8 -*-
#

###################################################
# LOCAL import 
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, byteify, GetConfigDir, GetHostsList, IsHostEnabled
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostsGroupItem
from Plugins.Extensions.IPTVPlayer.libs.e2ijson import loads as json_loads, dumps as json_dumps
###################################################

###################################################
# FOREIGN import
###################################################
import codecs
import os
from os import path as os_path, remove as os_remove
###################################################


class IPTVHostsGroups:
    def __init__(self):
        printDBG("IPTVHostsGroups.__init__")
        self.lastError = ''
        self.GROUPS_FILE = GetConfigDir('iptvplayerhostsgroups.json')
        
        # groups
        self.PREDEFINED_GROUPS = ["userdefined", "moviesandseries", "cartoonsandanime", "music", "sport", "documentary", \
                                  "polish", "english", "german", "french", "russian", "hungarian", "arabic", "greek", "spanish", "indian", "italian","swedish","balkans","others"]
        self.PREDEFINED_GROUPS_TITLES = {"userdefined":      "User defined", 
                                         "moviesandseries":  "Movies and series",
                                         "cartoonsandanime": "Cartoons and anime",
                                         "music":            "Music and Radio",
                                         "sport":            "Sport",
                                         "documentary":      "Documentary",
                                         "polish":           "Polish",
                                         "english":          "English",
                                         "german":           "German",
                                         "french":           "French",
                                         "russian":          "Russian",
                                         "hungarian":        "Hungarian",
                                         "arabic":           "Arabic",
                                         "greek":            "Greek",
                                         "spanish":          "Spanish",
                                         "indian":           "Indian",
                                         "italian":          "Italian",
                                         'swedish':          "Swedish",
                                         "balkans":          "Balkans",
                                         "others":           "Others",
                                        }
        
        self.LOADED_GROUPS = []
        self.LOADED_GROUPS_TITLES = {}
        self.LOADED_DISABLED_GROUPS = []
        
        self.CACHE_GROUPS = None
        
        # hosts
        self.PREDEFINED_HOSTS = {}
        self.PREDEFINED_HOSTS['userdefined']      = ['favourites', 'localmedia', 'youtube', 'dailymotion', 'vimeo ','appletrailers' ,'webstream','tsiplayer','infoversion']
        self.PREDEFINED_HOSTS['moviesandseries']  = ['yifytv','solarmovie','mythewatchseries','thewatchseriesto','classiccinemaonline','seriesonline', 'filma24hdcom', 'allboxtv', 'alltubetv', 'ekinotv', 'gledalica', \
                                                     'tfarjocom','efilmytv','akoam','kinox','filmativa','putlockertvto','filmovizijastudio','forjatn', 'movierulzsx','streamzennet','serienstreamto', 'fenixsite', \
                                                     'filisertv','iitvpl','movs4ucom','serialeco','serialnet','videopenny','zalukajcom','cineto','ddl','cinemay','dpstreamingcx','planetstreamingcom',  \
                                                     'movizlandcom','bsto','altadefinizione','altadefinizione01','altadefinizione1','altadefinizionecool','tantifilmorg','filmezz','mooviecc','mozicsillag','mrpiracy','gamatotvme','oipeirates', \
                                                     'tainieskaiseirestv','andrijaiandjelka','pregledajnet','icefilmsinfo', 'appletrailers','cdapl','cimaclubcom','dardarkomcom', 'cb01', \
                                                     'filma24io','filmaoncom','filmehdnet','freediscpl','guardaserie','lookmovieag','tsiplayer'
                                                     ]
        self.PREDEFINED_HOSTS['cartoonsandanime'] = ['watchcartoononline','bajeczkiorg','animeodcinki','kreskowkazone','otakufr']
        self.PREDEFINED_HOSTS['sport']            = ['webstream','bbcsport','twitchtv','ourmatchnet','watchwrestling','watchwrestling','eurosportplayer','hoofootcom','ekstraklasatv','pmgsport','hitboxtv','meczykipl','del','redbull','laola1tv','ngolos', \
                                                     'okgoals','pinkbike','watchwrestlinguno','fullmatchtvcom']
        self.PREDEFINED_HOSTS['documentary']      = ['dailymotion','ororotv','dokumentalnenet','vumedicom','greekdocumentaries3','dsda']
        
        self.PREDEFINED_HOSTS['polish']           = ['favourites','webstream','localmedia','youtube','twitchtv','bajeczkiorg','allboxtv','efilmytv','ekinotv','kinox','ekstraklasahttps://www.facebook.com/groups/629673107501622/?ref=bookmarkstv','alltubetv','dokumentalnenet','filisertv','hitboxtv','iitvpl', \
                                                     'interiatv', 'kabarety', 'maxtvgo', 'meczykipl','ninateka','playpuls','serialeco','serialnet','spryciarze','tvgrypl','tvpvod','videopenny', 'vimeo','vodpl','joemonsterorg', 'tvproart', 'tvrepublika', \
                                                     'wgrane','zalukajcom','artetv','animeodcinki','cdapl','freediscpl','kreskowkazone','tvn24','tvnvod','wolnelekturypl','wpolscepl','wptv','wrealu24tv']
        
        self.PREDEFINED_HOSTS['english']          = ['favourites','youtube','musicbox','liveleak','twitchtv','hitboxtv','tvplayercom','bbciplayer','itvcom','lookmovieag', 'streamzennet','filmativa','filmovizijastudio','solarmovie','putlockertvto', \
                                                     'yifytv','icefilmsinfo','movierulzsx','streamzennet','forjatn','classiccinemaonline','seriesonline','mythewatchseries','thewatchseriesto','bbcsport','ourmatchnet','watchwrestling','watchwrestlinguno','hoofootcom','eurosportplayer','ngolos', \
                                                     'laola1tv','redbull','dailymotion','artetv','ted', 'pinkbike','watchcartoononline','orthobulletscom','vumedicom','ororotv','appletrailers','localmedia','webstream','tsiplayer','infoversion']
        
        self.PREDEFINED_HOSTS['german']           = ['filmpalast','hdfilmetv','kinox','serienstreamto', 'bsto','cineto','hdstreams','artetv', 'tvnowde','playrtsiw','ardmediathek','hitboxtv','sportdeutschland', 'twitchtv','zdfmediathek','youtube', \
                                                     'dailymotion','vimeo', 'vevo','webstream','favourites','localmedia','appletrailers', 'tsiplayer','infoversion']
        self.PREDEFINED_HOSTS['french']           = ['favourites','webstream','localmedia','youtube','twitchtv','dailymotion','vevo','tsiplayer','tfarjocom','hitboxtv', 'vimeo','artetv','cinemay','dpstreamingcx','librestream', \
                                                     'rtbfbe', 'otakufr','planetstreamingcom','playrtsiw', 'francetv','appletrailers','forjatn','infoversion']
        self.PREDEFINED_HOSTS['russian']          = ['kinogo','kinotan','hd1080online','sovdub', 'kinox', 'youtube', 'dailymotion', 'vimeo', 'vevo', 'twitchtv', 'hitboxtv', 'webstream', 'favourites', 'localmedia', 'appletrailers', 'tsiplayer', 'infoversion']
        self.PREDEFINED_HOSTS['hungarian']        = ['filmezz','mooviecc', 'mozicsillag', 'kinox', 'youtube', 'dailymotion', 'vimeo', 'vevo', 'webstream', 'favourites', 'localmedia', 'twitchtv', 'hitboxtv', 'appletrailers', 'tsiplayer', 'infoversion']
        self.PREDEFINED_HOSTS['arabic']           = ['tsiplayer','akoam','egybest','dardarkomcom','movs4ucom', 'movizlandcom','faselhdcom','arbcinema','forjatn','webstream','youtube', 'dailymotion','vimeo','vevo','localmedia','favourites', 'appletrailers','hitboxtv','twitchtv','infoversion']
        self.PREDEFINED_HOSTS['greek']            = ['tainieskaiseirestv','greekdocumentaries3', 'oipeirates', 'gamatotvme', 'youtube', 'dailymotion', 'vimeo', 'vevo', 'twitchtv', 'hitboxtv', 'webstream', 'localmedia', 'favourites', 'appletrailers', 'tsiplayer', 'infoversion']
        self.PREDEFINED_HOSTS['spanish']          = ['mrpiracy','plusdede','hdfull', 'vidcorncom', 'dixmax', 'seriesblanco', 'artetv', 'hitboxtv', 'twitchtv', 'youtube', 'vimeo', 'dailymotion', 'vevo', 'webstream', 'favourites', 'localmedia', 'tsiplayer', 'appletrailers', 'infoversion', 'sagasclasicas', \
                                                     'tdtiptvchannels','boxtvmania',]
        self.PREDEFINED_HOSTS['indian']           = ['movierulzsx','favourites','webstream', 'localmedia', 'youtube', 'dailymotion', 'vevo', 'twitchtv', 'hitboxtv', 'appletrailers', 'tsiplayer', 'infoversion']
        self.PREDEFINED_HOSTS['italian']          = ['altadefinizione01','altadefinizionecool', 'altadefinizione1', 'tantifilmorg', 'cb01', 'cb01uno', 'filmstreamhdit', 'guardaserie', 'dsda', 'playrtsiw', 'la7it', 'raiplay', 'artetv', 'dplayit', 'mediasetplay', 'pmgsport', \
                                                     'sportitalia','youtube','dailymotion','vimeo', 'vevo', 'twitchtv', 'hitboxtv', 'webstream', 'favourites', 'localmedia', 'tsiplayer', 'appletrailers', 'infoversion'
                                                     ]
        self.PREDEFINED_HOSTS['swedish']          = ['favourites','webstream','localmedia','youtube','dailymotion','vimeo','vevo','twitchtv','hitboxtv','appletrailers','tsiplayer','infoversion']
        self.PREDEFINED_HOSTS['balkans']          = ['fenixsite','gledalica','filma24io','andrijaiandjelka','filmehdnet','filmaoncom','filmovizijastudio','filmativa','filma24hdcom','kinox','youtube','dailymotion','vimeo','vevo','hitboxtv','twitchtv','webstream', \
                                                     'favourites','localmedia','appletrailers','tsiplayer','infoversion','filmowood']
        self.PREDEFINED_HOSTS['music']            = ['vevo','musicmp3ru','musicbox','shoutcast','youtube','dailymotion','vimeo','localmedia','favourites']      
        self.PREDEFINED_HOSTS['others']           = ['favourites','webstream','youtube','dailymotion','vimeo','localmedia', 'urllist', 'tsiplayer', 'liveleak', 'twitchtv', 'hitboxtv', 'spryciarze', 'wgrane', 'playrtsiw', 'cdapl', 'drdk', 'appletrailers', 'infoversion']
        self.PREDEFINED_HOSTS['live']=[]
        self.PREDEFINED_HOSTS['science']=[]
        self.LOADED_HOSTS = {}
        self.LOADED_DISABLED_HOSTS = {}
        self.CACHE_HOSTS = {}
        
        self.ADDED_HOSTS = {}

        
        self.hostListFromFolder = None
        self.hostListFromList = None

        self._setTsiplayerGroup()
        
    def _setTsiplayerGroup(self):
		folder='/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/tsiplayer' 
		if os.path.exists(folder):
			#add Tsiplayer group 
			self.PREDEFINED_GROUPS.append('tsiplayerc')
			self.PREDEFINED_HOSTS['tsiplayerc']=[]
			self.PREDEFINED_GROUPS_TITLES['tsiplayerc']='TSIPlayer'
			#add Tsiplayer hosts to groups
			self.PREDEFINED_HOSTS['others'].append('tsiplayer')
			self.PREDEFINED_HOSTS['tsiplayerc'].append('tsiplayer')
			lst=[] 
			lst=os.listdir(folder)
			lst.sort()
			for (file_) in lst:
				if (file_.endswith('.py'))and(file_.startswith('host_')):
					try:
						hst_titre=file_.replace('.py','')
						_temp = __import__('Plugins.Extensions.IPTVPlayer.tsiplayer.'+hst_titre, globals(), locals(), ['getinfo'], -1)
						inf=_temp.getinfo()
						cat_= inf.get('cat_id','0')
						if (cat_!='104')and(cat_!='102'):
							self.PREDEFINED_HOSTS['tsiplayerc'].append(hst_titre.replace('host_','TS_')) 
						if (cat_=='202')or(cat_=='203')or(cat_=='302')or(cat_=='303')or(cat_=='402')or(cat_=='403'):
							self.PREDEFINED_HOSTS['cartoonsandanime'].append(hst_titre.replace('host_','TS_'))
						if (cat_=='201')or(cat_=='301')or(cat_=='401')or(cat_=='101'):
							self.PREDEFINED_HOSTS['moviesandseries'].append(hst_titre.replace('host_','TS_'))
						if (cat_=='401')or(cat_=='402')or(cat_=='403')or(cat_=='101'):
							self.PREDEFINED_HOSTS['english'].append(hst_titre.replace('host_','TS_'))
						if (cat_=='301')or(cat_=='302')or(cat_=='403')or(cat_=='101'):
							self.PREDEFINED_HOSTS['french'].append(hst_titre.replace('host_','TS_'))                    
						if (cat_=='201')or(cat_=='202')or(cat_=='203')or(cat_=='204')or(cat_=='101'):
							self.PREDEFINED_HOSTS['arabic'].append(hst_titre.replace('host_','TS_'))                    
						if (cat_=='100')or(cat_=='110'):
							self.PREDEFINED_HOSTS['sport'].append(hst_titre.replace('host_','TS_'))                     
						if (cat_=='100')or(cat_=='120'):
							self.PREDEFINED_HOSTS['live'].append(hst_titre.replace('host_','TS_')) 
					except:
						pass                    
			#add Tsmedia group
			folder='/usr/lib/enigma2/python/Plugins/Extensions/TSmedia/addons'
			if os.path.exists(folder):
				self.PREDEFINED_GROUPS.append('tsmedia')           
				self.PREDEFINED_HOSTS['tsmedia']=[]
				self.PREDEFINED_GROUPS_TITLES['tsmedia']='TSMedia'
				printDBG('Start Get Tsmedia Hosts')
				lst=[]
				lst=os.listdir(folder)
				for (dir_) in lst:
					try:
						if ('.py' not in dir_)and('youtube' not in dir_)and('programs' not in dir_)and('favorites' not in dir_):
							folder2=folder+'/'+dir_
							lst2=[]
							lst2=os.listdir(folder2)
							for (dir_2) in lst2:
								try:
									if ('.py' not in dir_2):
										hst_titre='TSM_'+dir_+'__'+dir_2
										self.PREDEFINED_HOSTS['tsmedia'].append(hst_titre)				    
										if (dir_=='arabic')      : self.PREDEFINED_HOSTS['arabic'].append(hst_titre)	
										elif (dir_=='sport')     : self.PREDEFINED_HOSTS['sport'].append(hst_titre)	        
										elif (dir_=='french')    : self.PREDEFINED_HOSTS['french'].append(hst_titre)	
										elif (dir_=='kids')      : self.PREDEFINED_HOSTS['cartoonsandanime'].append(hst_titre)	
										elif (dir_=='movies')    : 
											self.PREDEFINED_HOSTS['moviesandseries'].append(hst_titre)
											self.PREDEFINED_HOSTS['english'].append(hst_titre)	
										elif (dir_=='iptv')      : self.PREDEFINED_HOSTS['live'].append(hst_titre)
										elif (dir_=='radio')     : self.PREDEFINED_HOSTS['live'].append(hst_titre)
										elif (dir_=='netmedia')  : self.PREDEFINED_HOSTS['live'].append(hst_titre)
										elif (dir_=='science')   : self.PREDEFINED_HOSTS['science'].append(hst_titre)										
										elif (dir_=='music')     : self.PREDEFINED_HOSTS['music'].append(hst_titre)										                        
										else: self.PREDEFINED_HOSTS['others'].append(hst_titre) 
								except: pass
					except: pass                
                                                   
    def _getGroupFile(self, groupName):
        printDBG("IPTVHostsGroups._getGroupFile")
        return GetConfigDir("iptvplayer%sgroup.json" % groupName)
        
    def getLastError(self):
        return self.lastError
        
    def addHostToGroup(self, groupName, hostName):
        printDBG("IPTVHostsGroups.addHostToGroup")
        hostsList = self.getHostsList(groupName)
        self.ADDED_HOSTS[groupName] = []
        if hostName in hostsList or hostName in self.ADDED_HOSTS[groupName]:
            self.lastError = _('This host has been added already to this group.')
            return False
        self.ADDED_HOSTS[groupName].append(hostName)
        return True
        
    def flushAddedHosts(self):
        printDBG("IPTVHostsGroups.flushAddedHosts")
        for groupName in self.ADDED_HOSTS:
            if 0 == len(self.ADDED_HOSTS[groupName]): continue
            newList = list(self.CACHE_HOSTS[groupName])
            newList.extend(self.ADDED_HOSTS[groupName])
            self.setHostsList(groupName, newList)
        self.ADDED_HOSTS = {}
        
    def getGroupsWithoutHost(self, hostName):
        groupList = self.getGroupsList()
        retList = []
        for groupItem in groupList:
            hostsList = self.getHostsList(groupItem.name)
            if hostName not in hostsList and hostName not in self.ADDED_HOSTS.get(groupItem.name, []):
                retList.append(groupItem)
        return retList
        
    def getHostsList(self, groupName):
        printDBG("IPTVHostsGroups.getHostsList")
        if groupName in self.CACHE_HOSTS:
            return self.CACHE_HOSTS[groupName]
    
        if self.hostListFromFolder == None:
            self.hostListFromFolder = GetHostsList(fromList=False, fromHostFolder=True)
        if self.hostListFromList == None: 
            self.hostListFromList = GetHostsList(fromList=True, fromHostFolder=False)
        
        groupFile = self._getGroupFile(groupName)
        self._loadHosts(groupFile, groupName, self.hostListFromFolder, self.hostListFromFolder)
        
        hosts = []
        for host in self.LOADED_HOSTS[groupName]:
            if IsHostEnabled(host):
                hosts.append(host)
        
        for host in self.PREDEFINED_HOSTS.get(groupName, []):
            if host not in hosts and host not in self.LOADED_DISABLED_HOSTS[groupName] and host in self.hostListFromFolder and IsHostEnabled(host):
                hosts.append(host)
        
        printDBG('Group Hosts = '+str(hosts))
        
        
                
        self.CACHE_HOSTS[groupName] = hosts
        return hosts
        
    def setHostsList(self, groupName, hostsList):
        printDBG("IPTVHostsGroups.setHostsList groupName[%s], hostsList[%s]" % (groupName, hostsList))
        # hostsList - must be updated with host which were not disabled in this group but they are not 
        # available or they are disabled globally
        outObj = {"version":0, "hosts":hostsList, "disabled_hosts":[]}
        
        #check if some host from diabled one has been enabled
        disabledHosts = []
        for host in self.LOADED_DISABLED_HOSTS[groupName]:
            if host not in hostsList:
                disabledHosts.append(host)
        
        # check if some host has been disabled
        for host in self.CACHE_HOSTS[groupName]:
            if host not in hostsList and host in self.PREDEFINED_HOSTS.get(groupName, []):
                disabledHosts.append(host)
        
        outObj['disabled_hosts'] = disabledHosts
        
        self.LOADED_DISABLED_HOSTS[groupName] = disabledHosts
        self.CACHE_HOSTS[groupName] = hostsList
        
        groupFile = self._getGroupFile(groupName)
        return self._saveHosts(outObj, groupFile)
        
    def _saveHosts(self, outObj, groupFile):
        printDBG("IPTVHostsGroups._saveHosts")
        ret = True
        try:
            data = json_dumps(outObj)
            self._saveToFile(groupFile, data)
        except Exception:
            printExc()
            self.lastError = _("Error writing file \"%s\".\n") % self.GROUPS_FILE
            ret = False
        return ret
        
    def _loadHosts(self, groupFile, groupName, hostListFromFolder, hostListFromList):
        printDBG("IPTVHostsGroups._loadHosts groupName[%s]" % groupName)
        predefinedHosts = self.PREDEFINED_HOSTS.get(groupName, [])
        hosts = []
        disabledHosts = []
        printDBG('All Host = '+str(hostListFromFolder))
        ret = True
        if os_path.isfile(groupFile):
            try:
                data = self._loadFromFile(groupFile)
                data = json_loads(data) 
                for item in data.get('disabled_hosts', []):
                    # we need only information about predefined hosts which were disabled
                    if item in predefinedHosts and item in hostListFromList:
                        disabledHosts.append(str(item))
                
                for item in data.get('hosts', []):
                    if item in hostListFromFolder:
                        hosts.append(item)
            except Exception:
                printExc()
        printDBG('Host from File'+str(hosts))
        self.LOADED_HOSTS[groupName] = hosts
        self.LOADED_DISABLED_HOSTS[groupName] = disabledHosts
        printDBG('self.LOADED_HOSTS = '+str(hosts))
        
    def getGroupsList(self):
        printDBG("IPTVHostsGroups.getGroupsList")
        if self.CACHE_GROUPS != None:
            return self.CACHE_GROUPS
        self._loadGroups()
        groups = list(self.LOADED_GROUPS)
        
        for group in self.PREDEFINED_GROUPS:
            if group not in self.LOADED_GROUPS and group not in self.LOADED_DISABLED_GROUPS:
                groups.append(group)
        
        groupList = []
        for group in groups:
            title = self.PREDEFINED_GROUPS_TITLES.get(group, '')
            if title == '': title = self.LOADED_GROUPS_TITLES.get(group, '')
            if title == '': title = group.title()
            item = CHostsGroupItem(group, _(title))
            groupList.append(item)
        self.CACHE_GROUPS = groupList
        return groupList
        
    def getPredefinedGroupsList(self):
        printDBG("IPTVHostsGroups.getPredefinedGroupsList")
        groupList = []
        for group in self.PREDEFINED_GROUPS: 
            title = self.PREDEFINED_GROUPS_TITLES[group]
            item = CHostsGroupItem(group, title)
            groupList.append(item)
        return groupList
        
    def setGroupList(self, groupList):
        printDBG("IPTVHostsGroups.setGroupList groupList[%s]" % groupList)
        # update disabled groups
        outObj = {"version":0, "groups":[], "disabled_groups":[]}
        
        for group in self.PREDEFINED_GROUPS:
            if group not in groupList:
                outObj['disabled_groups'].append(group)
        
        for group in groupList:
            outObj['groups'].append({'name':group})
            if group in self.LOADED_GROUPS_TITLES:
                outObj['groups']['title'] = self.LOADED_GROUPS_TITLES[group]
                
        return self._saveGroups(outObj)
        
    def _saveGroups(self, outObj):
        printDBG("IPTVHostsGroups._saveGroups")
        ret = True
        try:
            data = json_dumps(outObj)
            self._saveToFile(self.GROUPS_FILE, data)
        except Exception:
            printExc()
            self.lastError = _("Error writing file \"%s\".\n") % self.GROUPS_FILE
            ret = False
        return ret
        
    def _loadGroups(self):
        printDBG("IPTVHostsGroups._loadGroups")
        self.LOADED_GROUPS = []
        self.LOADED_DISABLED_GROUPS = []
        self.LOADED_GROUPS_TITLES = {}
        
        groups = []
        titles = {}
        disabledGroups = []
        
        ret = True
        if os_path.isfile(self.GROUPS_FILE):
            try:
                data = self._loadFromFile(self.GROUPS_FILE)
                data = json_loads(data)
                for item in data.get('disabled_groups', []):
                    # we need only information about predefined groups which were disabled
                    if item in self.PREDEFINED_GROUPS:
                        disabledGroups.append(str(item))
                
                for item in data.get('groups', []):
                    name = str(item['name'])
                    groups.append(name)
                    if 'title' in item: titles[name] = str(item['title'])
            except Exception:
                printExc()
        
        self.LOADED_GROUPS = groups
        self.LOADED_DISABLED_GROUPS = disabledGroups 
        self.LOADED_GROUPS_TITLES = titles
        
    def _saveToFile(self, filePath, data, encoding='utf-8'):
        printDBG("IPTVHostsGroups._saveToFile filePath[%s]" % filePath)
        with codecs.open(filePath, 'w', encoding, 'replace') as fp:
            fp.write(data)
            
    def _loadFromFile(self, filePath, encoding='utf-8'):
        printDBG("IPTVHostsGroups._loadFromFile filePath[%s]" % filePath)
        with codecs.open(filePath, 'r', encoding, 'replace') as fp:
            return fp.read()
        
        
