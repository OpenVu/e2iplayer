# Embedded file name: /IPTVPlayer/hosts/hostdixmax.py
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, MergeDicts, rm, GetCookieDir, ReadTextFile, WriteTextFile
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common
from Plugins.Extensions.IPTVPlayer.libs import ph
from Plugins.Extensions.IPTVPlayer.libs.e2ijson import loads as json_loads
from binascii import hexlify
from hashlib import md5
from datetime import datetime
import urllib
import re
from Components.config import config, ConfigText, getConfigListEntry
from Screens.MessageBox import MessageBox
config.plugins.iptvplayer.dixmax_login = ConfigText(default='', fixed_size=False)
config.plugins.iptvplayer.dixmax_password = ConfigText(default='', fixed_size=False)

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry(_('login'), config.plugins.iptvplayer.dixmax_login))
    optionList.append(getConfigListEntry(_('password'), config.plugins.iptvplayer.dixmax_password))
    return optionList


def gettytul():
    return 'https://dixmax.com/'


class SuggestionsProvider():
    MAIN_URL = 'https://dixmax.com/'
    COOKIE_FILE = ''

    def __init__(self):
        self.cm = common()
        self.HTTP_HEADER = {'User-Agent': self.cm.getDefaultHeader(browser='chrome')['User-Agent'],
         'X-Requested-With': 'XMLHttpRequest'}
        self.defaultParams = {'header': self.HTTP_HEADER,
         'use_cookie': True,
         'load_cookie': True,
         'cookiefile': self.COOKIE_FILE}

    def getName(self):
        return _('DixMax Suggestions')

    def getSuggestions(self, text, locale):
        url = self.MAIN_URL + 'api/private/get/search?query=%s&limit=10&f=0' % urllib.quote(text)
        sts, data = self.cm.getPage(url, self.defaultParams)
        if sts:
            retList = []
            for item in json_loads(data)['result']['ficha']['fichas']:
                retList.append(item['title'])

            return retList
        else:
            return None


class DixMax(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history': 'dixmax.com',
         'cookie': 'dixmax.com.cookie'})
        SuggestionsProvider.COOKIE_FILE = self.COOKIE_FILE
        self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
        self.defaultParams = {'header': self.HTTP_HEADER,
         'use_cookie': True,
         'load_cookie': True,
         'save_cookie': True,
         'cookiefile': self.COOKIE_FILE}
        self.MAIN_URL = 'https://dixmax.com/v2'
        self.DEFAULT_ICON_URL = 'https://4.bp.blogspot.com/-1UOMBRAcpSI/XJtljugnlMI/AAAAAAAAK7U/R-t7qkzA0zI-skW_SLacxnIkJPse7X8vACLcBGAs/w1200-h630-p-k-no-nu/wDVfEIHE_400x400.png'
        self.cacheLinks = {}
        self.loggedIn = None
        self.login = ''
        self.password = ''
        self.dbApiKey = ''
        self.cacheFilters = {}
        self.cacheFiltersKeys = ['genre',
         'age',
         'tmdb',
         'year',
         'quality']
        self.cacheFilters['genre'] = [{'title': 'Todo'},
         {'title': 'Accion',
          'f_genre': '40'},
         {'title': 'Animacion',
          'f_genre': '57'},
         {'title': 'Anime',
          'f_genre': '386'},
         {'title': 'Aventura',
          'f_genre': '29'},
         {'title': 'Belico',
          'f_genre': '102'},
         {'title': 'Ciencia ficcion',
          'f_genre': '41'},
         {'title': 'Cine negro',
          'f_genre': '61'},
         {'title': 'Comedia',
          'f_genre': '8'},
         {'title': 'Crimen',
          'f_genre': '4'},
         {'title': 'Drama',
          'f_genre': '3'},
         {'title': 'Fantastico',
          'f_genre': '28'},
         {'title': 'Infantil',
          'f_genre': '60'},
         {'title': 'Intriga',
          'f_genre': '14'},
         {'title': 'Musical',
          'f_genre': '71'},
         {'title': 'Romance',
          'f_genre': '25'},
         {'title': 'Terror',
          'f_genre': '44'},
         {'title': 'Thriller',
          'f_genre': '2'}]
        self.cacheFilters['age'] = [{'title': 'Todo'},
         {'title': '+18',
          'f_age': '18'},
         {'title': '+16',
          'f_age': '16'},
         {'title': '+13',
          'f_age': '13'},
         {'title': '+12',
          'f_age': '12'},
         {'title': '+7',
          'f_age': '7'},
         {'title': 'TP',
          'f_age': '1'}]
        self.cacheFilters['tmdb'] = [{'title': 'Todo'}]
        for f in range(9, 0, -1):
            self.cacheFilters['tmdb'].append({'title': '%s-10' % f,
             'f_tmdb_from': '%s.0' % f,
             'f_tmdb_to': '10.0'})

        currYear = datetime.now().year
        self.cacheFilters['year'] = [{'title': 'Todo'}]
        for f in range(currYear, 1899, -1):
            self.cacheFilters['year'].append({'title': '%s' % f,
             'f_year_from': '%s' % f,
             'f_year_to': '%s' % f})

        self.cacheFilters['quality'] = [{'title': 'Todo'},
         {'title': 'HD 1080',
          'f_quality': 'HD 1080'},
         {'title': 'HD 720',
          'f_quality': 'HD 720'},
         {'title': 'RIP',
          'f_quality': 'RIP'},
         {'title': 'CAM',
          'f_quality': 'CAM'}]
        return

    def getPage(self, baseUrl, addParams = {}, post_data = None):
        if addParams == {}:
            addParams = dict(self.defaultParams)
        return self.cm.getPage(baseUrl, addParams, post_data)

    def setMainUrl(self, url):
        CBaseHostClass.setMainUrl(self, url)
        SuggestionsProvider.MAIN_URL = self.getMainUrl()

    def getFullIconUrl(self, url, baseUrl = None):
        if url.startswith('/'):
            return 'https://image.tmdb.org/t/p/w185' + url
        return CBaseHostClass.getFullIconUrl(self, url, baseUrl)

    def getDBApiKey(self, data = None):
        printDBG('DixMax.listMain')
        if self.dbApiKey:
            return self.dbApiKey
        sts, data = self.getPage(self.getFullUrl('/index.php'))
        if not sts:
            return
        data = ph.find(data, 'filterCat(', ')', 0)[1].split(',')
        self.dbApiKey = data[-1].strip()[1:-1]

    def listMain(self, cItem):
        printDBG('DixMax.listMain')
        sts, data = self.getPage(self.getFullUrl('/index.php'))
        if not sts:
            return
        cUrl = self.cm.meta['url']
        self.setMainUrl(cUrl)
        cUrl = cUrl.split('?', 1)[0]
        if not cUrl.endswith('/'):
            cUrl += '/'
        tmp = ph.find(data, ('<ul', '>', 'header__nav'), '</ul>', flags=0)[1]
        tmp = ph.findall(data, ('<li', '>'), '</li>', flags=0, limits=3)
        for item in tmp:
            title = ph.clean_html(item)
            url = self.getFullUrl(ph.search(item, ph.A)[1], cUrl)
            type = url.rsplit('/', 1)[-1]
            if type in ('series', 'movies'):
                self.addDir(MergeDicts(cItem, {'category': 'list_filters',
                 'title': title,
                 'url': url}))
            elif type == 'v2':
                self.addDir(MergeDicts(cItem, {'category': 'list_popular',
                 'title': title,
                 'url': url}))

        MAIN_CAT_TAB = [{'category': 'search',
          'title': _('Search'),
          'search_item': True}, {'category': 'search_history',
          'title': _('Search history')}]
        self.listsTab(MAIN_CAT_TAB, cItem)

    def listFilters(self, cItem, nextCategory):
        printDBG('DixMax.listFilters')
        cItem = dict(cItem)
        f_idx = cItem.get('f_idx', 0)
        if f_idx >= len(self.cacheFiltersKeys):
            return
        filter = self.cacheFiltersKeys[f_idx]
        f_idx += 1
        cItem['f_idx'] = f_idx
        if f_idx == len(self.cacheFiltersKeys):
            cItem['category'] = nextCategory
        self.listsTab(self.cacheFilters.get(filter, []), cItem)

    def listPopular(self, cItem):
        printDBG('DixMax.listPopular')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        self.setMainUrl(self.cm.meta['url'])
        data = ph.find(data, ('<section', '>', 'content'), '</section>', flags=0)[1]
        titleMap = {}
        tmp = ph.find(data, ('<ul', '>', 'tablist'), '</ul>', flags=0)[1]
        tmp = ph.findall(tmp, ('<a', '>', 'aria-controls'), '</a>', flags=ph.START_S)
        for idx in range(1, len(tmp), 2):
            title = ph.clean_html(tmp[idx])
            key = ph.getattr(tmp[idx - 1], 'aria-controls')
            titleMap[key] = title

        data = ph.rfindall(data, '</div>', ('<div', '>', 'tabpanel'))
        for item in data:
            title = titleMap.get(ph.getattr(item, 'id'), '')
            subItems = self._listItems2(cItem, 'explore_item', item)
            if subItems:
                self.addDir(MergeDicts(cItem, {'title': title,
                 'category': 'sub_items',
                 'sub_items': subItems}))

    def _listItems(self, cItem, nextCategory, data):
        printDBG('DixMax._listItems')
        retList = []
        for item in data:
            item = item['info']
            icon = item.get('cover', '')
            if not icon:
                icon = item.get('poster', '')
            icon = self.getFullIconUrl(icon) if icon else ''
            title = ph.clean_html(item['title'])
            title2 = ph.clean_html(item['originalTitle'])
            if title2 and title2 != title:
                title += ' (%s)' % title2
            type = item['type']
            desc = [type]
            desc.append(item['year'])
            duration = _('%s minutes') % item['duration']
            desc.append(duration)
            rating = '%s (%s)' % (item['rating'], item['votes']) if int(item['votes']) else ''
            if rating:
                desc.append(rating)
            desc.append(item['country'])
            desc.append(item['genres'])
            desc.append(item['popularity'])
            desc = ' | '.join(desc) + '[/br]' + item['sinopsis']
            url = 'serie' if int(item['isSerie']) else 'movie'
            url = self.getFullUrl('v2/%s/%s' % (url, item['id']))
            retList.append(MergeDicts(cItem, {'good_for_fav': True,
             'category': nextCategory,
             'title': title,
             'url': url,
             'icon': icon,
             'desc': desc}))

        return retList

    def listItems(self, cItem, nextCategory):
        printDBG('DixMax.listItems %s' % cItem)
        page = cItem.get('page', 1)
        url = cItem['url'][:-1] if cItem['url'].endswith('/') else cItem['url']
        url += '/page/%s' % page
        query = {}
        for key, val in cItem.iteritems():
            if key.startswith('f_') and key != 'f_idx':
                query[key[2:]] = val

        url += '?' + urllib.urlencode(query)
        sts, data = self.getPage(url)
        if not sts:
            return
        self.setMainUrl(self.cm.meta['url'])
        data = ph.find(data, ('<div', '>', 'card'), '</section>')[1].split('paginator', 1)
        if len(data) == 2:
            nextPage = ph.search(data[-1], '/page/(%s)[^0-9]' % (page + 1))[0]
        else:
            nextPage = ''
        self.currList = self._listItems2(cItem, nextCategory, data[0])
        if nextPage:
            self.addDir(MergeDicts(cItem, {'title': _('Next page'),
             'page': page + 1}))

    def _listItems2(self, cItem, nextCategory, data):
        printDBG('DixMax._listItems2')
        retLit = []
        data = ph.rfindall(data, '</div>', ('<div', '>', 'col-'))
        for item in data:
            icon = ph.find(item, '<img', '>', flags=0)[1]
            icon = self.getFullIconUrl(ph.getattr(icon, 'data-src-lazy'))
            title = ph.find(item, ('<h3', '>'), '</h3>', flags=0)[1]
            url = self.getFullUrl(ph.search(title, ph.A)[1])
            title = ph.clean_html(title)
            desc = []
            tmp = ph.findall(item, ('<span', '>'), '</span>', flags=0)
            for t in tmp:
                t = ph.clean_html(t.replace('</a>', ', '))
                if t.endswith(','):
                    t = t[:-1]
                if t:
                    desc.append(t)

            retLit.append({'good_for_fav': True,
             'type': 'category',
             'name': 'category',
             'category': nextCategory,
             'title': title,
             'url': url,
             'icon': icon,
             'desc': ' | '.join(desc)})

        return retLit

    def _getParams(self, data):
        params = []
        data = data.split(',')
        for item in data:
            item = item.strip()
            for m in ('"', "'"):
                if item.startswith(m) and item.endswith(m):
                    item = item[1:-1]
                    break

            params.append(item)

        return params

    def exploreItem(self, cItem, nextCategory):
        printDBG('DixMax.exploreItem')
        self.cacheLinks = {}
        itemType = ph.search(cItem['url'], '/(serie|movie)/([0-9]+)')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        tmp = ph.find(data, ('<div', '>', 'ytplayer'), '</script>', flags=0)[1]
        trailer = ph.search(tmp, 'videoId\\s*:\\s*[\'"]([^\'^"]+?)[\'"]')[0]
        if trailer:
            title = '%s - %s' % (cItem['title'], ph.clean_html(ph.find(tmp, ('<h', '>'), ('</h', '>'), flags=0)[1]))
            url = 'https://www.youtube.com/watch?v=%s' % trailer
            self.addVideo(MergeDicts(cItem, {'good_for_fav': True,
             'title': title,
             'url': url,
             'prev_url': cItem['url']}))
        if itemType[0] == 'serie':
            try:
                seriesTitle = ph.clean_html(ph.find(data, ('<h1', '>', 'title'), '</h1>', flags=0)[1])
                reObj = re.compile('([0-9]+)')
                sIcon = self.getFullIconUrl(ph.getattr(data, 'data-src-lazy'))
                data = ph.findall(data, ('<button', '>', 'collapsed'), '</table>', flags=0)
                for seasonData in data:
                    seasonData = seasonData.split('</button>', 1)
                    sTitle = ph.findall(seasonData[0], ('<span', '>'), '</span>')
                    if sTitle:
                        sDesc = ph.clean_html(sTitle[-1])
                        sTitle = ph.clean_html(sTitle[0])
                    else:
                        sDesc = ph.clean_html(seasonData[0])
                        sTitle = ph.clean_html(seasonData[0])
                    sNum = ph.search(sTitle, reObj)[0]
                    subItems = []
                    seasonData = ph.findall(seasonData[-1], ('<tr', '>'), '</tr>', flags=0)
                    for item in seasonData:
                        item = ph.findall(item, ('<t', '>'), ('</t', '>'), flags=0)
                        eNum = ph.clean_html(item[1])
                        title = ph.clean_html(item[2])
                        desc = ph.clean_html(item[3])
                        item = self._getParams(ph.find(item[3], 'verEnlaces2(', ')', flags=0)[1])
                        if len(item) < 5:
                            printDBG('Param parse failed [%s]' % item)
                            continue
                        icon = self.getFullIconUrl(item[2])
                        title = '%s: s%se%s %s' % (seriesTitle,
                         sNum.zfill(2),
                         eNum.zfill(2),
                         item[2])
                        params = {'good_for_fav': True,
                         'prev_url': cItem['url'],
                         'type': 'video',
                         'title': title,
                         'icon': icon,
                         'desc': desc,
                         'f_isepisode': 1,
                         'f_id': item[1],
                         'f_season': item[4],
                         'f_episode': item[5],
                         'f_title': item[2]}
                        params['url'] = '%s#%sx%sx%s' % (cItem['url'],
                         params['f_id'],
                         params['f_episode'].zfill(2),
                         params['f_season'].zfill(2))
                        subItems.append(params)

                    if len(subItems):
                        params = {'f_type': _('Season'),
                         'f_isseason': 1,
                         'f_season': sNum}
                        params = MergeDicts(cItem, {'good_for_fav': False,
                         'prev_url': cItem['url'],
                         'category': nextCategory,
                         'sub_items': subItems,
                         'title': sTitle,
                         'icon': sIcon,
                         'desc': sDesc}, params)
                        self.addDir(params)

            except Exception:
                printExc()

        else:
            item = self._getParams(ph.find(data, 'verEnlaces(', ')', flags=0)[1])
            if len(item) < 3:
                printDBG('Param parse failed [%s]' % item)
                return
            icon = self.getFullIconUrl(item[2])
            self.addVideo(MergeDicts(cItem, {'prev_url': cItem['url'],
             'icon': icon,
             'f_id': item[1]}))

    def listSearchResult(self, cItem, searchPattern, searchType):
        self.tryTologin()
        url = self.getFullUrl('/api/private/get/search?query=%s&limit=100&f=1' % urllib.quote(searchPattern))
        sts, data = self.getPage(url)
        if not sts:
            return
        self.setMainUrl(self.cm.meta['url'])
        try:
            data = json_loads(data)
            for key in data['result']:
                subItems = self._listItems(cItem, 'explore_item', data['result'][key])
                if subItems:
                    self.addDir(MergeDicts(cItem, {'title': key.title(),
                     'category': 'sub_items',
                     'sub_items': subItems}))

        except Exception:
            printExc()

        if len(self.currList) == 1:
            self.currList = self.currList[0]['sub_items']

    def _getLinks(self, key, cItem):
        printDBG('DixMax._getLinks [%s]' % cItem['f_id'])
        post_data = {'id': cItem['f_id']}
        isSeries = cItem.get('f_isepisode') or cItem.get('f_isserie')
        if isSeries:
            post_data.update({'i': 'true',
             't': cItem.get('f_season'),
             'e': cItem.get('f_episode')})
        else:
            post_data.update({'i': 'false'})
        url = self.getFullUrl('api/private/get_links.php')
        sts, data = self.getPage(url, post_data=post_data)
        if not sts:
            return
        printDBG(data)
        try:
            data = json_loads(data)
            for item in data:
                if key not in self.cacheLinks:
                    self.cacheLinks[key] = []
                name = '[%s] %s | %s (%s) | %s | %s | %s ' % (item['host'],
                 item['calidad'],
                 item['audio'],
                 item['sonido'],
                 item['sub'],
                 item['fecha'],
                 item['autor_name'])
                url = self.getFullUrl(item['link'])
                self.cacheLinks[key].append({'name': name,
                 'url': strwithmeta(url, {'Referer': self.getMainUrl()}),
                 'need_resolve': 1})

        except Exception:
            printExc()

    def getLinksForVideo(self, cItem):
        self.tryTologin()
        url = cItem.get('url', '')
        if 0 != self.up.checkHostSupport(url):
            return self.up.getVideoLinkExt(url)
        if 'f_isepisode' in cItem:
            key = '%sx%sx%s' % (cItem['f_id'], cItem['f_episode'].zfill(2), cItem['f_season'].zfill(2))
        else:
            key = cItem['f_id']
        linksTab = self.cacheLinks.get(key, [])
        if not linksTab:
            self._getLinks(key, cItem)
            linksTab = self.cacheLinks.get(key, [])
        return linksTab

    def getVideoLinks(self, videoUrl):
        printDBG('DixMax.getVideoLinks [%s]' % videoUrl)
        if len(self.cacheLinks.keys()):
            for key in self.cacheLinks:
                for idx in range(len(self.cacheLinks[key])):
                    if videoUrl in self.cacheLinks[key][idx]['url']:
                        if not self.cacheLinks[key][idx]['name'].startswith('*'):
                            self.cacheLinks[key][idx]['name'] = '*' + self.cacheLinks[key][idx]['name']

        if 0 != self.up.checkHostSupport(videoUrl):
            return self.up.getVideoLinkExt(videoUrl)
        return []

    def getArticleContent(self, cItem):
        printDBG('DixMax.getVideoLinks [%s]' % cItem)
        retTab = []
        itemsList = []
        if 'prev_url' in cItem:
            url = cItem['prev_url']
        else:
            url = cItem['url'].split('#', 1)[0]
        sts, data = self.getPage(url)
        if not sts:
            return
        data = ph.find(data, ('<section', '>', 'details'), '</section>', flags=0)[1]
        icon = self.getFullIconUrl(ph.getattr(data, 'data-src-lazy'))
        title = ph.clean_html(ph.find(data, ('<h1', '>', 'title'), '</h1>', flags=0)[1])
        desc = ph.clean_html(ph.find(data, ('<div', '>', 'description'), '</div>', flags=0)[1])
        val = ph.clean_html(ph.find(data, ('<span', '>', 'rate'), '</span>', flags=0)[1])
        itemsList.append((_('Rating:'), val))
        data = ph.find(data, ('<ul', '>', 'meta'), '</ul>', flags=0)[1]
        data = ph.findall(data, ('<li', '>'), '</li>', flags=0)
        for item in data:
            item = item.split('</span>', 1)
            if len(item) < 2:
                continue
            key = ph.clean_html(item[0])
            val = ph.clean_html(item[1])
            if key == '' or val == '':
                continue
            itemsList.append((key, val))

        if title == '':
            title = cItem['title']
        if icon == '':
            icon = cItem.get('icon', self.DEFAULT_ICON_URL)
        if desc == '':
            desc = cItem.get('desc', '')
        return [{'title': title,
          'text': desc,
          'images': [{'title': '',
                      'url': icon}],
          'other_info': {'custom_items_list': itemsList}}]

    def tryTologin(self):
        printDBG('tryTologin start')
        loginUrl = self.getFullUrl('?view=perfil')
        if None == self.loggedIn or self.login != config.plugins.iptvplayer.dixmax_login.value or self.password != config.plugins.iptvplayer.dixmax_password.value:
            loginCookie = GetCookieDir('dixmax.com.login')
            self.login = config.plugins.iptvplayer.dixmax_login.value
            self.password = config.plugins.iptvplayer.dixmax_password.value
            sts, data = self.getPage(loginUrl)
            if sts:
                self.setMainUrl(self.cm.meta['url'])
            freshSession = False
            if sts and 'logout.php' in data:
                printDBG('Check hash')
                hash = hexlify(md5('%s@***@%s' % (self.login, self.password)).digest())
                prevHash = ReadTextFile(loginCookie)[1].strip()
                printDBG('$hash[%s] $prevHash[%s]' % (hash, prevHash))
                if hash == prevHash:
                    self.loggedIn = True
                    return
                freshSession = True
            rm(loginCookie)
            rm(self.COOKIE_FILE)
            if freshSession:
                sts, data = self.getPage(self.getMainUrl(), MergeDicts(self.defaultParams, {'use_new_session': True}))
            self.loggedIn = False
            if '' == self.login.strip() or '' == self.password.strip():
                msg = _('The host %s requires registration. \nPlease fill your login and password in the host configuration. Available under blue button.' % self.getMainUrl())
                self.sessionEx.waitForFinishOpen(MessageBox, msg, type=MessageBox.TYPE_INFO, timeout=10)
                return False
            msgTab = [_('Login failed.')]
            if sts:
                actionUrl = self.getFullUrl('/session.php?action=1')
                post_data = {'username': self.login,
                 'password': self.password,
                 'remember': '1'}
                httpParams = dict(self.defaultParams)
                httpParams['header'] = MergeDicts(httpParams['header'], {'Referer': self.cm.meta['url'],
                 'Accept': '*/*'})
                sts, data = self.getPage(actionUrl, httpParams, post_data)
                printDBG(data)
                if sts:
                    msgTab.append(ph.clean_html(data))
                sts, data = self.getPage(loginUrl)
            # if sts and 'logout.php' in data:
            if sts and 'local_out' in data:
                printDBG('tryTologin OK')
                self.loggedIn = True
            else:
                printDBG(data)
                self.sessionEx.waitForFinishOpen(MessageBox, '\n'.join(msgTab), type=MessageBox.TYPE_ERROR, timeout=10)
                printDBG('tryTologin failed')
            if self.loggedIn:
                hash = hexlify(md5('%s@***@%s' % (self.login, self.password)).digest())
                WriteTextFile(loginCookie, hash)
        return self.loggedIn

    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        name = self.currItem.get('name', '')
        category = self.currItem.get('category', '')
        printDBG('handleService: ||| name[%s], category[%s] ' % (name, category))
        self.currList = []
        self.tryTologin()
        if name == None:
            self.listMain({'name': 'category',
             'type': 'category'})
        elif category == 'list_filters':
            self.listFilters(self.currItem, 'list_items')
        elif category == 'list_popular':
            self.listPopular(self.currItem)
        elif category == 'sub_items':
            self.listSubItems(self.currItem)
        elif category == 'list_items':
            self.listItems(self.currItem, 'explore_item')
        elif category == 'explore_item':
            self.exploreItem(self.currItem, 'sub_items')
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

    def getSuggestionsProvider(self, index):
        printDBG('DixMax.getSuggestionsProvider')
        return SuggestionsProvider()


class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, DixMax(), True, [])

    def withArticleContent(self, cItem):
        return 'prev_url' in cItem or cItem.get('category') == 'explore_item'