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
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, byteify, MergeDicts
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs.e2ijson import loads as json_loads
from Plugins.Extensions.IPTVPlayer.libs import ph
import urlparse
import re
import urllib

def gettytul():
    return 'https://ororo.tv/'


class OroroTV(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history': 'ororo.tv',
         'cookie': 'ororo.tv.cookie'})
        self.DEFAULT_ICON_URL = 'http://www.yourkodi.com/wp-content/uploads/2016/02/ororo.png'
        self.USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        self.MAIN_URL = 'https://ororo.tv/'
        self.HEADER = {'User-Agent': self.USER_AGENT,
         'DNT': '1',
         'Accept': 'text/html',
         'Accept-Encoding': 'gzip, deflate',
         'Referer': self.getMainUrl(),
         'Origin': self.getMainUrl()}
        self.AJAX_HEADER = dict(self.HEADER)
        self.AJAX_HEADER.update({'X-Requested-With': 'XMLHttpRequest',
         'Accept-Encoding': 'gzip, deflate',
         'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
         'Accept': 'application/json, text/javascript, */*; q=0.01'})
        self.cacheFilters = {}
        self.cacheLinks = {}
        self.defaultParams = {'header': self.HEADER,
         'use_cookie': True,
         'load_cookie': True,
         'save_cookie': True,
         'cookiefile': self.COOKIE_FILE}
        self.MAIN_CAT_TAB = [{'category': 'list_channels',
          'title': _('Channels'),
          'url': self.getFullUrl('/channels')}, {'category': 'search',
          'title': _('Search'),
          'search_item': True}, {'category': 'search_history',
          'title': _('Search history')}]

    def getPage(self, baseUrl, addParams = {}, post_data = None):
        if addParams == {}:
            addParams = dict(self.defaultParams)
        baseUrl = self.cm.iriToUri(baseUrl)
        addParams['cloudflare_params'] = {'cookie_file': self.COOKIE_FILE,
         'User-Agent': self.USER_AGENT}
        return self.cm.getPageCFProtection(baseUrl, addParams, post_data)

    def listChannels(self, cItem, nextCategory):
        printDBG('OroroTV.listChannels')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        data = self.cm.ph.getDataBeetwenMarkers(data, '"items":', '};', False)[1]
        try:
            data = json_loads(data, '', True)
            for item in data:
                url = self.getFullUrl(item.get('url', ''))
                icon = self.getFullUrl(item.get('banner', ''))
                if icon == '':
                    icon = self.getFullUrl(item.get('image', ''))
                title = self.cleanHtmlStr(item.get('title', ''))
                desc = ' | '.join(item.get('parsed_tags', []))
                if desc != '':
                    desc += ' [/br]'
                desc += self.cleanHtmlStr(item.get('description', ''))
                params = dict(cItem)
                params.update({'good_for_fav': True,
                 'category': nextCategory,
                 'title': title,
                 'desc': desc,
                 'url': url,
                 'icon': icon})
                self.addDir(params)

        except Exception:
            printExc()

    def listItems(self, cItem):
        printDBG('OroroTV.listItems [%s]' % cItem)
        page = cItem.get('page', 1)
        params = MergeDicts(self.defaultParams, {'header': MergeDicts(self.HEADER, {'Accept': 'application/json'})})
        sts, data = self.getPage(cItem['url'] + '?page=' + str(page), params)
        if not sts:
            return
        cUrl = self.cm.meta['url'].split('?', 1)[0]
        try:
            data = json_loads(data)
            count = cItem.get('count', 0)
            for item in data['items']:
                title = ph.clean_html(item['title'])
                icon = 'https://img.youtube.com/vi/%s/mqdefault.jpg' % item['youtube_id']
                url = cUrl + '/videos/' + str(item['id'])
                yUrl = 'https://www.youtube.com/watch?v=%s' % item['youtube_id']
                desc = []
                desc.append(item['airdate'])
                desc.extend(item.get('enabled_subtitles', []))
                desc = ' | '.join(desc) + '[/br]' + ph.clean_html(item['description'])
                self.addVideo(MergeDicts(cItem, {'good_for_fav': True,
                 'title': title,
                 'url': url,
                 'y_url': yUrl,
                 'desc': desc,
                 'icon': icon}))

            if data.get('total_count', 0) > count:
                self.addDir(MergeDicts(cItem, {'title': _('Next page'),
                 'page': page + 1,
                 'count': count + len(self.currList)}))
        except Exception:
            printExc()

    def listSearchResult(self, cItem, searchPattern, searchType):
        printDBG('OroroTV.listSearchResult cItem[%s], searchPattern[%s] searchType[%s]' % (cItem, searchPattern, searchType))
        url = self.getFullUrl('/api/frontend/search?query=') + urllib.quote_plus(searchPattern)
        sts, data = self.getPage(url)
        if not sts:
            return
        data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<a', '</a>')
        for item in data:
            url = self.getFullUrl(self.cm.ph.getSearchGroups(item, 'href=[\'"]([^\'^"]+?)[\'"]')[0])
            icon = self.getFullUrl(self.cm.ph.getSearchGroups(item, 'src=[\'"]([^\'^"]+?)[\'"]')[0])
            tmp = self.cm.ph.getAllItemsBeetwenMarkers(item, '<p', '</p>')
            title = self.cleanHtmlStr(tmp[0])
            desc = self.cleanHtmlStr(tmp[1])
            params = dict(cItem)
            params.update({'good_for_fav': True,
             'title': title,
             'url': url,
             'desc': desc,
             'icon': icon})
            if '/channels/' in url and '/videos/' not in url:
                params['category'] = 'list_items'
                self.addDir(params)
            else:
                self.addVideo(params)

    def getLinksForVideo(self, cItem):
        printDBG('OroroTV.getLinksForVideo [%s]' % cItem)
        retTab = []
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return []
        data = self.cm.ph.getDataBeetwenMarkers(data, '<video', '</video>')[1]
        tmp = self.cm.ph.getDataBeetwenMarkers(data, '<source', '>')[1]
        videoUrl = self.cm.ph.getSearchGroups(tmp, 'src=[\'"](https?://[^\'^"]+?)[\'"]')[0]
        type = self.cm.ph.getSearchGroups(tmp, 'type=[\'"]([^\'^"]+?)[\'"]')[0]
        retTab = self.up.getVideoLinkExt(videoUrl)
        if not retTab:
            retTab = self.up.getVideoLinkExt(cItem.get('y_url', ''))
        if not retTab:
            return []
        subTracks = []
        tmp = self.cm.ph.getAllItemsBeetwenMarkers(data, '<track', '>')
        for item in tmp:
            if 'subtitles' not in item:
                continue
            url = self.cm.ph.getSearchGroups(item, 'src=[\'"](https?://[^\'^"]+?)[\'"]')[0]
            lang = self.cm.ph.getSearchGroups(item, 'label=[\'"]([^\'^"]+?)[\'"]')[0]
            title = self.cm.ph.getSearchGroups(item, 'title=[\'"]([^\'^"]+?)[\'"]')[0]
            if url != '':
                subTracks.append({'title': title,
                 'url': url,
                 'lang': lang,
                 'format': url[-3:]})

        if len(subTracks):
            for idx in range(len(retTab)):
                tmp = list(subTracks)
                tmp.extend(retTab[idx]['url'].meta.get('external_sub_tracks', []))
                retTab[idx]['url'] = strwithmeta(retTab[idx]['url'], {'external_sub_tracks': list(tmp)})

        return retTab

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
        elif category == 'list_channels':
            self.listChannels(self.currItem, 'list_items')
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
        CHostBase.__init__(self, OroroTV(), True, [])