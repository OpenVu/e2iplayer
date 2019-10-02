
# -*- coding: utf-8 -*-

#
#
# @Codermik release, based on @Samsamsam's E2iPlayer public.
# Released with kind permission of Samsamsam.
# All code developed by Samsamsam is the property of the Samsamsam and the E2iPlayer project,  
# all other work is Â© E2iStream Team, aka Codermik.  
#
# https://www.facebook.com/e2iStream/
#
#

##########################################################################################

from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, MergeDicts, rm, GetCookieDir, ReadTextFile, WriteTextFile
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common
from Plugins.Extensions.IPTVPlayer.libs import ph
from Plugins.Extensions.IPTVPlayer.tools.e2ijs import js_execute
from Plugins.Extensions.IPTVPlayer.libs.e2ijson import loads as json_loads

##########################################################################################
import urllib, re

def gettytul():
    return 'http://fenixsite.co'


class Fenixsite(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history': 'fenixsite.co', 'cookie': 'fenixsite.co.cookie'})
        self.HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
        self.defaultParams = {'header': self.HTTP_HEADER, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE}
        self.MAIN_URL = 'http://fenixsite.co/'
        self.DEFAULT_ICON_URL = 'https://i.pinimg.com/originals/67/70/a3/6770a3fa9bdcc1bd33770106cd70fb22.png'
        self.cacheFilters = {}
        self.cacheFiltersKeys = []
        self.cacheLinks = {}

        self.HOST_VER = '1.0 (19/08/2019)'
        self.HOST_DESC = '\c00????00 Info: \c00??????https://www.fenixsite.co\\n \c00????00Version/Date: \c00??????'+self.HOST_VER+'\\n \c00????00Developer: \c00??????Codermik\\n'

    def getPage(self, baseUrl, addParams={}, post_data=None):
        if addParams == {}:
            addParams = dict(self.defaultParams)
        return self.cm.getPage(baseUrl, addParams, post_data)

    def listMain(self, cItem, nextCategory):
        printDBG('Fenixsite >>>>>>>>>>>> listMain >> %s' % cItem )
        sts, data = self.getPage(self.getMainUrl())
        if not sts: return
        self.setMainUrl(self.cm.meta['url'])
        data = ph.find(data, ('<ul', '>', 'navbar'), '</ul>')[1]
        data = ph.findall(data, ('<li', '>'), '</li>')
        for item in data:
            url = ph.getattr(item, 'href')
            if '/strani_filmovi/' in url or '/strane_serije/' in url:
                title = ph.clean_html(item)
                self.addDir(MergeDicts(cItem, {'category': nextCategory, 'url': self.getFullUrl(url), 'title': title, 'desc': self.HOST_DESC}))
        
        MAIN_CAT_TAB = [
                            {'category': nextCategory, 'title': 'Anime', 'url': self.getFullUrl('/load/anime_serije/95'), 'desc': self.HOST_DESC}, 
                            {'category': 'search', 'title': _('Search'), 'search_item': True, 'desc': self.HOST_DESC}, 
                            {'category': 'search_history', 'title': _('Search history'), 'desc': self.HOST_DESC}
                       ]

        self.listsTab(MAIN_CAT_TAB, cItem)

    def listCategories(self, cItem, nextCategory):
        printDBG('Fenixsite >>>>>>>>>>>> listCategories >> %s' % cItem )
        sts, data = self.getPage(cItem['url'])
        if not sts: return
        self.setMainUrl(self.cm.meta['url'])
        data = ph.find(data, ('<div', '>', 'owl-box'), '</table>')[1]
        data = ph.findall(data, ('<a', '>'), '</td>', flags=ph.START_S)
        itemsList = []
        for idx in range(1, len(data), 2):
            url = self.getFullUrl(ph.getattr(data[(idx - 1)], 'href'))
            title = ph.clean_html(data[idx])
            itemsList.append(MergeDicts(cItem, {'good_for_fav': True, 'category': nextCategory, 'url': url, 'title': title}))
        if '/strane_serije/' in cItem['url']:
            subItems = {}
            letters = []
            for item in itemsList:
                letter = item['title'].decode('utf-8')[0].upper()
                if letter.isnumeric():
                    letter = '#'
                if letter not in subItems:
                    subItems[letter] = []
                    letters.append(letter)
                subItems[letter].append(item)
            for letter in letters:
                self.addDir(MergeDicts(cItem, {'good_for_fav': False, 'category': 'sub_items', 'sub_items': subItems[letter], 'title': '%s [%d]' % (letter.encode('utf-8'), len(subItems[letter])), 'desc': self.HOST_DESC }))
        else:
            self.currList.append(MergeDicts(cItem, {'title': _('--All--'), 'category': nextCategory}))
            self.currList.extend(itemsList)

    def listSort(self, cItem, nextCategory):
        printDBG('Fenixsite >>>>>>>>>>>> listSort >> %s' % cItem )
        sts, pageData = self.getPage(cItem['url'])
        if not sts: return
        self.setMainUrl(self.cm.meta['url'])
        directionsTitle = {1: 'â', 0: 'â'}
        data = ph.find(pageData, ('<span', '>', 'sortBlock'), '</span>')[1]
        data = ph.findall(data, ('<a', '>'), '</a>', flags=ph.START_S)
        items = [[], []]
        for idx in range(1, len(data), 2):
            item = ph.find(data[(idx - 1)], 'ssorts(', ')', flags=0)[1].split(',')
            if len(item) != 3:
                continue
            title = ph.clean_html(data[idx])
            url = self.getFullUrl(item[1].strip()[1:-1])
            try:
                sort = int(item[0].strip()[1:-1])
                sort = sort + 1 if sort % 2 else sort
                for i in range(2):
                    sort -= i
                    items[i].append(MergeDicts(cItem, {'good_for_fav': True, 'category': nextCategory, 'url': url, 'title': '%s %s' % (directionsTitle[i], title), 'f_sort': sort}))
            except Exception:
                printExc()
        self.currList = items[0]
        self.currList.extend(items[1])
        if not self.currList:
            self.listItems(MergeDicts(cItem, {'category': nextCategory}), pageData)

    def listItems(self, cItem, data=None):
        printDBG('Fenixsite >>>>>>>>>>>> listItems >> %s' % cItem )
        page = cItem.get('page', 1)
        if not data:
            url = cItem['url']
            if page == 1:
                url += '-%s-%s' % (page, cItem['f_sort'])
            sts, data = self.getPage(url)
            if not sts:
                return

        self.setMainUrl(self.cm.meta['url'])
        mainDesc = ph.clean_html(ph.find(data, ('<div', '>', 'shortstory-news'), '</div>', flags=0)[1].split('</h1>', 1)[(-1)])
        tmp = ph.find(data, ('<span', '>', 'pagesBlock'), '</td>')[1]
        tmp = ph.search(tmp, '<a([^>]+?spages\\(\\s*?[\'"]%s[\'"][^>]*?)>' % (page + 1))[0]
        nextPage = self.getFullUrl(ph.getattr(tmp, 'href'))
        reIcon = re.compile('<img[^>]+?src=([\'"])([^>]*?\\.(?:jpe?g|png|gif)(?:\\?[^\\1]*?)?)(?:\\1)', re.I)
        data = ph.findall(data, ('<div', '>', 'entry'), '</ul>')
        for item in data:
            url = self.getFullUrl(ph.search(item, ph.A_HREF_URI_RE)[1])
            icon = self.getFullIconUrl(ph.search(item, reIcon)[1])
            title = ph.clean_html(ph.find(item, ('<h', '>'), '</h', flags=0)[1])
            desc = []
            tmp = [
             ph.find(item, ('<i', '>', 'eye'), '</span', flags=0)[1], ph.find(item, ('<i', '>', 'comments'), '</span', flags=0)[1], ph.find(item, ('<i', '>', 'comments'), '</span', flags=0)[1]]
            for t in tmp:
                t = ph.clean_html(t)
                if t:
                    desc.append(t)

            tmp = ph.find(item, ('<ul', '>', 'title'))[1]
            desc.append(ph.getattr(tmp, 'title').replace('/', ' (') + ')')
            self.addVideo({'good_for_fav': True, 'title': title, 'url': url, 'icon': icon, 'desc': self.HOST_DESC })

        if nextPage:
            self.addDir(MergeDicts(cItem, {'good_for_fav': False, 'title': _('Next page'), 'url': nextPage, 'page': page + 1}))

    def listSearchResult(self, cItem, searchPattern, searchType):
        url = self.getFullUrl('/search/?q=%s&m=load&t=0' % urllib.quote(searchPattern))
        self.listSearchItems(MergeDicts(cItem, {'category': 'list_search_items', 'url': url}))

    def listSearchItems(self, cItem):
        page = cItem.get('page', 1)
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        self.setMainUrl(self.cm.meta['url'])
        tmp = ph.find(data, ('<span', '>', 'pagesBlock'), '</div>')[1]
        tmp = ph.find(tmp, ('<a', '>', ';p=%s;' % (page + 1)))[1]
        nextPage = self.getFullUrl(ph.getattr(tmp, 'href'))
        data = ph.find(data, ('<div', '>', 'eTitle'), ('<div', '>', 'clearfix'), flags=ph.START_E)[1]
        data = ph.rfindall(data, '</div>', ('<div', '>', 'eTitle'), flags=0)
        for item in data:
            url = self.getFullUrl(ph.search(item, ph.A)[1])
            icon = self.getFullIconUrl(ph.search(item, ph.IMG)[1])
            title = ph.clean_html(ph.find(item, ('<a', '>'), '</a>', flags=0)[1])
            desc = [ph.clean_html(ph.find(item, ('<div', '>', 'eDetails'), '</div>', flags=0)[1])]
            desc.append(ph.clean_html(ph.find(item, ('<div', '>', 'eMessage'), '</div>', flags=0)[1]))
            self.addVideo({'good_for_fav': True, 'title': title, 'url': url, 'icon': icon, 'desc': ('[/br]').join(desc)})
        if nextPage:
            self.addDir(MergeDicts(cItem, {'good_for_fav': False, 'title': _('Next page'), 'url': nextPage, 'page': page + 1}))

    def getLinksForVideo(self, cItem):
        printDBG('Fenixsite >>>>>>>>>>>> getLinksForVideo >> %s' % cItem )
        linksTab = self.cacheLinks.get(cItem['url'], [])
        if linksTab:
            return linksTab
        linksTab = []
        subTrack = ''
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return []
        self.setMainUrl(self.cm.meta['url'])
        cUrl = self.cm.meta['url']
        trailerUrl = ''
        tmp = ph.findall(data, ('<script', '>'), '</script>')
        for item in tmp:
            if 'getJSON' in item:
                key = ph.search(item, 'var\\s+?keys\\s*?=[^;^\'^"]*?[\'"]([^\'^"]+?)[\'"]')[0]
                item = ph.find(item, 'getJSON(', ',', flags=0)[1].split('+')
                apiLink = ''
                for it in item:
                    it = it.strip()
                    if it.startswith('"') or it.startswith("'"):
                        apiLink += it[1:-1]
                    elif 'key' in it:
                        apiLink += urllib.quote_plus(key)
                    elif 'count' in it:
                        apiLink += '1'
                apiLink = self.getFullUrl(apiLink)
                sts, tmp = self.getPage(apiLink)
                if sts:
                    try:
                        trailerUrl = 'https://www.youtube.com/watch?v=' + json_loads(tmp)['items'][0]['videoId']
                    except Exception:
                        printExc()
                break
        labelsMap = []
        tmp = ph.find(data, ('<ul', '>', 'tablist'), '</ul>', flags=0)[1]
        tmp = ph.findall(tmp, ('<li', '>'), '</li>', flags=0)
        titlesMap = {}
        for item in tmp:
            key = ph.search(item, ph.A_HREF_URI_RE)[1]
            title = ph.clean_html(item)
            if not key:
                continue
            titlesMap[key] = title
        data = ph.find(data, ('<div', '>', 'tab-content'), ('<div', '>', 'fstory'), flags=0)[1]
        data = ph.rfindall(data, '</div>', ('<div', '>', 'tab-pane'), flags=ph.END_S)
        for idx in xrange(1, len(data), 2):
            id = ph.getattr(data[(idx - 1)], 'id')
            item = data[idx]
            title = titlesMap.get('#%s' % id, '')
            url = ph.search(item, ph.IFRAME_SRC_URI_RE)[1]
            if url:
                linksTab.append({'name': '%s | %s' % (title, self.up.getDomain(url)), 'url': self.getFullUrl(url), 'need_resolve': 1})
            elif 'gkpluginsphp' in item:
                idx1 = item.find('{')
                idx2 = item.rfind('}')
                if idx1 >= 0 and idx2 >= 0:
                    ret = js_execute('print(JSON.stringify(%s));' % item[idx1:idx2 + 1])
                    if ret['sts'] and 0 == ret['code']:
                        try:
                            item = json_loads(ret['data'])
                            if item.get('subtitle'):
                                subTrack = self.getFullUrl(item['subtitle'])
                            for it in item['gklist']:
                                if it['link']:
                                    linksTab.append({'name': '%s | %s | %s' % (title, it['title'], self.up.getDomain(it['link'])), 'url': self.getFullUrl(it['link']), 'need_resolve': 1})
                        except Exception:
                            printExc()

        if len(linksTab):
            if subTrack:
                subTrack = [{'title': _('Default'), 'url': subTrack, 'lang': 'default', 'format': 'vtt'}]
                for item in linksTab:
                    item['url'] = strwithmeta(item['url'], {'Referer': cUrl, 'external_sub_tracks': subTrack})

            self.cacheLinks[cItem['url']] = linksTab
        if trailerUrl:
            linksTab.append({'name': _('Trailer'), 'url': trailerUrl, 'need_resolve': 1})
        return linksTab

    def getVideoLinks(self, videoUrl):
        printDBG('Fenixsite >>>>>>>>>>>> getVideoLinks >> %s' % videoUrl )
        if len(self.cacheLinks.keys()):
            for key in self.cacheLinks:
                for idx in range(len(self.cacheLinks[key])):
                    if videoUrl in self.cacheLinks[key][idx]['url']:
                        if not self.cacheLinks[key][idx]['name'].startswith('*'):
                            self.cacheLinks[key][idx]['name'] = '*' + self.cacheLinks[key][idx]['name']
        linksTab = self.up.getVideoLinkExt(videoUrl)
        if linksTab:
            meta = strwithmeta(videoUrl).meta
            subTracks = meta.get('external_sub_tracks')
            if subTracks:
                for item in linksTab:
                    item['url'] = strwithmeta(item['url'], MergeDicts(meta, {'external_sub_tracks': subTracks + strwithmeta(item['url']).meta.get('external_sub_tracks', [])}))
        return linksTab

    def getArticleContent(self, cItem, data=None):
        printDBG('Fenixsite >>>>>>>>>>>> getArticleContent >> %s' % cItem )
        retTab = []
        if not data:
            sts, data = self.getPage(cItem['url'])
            if not sts: 
                return []
            self.setMainUrl(self.cm.meta['url'])
        tmp = ph.find(data, ('<div', '>', 'fullstory'), '</div>', flags=0)[1]
        title = ph.clean_html(ph.find(tmp, ('<h1', '>'), '</h1>', flags=0)[1])
        icon = self.getFullIconUrl(ph.search(tmp, ph.IMAGE_SRC_URI_RE)[1])
        desc = ph.clean_html(ph.find(data, ('<div', '>', 'h1'), '</p>', flags=0)[1])
        itemsList = []
        data = ph.find(data, ('<div', '>', 'finfo'), ('<div', '>', 'berrors'), flags=0)[1]
        data = ph.rfindall(data, '</div>', ('<div', '>', 'finfo-block'), flags=0)
        for item in data:
            key = ph.clean_html(ph.find(item, ('<div', '>', 'title'), '</div>', flags=0)[1])
            if 'Pomoc' in key or 'Prijavi' in key:
                continue
            if 'imdbRatingPlugin' in item:
                url = ('http://p.media-imdb.com/static-content/documents/v1/title/{0}/ratings%3Fjsonp=imdb.rating.run:imdb.api.title.ratings/data.json?u={1}&s={2}').format(ph.getattr(item, 'data-title'), ph.getattr(item, 'data-user'), ph.getattr(item, 'data-style'))
                try:
                    sts, tmp = self.getPage(url)
                    printDBG('>>' + tmp.strip()[16:-1])
                    tmp = json_loads(tmp.strip()[16:-1])['resource']
                    value = '%s (%s)' % (tmp['rating'], tmp['ratingCount'])
                except Exception:
                    printExc()
                    continue
            else:
                value = ph.clean_html(ph.find(item, ('<div', '>', 'text'), '</div>', flags=0)[1].rsplit('</ul>', 1)[(-1)])
            itemsList.append((key, value))
        if title == '':
            title = cItem['title']
        if icon == '':
            icon = cItem.get('icon', self.DEFAULT_ICON_URL)
        if desc == '':
            desc = cItem.get('desc', '')
        return [{'title': ph.clean_html(title), 'text': ph.clean_html(desc), 'images': [{'title': '', 'url': self.getFullUrl(icon)}], 'other_info': {'custom_items_list': itemsList}}]

    def handleService(self, index, refresh=0, searchPattern='', searchType=''):
        printDBG('Fenixsite >>>>>>>>>>>> handleService >> searchPattern = [%s]  searchType = [%s]' % (searchPattern, searchType) )
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        name = self.currItem.get('name', '')
        category = self.currItem.get('category', '')
        printDBG('handleService: ||| name[%s], category[%s] ' % (name, category))
        self.currList = []
        if name == None:
            self.listMain({'name': 'category', 'type': 'category'}, 'list_categories')
        else:
            if category == 'list_filters':
                self.listFilters(self.currItem, 'list_items')
            elif category == 'list_categories':
                self.listCategories(self.currItem, 'list_sort')
            elif category == 'list_sort':
                self.listSort(self.currItem, 'list_items')
            elif category == 'sub_items':
                self.listSubItems(self.currItem)
            elif category == 'list_items':
                self.listItems(self.currItem)
            elif category == 'list_search_items':
                self.listSearchItems(self.currItem)
            else:
                if category in ('search', 'search_next_page'):
                    cItem = dict(self.currItem)
                    cItem.update({'search_item': False, 'name': 'category'})
                    self.listSearchResult(cItem, searchPattern, searchType)
                else:
                    if category == 'search_history':
                        self.listsHistory({'name': 'history', 'category': 'search'}, 'desc', _('Type: '))
                    else:
                        printExc()
        CBaseHostClass.endHandleService(self, index, refresh)
        return


class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, Fenixsite(), True, [])

    def withArticleContent(self, cItem):
        if 'video' == cItem.get('type'):
            return True
        return False

