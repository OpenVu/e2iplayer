from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass, CDisplayListItem, RetHost, CUrlItem
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, GetLogoDir
from Plugins.Extensions.IPTVPlayer.tools.iptvfilehost import IPTVFileHost
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import getDirectM3U8Playlist, getF4MLinksWithMeta, getMPDLinksWithMeta
from Plugins.Extensions.IPTVPlayer.libs.urlparser import urlparser
from Plugins.Extensions.IPTVPlayer.libs import ph
from Components.config import config, ConfigYesNo, ConfigDirectory, getConfigListEntry
from os.path import normpath
config.plugins.iptvplayer.Sciezkaurllist = ConfigDirectory(default='/usr/lib/enigma2/python/Plugins/Extensions/IPTVPlayer/iptvurl/')
config.plugins.iptvplayer.grupujurllist = ConfigYesNo(default=True)
config.plugins.iptvplayer.sortuj = ConfigYesNo(default=True)

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry(_('Text files ytlist and urllist are in:'), config.plugins.iptvplayer.Sciezkaurllist))
    optionList.append(getConfigListEntry(_('Sort the list:'), config.plugins.iptvplayer.sortuj))
    optionList.append(getConfigListEntry(_('Group links into categories: '), config.plugins.iptvplayer.grupujurllist))
    return optionList


def gettytul():
    return _('Sagas Clasicas')

class Urllist(CBaseHostClass):
    URLLIST_FILE = 'urllist.estrenos'
    URRLIST_STREAMS = 'urllist.saga'
    URRLIST_USER = 'urllist.disney'
    URRLIST_IPTV = 'urllist.clemente'
    URRLIST_ANIME = 'urllist.anime'
    URRLIST_CINE4K = 'urllist.cine4k'
    URRLIST_SERIECOLOMBO = 'urllist.seriecolombo'
    URRLIST_NETFLIX = 'urllist.netflix'
    URRLIST_CULTO = 'urllist.culto'
    URRLIST_MARVEL = 'urllist.marvel'
    URRLIST_BOND = 'urllist.bond'

    def __init__(self):
        printDBG('Urllist.__init__')
        path = config.plugins.iptvplayer.Sciezkaurllist.value + '/'

#       self.MAIN_GROUPED_TAB = [{'category': 'all',
#         'title': _('All in one'),
#         'desc': _('Links from all files without categories'),
#         'icon': 'https://mikeharwood.files.wordpress.com/2011/01/all-in-one-logo-on-blue.jpg'}]
        self.MAIN_GROUPED_TAB = ([{'category': Urllist.URLLIST_FILE,
          'title': _('Cine Estrenos'),
          'desc': _('Links from the file %s') % normpath(path + 'urllist.estrenos'),
          'icon': 'http://elrinconenigma2.hol.es/E2iplayericons/cineestrenos.jpg'}, {'category': Urllist.URRLIST_STREAMS,
          'title': _('Sagas Clasicas'),
          'desc': _('Links from the file %s') % normpath(path + 'urllist.saga'),
          'icon': 'http://elrinconenigma2.hol.es/E2iplayericons/sagasclasicas135.png'}, {'category': Urllist.URRLIST_USER,
          'title': _('Clasicos Disney'),
          'desc': _('Links from the file %s') % normpath(path + 'urllist.disney'),
          'icon': 'http://elrinconenigma2.hol.es/E2iplayericons/Disney_logo.jpg'}, {'category': Urllist.URRLIST_IPTV,
          'title': _('Clasicos Adultos'),
          'desc': _('Links from the file %s') % normpath(path + 'urllist.clemente'),
          'icon': 'http://elrinconenigma2.hol.es/E2iplayericons/sca.jpg'}, {'category': Urllist.URRLIST_ANIME,
          'title': _('Peliculas Anime'),
          'desc': _('Links from the file %s') % normpath(path + 'urllist.anime'),
          'icon': 'http://elrinconenigma2.hol.es/E2iplayericons/anime.jpg'}, {'category': Urllist.URRLIST_CINE4K,
          'title': _('Cine Mejor Calidad (FHD&4K)'),
          'desc': _('Links from the file %s') % normpath(path + 'urllist.cine4k'),
          'icon': 'http://elrinconenigma2.hol.es/E2iplayericons/sagasclasicas135.png'}, {'category': Urllist.URRLIST_SERIECOLOMBO,
          'title': _('Serie Colombo (Tributo al Maestro)'),
          'desc': _('Links from the file %s') % normpath(path + 'urllist.seriecolombo'),
          'icon': 'http://elrinconenigma2.hol.es/E2iplayericons/sagasclasicas135.png'}, {'category': Urllist.URRLIST_NETFLIX,
          'title': _('Cine Netflix Hbo y Amazon Prime'),
          'desc': _('Links from the file %s') % normpath(path + 'urllist.netflix'),
          'icon': 'http://elrinconenigma2.hol.es/E2iplayericons/sagasclasicas135.png'}, {'category': Urllist.URRLIST_CULTO,
          'title': _('Cine De Culto'),
          'desc': _('Links from the file %s') % normpath(path + 'urllist.culto'),
          'icon': 'http://elrinconenigma2.hol.es/E2iplayericons/sagasclasicas135.png'}, {'category': Urllist.URRLIST_MARVEL,
          'title': _('Saga Peliculas Marvel (EL INFINITO)'),
          'desc': _('Links from the file %s') % normpath(path + 'urllist.marvel'),
          'icon': 'http://elrinconenigma2.hol.es/E2iplayericons/sagasclasicas135.png'}, {'category': Urllist.URRLIST_BOND,
          'title': _('Saga James Bond 007'),
          'desc': _('Links from the file %s') % normpath(path + 'urllist.bond'),
          'icon': 'http://elrinconenigma2.hol.es/E2iplayericons/sagasclasicas135.png'}])

        CBaseHostClass.__init__(self)
        self.currFileHost = None
        return

    def _getHostingName(self, url):
        if 0 != self.up.checkHostSupport(url):
            return self.up.getHostName(url)
        elif self._uriIsValid(url):
            return _('direct link')
        else:
            return _('unknown')

    def _uriIsValid(self, url):
        return '://' in url

    def listCategory(self, cItem, searchMode = False):
        printDBG('Urllist.listCategory cItem[%s]' % cItem)
        sortList = config.plugins.iptvplayer.sortuj.value
        filespath = config.plugins.iptvplayer.Sciezkaurllist.value
        groupList = config.plugins.iptvplayer.grupujurllist.value
        if cItem['category'] in ['all',
         Urllist.URLLIST_FILE,
         Urllist.URRLIST_STREAMS,
         Urllist.URRLIST_USER,
         Urllist.URRLIST_IPTV,
         Urllist.URRLIST_ANIME,
         Urllist.URRLIST_CINE4K,
         Urllist.URRLIST_SERIECOLOMBO,
         Urllist.URRLIST_NETFLIX,
         Urllist.URRLIST_CULTO,
         Urllist.URRLIST_MARVEL,
         Urllist.URRLIST_BOND]:
            self.currFileHost = IPTVFileHost()
            if cItem['category'] in ['all', Urllist.URLLIST_FILE]:
                self.currFileHost.addFile(filespath + Urllist.URLLIST_FILE, encoding='utf-8')
            if cItem['category'] in ['all', Urllist.URRLIST_STREAMS]:
                self.currFileHost.addFile(filespath + Urllist.URRLIST_STREAMS, encoding='utf-8')
            if cItem['category'] in ['all', Urllist.URRLIST_USER]:
                self.currFileHost.addFile(filespath + Urllist.URRLIST_USER, encoding='utf-8')
            if cItem['category'] in ['all', Urllist.URRLIST_IPTV]:
                self.currFileHost.addFile(filespath + Urllist.URRLIST_IPTV, encoding='utf-8')
            if cItem['category'] in ['all', Urllist.URRLIST_ANIME]:
                self.currFileHost.addFile(filespath + Urllist.URRLIST_ANIME, encoding='utf-8')
            if cItem['category'] in ['all', Urllist.URRLIST_CINE4K]:
                self.currFileHost.addFile(filespath + Urllist.URRLIST_CINE4K, encoding='utf-8')
            if cItem['category'] in ['all', Urllist.URRLIST_SERIECOLOMBO]:
                self.currFileHost.addFile(filespath + Urllist.URRLIST_SERIECOLOMBO, encoding='utf-8')
            if cItem['category'] in ['all', Urllist.URRLIST_NETFLIX]:
                self.currFileHost.addFile(filespath + Urllist.URRLIST_NETFLIX, encoding='utf-8')
            if cItem['category'] in ['all', Urllist.URRLIST_CULTO]:
                self.currFileHost.addFile(filespath + Urllist.URRLIST_CULTO, encoding='utf-8')
            if cItem['category'] in ['all', Urllist.URRLIST_MARVEL]:
                self.currFileHost.addFile(filespath + Urllist.URRLIST_MARVEL, encoding='utf-8')
            if cItem['category'] in ['all', Urllist.URRLIST_BOND]:
                self.currFileHost.addFile(filespath + Urllist.URRLIST_BOND, encoding='utf-8')
            if 'all' != cItem['category'] and groupList:
                tmpList = self.currFileHost.getGroups(sortList)
                for item in tmpList:
                    if '' == item:
                        title = _('COLOMBO TEAM')
                    else:
                        title = item
                    params = {'name': 'category',
                     'category': 'group',
                     'title': title,
                     'group': item}
                    self.addDir(params)

            else:
                tmpList = self.currFileHost.getAllItems(sortList)
                for item in tmpList:
                    desc = _('Hosting: %s, Teamcolombo') % (self._getHostingName(item['url']))
                    if item['desc'] != '':
                        desc = item['desc']
                    params = {'title': item['full_title'],
                     'url': item['url'],
                     'desc': desc,
                     'icon': item['icon']}
                    self.addVideo(params)

        elif 'group' in cItem:
            tmpList = self.currFileHost.getItemsInGroup(cItem['group'], sortList)
            for item in tmpList:
                if '' == item['title_in_group']:
                    title = item['full_title']
                else:
                    title = item['title_in_group']
                desc = _('Hosting: %s, ColomboTeam') % (self._getHostingName(item['url']))
                if item.get('desc', '') != '':
                    desc = item['desc']
                params = {'title': title,
                 'url': item['url'],
                 'desc': desc,
                 'icon': item.get('icon', '')}
                self.addVideo(params)

    def getLinksForVideo(self, cItem):
        printDBG('Urllist.getLinksForVideo url[%s]' % cItem['url'])
        videoUrls = []
        uri = urlparser.decorateParamsFromUrl(cItem['url'])
        protocol = uri.meta.get('iptv_proto', '')
        printDBG('PROTOCOL [%s] ' % protocol)
        urlSupport = self.up.checkHostSupport(uri)
        if 1 == urlSupport:
            retTab = self.up.getVideoLinkExt(uri)
            videoUrls.extend(retTab)
        elif 0 == urlSupport and self._uriIsValid(uri):
            if protocol == 'm3u8':
                retTab = getDirectM3U8Playlist(uri, checkExt=False, checkContent=True)
                videoUrls.extend(retTab)
            elif protocol == 'f4m':
                retTab = getF4MLinksWithMeta(uri)
                videoUrls.extend(retTab)
            elif protocol == 'mpd':
                retTab = getMPDLinksWithMeta(uri, False)
                videoUrls.extend(retTab)
            else:
                videoUrls.append({'name': 'direct link',
                 'url': uri})
        return videoUrls

    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('Urllist.handleService start')
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        name = self.currItem.get('name', None)
        category = self.currItem.get('category', '')
        printDBG('Urllist.handleService: ---------> name[%s], category[%s] ' % (name, category))
        self.currList = []
        if None == name:
            self.listsTab(self.MAIN_GROUPED_TAB, self.currItem)
        else:
            self.listCategory(self.currItem)
        CBaseHostClass.endHandleService(self, index, refresh)
        return


class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, Urllist(), True)

    def _isPicture(self, url):

        def _checkExtension(url):
            return url.endswith('.jpeg') or url.endswith('.jpg') or url.endswith('.png')

        if _checkExtension(url):
            return True
        if _checkExtension(url.split('|')[0]):
            return True
        if _checkExtension(url.split('?')[0]):
            return True
        return False

    def getLogoPath(self):
        return RetHost(RetHost.OK, value=[GetLogoDir('sagasclasicaslogo.png')])

    def getLinksForVideo(self, Index = 0, selItem = None):
        listLen = len(self.host.currList)
        if listLen < Index and listLen > 0:
            printDBG('ERROR getLinksForVideo - current list is to short len: %d, Index: %d' % (listLen, Index))
            return RetHost(RetHost.ERROR, value=[])
        if self.host.currList[Index]['type'] != 'video':
            printDBG('ERROR getLinksForVideo - current item has wrong type')
            return RetHost(RetHost.ERROR, value=[])
        retlist = []
        uri = self.host.currList[Index].get('url', '')
        if not self._isPicture(uri):
            urlList = self.host.getLinksForVideo(self.host.currList[Index])
            for item in urlList:
                retlist.append(CUrlItem(item['name'], item['url'], 0))

        else:
            retlist.append(CUrlItem('picture link', urlparser.decorateParamsFromUrl(uri, True), 0))
        return RetHost(RetHost.OK, value=retlist)

    def convertList(self, cList):
        hostList = []
        searchTypesOptions = []
        for cItem in cList:
            hostLinks = []
            type = CDisplayListItem.TYPE_UNKNOWN
            possibleTypesOfSearch = None
            if cItem['type'] == 'category':
                if cItem['title'] == 'Wyszukaj':
                    type = CDisplayListItem.TYPE_SEARCH
                    possibleTypesOfSearch = searchTypesOptions
                else:
                    type = CDisplayListItem.TYPE_CATEGORY
            elif cItem['type'] == 'video':
                type = CDisplayListItem.TYPE_VIDEO
                url = cItem.get('url', '')
                if self._isPicture(url):
                    type = CDisplayListItem.TYPE_PICTURE
                else:
                    type = CDisplayListItem.TYPE_VIDEO
                if '' != url:
                    hostLinks.append(CUrlItem('Link', url, 1))
            title = cItem.get('title', '')
            description = ph.clean_html(cItem.get('desc', ''))
            icon = cItem.get('icon', '')
            hostItem = CDisplayListItem(name=title, description=description, type=type, urlItems=hostLinks, urlSeparateRequest=1, iconimage=icon, possibleTypesOfSearch=possibleTypesOfSearch)
            hostList.append(hostItem)

        return hostList

    def getSearchItemInx(self):
        try:
            list = self.host.getCurrList()
            for i in range(len(list)):
                if list[i]['category'] == 'Wyszukaj':
                    return i

        except Exception:
            printDBG('getSearchItemInx EXCEPTION')
            return -1

    def setSearchPattern(self):
        try:
            list = self.host.getCurrList()
            if 'history' == list[self.currIndex]['name']:
                pattern = list[self.currIndex]['title']
                search_type = list[self.currIndex]['search_type']
                self.host.history.addHistoryItem(pattern, search_type)
                self.searchPattern = pattern
                self.searchType = search_type
        except Exception:
            printDBG('setSearchPattern EXCEPTION')
            self.searchPattern = ''
            self.searchType = ''
