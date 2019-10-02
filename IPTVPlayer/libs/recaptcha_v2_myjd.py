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


###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _
from Plugins.Extensions.IPTVPlayer.components.asynccall import MainSessionWrapper
from Plugins.Extensions.IPTVPlayer.components.recaptcha_v2myjd_widget import UnCaptchaReCaptchaMyJDWidget

class UnCaptchaReCaptcha:
    def __init__(self, lang='en'):
        self.sessionEx = MainSessionWrapper()
    
    def processCaptcha(self, sitekey, referer=''):
        answer = ''
        retArg = self.sessionEx.waitForFinishOpen(UnCaptchaReCaptchaMyJDWidget,  title=_("My JDownloader reCAPTCHA v2 solution"), sitekey=sitekey, referer=referer)
        if retArg is not None and len(retArg) and retArg[0]:
            answer = retArg[0]
        return answer