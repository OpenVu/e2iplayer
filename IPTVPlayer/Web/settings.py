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


WebInterfaceVersion = '0.9'
MaxLogLinesToShow = 1000
excludedCFGs = ['fakeUpdate','fakeHostsList','fakExtMoviePlayerList']
activeHost = {}
activeHostsHTML = {}
currItem = {}
retObj = None

configsHTML = {}
tempLogsHTML = ''
NewHostListShown = True

StopThreads = False

hostsWithNoSearchOption = []
GlobalSearchListShown = True
GlobalSearchTypes = ["VIDEO"]
GlobalSearchQuery = ''
GlobalSearchResults = {}
searchingInHost = None
