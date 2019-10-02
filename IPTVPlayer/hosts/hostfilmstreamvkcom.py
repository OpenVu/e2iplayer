# Embedded file name: /IPTVPlayer/hosts/hostfilmstreamvkcom.py
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, MergeDicts
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs import ph
import re
import urllib
from Components.config import config, ConfigSelection, ConfigText, getConfigListEntry
config.plugins.iptvplayer.filmstreamvk_proxy = ConfigSelection(default='None', choices=[('None', _('None')), ('proxy_1', _('Alternative proxy server (1)')), ('proxy_2', _('Alternative proxy server (2)'))])
config.plugins.iptvplayer.filmstreamvk_alt_domain = ConfigText(default='', fixed_size=False)

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry(_('Use proxy server:'), config.plugins.iptvplayer.filmstreamvk_proxy))
    if config.plugins.iptvplayer.filmstreamvk_proxy.value == 'None':
        optionList.append(getConfigListEntry(_('Alternative domain:'), config.plugins.iptvplayer.filmstreamvk_alt_domain))
    return optionList


def gettytul():
    return 'https://filmstreamvf.com/'


class FilmstreamvkCom(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history': 'filmstreamvk.com',
         'cookie': 'filmstreamvkcom.cookie'})
        self.HTTP_HEADER = self.cm.getDefaultHeader('chrome')
        self.DEFAULT_ICON_URL = 'https://image2.owler.com/4364858-1514556867755.png'
        self.MAIN_URL = None
        self.defaultParams = {'header': self.HTTP_HEADER,
         'use_cookie': True,
         'load_cookie': True,
         'save_cookie': True,
         'cookiefile': self.COOKIE_FILE}
        return

    def getPage(self, baseUrl, addParams = {}, post_data = None):
        if addParams == {}:
            addParams = dict(self.defaultParams)
        proxy = config.plugins.iptvplayer.filmstreamvk_proxy.value
        if proxy != 'None':
            if proxy == 'proxy_1':
                proxy = config.plugins.iptvplayer.alternative_proxy1.value
            else:
                proxy = config.plugins.iptvplayer.alternative_proxy2.value
            addParams = dict(addParams)
            addParams.update({'http_proxy': proxy})
        return self.cm.getPage(baseUrl, addParams, post_data)

    def getFullIconUrl(self, url):
        url = self.getFullUrl(url)
        proxy = config.plugins.iptvplayer.filmstreamvk_proxy.value
        if proxy != 'None':
            if proxy == 'proxy_1':
                proxy = config.plugins.iptvplayer.alternative_proxy1.value
            else:
                proxy = config.plugins.iptvplayer.alternative_proxy2.value
            url = strwithmeta(url, {'iptv_http_proxy': proxy})
        return url

    def selectDomain(self):
        if self.MAIN_URL == None:
            domains = ['https://filmstreamvf.com/']
            domain = config.plugins.iptvplayer.filmstreamvk_alt_domain.value.strip()
            if self.cm.isValidUrl(domain):
                if domain[-1] != '/':
                    domain += '/'
                domains.insert(0, domain)
            for domain in domains:
                sts, data = self.getPage(domain)
                if not sts:
                    continue
                if '/serie' in data:
                    self.setMainUrl(self.cm.meta['url'])
                    break

        if self.MAIN_URL == None:
            self.MAIN_URL = domains[0]
        return

    def listMain(self, cItem):
        printDBG('FilmstreamvkCom.listMain')
        MAIN_CAT_TAB = [{'category': 'categories',
          'title': _('Movies'),
          'url': self.getFullUrl('/film-streaming-vf')},
         {'category': 'list_items',
          'title': _('Series'),
          'url': self.getFullUrl('/serie')},
         {'category': 'list_items',
          'title': _('Manga'),
          'url': self.getFullUrl('/manga')},
         {'category': 'search',
          'title': _('Search'),
          'search_item': True},
         {'category': 'search_history',
          'title': _('Search history')}]
        self.listsTab(MAIN_CAT_TAB, cItem)

    def listCategories(self, cItem, nextCategory):
        printDBG('FilmstreamvkCom.listCategories')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        self.addDir(MergeDicts(cItem, {'category': nextCategory,
         'title': _('--All--')}))
        data = ph.find(data, ('<li', '>', 'cat-item'), '</ul>')[1]
        data = ph.findall(data, ('<a', '>'), '</a>', flags=ph.START_S)
        for idx in range(1, len(data), 2):
            title = ph.clean_html(data[idx])
            url = self.getFullUrl(ph.getattr(data[idx - 1], 'href'))
            self.addDir(MergeDicts(cItem, {'category': nextCategory,
             'url': url,
             'title': title}))

        if not self.currList:
            self.listSort(MergeDicts(cItem, {'category': nextCategory}), 'list_items')

    def listSort(self, cItem, nextCategory):
        printDBG('FilmstreamvkCom.listSort')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        data = ph.find(data, ('<div', '>', 'sort'), '</ul>', flags=0)[1]
        data = ph.findall(data, ('<a', '>'), '</a>', flags=ph.START_S)
        for idx in range(1, len(data), 2):
            title = ph.clean_html(ph.getattr(data[idx - 1], 'title'))
            url = self.getFullUrl(ph.getattr(data[idx - 1], 'href'))
            self.addDir(MergeDicts(cItem, {'category': nextCategory,
             'url': url,
             'title': title}))

        if not self.currList:
            self.listItems(MergeDicts(cItem, {'category': nextCategory}), 'episodes')

    def listItems(self, cItem, nextCategory):
        printDBG('FilmstreamvkCom.listItems')
        page = cItem.get('page', 1)
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        cUrl = self.cm.meta['url']
        nextPage = ph.find(data, 'pagenavi', '</div>', flags=0)[1]
        nextPage = ph.rfind(data, '>%s</a>' % (page + 1), '<a ')[1]
        nextPage = self.getFullUrl(ph.search(nextPage, ph.A)[1])
        data = ph.findall(data, ('<div', '>', 'movie-preview'), ('<div', '>', 'clear'))
        for sItem in data:
            sItem = ph.rfindall(sItem, '</div>', ('<div', '>', 'movie-preview'), flags=0)
            for item in sItem:
                url = self.getFullUrl(ph.search(item, ph.A)[1])
                icon = self.getFullIconUrl(ph.search(item, ph.IMG)[1])
                title = ph.clean_html(ph.find(item, ('<span', '>', 'movie-title'), '</span>', flags=0)[1])
                tmp = ph.clean_html(ph.find(item, ('<span', '>', 'movie-release'), '</span>', flags=0)[1])
                if tmp:
                    title = '%s (%s)' % (title, tmp)
                tmp = ph.findall(item, ('<p', '>'), '</p>', flags=0)
                desc = []
                for t in tmp:
                    t = ph.clean_html(t)
                    if t:
                        desc.append(t)

                tmp = ph.clean_html(ph.find(item, ('<div', '>', 'movie-info'), '</div>', flags=0)[1])
                if tmp:
                    desc.append(tmp)
                params = MergeDicts(cItem, {'category': nextCategory,
                 'url': url,
                 'title': title,
                 'icon': icon,
                 'desc': '[/br]'.join(desc)})
                if 'saison-' in url or '/manga/' in url or '/serie/' in url:
                    season = ph.search(url + '-', 'aison-([0-9]+?)-')[0]
                    params['season'] = season
                    self.addDir(params)
                else:
                    self.addVideo(params)

        if nextPage:
            params = dict(cItem)
            params.update({'title': _('Next page'),
             'url': nextPage,
             'page': page + 1})
            self.addDir(params)

    def listEpisodes(self, cItem, nextCategory):
        printDBG('FilmstreamvkCom.listEpisodes')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        data = ph.findall(data, 'liste_episode', '</tr>')
        for idx in range(len(data)):
            title = ph.clean_html(self.cm.ph.getDataBeetwenMarkers(data[idx], '>', '<', False)[1])
            params = dict(cItem)
            params.update({'category': nextCategory,
             'title': title,
             's_title': cItem['title'],
             'erow_idx': idx})
            self.addDir(params)

    def listEpisodesByLanguage(self, cItem):
        printDBG('FilmstreamvkCom.listEpisodesByLanguage')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        tmp = ph.find(data, ('<div', '>', 'single-content'), ('<div', '>', 'content-left'), flags=0)[1]
        icon = self.getFullIconUrl(ph.search(tmp, ph.IMG)[1])
        if not icon:
            icon = cItem.get('icon', '')
        desc = []
        tmp = tmp.split('info-right', 1)[-1]
        tmp = re.compile('<!--[\\s\\S]*?-->').sub('', tmp)
        tmp = ph.findall(tmp, ('<div', '>'), '</div>', flags=0)
        for t in tmp:
            t = ph.clean_html(t)
            if t:
                desc.append(t)

        desc = '[/br]'.join(desc)
        titleSeason = ph.clean_html(cItem.get('s_title', '').split('Saison')[0])
        idx = cItem.get('erow_idx', 0)
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, 'liste_episode', '</tr>')
        if idx < len(data):
            data = data[idx]
        else:
            return
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
        for item in data:
            url = self.cm.ph.getSearchGroups(item, 'href=[\'"]([^\'^"]+?)[\'"]')[0]
            if self.cm.isValidUrl(url):
                title = ph.clean_html(item)
                fullTitle = titleSeason + ' '
                if cItem['season'] != '':
                    fullTitle += 's%s' % str(cItem['season']).zfill(2)
                try:
                    title = int(title)
                    fullTitle += 'e%s' % str(title).zfill(2)
                except Exception:
                    fullTitle += ' %s' % str(title).zfill(2)

                urlName = url.split('-')[-1]
                if urlName != '':
                    fullTitle += ' [%s]' % urlName
                params = dict(cItem)
                params.update({'url': url,
                 'title': fullTitle,
                 'icon': icon,
                 'desc': desc})
                self.addVideo(params)

    def listSearchResult(self, cItem, searchPattern, searchType):
        printDBG('FilmstreamvkCom.listSearchResult cItem[%s], searchPattern[%s] searchType[%s]' % (cItem, searchPattern, searchType))
        self.selectDomain()
        cItem = MergeDicts(cItem, {'category': 'list_items',
         'url': self.getFullUrl('/?s=') + urllib.quote(searchPattern)})
        self.listItems(cItem, 'episodes')

    def _getAjaxData(self, data, cUrl):
        post_data = {'action': 'electeur'}
        ajaxUrl = self.getFullUrl(ph.search(data, '\\s*=\\s*[\'"]([^\'^"]*?ajax[^\'^"]*?)[\'"]')[0].replace('\\/', '/'))
        data = ph.find(data, ('<div', '>', 'content-left'), ('<div', '>', 'watch-area'), flags=0)[1]
        data = ph.findall(data, '<input', '>', flags=0)
        for item in data:
            val = ph.getattr(item, 'value')
            name = ph.getattr(item, 'name')
            post_data[name] = val

        header = MergeDicts(self.defaultParams['header'], {'Referer': cUrl,
         'Accept': '*/*',
         'X-Requested-With': 'XMLHttpRequest'})
        params = MergeDicts(self.defaultParams, {'header': header})
        sts, data = self.getPage(ajaxUrl, params, post_data)
        return str(data)

    def _getBaseVideoLink(self, wholeData):
        videoUrlParams = []
        tmpUrls = []
        data = ph.findall(wholeData, '<iframe', '</iframe>', flags=ph.I | ph.START_E | ph.END_E)
        for item in data:
            url = ph.getattr(item, 'src', flags=ph.I)
            if url in tmpUrls:
                continue
            tmpUrls.append(url)
            if url.startswith('http') and 'facebook.com' not in url and 1 == self.up.checkHostSupport(url):
                videoUrlParams.append({'name': self.up.getHostName(url),
                 'url': url,
                 'need_resolve': 1})

        data = re.compile('onclick=[^>]*?[\'"](https?://[^\'^"]+?)[\'"]').findall(wholeData)
        for url in data:
            if url in tmpUrls:
                continue
            tmpUrls.append(url)
            if 'facebook.com' not in url and 1 == self.up.checkHostSupport(url):
                videoUrlParams.append({'name': self.up.getHostName(url),
                 'url': url,
                 'need_resolve': 1})

        return videoUrlParams

    def getLinksForVideo(self, cItem):
        printDBG('FilmstreamvkCom.getLinksForVideo [%s]' % cItem)
        self.selectDomain()
        urlTab = []
        sts, baseData = self.getPage(cItem['url'])
        if not sts:
            return []
        cUrl = self.cm.meta['url']
        data = baseData
        urlTab = self._getBaseVideoLink(data)
        data = ph.find(data, 'keremiya_part', '</div>')[1]
        data = ph.findall(data, ('<a ', '>'), '</a>')
        for item in data:
            url = ph.getattr(item, 'href')
            name = ph.clean_html(item)
            if url.startswith('http'):
                urlTab.append({'name': name,
                 'url': self.getFullUrl(url),
                 'need_resolve': 1})

        if len(urlTab) < 2:
            data = self._getAjaxData(baseData, cUrl)
            urlTab = self._getBaseVideoLink(data)
        return urlTab

    def getVideoLinks(self, videoUrl):
        printDBG('FilmstreamvkCom.getVideoLinks [%s]' % videoUrl)
        self.selectDomain()
        urlTab = []
        if self.up.getDomain(self.getMainUrl()) == self.up.getDomain(videoUrl):
            sts, data = self.getPage(videoUrl)
            if not sts:
                return []
            data = self._getAjaxData(data, self.cm.meta['url'])
            data = self._getBaseVideoLink(data)
            for item in data:
                urlTab.extend(self.up.getVideoLinkExt(item['url']))

        else:
            urlTab.extend(self.up.getVideoLinkExt(videoUrl))
        return urlTab

    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        name = self.currItem.get('name', '')
        category = self.currItem.get('category', '')
        mode = self.currItem.get('mode', '')
        printDBG('handleService: |||||||||||||||||||||||||||||||||||| name[%s], category[%s] ' % (name, category))
        self.currList = []
        self.selectDomain()
        if name == None:
            self.listMain({'name': 'category'})
        elif category == 'categories':
            self.listCategories(self.currItem, 'list_sort')
        elif category == 'list_sort':
            self.listSort(self.currItem, 'list_items')
        elif category == 'list_items':
            self.listItems(self.currItem, 'episodes')
        elif category == 'episodes':
            self.listEpisodes(self.currItem, 'episodes_by_language')
        elif category == 'episodes_by_language':
            self.listEpisodesByLanguage(self.currItem)
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
        CHostBase.__init__(self, FilmstreamvkCom(), True, [])