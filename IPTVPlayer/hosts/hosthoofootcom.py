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
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc
from Plugins.Extensions.IPTVPlayer.libs import ph
import re

def gettytul():
    return 'https://hoofoot.com/'


class HoofootCom(CBaseHostClass):
    HEADER = {'User-Agent': 'Mozilla/5.0',
     'Accept': 'text/html'}
    AJAX_HEADER = dict(HEADER)
    AJAX_HEADER.update({'X-Requested-With': 'XMLHttpRequest'})
    MAIN_URL = 'https://hoofoot.com/'
    DEFAULT_ICON_URL = 'https://th.hoofoot.com/pics/default.jpg'
    MAIN_CAT_TAB = [{'category': 'list_cats',
      'title': _('Main'),
      'url': MAIN_URL},
     {'category': 'list_cats2',
      'title': _('Popular'),
      'url': MAIN_URL},
     {'category': 'list_cats3',
      'title': _('Promoted'),
      'url': MAIN_URL},
     {'category': 'search',
      'title': _('Search'),
      'search_item': True},
     {'category': 'search_history',
      'title': _('Search history')}]

    def __init__(self):
        CBaseHostClass.__init__(self, {'history': 'hoofoot.com',
         'cookie': 'hoofootcom.cookie'})
        self.defaultParams = {'use_cookie': True,
         'load_cookie': True,
         'save_cookie': True,
         'cookiefile': self.COOKIE_FILE}
        self.cache = []

    def listCats(self, cItem, category):
        printDBG('HoofootCom.listCats [%s]' % cItem)
        self.cache = []
        sts, data = self.cm.getPage(cItem['url'])
        if not sts:
            return
        sp = re.compile('<li[^>]+?class=[\'"]has-sub[^>]+?>')
        tmp = self.cm.ph.getDataBeetwenReMarkers(data, sp, re.compile('Community'), False)[1]
        tmp = sp.split(tmp)
        for item in tmp:
            item = item.split('<ul')
            catTitle = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(item[0], '<a ', '</a>')[1])
            catUrl = self.cm.ph.getSearchGroups(item[0], 'href=[\'"]([^\'^"]+?)[\'"]')[0]
            catTab = []
            if 2 == len(item):
                catData = self.cm.ph.getAllItemsBeetwenMarkers(item[1], '<li>', '</li>')
                for catItem in catData:
                    url = self.cm.ph.getSearchGroups(catItem, 'href=[\'"]([^\'^"]+?)[\'"]')[0]
                    if '' == url:
                        continue
                    title = ph.clean_html(catItem)
                    catTab.append({'title': title,
                     'url': self.getFullUrl(url)})

            params = dict(cItem)
            params['title'] = catTitle
            if len(catTab):
                params.update({'category': category,
                 'idx': len(self.cache)})
                self.cache.append(catTab)
                self.addDir(params)
            elif catUrl != '#' and catUrl != '':
                params.update({'category': 'list_items',
                 'url': self.getFullUrl(catUrl)})
                self.addDir(params)

    def listCats2(self, cItem, category):
        printDBG('HoofootCom.listCats2 [%s]' % cItem)
        sts, data = self.cm.getPage(cItem['url'])
        if not sts:
            return
        data = self.cm.ph.getDataBeetwenMarkers(data, '<ul id="menu">', '</ul>', False)[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li>', '</li>')
        for catItem in data:
            url = self.cm.ph.getSearchGroups(catItem, 'href=[\'"]([^\'^"]+?)[\'"]')[0]
            if '' == url:
                continue
            title = ph.clean_html(catItem)
            params = dict(cItem)
            params.update({'category': category,
             'title': title,
             'url': self.getFullUrl(url)})
            self.addDir(params)

    def listCats3(self, cItem, category):
        printDBG('HoofootCom.listCats3 [%s]' % cItem)
        sts, data = self.cm.getPage(cItem['url'])
        if not sts:
            return
        titlesMap = {}
        tmp = self.cm.ph.getDataBeetwenMarkers(data, '<div id="star"', '<div id="club">')[1]
        tmp = re.compile('<div[^>]+?id=[\'"]([^\'^"]+?)[\'"][^>]*?>([^<]+?)<').findall(tmp)
        for item in tmp:
            titlesMap[item[0]] = ph.clean_html(item[1])

        data = self.cm.ph.getDataBeetwenMarkers(data, '<div id="club">', '</div>', False)[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a ', '</a>')
        for catItem in data:
            ff = self.cm.ph.getSearchGroups(catItem, 'mostrar\\([\'"]([^\'^"]+?)[\'"]\\)')[0]
            if '' == ff:
                continue
            title = titlesMap.get(ff, '')
            if title == '':
                title = ph.clean_html(self.cm.ph.getSearchGroups(catItem, 'alt=[\'"]([^\'^"]+?)[\'"]')[0])
            icon = self.cm.ph.getSearchGroups(catItem, 'src=[\'"]([^\'^"]+?)[\'"]')[0]
            params = dict(cItem)
            params.update({'category': category,
             'title': title,
             'ff': ff,
             'url': self.getFullUrl('/pagerg.php'),
             'icon': self.getFullUrl(icon)})
            self.addDir(params)

    def listSubCats(self, cItem, category):
        printDBG('HoofootCom.listSubCats [%s]' % cItem)
        tab = self.cache[cItem['idx']]
        for idx in range(len(tab)):
            item = tab[idx]
            params = dict(cItem)
            params.update({'category': category,
             'title': item['title'],
             'url': item['url']})
            self.addDir(params)

    def _urlAppendPage(self, url, page, ff):
        if ff == '':
            post_data = None
        else:
            post_data = {'ff': '%s' % ff}
        if page > 1:
            if ff == '':
                if '?' in url:
                    url += '&'
                else:
                    url += '?'
                url += 'page=%d' % page
            else:
                post_data = {'ff': '%s,%d' % (ff, page)}
        return (post_data, url)

    def listItems(self, cItem):
        printDBG('HoofootCom.listItems [%s]' % cItem)
        page = cItem.get('page', 1)
        ff = cItem.get('ff', '')
        post_data, url = self._urlAppendPage(cItem['url'], page, ff)
        sts, data = self.cm.getPage(url, {}, post_data)
        if not sts:
            return
        hasItems = False
        data = self.cm.ph.getAllItemsBeetwenNodes(data, ('<table>', '<tr>'), ('<div id="port"', '>'))
        for item in data:
            url = self.cm.ph.getSearchGroups(item, 'href=[\'"]([^\'^"]+?)[\'"]')[0]
            if '' == url:
                continue
            icon = self.cm.ph.getSearchGroups(item, 'src=[\'"]([^\'^"^>]+?\\.jpg)[\'"]')[0]
            title = ph.clean_html(self.cm.ph.getSearchGroups(item, 'alt=[\'"]([^\'^"]+?)[\'"]')[0])
            if title == '':
                title = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(item, '<h2 ', '</h2>')[1])
            desc = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(item, 'class="info">', '</div>', False)[1])
            params = dict(cItem)
            params.update({'title': title,
             'url': self.getFullUrl(url),
             'icon': icon,
             'desc': desc})
            self.addVideo(params)
            hasItems = True

        if hasItems:
            post_data, url = self._urlAppendPage(cItem['url'], page + 1, ff)
            sts, data = self.cm.getPage(url, {}, post_data)
            if not sts:
                return
            if '<div id="port"' in data:
                params = dict(cItem)
                params.update({'title': _('Next page'),
                 'page': page + 1})
                self.addDir(params)

    def getLinksForVideo(self, cItem):
        printDBG('HoofootCom.getLinksForVideo [%s]' % cItem)
        urlTab = []
        sts, data = self.cm.getPage(cItem['url'])
        if not sts:
            return urlTab
        tmpTab = []
        tmp = ph.find(data, 'Alternatives', '</div>', flags=0)[1]
        tmp = ph.findall(tmp, '<a ', '</a>')
        for item in tmp:
            name = ph.clean_html(item)
            if 'focusd' in item:
                url = cItem['url']
            else:
                url = ph.search(item, "rruta\\('([0-9,]+?)'\\)")[0]
            if url == '':
                continue
            urlTab.append({'name': name,
             'url': url,
             'need_resolve': 1})

        return urlTab

    def getVideoLinks(self, videoUrl):
        printDBG('HoofootCom.getVideoLinks [%s]' % videoUrl)
        urlTab = []
        post_data = None
        if not self.cm.isValidUrl(videoUrl):
            post_data = {'rr': videoUrl}
            videoUrl = self.getFullUrl('videosx.php')
        sts, data = self.cm.getPage(videoUrl, {}, post_data)
        if not sts:
            return []
        else:
            cUrl = self.cm.meta['url']
            printDBG(data)
            data = ph.find(data, ('<div', '>', 'player'), '</div>', flags=0)[1]
            videoUrl = self.cm.getFullUrl(ph.search(data, ph.IFRAME)[1], cUrl)
            if videoUrl:
                urlTab.extend(self.up.getVideoLinkExt(videoUrl))
            return urlTab

    def listSearchResult(self, cItem, searchPattern, searchType):
        printDBG('HoofootCom.listSearchResult cItem[%s], searchPattern[%s] searchType[%s]' % (cItem, searchPattern, searchType))
        cItem = dict(cItem)
        cItem.update({'ff': searchPattern,
         'url': self.getFullUrl('/pagerg.php')})
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
        printDBG('handleService: || name[%s], category[%s] ' % (name, category))
        self.currList = []
        if name == None:
            self.listsTab(self.MAIN_CAT_TAB, {'name': 'category'})
        elif category == 'list_cats':
            self.listCats(self.currItem, 'list_sub_cats')
        elif category == 'list_cats2':
            self.listCats2(self.currItem, 'list_items')
        elif category == 'list_cats3':
            self.listCats3(self.currItem, 'list_items')
        elif category == 'list_sub_cats':
            self.listSubCats(self.currItem, 'list_items')
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
        CHostBase.__init__(self, HoofootCom(), True, favouriteTypes=[CDisplayListItem.TYPE_VIDEO, CDisplayListItem.TYPE_AUDIO])