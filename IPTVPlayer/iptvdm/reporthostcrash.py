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


import urllib2
import urllib
import sys

def ReportCrash(url, except_msg):
    request = urllib2.Request(url, data=urllib.urlencode({'except':except_msg}))
    data = urllib2.urlopen(request).read()
    print(data)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
    
    ReportCrash(sys.argv[1], sys.argv[2])
    sys.exit(0)
