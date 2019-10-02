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
from Plugins.Extensions.IPTVPlayer.libs import ph
import urllib

def gettytul():
    return 'http://filma24.cc/'


class Filma24IO(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history': 'Filma24IO',
         'cookie': 'Filma24IO.cookie'})
        self.MAIN_URL = 'http://www.filma24.cc/'
        self.DEFAULT_ICON_URL = self.getFullIconUrl('wp-content/themes/cr_filma_greenv2/assets/img/logo2019.png')
        self.cacheLinks = {}

    def getPage(self, baseUrl, addParams = {}, post_data = None):
        return self.cm.getPage(baseUrl, addParams, post_data)

    def listMain(self, cItem):
        printDBG('Filma24IO.listMain')
        sts, data = self.getPage(self.getMainUrl())
        if not sts:
            return
        self.setMainUrl(self.cm.meta['url'])
        subItems = []
        tmp = ph.find(data, ('<div', '>', 'sort'), '</ul>', flags=0)[1]
        tmp = ph.findall(tmp, ('<a', '>'), '</a>', flags=ph.START_S)
        for idx in range(1, len(tmp), 2):
            url = self.getFullUrl(ph.search(tmp[idx - 1], ph.A)[1])
            title = ph.clean_html(tmp[idx])
            subItems.append(MergeDicts(cItem, {'title': title,
             'url': url,
             'category': 'list_items'}))

        tmp = ph.find(data, ('<div', '>', 'head-menu'), ('<div', '>', 'head-categories'), flags=0)[1]
        tmp = ph.findall(tmp, ('<a', '>'), '</a>', flags=ph.START_S)
        for idx in range(1, len(tmp), 2):
            url = self.getFullUrl(ph.getattr(tmp[idx - 1], 'href'))
            title = ph.clean_html(tmp[idx])
            icon = self.getFullIconUrl(ph.search(tmp[idx], ph.IMG)[1])
            if subItems:
                params = {'category': 'sub_items',
                 'sub_items': subItems}
                subItems = []
            else:
                params = {'category': 'list_items'}
            self.addDir(MergeDicts(cItem, params, {'title': title,
             'url': url,
             'icon': icon}))

        subItems = []
        tmp = ph.find(data, ('<div', '>', 'head-categories'), '</div>', flags=0)[1]
        sTitle = ph.clean_html(ph.find(tmp, ('<a', '>'), '</a>', flags=0)[1])
        sIcon = self.getFullIconUrl(ph.search(tmp[idx], ph.IMG)[1])
        tmp = ph.findall(tmp, ('<li', '>'), '</li>', flags=0)
        for item in tmp:
            if '_blank' in item:
                continue
            url = self.getFullUrl(ph.search(item, ph.A)[1])
            title = ph.clean_html(item)
            subItems.append(MergeDicts(cItem, {'title': title,
             'icon': sIcon,
             'url': url,
             'category': 'list_items'}))

        if subItems:
            self.addDir(MergeDicts(cItem, {'title': sTitle,
             'category': 'sub_items',
             'sub_items': subItems,
             'icon': sIcon}))
        MAIN_CAT_TAB = [{'category': 'search',
          'title': _('Search'),
          'search_item': True}, {'category': 'search_history',
          'title': _('Search history')}]
        self.listsTab(MAIN_CAT_TAB, cItem)

    def listItems(self, cItem, nextCategory):
        printDBG('Filma24IO.listItems [%s]' % cItem)
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        page = cItem.get('page', 1)
        nextPage = self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'pagination'), ('</div', '>'), False)[1]
        nextPage = self.cm.ph.getDataBeetwenNodes(nextPage, ('<a', '>', 'next'), ('</a', '>'))[1]
        nextPage = self.getFullUrl(self.cm.ph.getSearchGroups(nextPage, 'href=[\'"]([^"^\']+?)["\']', 1, True)[0])
        if '/seriale/' in cItem['url']:
            baseTitle = ph.clean_html(self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'category-head'), ('</div', '>'))[1]) + ' : %s'
            data = self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'post-'), ('<div', '>', 'footer'))[1]
        else:
            baseTitle = '%s'
            data = self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'post-'), ('<div', '>', 'pagination'))[1]
        data = self.cm.ph.rgetAllItemsBeetwenNodes(data, ('</div', '>'), ('<div', '>', 'post-'))
        for item in data:
            url = self.getFullUrl(self.cm.ph.getSearchGroups(item, 'href=[\'"]([^"^\']+?)["\']', 1, True)[0])
            if url == '':
                continue
            icon = self.cm.ph.getSearchGroups(item, 'image\\:url\\(([^\\)]+?)\\)', 1, True)[0].strip()
            if icon[:1] in ('"', "'"):
                icon = icon[1:-1]
            if icon == '':
                icon = self.cm.ph.getSearchGroups(item, '\\ssrc=[\'"]([^"^\']+?\\.(?:jpe?g|png)(?:\\?[^\'^"]*?)?)[\'"]')[0]
            title = ph.clean_html(self.cm.ph.getDataBeetwenNodes(item, ('<h', '>'), ('</h', '>'), False)[1])
            desc = []
            t = self.cm.ph.getDataBeetwenNodes(item, ('<div', '>', 'tags'), ('</div', '>'), False)[1]
            tmp = self.cm.ph.getAllItemsBeetwenNodes(item, ('<div', '>', '-poster'), ('</div', '>'), False)
            tmp.extend(self.cm.ph.getAllItemsBeetwenMarkers(t, '<li', '</li>'))
            for t in tmp:
                t = ph.clean_html(t)
                if t != '':
                    desc.append(t)

            params = dict(cItem)
            params.update({'good_for_fav': True,
             'title': baseTitle % title,
             'url': url,
             'desc': ' | '.join(desc),
             'icon': self.getFullIconUrl(icon)})
            if '/seriale/' not in url:
                params['category'] = nextCategory
            self.addDir(params)

        if nextPage != '':
            params = dict(cItem)
            params.update({'good_for_fav': False,
             'title': _('Next page'),
             'page': page + 1,
             'url': nextPage})
            self.addDir(params)

    def exploreItem(self, cItem):
        printDBG('Filma24IO.exploreItem')
        self.cacheLinks = {}
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        cUrl = self.cm.meta['url']
        self.setMainUrl(cUrl)
        desc = []
        try:
            descObj = self.getArticleContent(cItem, data)[0]
            for item in descObj['other_info']['custom_items_list']:
                desc.append(item[1])

            desc = ' | '.join(desc) + '[/br]' + descObj['text']
        except Exception:
            printExc()

        trailerUrl = ph.find(data, ('<div', '>', 'trailer-player'), '</div>', flags=0)[1]
        trailerUrl = self.getFullUrl(ph.search(trailerUrl, ph.IFRAME)[1])
        if trailerUrl:
            trailerUrl = strwithmeta(trailerUrl, {'Referer': cItem['url']})
            params = {'good_for_fav': False,
             'title': '%s - %s' % (cItem['title'], _('trailer')),
             'url': trailerUrl,
             'trailer': True,
             'desc': desc,
             'prev_url': cItem['url']}
            self.addVideo(MergeDicts(cItem, params))
        self.cacheLinks[cUrl] = []
        tmp = ph.findall(data, ('<ul', '>', 'w-links'), '</ul>', flags=0)
        for tmpItem in tmp:
            tmpItem = ph.findall(tmpItem, ('<a', '>'), '</a>', flags=ph.START_S)
            for idx in range(1, len(tmpItem), 2):
                name = ph.clean_html(tmpItem[idx])
                url = self.getFullUrl(ph.getattr(tmpItem[idx - 1], 'href'))
                self.cacheLinks[cUrl].append({'name': name,
                 'url': url,
                 'need_resolve': 1})

        tmp = ph.find(data, ('<div', '>', 'movie-player'), '</div>', flags=0)[1]
        url = self.getFullUrl(ph.search(tmp, ph.IFRAME)[1])
        if url:
            self.cacheLinks[cUrl].insert(0, {'name': self.cm.getBaseUrl(url, True).upper(),
             'url': url,
             'need_resolve': 1})
        if len(self.cacheLinks[cUrl]):
            self.addVideo(MergeDicts(cItem, {'good_for_fav': False,
             'url': cUrl,
             'desc': desc,
             'prev_url': cItem['url']}))

    def listSearchResult(self, cItem, searchPattern, searchType):
        searchPattern = urllib.quote_plus(searchPattern)
        cItem = dict(cItem)
        cItem['url'] = self.getFullUrl('/?s=') + urllib.quote_plus(searchPattern)
        cItem['category'] = 'list_items'
        self.listItems(cItem, 'explore_item')

    def getLinksForVideo(self, cItem):
        printDBG('Filma24IO.getLinksForVideo [%s]' % cItem)
        if 'trailer' in cItem:
            return self.up.getVideoLinkExt(cItem['url'])
        return self.cacheLinks.get(cItem['url'], [])

    def getVideoLinks(self, videoUrl):
        printDBG('Filma24IO.getVideoLinks [%s]' % videoUrl)
        if len(self.cacheLinks.keys()):
            for key in self.cacheLinks:
                for idx in range(len(self.cacheLinks[key])):
                    if videoUrl in self.cacheLinks[key][idx]['url']:
                        if not self.cacheLinks[key][idx]['name'].startswith('*'):
                            self.cacheLinks[key][idx]['name'] = '*' + self.cacheLinks[key][idx]['name']

        if 0 == self.up.checkHostSupport(videoUrl):
            from Plugins.Extensions.IPTVPlayer.libs.unshortenit import unshorten
            uri, sts = unshorten(videoUrl)
            uri = str(uri)
            if self.cm.isValidUrl(uri):
                videoUrl = uri
        return self.up.getVideoLinkExt(videoUrl)

    def getArticleContent(self, cItem, data = None):
        printDBG('Altadefinizione.getArticleContent [%s]' % cItem)
        retTab = []
        url = cItem.get('prev_url', cItem['url'])
        if data == None:
            sts, data = self.getPage(url)
            if not sts:
                data = ''
        data = self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'movie-info'), ('<div', '>', 'watch-links'), False)[1]
        icon = ''
        if '/seria/' in url:
            title = ''
        else:
            title = ph.clean_html(self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'title'), ('</div', '>'), False)[1])
        desc = ph.clean_html(self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'synopsis'), ('</div', '>'), False)[1])
        itemsList = []
        tmp = self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'info-right'), ('</div', '>'), False)[1]
        tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<span', '</span>')
        for idx in range(1, len(tmp), 2):
            key = ph.clean_html(tmp[idx - 1])
            val = ph.clean_html(tmp[idx])
            if key == '' or val == '':
                continue
            itemsList.append((key, val))

        tmp = ph.clean_html(self.cm.ph.getDataBeetwenNodes(data, ('<span', '>', 'movie-len'), ('</span', '>'), False)[1])
        if tmp != '':
            itemsList.append((_('Duration:'), tmp))
        data = self.cm.ph.getDataBeetwenNodes(data, ('<ul', '>', 'genre'), ('</ul', '>'), False)[1]
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li', '</li>')
        tmp = []
        for t in data:
            t = ph.clean_html(t)
            if t != '':
                tmp.append(t)

        if len(tmp):
            itemsList.append((_('Genres:'), ', '.join(tmp)))
        if title == '':
            title = cItem['title']
        if icon == '':
            icon = cItem.get('icon', self.DEFAULT_ICON_URL)
        if desc == '':
            desc = cItem.get('desc', '')
        return [{'title': ph.clean_html(title),
          'text': ph.clean_html(desc),
          'images': [{'title': '',
                      'url': self.getFullUrl(icon)}],
          'other_info': {'custom_items_list': itemsList}}]

    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        name = self.currItem.get('name', '')
        category = self.currItem.get('category', '')
        printDBG('handleService: ||| name[%s], category[%s] ' % (name, category))
        self.currList = []
        if name == None:
            self.listMain({'name': 'category',
             'type': 'category'})
        elif category == 'sub_items':
            self.listSubItems(self.currItem)
        elif category == 'list_items':
            self.listItems(self.currItem, 'explore_item')
        elif category == 'explore_item':
            self.exploreItem(self.currItem)
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
        CHostBase.__init__(self, Filma24IO(), True, [])

    def withArticleContent(self, cItem):
        if 'prev_url' in cItem or cItem.get('category', '') == 'explore_item':
            return True
        else:
            return False