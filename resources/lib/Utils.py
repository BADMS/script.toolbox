import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import xbmcplugin
import os
import simplejson
import hashlib
import urllib
import random
from PIL import Image, ImageOps, ImageEnhance
from ImageOperations import MyGaussianBlur
from xml.dom.minidom import parse

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_LANGUAGE = ADDON.getLocalizedString
ADDON_DATA_PATH = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID))
HOME = xbmcgui.Window(10000)


class TextViewer_Dialog(xbmcgui.WindowXMLDialog):
    ACTION_PREVIOUS_MENU = [9, 92, 10]

    def __init__(self, *args, **kwargs):
        xbmcgui.WindowXMLDialog.__init__(self)
        self.text = kwargs.get('text')
        self.header = kwargs.get('header')

    def onInit(self):
        self.getControl(1).setLabel(self.header)
        self.getControl(5).setText(self.text)

    def onAction(self, action):
        if action in self.ACTION_PREVIOUS_MENU:
            self.close()

    def onClick(self, controlID):
        pass

    def onFocus(self, controlID):
        pass


def RemoveQuotes(label):
    if label.startswith("'") and label.endswith("'") and len(label) > 2:
        label = label[1:-1]
        if label.startswith('"') and label.endswith('"') and len(label) > 2:
            label = label[1:-1]
    return label


def Filter_Image(filterimage, radius):
    if HOME.getProperty('colorbox_running') != 'True'
    	if not xbmcvfs.exists(ADDON_DATA_PATH):
    		xbmcvfs.mkdir(ADDON_DATA_PATH)
    	HOME.setProperty('colorbox_running', 'True')
    md5 = hashlib.md5(filterimage).hexdigest()
    filename = md5 + str(radius) + ".png"
    targetfile = os.path.join(ADDON_DATA_PATH, filename)
    cachedthumb = xbmc.getCacheThumbName(filterimage)
    xbmc_vid_cache_file = os.path.join("special://profile/Thumbnails/Video", cachedthumb[0], cachedthumb)
    xbmc_cache_file = os.path.join("special://profile/Thumbnails/", cachedthumb[0], cachedthumb[:-4] + ".jpg")
    if filterimage == "":
        return "", ""
    if not xbmcvfs.exists(targetfile):
        img = None
        for i in range(1, 4):
            try:
                if xbmcvfs.exists(xbmc_cache_file):
                    log("image already in xbmc cache: " + xbmc_cache_file)
                    img = Image.open(xbmc.translatePath(xbmc_cache_file))
                    break
                elif xbmcvfs.exists(xbmc_vid_cache_file):
                    log("image already in xbmc video cache: " + xbmc_vid_cache_file)
                    img = Image.open(xbmc.translatePath(xbmc_vid_cache_file))
                    break
                else:
                    filterimage = urllib.unquote(filterimage.replace("image://", "")).decode('utf8')
                    if filterimage.endswith("/"):
                        filterimage = filterimage[:-1]
                    log("copy image from source: " + filterimage)
                    xbmcvfs.copy(filterimage, targetfile)
                    img = Image.open(targetfile)
                    break
            except:
                log("Could not get image for %s (try %i)" % (filterimage, i))
                xbmc.sleep(500)
        if not img:
            return "", ""
        img.thumbnail((200, 200), Image.ANTIALIAS)
        img = img.convert('RGB')
        imgfilter = MyGaussianBlur(radius=radius)
        img = img.filter(imgfilter)
        img.save(targetfile)
    else:
        log("blurred img already created: " + targetfile)
        img = Image.open(targetfile)
    imagecolor = Get_Colors(img)
    return targetfile, imagecolor


def Filter_Pixelate(filterimage, pixels):
    if HOME.getProperty('colorbox_running') != 'True'
    	if not xbmcvfs.exists(ADDON_DATA_PATH):
    		xbmcvfs.mkdir(ADDON_DATA_PATH)
    	HOME.setProperty('colorbox_running', 'True')
    md5 = hashlib.md5(filterimage).hexdigest()
    filename = md5 + "pixel" + str(pixels) + ".png"
    targetfile = os.path.join(ADDON_DATA_PATH, filename)
    cachedthumb = xbmc.getCacheThumbName(filterimage)
    xbmc_vid_cache_file = os.path.join("special://profile/Thumbnails/Video", cachedthumb[0], cachedthumb)
    xbmc_cache_file = os.path.join("special://profile/Thumbnails/", cachedthumb[0], cachedthumb[:-4] + ".jpg")
    imagecolor = "ff" + "%06x" % random.randint(0, 0xFFFFFF)
    if filterimage == "":
        return "", imagecolor
    if not xbmcvfs.exists(targetfile):
        img = None
        for i in range(1, 4):
            try:
                if xbmcvfs.exists(xbmc_cache_file):
                    log("image already in xbmc cache: " + xbmc_cache_file)
                    img = Image.open(xbmc.translatePath(xbmc_cache_file))
                    break
                elif xbmcvfs.exists(xbmc_vid_cache_file):
                    log("image already in xbmc video cache: " + xbmc_vid_cache_file)
                    img = Image.open(xbmc.translatePath(xbmc_vid_cache_file))
                    break
                else:
                    filterimage = urllib.unquote(filterimage.replace("image://", "")).decode('utf8')
                    if filterimage.endswith("/"):
                        filterimage = filterimage[:-1]
                    log("copy image from source: " + filterimage)
                    xbmcvfs.copy(filterimage, targetfile)
                    img = Image.open(targetfile)
                    break
            except:
                log("Could not get image for %s (try %i)" % (filterimage, i))
                xbmc.sleep(500)
        if not img:
            return "", imagecolor
        img = Pixelate_Image(img,pixels)
        img.save(targetfile)
    else:
        log("pixelated img already created: " + targetfile)
    return targetfile, imagecolor


def Filter_Twotone(filterimage, black, white):
    if HOME.getProperty('colorbox_running') != 'True'
    	if not xbmcvfs.exists(ADDON_DATA_PATH):
    		xbmcvfs.mkdir(ADDON_DATA_PATH)
    	HOME.setProperty('colorbox_running', 'True')
    md5 = hashlib.md5(filterimage).hexdigest()
    filename = md5 + "twotone" + str(black) + str(white) + ".png"
    targetfile = os.path.join(ADDON_DATA_PATH, filename)
    cachedthumb = xbmc.getCacheThumbName(filterimage)
    xbmc_vid_cache_file = os.path.join("special://profile/Thumbnails/Video", cachedthumb[0], cachedthumb)
    xbmc_cache_file = os.path.join("special://profile/Thumbnails/", cachedthumb[0], cachedthumb[:-4] + ".jpg")
    if filterimage == "":
        return ""
    if not xbmcvfs.exists(targetfile):
        img = None
        for i in range(1, 4):
            try:
                if xbmcvfs.exists(xbmc_cache_file):
                    log("image already in xbmc cache: " + xbmc_cache_file)
                    img = Image.open(xbmc.translatePath(xbmc_cache_file))
                    break
                elif xbmcvfs.exists(xbmc_vid_cache_file):
                    log("image already in xbmc video cache: " + xbmc_vid_cache_file)
                    img = Image.open(xbmc.translatePath(xbmc_vid_cache_file))
                    break
                else:
                    filterimage = urllib.unquote(filterimage.replace("image://", "")).decode('utf8')
                    if filterimage.endswith("/"):
                        filterimage = filterimage[:-1]
                    log("copy image from source: " + filterimage)
                    xbmcvfs.copy(filterimage, targetfile)
                    img = Image.open(targetfile)
                    break
            except:
                log("Could not get image for %s (try %i)" % (filterimage, i))
                xbmc.sleep(500)
        if not img:
            return ""
        img = image_recolorize(img,black,white)
        img.save(targetfile)
    else:
        log("pixelated img already created: " + targetfile)
    return targetfile


def Pixelate_Image(img, pixelSize=20):
    backgroundColor = (0,)*3
    image = img
    image = image.resize((image.size[0]/pixelSize, image.size[1]/pixelSize), Image.NEAREST)
    image = image.resize((image.size[0]*pixelSize, image.size[1]*pixelSize), Image.NEAREST)
    pixel = image.load()
    for i in range(0,image.size[0],pixelSize):
      for j in range(0,image.size[1],pixelSize):
        for r in range(pixelSize):
          pixel[i+r,j] = backgroundColor
          pixel[i,j+r] = backgroundColor
    return image


def Get_Colors(img):
    width, height = img.size
    pixels = img.load()
    data = []
    for x in range(width / 2):
        for y in range(height / 2):
            cpixel = pixels[x * 2, y * 2]
            data.append(cpixel)
    r = 0
    g = 0
    b = 0
    counter = 0
    for x in range(len(data)):
        brightness = data[x][0] + data[x][1] + data[x][2]
        if brightness > 150 and brightness < 720:
            r += data[x][0]
            g += data[x][1]
            b += data[x][2]
            counter += 1
    if counter > 0:
        rAvg = int(r / counter)
        gAvg = int(g / counter)
        bAvg = int(b / counter)
        Avg = (rAvg + gAvg + bAvg) / 3
        minBrightness = 130
        if Avg < minBrightness:
            Diff = minBrightness - Avg
            if rAvg <= (255 - Diff):
                rAvg += Diff
            else:
                rAvg = 255
            if gAvg <= (255 - Diff):
                gAvg += Diff
            else:
                gAvg = 255
            if bAvg <= (255 - Diff):
                bAvg += Diff
            else:
                bAvg = 255
        imagecolor = "FF%s%s%s" % (format(rAvg, '02x'), format(gAvg, '02x'), format(bAvg, '02x'))
    else:
        imagecolor = "FFF0F0F0"
    log("Average Color: " + imagecolor)
    return imagecolor


def image_recolorize(src, black="#000000", white="#FFFFFF"):
    # img = image_recolorize(img, black="#000000", white="#FFFFFF")
    """
    Returns a recolorized version of the initial image using a two-tone
    approach. The color in the black argument is used to replace black pixels
    and the color in the white argument is used to replace white pixels.

    The defaults set the image to a b/w hued image.
    """
    return ImageOps.colorize(ImageOps.grayscale(src), black, white)


def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (ADDON_ID, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)


def prettyprint(string):
    log(simplejson.dumps(string, sort_keys=True, indent=4, separators=(',', ': ')))
