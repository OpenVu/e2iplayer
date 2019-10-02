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

from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _, GetIPTVNotify
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc, rm, MergeDicts
from Plugins.Extensions.IPTVPlayer.libs.e2ijson import loads as json_loads
from Plugins.Extensions.IPTVPlayer.libs import ph
from Plugins.Extensions.IPTVPlayer.libs.youtube_dl.extractor.bbc import BBCCoUkIE

import urllib
import re

from datetime import datetime, timedelta
from Components.config import config, ConfigText, getConfigListEntry
config.plugins.iptvplayer.bbc_login = ConfigText(default='', fixed_size=False)
config.plugins.iptvplayer.bbc_password = ConfigText(default='', fixed_size=False)

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry(_('Use web-proxy (it may be illegal):'), config.plugins.iptvplayer.bbc_use_web_proxy))
    if not config.plugins.iptvplayer.bbc_use_web_proxy.value:
        optionList.append(getConfigListEntry(_('e-mail') + ':', config.plugins.iptvplayer.bbc_login))
        optionList.append(getConfigListEntry(_('password') + ':', config.plugins.iptvplayer.bbc_password))
    optionList.append(getConfigListEntry(_('Default video quality:'), config.plugins.iptvplayer.bbc_default_quality))
    optionList.append(getConfigListEntry(_('Use default video quality:'), config.plugins.iptvplayer.bbc_use_default_quality))
    optionList.append(getConfigListEntry(_('Preferred format:'), config.plugins.iptvplayer.bbc_prefered_format))
    return optionList


def gettytul():
    return 'https://www.bbc.co.uk/sport'


class BBCSport(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history': 'bbc.com.sport',
         'cookie': 'bbc.com.sport.cookie'})
        self.MAIN_URL = 'https://www.bbc.co.uk/'
        self.DEFAULT_ICON_URL = 'https://pbs.twimg.com/profile_images/878266143571443712/goIG59xP_400x400.jpg'
        self.HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0',
         'DNT': '1',
         'Accept': 'text/html',
         'Accept-Encoding': 'gzip, deflate'}
        self.AJAX_HEADER = dict(self.HEADER)
        self.AJAX_HEADER.update({'X-Requested-With': 'XMLHttpRequest'})
        self.defaultParams = {'with_metadata': True,
         'ignore_http_code_ranges': [],
         'header': self.HEADER,
         'use_cookie': True,
         'load_cookie': True,
         'save_cookie': True,
         'cookiefile': self.COOKIE_FILE}
        self.loggedIn = None
        self.login = ''
        self.password = ''
        self.sessionUrl = 'https://session.bbc.com/session'
        self.liveGuideItemsCache = {}
        self.OFFSET = datetime.now() - datetime.utcnow()
        seconds = self.OFFSET.seconds + self.OFFSET.days * 24 * 3600
        if (seconds + 1) % 10 == 0:
            seconds += 1
        elif (seconds - 1) % 10 == 0:
            seconds -= 1
        self.OFFSET = timedelta(seconds=seconds)
        self.ABBREVIATED_DAYS_NAME_TAB = ['Mon',
         'Tue',
         'Wed',
         'Thu',
         'Fri',
         'Sat',
         'Sun']
        return

    def _str2date(self, txt):
        txt = ph.search(txt, '([0-9]+\\-[0-9]+\\-[0-9]+T[0-9]+\\:[0-9]+:[0-9]+)')[0]
        return datetime.strptime(txt, '%Y-%m-%dT%H:%M:%S')

    def _gmt2local(self, txt):
        utc_date = self._str2date(txt)
        utc_date = utc_date + self.OFFSET
        if utc_date.time().second == 59:
            utc_date = utc_date + timedelta(0, 1)
        return utc_date

    def _absTimeDelta(self, d1, d2, div = 60):
        if d1 > d2:
            td = d1 - d2
        else:
            td = d2 - d1
        return (td.seconds + td.days * 24 * 3600) / div

    def getFullIconUrl(self, icon, baseUrl = None):
        return CBaseHostClass.getFullIconUrl(self, icon, baseUrl).replace('/$recipe/', '/480x270_b/')

    def getPage(self, url, addParams = {}, post_data = None):
        if addParams == {}:
            addParams = dict(self.defaultParams)
        return self.cm.getPage(url, addParams, post_data)

    def listMainMenu(self, cItem, nextCategory1, nextCategory2):
        printDBG('BBCSport.listMainMenu')
        url = self.getFullUrl('/sport/snooker')
        sts, data = self.getPage(url)
        if not sts:
            return
        self.setMainUrl(data.meta['url'])
        liveguideData = ph.find(data, ('<aside', '</aside>', 'liveguide'), ('<div', '</div>'))[1]
        icon = self.getFullIconUrl(ph.search(liveguideData, ph.IMG)[1])
        url = self.getFullUrl(ph.search(liveguideData, ph.A)[1])
        if url:
            title = ph.clean_html(ph.getattr(liveguideData, 'alt'))
            desc = ph.clean_html(ph.find(liveguideData, ('<p', '>', 'summary'), '</p>', flags=0)[1])
            self.addDir(MergeDicts(cItem, {'good_for_fav': True,
             'category': 'live_guide',
             'title': title,
             'url': url,
             'icon': icon,
             'desc': desc}))
        data = ph.find(data, ('<nav', '>', 'primary-nav'), ('</nav', '>'), flags=0)[1]
        data = ph.findall(data, ('<li', '>'), '</li>', flags=0)
        for item in data:
            url = self.getFullUrl(ph.search(item, ph.A)[1])
            if not self.cm.isValidUrl(url):
                continue
            if '/my-sport' in url:
                continue
            title = ph.clean_html(item)
            if '/all-sports' in url:
                category = nextCategory2
            else:
                category = nextCategory1
            self.addDir(MergeDicts(cItem, {'good_for_fav': True,
             'category': category,
             'title': title,
             'url': url}))

    def listAllItems(self, cItem, nextCategory):
        printDBG('BBCSport.listAllItems')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        data = ph.findall(data, ('<li', '>', 'list-item'), '</li>', flags=0)
        for item in data:
            url = self.getFullUrl(ph.search(item, ph.A)[1])
            if not url:
                continue
            title = ph.clean_html(item)
            self.addDir(MergeDicts(cItem, {'good_for_fav': True,
             'category': nextCategory,
             'title': title,
             'url': url}))

    def listLiveGuideMenu(self, cItem, nextCategory):
        printDBG('BBCSport.listLiveGuideMenu')
        self.liveGuideItemsCache = {}
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        mediaDataTab = []
        mediaData = ''
        tmp = ph.findall(data, '.setPayload(', '</script>', flags=0)
        for item in tmp:
            if '"promoted"' in item:
                mediaData = item
                break

        mediaData = ph.findblock(mediaData, '{', '}', beg=mediaData.find('"body":{') + 7)
        try:
            mediaData = json_loads(mediaData, '', True)
            for item in [{'key': 'promoted',
              'title': _('Promoted')},
             {'key': 'live',
              'title': _('Live')},
             {'key': 'coming_up',
              'title': _('Coming up')},
             {'key': 'catch_up',
              'title': _('Catch up')}]:
                try:
                    if isinstance(mediaData[item['key']], list) and len(mediaData[item['key']]):
                        self.liveGuideItemsCache[item['key']] = mediaData[item['key']]
                        params = dict(cItem)
                        params.update({'good_for_fav': False,
                         'category': nextCategory,
                         'title': item['title'],
                         'f_key': item['key']})
                        self.addDir(params)
                except Exception:
                    printExc()

        except Exception:
            printExc()

    def listLiveGuideItems(self, cItem, nextCategory):
        printDBG('BBCSport.listLiveGuideItems')
        try:
            NOW = datetime.now()
            for datItem in self.liveGuideItemsCache[cItem['f_key']]:
                sDate = self._gmt2local(datItem['scheduledStartTime'])
                if (datItem['hasAudio'] or datItem['hasVideo']) and datItem['status'] != 'COMING_UP':
                    for item in datItem['media']:
                        if 'identifiers' not in item or 'playablePid' not in item['identifiers']:
                            continue
                        vpid = item['identifiers']['playablePid']
                        if vpid == '':
                            continue
                        url = self.getFullUrl('/iplayer/vpid/%s/' % vpid)
                        icon = self.getFullIconUrl(item['coverImage'])
                        title = ph.clean_html(item['title'])
                        mediaType = item['mediaType']
                        if 'COMING_SOON' in item['status']:
                            continue
                        desc = [datItem['sectionName'], item['status']]
                        if 'schedule' in item and 'formattedStartTime' in item['schedule']:
                            desc.append('%s-%s' % (item['schedule']['formattedStartTime'], item['schedule']['formattedEndTime']))
                        h = ph.search(item.get('duration', ''), '([0-9]+)H')[0]
                        if h == '':
                            h = '0'
                        m = ph.search(item.get('duration', ''), '([0-9]+)M')[0]
                        if m == '':
                            m = '0'
                        if m != '0' or h != '0':
                            desc.append(str(timedelta(hours=int(h), minutes=int(m))))
                        desc = [' | '.join(desc)]
                        desc.append(ph.clean_html(item['summary']))
                        params = dict(cItem)
                        params = {'good_for_fav': True,
                         'title': title,
                         'url': url,
                         'icon': icon,
                         'desc': '[/br]'.join(desc)}
                        if mediaType == 'video':
                            self.addVideo(params)
                        elif mediaType == 'audio':
                            self.addAudio(params)
                        else:
                            printDBG('Unknown media type\n%s\n>>>>' % mediaType)

                else:
                    url = self.getFullUrl(datItem['url'])
                    title = ph.clean_html(datItem['shortTitle'])
                    icon = self.getFullIconUrl(datItem['image']['href'])
                    desc = [datItem['sectionName']]
                    diff = sDate.day - NOW.day
                    if diff >= 0 and diff < 7:
                        if NOW.day == sDate.day:
                            desc.append('%s:%s' % (str(sDate.hour).zfill(2), str(sDate.minute).zfill(2)))
                        elif diff == 1:
                            desc.append('Tomorrow at %s:%s' % (str(sDate.hour).zfill(2), str(sDate.minute).zfill(2)))
                        else:
                            desc.append('%s at %s:%s' % (self.ABBREVIATED_DAYS_NAME_TAB[sDate.weekday()], str(sDate.hour).zfill(2), str(sDate.minute).zfill(2)))
                    else:
                        desc.append('%s at %s:%s' % (sDate.strftime('%Y-%m-%d'), str(sDate.hour).zfill(2), str(sDate.minute).zfill(2)))
                    desc = [' | '.join(desc)]
                    desc.append(ph.clean_html(datItem['summary']))
                    self.addDir(MergeDicts(cItem, {'good_for_fav': True,
                     'category': nextCategory,
                     'title': title,
                     'url': url,
                     'icon': icon,
                     'desc': '[/br]'.join(desc)}))

        except Exception:
            printExc()

    def listSubMenu(self, cItem, nextCategory1, nextCategory2):
        printDBG('BBCSport.listSubMenu')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        cItem = dict(cItem)
        cItem.update({'category': nextCategory1})
        self.listItems(cItem, nextCategory2, data)

    def listItems(self, cItem, nextCategory, data = None):
        printDBG('BBCSport.listItems')
        if data == None:
            sts, data = self.getPage(cItem['url'])
            if not sts:
                return
        liveItemList = []
        maediaList = []
        othersList = []
        reObj = re.compile('\\ssrc=[\'"]([^"^\']+?\\.(?:jpe?g|png)(?:\\?[^"^\']+?)?)[\'"]', re.I)
        sections = ph.findall(data, ('<section', '>'), '</section>')
        for mediaData in sections:
            if 'id="audio-video"' in mediaData:
                promote = True
            else:
                promote = False
            mediaData = ph.findall(mediaData, ('<article', '>', 'has-media'), '</article>')
            for item in mediaData:
                tmp = ph.find(item, ('<h3', '>'), '</h3>')[1]
                url = self.getFullUrl(ph.search(tmp, ph.A)[1])
                if not url:
                    continue
                title = ph.clean_html(tmp)
                icon = self.getFullIconUrl(ph.search(item, reObj)[0])
                desc = []
                tmp = ph.find(item, ('<div', '>', '_meta'), '</div>', flags=0)[1]
                tmp = ph.findall(tmp, ('<li', '>'), '</li>', flags=0)
                for t in tmp:
                    t = ph.clean_html(t)
                    if t != '':
                        desc.append(t)

                desc = ' | '.join(desc)
                if desc == '':
                    desc = []
                else:
                    desc = [desc]
                desc.append(ph.clean_html(ph.find(item, ('<p', '>', 'summary'), '</p>', flags=0)[1]))
                params = MergeDicts(cItem, {'good_for_fav': True,
                 'title': title,
                 'url': url,
                 'icon': icon,
                 'desc': '[/br]'.join(desc)})
                if 'gelicon--listen' in item:
                    params['type'] = 'audio'
                    maediaList.append(params)
                elif 'gelicon--play' in item:
                    params['type'] = 'video'
                    maediaList.append(params)
                else:
                    params.update({'type': 'category',
                     'category': nextCategory})
                    if 'gelicon--live' in item:
                        liveItemList.append(params)
                    else:
                        othersList.append(params)
                    printDBG('Unknown media type\n%s\n>>>>' % item)

        mediaData = ph.findblock(data, '[', ']', beg=data.find('"clusters":[') + 11)
        if mediaData:
            try:
                mediaData = json_loads(mediaData)
                for sItem in mediaData:
                    for item in sItem['items']:
                        mediaType = item['type'].lower()
                        if mediaType not in ('video', 'audio'):
                            printDBG('Unknown media type\n%s\n>>>>' % mediaType)
                            continue
                        url = self.getFullUrl(item['link'])
                        title = ph.clean_html(item['title'])
                        icon = self.getFullIconUrl(item['image']['url'])
                        d = self._gmt2local(item['publishedDateTime'])
                        d = '%s at %s:%s' % (d.strftime('%Y-%m-%d'), str(d.hour).zfill(2), str(d.minute).zfill(2))
                        desc = '%s | %s[/br]%s' % (item['type'], d, ph.clean_html(item['summary']))
                        params = MergeDicts(cItem, {'good_for_fav': True,
                         'type': mediaType,
                         'title': title,
                         'url': url,
                         'icon': icon,
                         'desc': desc})
                        if item.get('isLive'):
                            liveItemList.append(params)
                        else:
                            maediaList.append(params)

            except Exception:
                printExc()

        self.currList.extend(liveItemList)
        self.currList.extend(maediaList)
        self.currList.extend(othersList)
        return

    def exploreItem(self, cItem):
        printDBG('BBCSport.exploreItem')
        sts, data = self.getPage(cItem['url'])
        if not sts:
            return
        mediaDataTab = []
        tmp = ph.findall(data, '.setPayload(', '</script>', flags=0)
        for mediaData in tmp:
            mediaData = ph.findblock(mediaData, '{', '}', beg=mediaData.find('"body":{') + 7)
            if mediaData:
                try:
                    mediaData = json_loads(mediaData)
                    if 'components' in mediaData:
                        for item in mediaData['components']:
                            try:
                                if item['props']['supportingMedia']:
                                    mediaDataTab.extend(item['props']['supportingMedia'])
                                if item['props']['leadMedia']:
                                    mediaDataTab.append(item['props']['leadMedia'])
                            except Exception:
                                printExc()

                    if 'sessions' in mediaData:
                        for item in mediaData['sessions']:
                            try:
                                mediaDataTab.extend(item['media'])
                            except Exception:
                                printExc()

                except Exception:
                    printExc()

        for item in mediaDataTab:
            try:
                if 'identifiers' not in item or 'playablePid' not in item['identifiers']:
                    continue
                vpid = item['identifiers']['playablePid']
                if vpid == '':
                    continue
                url = self.getFullUrl('/iplayer/vpid/%s/' % vpid)
                icon = self.getFullIconUrl(item['coverImage'])
                title = ph.clean_html(item['title'])
                mediaType = item['mediaType'].lower()
                if mediaType not in ('video', 'audio'):
                    printDBG('Unknown media type\n%s\n>>>>' % mediaType)
                    continue
                if 'COMING_SOON' in item['status']:
                    printDBG('SKIP media with status \n%s\n>>>>' % item['status'])
                    continue
                desc = [item['status']]
                if 'schedule' in item and 'formattedStartTime' in item['schedule']:
                    desc.append('%s-%s' % (item['schedule']['formattedStartTime'], item['schedule']['formattedEndTime']))
                elif 'duration' in item and 'formattedDuration' in item['duration']:
                    desc.append(item['duration']['formattedDuration'])
                desc = [' | '.join(desc)]
                desc.append(ph.clean_html(item['summary']))
                self.currList.append(MergeDicts(cItem, {'good_for_fav': True,
                 'type': mediaType,
                 'title': title,
                 'url': url,
                 'icon': icon,
                 'desc': '[/br]'.join(desc)}))
            except Exception:
                printExc()

        tmp = ph.findall(data, ('<div', '>', 'data-media-type'), '</div>')
        for item in tmp:
            mediaType = ph.getattr(item, 'data-media-type')
            mediaType = ph.getattr(item, 'data-content-type').lower()
            if mediaType not in ('video', 'audio'):
                printDBG('Unknown media type\n%s\n>>>>' % mediaType)
                continue
            vpid = ph.getattr(item, 'data-media-vpid')
            title = ph.getattr(item, 'data-title')
            icon = ph.getattr(item, 'data-image-url')
            duration = ph.getattr(item, 'data-media-duration')
            if vpid == '':
                continue
            url = self.getFullUrl('/iplayer/vpid/%s/' % vpid)
            self.currList.append(MergeDicts(cItem, {'good_for_fav': True,
             'type': mediaType,
             'title': title,
             'url': url,
             'icon': icon,
             'desc': duration}))

    def listSubItems(self, cItem):
        printDBG('BBCSport.listSubItems')
        self.currList = cItem['sub_items']

    def tryTologin(self):
        printDBG('BBCSport.tryTologin start')
        netErrorMsg = _('Error communicating with the server.')
        datErrorMsg = _('Data mismatch.')
        if config.plugins.iptvplayer.bbc_use_web_proxy.value:
            if False != self.loggedIn:
                rm(self.COOKIE_FILE)
                self.loggedIn = False
            return False
        elif None == self.loggedIn or self.login != config.plugins.iptvplayer.bbc_login.value or self.password != config.plugins.iptvplayer.bbc_password.value:
            self.login = config.plugins.iptvplayer.bbc_login.value
            self.password = config.plugins.iptvplayer.bbc_password.value
            rm(self.COOKIE_FILE)
            self.loggedIn = False
            self.loginMessage = ''
            if '' == self.login.strip() or '' == self.password.strip():
                return False
            sts, data = self.getPage(self.getFullUrl('/sport'))
            if not sts:
                msg = _(netErrorMsg) + _('\nError[1].')
                GetIPTVNotify().push(msg, 'error', 10)
                return False
            cUrl = data.meta['url']
            self.setMainUrl(cUrl)
            try:
                url = self.sessionUrl + '?ptrt=' + urllib.quote(cUrl.split('?', 1)[0]) + '&userOrigin=sport&context=sport'
                sts, data = self.getPage(url)
                if not sts:
                    msg = _(netErrorMsg) + _('\nError[2].')
                    GetIPTVNotify().push(msg, 'error', 10)
                    return False
                cUrl = data.meta['url']
                sts, data = ph.find(data, ('<form', '>'), '</form>')
                if not sts:
                    msg = _(datErrorMsg) + _('\nError[3].')
                    GetIPTVNotify().push(msg, 'error', 10)
                    return False
                actionUrl = self.cm.getFullUrl(ph.getattr(data, 'action')[0].replace('&amp;', '&'), cUrl)
                if actionUrl == '':
                    actionUrl = cUrl
                formData = ph.findall(data, '<input', '>')
                post_data = {}
                for item in formData:
                    name = ph.getattr(item, 'name')
                    value = ph.getattr(item, 'value')
                    post_data[name] = value

                post_data.update({'username': self.login,
                 'password': self.password})
                httpParams = dict(self.defaultParams)
                httpParams['header'] = MergeDicts(httpParams['header'], {'Referer': self.getMainUrl()})
                sts, data = self.cm.getPage(actionUrl, httpParams, post_data)
                if sts:
                    printDBG('tryTologin OK')
                    if '/signin' in data.meta['url']:
                        msg = ph.clean_html(ph.find(data, ('<p', '>', 'form-message'), '</p>', flags=0)[1])
                        GetIPTVNotify().push(_('Login failed.') + '\n' + msg, 'error', 10)
                        return False
                    self.loggedIn = True
                    msg = _('A TV License is required to watch BBC iPlayer streams, see the BBC website for more information: https://www.bbc.co.uk/iplayer/help/tvlicence')
                    GetIPTVNotify().push(msg, 'info', 5)
                    self.loginMessage = msg
                else:
                    msg = _(netErrorMsg) + _('\nError[4].')
                    GetIPTVNotify().push(msg, 'error', 10)
                    return False
            except Exception:
                printExc()

            printDBG('EuroSportPlayer.tryTologin end loggedIn[%s]' % self.loggedIn)
            return self.loggedIn
        else:
            return

    def getLinksForVideo(self, cItem):
        printDBG('BBCSport.getLinksForVideo [%s]' % cItem)
        self.tryTologin()
        urlTab = []
        if '/vpid/' in cItem['url']:
            urlTab.append({'name': cItem['title'],
             'url': cItem['url'],
             'need_resolve': 1})
        else:
            sts, data = self.getPage(cItem['url'])
            if not sts:
                return urlTab
            cUrl = self.cm.meta['url']
            mediaData = ph.find(data, '.setPayload(', '</script>', flags=0)[1]
            mediaData = ph.findblock(mediaData, '{', '}', beg=mediaData.find('"body":{') + 7)
            if mediaData:
                try:
                    mediaData = json_loads(mediaData)
                    if mediaData['media'] and mediaData['media']['mediaType'].lower() == 'video' and '' != mediaData['media']['pid']:
                        url = self.getFullUrl('/iplayer/vpid/%s/' % mediaData['media']['pid'])
                        urlTab.append({'name': mediaData['media']['entityType'],
                         'url': url,
                         'need_resolve': 1})
                except Exception:
                    printExc()

            mediaData = ph.find(data, '"allAvailableVersions"', '"holdingImage"', flags=0)[1].strip()[1:-1].strip()
            if mediaData:
                try:
                    uniqueTab = set()
                    mediaData = json_loads(mediaData, '', True)
                    for tmp in mediaData:
                        title = ph.clean_html(tmp['smpConfig']['title'])
                        for item in tmp['smpConfig']['items']:
                            url = self.getFullUrl('/iplayer/vpid/%s/' % item['vpid'])
                            if url not in uniqueTab:
                                uniqueTab.add(url)
                                name = item['kind'].title()
                                urlTab.append({'name': '[%s] %s' % (name, title),
                                 'url': url,
                                 'need_resolve': 1})

                except Exception:
                    printExc()

            mediaData = ph.find(data, ('<div', '>', 'player-wrapper'), '</div>', flags=0)[1]
            mediaData = ph.clean_html(ph.getattr(mediaData, 'data-playable'))
            if mediaData:
                try:
                    mediaData = json_loads(mediaData)
                    title = mediaData['settings']['playlistObject']['title']
                    for item in mediaData['settings']['playlistObject']['items']:
                        url = self.getFullUrl('/iplayer/vpid/%s/' % item['vpid'])
                        name = item['kind'].title()
                        urlTab.append({'name': '[%s] %s' % (name, title),
                         'url': url,
                         'need_resolve': 1})

                except Exception:
                    printExc()

            if '/programmes/' in cUrl:
                url = ph.find(data, ('<a', '>', 'iplayer_episodepage_playcurrent'))[1]
                url = self.getFullUrl(ph.getattr(url, 'href'), cUrl)
                sts, data = self.getPage(url)
                if not sts:
                    return urlTab
                cUrl = self.cm.meta['url']
                mediaData = ph.findblock(data, '{', '}', beg=data.find('"current":{') + 10)
                if mediaData:
                    try:
                        uniqueTab = set()
                        for key, value in json_loads(mediaData)['download']['quality_variants'].iteritems():
                            url = self.getFullUrl(value['file_url'], cUrl)
                            if url not in uniqueTab:
                                uniqueTab.add(url)
                                urlTab.append({'name': key,
                                 'url': url,
                                 'need_resolve': 0})

                    except Exception:
                        printExc()

        return urlTab

    def getVideoLinks(self, videoUrl):
        printDBG('BBCSport.getVideoLinks [%s]' % videoUrl)
        urlTab = []
        if videoUrl:
            urlTab = self.up.getVideoLinkExt(videoUrl)
        return urlTab

    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        printDBG('handleService start')
        CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
        self.informAboutGeoBlockingIfNeeded('GB')
        self.tryTologin()
        category = self.currItem.get('category', '')
        printDBG('handleService: >> category[%s] ' % category)
        self.currList = []
        if not category:
            self.listMainMenu({}, 'sub_menu', 'all_items')
        elif category == 'all_items':
            self.listAllItems(self.currItem, 'sub_menu')
        elif category == 'live_guide':
            self.listLiveGuideMenu(self.currItem, 'live_guide_items')
        elif category == 'live_guide_items':
            self.listLiveGuideItems(self.currItem, 'explore_item')
        elif category == 'sub_menu':
            self.listSubMenu(self.currItem, 'list_items', 'explore_item')
        elif category == 'list_items':
            self.listItems(self.currItem, 'explore_item')
        elif category == 'explore_item':
            self.exploreItem(self.currItem)
        elif category == 'sub_items':
            self.listSubItems(self.currItem)
        else:
            printExc()
        CBaseHostClass.endHandleService(self, index, refresh)


class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, BBCSport(), True, [])