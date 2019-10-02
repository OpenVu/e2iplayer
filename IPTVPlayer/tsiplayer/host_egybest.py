# -*- coding: utf-8 -*-
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG
from Plugins.Extensions.IPTVPlayer.libs import ph
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.tsiplayer.libs.tstools import TSCBaseHostClass
from Components.config import config
from Plugins.Extensions.IPTVPlayer.tools.e2ijs import js_execute
import base64
import re
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import GetIPTVSleep


def getinfo():
	info_={}
	info_['name']='Egy.Best'
	info_['version']='1.1 14/05/2019'
	info_['dev']='RGYSoft'
	info_['cat_id']='104'
	info_['desc']='أفلام عربية و اجنبية + مسلسلات اجنبية'
	info_['icon']='https://cdn-static.egybest.net/static/img/egybest_logo.png'
	info_['recherche_all']='1'
	info_['update']='Site Out'
		
	return info_
	
	
class TSIPHost(TSCBaseHostClass):
	def __init__(self):
		TSCBaseHostClass.__init__(self,{'cookie':'egybest1.cookie'})
		self.USER_AGENT = 'Mozilla/5.0 (Linux; Android 7.0; PLUS Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36'
		self.MAIN_URL = 'https://wilo.egybest.xyz'	
		self.HTTP_HEADER = {'User-Agent': self.USER_AGENT, 'DNT':'1', 'Accept': 'text/html', 'Accept-Encoding':'gzip, deflate', 'Referer':self.getMainUrl(), 'Origin':self.getMainUrl()}
		self.AJAX_HEADER = dict(self.HTTP_HEADER)
		self.AJAX_HEADER.update( {'X-Requested-With': 'XMLHttpRequest', 'Accept-Encoding':'gzip, deflate', 'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8', 'Accept':'application/json, text/javascript, */*; q=0.01'} )
		self.defaultParams = {'header':self.HTTP_HEADER, 'with_metadata':True, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True, 'cookiefile': self.COOKIE_FILE}
		self.error_login_egy=False
		#self.egy_intro()
		
	def egy_intro(self):
		self.loggedIn = False
		if (config.plugins.iptvplayer.ts_egybest_email.value!='' and config.plugins.iptvplayer.ts_egybest_pass.value !=''):
			try:
				self.login = config.plugins.iptvplayer.ts_egybest_email.value
				self.password = config.plugins.iptvplayer.ts_egybest_pass.value
				sts, data = self.getPage('https://egy.best/?login=check')
				if sts and '/logout' in data and 'تسجيل الدخول' not in data:
					printDBG('Login OK')
					self.loggedIn = True
				else:	
					rm(self.COOKIE_FILE)
					self.tryTologin()
			except:
				pass 

	def getPage(self, baseUrl, addParams = {}, post_data = None):
		if addParams == {}: addParams = dict(self.defaultParams)
		addParams['cloudflare_params'] = {'cookie_file':self.COOKIE_FILE, 'User-Agent':self.USER_AGENT}
		return self.cm.getPageCFProtection(baseUrl, addParams, post_data)
		
		
		
	def tryTologin(self):
		printDBG('tryTologin start')
		self.loggedIn = False
		url = 'https://ssl.egexa.com/login/?domain=egy.best&url=ref'
		sts, data = self.getPage(url)
		if sts:
			sts, data = ph.find(data, ('<form', '>', ph.check(ph.any, ('LoginForm', 'login_form'))), '</form>')
			if sts:
				actionUrl, post_data = self.cm.getFormData(data, url)
				post_data.update({'email':self.login, 'password':self.password})
				httpParams = dict(self.defaultParams) 
				httpParams['header'] = dict(httpParams['header'])
				httpParams['header']['Referer'] = url
				sts, data = self.getPage(actionUrl, httpParams, post_data)
				if sts:
					sts, data = self.getPage(self.getFullUrl('/?login=check'))
		if sts and '/logout' in data and 'تسجيل الدخول' not in data:
			printDBG('tryTologin OK')
			self.loggedIn = True
		else:
			if self.error_login_egy:
				self.sessionEx.open(MessageBox, _('Login failed.'), type = MessageBox.TYPE_ERROR, timeout = 10)
				self.error_login_egy=True
			printDBG('tryTologin failed')
		return self.loggedIn


	def showmenu0(self,cItem):
		hst='host2'
		img=cItem['icon']	
		Cimaclub_TAB=[{'category':hst,'title': 'Films'    ,'mode':'20'  ,'icon':img ,'sub_mode':'film'},
					{'category':hst,'title': 'Series'   ,'mode':'20' ,'icon':img ,'sub_mode':'serie'},					  
					{'category':'search'  ,'title': _('Search'),'search_item':True,'page':1,'hst':'tshost','icon':img},
					]
		self.listsTab(Cimaclub_TAB, {'import':cItem['import'],'name':hst})
		self.addDir({'import':cItem['import'], 'name':'categories', 'category':hst, 'url':'https://wilo.egybest.xyz/movie/gemini-man-2019/?ref=movies-p1', 'title':'Test Link', 'desc':'','hst':'tshost', 'icon':'', 'mode':'31'} )							
		
		
	def showmenu1(self,cItem):
		base=self.MAIN_URL
		gnr2=cItem['sub_mode']
		hst='host2'
		img=cItem['icon']			 
		url=self.MAIN_URL+'/'
		sts1, data = self.getPage(url)
				
		if gnr2=='film':
			sts, data2 = self.getPage(self.MAIN_URL+'/movies/')
			if sts:
				lst_data1 = re.findall('<div class="sub_nav">(.*?)<div id="movies',data2, re.S)
				if  lst_data1:
					self.addDir({'import':cItem['import'],'name':'categories', 'category' :'host2', 'url':'', 'title':'\c00????00'+'By Filter', 'desc':'', 'icon':img, 'mode':'21', 'count':1,'data':lst_data1[0],'code':'','type_':'movies'})						
		
			self.addMarker({'title':'\c0000??00Main','icon':'','desc':''})				
			egy_films=[ {'title': 'أفلام جديدة'       , 'url':self.MAIN_URL+'/movies/'      , 'mode':'30', 'page':1},						  
						{'title': 'احدث الاضافات'     , 'url':self.MAIN_URL+'/movies/latest' , 'mode':'30', 'page':1},						  
						{'title': 'أفضل الافلام', 'url':self.MAIN_URL+'/movies/top'  , 'mode':'30', 'page':1},						  
						{'title': 'الاكثر شهرة' , 'url':self.MAIN_URL+'/movies/popular' , 'mode':'30', 'page':1},
						]							
			self.listsTab(egy_films, {'import':cItem['import'],'name':'categories', 'category':hst, 'desc':'', 'icon':img})		
			self.addMarker({'title':'\c0000??00Trendinge','icon':'','desc':''})				
			egy_films=[ {'title': 'الاكثر مشاهدة الان'       , 'url':self.MAIN_URL+'/trending/'      , 'mode':'30', 'page':1},						  
						{'title': 'الاكثر مشاهدة اليوم'     , 'url':self.MAIN_URL+'/trending/today' , 'mode':'30', 'page':1},						  
						{'title': 'الاكثر مشاهدة هذا الاسبوع', 'url':self.MAIN_URL+'/trending/week'  , 'mode':'30', 'page':1},						  
						{'title': 'الاكثر مشاهدة هذا الشهر' , 'url':self.MAIN_URL+'/trending/month' , 'mode':'30', 'page':1},						  
						]
			self.listsTab(egy_films, {'import':cItem['import'],'name':'categories', 'category':hst, 'desc':'', 'icon':img})
			if sts1:
				self.addMarker({'title':'\c0000??00Genre','icon':'','desc':''})					
				lst_data1 = re.findall('mgb table full">.*?href="(.*?)">(.*?)<.*?td">.*?href="(.*?)">(.*?)<',data, re.S)
				for (url1,titre1,url2,titre2) in lst_data1:
					self.addDir({'import':cItem['import'],'name':'categories', 'category' :hst, 'url':base+url1, 'title':titre1, 'desc':titre1, 'icon':img, 'mode':'30', 'page':1})				
					self.addDir({'import':cItem['import'],'name':'categories', 'category' :hst, 'url':base+url2, 'title':titre2, 'desc':titre2, 'icon':img, 'mode':'30', 'page':1})

			
 
		if gnr2=='serie':
			sts, data2 = self.getPage(self.MAIN_URL+'/tv/')
			if sts:
				lst_data1 = re.findall('<div class="sub_nav">(.*?)<div id="movies',data2, re.S)
				if  lst_data1:
					self.addDir({'import':cItem['import'],'name':'categories', 'category' :hst, 'url':'', 'title':'\c00????00'+'By Filter', 'desc':'', 'icon':img, 'mode':'21', 'count':1,'data':lst_data1[0],'code':'','type_':'tv'})						
		
			self.addMarker({'title':'\c0000??00Main','icon':'','desc':''})				
			egy_films=[ {'title': 'احدث الحلقات'  , 'url':self.MAIN_URL+'/tv/'        , 'mode':'30', 'page':1},						  
						{'title': 'مسلسلات جديدة'  , 'url':self.MAIN_URL+'/tv/new'     , 'mode':'30', 'page':1},						  
						{'title': 'أفضل المسلسلات' , 'url':self.MAIN_URL+'/tv/top'     , 'mode':'30', 'page':1},						  
						{'title': 'الاكثر شهرة'    , 'url':self.MAIN_URL+'/tv/popular' , 'mode':'30', 'page':1},	
						]
			self.listsTab(egy_films, {'import':cItem['import'],'name':'categories', 'category':hst, 'desc':'', 'icon':img})				

	def showmenu2(self,cItem):	
		hst='host2'
		img=cItem['icon']	
		count=cItem['count']
		data=cItem['data']	
		codeold=cItem['code']	
		type_=cItem['type_']			
		lst_data1 = re.findall('class="dropdown">(.*?)</div></div>',data, re.S)	
		if lst_data1:
			data2=lst_data1[count-1]
			if count==7:
				url=self.MAIN_URL+'/'+type_+'/'+codeold
				self.addDir({'import':cItem['import'],'name':'categories', 'category' :hst, 'url':url, 'title':'الكل', 'desc':codeold, 'icon':img, 'mode':'30', 'page':1})					
			else:
				self.addDir({'import':cItem['import'],'name':'categories', 'category' :hst, 'url':'', 'title':'الكل', 'desc':codeold, 'icon':img, 'mode':'21', 'count':count+1,'data':data,'code':codeold,'type_':type_})
			lst_data2 = re.findall('href="/'+type_+'/(.*?)">(.*?)<',data2, re.S)					
			for (code,titre) in lst_data2:
				if codeold!='':
					code = codeold+'-'+code
				if count==7:
					url=self.MAIN_URL+'/'+type_+'/'+code
					self.addDir({'import':cItem['import'],'name':'categories', 'category' :hst, 'url':url, 'title':titre, 'desc':code, 'icon':img, 'mode':'30', 'page':1})					
				else:	
					self.addDir({'import':cItem['import'],'name':'categories', 'category' :hst, 'url':'', 'title':titre, 'desc':code, 'icon':img, 'mode':'21', 'count':count+1,'data':data,'code':code,'type_':type_})
		
	def showitms(self,cItem):
		hst='host2'
		img=cItem['icon']	
		base=self.MAIN_URL
		page=cItem['page']
		url0=cItem['url']
		url=url0+'?page='+str(page)+'&output_format=json&output_mode=movies_list'
		sts, data = self.getPage(url)
		if sts:
			data=data.replace('\\"','"')	
			data=data.replace('\\/','/')				
			lst_data=re.findall('<a href="(.*?)".*?rating">(.*?)</i>.*?src="(.*?)".*?title">(.*?)<.*?ribbon.*?<span>(.*?)<', data, re.S)			
			for (url1,rate,image,name_eng,qual) in lst_data:
				desc='Rating:'+self.cleanHtmlStr(rate)+'  Qual:'+qual
				self.addDir({'import':cItem['import'],'good_for_fav':True, 'name':'categories', 'category':hst, 'url':base+url1, 'title':str(name_eng.decode('unicode_escape')), 'desc':desc,'EPG':True,'hst':'tshost', 'icon':image, 'mode':'31'} )							
			self.addDir({'import':cItem['import'],'name':'categories', 'category':hst, 'url':url0, 'title':'Page Suivante', 'page':page+1, 'desc':'Page Suivante', 'icon':img, 'mode':'30'})	

	def showelems(self,cItem):
		desc=''
		base=self.MAIN_URL
		img=cItem['icon']
		url0=cItem['url']	
		titre=cItem['title']
		sts, data = self.getPage(url0)
		if sts:
			cat_data0=re.findall('<table class="movieTable full">(.*?)</table>', data, re.S)
			if cat_data0:
				desc1=cat_data0[0].replace('<tr',' | <tr')
				desc=self.cleanHtmlStr(desc1)+'\n'
				
			cat_data0=re.findall('القصة</strong>.*?<div.*?">(.*?)</div>', data, re.S)
			if cat_data0:
				desc1=cat_data0[0]
				desc=desc+self.cleanHtmlStr(desc1)
								
			cat_data2=re.findall('<div id="yt_trailer".*?url="(.*?)".*?src="(.*?)"', data, re.S)
			for (URl,IMg) in cat_data2:					
				self.addVideo({'import':cItem['import'],'good_for_fav':True,'name':'categories','category' : 'video','url': URl,'title':'Trailer','desc':desc,'icon':IMg,'hst':'none'})						
							
			if (('/series/' in url0) or ('/season/' in url0)):			
				cat_data=re.findall('movies_small">(.*?)</div>', data, re.S)	
				if cat_data:
					el_data=re.findall('<a href="(.*?)".*?src="(.*?)".*?">(.*?)<', cat_data[0], re.S)
					for (url1,image,name_eng) in el_data:					
						self.addDir({'import':cItem['import'],'good_for_fav':True, 'name':'categories', 'category':'host2', 'url':base+url1, 'title':name_eng, 'desc':desc, 'icon':img, 'mode':'31'} )							
			else: 
				self.addVideo({'import':cItem['import'],'good_for_fav':True,'name':'categories','category' : 'video','url': url0,'title':titre,'desc':desc,'icon':img,'hst':'tshost'})			
		
		
		
	def SearchResult(self,str_ch,page,extra):
		url_=self.MAIN_URL+'/explore/?page='+str(page)+'&output_format=json&q='+str_ch+'&output_mode=movies_list'
		sts, data = self.getPage(url_)	
		if sts:
			data=data.replace('\\"','"')	
			data=data.replace('\\/','/')				
			lst_data=re.findall('<a href="(.*?)".*?rating">(.*?)</i>.*?src="(.*?)".*?title">(.*?)<.*?ribbon.*?<span>(.*?)<', data, re.S)			
			for (url1,rate,image,name_eng,qual) in lst_data:
				desc='Rating:'+self.cleanHtmlStr(rate)+'  Qual:'+qual
				url1=self.MAIN_URL+'/'+url1
				url1=url1.replace('best//','best/')
				self.addDir({'import':extra,'good_for_fav':True,'EPG':True, 'name':'categories', 'category':'host2', 'url':url1, 'title':str(name_eng.decode('unicode_escape')), 'desc':desc, 'icon':image, 'mode':'31','hst':'tshost'} )							
		




	def get_verify_url(self,url):
		self.cm.clearCookie(self.COOKIE_FILE, removeNames=['PHPSID','PSSID','__cfduid','vclid'])
		cookieHeader = self.cm.getCookieHeader(self.COOKIE_FILE)
		printDBG('coooooooooooooooooooooooooooook'+cookieHeader)
		HTTP_HEADER =  {'Host':'vidstream.to','User-Agent': self.USER_AGENT,'Accept-Encoding': 'gzip, deflate, br', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3','Connection': 'keep-alive','Cookie': cookieHeader,'Upgrade-Insecure-Requests': '1'}
		http_params = {'header':HTTP_HEADER, 'cookiefile':self.COOKIE_FILE, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True}	
		HTTP_HEADER0 =  {'Host':'vidstream.to','User-Agent': self.USER_AGENT, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3','Connection': 'keep-alive','Cookie': cookieHeader,'Upgrade-Insecure-Requests': '1'}
		http_params0 = {'header':HTTP_HEADER0, 'cookiefile':self.COOKIE_FILE, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True}	
		
#		AJAX_HEADER = dict(self.HTTP_HEADER)
#		AJAX_HEADER.update( {'X-Requested-With': 'XMLHttpRequest', 'Accept-Encoding':'gzip, deflate', 'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8', 'Accept':'*/*', 'TE': 'Trailers'} )
#		http_params2 = {'header':AJAX_HEADER, 'cookiefile':self.COOKIE_FILE, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True}
		
		
		cv_url = ''
		sts, data = self.getPage(url,http_params)
				
		cookieHeader = self.cm.getCookieHeader(self.COOKIE_FILE)
		printDBG('coooooooooooooooooooooooooooook'+cookieHeader)
		
		sts, data = self.getPage(url,http_params0)
		
		
		cookieHeader = self.cm.getCookieHeader(self.COOKIE_FILE)
		printDBG('coooooooooooooooooooooooooooook'+cookieHeader)		
		printDBG('data'+str(data))
		
		tmp_script = re.findall("<script.*?>(.*?)</script>", data, re.S)
		if tmp_script:
			script=tmp_script[0]
			#script='''function OrHZcmzkt(){ var a=['XcUSwp','VZbUwbWoKdERMuVDIDu8OT','7FolFu','chnXlPQY','fwcoWgWgP3uZF','GcZCMzsKp','FfvdiVb','PVBDXG','NJYZz','xoMEMne','ixpfdhV','PHcmWy','jyfZsCWQMV','HABVoVoHoQDiap','JAral','mfeN0clKp','bNSYMsNCLf','AxJQ93','sj97qWNg','tZudZcD','MnrVoHoV','WsxhxPn','ftdRIsJ','7nrVoVoHoaLZx1qi','sZAsWHoVogX4mcRV','DBcBA','ZK7tVHVoVGMzTnkCSD','pzhwFW','SGOApMfHga','vrCrVoHWvuve3gK','Jptje','oWgWg','Tnkx11efde1005kQZG','5lCQ7cEi0','HE48gfFBG','kMrjANi','vbwMnrVoHoVTsfnxAY','AdYBdqn','SygdPwE','yosMA0','kWRlLAlOAC','XapgdrpWFp','HWfAC','Rkvdv','elb1aVoVoHoYFT1zn','GWxoMEMne78WS','MQM9jqxl','xyq3tz0','RoAYuP','WeNBheVLu','tpQZWhNRjt','XdmNoEn','ZAsWHoVogX9rYb9V','ivHkQnwoX','VoxVWeLz','sWOFbwsgpMuevB0LbV','KXapgdrpWFpn5Ax','QUjbNme','11efde1005','k0GbiF3Svs','XmcLAEWp','jPHDqJoM','ep650b8Ol8','m3wVklF','pRFUlD','zaRnOxoMEMneNYn','HPWHWoWgWuu97bSi','khDBqV79f','oB1p','GWhbEhMhJj','XJVoHoVf11itb','TO4C4egbPY','BsvjqBe','PpkTjsWyTXOIk','OzbGEvy','QtpMusIGoVHSi2','tXYSC','RpkTjsWyG7TAF','wsSbJTlI','NnKWXWhMs','DAdVoxVWeLzmuF','uMH4jPka','DTicRKY','MZBTREXap','6cLoooVe','OtIkDLR','UUoVEXoGW','ZUS8M8b454fce8ChvbeQ','fKfyHbTrIm','VHVoVGMztju','MdZMTy','ofrXCk','FpJmClT','Fys5a91soz','OHZfLOe','CNLEQ','zVoxVWeLzSl8L8f','VoVoMuzdG','kKKIe','62j6cLoooVeYHAd2','IpiAwjIO','TMhyXnw4','6O29haRYNu','pjVNHiD','YZ4wc9b536DrxoD','rIiduZC','09750SfPrh','wZrsMO','mXFVHVoVGMzdo489','CtFhiaX8PV','IEpHLF','riVObFG','XapgdrpWFpaVICs','ZeuX4klf','UkDpL','HHOPtwUv','qjhFoB','8b454fcezBnu','MYLWTbKqqr','PlnBnRZy','0U7jE9U','MserMbew','VpRswL','PZspkTjsWyefE','obIZPQud','tpMusIGoVH','VHVoVGMz','h8MserMbewJb4i','V9VoVoMuzdG9MX','18MUA4Wrq','AnwY11efde10052uHf2TD','zYCCyUtELi','hVoHoVfJMEj0','NYcvakk','e9724','IkGJCiJ','HJxFBo','DOpenjph','iWGT0ofrXCkcz68Wu','LAudvyOHxU','tpMusIGoVHRVD','8uK1Q8S2','vXIBLP','650b8','mOxfWfXH','aeGTCZstMQ','gVOdWgCXDoIU8R6','sIxsqhjAk','R86cLoooVewlQKT','CQHw6Y','enYUGSbv','GkzFdCPF','gJaMnrVoHoVP5ekz','SCzJ2afH0Y','Gk2Ba','RWGaDrW','bMfvPPVoVykzgTIR','QAxItNpFC','sWNCSqefU','WHWoWgWuuvHsH6Q','wsgpMue','pfToWgWgyHhd2','JrjjGm','8Cae9724bfM','fAVlSLhjv','VOdWgCXDokTMz7','phWHcJ','JeKFpoVZ','VOdWgCXDo','EqRJuXapgdrpWFpgZpyM','eCenYZn','EKkVoxVWeLzdnnl0Pj','ICisg','Cfi3ac9b5368Pr8i','lwhdGKf','ZvycUz','ZJyEHZAsWHoVogze7uhxV','yxJqg','u6OyfgOUqX','iJZcbSOO','U9bWoKdERMuVprzqw','wafSsgcpEV','TTVoHoVf4kjjY','THGoFVz8f','StbZzSbB','097503pQASh','caQBUSJ','sZ343VoVoMuzdGCdnhrdi','xEykM','c9b536','WHWoWgWuu','SeYHikEbsO','pkTjsWy','jYoIm','VoHoVf','Zedsh','NRBhErCIg','t3yMserMbewxAac','39qBAt','XO39CwkxY','xtJiDJuSUb','zPbGxRgr','Dce9724ndlZf','THDYc','g3pv9Wxy','HcOyQ','NeX65ab178beeV9P1e','ovvAZk','1XTdnhP','DoccXixQl','RDpHzfcqFW','XqX3yf','E11ysEqE','pCptbM','TWaxrVoHWvOuTmRMD','ZAsWHoVog','7r24jbGWig','jNwGt','oWgWgnJ8i','npmTZEudSi','ofrXCkhAn6OTw','7U8QtNJr','MTFNzSM','SByguc','WuvDLpR','qeY60','YGlqh','joYsPTC2dC','Zo7Clr','INQnV','gyYQORDpHzfcqFWWhx24FA','09750','yuaFdBrj','QqaBBCfIAW','lamLkrH','HQfYoCJUQ','HVYFXV9','bRsCEt','tafBHA','.noad','mkBjd','open','eRXcq','RdmYp','isFullscreen','lock','landscape','catch','mGxar','RgMLj','RfMtb','DBcEr','PIBFn','.vjs-icon-hd','button.vjs-menu-button.vjs-icon-hd','wXcKH','jfmuh','undefined','#video.video-js','attr','ready','NLEWc','QWcsR','mHSJY','hotkeys','qualityPickerPlugin','fullscreenchange','jSaKQ','fNrBq','OaIhl','nqSQd','sqJWI','GxiBY','#video.video-js\x20*','hasClass','GVpzr','FoXJM','touchstart','paused','originalEvent','touches','pageX','preventDefault','KPSPt','pause','eIons','apply','eQYOE','div.vjs-menu','vjs-lock-showing','className','search','vjs-icon-hd','target','parents','length','find','trigger','tWThC','item','value','return\x20(function()\x20','{}.constructor(\x22return\x20this\x22)(\x20)','KotZF','play','FCAry','attribute','iNspS','.video-js','append','<a\x20href=\x22https://vidstream.top/?utm_source=player-logo\x22\x20target=\x22_blank\x22><img\x20src=\x22','data','logo','\x22\x20class=\x22vjs-logo\x22></a>','orientation','unlock','[XhSRbRCNBhLJkgPDRbkXybJkFIcfxHfNShTFBZCcSVFSATgGWJRkfGGIFYLEgMXUgKGgJyNuySEMKfTxjKIycNqSbjShcFUzZYkjAKjYNxguNWjByMHZqOIILVxjZuGgYzBkZBUCENjJhDhMJgk]','XhvidSsRtrbReamC.topNBhL;Jwkwgw.vPDRidstbrekaXm.ybJkFIctfxopHfN;ShTvidstFBZream.oCcnSVlFSineA;Twgww.GviWdJRksftGGreaIm.onFliYLEnegMXUgKGgJyNuySEMKfTxjKIycNqSbjShcFUzZYkjAKjYNxguNWjByMHZqOIILVxjZuGgYzBkZBUCENjJhDhMJgk','replace','split','ezaRi','charCodeAt','goVjO','dqdLm','eUqfD','gqueK','ajax','/cv.php?verify=','POST','Srdiy','._reload','click','location','href','indexOf','NUBVI','currentTime','BXBVI','zyhTx','RNqMJ','PIMNo','ynWgt','ulhqb','TGpoR','dfJyv','OWFYw','JfWHW','iWBtW','duration','WfVWm','test','userAgent','lgjzSBauoi','PVoVyk','ICcvN','f6cLoooVeTErx','fy57tdhiTY','Xnxvl','rvstpMusIGoVHY5sYt','VLBn3J','49XbB','obxRQo','yXwsgpMueQTdk','7LMpbWoKdERMuVaVCl','NuwgPiFyQ','WWvGVO','h06xT'];(function(c,d){var e=function(f){while(--f){c['push'](c['shift']());}};var g=function(){var h={'data':{'key':'cookie','value':'timeout'},'setCookie':function(i,j,k,l){l=l||{};var m=j+'='+k;var n=0x0;for(var n=0x0,p=i['length'];n<p;n++){var q=i[n];m+=';\x20'+q;var r=i[q];i['push'](r);p=i['length'];if(r!==!![]){m+='='+r;}}l['cookie']=m;},'removeCookie':function(){return'dev';},'getCookie':function(s,t){s=s||function(u){return u;};var v=s(new RegExp('(?:^|;\x20)'+t['replace'](/([.$?*|{}()[]\/+^])/g,'$1')+'=([^;]*)'));var w=function(x,y){x(++y);};w(e,d);return v?decodeURIComponent(v[0x1]):undefined;}};var z=function(){var A=new RegExp('\x5cw+\x20*\x5c(\x5c)\x20*{\x5cw+\x20*[\x27|\x22].+[\x27|\x22];?\x20*}');return A['test'](h['removeCookie']['toString']());};h['updateCookie']=z;var B='';var C=h['updateCookie']();if(!C){h['setCookie'](['*'],'counter',0x1);}else if(C){B=h['getCookie'](null,'counter');}else{h['removeCookie']();}};g();}(a,0x11b));var b=function(c,d){c=c-0x0;var e=a[c];return e;};var d=function(){var c=!![];return function(d,e){var f=c?function(){if(e){var g=e['apply'](d,arguments);e=null;return g;}}:function(){};c=![];return f;};}();var b3=d(this,function(){var c=function(){return'\x64\x65\x76';},d=function(){return'\x77\x69\x6e\x64\x6f\x77';};var e=function(){var f=new RegExp('\x5c\x77\x2b\x20\x2a\x5c\x28\x5c\x29\x20\x2a\x7b\x5c\x77\x2b\x20\x2a\x5b\x27\x7c\x22\x5d\x2e\x2b\x5b\x27\x7c\x22\x5d\x3b\x3f\x20\x2a\x7d');return!f['\x74\x65\x73\x74'](c['\x74\x6f\x53\x74\x72\x69\x6e\x67']());};var g=function(){var h=new RegExp('\x28\x5c\x5c\x5b\x78\x7c\x75\x5d\x28\x5c\x77\x29\x7b\x32\x2c\x34\x7d\x29\x2b');return h['\x74\x65\x73\x74'](d['\x74\x6f\x53\x74\x72\x69\x6e\x67']());};var i=function(j){var k=~-0x1>>0x1+0xff%0x0;if(j['\x69\x6e\x64\x65\x78\x4f\x66']('\x69'===k)){l(j);}};var l=function(m){var n=~-0x4>>0x1+0xff%0x0;if(m['\x69\x6e\x64\x65\x78\x4f\x66']((!![]+'')[0x3])!==n){i(m);}};if(!e()){if(!g()){i('\x69\x6e\x64\u0435\x78\x4f\x66');}else{i('\x69\x6e\x64\x65\x78\x4f\x66');}}else{i('\x69\x6e\x64\u0435\x78\x4f\x66');}});b3();var c=function(){var w=!![];return function(x,y){if('KPSPt'!==b('0x0')){player[b('0x1')]();}else{var A=w?function(){if(b('0x2')!==b('0x2')){if(y){var h=y[b('0x3')](x,arguments);y=null;return h;}}else{if(y){if(b('0x4')==='BZVNF'){if(video['find'](b('0x5'))['hasClass'](b('0x6'))&&e['target'][b('0x7')][b('0x8')](b('0x9'))<0x0&&!$(e[b('0xa')])[b('0xb')]('.vjs-icon-hd')[b('0xc')]){video[b('0xd')]('button.vjs-menu-button.vjs-icon-hd')[b('0xe')]('click');}vtapped=setTimeout(function(){vtapped=null;},0x12c);}else{var E=y[b('0x3')](x,arguments);y=null;return E;}}}}:function(){};w=![];return A;}};}();var e=c(this,function(){var F;try{if(b('0xf')!=='tWThC'){for(var m=0x0;m<0x3e8;m--){var n=m>0x0;switch(n){case!![]:return this[b('0x10')]+'_'+this[b('0x11')]+'_'+m;default:this[b('0x10')]+'_'+this[b('0x11')];}}}else{var J=Function(b('0x12')+b('0x13')+');');F=J();}}catch(K){if('KotZF'===b('0x14')){F=window;}else{player[b('0x15')]();}}var M=function(){if(b('0x16')!=='FCAry'){return;}else{return{'key':b('0x10'),'value':b('0x17'),'getAttribute':function(){if(b('0x18')===b('0x18')){for(var O=0x0;O<0x3e8;O--){if('RiVDr'==='RiVDr'){var P=O>0x0;switch(P){case!![]:return this[b('0x10')]+'_'+this['value']+'_'+O;default:this[b('0x10')]+'_'+this[b('0x11')];}}else{$(U)[b('0xd')](b('0x19'))[b('0x1a')](b('0x1b')+video[b('0x1c')](b('0x1d'))+b('0x1e'));}}}else{screen[b('0x1f')][b('0x20')]();}}()};}};var S=new RegExp(b('0x21'),'g');var T=b('0x22')[b('0x23')](S,'')[b('0x24')](';');var U;var V;var W;var X;for(var Y in F){if('fAGVY'!==b('0x25')){if(Y['length']==0x8&&Y['charCodeAt'](0x7)==0x74&&Y[b('0x26')](0x5)==0x65&&Y[b('0x26')](0x3)==0x75&&Y[b('0x26')](0x0)==0x64){if(b('0x27')===b('0x28')){return{'key':b('0x10'),'value':'attribute','getAttribute':function(){for(var k=0x0;k<0x3e8;k--){var l=k>0x0;switch(l){case!![]:return this[b('0x10')]+'_'+this[b('0x11')]+'_'+k;default:this[b('0x10')]+'_'+this[b('0x11')];}}}()};}else{U=Y;break;}}}else{for(var t=0x0;t<=_EsDZHzy['length'];t++){_kiowgRmA+=_GwwO[_EsDZHzy[t]]||'';}}}for(var a4 in F[U]){if(b('0x29')===b('0x2a')){if(_kiowgRmA){$[b('0x2b')]({'url':b('0x2c')+_kiowgRmA,'cache':![],'method':b('0x2d'),'data':{'_WSuaBvzajtUJ7Xn6TOv':'no'}});}_r3sEG0=!![];}else{if(a4[b('0xc')]==0x6&&a4[b('0x26')](0x5)==0x6e&&a4[b('0x26')](0x0)==0x64){if(b('0x2e')!==b('0x2e')){$(b('0x2f'))[b('0x30')](function(){setTimeout(function(){window[b('0x31')]=window[b('0x31')][b('0x32')]+(window['location'][b('0x32')][b('0x33')]('?')>=0x0?'&':'?')+'r';},0xbb8);});startVideo();}else{V=a4;break;}}}}if(!('~'>V)){if(b('0x34')!=='NUBVI'){seekTo=player[b('0x35')]()-0xa;if(seekTo<0x0){seekTo=0x0;}}else{for(var a8 in F[U]){if('wIXnY'!=='Gkqju'){if(a8[b('0xc')]==0x8&&a8[b('0x26')](0x7)==0x6e&&a8[b('0x26')](0x0)==0x6c){if(b('0x36')!==b('0x36')){F=window;}else{W=a8;break;}}}else{var i=fn[b('0x3')](context,arguments);fn=null;return i;}}for(var ac in F[U][W]){if(b('0x37')===b('0x38')){$[b('0x2b')]({'url':b('0x2c')+_kiowgRmA,'cache':![],'method':'POST','data':{'_WSuaBvzajtUJ7Xn6TOv':'ok'}});}else{if(ac[b('0xc')]==0x8&&ac[b('0x26')](0x7)==0x65&&ac[b('0x26')](0x0)==0x68){if('KotlA'!==b('0x39')){X=ac;break;}else{if(_kiowgRmA){$[b('0x2b')]({'url':b('0x2c')+_kiowgRmA,'cache':![],'method':b('0x2d'),'data':{'_WSuaBvzajtUJ7Xn6TOv':'ok'}});}setTimeout(function(){_r3sEG0=!![];},(_lUWnp[_OhH2J]||_lUWnp[_lUWnp[b('0xc')]-0x1])*0x3e8);_OhH2J++;}}}}}}if(!U||!F[U]){if(b('0x3a')===b('0x3b')){var j=Function(b('0x12')+b('0x13')+');');F=j();}else{return;}}var ah=F[U][V];var ai=!!F[U][W]&&F[U][W][X];var aj=ah||ai;if(!aj){if(b('0x3c')==='hxQuu'){vtapped=null;}else{return;}}var al=![];for(var am=0x0;am<T[b('0xc')];am++){if(b('0x3d')!=='fnmLF'){var V=T[am];var ao=aj[b('0xc')]-V[b('0xc')];var ap=aj[b('0x33')](V,ao);var aq=ap!==-0x1&&ap===ao;if(aq){if(b('0x3e')==='OWFYw'){if(aj[b('0xc')]==V[b('0xc')]||V[b('0x33')]('.')===0x0){if(b('0x3f')!=='JfWHW'){return;}else{al=!![];}}}else{if(aj[b('0xc')]==V[b('0xc')]||V[b('0x33')]('.')===0x0){al=!![];}}}}else{_r3sEG0=!![];}}if(!al){if(b('0x40')===b('0x40')){data;}else{seekTo=player[b('0x41')]()-0x1;}}else{if(b('0x42')!==b('0x42')){$[b('0x2b')]({'url':'/cv.php?verify='+_kiowgRmA,'cache':![],'method':b('0x2d'),'data':{'_WSuaBvzajtUJ7Xn6TOv':'no'}});}else{return;}}M();});e();var _r3sEG0=!![];var _OhH2J=0x0;var _kiowgRmA='';var _lUWnp=[];var _GwwO=[];var _EsDZHzy=[];var _Xw5SVk=![];var ismob=/android|ios|mobile/i[b('0x43')](navigator[b('0x44')]);_GwwO[b('0x45')]=b('0x46');_GwwO[b('0x47')]=b('0x48');_EsDZHzy[0x2b]=b('0x49');_GwwO[b('0x4a')]=b('0x4b');var NhdOONB=b('0x4c');_EsDZHzy[0x8]=b('0x4d');_GwwO[b('0x4e')]=b('0x4f');_GwwO['oPkDf']=b('0x50');_GwwO['wSYhgp']='VoVoHo';_lUWnp[0x0]='30';_EsDZHzy[0x15]=b('0x51');_EsDZHzy[0x37]=b('0x52');_EsDZHzy[0x63]=b('0x53');_GwwO[b('0x54')]=b('0x55');_EsDZHzy[0x11]=b('0x56');_GwwO[b('0x57')]=b('0x58');_EsDZHzy[0x54]=b('0x59');var qTdKmUa=b('0x5a');var iQgiDjA=b('0x5b');_GwwO[b('0x5c')]=b('0x5d');_GwwO[b('0x5e')]='8b454fce';var lNqml=b('0x5f');_GwwO[b('0x60')]=b('0x61');_EsDZHzy[0x1b]=b('0x62');_EsDZHzy[0x35]=b('0x63');_EsDZHzy[0x17]=b('0x64');_EsDZHzy[0x18]='iCON3c6Oq';_EsDZHzy[0x48]=b('0x5c');_EsDZHzy[0x19]='QLMsPPP';var Kzhdc=b('0x65');_EsDZHzy[0x61]=b('0x66');_GwwO[b('0x67')]=b('0x68');_GwwO[b('0x69')]='tylppofrXCk5awQGr';_EsDZHzy[0x23]='LqUPBCUvB';_GwwO[b('0x6a')]=b('0x6b');_GwwO['oCerPTbgR']=b('0x6c');_GwwO[b('0x6d')]='PmFsP650b8qel';_GwwO['ucMeG']=b('0x6e');_EsDZHzy[0x1]=b('0x6f');_GwwO[b('0x70')]=b('0x71');_GwwO[b('0x72')]=b('0x73');_GwwO['HFVIg']=b('0x74');_EsDZHzy[0x4b]=b('0x75');_EsDZHzy[0x2e]=b('0x76');_GwwO[b('0x77')]=b('0x78');_EsDZHzy[0x29]=b('0x79');_GwwO[b('0x7a')]='rVoHWv1gQ3Nd';_EsDZHzy[0x30]='w3BCQAqBkc';var XJTOgjMr=b('0x7b');_GwwO[b('0x7c')]=b('0x7d');_GwwO['izUuE']='kjv65ab178beexMu';_EsDZHzy[0x4f]=b('0x7e');_EsDZHzy[0x58]='kWRlLAlOAC';_EsDZHzy[0x32]='wSYhgp';_lUWnp[0x7]='90';_EsDZHzy[0x3a]='RAU8k';_GwwO[b('0x7f')]=b('0x80');_GwwO['uSbFdumQ']=b('0x81');_EsDZHzy[0x52]='r3aEz3';_EsDZHzy[0x6]=b('0x82');var KrZBSRz=b('0x83');_GwwO[b('0x84')]='HNLMserMbew50di';_GwwO[b('0x64')]='dab6a';_EsDZHzy[0x1d]=b('0x85');_EsDZHzy[0x66]=b('0x86');_GwwO[b('0x87')]=b('0x88');_GwwO[b('0x89')]=b('0x8a');_GwwO['JmxhN']=b('0x8b');_GwwO['wMchQ']=b('0x8c');_GwwO[b('0x8d')]=b('0x8e');_EsDZHzy[0x33]=b('0x8f');_EsDZHzy[0x53]='tZudZcD';_GwwO[b('0x90')]='xMnrVoHoVdYC';_GwwO['AoPvrDb']='1X2Cdab6aMmH2w';_GwwO[b('0x91')]=b('0x92');_EsDZHzy[0x1c]=b('0x93');_lUWnp[0x1]='30';_GwwO[b('0x94')]=b('0x95');_GwwO['PbtyieVXJB']=b('0x96');_EsDZHzy[0x40]=b('0x97');var umJwO=b('0x98');_GwwO[b('0x99')]=b('0x9a');_EsDZHzy[0x1a]=b('0x9b');_GwwO[b('0x9c')]=b('0x9d');_GwwO[b('0x9e')]=b('0x9f');_GwwO[b('0xa0')]=b('0xa1');_EsDZHzy[0x49]=b('0xa2');var rWuLrKV='cXHcVBQ';_GwwO[b('0xa3')]=b('0xa4');_EsDZHzy[0x10]=b('0xa5');_GwwO['BfIFugG']='X2ldWVoVoMuzdGaYNm5wz';_EsDZHzy[0x3]=b('0xa6');_GwwO[b('0xa7')]='WHWoWgWuuNIPRT3';_GwwO[b('0x62')]=b('0xa8');var XOwrzMSo=b('0xa9');_GwwO[b('0xaa')]=b('0xab');_GwwO[b('0xac')]=b('0xad');_lUWnp[0x2]='30';_GwwO[b('0xae')]=b('0xaf');_EsDZHzy[0xc]=b('0xb0');_EsDZHzy[0x57]=b('0xb1');_GwwO[b('0xb2')]='ePVoVyknXhi0';_GwwO[b('0xb3')]=b('0xb4');_GwwO[b('0x7e')]=b('0xb5');_GwwO[b('0xb6')]=b('0xb7');_GwwO[b('0xb8')]='2RDpHzfcqFWGTsgg5';_EsDZHzy[0x28]=b('0xb9');_EsDZHzy[0x5d]=b('0xba');_EsDZHzy[0x13]=b('0x8d');_EsDZHzy[0x3f]=b('0xbb');_EsDZHzy[0x25]=b('0x72');_GwwO['fKIUkrYL']=b('0xbc');_lUWnp[0x6]='60';_GwwO[b('0xbd')]=b('0xbe');_GwwO[b('0xbf')]=b('0xc0');_EsDZHzy[0x26]=b('0xc1');_EsDZHzy[0x50]='unKVLvE';var NOvodh=b('0xc2');_GwwO[b('0xc3')]=b('0xc4');var bKiF='DpFAUeQ';_EsDZHzy[0x69]=b('0xc5');_EsDZHzy[0x2c]='tuJdV';_EsDZHzy[0x1f]=b('0xc6');_lUWnp[0x3]='40';_EsDZHzy[0x64]=b('0xc7');_GwwO[b('0xc8')]=b('0xc9');_EsDZHzy[0x68]=b('0xca');_GwwO[b('0xcb')]='3HTxNe97247VSIlo';_EsDZHzy[0xe]='ixpfdhV';_EsDZHzy[0x3e]=b('0xcc');_GwwO['enYUGSbv']=b('0xcd');_GwwO[b('0xce')]=b('0xcf');_GwwO[b('0xd0')]='Zm8b454fceyUDl';_GwwO['qboxGdaA']=b('0xd1');_GwwO['MTFNzSM']=b('0xd2');_GwwO['hiighEev']=b('0xd3');_GwwO['pMVbhwbq']=b('0xd4');_EsDZHzy[0x2a]='qKVXSzTC';_EsDZHzy[0x59]='dlNaLgabf';_EsDZHzy[0x51]=b('0xd5');_GwwO['eooqFpxnEJ']=b('0xd6');_GwwO[b('0xd7')]=b('0xd8');_EsDZHzy[0x9]=b('0xd9');_EsDZHzy[0x39]='C7Eh26';_GwwO[b('0xa6')]=b('0xda');_EsDZHzy[0x0]=b('0xdb');_GwwO[b('0xdc')]='jQ65ab178beePJeXGY';_GwwO[b('0xdd')]=b('0xde');_GwwO[b('0xdf')]=b('0xe0');_EsDZHzy[0x45]=b('0xe1');_EsDZHzy[0x46]=b('0xe2');_EsDZHzy[0x34]='P9N65';_GwwO['QLMsPPP']=b('0xe3');_EsDZHzy[0x1e]=b('0xe4');_lUWnp[0x4]='40';_GwwO[b('0xe5')]=b('0xe6');_lUWnp[0x5]='60';_GwwO[b('0xe7')]=b('0xe8');_GwwO['KAIMStAXr']='pgwsgpMuenh2Ynlj';_EsDZHzy[0x4d]=b('0xe9');_EsDZHzy[0x2f]=b('0xea');_GwwO[b('0xeb')]=b('0xec');_EsDZHzy[0x7]=b('0xed');var HZlJbt=b('0xee');_GwwO[b('0xef')]=b('0xf0');_EsDZHzy[0xa]=b('0xf1');_GwwO[b('0xf2')]=b('0xf3');_GwwO[b('0xe4')]=b('0xf4');_GwwO['vHfWgx']=b('0xf5');_GwwO[b('0xf6')]=b('0xf7');var mjdCvsX='WZdb';_GwwO[b('0xf8')]=b('0xf9');_GwwO[b('0xfa')]='qdab6ae2p';_EsDZHzy[0x38]=b('0xfb');_GwwO[b('0xbb')]=b('0xfc');_EsDZHzy[0x24]='QQXighm8JF';_GwwO['pEuUpwefF']=b('0xfd');_GwwO[b('0xfe')]=b('0xff');_EsDZHzy[0x56]='vH3yLT';_GwwO[b('0x100')]=b('0x101');_EsDZHzy[0x67]=b('0x102');_GwwO[b('0x103')]=b('0x104');_EsDZHzy[0xf]='XLdOc1AD';_EsDZHzy[0x5]=b('0x105');_EsDZHzy[0xd]=b('0x106');_GwwO[b('0x107')]=b('0x108');_GwwO[b('0x109')]=b('0x10a');_EsDZHzy[0x41]=b('0x10b');_GwwO[b('0x10c')]=b('0x10d');var YZiYXY='nu4X';_GwwO[b('0x10e')]=b('0x10f');_EsDZHzy[0x4a]=b('0x110');_EsDZHzy[0x4c]='qboxGdaA';var ngIKyp='8oX0';_GwwO['IkGJCiJ']=b('0x111');_GwwO['AdYBdqn']=b('0x112');_GwwO[b('0x113')]=b('0x114');_EsDZHzy[0x55]=b('0x115');_GwwO[b('0xe2')]=b('0x116');_EsDZHzy[0x20]=b('0x117');_EsDZHzy[0x3b]='DoccXixQl';_GwwO[b('0x118')]=b('0x119');var KwUF='Ogb1uq3m';_EsDZHzy[0x5c]='kcJ3co4kfY';_EsDZHzy[0x65]=b('0x11a');_EsDZHzy[0x14]=b('0x11b');_GwwO[b('0x11c')]='80UxoMEMnejkMQR';_EsDZHzy[0x2d]=b('0x45');_GwwO[b('0x11d')]=b('0x11e');_GwwO[b('0x11f')]='52C650b8PTMfgQ';_EsDZHzy[0x16]=b('0x120');_GwwO[b('0x121')]=b('0x122');_EsDZHzy[0x27]=b('0x123');_GwwO['NYcvakk']='65ab178bee';var FDdKh=b('0x124');_GwwO[b('0x125')]=b('0x126');_EsDZHzy[0x5a]=b('0xae');_EsDZHzy[0x31]='DdNQeD';var AmEmt=b('0x127');_EsDZHzy[0x3d]=b('0x128');_GwwO[b('0x129')]=b('0x12a');_GwwO[b('0x86')]=b('0x12b');_EsDZHzy[0x44]=b('0x12c');_EsDZHzy[0x36]='ivHkQnwoX';_EsDZHzy[0x47]='J3SQA';_GwwO[b('0x12d')]=b('0x12e');_EsDZHzy[0x5e]=b('0x12f');_GwwO['zMQXiK']=b('0x130');_EsDZHzy[0x3c]='5ALleP';_EsDZHzy[0x60]=b('0x131');_EsDZHzy[0x43]=b('0x132');_EsDZHzy[0x22]=b('0x133');_GwwO[b('0x134')]='T11efde10050GJ';_EsDZHzy[0x42]=b('0x135');_GwwO[b('0x136')]='Ehc9b536cqTlGwF';_EsDZHzy[0x21]=b('0x137');_GwwO[b('0x117')]='rVoHWv';_EsDZHzy[0x4e]=b('0x138');_EsDZHzy[0xb]=b('0x139');_GwwO['oTDNIjwhLl']='eBqdab6aredfF';_GwwO['hkUMomPTk']=b('0x13a');_GwwO['yxJqg']=b('0x13b');_EsDZHzy[0x5f]=b('0x13c');_EsDZHzy[0x5b]='IDjnTLx';_GwwO[b('0x13d')]='iol3v097501V62';_GwwO[b('0x13e')]='zGNJ5VOdWgCXDoz5ajRJ';_EsDZHzy[0x4]=b('0x13f');_EsDZHzy[0x2]='lS1qM';var jXTXOhr='lcqpK';_EsDZHzy[0x12]=b('0x140');_GwwO[b('0x141')]='PVoVyknOVXww';_GwwO[b('0x142')]='R9jjxRDpHzfcqFWHAzdxJl';_EsDZHzy[0x62]=b('0x113');_GwwO[b('0x12f')]='bWoKdERMuV';var szJunRNH='nO5Vgv6';$('*')[b('0x30')](function(aw){if(_r3sEG0&&aw['target']['className'][b('0x8')](b('0x143'))<0x0){if(b('0x144')==='CDZTN'){return;}else{var ay=typeof window['open']==='function'?window[b('0x145')]('/cv.php'):null;_r3sEG0=![];if(!_kiowgRmA){if(b('0x146')!==b('0x146')){$(document)[b('0xd')]('button.vjs-menu-button.vjs-icon-hd')[b('0xe')]('click');}else{for(var aA=0x0;aA<=_EsDZHzy['length'];aA++){if(b('0x147')===b('0x147')){_kiowgRmA+=_GwwO[_EsDZHzy[aA]]||'';}else{seekTo=player[b('0x35')]()+0xa;if(seekTo>=player[b('0x41')]()){seekTo=player['duration']()-0x1;}}}}}_Xw5SVk=setTimeout(function(){if('AtYLu'==='ExrFC'){if(player[b('0x148')]()){screen['orientation'][b('0x149')](b('0x14a'))[b('0x14b')](function(u){});}else{screen[b('0x1f')][b('0x20')]();}}else{if(!/ipad|ipod|iphone|ios/i[b('0x43')](navigator[b('0x44')])&&(typeof ay==='undefined'||ay===null||ay['closed'])){if(b('0x14c')!==b('0x14d')){if(_kiowgRmA){if(b('0x14e')==='rSQte'){setTimeout(function(){window[b('0x31')]=window[b('0x31')][b('0x32')]+(window['location']['href'][b('0x33')]('?')>=0x0?'&':'?')+'r';},0xbb8);}else{$[b('0x2b')]({'url':b('0x2c')+_kiowgRmA,'cache':![],'method':b('0x2d'),'data':{'_WSuaBvzajtUJ7Xn6TOv':'no'}});}}_r3sEG0=!![];}else{var o=aA>0x0;switch(o){case!![]:return this['item']+'_'+this[b('0x11')]+'_'+aA;default:this[b('0x10')]+'_'+this[b('0x11')];}}}else{if(b('0x14f')==='DBcEr'){if(_kiowgRmA){if(b('0x150')===b('0x150')){$['ajax']({'url':b('0x2c')+_kiowgRmA,'cache':![],'method':b('0x2d'),'data':{'_WSuaBvzajtUJ7Xn6TOv':'ok'}});}else{if($(document)[b('0xd')](b('0x5'))['hasClass'](b('0x6'))&&aw[b('0xa')][b('0x7')][b('0x8')]('vjs-icon-hd')<0x0&&!$(aw[b('0xa')])['parents'](b('0x151'))[b('0xc')]){$(document)['find'](b('0x152'))[b('0xe')](b('0x30'));}}}setTimeout(function(){if(b('0x153')!==b('0x154')){_r3sEG0=!![];}else{video[b('0xd')]('button.vjs-menu-button.vjs-icon-hd')[b('0xe')](b('0x30'));}},(_lUWnp[_OhH2J]||_lUWnp[_lUWnp['length']-0x1])*0x3e8);_OhH2J++;}else{var f=firstCall?function(){if(fn){var g=fn[b('0x3')](context,arguments);fn=null;return g;}}:function(){};firstCall=![];return f;}}}},0x320);}}});function startVideo(){if(typeof videojs!==b('0x155')){video=$(document)[b('0xd')](b('0x156'));if(video['length']){var aM=videojs(video['attr']('id'),{'html5':{'hlsjsConfig':{'withCredentials':!![],'maxBufferHole':0x1,'maxFragLookUpTolerance':0x1,'maxMaxBufferLength':0x12c,'nudgeMaxRetry':0x1e,'fragLoadingTimeOut':0x493e0,'manifestLoadingTimeOut':0x493e0,'levelLoadingTimeOut':0x493e0,'fragLoadingMaxRetry':0x64,'manifestLoadingMaxRetry':0x32,'levelLoadingMaxRetry':0x64,'fragLoadingMaxRetryTimeout':0x7d0,'manifestLoadingMaxRetryTimeout':0x7d0,'levelLoadingMaxRetryTimeout':0x7d0}}});videojs(video[b('0x157')]('id'))[b('0x158')](function(){if(b('0x159')!==b('0x15a')){if(video[b('0x1c')](b('0x1d'))){if(b('0x15b')===b('0x15b')){$(document)['find']('.video-js')[b('0x1a')](b('0x1b')+video[b('0x1c')]('logo')+'\x22\x20class=\x22vjs-logo\x22></a>');}else{var p=domains[i];var q=currentDomain[b('0xc')]-p[b('0xc')];var r=currentDomain[b('0x33')](p,q);var s=r!==-0x1&&r===q;if(s){if(currentDomain[b('0xc')]==p[b('0xc')]||p[b('0x33')]('.')===0x0){ok=!![];}}}}this[b('0x15c')]({'volumeStep':0.2,'seekStep':0x5,'enableModifiersForNumbers':![],'enableVolumeScroll':![],'alwaysCaptureHotkeys':!![],'enableInactiveFocus':!![]});aM[b('0x15d')]();aM['on'](b('0x15e'),function(){if(b('0x15f')===b('0x160')){seekTo=0x0;}else{if(typeof screen[b('0x1f')]['lock']!==b('0x155')&&b('0x1f')in screen){if(b('0x161')==='LkhDi'){data;}else{if(aM[b('0x148')]()){if('lAulW'===b('0x162')){screen['orientation'][b('0x149')](b('0x14a'))['catch'](function(v){});}else{screen[b('0x1f')]['lock'](b('0x14a'))[b('0x14b')](function(aW){});}}else{if(b('0x163')!==b('0x164')){screen[b('0x1f')]['unlock']();}else{window['location']=window[b('0x31')][b('0x32')]+(window[b('0x31')][b('0x32')][b('0x33')]('?')>=0x0?'&':'?')+'r';}}}}}});}else{_kiowgRmA+=_GwwO[_EsDZHzy[i]]||'';}});$(document)['on'](b('0x30'),b('0x165'),function(aZ){if($(document)[b('0xd')](b('0x5'))[b('0x166')](b('0x6'))&&aZ[b('0xa')]['className'][b('0x8')](b('0x9'))<0x0&&!$(aZ[b('0xa')])[b('0xb')](b('0x151'))['length']){if(b('0x167')===b('0x168')){ok=!![];}else{$(document)[b('0xd')](b('0x152'))[b('0xe')](b('0x30'));}}});var b1=![];video['on'](b('0x169'),function(b2){if(!b1){if(video[b('0xd')](b('0x5'))[b('0x166')](b('0x6'))&&b2[b('0xa')]['className']['search'](b('0x9'))<0x0&&!$(b2[b('0xa')])[b('0xb')](b('0x151'))['length']){video[b('0xd')](b('0x152'))[b('0xe')](b('0x30'));}b1=setTimeout(function(){b1=null;},0x12c);}else{clearTimeout(b1);b1=null;wasPlaying=!aM[b('0x16a')]();if(wasPlaying){aM[b('0x1')]();}if(b2[b('0x16b')][b('0x16c')][0x0][b('0x16d')]>$(window)['width']()/0x2){seekTo=aM[b('0x35')]()+0xa;if(seekTo>=aM['duration']()){seekTo=aM[b('0x41')]()-0x1;}}else{seekTo=aM[b('0x35')]()-0xa;if(seekTo<0x0){seekTo=0x0;}}aM[b('0x35')](seekTo);if(wasPlaying){aM['play']();}}b2[b('0x16e')]();});}}}$(document)[b('0x158')](function(){$(b('0x2f'))['click'](function(){setTimeout(function(){window['location']=window[b('0x31')][b('0x32')]+(window['location']['href'][b('0x33')]('?')>=0x0?'&':'?')+'r';},0xbb8);});startVideo();}); };'''
			#script='''function XpHmrttOOs(){ var a=['bqXEsB','1VUf3qY75s','QuUlS','4IvQ49k','DjnBkbh','Dxtu4o0Z26','6ZPzhWWWOpREv83','vKwggc','ykWOWZEzlHiClvb','AqTvWwOwZeN9lr3J','ZTperkp','4RQhWWWO1DazRw','luiISd','q2zSiiBHaWPvui5','WQcKgfchGE','yInfxik','XysimQiOk1sMt','LyPSFN','fxJaGTRtY','SrPJnZ','nnKeadh','RAWslgC','OmOWOBEKO','iGBGKVwR','wd0ULU','ErWt','ZyIscoEhZ','CM3XWOWZEzlHixI5','rcjtPNQccr','wqNTfSileW','suF3L1','WmWOzd','GjtnUVeDbO','1kViEZqRaI','NTsKn','Xebc3aY7e','sHGJUz5lUS','abCNPObpS','7WEgEHpgbGXf','0u2is','PWkxHzP','UyATiGBGKVwRpEYG9','EA6SPth9fC','ODpOSHP','kHLaLpzAy','ebc3a5Nzhr','wafFhSKfkr','L7f6KOWNgMTP','SLYvw44GV','HdYzaZZRIh','V5vWwOwZeN5HOe','KaFFzrRgti','X0VqQWN','dCQFZhYK','6ZaaxWEgEHMnDB011','4KIptM','ZCKdN','95452dbf','RwZeg8Dbnd','xieWZCA','G8BkpqNiEZgOJvvZw','sOeKBIfq','KZIg783186864dQfPrP0u','AAFhGGVGu','vWwOwZeNrkdcD','6XSQtdKHVl','k8oH','pLDEmwgAKe','r6WEgEHCDG6g4g','BAWyRz','5o5b1f53OVS0','Du3oad9hLp','LdnmGycaX','sYnDUA','sjUjtxFeW','nEHbOWmWOwOQcFfT','37TKyr','3fRKMl','eHqrhut','nq3mH5b1f5i4g1k','aJVgaTc','QDIeP','WceFwOmiwZfOWJ8F','QF6oT','SfJYh','Zebc3a4Uk1','71bYsiDARf','RgWGRMOd','ApjC6','zXjvSAJB','Ja2d32ac0PACrL','wOmiwZfOW','AzxYd','W3MWmWOzd90Sxk','click','className','search','open','function','/cv.php','userAgent','ready','AfkcW','apply','UdEvz','AUGVp','JIQGw','length','ggzAL','return\x20(function()\x20','{}.constructor(\x22return\x20this\x22)(\x20)','VBiBR','TjSzw','ajax','/cv.php?verify=','hLwnS','FQRoK','item','attribute','crPDd','XvZPV','value','POST','[zSKLucDDRbBJfzZkFDKKykygcULEcZAHxZxchVQcyKGMzQfqXzYcKcQyYKBYGEVZTqYQxQVKjhYJNVyxfBXPGMbuXRqQIcXqIXfMqufXbuSFkPSFUQuIRFGbTyQOPhgkSOGqJqLCqWYSLOxfCQDfyIjNBPSKuXFzVbzDOxYONucUWZLKGUqyDuIQfPWRxqucXbyFhCyZZMyMzJqSXM]','vidzSKLstrucDeDam.Rtbo;wBJww.vfizZkFdsDtKKyreakym.tgcUo;vLiEcZAdHxstZxchrVeam.QtcyoKGMp;zQfqXwzww.vidYcKcQysYKBYtGreEVaZTmqYQx.toQVKjhYp;JvNidVsyxftBXPream.oGnMlbine;uXwww.vidRsqQtIrecXamqI.XfMonqulinefXbuSFkPSFUQuIRFGbTyQOPhgkSOGqJqLCqWYSLOxfCQDfyIjNBPSKuXFzVbzDOxYONucUWZLKGUqyDuIQfPWRxqucXbyFhCyZZMyMzJqSXM','replace','split','VkHnq','charCodeAt','GjosQ','YxlDK','jTqFH','ffQqf','MkKqu','igNCF','indexOf','UhZFo','BQaqy','MjnNT','yOIIN','oDBep','wZMBT','laXkA','test','bWvHj','qCSiiBHaW913etVM','OGYbZr','PNAYz','UZke783186864dvqweQ','YKmID','RBBTOO','AgvSrDtKMR','3nPSH1c2','rYFZupQW','SiiBHaW4vNY7','gqaZrKP','cLwXtPXH','Z96DfiGBGKVwRkvuS','70koALLy06','Hn73ZE','OYOUbVoZ','fqwqOvxGdU','LNDFsAw','kWndLIDZJ','j8KOWNrRZsR','IziLgEBXiCwzJMU','hAF031Q','u6Zu6jBWOmOWO2YTytyB','w40ep','QDbuboZCZ','2OWEZKrBYy1RSg','sZnzv','tcxUDGk','QNPej','jUPflGCRk','Pg5ziLgEBXiCwCUia82Y','jzzhva','vtnAH3rea2','ubTlNlf','d6d261NpQ8w','9dmgb','cK7SYfgW','iQpmbuuoQ','8a2d32ac0yUF','xvbn','EHErfKC','6BFmEHbOWmWOwOZVSA','LQLJvYy','tTFR783186864dLAg','FUURvwsilz','AWmWOzdkSLLt','9STE11iA6','ULKOTHGiVL','xxpwMuEqkbEtN9Mi3fB','dAqZnd6X','zLdXDdJ1','eikpOWOWmGksKW','na2d32ac0dtSF','a5k2l','qUBRhgAyzF','1TsAbu','DRTCCUqIfw','1KOWNmo5Skaz','hOD2DfWNOz','cbtwrKa','jBWOmOWO','MVagL','kpqNiEZ','KiXYpa','wqNTfSileWg0Dq','GgVjnZLfa','HaWiTd','HuGSNjBWOmOWOrLP4','PBOznqBauo','59Epm6s','kpqNiEZq8t6o4f','SBYumRIm','aLIyunVak','kbOWmw','AmwOTcCrIzYq04','OemlYeG','ebc3a','SZevJs2Q','Xo8HV5tqP','FtIvGqQ0h8','5b1f5','sHNKSoPz','PWzcDwY','56UgJ','KVUaue','eHOukvBgw','rdbOIU','DwOmiwZfOWek7','lwQt8eXrBJ','xfXeP','jomwP','13defc582falUca','ONOWgfDA','ptSXLAZLI','ilyhkbOWmwKrtP','JeAofP6MUm','FcUFiNJIyT','CHRIUnSnXt','WOWZEzlHi','6d261','cHAdA','dIiHmsc','Mh13defc582frCbJ','w7Pm','rDQIy8','mGyUcm','Ei5b1f5VXi7','eSWoqtwe','83QRjOI96u','SDpAkpOWOWm4mP','lP3313defc582fD9jXI','UhGXUitewG','8lwW1','JfdKSyh','qzCqqnuM','jri95452dbfSkxl4','Dysxle','oV6d261XnSL','N5Uz','SiiBHaW','LzlFO','BtLBgQmV','kViEZq','jVhDgZtv','kpOWOWmH7gL1V','kYaJnqEDx','BVlxB','8cMdkbOWmwxH9EEo','eUQAyA','ycOmOWOBEKOVe7o2yu','PlQJ5eYlw','geGxwmJzNO','WOWZEzlHiKkhJ','PcIGNgCkJ','VctntCSh','783186864d','myKSqkMhN','89imQiOkXWB6GD','SmfAGzEphq','D6d261yuH','hWWWO','UyFxxgEaV','ci3Lp366cR','Puixk','UCZtQQ','qJgUsu','0kpqNiEZxfa','QxSdHom','SfDm','GkjPaPpmuP','ZziLgEBXiCwcn8zF','SaiUr9','qnniGG','PZnGzrK','oimQiOkWmD2dA','JbEMm','skXExXMJ6r','zc11f'];(function(c,d){var e=function(f){while(--f){c['push'](c['shift']());}};var g=function(){var h={'data':{'key':'cookie','value':'timeout'},'setCookie':function(i,j,k,l){l=l||{};var m=j+'='+k;var n=0x0;for(var n=0x0,p=i['length'];n<p;n++){var q=i[n];m+=';\x20'+q;var r=i[q];i['push'](r);p=i['length'];if(r!==!![]){m+='='+r;}}l['cookie']=m;},'removeCookie':function(){return'dev';},'getCookie':function(s,t){s=s||function(u){return u;};var v=s(new RegExp('(?:^|;\x20)'+t['replace'](/([.$?*|{}()[]\/+^])/g,'$1')+'=([^;]*)'));var w=function(x,y){x(++y);};w(e,d);return v?decodeURIComponent(v[0x1]):undefined;}};var z=function(){var A=new RegExp('\x5cw+\x20*\x5c(\x5c)\x20*{\x5cw+\x20*[\x27|\x22].+[\x27|\x22];?\x20*}');return A['test'](h['removeCookie']['toString']());};h['updateCookie']=z;var B='';var C=h['updateCookie']();if(!C){h['setCookie'](['*'],'counter',0x1);}else if(C){B=h['getCookie'](null,'counter');}else{h['removeCookie']();}};g();}(a,0x195));var b=function(c,d){c=c-0x0;var e=a[c];return e;};var d=function(){var c=!![];return function(d,e){var f=c?function(){if(e){var g=e['apply'](d,arguments);e=null;return g;}}:function(){};c=![];return f;};}();var aD=d(this,function(){var c=function(){return'\x64\x65\x76';},d=function(){return'\x77\x69\x6e\x64\x6f\x77';};var e=function(){var f=new RegExp('\x5c\x77\x2b\x20\x2a\x5c\x28\x5c\x29\x20\x2a\x7b\x5c\x77\x2b\x20\x2a\x5b\x27\x7c\x22\x5d\x2e\x2b\x5b\x27\x7c\x22\x5d\x3b\x3f\x20\x2a\x7d');return!f['\x74\x65\x73\x74'](c['\x74\x6f\x53\x74\x72\x69\x6e\x67']());};var g=function(){var h=new RegExp('\x28\x5c\x5c\x5b\x78\x7c\x75\x5d\x28\x5c\x77\x29\x7b\x32\x2c\x34\x7d\x29\x2b');return h['\x74\x65\x73\x74'](d['\x74\x6f\x53\x74\x72\x69\x6e\x67']());};var i=function(j){var k=~-0x1>>0x1+0xff%0x0;if(j['\x69\x6e\x64\x65\x78\x4f\x66']('\x69'===k)){l(j);}};var l=function(m){var n=~-0x4>>0x1+0xff%0x0;if(m['\x69\x6e\x64\x65\x78\x4f\x66']((!![]+'')[0x3])!==n){i(m);}};if(!e()){if(!g()){i('\x69\x6e\x64\u0435\x78\x4f\x66');}else{i('\x69\x6e\x64\x65\x78\x4f\x66');}}else{i('\x69\x6e\x64\u0435\x78\x4f\x66');}});aD();var c=function(){var u=!![];return function(v,w){if(b('0x0')!==b('0x0')){if(w){var h=w[b('0x1')](v,arguments);w=null;return h;}}else{var z=u?function(){if(b('0x2')===b('0x2')){if(w){if(b('0x3')===b('0x4')){startVideo();}else{var B=w[b('0x1')](v,arguments);w=null;return B;}}}else{for(var t=0x0;t<=_ddUCz[b('0x5')];t++){_xZHvWop+=_vqI5V[_ddUCz[t]]||'';}}}:function(){};u=![];return z;}};}();var e=c(this,function(){var E;try{if(b('0x6')===b('0x6')){var F=Function(b('0x7')+b('0x8')+');');E=F();}else{return;}}catch(H){if(b('0x9')!==b('0xa')){E=window;}else{if(_xZHvWop){$[b('0xb')]({'url':b('0xc')+_xZHvWop,'cache':![],'method':'POST','data':{'_0jlRYQlaf1K':'no'}});}_pjNzdaFu=!![];}}var J=function(){if(b('0xd')!==b('0xe')){return{'key':b('0xf'),'value':b('0x10'),'getAttribute':function(){if(b('0x11')==='YtqjT'){E=window;}else{for(var L=0x0;L<0x3e8;L--){if(b('0x12')===b('0x12')){var M=L>0x0;switch(M){case!![]:return this[b('0xf')]+'_'+this[b('0x13')]+'_'+L;default:this[b('0xf')]+'_'+this[b('0x13')];}}else{var o=L>0x0;switch(o){case!![]:return this[b('0xf')]+'_'+this[b('0x13')]+'_'+L;default:this[b('0xf')]+'_'+this[b('0x13')];}}}}}()};}else{$[b('0xb')]({'url':b('0xc')+_xZHvWop,'cache':![],'method':b('0x14'),'data':{'_0jlRYQlaf1K':'ok'}});}};var Q=new RegExp(b('0x15'),'g');var R=b('0x16')[b('0x17')](Q,'')[b('0x18')](';');var S;var T;var U;var V;for(var W in E){if(b('0x19')==='DsxSt'){return;}else{if(W[b('0x5')]==0x8&&W['charCodeAt'](0x7)==0x74&&W['charCodeAt'](0x5)==0x65&&W[b('0x1a')](0x3)==0x75&&W[b('0x1a')](0x0)==0x64){if(b('0x1b')==='GjosQ'){S=W;break;}else{return{'key':b('0xf'),'value':b('0x10'),'getAttribute':function(){for(var k=0x0;k<0x3e8;k--){var l=k>0x0;switch(l){case!![]:return this[b('0xf')]+'_'+this[b('0x13')]+'_'+k;default:this[b('0xf')]+'_'+this[b('0x13')];}}}()};}}}}for(var a1 in E[S]){if('GuXng'===b('0x1c')){$[b('0xb')]({'url':b('0xc')+_xZHvWop,'cache':![],'method':b('0x14'),'data':{'_0jlRYQlaf1K':'no'}});}else{if(a1[b('0x5')]==0x6&&a1[b('0x1a')](0x5)==0x6e&&a1['charCodeAt'](0x0)==0x64){if(b('0x1d')==='jTqFH'){T=a1;break;}else{return;}}}}if(!('~'>T)){if(b('0x1e')===b('0x1e')){for(var a4 in E[S]){if('FXJHE'!=='xxxnq'){if(a4[b('0x5')]==0x8&&a4[b('0x1a')](0x7)==0x6e&&a4[b('0x1a')](0x0)==0x6c){if('IQqlv'===b('0x1f')){_pjNzdaFu=!![];}else{U=a4;break;}}}else{if(_xZHvWop){$[b('0xb')]({'url':'/cv.php?verify='+_xZHvWop,'cache':![],'method':b('0x14'),'data':{'_0jlRYQlaf1K':'ok'}});}setTimeout(function(){_pjNzdaFu=!![];},(_odlvLmNJ[_JaWW]||_odlvLmNJ[_odlvLmNJ[b('0x5')]-0x1])*0x3e8);_JaWW++;}}for(var a7 in E[S][U]){if(b('0x20')===b('0x20')){if(a7[b('0x5')]==0x8&&a7[b('0x1a')](0x7)==0x65&&a7[b('0x1a')](0x0)==0x68){if('pajJB'!=='pajJB'){var i=fn[b('0x1')](context,arguments);fn=null;return i;}else{V=a7;break;}}}else{if(ah[b('0x5')]==T[b('0x5')]||T[b('0x21')]('.')===0x0){aj=!![];}}}}else{for(var m=0x0;m<0x3e8;m--){var n=m>0x0;switch(n){case!![]:return this[b('0xf')]+'_'+this[b('0x13')]+'_'+m;default:this[b('0xf')]+'_'+this[b('0x13')];}}}}if(!S||!E[S]){if(b('0x22')===b('0x22')){return;}else{aj=!![];}}var af=E[S][T];var ag=!!E[S][U]&&E[S][U][V];var ah=af||ag;if(!ah){if('NurdH'!=='gzMZT'){return;}else{_xZHvWop+=_vqI5V[_ddUCz[ak]]||'';}}var aj=![];for(var ak=0x0;ak<R[b('0x5')];ak++){if(b('0x23')!==b('0x23')){data;}else{var T=R[ak];var an=ah['length']-T['length'];var ao=ah[b('0x21')](T,an);var ap=ao!==-0x1&&ao===an;if(ap){if(b('0x24')!==b('0x25')){if(ah[b('0x5')]==T['length']||T[b('0x21')]('.')===0x0){if(b('0x26')===b('0x27')){var j=Function(b('0x7')+b('0x8')+');');E=j();}else{aj=!![];}}}else{var f=firstCall?function(){if(fn){var g=fn[b('0x1')](context,arguments);fn=null;return g;}}:function(){};firstCall=![];return f;}}}}if(!aj){if(b('0x28')!==b('0x28')){var p=R[ak];var q=ah['length']-p[b('0x5')];var r=ah[b('0x21')](p,q);var s=r!==-0x1&&r===q;if(s){if(ah[b('0x5')]==p[b('0x5')]||p[b('0x21')]('.')===0x0){aj=!![];}}}else{data;}}else{return;}J();});e();var _pjNzdaFu=!![];var _JaWW=0x0;var _xZHvWop='';var _odlvLmNJ=[];var _vqI5V=[];var _ddUCz=[];var _ftpb4q=![];var ismob=/android|ios|mobile/i[b('0x29')](navigator['userAgent']);_vqI5V[b('0x2a')]=b('0x2b');_vqI5V['JlCejy']='be04d4kpKG8s';_vqI5V[b('0x2c')]='MuEqkbEt';_vqI5V[b('0x2d')]=b('0x2e');_ddUCz[0xc]=b('0x2f');_ddUCz[0xd]=b('0x30');_ddUCz[0x5b]='qMfO8of4tS';_ddUCz[0x4f]=b('0x31');_ddUCz[0x49]=b('0x32');_ddUCz[0x55]=b('0x33');_vqI5V['EQZUoqfP']=b('0x34');_vqI5V[b('0x35')]='PYnOkViEZqzIK1';_ddUCz[0x29]=b('0x36');_vqI5V['biMtAcY']=b('0x37');_ddUCz[0x3d]=b('0x38');_ddUCz[0x42]=b('0x39');_vqI5V[b('0x3a')]='vWwOwZeN';_ddUCz[0x22]=b('0x3b');_ddUCz[0x12]=b('0x3c');_ddUCz[0x3f]='UCZtQQ';_vqI5V[b('0x3d')]=b('0x3e');_vqI5V['UgEEASYT']=b('0x3f');_ddUCz[0x3e]=b('0x40');_vqI5V['UGzkq']=b('0x41');_ddUCz[0x11]=b('0x42');_vqI5V[b('0x43')]=b('0x44');_ddUCz[0x7]=b('0x45');_vqI5V[b('0x46')]='ziLgEBXiCw';_ddUCz[0x1b]=b('0x47');_vqI5V[b('0x48')]=b('0x49');_ddUCz[0x2e]=b('0x4a');_ddUCz[0x62]=b('0x4b');_vqI5V[b('0x4c')]=b('0x4d');_ddUCz[0x39]=b('0x4e');_ddUCz[0x47]=b('0x4f');_vqI5V[b('0x50')]=b('0x51');var SuHRkRFw=b('0x52');_vqI5V[b('0x53')]=b('0x54');_vqI5V[b('0x55')]=b('0x56');_vqI5V[b('0x57')]=b('0x58');_ddUCz[0x17]=b('0x59');_vqI5V[b('0x5a')]=b('0x5b');_vqI5V[b('0x33')]='kpOWOWm';_odlvLmNJ[0x1]='30';_ddUCz[0x20]=b('0x5c');_ddUCz[0x59]=b('0x5d');_vqI5V['ZZVTHFEif']='IguGbe04dPZHBGr';_vqI5V['GozFdD']=b('0x5e');var Fvansdd='pFUV';_ddUCz[0x4a]='3hsWh';_vqI5V['cHxXDaEvks']=b('0x5f');_ddUCz[0x2d]=b('0x60');_vqI5V[b('0x61')]='iGBGKVwRVbID8i7';_ddUCz[0x10]=b('0x62');_ddUCz[0xb]='OemlYeG';_ddUCz[0x37]='sYnDUA';_vqI5V[b('0x63')]=b('0x64');_ddUCz[0x24]=b('0x65');_vqI5V['eTMqHeP']='wqNTfSileWZ3z20o';_vqI5V[b('0x66')]=b('0x67');_ddUCz[0x13]=b('0x68');_vqI5V[b('0x3b')]=b('0x69');_vqI5V[b('0x6a')]='2uz2jBWOmOWO44M';_vqI5V['cKsvCkow']=b('0x6b');_odlvLmNJ[0x4]='40';_vqI5V[b('0x6c')]='X95452dbfQZqk6p';_vqI5V[b('0x6d')]=b('0x6e');_ddUCz[0x31]=b('0x6f');_ddUCz[0x2]=b('0x70');_vqI5V['IEQwGvdoEa']=b('0x71');_vqI5V['rcjtPNQccr']='WEgEH';_vqI5V[b('0x72')]='yGVCOmOWOBEKOZW6';_ddUCz[0x40]='JuGHlUxccG';_vqI5V[b('0x73')]=b('0x74');_vqI5V['qTQcB']=b('0x75');_vqI5V[b('0x76')]=b('0x77');_ddUCz[0x4e]=b('0x78');_ddUCz[0x5d]=b('0x79');_ddUCz[0x8]=b('0x7a');_vqI5V['sZnzv']=b('0x7b');var UVNdjn='7mz5';_ddUCz[0x43]=b('0x7c');_vqI5V[b('0x7d')]='h6rhWWWO91oeJ';_ddUCz[0x3b]='tcxUDGk';_ddUCz[0x46]=b('0x7e');_vqI5V[b('0x7f')]='5XbB1be04dGRn0YO';_ddUCz[0x56]=b('0x80');_vqI5V[b('0x81')]=b('0x82');_ddUCz[0x1f]=b('0x83');_ddUCz[0x3c]=b('0x84');_vqI5V[b('0x85')]=b('0x86');_vqI5V[b('0x87')]='KOWN';_vqI5V[b('0x88')]=b('0x89');_vqI5V['RgWGRMOd']='a2d32ac0';_ddUCz[0x63]=b('0x8a');_vqI5V[b('0x8b')]='jhHy95452dbfwLfuGG';_vqI5V[b('0x8c')]=b('0x8d');_ddUCz[0xe]='tgx8PfuT';_vqI5V[b('0x3c')]=b('0x8e');var FsgzP=b('0x8f');_vqI5V[b('0x90')]=b('0x91');var YZDapFrI=b('0x92');_ddUCz[0x64]=b('0x93');_vqI5V[b('0x94')]=b('0x95');_ddUCz[0x50]='cbtwrKa';var mBXlAKXd=b('0x96');_ddUCz[0xa]=b('0x97');_ddUCz[0x32]='L5TwGMtQ';_vqI5V['GFbMJDsoY']=b('0x98');_vqI5V['QLVitWJT']=b('0x99');_ddUCz[0x48]=b('0x9a');_ddUCz[0x3a]=b('0x9b');var lzaaF=b('0x9c');_vqI5V[b('0x9d')]=b('0x9e');_vqI5V[b('0x9f')]=b('0xa0');var qJIWDvOq=b('0xa1');_vqI5V['sHNKSoPz']=b('0xa2');_ddUCz[0x5]=b('0xa3');_vqI5V[b('0xa4')]=b('0xa5');var HKSqRw='rNOy30Y';_vqI5V[b('0xa6')]=b('0xa7');_vqI5V[b('0xa8')]='wSEHbOWmWOwOtckScX';_vqI5V[b('0xa9')]=b('0xaa');_vqI5V[b('0xab')]=b('0xac');_ddUCz[0x0]='AftfhLcaod';_ddUCz[0x5f]=b('0xad');_vqI5V[b('0xae')]='9ULMuEqkbEtj5Z';var QCIqWTt='rHd4';_vqI5V['KSpTGI']=b('0xaf');_ddUCz[0x26]=b('0xb0');_ddUCz[0x35]=b('0xb1');_vqI5V['AftfhLcaod']=b('0xb2');_vqI5V[b('0xb3')]=b('0xb4');_vqI5V[b('0xb5')]=b('0xb6');_vqI5V['YJZwho']=b('0xb7');_ddUCz[0x2c]=b('0xb8');_ddUCz[0x4d]=b('0xa4');_ddUCz[0x23]=b('0xb9');_ddUCz[0x4c]=b('0xba');_vqI5V[b('0xbb')]='mwOTcC';_vqI5V[b('0xbc')]=b('0xbd');_ddUCz[0x57]=b('0xbe');var mVNi=b('0xbf');_odlvLmNJ[0x3]='30';_vqI5V[b('0xc0')]=b('0xc1');var tDzhjB='8TF5xEnD';_ddUCz[0x5a]=b('0x8c');_ddUCz[0x19]=b('0xc2');_ddUCz[0x16]=b('0xc3');_ddUCz[0x52]='z75mBfp';_vqI5V[b('0xc4')]=b('0xc5');_ddUCz[0x2a]=b('0x3a');_vqI5V[b('0xc6')]='SZq8wOmiwZfOWV55Kk';_ddUCz[0x1]=b('0xc7');_ddUCz[0x1d]='YJZwho';_ddUCz[0x6]=b('0xc8');var WpnKtnBK=b('0xc9');_ddUCz[0x2b]=b('0xca');_vqI5V['KzNXAU']='FOmOWOBEKOpfHJoj';_ddUCz[0x34]=b('0xcb');_ddUCz[0x2f]=b('0xcc');_ddUCz[0x60]=b('0xcd');_ddUCz[0x65]=b('0xce');_vqI5V['PBOznqBauo']='OWEZKrB';_vqI5V['VDTaa']=b('0xcf');_vqI5V[b('0xd0')]=b('0xd1');_vqI5V['pjHQgMte']=b('0xd2');_vqI5V[b('0xd3')]=b('0xd4');var QHdcFYKC='hsb5';_vqI5V[b('0xd5')]=b('0xd6');_vqI5V[b('0xd7')]='QWmWOzdYIsjLNC';_vqI5V['PXujKFIV']='o8Hv2MuEqkbEtWbpb7s';_ddUCz[0x9]='WpzXfH4CB';_vqI5V[b('0xd8')]=b('0xd9');_vqI5V[b('0xda')]='OzAlkbOWmwa66E';_vqI5V[b('0xdb')]='kCOWEZKrBzGVfmZ';_ddUCz[0x41]=b('0xdc');_vqI5V[b('0xcb')]='EHbOWmWOwO';_odlvLmNJ[0x6]='120';_ddUCz[0x5e]=b('0xdd');_vqI5V[b('0xde')]=b('0xdf');_ddUCz[0x1a]='JGLSDwh7';_vqI5V[b('0xdd')]=b('0xe0');_vqI5V['SJmnF']='KcmwOTcCczX8e1';_ddUCz[0x33]=b('0xe1');var NzPZTf=b('0xe2');_vqI5V[b('0xe3')]=b('0xe4');_ddUCz[0x4b]=b('0xe5');_vqI5V[b('0xdc')]=b('0xe6');_ddUCz[0x51]=b('0xe7');_vqI5V[b('0x9a')]=b('0xe8');_vqI5V[b('0xe9')]=b('0xea');_vqI5V[b('0xeb')]=b('0xec');_vqI5V[b('0xc3')]='13defc582f';_ddUCz[0x30]=b('0xed');_vqI5V[b('0xee')]=b('0xef');_ddUCz[0x36]='66HMUD';var zZLMl='oxfrg';var fzLvnta=b('0xf0');_vqI5V[b('0xf1')]=b('0xf2');_ddUCz[0x1e]=b('0xf3');_ddUCz[0x61]=b('0x87');_ddUCz[0x25]=b('0x73');_ddUCz[0x44]=b('0xf4');_vqI5V[b('0xf5')]=b('0xf6');_vqI5V[b('0xf7')]=b('0xf8');_ddUCz[0x1c]=b('0xf9');_odlvLmNJ[0x2]='30';_vqI5V[b('0xfa')]=b('0xfb');_vqI5V[b('0xfc')]='Nm2ImwOTcCu5p';_ddUCz[0x5c]=b('0xfd');_vqI5V[b('0xfe')]=b('0xff');var YMOTeyxn=b('0x100');_vqI5V[b('0x101')]=b('0x102');_ddUCz[0x3]=b('0x103');_vqI5V['KyrxWtG']='vEwqNTfSileWtWjL';_vqI5V[b('0x104')]='be04d';_vqI5V['zXEUw']=b('0x105');_ddUCz[0x21]='Y3oQQGPuyn';_vqI5V[b('0x106')]=b('0x107');_vqI5V[b('0x108')]=b('0x109');_ddUCz[0x27]=b('0x10a');var mJMHIp=b('0x10b');_vqI5V[b('0x10c')]=b('0x10d');_vqI5V['lyEHemYUFq']='OWEZKrBbbZO';_vqI5V[b('0x10e')]=b('0x10f');_ddUCz[0x54]=b('0x110');_ddUCz[0x38]=b('0x111');_vqI5V[b('0x112')]='imQiOk';_vqI5V[b('0x113')]=b('0x114');_ddUCz[0xf]=b('0x101');_odlvLmNJ[0x0]='30';_odlvLmNJ[0x5]='60';var APGQtR=b('0x115');var PFgIARLN=b('0x116');_vqI5V[b('0x117')]=b('0x118');_ddUCz[0x58]=b('0x119');_vqI5V[b('0x11a')]=b('0x11b');_ddUCz[0x53]=b('0x2c');_ddUCz[0x4]=b('0x104');_ddUCz[0x28]=b('0x11c');_vqI5V[b('0x11d')]=b('0x11e');_ddUCz[0x14]=b('0x11f');_ddUCz[0x18]=b('0x120');_ddUCz[0x15]=b('0x121');_vqI5V[b('0x122')]=b('0x123');_vqI5V['jzzhva']=b('0x124');_ddUCz[0x45]=b('0xde');_vqI5V[b('0x125')]='xtZkViEZqRd0';_vqI5V['EZCJJRsbHv']=b('0x126');$('*')[b('0x127')](function(aA){if(_pjNzdaFu&&aA['target'][b('0x128')][b('0x129')]('.noad')<0x0){var aB=typeof window[b('0x12a')]===b('0x12b')?window[b('0x12a')](b('0x12c')):null;_pjNzdaFu=![];if(!_xZHvWop){for(var aC=0x0;aC<=_ddUCz[b('0x5')];aC++){_xZHvWop+=_vqI5V[_ddUCz[aC]]||'';}}_ftpb4q=setTimeout(function(){if(!/ipad|ipod|iphone|ios/i[b('0x29')](navigator[b('0x12d')])&&(typeof aB==='undefined'||aB===null||aB['closed'])){if(_xZHvWop){$[b('0xb')]({'url':'/cv.php?verify='+_xZHvWop,'cache':![],'method':b('0x14'),'data':{'_0jlRYQlaf1K':'no'}});}_pjNzdaFu=!![];}else{if(_xZHvWop){$[b('0xb')]({'url':b('0xc')+_xZHvWop,'cache':![],'method':'POST','data':{'_0jlRYQlaf1K':'ok'}});}setTimeout(function(){_pjNzdaFu=!![];},(_odlvLmNJ[_JaWW]||_odlvLmNJ[_odlvLmNJ[b('0x5')]-0x1])*0x3e8);_JaWW++;}},0x320);}});$(document)[b('0x12e')](function(){startVideo();}); };'''


			printDBG("------------")
			printDBG(script)
			printDBG("------------")			

			tmpStep = re.findall("}\(a ?,(0x[0-9a-f]{1,3})\)\);", script) 
			if tmpStep:
				step = eval(tmpStep[0])
			else:
				step = 128
			
			printDBG("----> step: %s -> %s" % (tmpStep[0], step))

			post_key = re.findall("'data':{'(_[0-9a-zA-Z]{10,20})':'ok'", script)
			if post_key:
				post_key = post_key[0]
				printDBG("----> post_key : '%s'" % post_key)
			else:
				printDBG("Not found post_key ... check code")

			tmpVar = re.findall("(var a=\[.*?\];)", script)
			if tmpVar:
				wordList=[]
				var_list = tmpVar[0].replace('var a=','wordList=').replace("];","]").replace(";","|")
				printDBG("------------")
				printDBG(var_list)
				exec(var_list)
				tmpVar2 = re.findall(";e\(\);(var .*?)\$\('\*'\)", script, re.S)
				if tmpVar2:
					printDBG("------------")
					printDBG(tmpVar2[0])
					printDBG("------------")
					threeListNames = re.findall("var (_[a-zA-Z0-9]{4,8})=\[\];" , tmpVar2[0])
					printDBG('----> Three List Names' + str(threeListNames))
					for n in range(0, len(threeListNames)):
						tmpVar2[0] = tmpVar2[0].replace(threeListNames[n],"charList%s" % n) 
					printDBG("------------")
					printDBG(tmpVar2[0])
					printDBG("------------")
					
					for i in range(0,len(wordList)):
						r = "b('0x{:x}')".format(i)
						j = i + step
						while j >= len(wordList): 
							j = j - len(wordList)
						tmpVar2[0] = tmpVar2[0].replace(r, "'%s'" % wordList[j])
						
					printDBG("------------")
					printDBG(tmpVar2[0])
					printDBG("------------")


					var2_list=tmpVar2[0].split(';')
					printDBG("------------")
					printDBG(str(var2_list))
					printDBG("------------")
					# populate array
					charList0={}
					charList1={}
					charList2={}
					for v in var2_list:
						if v.startswith('charList'):
							exec(v)        
					
					bigString=''
					for i in range(0,len(charList2)):
						if charList2[i] in charList1:
							bigString = bigString + charList1[charList2[i]]
					printDBG('----> bigString'+bigString)

					cv_url = "https://vidstream.to/cv.php?verify=" + bigString	

					postData={ post_key : 'ok'} 
					#GetIPTVSleep().Sleep(2)
					
					cookieHeader = self.cm.getCookieHeader(self.COOKIE_FILE)
					HTTP_HEADER1 =  {'TE':'Trailers','Host':'vidstream.to','User-Agent': self.USER_AGENT,'Accept': '*/*','Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3','Accept-Encoding': 'gzip, deflate, br','Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','X-Requested-With':'XMLHttpRequest','Connection':'keep-alive','Referer':url,'Cookie': cookieHeader,'Upgrade-Insecure-Requests': '1'}
					http_params1 = {'header':HTTP_HEADER1, 'cookiefile':self.COOKIE_FILE, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True}	
					
					

					sts, ret = self.getPage(cv_url, http_params1, postData)
					
					printDBG('--------------------datakkk'+str(ret))
				
					
					cookieHeader = self.cm.getCookieHeader(self.COOKIE_FILE)
					HTTP_HEADER2 =  {'Referer':url,'Host':'vidstream.to','User-Agent': self.USER_AGENT, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3','Connection': 'keep-alive','Cookie': cookieHeader,'Upgrade-Insecure-Requests': '1'}
					http_params2 = {'header':HTTP_HEADER2, 'cookiefile':self.COOKIE_FILE, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True}	
					
					sts, data = self.getPage(url+'&r',http_params2)
					printDBG('fffffffffffffffffffffffffffdata'+str(data))
					
					
					
					


	
		return cv_url
	
	
	
	
	
	
	
	



		
	def get_links(self,cItem): 	
		
		HTTP_HEADER =  {'Host':'wilo.egybest.xyz','User-Agent': self.USER_AGENT, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3','Connection': 'keep-alive','Cookie': '','Upgrade-Insecure-Requests': '1'}
		http_params = {'header':HTTP_HEADER, 'cookiefile':self.COOKIE_FILE, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True}

		urlTab = []
		URL=cItem['url']
		printDBG(' ----------> Link='+URL)	
		sts, data = self.getPage(URL,http_params)
		if sts:
			Liste_els0 = re.findall('<table(.*?)</table>', data, re.S)
			if Liste_els0:
				printDBG('data='+Liste_els0[-1])
				Liste_els1 = re.findall('<tr>(.*?)<td class.*?url="(.*?)"', data, re.S)
				for (titre,url) in Liste_els1:
					urlTab.append({'name':ph.clean_html(titre), 'url':'hst#tshost#'+url, 'need_resolve':1})
				
				
				
				
				
				
				#Liste_els = re.findall('<iframe.*?src="(.*?)"', data, re.S)
				#if Liste_els:
					#printDBG(' ----------> URL='+Liste_els[0])
					#url_verify = self.get_verify_url(Liste_els[0])	
					#printDBG(' ----------> URL_verify='+url_verify)	
					
					
					
					
				'''	
					
					data = self.cm.getCookieItems(self.COOKIE_FILE)
					printDBG('dat1111a22='+str(data))
					sts, data = self.getPage(Liste_els1[0])
					printDBG('dat1111a222='+data)
					sts, data = self.getPage(Liste_els1[0])
					printDBG('dat1111a2223='+data)
					data = self.cm.getCookieItems(self.COOKIE_FILE)
					printDBG('dat1111a22='+str(data))
					urlTab.append({'name':'2', 'url':'rr', 'need_resolve':0}) 
					
					
					
					
				
				Liste_els1 = re.findall('<tr>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?<td>(.*?)</td>.*?data-url.*?"(.*?)"', Liste_els0[-1], re.S)
				for (x1,type_,x3,src_) in Liste_els1:
					sts, data = self.getPage('https://egy.best'+src_)#,{'header':HTTP_HEADER})	
					if sts:	
						printDBG('dat1111a='+data)
						Liste_els0 = re.findall('assets/style.css.*?javascript">(.*?)</script>', data, re.S)
						jscode = Liste_els0[0]
						jscode = part1 + '\n' + jscode + '\n' + part2
						ret = js_execute( jscode )
						#if ret['sts'] and 0 == ret['code']:
						'''
						
						
						
						

					
					
					
					
					
					
				'''
				printDBG('login url='+Liste_els0[-1])
				stsx, datax = self.getPage(Liste_els0[-1])			
				Liste_els = re.findall('<video.*?type="(.*?)".*?src="(.*?)"', data1, re.S)
				for(type_,src_) in Liste_els:
					sts, data = self.getPage('https://egy.best'+src_)#,{'header':HTTP_HEADER})	
					if sts:	
						Link = re.findall('#EXT-X-STREAM.*?RESOLUTION=(.*?),.*?(htt.*?m3u8)', data, re.S)
						for (_res,_url) in Link:
							urlTab.append({'name':_res, 'url':_url, 'need_resolve':0})
				if self.loggedIn == True:
					Liste_els = re.findall('<tbody>(.*?)</div>', data1, re.S)
					if Liste_els:					
						Liste_els1 = re.findall('<tr>.*?<td>(.*?)<.*?<td>(.*?)<.*?<td>(.*?)<.*?call="(.*?)"', Liste_els[0], re.S)
						for(qual1,qual2,qual3,call_) in Liste_els1:			
							name=qual1+' '+qual2+' ('+qual3+')'
							urlTab.append({'name':name, 'url':'hst#tshost#'+call_+'|'+'ttttt'+'|'+URL, 'need_resolve':1})
'''
		return urlTab

		 
	def getVideos(self,videoUrl):
		urlTab = []	
		videoUrl=self.MAIN_URL+videoUrl
		printDBG(' -----------> URL = '+videoUrl)
		
		
		HTTP_HEADER =  {'Host':'wilo.egybest.xyz','User-Agent': self.USER_AGENT, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3','Connection': 'keep-alive','Upgrade-Insecure-Requests': '1','Pragma': 'no-cache','Cache-Control': 'no-cache'}
		http_params = {'header':HTTP_HEADER,'with_metadata':True,'no_redirection':True, 'cookiefile':self.COOKIE_FILE, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True}
		
		
	
		
		sts, data = self.getPage(videoUrl,http_params)
		if sts:
			printDBG('daaaaaaaaattttttttttttaaaaaaaaameta'+str(data.meta))
			URL = data.meta['location']
			printDBG('------------> Location:'+URL)
			HTTP_HEADER1 =  {'Host':'vidstream.to','User-Agent': self.USER_AGENT, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','Accept-Language': 'fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3','Connection': 'keep-alive','Upgrade-Insecure-Requests': '1','Pragma': 'no-cache','Cache-Control': 'no-cache'}
			http_params1 = {'header':HTTP_HEADER1,'with_metadata':True,'no_redirection':True, 'cookiefile':self.COOKIE_FILE, 'use_cookie': True, 'load_cookie': True, 'save_cookie': True}
			url_verify = self.get_verify_url(URL)	
 





		return urlTab	 							
		
	def getArticle(self, cItem):
		printDBG("EgyBest.getArticleContent [%s]" % cItem)
		desc = ''
		retTab = []
		otherInfo = {}
		sts, data = self.getPage(cItem['url'])
		if sts:
			desc = ph.clean_html(self.cm.ph.getDataBeetwenNodes(data, ('<strong', '</div>', 'القصة'), ('</div', '>'), False)[1])
			tmp  = self.cm.ph.getDataBeetwenNodes(data, ('<div', '>', 'full_movie'), ('</table', '>'), False)[1]
			icon  = self.cm.ph.getDataBeetwenNodes(tmp, ('<div', '>', 'movie_img'), ('</div', '>'), False)[1]
			icon  = self.getFullIconUrl(self.cm.ph.getSearchGroups(icon, '''src=['"]([^'^"]+?)['"]''')[0])
			title = ph.clean_html(self.cm.ph.getDataBeetwenNodes(tmp, ('<div', '>', 'movie_title'), ('</div', '>'), False)[1])

			keysMap = {'اللغة • البلد'            :'country',
					   'التصنيف'                  :'type',
					   'النوع'                    :'genres', 
					   'التقييم العالمي'          :'rating',
					   'المدة'                    :'duration',
					   'الجودة'                   :'quality',
					   'الترجمة'                  :'translation'}

			tmp = self.cm.ph.getAllItemsBeetwenMarkers(tmp, '<tr>', '</tr>')
			for item in tmp:
				item = item.split('</td>', 1)
				if len(item) != 2: continue
				keyMarker = ph.clean_html(item[0]).replace(':', '').strip()
				printDBG("+++ keyMarker[%s]" % keyMarker)
				value = ph.clean_html(item[1]).replace(' , ', ', ')
				key = keysMap.get(keyMarker, '')
				if key != '' and value != '': otherInfo[key] = value

			# actors
			tTab = []
			tmp = self.cm.ph.getAllItemsBeetwenNodes(data, ('<div', '>', 'cast_item'), ('</span', '>'))
			for t in tmp:
				t = ph.clean_html(t)
				if t != '': tTab.append(t)
			if len(tTab): otherInfo['actors'] = ', '.join(tTab)

		title = cItem['title']
		if desc == '':  desc = cItem.get('desc', '')
		cItem.get('icon', '')

		return [{'title':ph.clean_html( title ), 'text': ph.clean_html( desc ), 'images':[{'title':'', 'url':self.getFullUrl(icon)}], 'other_info':otherInfo}]

	
	def start(self,cItem):      
		mode=cItem.get('mode', None)
		if mode=='00':
			self.showmenu0(cItem)
		if mode=='20':
			self.showmenu1(cItem)
		if mode=='21':
			self.showmenu2(cItem)
		if mode=='30':
			self.showitms(cItem)			
		if mode=='31':
			self.showelems(cItem)
