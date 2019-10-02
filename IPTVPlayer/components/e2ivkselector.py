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
#  Keyboard Selector
#
#  $Id$
#
# 
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, printExc
from Components.config import config

def GetVirtualKeyboard(caps={}):
    type = config.plugins.iptvplayer.osk_type.value
    
    if type in ['own', '']:
        try:
            from enigma import getDesktop
            if getDesktop(0).size().width() >= 1050:
                from Plugins.Extensions.IPTVPlayer.components.e2ivk import E2iVirtualKeyBoard
                
                caps.update({'has_additional_params':True, 'has_suggestions':True})
                return E2iVirtualKeyBoard
        except Exception:
            printExc()

    from Screens.VirtualKeyBoard import VirtualKeyBoard
    return VirtualKeyBoard

