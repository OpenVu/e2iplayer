# -*- coding: utf-8 -*-

#
#
# @Codermik release, based on @Samsamsam's E2iPlayer public.
# Released with kind permission of Samsamsam.
# All code developed by Samsamsam is the property of the Samsamsam and the E2iPlayer project,  
# all other work is ? E2iStream Team, aka Codermik.  TSiPlayer is ? Rgysoft, his group can be
# found here:  https://www.facebook.com/E2TSIPlayer/
#
# https://www.facebook.com/e2iStream/
#
#

from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass, CDisplayListItem
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, MergeDicts
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import getDirectM3U8Playlist
from Plugins.Extensions.IPTVPlayer.libs import ph
from Plugins.Extensions.IPTVPlayer.libs.e2ijson import loads as json_loads
import re
import urllib
from Components.config import config

def gettytul():
    return 'http://ourmatch.net/'


class OurmatchNet(CBaseHostClass):
    HEADER = {'User-Agent': 'Mozilla/5.0',
     'Accept': 'text/html'}
    AJAX_HEADER = dict(HEADER)
    AJAX_HEADER.update({'X-Requested-With': 'XMLHttpRequest'})
    MAIN_URL = 'http://ourmatch.net/'
    DEFAULT_ICON = 'http://ourmatch.net/wp-content/themes/OurMatch/images/logo.png'
    MAIN_CAT_TAB = [{'category': 'list_items',
      'title': _('Home'),
      'url': MAIN_URL,
      'icon': DEFAULT_ICON},
     {'category': 'trending',
      'title': _('Trending'),
      'url': MAIN_URL,
      'icon': DEFAULT_ICON},
     {'category': 'popular',
      'title': _('Popular'),
      'url': MAIN_URL,
      'icon': DEFAULT_ICON},
     {'category': 'allleagues',
      'title': _('All Leagues'),
      'url': MAIN_URL,
      'icon': DEFAULT_ICON},
     {'category': 'seasons',
      'title': _('Previous Seasons'),
      'url': MAIN_URL + 'previous-seasons/',
      'icon': DEFAULT_ICON},
     {'category': 'video',
      'title': _('Goal Of The Month'),
      'url': MAIN_URL + 'goal-of-the-month/',
      'icon': DEFAULT_ICON},
     {'category': 'search',
      'title': _('Search'),
      'search_item': True,
      'icon': DEFAULT_ICON},
     {'category': 'search_history',
      'title': _('Search history'),
      'icon': DEFAULT_ICON}]

    def __init__(self):
        CBaseHostClass.__init__(self, {'history': 'ourmatch.net',
         'cookie': 'ourmatchnet.cookie'})
        self.defaultParams = {'use_cookie': True,
         'load_cookie': True,
         'save_cookie': True,
         'cookiefile': self.COOKIE_FILE}
        self.cache = {'popular': [],
         'trending': [],
         'allleagues': []}
        self.cache2 = {}

    def fillCache(self, cItem):
        printDBG('OurmatchNet.fillCache [%s]' % cItem)
        self.cache = {'popular': [],
         'trending': [],
         'allleagues': []}
        sts, data = self.cm.getPage(cItem['url'])
        if not sts:
            return
        for marker in [('<li class="popular-leagues-list">', '</ul>', 'popular'), ('<li class="trending-competitions">', '</ul>', 'trending')]:
            tmp = self.cm.ph.getDataBeetwenMarkers(data, marker[0], marker[1])[1]
            tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<li ', '</li>')
            for item in tmp:
                url = self.cm.ph.getSearchGroups(item, 'href=[\'"](http[^\'^"]+?)[\'"]')[0]
                if '' == url:
                    continue
                title = ph.clean_html(item)
                self.cache[marker[2]].append({'title': title,
                 'url': url})

        tmp = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li class="header">', '</ul>')
        for division in tmp:
            division = division.split('<ul class="regions">')
            if 2 != len(division):
                continue
            divisionTitle = ph.clean_html(division[0])
            regionsTab = []
            regions = self.cm.ph.getAllItemsBeetwenMarkers(division[1], '<li ', '</li>')
            for region in regions:
                url = self.cm.ph.getSearchGroups(region, 'href=[\'"](http[^\'^"]+?)[\'"]')[0]
                if '' == url:
                    continue
                title = ph.clean_html(region)
                regionsTab.append({'title': title,
                 'url': url})

            if len(regionsTab):
                self.cache['allleagues'].append({'title': divisionTitle,
                 'regions_tab': regionsTab})

    def listPopulars(self, cItem, category):
        printDBG('OurmatchNet.listPopulars [%s]' % cItem)
        tab = self.cache.get('popular', [])
        if 0 == len(tab):
            self.fillCache(cItem)
        tab = self.cache.get('popular', [])
        params = dict(cItem)
        params['category'] = category
        self.listsTab(tab, params)

    def listTrending(self, cItem):
        printDBG('OurmatchNet.listTrending [%s]' % cItem)
        tab = self.cache.get('trending', [])
        if 0 == len(tab):
            self.fillCache(cItem)
        tab = self.cache.get('trending', [])
        params = dict(cItem)
        self.listsTab(tab, params, 'video')

    def listLeagues(self, cItem, category):
        printDBG('OurmatchNet.listLeagues [%s]' % cItem)
        tab = self.cache.get('allleagues', [])
        if 0 == len(tab):
            self.fillCache(cItem)
        tab = self.cache.get('allleagues', [])
        for idx in range(len(tab)):
            item = tab[idx]
            params = dict(cItem)
            params.update({'category': category,
             'title': item['title'],
             'idx': idx})
            self.addDir(params)

    def listLeagueItems(self, cItem, category):
        printDBG('OurmatchNet.listLeadItems [%s]' % cItem)
        idx = cItem['idx']
        tab = self.cache['allleagues'][idx]['regions_tab']
        params = dict(cItem)
        params['category'] = category
        self.listsTab(tab, params)

    def listYersTabs(self, cItem, category):
        printDBG('OurmatchNet.listYersTabs [%s]' % cItem)
        self.cache2 = {}
        sts, data = self.cm.getPage(cItem['url'])
        if not sts:
            return
        data = self.cm.ph.getDataBeetwenMarkers(data, '<div id="tabs_container">', '<div class="widget">')[1]
        tmp = self.cm.ph.getDataBeetwenMarkers(data, '<ul id="tabs">', '</ul>')[1]
        tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<a ', '</a>')
        tabs = []
        for tab in tmp:
            tabId = self.cm.ph.getSearchGroups(tab, 'href=[\'"]#([^\'^"]+?)[\'"]')[0]
            tabTitle = ph.clean_html(tab)
            tabs.append({'title': tabTitle,
             'id': tabId})

        data = data.split('<div class="tab_content" ')
        if len(data):
            del data[0]
        if len(data) != len(tabs):
            return
        for idx in range(len(data)):
            tab = tabs[idx]
            divisionsTab = []
            divisions = self.cm.ph.getAllItemsBeetwenMarkers(data[idx], '<li class="header">', '</ul>')
            for division in divisions:
                divisionsTitle = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(division, '<li class="header">', '</li>')[1])
                regionsTab = []
                regions = re.compile('<a[^>]+?href="([^"]+?)"[^>]*?>([^<]+?)</a>').findall(division)
                for item in regions:
                    regionsTab.append({'title': ph.clean_html(item[1]),
                     'url': self.getFullUrl(item[0])})

                if len(regionsTab):
                    divisionsTab.append({'title': divisionsTitle,
                     'regions_tab': regionsTab})

            if len(divisionsTab):
                self.cache2[tab['id']] = divisionsTab
                params = dict(cItem)
                params.update({'category': category,
                 'title': tab['title'],
                 'tab': tab['id']})
                self.addDir(params)

    def listLeagues2(self, cItem, category):
        printDBG('OurmatchNet.listLeagues2 [%s]' % cItem)
        tab = self.cache2.get(cItem['tab'], [])
        for idx in range(len(tab)):
            item = tab[idx]
            params = dict(cItem)
            params.update({'category': category,
             'title': item['title'],
             'idx': idx})
            self.addDir(params)

    def listLeagueItems2(self, cItem, category):
        printDBG('OurmatchNet.listLeadItems2 [%s]' % cItem)
        tab = self.cache2[cItem['tab']][cItem['idx']]['regions_tab']
        params = dict(cItem)
        params['category'] = category
        self.listsTab(tab, params)

    def listItems(self, cItem):
        printDBG('OurmatchNet.listItems [%s]' % cItem)
        page = cItem.get('page', 1)
        url = cItem['url']
        if page > 1:
            url += 'page/%d/' % page
        if 's' in cItem:
            url += '?s=' + cItem['s']
        sts, data = self.cm.getPage(url)
        if not sts:
            return
        cUrl = self.cm.meta['url']
        nextPage = True if '/page/%d/' % (page + 1) in data else False
        sp = '<div class="vidthumb">'
        data = ph.find(data, sp, '<footer id="footer">')[1]
        data = data.split(sp)
        for item in data:
            url = self.getFullUrl(ph.search(item, ph.A)[1], cUrl)
            if not url:
                continue
            icon = self.getFullIconUrl(ph.search(item, ph.IMG)[1], cUrl)
            title = ph.clean_html(ph.getattr(item, 'title'))
            desc = ph.clean_html(ph.find(item, ('<div', '>', 'vidinfo'), '</div>', flags=0)[1])
            self.addVideo(MergeDicts(cItem, {'title': title,
             'url': url,
             'icon': icon,
             'desc': desc}))

        if nextPage:
            self.addDir(MergeDicts(cItem, {'title': _('Next page'),
             'page': page + 1}))

    def getLinksForVideo(self, cItem):
        printDBG('OurmatchNet.getLinksForVideo [%s]' % cItem)
        urlTab = []
        sts, data = self.cm.getPage(cItem['url'])
        if not sts:
            return []
        cUrl = self.cm.meta['url']
        tmp = ph.findall(data, '<li data-pos="top" ', '</li>')
        for item in tmp:
            name = ph.clean_html(item)
            url = ph.find(item, 'data-config=&quot;', '&quot;', flags=0)[1]
            if url:
                urlTab.append({'name': name,
                 'url': self.getFullUrl(url, cUrl),
                 'need_resolve': 1})

        videoContents = ph.find(data, 'var video_contents', '</script>', flags=0)[1]
        tmp = ph.findall(videoContents, '{embed:', '}')
        for item in tmp:
            nameTab = []
            for key in ['lang',
             'type',
             'qualty',
             'source']:
                name = ph.search(item, '[\'"]?%s[\'"]?:[\'"]([^\'^"]+?)[\'"]' % key)[0]
                if name != '':
                    nameTab.append(name)

            needResolve = 1
            url = self.getFullUrl(ph.search(item, ph.IFRAME)[1], cUrl)
            if not url:
                url = ph.find(item, ('<a', '>', 'watch?v='), '</a>', flags=ph.START_E | ph.I)[1]
                url = self.getFullUrl(ph.search(url, ph.A)[1], cUrl)
            if not url:
                url = ph.find(item, '<source', '>', flags=ph.I)[1]
                url = self.getFullUrl(ph.getattr(url, 'src'), cUrl)
                needResolve = 0
            if url:
                urlTab.append({'name': ' '.join(nameTab),
                 'url': url,
                 'need_resolve': needResolve})

        tmp = self.cm.ph.getDataBeetwenMarkers(data, '<div id="details" class="section-box">', '</div>', False)[1]
        tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<p>', '</p>')
        for item in tmp:
            name = ph.clean_html(item)
            url = self.cm.ph.getDataBeetwenMarkers(item, 'data-config="', '"', False)[1]
            if url == '':
                url = self.cm.ph.getSearchGroups(item, '<iframe[^>]+?src="([^"]+?)"', 1, ignoreCase=True)[0]
            url = self.getFullUrl(url)
            if not url.startswith('http'):
                continue
            urlTab.append({'name': name,
             'url': url,
             'need_resolve': 1})

        if 0 == len(urlTab):
            tmp = self.cm.ph.getAllItemsBeetwenMarkers(data, '//config.playwire.com/', '.json')
            for item in tmp:
                name = 'playwire.com'
                urlTab.append({'name': name,
                 'url': self.getFullUrl(item),
                 'need_resolve': 1})

        if 0 == len(urlTab):
            data = re.compile('<iframe[^>]+?src="([^"]+?)"', re.IGNORECASE).findall(data)
            for link in data:
                link = self.getFullUrl(link)
                if 'facebook' in link:
                    continue
                if 'twitter.' in link:
                    continue
                if 1 != self.up.checkHostSupport(link):
                    continue
                name = self.up.getHostName(link, True)
                urlTab.append({'name': name,
                 'url': link,
                 'need_resolve': 1})

        return urlTab

    def getVideoLinks(self, videoUrl):
        printDBG('OurmatchNet.getVideoLinks [%s]' % videoUrl)
        urlTab = []
        if 'playwire.com' in videoUrl:
            sts, data = self.cm.getPage(videoUrl)
            if not sts:
                return []
            try:
                data = json_loads(data)
                if 'content' in data:
                    url = data['content']['media']['f4m']
                else:
                    url = data['src']
                sts, data = self.cm.getPage(url)
                baseUrl = self.cm.ph.getDataBeetwenMarkers(data, '<baseURL>', '</baseURL>', False)[1].strip()
                data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<media ', '>')
                for item in data:
                    url = self.cm.ph.getSearchGroups(item, 'url=[\'"]([^\'^"]+?)[\'"]')[0]
                    name = self.cm.ph.getSearchGroups(item, 'height=[\'"]([^\'^"]+?)[\'"]')[0]
                    if name == '':
                        self.cm.ph.getSearchGroups(item, 'bitrate=[\'"]([^\'^"]+?)[\'"]')[0]
                    if not url.startswith('http'):
                        url = baseUrl + '/' + url
                    if url.startswith('http'):
                        if 'm3u8' in url:
                            hlsTab = getDirectM3U8Playlist(url)
                            urlTab.extend(hlsTab)
                        else:
                            urlTab.append({'name': name,
                             'url': url})

            except Exception:
                printExc()

        elif videoUrl.startswith('http'):
            urlTab.extend(self.up.getVideoLinkExt(videoUrl))
        return urlTab

    def listSearchResult(self, cItem, searchPattern, searchType):
        printDBG('OurmatchNet.listSearchResult cItem[%s], searchPattern[%s] searchType[%s]' % (cItem, searchPattern, searchType))
        cItem = dict(cItem)
        cItem.update({'url': self.MAIN_URL,
         's': urllib.quote(searchPattern)})
        self.listItems(cItem)

    def getFavouriteData(self, cItem):
        return cItem['url']

    def getLinksForFavourite(self, fav_data):
        return self.getLinksForVideo({'url': fav_data})

    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        name = self.currItem.get('name', '')
        category = self.currItem.get('category', '')
        mode = self.currItem.get('mode', '')
        printDBG('handleService: |||||||||||||||||||||||||||||||||||| name[%s], category[%s] ' % (name, category))
        self.currList = []
        if name == None:
            self.listsTab(self.MAIN_CAT_TAB, {'name': 'category'})
        elif category == 'trending':
            self.listTrending(self.currItem)
        elif category == 'popular':
            self.listPopulars(self.currItem, 'list_items')
        elif category == 'allleagues':
            self.listLeagues(self.currItem, 'list_league')
        elif category == 'list_league':
            self.listLeagueItems(self.currItem, 'list_items')
        elif category == 'seasons':
            self.listYersTabs(self.currItem, 'allleagues2')
        elif category == 'allleagues2':
            self.listLeagues2(self.currItem, 'list_league2')
        elif category == 'list_league2':
            self.listLeagueItems2(self.currItem, 'list_items')
        elif category == 'list_items':
            self.listItems(self.currItem)
        elif category in ('search', 'search_next_page'):
            cItem = dict(self.currItem)
            cItem.update({'search_item': False,
             'name': 'category'})
            self.listSearchResult(cItem, searchPattern, searchType)
        elif category == 'search_history':
            self.listsHistory({'name': 'history',
             'category': 'search'}, 'desc', _('Type: '))
        else:
            printExc()
        CBaseHostClass.endHandleService(self, index, refresh)
        return


class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, OurmatchNet(), True, favouriteTypes=[CDisplayListItem.TYPE_VIDEO, CDisplayListItem.TYPE_AUDIO])