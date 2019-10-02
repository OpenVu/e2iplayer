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


from __future__ import print_function
import urllib
import sys
import traceback

def formatExceptionInfo(maxTBlevel=1):
    cla, exc, trbk = sys.exc_info()
    excName = cla.__name__
    try:
        excArgs = exc.__dict__["args"]
    except KeyError:
        excArgs = "<no args>"
    excTb = traceback.format_tb(trbk, maxTBlevel)
    cla  = None
    exc  = None
    trbk = None
    return "%s\n%s\n%s" % (excName, excArgs, excTb)
    
def CheckVer(params):
    url = "http://softrix.co.uk/istream/reporting/check.php?" + params
    f = urllib.urlopen(url)
    data = f.read()
    print("CheckVer [%s]\n" % data)
    f.close()

def download(url, file):
    try:
        (tmpfile, headers) = urllib.urlretrieve(url, file)
        return 0,str(headers)
    except Exception:
        return 2,str( formatExceptionInfo() )

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('Usage: python pwget url file', file=sys.stderr)
        sys.exit(1)
        
    try:
        params = sys.argv[1].split('?')[1]
        CheckVer(params)
    except Exception:
        pass

    sts,data = download(sys.argv[1], sys.argv[2])
    print(data, file=sys.stderr)
    sys.exit(sts)
