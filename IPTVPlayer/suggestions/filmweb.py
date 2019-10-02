# -*- coding: utf-8 -*-

#
#
# @Codermik release, based on @Samsamsam's E2iPlayer public.
# Released with kind permission of Samsamsam.
# All code developed by Samsamsam is the property of Samsamsam and the E2iPlayer project,  
# all other work is © E2iStream Team, aka Codermik.  TSiPlayer is © Rgysoft, his group can be
# found here:  https://www.facebook.com/E2TSIPlayer/
#
# https://www.facebook.com/e2iStream/
#
#

#
import urllib
try:    import json
except Exception: import simplejson as json

from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.libs.pCommon import common
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc

class SuggestionsProvider:

    def __init__(self):
        self.cm = common()
        
    def getName(self):
        return _("Filmweb Suggestions")

    def getSuggestions(self, text, locale):
        url = 'http://www.filmweb.pl/search/live?q=' + urllib.quote(text)
        sts, data = self.cm.getPage(url)
        if sts and data.startswith("f\\c"):
            retList = []
            data = data.split("\\af")
            for item in data:
                item = item.split('\\c')
                retList.append(item[4])
                if item[4] != item[3]:
                    retList.append(item[3])
            return retList 
        return None
