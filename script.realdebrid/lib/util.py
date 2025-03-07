import urllib, ssl, sys
import xbmc, xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs

try:  # Python 3
    import urllib.parse
    import urllib.request
    from urllib.parse import unquote
    from urllib.parse import unquote_plus
    from urllib.parse import quote_plus
    from urllib.request import urlopen
    from urllib.request import Request
    from urllib.parse import urlencode
    p2 = False
except ImportError:
    import cookielib
    from urllib2 import urlopen
    from urllib import unquote
    from urllib import unquote_plus
    from urllib import quote_plus
    from urllib2 import Request
    from urllib import urlencode
    p2 = True

sysarg=str(sys.argv[1])

try:
    addon = xbmcaddon.Addon()
except:
    addon=''

headers = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3',
           'Accept': '*/*',
           'Connection': 'keep-alive'}

def parseParameters(inputString=sys.argv[2]):
    """Parses a parameter string starting at the first ? found in inputString

    Argument:
    inputString: the string to be parsed, sys.argv[2] by default

    Returns a dictionary with parameter names as keys and parameter values as values
    """

    parameters = {}
    p1 = inputString.find('?')
    if p1 >= 0:
        splitParameters = inputString[p1 + 1:].split('&')
        for nameValuePair in splitParameters:
            try:
                if (len(nameValuePair) > 0):
                    pair = nameValuePair.split('=')
                    key = pair[0]
                    value = unquote(unquote_plus(pair[1]))
                    if p2:
                        value = value.decode('utf-8')
                    parameters[key] = value
            except:
                pass
    return parameters

def extractAll(text, startText, endText):
    result = []
    start = 0
    pos = text.find(startText, start)
    while pos != -1:
        start = pos + startText.__len__()
        end = text.find(endText, start)
        result.append(text[start:end].replace('\n', '').replace('\t', '').lstrip())
        pos = text.find(startText, end)
    return result

def extract(text, startText, endText):
    start = text.find(startText, 0)
    if start != -1:
        start = start + startText.__len__()
        end = text.find(endText, start + 1)
        if end != -1:
            return text[start:end]
    return None

def getURL(url, header=headers, error=True):
    response=""
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        req = Request(url, headers=header)

        response = urlopen(req, context=ctx)
    except:
        try:
            req = Request(url, headers=header)

            response = urlopen(req, timeout=int(xbmcaddon.Addon().getSetting("timeout")))
        except:
           pass

    if response and response.getcode() == 200:
        if response.info().get('Content-Encoding') == 'gzip':
            buf = StringIO.StringIO( response.read())
            gzip_f = gzip.GzipFile(fileobj=buf)
            content = gzip_f.read()
        else:
            content = response.read()
        content = content.decode('utf-8', 'ignore')
        return content
    else:
        if error:
            try:
                xbmc.log('Error Loading URL : '+str(response.getcode()), xbmc.LOGERROR)
            except:
                print('Error Loading URL : '+url)
    return False

def logError(error):
    try:
        xbmc.log(str(error.encode("utf-8")), xbmc.LOGERROR)
    except:
        print(str(error))

def alert(alertText):
    try:
        dialog = xbmcgui.Dialog()
        ret = dialog.ok("RealDebrid", alertText)
    except:
        print(alertText)

def notify(message, reportError=False, timeShown=5000):
    """Displays a notification to the user

    Parameters:
    addonId: the current addon id
    message: the message to be shown
    timeShown: the length of time for which the notification will be shown, in milliseconds, 5 seconds by default
    """
    global addon
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (addon.getAddonInfo('name'), message, timeShown, addon.getAddonInfo('icon')))
    if reportError:
        logError(message)

def progressStart(title, status):
    pDialog = xbmcgui.DialogProgress()
    pDialog.create(title, status)
    xbmc.executebuiltin( "Dialog.Close(busydialognocancel)" )
    progressUpdate(pDialog, 1, status)
    return pDialog

def progressStop(pDialog):
    pDialog.close

def progressCancelled(pDialog):
    if pDialog.iscanceled():
        pDialog.close
        return True
    return False

def progressUpdate(pDialog, progress, status):
    pDialog.update(int(progress), status)

def searchDialog(searchText="Please enter search text") :
    keyb=xbmc.Keyboard('', searchText)
    keyb.doModal()
    searchText=''

    if (keyb.isConfirmed()) :
        searchText = keyb.getText()
    if searchText!='':
        return searchText
    return False

def playMedia(title, thumbnail, link, mediaType='Video', library=True, title2="", force=False) :
    if p2:
        li = xbmcgui.ListItem(label=title2, iconImage=thumbnail, thumbnailImage=thumbnail, path=link)
    else:
        li = xbmcgui.ListItem(label=title2, path=link)
        li.setArt({'icon':thumbnail})
        li.setArt({'thumbnailImage': thumbnail})
    li.setInfo( "video", { "Title" : title } )

    if not force:
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, li)
    else:
        xbmc.Player().play(item=link, listitem=li)

def addMenuItems(details):
    changed=False
    for detail in details:
        try:
            u=sys.argv[0]+"?url="+detail['url']+"&mode="+str(detail['mode'])+"&name="+quote_plus(detail['title'].encode("utf-8"))+"&icon="+detail['icon']
            if p2:
                liz=xbmcgui.ListItem(detail['title'].encode("utf-8"), iconImage=detail['icon'], thumbnailImage=detail['icon'])
            else:
                liz=xbmcgui.ListItem(detail['title'].encode("utf-8"))
                liz.setArt({'icon':detail['icon']})
                liz.setArt({'thumbnailImage': detail['icon']})
            liz.setInfo(type=detail['type'], infoLabels={ "Title": detail['title'].encode("utf-8"),"Plot": detail['plot']} )
        except:
            u=sys.argv[0]+"?url="+detail['url']+"&mode="+str(detail['mode'])+"&name="+quote_plus(detail['title'].decode("utf-8"))+"&icon="+detail['icon']
            if p2:
                liz=xbmcgui.ListItem(detail['title'].encode("utf-8"), iconImage=detail['icon'], thumbnailImage=detail['icon'])
            else:
                liz=xbmcgui.ListItem(detail['title'].encode("utf-8"))
                liz.setArt({'icon':detail['icon']})
                liz.setArt({'thumbnailImage': detail['icon']})
            liz.setInfo(type=detail['type'], infoLabels={ "Title": detail['title'].decode("utf-8"),"Plot": detail['plot']} )

        try:
            liz.setProperty("Fanart_Image", detail['fanart'])
            u=u+"&fanart="+detail['fanart']
        except:
            pass
        try:
            liz.setProperty("Landscape_Image", detail['landscape'])
            u=u+"&landscape="+detail['landscape']
        except:
            pass
        try:
            liz.setProperty("Poster_Image", detail['poster'])
            u=u+"&poster="+detail['poster']
        except:
            pass
        try:
            u=u+"&extras="+str(detail["extras"])
        except:
            pass

        if 'isPlayable' in detail:
            liz.setProperty('IsPlayable', 'true')

        if "method" in detail:
            download = (sys.argv[0] +
                "?url=" + detail['url'] +
                "&mode=" + str(12) +
                "&method="+detail['method']+
                "&id="+str(detail['id'])+
                "&poster="+detail['poster']+
                "&fanart="+detail['fanart']+
                "&name=" + quote_plus(detail['title'].encode("utf-8"))
            )
            delete = (sys.argv[0] +
                "?url=" + detail['id'] +
                "&method="+detail['method']+
                "&id="+str(detail['id'])+
                "&mode=" + str(13) +
                "&poster="+detail['poster']+
                "&fanart="+detail['fanart']+
                "&name=" + quote_plus(detail['title'].encode("utf-8"))
            )

            liz.addContextMenuItems([('Download', 'RunPlugin('+download+')'), ('Delete', 'RunPlugin('+delete+')')])

        if detail['isFolder']:
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        else:
            ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False)
    xbmcplugin.endOfDirectory(int(sysarg))