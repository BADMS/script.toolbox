import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import xbmcplugin
import os, sys
import simplejson
import hashlib
import urllib
import random
import math
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageStat
from ImageOperations import MyGaussianBlur
from decimal import *
from xml.dom.minidom import parse

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_LANGUAGE = ADDON.getLocalizedString
ADDON_DATA_PATH = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID))
HOME = xbmcgui.Window(10000)


def ColorboxFirstRun():
    initdone = HOME.getProperty("colorbox_initialised")
    if not initdone:
        if not xbmcvfs.exists(ADDON_DATA_PATH):
            # addon data path does not exist...create it
            xbmcvfs.mkdir(ADDON_DATA_PATH)
            HOME.setProperty('colorbox_initialised', 'True')
        else: 
            # addon data path exists
            HOME.setProperty('colorbox_initialised', 'True')


def Random_Color():
    return "ff" + "%06x" % random.randint(0, 0xFFFFFF)

def Complementary_Color(hex_color):
    """Returns complementary RGB color [should be format((255!]
    rgb = [hex_color[2:4], hex_color[4:6], hex_color[6:8]]
    comp = [format((325 - int(a, 16)), '02x') for a in rgb]
    return "FF" + "%s" % ''.join(comp)
    Example:
    >>>complementaryColor('FFFFFF')
    '000000'
    """
    rgb = [hex_color[2:4], hex_color[4:6], hex_color[6:8]]
    comp = ['%02X' % (255 - int(a, 16)) for a in rgb]
    """
    if (int(comp[0], 16) > 99 and int(comp[0], 16) < 150 and
        int(comp[1], 16) > 99 and int(comp[1], 16) < 150 and
        int(comp[2], 16) > 99 and int(comp[2], 16) < 150):
            return "FFc2836d"
    """
    return "FF" + "%s" % ''.join(comp)

def RemoveQuotes(label):
    if label.startswith("'") and label.endswith("'") and len(label) > 2:
        label = label[1:-1]
        if label.startswith('"') and label.endswith('"') and len(label) > 2:
            label = label[1:-1]
    return label

def Show_Percentage():
    """nitems = int(xbmc.getInfoLabel('Container().NumItems'))
    for x in range(0, nitems):"""
    try:
        stot = int(xbmc.getInfoLabel('ListItem.Property(TotalEpisodes)'))
        wtot = int(xbmc.getInfoLabel('ListItem.Property(WatchedEpisodes)'))
        """dbid = int(xbmc.getInfoLabel('ListItem(%s).DBID' %x))"""
        getcontext().prec = 6
        perc = "{:.0f}".format(100 / Decimal(stot) * Decimal(wtot))
        """prop = "%i.Show_Percentage" % dbid"""
        HOME.setProperty("Show_Percentage", perc)
    except:
        return
    return

def Filter_Image(filterimage, radius):
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
                    
                    img = Image.open(xbmc.translatePath(xbmc_cache_file))
                    break
                elif xbmcvfs.exists(xbmc_vid_cache_file):
                    
                    img = Image.open(xbmc.translatePath(xbmc_vid_cache_file))
                    break
                else:
                    filterimage = urllib.unquote(filterimage.replace("image://", "")).decode('utf8')
                    if filterimage.endswith("/"):
                        filterimage = filterimage[:-1]
                    
                    xbmcvfs.copy(filterimage, targetfile)
                    img = Image.open(targetfile)
                    break
            except:
                xbmc.sleep(300)
        if not img:
            return "", ""
        img.thumbnail((200, 200), Image.ANTIALIAS)
        img = img.convert('RGB')
        imgfilter = MyGaussianBlur(radius=radius)
        img = img.filter(imgfilter)
        img.save(targetfile)
    else:
        img = Image.open(targetfile)
    imagecolor = Get_Colors(img)
    return targetfile, imagecolor


def Filter_ImageOnly(filterimage, radius):
    md5 = hashlib.md5(filterimage).hexdigest()
    filename = md5 + str(radius) + ".png"
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
                    
                    img = Image.open(xbmc.translatePath(xbmc_cache_file))
                    break
                elif xbmcvfs.exists(xbmc_vid_cache_file):
                    
                    img = Image.open(xbmc.translatePath(xbmc_vid_cache_file))
                    break
                else:
                    filterimage = urllib.unquote(filterimage.replace("image://", "")).decode('utf8')
                    if filterimage.endswith("/"):
                        filterimage = filterimage[:-1]
                    
                    xbmcvfs.copy(filterimage, targetfile)
                    img = Image.open(targetfile)
                    break
            except:
                
                xbmc.sleep(300)
        if not img:
            return ""
        img.thumbnail((200, 200), Image.ANTIALIAS)
        img = img.convert('RGB')
        imgfilter = MyGaussianBlur(radius=radius)
        img = img.filter(imgfilter)
        img.save(targetfile)
    return targetfile


def Filter_Pixelate(filterimage, pixels):
    md5 = hashlib.md5(filterimage).hexdigest()
    filename = md5 + "pixel" + str(pixels) + ".png"
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
                    
                    img = Image.open(xbmc.translatePath(xbmc_cache_file))
                    break
                elif xbmcvfs.exists(xbmc_vid_cache_file):
                    img = Image.open(xbmc.translatePath(xbmc_vid_cache_file))
                    break
                else:
                    filterimage = urllib.unquote(filterimage.replace("image://", "")).decode('utf8')
                    if filterimage.endswith("/"):
                        filterimage = filterimage[:-1]
                    xbmcvfs.copy(filterimage, targetfile)
                    img = Image.open(targetfile)
                    break
            except:
                xbmc.sleep(300)
        if not img:
            return ""
        img = Pixelate_Image(img,pixels)
        img.save(targetfile)
    return targetfile


def Filter_Fakelight(filterimage, pixels):
    md5 = hashlib.md5(filterimage).hexdigest()
    filename = md5 + "fakelight" + str(pixels) + ".png"
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
                    
                    img = Image.open(xbmc.translatePath(xbmc_cache_file))
                    break
                elif xbmcvfs.exists(xbmc_vid_cache_file):
                    img = Image.open(xbmc.translatePath(xbmc_vid_cache_file))
                    break
                else:
                    filterimage = urllib.unquote(filterimage.replace("image://", "")).decode('utf8')
                    if filterimage.endswith("/"):
                        filterimage = filterimage[:-1]
                    xbmcvfs.copy(filterimage, targetfile)
                    img = Image.open(targetfile)
                    break
            except:
                xbmc.sleep(300)
        if not img:
            return ""
        img = fake_light(img,pixels)
        img.save(targetfile)
    return targetfile


def Filter_Twotone(filterimage, black, white):
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
                    
                    img = Image.open(xbmc.translatePath(xbmc_cache_file))
                    break
                elif xbmcvfs.exists(xbmc_vid_cache_file):
                    
                    img = Image.open(xbmc.translatePath(xbmc_vid_cache_file))
                    break
                else:
                    filterimage = urllib.unquote(filterimage.replace("image://", "")).decode('utf8')
                    if filterimage.endswith("/"):
                        filterimage = filterimage[:-1]
                    
                    xbmcvfs.copy(filterimage, targetfile)
                    img = Image.open(targetfile)
                    break
            except:
                
                xbmc.sleep(300)
        if not img:
            return ""
        img = image_recolorize(img,black,white)
        img.save(targetfile)
    return targetfile


def Filter_Posterize(filterimage, bits):
    md5 = hashlib.md5(filterimage).hexdigest()
    filename = md5 + "posterize" + str(bits) + ".png"
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
                    
                    img = Image.open(xbmc.translatePath(xbmc_cache_file))
                    break
                elif xbmcvfs.exists(xbmc_vid_cache_file):
                    
                    img = Image.open(xbmc.translatePath(xbmc_vid_cache_file))
                    break
                else:
                    filterimage = urllib.unquote(filterimage.replace("image://", "")).decode('utf8')
                    if filterimage.endswith("/"):
                        filterimage = filterimage[:-1]
                    
                    xbmcvfs.copy(filterimage, targetfile)
                    img = Image.open(targetfile)
                    break
            except:
                
                xbmc.sleep(300)
        if not img:
            return ""
        img = image_posterize(img,bits)
        img.save(targetfile)
    return targetfile


def Filter_Distort(filterimage, delta_x, delta_y):
    md5 = hashlib.md5(filterimage).hexdigest()
    filename = md5 + "distort" + str(delta_x) + str(delta_y) + ".png"
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
                    
                    img = Image.open(xbmc.translatePath(xbmc_cache_file))
                    break
                elif xbmcvfs.exists(xbmc_vid_cache_file):
                    
                    img = Image.open(xbmc.translatePath(xbmc_vid_cache_file))
                    break
                else:
                    filterimage = urllib.unquote(filterimage.replace("image://", "")).decode('utf8')
                    if filterimage.endswith("/"):
                        filterimage = filterimage[:-1]
                    
                    xbmcvfs.copy(filterimage, targetfile)
                    img = Image.open(targetfile)
                    break
            except:
                
                xbmc.sleep(300)
        if not img:
            return ""
        img = image_distort(img,delta_x,delta_y)
        img.save(targetfile)
    return targetfile


def Get_Colors(img):
    colour_tuple = [None, None, None]
    for channel in range(3):

        # Get data for one channel at a time
        pixels = img.getdata(band=channel)

        values = []
        for pixel in pixels:
            values.append(pixel)

        colour_tuple[channel] = clamp(sum(values) / len(values))

    return 'ff%02x%02x%02x' % tuple(colour_tuple)


def Get_Frequent_Color(img):
    w, h = img.size
    pixels = img.getcolors(w * h)

    most_frequent_pixel = pixels[0]

    for count, colour in pixels:
        if count > most_frequent_pixel[0]:
            most_frequent_pixel = (count, colour)

    return 'ff%02x%02x%02x' % tuple(most_frequent_pixel[1])


def clamp(x): 
    return max(0, min(x, 255))


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


def image_recolorize(src, black="#000000", white="#FFFFFF"):
    # img = image_recolorize(img, black="#000000", white="#FFFFFF")
    """
    Returns a recolorized version of the initial image using a two-tone
    approach. The color in the black argument is used to replace black pixels
    and the color in the white argument is used to replace white pixels.

    The defaults set the image to a b/w hued image.
    """
    return ImageOps.colorize(ImageOps.grayscale(src), black, white)


def image_posterize(src, bits="2"):
    # img = image_recolorize(img, black="#000000", white="#FFFFFF")
    """
    Returns a posterized version of the src image.
    Bits 1-8 define your Atari system decade!

    The defaults set the image to a 2 bits crushed image.
    """
    return ImageOps.posterize(src, bits)


def fake_light(img, tilesize=50):
    WIDTH, HEIGHT = img.size
    for x in xrange(0, WIDTH, tilesize):
        for y in xrange(0, HEIGHT, tilesize):
            br = int(255 * (1 - x / float(WIDTH) * y / float(HEIGHT)))
            tile = Image.new("RGBA", (tilesize, tilesize), (255,255,255,128))
            img.paste((br,br,br), (x, y, x + tilesize, y + tilesize), mask=tile)
    return img            


def image_distort(img, delta_x=50, delta_y=90):
    WIDTH, HEIGHT = img.size
    img_data = img.load()          #loading it, for fast operation
    output = Image.new('RGB',img.size,"gray")  #New image for putput
    output_img = output.load()    #loading this also, for fast operation
    pix=[0, 0]
    for x in range(WIDTH):
        for y in range(HEIGHT):
            #following expression calculates the snuffling 
            x_shift, y_shift =  ( int(abs(math.sin(x) * WIDTH / delta_x)) ,
                                  int(abs(math.tan(math.sin(y))) * HEIGHT / delta_y))
            if x + x_shift < WIDTH:
                pix[0] = x + x_shift
            else:
                pix[0] = x
            if y + y_shift < HEIGHT :
                pix[1] = y + y_shift
            else:
                pix[1] = y
            # do the shuffling
            output_img[x,y] = img_data[tuple(pix)]
    return output            


def log(txt):
    if isinstance(txt, str):
        txt = txt.decode("utf-8")
    message = u'%s: %s' % (ADDON_ID, txt)
    xbmc.log(msg=message.encode("utf-8"), level=xbmc.LOGDEBUG)


def prettyprint(string):
    log(simplejson.dumps(string, sort_keys=True, indent=4, separators=(',', ': ')))
