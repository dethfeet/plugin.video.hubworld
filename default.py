import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
import urllib, urllib2
import re
import brightcovePlayer

addon = xbmcaddon.Addon(id='plugin.video.hubworld')

thisPlugin = int(sys.argv[1])

baseLink = "http://www.hubworld.com/"


extractSection = re.compile("<section class=\".*?video-box\">.*?<div class=\"fb-top\">.*?<h2>(.*?)</h2>(.*?)<div class=\"fb-bottom\">",re.DOTALL)

def mainPage():
    global thisPlugin
    
    addDirectoryItem("Videos", {"action":"showVideos","link":baseLink+"videos"}, "")
    addDirectoryItem("Shows", {"action":"showShows","link":baseLink+"shows"}, "")
     
    xbmcplugin.endOfDirectory(thisPlugin)
    
def showVideos(link):
    link = urllib.unquote(link)
    page = load_page(link)
    extractShowMoreButton = re.compile("<a href=\"(.*?)\" class=\"lite-button\">")
    extractSections = extractSection.findall(page)
    if len(extractSections) == 1:
        showVideosSection(link,extractSections[0][0])
        return False
    else:
        for section in extractSections:
            sectionLink = link
            sectionTitle = section[0]
            sectionHtml = section[1]
            showMoreButton = extractShowMoreButton.search(sectionHtml)
            sectionLinkSection = sectionTitle
            if showMoreButton is not None:
                sectionLink = baseLink+showMoreButton.group(1)
                sectionLinkSection = ""
            addDirectoryItem(sectionTitle, {"action":"showVideosSection","link":sectionLink,"section":sectionLinkSection}, "")
    
    xbmcplugin.endOfDirectory(thisPlugin)
    
def showVideosSection(link,section):
	link = urllib.unquote(link)
	showSection = urllib.unquote_plus(section)
	
	page = load_page(link)
	
	extractVideo = re.compile("<section class=\".*?\">.*?<img src=\"(.*?)\".*?<a href=\"(.*?)\" class=\"title\">(.*?)</a>.*?<p>(.*?)</p>.*?</section>",re.DOTALL)

	sectionHtml = "";
	
	if showSection != "":
		#extract section from baseLink
		#print link
		#print showSection
		extractSections = extractSection.finditer(page)
		for section in extractSections:
			sectionTitle = section.group(1)
			if sectionTitle == showSection:
				sectionHtml = section.group(2)
	else:
		#extract videos from Page
		#print link
		sectionHtml = page
	
	for video in extractVideo.finditer(sectionHtml):
		videoTitle = video.group(3) + " (" + video.group(4).strip() + ")"
		videoImg = baseLink+video.group(1)
		videoLink = baseLink+video.group(2)
		addDirectoryItem(videoTitle, {"action":"playVideo","link":videoLink}, videoImg, False)

	xbmcplugin.endOfDirectory(thisPlugin)

def showShows(link):
	page = load_page(urllib.unquote(link))
	
	extractShow = re.compile("<section class=\".*?content-item-vertical.*?\">.*?<div class=\"thumbimg\">.*?src=\"(.*?)\".*?href=\"(.*?)\".*?>(.*?)</a>",re.DOTALL)
	
	for show in extractShow.finditer(page):
		showImg = baseLink+show.group(1)
		showLink = baseLink+show.group(2)+"/videos"
		showTitle = show.group(3)
		
		showPage = urllib.urlopen(showLink)
		if showLink == showPage.geturl():
			if extractSection.search(showPage.read()) is not None:
				addDirectoryItem(showTitle, {"action":"showVideos","link":showLink}, showImg)
	xbmcplugin.endOfDirectory(thisPlugin)

def showShowsShow(link):
	page = load_page(urllib.unquote(link))

def playVideo(link):
    page = load_page(urllib.unquote(link))
    videoPlayer = re.compile("brightcove_mediaId: ([0-9]*),").search(page).group(1)
    stream = brightcovePlayer.play(videoPlayer)
    
    rtmpbase = stream[1][0:stream[1].find("&")]
    playpath = stream[1][stream[1].find("&") + 1:]
    finalurl = rtmpbase + ' playpath=' + playpath
    
    item = xbmcgui.ListItem(stream[0], path=finalurl)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)

def load_page(url):
    print url
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def addDirectoryItem(name, parameters={}, pic="", folder=True):
    li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=pic)
    if not folder:
        li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=folder)
   
def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    
    return param
    
if not sys.argv[2]:
    mainPage()
else:
    params = get_params()
    if params['action'] == "showVideos":
        showVideos(params['link'])
    if params['action'] == "showVideosSection":
        showVideosSection(params['link'],params['section'])
    if params['action'] == "showShows":
        showShows(params['link'])
    if params['action'] == "showShowsShow":
        showShowsShow(params['link'])
    if params['action'] == "playVideo":
        playVideo(params['link'])
    else:
        mainPage()
