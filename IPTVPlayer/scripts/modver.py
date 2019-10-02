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


import sys

def printDBG(strDat):
    print("%s" % strDat)
    #print("%s" % strDat, file=sys.stderr)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        printDBG('Please provide libsPath and module name')
        sys.exit(1)
    try:
        libsPath = sys.argv[1]
        moduleDir = sys.argv[2]
        moduleName = sys.argv[3]
        sys.path.insert(1, libsPath)
        mod = __import__('%s.%s' % (moduleDir, moduleName), globals(), locals(), [''], -1)
        if hasattr(mod, '__version__'):
            print(mod.__version__)
        else:
            print(mod.version())
        sys.exit(0)
    except Exception as e:
        printDBG(e)
    sys.exit(1)

