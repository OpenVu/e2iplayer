# -*- coding: utf-8 -*-

#
#
# @Codermik release, based on @Samsamsam's E2iPlayer public.
# Released with kind permission of Samsamsam.
# All code developed by Samsamsam is the property of the Samsamsam and the E2iPlayer project,  
# all other work is ï¿½ E2iStream Team, aka Codermik.  TSiPlayer is ï¿½ Rgysoft, his group can be
# found here:  https://www.facebook.com/E2TSIPlayer/
#
# https://www.facebook.com/e2iStream/
#
#

from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, MergeDicts
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs.e2ijson import loads as json_loads
from Plugins.Extensions.IPTVPlayer.libs import ph

import re

def gettytul():
    return 'https://www.tfarjo.cc/'

class TfarjoCom(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history': 'tfarjo.com', 'cookie': 'tfarjo.com.cookie'})
        self.USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        self.MAIN_URL = 'https://www.tfarjo.cc/'
        self.DEFAULT_ICON_URL = 'https://www.tfarjo.cc/assets/theme/img/tfarjo-logo.png'
        self.HTTP_HEADER = {'User-Agent': self.USER_AGENT, 'DNT': '1', 'Accept': 'text/html', 'Accept-Encoding': 'gzip, deflate', 'Referer': self.getMainUrl(), 'Origin': self.getMainUrl()}
        self.AJAX_HEADER = dict(self.HTTP_HEADER)
        self.AJAX_HEADER.update({'X-Requested-With': 'XMLHttpRequest', 'Accept-Encoding': 'gzip, deflate', 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'Accept': 'application/json, text/javascript, */*; q=0.01'})
        self.cacheLinks = {}
        self.defaultParams = {'header': self.HTTP_HEADER, 'with_metadata': True, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE}
        self.cacheSeriesLetter = []
        self.cacheSetiesByLetter = {}
        self.cacheFilters = {}
        self.cacheFiltersKeys = []

    def getPage(self, baseUrl, addParams={}, post_data=None):
        if addParams == {}:
            addParams = dict(self.defaultParams)
        origBaseUrl = baseUrl
        baseUrl = self.cm.iriToUri(baseUrl)
        addParams['cloudflare_params'] = {'cookie_file': self.COOKIE_FILE, 'User-Agent': self.USER_AGENT}
        return self.cm.getPageCFProtection(baseUrl, addParams, post_data)

    def getFullIconUrl(self, url, cUrl=None):
        url = CBaseHostClass.getFullIconUrl(self, url.strip(), cUrl)
        if url == '':
            return ''
        cookieHeader = self.cm.getCookieHeader(self.COOKIE_FILE, domain=self.cm.getBaseUrl(url, domainOnly=True))
        return strwithmeta(url, {'Cookie': cookieHeader, 'User-Agent': self.USER_AGENT})

    def getDefaulIcon(self, cItem=None):
        return self.getFullIconUrl(self.DEFAULT_ICON_URL)

    def listMainMenu(self, cItem):
        printDBG('InteriaTv.listMainMenu')
        sts, data = self.getPage(self.getMainUrl())
        if not sts:
            return
        self.setMainUrl(data.meta['url'])
        MAIN_CAT_TAB = [{'category': 'movies', 'title': 'Films', 'url': self.getFullUrl('/films')}, {'category': 'list_items', 'title': 'Series', 'url': self.getFullUrl('/series')}, {'category': 'search', 'title': _('Search'), 'search_item': True}, {'category': 'search_history', 'title': _('Search history')}]
        self.listsTab(MAIN_CAT_TAB, cItem)

    def listMovies(self, cItem, nextCategory1, nextCategory2):
        printDBG('TfarjoCom.listMovies')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        self.setMainUrl(data.meta['url'])
        params = dict(cItem)
        params.update({'category': nextCategory2, 'title': _('--All--')})
        self.addDir(params)
        data = ph.find(data, ('<div', '>', 'buttons_filtre'), ('<div', '>', 'row'))[1]
        filters = ph.findall(data, '<button', '</button>')
        for filter in filters:
            fTitle = ph.clean_html(filter)
            fMarker = ph.search(filter, 'onclick=[\'"]([^"^\']+?)[\'"]')[0].replace('()', '')
            subItems = []
            tmp = ph.find(data, ('<p', '>', fMarker), '</p>', flags=0)[1]
            tmp = ph.findall(tmp, ('<a', '>'), '</a>', flags=ph.START_S)
            for idx in range(1, len(tmp), 2):
                url = self.getFullUrl(ph.getattr(tmp[(idx - 1)], 'href'))
                title = ph.clean_html(tmp[idx])
                if not title:
                    continue
                params = {'category': nextCategory2, 'title': title, 'url': url}
                subItems.append(params)

            if len(subItems):
                self.addDir({'category': nextCategory1, 'title': fTitle, 'sub_items': subItems})

    def listSeries(self, cItem, nextCategory):
        printDBG('TfarjoCom.listSeries [%s]' % cItem)
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        self.setMainUrl(data.meta['url'])
        self.addDir(MergeDicts(cItem, {'category': nextCategory, 'title': _('--All--')}))
        tmp = ph.find(data, ('<h4', '</h4>', 'Voir SÃ©ries'), ('<li', '>', 'genre'))[1]
        tmp = ph.findall(tmp, ('<a', '>'), '</a>', flags=ph.START_S)
        for idx in range(1, len(tmp), 2):
            url = self.getFullUrl(ph.getattr(tmp[(idx - 1)], 'href'))
            title = ph.clean_html(tmp[idx])
            if not title:
                continue
            self.addDir(MergeDicts(cItem, {'category': nextCategory, 'title': title, 'url': url}))

    def listSubItems(self, cItem):
        printDBG('TfarjoCom.listSubItems')
        subList = cItem['sub_items']
        for item in subList:
            self.currList.append(MergeDicts({'name': 'category', 'type': 'category'}, item))

    def listItems(self, cItem, nextCategory, data=None):
        printDBG('InteriaTv.listItems')
        page = cItem.get('page', 1)
        if data == None:
            sts, data = self.getPage(cItem['url'])
            if not sts:
                return
            self.setMainUrl(data.meta['url'])
        nextPage = ph.find(data, ('<ul', '>', 'pagination'), '</ul>', flags=0)[1]
        nextPage = self.getFullUrl(ph.search(nextPage, ('<a[^>]+?href=[\'"]([^"^\']+?)[\'"][^>]*?>\\s*?{0}\\s*?<').format(page + 1))[0])
        data = ph.find(data, ('<ul', '>', 'icon'), '</ul>', flags=0)[1]
        data = ph.findall(data, ('<li', '>'), '</li>', flags=0)
        for item in data:
            url = self.getFullUrl(ph.search(item, ph.A)[1])
            icon = self.getFullIconUrl(ph.search(item, ph.IMG)[1])
            title = ph.clean_html(ph.find(item, ('<p', '>'), '</p>', flags=0)[1])
            desc = []
            item = ph.findall(item, '<span', '</span>')
            for t in item:
                if 'VO' in t:
                    desc.append('VO')
                if 'VF' in t:
                    desc.append('VF')
                t = ph.clean_html(t)
                if t != '':
                    desc.append(t)
            self.addDir({'good_for_fav': True, 'priv_has_art': True, 'category': nextCategory, 'url': url, 'title': title, 'desc': (' | ').join(desc), 'icon': icon})

        if nextPage:
            self.addDir(MergeDicts(cItem, {'title': _('Next page'), 'url': nextPage, 'page': page + 1}))
        return

    def listSearchResult(self, cItem, searchPattern, searchType):
        printDBG('TfarjoCom.listSearchResult cItem[%s], searchPattern[%s] searchType[%s]' % (cItem, searchPattern, searchType))
        sts, data = self.getPage(self.getMainUrl())
        if not sts:
            return
        cUrl = data.meta['url']
        self.setMainUrl(cUrl)
        actionUrl, post_data = self.cm.getFormData(ph.find(data, ('<form', '>', 'form-user'), '</form>')[1], cUrl, {'search': searchPattern}, {'view': 'list'})
        if not actionUrl:
            return
        paramsUrl = dict(self.defaultParams)
        paramsUrl['header'] = dict(self.AJAX_HEADER)
        paramsUrl['header']['Referer'] = cUrl
        sts, data = self.getPage(actionUrl, paramsUrl, post_data)
        if not sts:
            return
        printDBG(data)
        try:
            data = json_loads(data, '', True)
            for item in data['data']['user']:
                if not isinstance(item, dict):
                    continue
                url = self.getFullUrl(item['url'])
                icon = self.getFullIconUrl(item.get('avatar', ''))
                title = '%s %s' % (item['name'], item['year'])
                params = {'good_for_fav': True, 'priv_has_art': True, 'category': 'explore_item', 'url': url, 'title': title, 'desc': '', 'icon': icon}
                self.addDir(params)
        except Exception:
            printExc()

    def exploreItem(self, cItem, nextCategory):
        printDBG('InteriaTv.listItems')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        cUrl = data.meta['url']
        if '/serie/' in cUrl and '/saison' in cUrl:
            cUrl = cUrl.split('/saison-', 1)[0]
            sts, data = self.getPage(cUrl)
            if not sts:
                return
            cUrl = data.meta['url']
        self.setMainUrl(cUrl)
        tmp = ph.find(data, ('<div', '>', 'bdetail'), ('<div', '>', 'col-md'), flags=0)[1]
        iTitle = ph.clean_html(ph.find(tmp, ('<h1', '>'), '</h1>', flags=0)[1])
        tmp = ph.find(tmp, ('<div', '>', 'dmovie'), '</div>', flags=0)[1]
        iIcon = self.getFullIconUrl(ph.search(tmp, ph.IMG)[1])
        iTrailer = self.getFullUrl(ph.search(tmp, ph.IFRAME)[1])
        if '/film/' in cUrl:
            if '"players' in data or "'players" in data:
                params = dict(cItem)
                params.update({'priv_has_art': True})
                self.addVideo(params)
        else:
            data = ph.find(data, ('<div', '>', 'panel-heading'), ('<footer', '>'), flags=0)[1]
            data = ph.rfindall(data, '</div>', ('<div', '>', 'col-md'))
            for season in data:
                sTitle = ph.clean_html(ph.find(season, ('<h', '>', 'panel-title'), ('</h',
                                                                                    '>'), flags=0)[1])
                printDBG('<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< %s' % sTitle)
                sUrl = self.getFullUrl(ph.search(season, ph.A)[1])
                season = ph.findall(season, ('<div', '>', 'panel-body'), '</div>', flags=0)
                episodesTab = []
                for item in season:
                    url = self.getFullUrl(ph.search(item, ph.A)[1])
                    title = ph.clean_html(ph.find(item, ('<a', '>'), '</a>', flags=0)[1])
                    desc = ph.clean_html(ph.find(item, ('<span', '>', 'ddcheck'), '</span>', flags=0)[1])
                    params = {'good_for_fav': True, 'priv_has_art': True, 'url': url, 'title': '%s - %s' % (iTitle, title), 'desc': desc, 'icon': iIcon}
                    if 'glyphicon-time' in item:
                        params['type'] = 'article'
                    else:
                        params['type'] = 'video'
                    episodesTab.append(params)

                if len(episodesTab):
                    params = {'good_for_fav': False, 'priv_has_art': True, 'category': nextCategory, 'title': sTitle, 'url': sUrl, 'sub_items': episodesTab, 'desc': '', 'icon': iIcon}
                    self.addDir(params)

        if iTrailer != '':
            params = {'good_for_fav': False, 'url': iTrailer, 'title': '%s - %s' % (iTitle, _('trailer')), 'icon': iIcon}
            self.addVideo(params)

    def getLinksForVideo(self, cItem):
        printDBG('TfarjoCom.getLinksForVideo [%s]' % cItem)
        if 1 == self.up.checkHostSupport(cItem.get('url', '')):
            videoUrl = cItem['url'].replace('youtu.be/', 'youtube.com/watch?v=')
            return self.up.getVideoLinkExt(videoUrl)
        cacheKey = cItem['url']
        cacheTab = self.cacheLinks.get(cacheKey, [])
        if len(cacheTab):
            return cacheTab
        self.cacheLinks = {}
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        cUrl = data.meta['url']
        self.setMainUrl(cUrl)
        tmp = ph.find(data, 'function getIframe', '</script>')[1]
        linkUrl = self.getFullUrl(ph.search(tmp, '[\'"]?url[\'"]?\\s*?:\\s*?[\'"]([^\'^"]+?)[\'"]')[0])
        if '/film/' in cUrl:
            itemType = 'movie'
        else:
            itemType = 'episode'
        linkTest = ph.search(data, '[\'"]?csrf_test_name[\'"]?\\s*?:\\s*?[\'"]([^\'^"]+?)[\'"]')[0]
        retTab = []
        data = re.sub('<!--[\\s\\S]*?-->', '', data)
        data = ph.findall(data, ('<button', '>', 'getIframe'), ('</button', '>'))
        for item in data:
            name = ph.clean_html(item)
            verType = ph.search(item, 'class=[\'"]players([^\'^"]+?)[\'"]')[0].upper()
            linkData = ph.find(item, 'getIframe(', ')', False)[1].strip()[1:-1]
            url = linkUrl + '#' + linkData
            retTab.append({'name': '[%s] %s' % (verType, name), 'url': strwithmeta(url, {'Referer': cUrl, 'iptv_link_data': linkData, 'iptv_link_test': linkTest, 'iptv_link_type': itemType}), 'need_resolve': 1})

        if retTab:
            self.cacheLinks[cacheKey] = retTab
        return retTab

    def markSelectedLink(self, cacheLinks, linkId, keyId='url', marker="*"):
        # mark requested link as used one
        if len(cacheLinks.keys()):
            for key in cacheLinks:
                for idx in range(len(cacheLinks[key])):
                    if linkId in cacheLinks[key][idx][keyId]:
                        if not cacheLinks[key][idx]['name'].startswith(marker):
                            cacheLinks[key][idx]['name'] = marker + cacheLinks[key][idx]['name'] + marker
                        break

    def getVideoLinks(self, baseUrl):
        printDBG('TfarjoCom.getVideoLinks [%s]' % baseUrl)
        baseUrl = strwithmeta(baseUrl)
        urlTab = []
        
        self.markSelectedLink(self.cacheLinks, baseUrl)

        paramsUrl = dict(self.defaultParams)
        paramsUrl['header'] = dict(self.AJAX_HEADER)
        paramsUrl['header']['Referer'] = baseUrl.meta['Referer']
        post_data = {'csrf_test_name': baseUrl.meta['iptv_link_test'], baseUrl.meta['iptv_link_type']: baseUrl.meta['iptv_link_data']}
        sts, data = self.getPage(baseUrl.split('#', 1)[0], paramsUrl, post_data)
        if not sts:
            return
        cUrl = self.cm.meta['url']
        printDBG(data)
        try:
            data = json_loads(data, '', True)
            data = data['iframe']
            videoUrl = self.getFullUrl(ph.search(data, ph.IFRAME)[1], cUrl)
            urlTab = self.up.getVideoLinkExt(videoUrl)
        except Exception:
            printExc()
        return urlTab

    def getArticleContent(self, cItem):
        printDBG('TfarjoCom.getArticleContent [%s]' % cItem)
        retTab = []
        otherInfo = {}
        url = cItem['url']
        url = url.split('/saison-', 1)[0]
        sts, data = self.getPage(url)
        if not sts:
            return []
        cUrl = data.meta['url']
        self.setMainUrl(cUrl)
        data = ph.find(data, ('<div', '>', 'bdetail'), ('<script ', '>'))[1]
        title = ph.clean_html(ph.find(data, ('<h1', '>'), '</h1>', flags=0)[1])
        icon = ph.find(data, ('<div', '>', 'dmovie'), '</div>', flags=0)[1]
        icon = self.getFullIconUrl(ph.search(icon, ph.IMG)[1])
        desc = ph.clean_html(ph.find(data, ('<p', '>', 'vtext'), '</p>')[1])
        keysMap = {'genre:': 'genre', 'imdb:': 'imdb_rating', 
           'durÃ©e:': 'duration', 
           'crÃ©Ã©e par:': 'writer', 
           'acteurs:': 'actors', 
           'annÃ©e de production:': 'year', 
           'date de production:': 'production', 
           'qualitÃ©:': 'quality', 
           'langue:': 'language'}
        tmp = ph.findall(data, ('<h5', '>'), '</h5>')
        reObj = re.compile('<span[^>]*?>')
        printDBG(tmp)
        for item in tmp:
            item = reObj.split(item, 1)
            val = ph.clean_html(item[(-1)]).replace(' ,', ',')
            if val == '' or val.lower() == 'n/a':
                continue
            key = ph.clean_html(item[0]).decode('utf-8').lower().encode('utf-8')
            if key not in keysMap:
                continue
            otherInfo[keysMap[key]] = val
        if title == '':
            title = cItem['title']
        if icon == '':
            icon = cItem.get('icon', self.DEFAULT_ICON_URL)
        return [{'title': ph.clean_html(title), 'text': ph.clean_html(desc), 'images': [{'title': '', 'url': self.getFullUrl(icon)}], 'other_info': otherInfo}]

    def handleService(self, index, refresh=0, searchPattern='', searchType=''):
        printDBG('handleService start')
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        name = self.currItem.get('name', '')
        category = self.currItem.get('category', '')
        mode = self.currItem.get('mode', '')
        printDBG('handleService: |||| name[%s], category[%s] ' % (name, category))
        self.cacheLinks = {}
        self.currList = []
        if name == None and category == '':
            self.cm.clearCookie(self.COOKIE_FILE, ['PHPSESSID', '__cfduid', 'cf_clearance'])
            self.listMainMenu({'name': 'category'})
        elif category == 'movies':
            self.listMovies(self.currItem, 'sub_items', 'list_items')
        elif category == 'series':
            self.listSeries(self.currItem, 'list_items')
        elif category == 'sub_items':
            self.listSubItems(self.currItem)
        elif category == 'list_items':
            self.listItems(self.currItem, 'explore_item')
        elif category == 'explore_item':
            self.exploreItem(self.currItem, 'sub_items')
        elif category in ('search', 'search_next_page'):
            cItem = dict(self.currItem)
            cItem.update({'search_item': False, 'name': 'category'})
            self.listSearchResult(cItem, searchPattern, searchType)
        elif category == 'search_history':
            self.listsHistory({'name': 'history', 'category': 'search'}, 'desc', _('Type: '))
        else:
            printExc()
        CBaseHostClass.endHandleService(self, index, refresh)
        return


class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, TfarjoCom(), True, [])

    def withArticleContent(self, cItem):
        if cItem.get('priv_has_art', False):
            return True
        return False


