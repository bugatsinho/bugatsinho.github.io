# -*- coding: utf-8 -*-
import re
import sys
import six
import requests
from kodi_six import xbmcaddon, xbmcgui, xbmcplugin, xbmc
from six.moves.urllib.parse import urljoin, unquote_plus, quote_plus, quote, unquote
from six.moves import zip
from resources.modules import control, client, dom_parser as dom

ADDON = xbmcaddon.Addon()
ADDON_DATA = ADDON.getAddonInfo('profile')
ADDON_PATH = ADDON.getAddonInfo('path')
DESCRIPTION = ADDON.getAddonInfo('description')
FANART = ADDON.getAddonInfo('fanart')
ICON = ADDON.getAddonInfo('icon')
ID = ADDON.getAddonInfo('id')
NAME = ADDON.getAddonInfo('name')
VERSION = ADDON.getAddonInfo('version')
Lang = ADDON.getLocalizedString
Dialog = xbmcgui.Dialog()
vers = VERSION
ART = ADDON_PATH + "/resources/icons/"

BASEURL = 'https://www.skylinewebcams.com/{0}/webcam.html'
base_url = 'https://www.skylinewebcams.com'
new_url = 'https://www.skylinewebcams.com/{0}/new-livecams.html'

headers = {'User-Agent': 'iPad',
		   'Referer': BASEURL}


# reload(sys)
# sys.setdefaultencoding("utf-8")

def get_lang():
	lang = ADDON.getSetting('lang').encode('utf-8') if six.PY2 else ADDON.getSetting('lang')
	lang_dict = {'English': 'en',
				 'Greek': 'el',
				 'Español': 'es',
				 'Français': 'fr',
				 'Deutsch': 'de',
				 'Italiano': 'it',
				 'Polish': 'pl',
				 'Hrvatski': 'hr',
				 'Slovenski': 'sl'}

	return lang_dict[lang]


web_lang = get_lang()


def Main_menu():
	addDir('[B][COLOR white]Top Live Cams[/COLOR][/B]',
		   'https://www.skylinewebcams.com/{0}/top-live-cams.html'.format(web_lang), 5, ICON, FANART, '')
	addDir('[B][COLOR white]New Live Cams[/COLOR][/B]', new_url.format(web_lang), 5, ICON, FANART, '')
	addDir('[B][COLOR white]Live Cams by Country[/COLOR][/B]', BASEURL.format(web_lang), 4, ICON, FANART, '')
	addDir('[B][COLOR white]Live Cams by Category[/COLOR][/B]', BASEURL.format(web_lang), 9, ICON, FANART, '')
	addDir('[B][COLOR white]Random Live Cam[/COLOR][/B]', base_url, 3, ICON, FANART, '')
	addDir('[B][COLOR white]Greek Live Cams[/COLOR][/B]', BASEURL.format(web_lang), 8, ICON, FANART, '')
	addDir('[B][COLOR cyan]Settings[/COLOR][/B]', '', 7, ICON, FANART, '')
	addDir('[B][COLOR gold]Version: [COLOR lime]%s[/COLOR][/B]' % vers, '', 'BUG', ICON, FANART, '')
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_cat_cams():
	try:
		html = six.ensure_str(getContent(base_url))
		data = client.parseDOM(html, 'li', attrs={'class': 'dropdown mega-dropdown'})[0]
		cats = client.parseDOM(data, 'div', attrs={'class': 'container-fluid'})[0]
		cats = dom.parse_dom(cats, 'a', req='href')
		for cat in cats:
			name = client.parseDOM(cat.content, 'p', attrs={'class': 'tcam'})[0]
			if six.PY2:
				name = name.encode('utf-8')
			name = '[B][COLOR white]{}[/COLOR][/B]'.format(name)
			icon = client.parseDOM(cat.content, 'img', ret='data-src')[0]
			icon = 'https:{}'.format(icon) if icon.startswith('//') else icon
			icon = icon + '|Referer={}'.format(base_url)
			url = cat.attrs['href'][3:]
			url = '{2}/{0}/{1}'.format(web_lang, url, base_url)
			addDir(name, url, 5, icon, FANART, '')
	except BaseException:
		pass
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')

	# addDir('[B][COLOR white]Beaches[/COLOR][/B]',
	#        'https://www.skylinewebcams.com/{0}/live-cams-category/beach-cams.html'.format(web_lang), 5, ICON, FANART, '')
	# addDir('[B][COLOR white]CITY Views[/COLOR][/B]',
	#        'https://www.skylinewebcams.com/{0}/live-cams-category/city-cams.html'.format(web_lang), 5, ICON, FANART, '')
	# addDir('[B][COLOR white]Landscapes[/COLOR][/B]',
	#        'https://www.skylinewebcams.com/{0}/live-cams-category/nature-mountain-cams.html'.format(web_lang), 5, ICON,
	#        FANART, '')
	# addDir('[B][COLOR white]Landscapes[/COLOR][/B]',
	#        'https://www.skylinewebcams.com/{0}/live-cams-category/nature-mountain-cams.html'.format(web_lang), 5, ICON, FANART, '')


def get_greek_cams():
	link = 'http://www.livecameras.gr/'
	headers = {"User-Agent": client.agent()}
	r = six.ensure_text(client.request(link, headers))
	cams = client.parseDOM(r, 'div', attrs={'class': 'fp-playlist'})[0]
	cams = zip(client.parseDOM(cams, 'a', ret='href'),
			   client.parseDOM(cams, 'a', ret='data-title'),
			   client.parseDOM(cams, 'img', ret='src'))
	for stream, name, poster in cams:
		name = re.sub(r'".+?false', '', name)
		name = client.replaceHTMLCodes(name)
		stream = 'http:' + stream if stream.startswith('//') else stream
		stream += '|Referer={}'.format(link)
		poster = link + poster if poster.startswith('/') else poster
		addDir('[B][COLOR white]%s[/COLOR][/B]' % name, stream, 100, poster, '', 'name')


def get_the_random(url):  # 3
	#r = six.ensure_str(client.request(url, headers=headers))
	r = getContent(url)
	frame = client.parseDOM(r, 'div', attrs={'class': 'row home'})[0]
	frame = client.parseDOM(frame, 'div', attrs={'class': 'row'})[0]
	cams = [i for i in client.parseDOM(frame, 'a', ret=True) if 'tcam' in i]
	for cam in cams:
		head = client.parseDOM(cam, 'p', attrs={'class': 'tcam'})[0]
		head = clear_Title(head)
		desc = client.parseDOM(cam, 'p', attrs={'class': 'subt'})[0]
		frame = client.parseDOM(cam, 'a', ret='href')[0]
		frame = base_url + frame if frame.startswith('/') else frame
		# xbmc.log('FRAME:%s' % frame)
		if six.PY2:
			head = head.encode('utf-8')
			desc = desc.encode('utf-8')
		head = '[B][COLOR white]{0}[/COLOR][/B]'.format(head)
		addDir(head, frame, 100, ICON, '', description=desc)
		xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_country(url):  # 4
	r = six.ensure_str(getContent(url))
	r = client.parseDOM(r, 'div', attrs={'class': 'dropdown mega-dropdown live'})[0]
	r = zip(client.parseDOM(r, 'a'),
			client.parseDOM(r, 'a', ret='href'))
	for name, link in r:
		name = re.sub('<.+?>', '', name).replace('&nbsp;', ' ')
		name = client.replaceHTMLCodes(name)
		name = '[B][COLOR white]{}[/COLOR][/B]'.format(name)
		link = client.replaceHTMLCodes(link)
		if six.PY2:
			name = name.encode('utf-8')
			link = link.encode('utf-8')
		link = base_url + link if link.startswith('/') else link
		addDir(name, link, 5, ICON, FANART, '')
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_new(url):
	r = six.ensure_str(getContent(url))
	r = client.parseDOM(r, 'div', attrs={'class': 'row'})[0]
	r = zip(client.parseDOM(r, 'a', ret='href'),
			client.parseDOM(r, 'img', ret='src'),
			client.parseDOM(r, 'img', ret='alt'))
	for link, poster, name in r:
		name = client.replaceHTMLCodes(name)

		link = client.replaceHTMLCodes(link)
		link = 'https:' + link if link.startswith('//') else link

		poster = client.replaceHTMLCodes(poster)
		poster = 'https:' + poster if poster.startswith('//') else poster
		if six.PY2:
			poster = poster.encode('utf-8')
			name = name.encode('utf-8')
			link = link.encode('utf-8')

		addDir('[B][COLOR white]%s[/COLOR][/B]' % name, link, 100, poster, FANART, '')
	xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def get_content(url):  # 5 <div id="content"><div class="container">
	r = six.ensure_str(getContent(url))
	data = client.parseDOM(r, 'div', attrs={'class': 'container'})[0]
	data = dom.parse_dom(data, 'a', req='href')
	data = [i for i in data if 'subt' in i.content]
	# xbmc.log('DATA22: {}'.format(str(r)))
	for item in data:
		link = item.attrs['href']
		if link == '#':
			continue
		link = client.replaceHTMLCodes(link)

		name = client.parseDOM(item.content, 'img', ret='alt')[0]
		name = client.replaceHTMLCodes(name)

		desc = client.parseDOM(item.content, 'p', attrs={'class': 'subt'})[0]
		desc = clear_Title(desc)

		try:
			poster = client.parseDOM(item.content, 'img', ret='data-src')[0]
		except IndexError:
			poster = client.parseDOM(item.content, 'img', ret='src')[0]
		poster = client.replaceHTMLCodes(poster)
		poster = 'https:' + poster if poster.startswith('//') else poster

		if six.PY2:
			link = link.encode('utf-8')
			name = name.encode('utf-8')
			desc = desc.decode('ascii', errors='ignore')
			poster = poster.encode('utf-8')
		link = '{}/{}'.format(base_url, link) if not link.startswith('http') else link
		addDir('[B][COLOR white]%s[/COLOR][/B]' % name, link, 100, poster, '', desc)

	xbmcplugin.setContent(int(sys.argv[1]), 'movies')


def clear_Title(txt):
	txt = re.sub('<.+?>', '', txt)
	txt = txt.replace("&quot;", "\"").replace('()', '').replace("&#038;", "&").replace('&#8211;', ':')
	txt = txt.replace("&amp;", "&").replace('&#8217;', "'").replace('&#039;', ':').replace('&#;', '\'')
	txt = txt.replace("&#38;", "&").replace('&#8221;', '"').replace('&#8216;', '"').replace('&#160;', '')
	txt = txt.replace("&nbsp;", "").replace('&#8220;', '"').replace('\t', ' ').replace('\n', ' ')
	return txt


def Open_settings():
	control.openSettings()


def getRandom():
	import random
	WEBBROWSER = [['%s.0' % i for i in range(18, 50)], ['37.0.2062.103', '37.0.2062.120', '37.0.2062.124', '38.0.2125.101','38.0.2125.104',
		'38.0.2125.111', '39.0.2171.71', '39.0.2171.95', '39.0.2171.99', '40.0.2214.93', '40.0.2214.111', '40.0.2214.115', '39.0.2171.99',
		'40.0.2214.93', '40.0.2214.111', '40.0.2214.115', '42.0.2311.90', '42.0.2311.135', '42.0.2311.152', '43.0.2357.81', '43.0.2357.124',
		'44.0.2403.155', '44.0.2403.157', '45.0.2454.101', '45.0.2454.85', '46.0.2490.71', '46.0.2490.80', '46.0.2490.86', '47.0.2526.73',
		'47.0.2526.80', '49.0.2623.112', '50.0.2661.86'], ['11.0'], ['8.0', '9.0', '10.0', '10.6']]
	WINDOWS = ['Windows NT 10.0', 'Windows NT 7.0', 'Windows NT 6.3', 'Windows NT 6.2', 'Windows NT 6.1', 'Windows NT 6.0',
		'Windows NT 5.1', 'Windows NT 5.0']
	FEATURES = ['; WOW64', '; Win64; IA64', '; Win64; x64', '']
	RANDOM_AGENT = ['Mozilla/5.0 ({windows}{features}; rv:{browser}) Gecko/20100101 Firefox/{browser}',
		'Mozilla/5.0 ({windows}{features}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{browser} Safari/537.36',
		'Mozilla/5.0 ({windows}{features}; Trident/7.0; rv:{browser}) like Gecko']
	index = random.randrange(len(RANDOM_AGENT))
	releases = {'windows': random.choice(WINDOWS), 'features': random.choice(FEATURES), 'browser': random.choice(WEBBROWSER[index])}
	new_agent = RANDOM_AGENT[index].format(**releases)
	return new_agent

def _header(ORIGIN=None, REFERRER=None):
	header = {} # !!! Accept-Language only set if browser should offer these languages !!!
	header['Cache-Control'] = 'public, max-age=300'
	header['Accept'] = 'application/json, application/x-www-form-urlencoded, text/plain, */*'
	header['documentLifecycle'] = 'active'
	header['User-Agent'] = getRandom()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	if ORIGIN: header['Origin'] = ORIGIN
	if REFERRER: header['Referer'] = REFERRER
	return header

def getContent(url, method='GET', queries='TEXT', ORG=base_url, REF=BASEURL, headers={}, redirects=True, verify=True, data=None, json=None, timeout=30):
	ANSWER = None
	try:
		response = requests.request(method, url, headers=_header(ORG, REF), allow_redirects=redirects, verify=verify, timeout=timeout)
		ANSWER = response.json() if queries == 'JSON' else response.text if queries == 'TEXT' else response
	except requests.exceptions.RequestException as exc:
		return sys.exit(0)
	return ANSWER

def resolve(name, url, iconimage, description):
	# xbmc.log('URLLLL: {}'.format(url))
	if 'm3u8' in url:
		link = url
		link += '|User-Agent={}&Referer={}'.format('iPad', quote_plus(headers['Referer']))
		liz = xbmcgui.ListItem(name, iconImage=ICON, thumbnailImage=iconimage)
	else:
		url = base_url + url if url.startswith('/') else url
		# xbmc.log('URLLLL2: {}'.format(url))
		# cj = client.request(base_url, headers=headers, output='cookie')
		# xbmc.log('COOKIES: {}'.format(str(cj)))
		# headers['Cookie'] = cj
		info = getContent(url)
		info = six.ensure_str(info, encoding='utf-8')
		head = client.parseDOM(info, 'title')[0]
		onviewers = client.parseDOM(info, "span", attrs={"id": "v_now"})[0]
		local_time = client.parseDOM(info, "span", attrs={"id": "servertime"})[0]
		title = client.parseDOM(info, 'h1')[0]
		title = '{0} - Local Time: [COLOR gold]{1}[/COLOR]'.format(title, local_time)
		descr = client.parseDOM(info, "div", attrs={"class": "descr"})[0]
		Plot = ('Title: {0}\n'
				'Online Viewers: [COLOR lime]{1}[/COLOR]\n'
				'Local Time: [COLOR gold]{2}[/COLOR]\n'
				'Description: {3}').format(head, onviewers, local_time, clear_Title(descr))

		poster = client.parseDOM(info, 'meta', ret='content', attrs={'property': 'og:image'})[0]
		if 'videoId:' in info:
			youtube_id = re.findall('''videoId\s*:\s*['"]([a-zA-Z0-9_-]+)['"]''', info, re.DOTALL )[0]
			link = 'plugin://plugin.video.youtube/play/?video_id={}'.format(youtube_id)
		else:
			link = re.findall(r'''source:['"](.+?)['"]\,''', info, re.DOTALL)[0]
			link = "https://hd-auth.skylinewebcams.com/" + link.replace('livee', 'live') if link.startswith(
				'live') else link
			# xbmc.log('LINK: {}'.format(link))
			link += '|User-Agent=iPad&Referer={}'.format(BASEURL)
		if six.PY2:
			head = head.encode('utf-8')
			link = str(link)
		liz = xbmcgui.ListItem(head)
		liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': poster, 'fanart': fanart})

	try:
		liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": Plot})
		liz.setProperty("IsPlayable", "true")
		liz.setPath(link)
		# control.player.play(link, liz)
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
	except:
		control.infoDialog("[COLOR red]Dead Link[/COLOR]!\n[COLOR white]Please Try Another[/COLOR]", NAME, '')


def addDir(name, url, mode, iconimage, fanart, description):
	u = sys.argv[0] + "?url=" + quote_plus(url) + "&mode=" + str(mode) + "&name=" + quote_plus(
		name) + "&iconimage=" + quote_plus(iconimage) + "&description=" + quote_plus(description)
	ok = True
	liz = xbmcgui.ListItem(name)
	liz.setArt({'icon': iconimage, 'thumb': iconimage, 'poster': iconimage, 'fanart': fanart})
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
	liz.setProperty('fanart_image', fanart)
	if mode == 100 or mode == 'BUG' or mode == 7:
		liz.setProperty("IsPlayable", "true")
		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
	elif mode == 7:
		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
	else:
		ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok


def get_params():
	param = []
	paramstring = sys.argv[2]
	if len(paramstring) >= 2:
		params = sys.argv[2]
		cleanedparams = params.replace('?', '')
		if (params[len(params) - 1] == '/'): params = params[0:len(params) - 2]
		pairsofparams = cleanedparams.split('&')
		param = {}
		for i in range(len(pairsofparams)):
			splitparams = {}
			splitparams = pairsofparams[i].split('=')
			if (len(splitparams)) == 2: param[splitparams[0]] = splitparams[1]
	return param


params = get_params()
url = BASEURL
name = NAME
iconimage = ICON
mode = None
fanart = FANART
description = DESCRIPTION
query = None

try:
	url = unquote_plus(params["url"])
except:
	pass
try:
	name = unquote_plus(params["name"])
except:
	pass
try:
	iconimage = unquote_plus(params["iconimage"])
except:
	pass
try:
	mode = int(params["mode"])
except:
	pass
try:
	fanart = unquote_plus(params["fanart"])
except:
	pass
try:
	description = unquote_plus(params["description"])
except:
	pass
try:
	query = unquote_plus(params["query"])
except:
	pass

print(str(NAME) + ': ' + str(VERSION))
print("Mode: " + str(mode))
print("URL: " + str(url))
print("Name: " + str(name))
print("IconImage: " + str(iconimage))
#########################################################

if mode is None:
	Main_menu()
elif mode == 3:
	get_the_random(url)
elif mode == 4:
	get_country(url)
elif mode == 5:
	get_content(url)
elif mode == 6:
	get_new(url)
elif mode == 7:
	Open_settings()
elif mode == 8:
	get_greek_cams()
elif mode == 9:
	get_cat_cams()
elif mode == 100:
	resolve(name, url, iconimage, description)
xbmcplugin.endOfDirectory(int(sys.argv[1]))
