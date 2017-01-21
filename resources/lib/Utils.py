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
from PIL import Image, ImageOps, ImageEnhance, ImageDraw, ImageStat, ImageFilter
from ImageOperations import MyGaussianBlur
from decimal import *
from xml.dom.minidom import parse
import time

ADDON = xbmcaddon.Addon()
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_LANGUAGE = ADDON.getLocalizedString
ADDON_DATA_PATH = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID))
ADDON_COLORS = os.path.join(ADDON_DATA_PATH, "colors.txt")
HOME = xbmcgui.Window(10000)

black_pixel = (0, 0, 0, 255)
white_pixel = (255, 255, 255, 255)
randomness = int(0)
threshold = int(100)
clength = int(50)
angle = float(0)
colors_dict={}


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


def Color_Only(filterimage, var1, var2):
    md5 = hashlib.md5(filterimage).hexdigest()
    if not colors_dict:
        try:
            with open(ADDON_COLORS) as file:
                for line in file:
                    a, b, c = line.strip().split(':')
                    global colors_dict
                    colors_dict[a] = b + ':' + c
        except:
            log ("no colors.txt yet")
    if md5 not in colors_dict:
        filename = md5 + ".png"
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
                    xbmc.sleep(200)
            if not img:
                return "", ""
            img.thumbnail((200, 200))
            img = img.convert('RGB')
            img.save(targetfile)
        else:
            img = Image.open(targetfile)
        imagecolor, cimagecolor = Get_Colors(img, md5)

        global colors_dict
        colors_dict[md5] = imagecolor + ':' + cimagecolor  # update entry
        with open(ADDON_COLORS, 'w') as file:  # rewrite file
            for id, values in colors_dict.items():
                file.write(':'.join([id] + values.split(':')) + '\n')
    else:
        imagecolor, cimagecolor = colors_dict[md5].split(':')
    var3 = 'Old' + var1
    var4 = 'Old' + var2
    linear_gradient(var1, HOME.getProperty(var3)[2:8], imagecolor[2:8], 100)
    linear_gradient(var2, HOME.getProperty(var4)[2:8], cimagecolor[2:8], 100)

    return imagecolor, cimagecolor


def Filter_Image(filterimage, radius):
    md5 = hashlib.md5(filterimage).hexdigest()
    filename = md5 + str(radius) + ".png"
    targetfile = os.path.join(ADDON_DATA_PATH, filename)
    cachedthumb = xbmc.getCacheThumbName(filterimage)
    xbmc_vid_cache_file = os.path.join("special://profile/Thumbnails/Video", cachedthumb[0], cachedthumb)
    xbmc_cache_file = os.path.join("special://profile/Thumbnails/", cachedthumb[0], cachedthumb[:-4] + ".jpg")
    if filterimage == "":
        return "", "", ""
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
                xbmc.sleep(100)
        if not img:
            return "", "", ""
        img.thumbnail((200, 200), Image.ANTIALIAS)
        img = img.convert('RGB')
        imgfilter = MyGaussianBlur(radius=radius)
        img = img.filter(imgfilter)
        img.save(targetfile)
    else:
        img = Image.open(targetfile)
    imagecolor, cimagecolor = Get_Colors(img, md5)
    return targetfile, imagecolor, cimagecolor


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
                
                xbmc.sleep(100)
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
                xbmc.sleep(100)
        if not img:
            return ""
        img = Pixelate_Image(img,pixels)
        img.save(targetfile)
    return targetfile


def Filter_Shiftblock(filterimage, blockSize=192, sigma=0.05, iterations=1920):
    md5 = hashlib.md5(filterimage).hexdigest()
    filename = md5 + "shift" + str(blockSize) + str(sigma) + str(iterations) + ".png"
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
                xbmc.sleep(100)
        if not img:
            return ""
        img = Shiftblock_Image(img, blockSize, sigma, iterations)
        img.save(targetfile)
    return targetfile


def Filter_Pixelshift(filterimage, ptype="none", pthreshold=100, pclength=50, pangle=00, prandomness=10):
    """stype; 1=random, 2=edges, 3=waves, 4=file, 5=file_edges, 0=none"""
    md5 = hashlib.md5(filterimage).hexdigest()
    filename = md5 + "pixelshift" + str(ptype) + str(pthreshold) + str(pclength) + str(pangle) + str(prandomness) + ".png"
    targetfile = os.path.join(ADDON_DATA_PATH, filename)
    cachedthumb = xbmc.getCacheThumbName(filterimage)
    xbmc_vid_cache_file = os.path.join("special://profile/Thumbnails/Video", cachedthumb[0], cachedthumb)
    xbmc_cache_file = os.path.join("special://profile/Thumbnails/", cachedthumb[0], cachedthumb[:-4] + ".jpg")
    global threshold
    threshold = int(pthreshold)
    global clength
    clength = int(pclength)
    global angle
    angle = int(pangle)
    global randomness
    randomness = float(prandomness)
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
                xbmc.sleep(100)
        if not img:
            return ""
        img.thumbnail((400, 400), Image.ANTIALIAS)
        img = img.convert('RGB')
        img = Pixelshift_Image(img, ptype)
        img.save(targetfile)
    else:
        img = Image.open(targetfile)
    imagecolor, cimagecolor = Get_Colors(img, md5)
    return targetfile, imagecolor, cimagecolor


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
                xbmc.sleep(100)
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
                
                xbmc.sleep(100)
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
                
                xbmc.sleep(100)
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
                
                xbmc.sleep(100)
        if not img:
            return ""
        img = image_distort(img,delta_x,delta_y)
        img.save(targetfile)
    return targetfile


def Get_Colors(img, md5):
    if not colors_dict:
        try:
            with open(ADDON_COLORS) as file:
                for line in file:
                    a, b, c = line.strip().split(':')
                    global colors_dict
                    colors_dict[a] = b + ':' + c
        except:
            log ("no colors.txt yet")
    if md5 not in colors_dict:
        colour_tuple = [None, None, None]
        for channel in range(3):
            # Get data for one channel at a time
            pixels = img.getdata(band=channel)
            values = []
            for pixel in pixels:
                values.append(pixel)
            colour_tuple[channel] = clamp(sum(values) / len(values))
        imagecolor = 'ff%02x%02x%02x' % tuple(colour_tuple)
        cimagecolor = Complementary_Color(imagecolor)
        global colors_dict
        colors_dict[md5] = imagecolor + ':' + cimagecolor  # update entry
        with open(ADDON_COLORS, 'w') as file:  # rewrite file
            for id, values in colors_dict.items():
                file.write(':'.join([id] + values.split(':')) + '\n')
    else:
        imagecolor, cimagecolor = colors_dict[md5].split(':')
    return imagecolor, cimagecolor




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


def linear_gradient(var1, start_hex="000000", finish_hex="FFFFFF", n=10, sleep=0.005):
    ''' returns a gradient list of (n) colors between
    two hex colors. start_hex and finish_hex
    should be the full six-digit color string,
    inlcuding the number sign ("#FFFFFF") '''
    # Starting and ending colors in RGB form
    if start_hex == '' or finish_hex == '':
        return
    s = hex_to_RGB('#' + start_hex)
    f = hex_to_RGB('#' + finish_hex)
    # Initilize a list of the output colors with the starting color
    RGB_list = [s]
    # Calcuate a color at each evenly spaced value of t from 1 to n
    for t in range(1, n):
        # Interpolate RGB vector for color at the current value of t
        curr_vector = [
            int(s[j] + (float(t)/(n-1))*(f[j]-s[j]))
            for j in range(3)
        ]
        # Add it to our list of output colors
        HOME.setProperty(var1, RGB_to_hex(curr_vector))
        time.sleep(sleep)
    return


def hex_to_RGB(hex):
    ''' "#FFFFFF" -> [255,255,255] '''
    # Pass 16 to the integer function for change of base
    return [int(hex[i:i+2], 16) for i in range(1,6,2)]


def RGB_to_hex(RGB):
    ''' [255,255,255] -> "#FFFFFF" '''
    # Components need to be integers for hex to make sense
    RGB = [int(x) for x in RGB]
    return "FF"+"".join(["0{0:x}".format(v) if v < 16 else "{0:x}".format(v) for v in RGB])

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


def Shiftblock_Image(image, blockSize=192, sigma=1.05, iterations=300):
    seed = random.random()
    r = random.Random(seed)
    for i in xrange(iterations):
        # Select a block
        bx = int(r.uniform(0, image.size[0]-blockSize))
        by = int(r.uniform(0, image.size[1]-blockSize))
        block = image.crop((bx, by, bx+blockSize-1, by+blockSize-1))

        # Figure out how much to move it.
        # The call to floor() is important so we always round toward
        # 0 rather than to -inf. Just int() would bias the block motion.
        mx = int(math.floor(r.normalvariate(0, sigma)))
        my = int(math.floor(r.normalvariate(0, sigma)))

        # Now actually move the block
        image.paste(block, (bx+mx, by+my))
    return image


# Sorts a given row of pixels
def sort_interval(interval):
	if interval == []:
		return []
	else:
		return(sorted(interval, key = lambda x: x[0] + x[1] + x[2]))

# Generates random widths for intervals. Used by int_random()
def random_width():
	x = random.random()
	# width = int(200*(1-(1-(x-1)**2)**0.5))
	width = int(clength*(1-x))
	# width = int(50/(x+0.1))
	return(width)

# Functions starting with int return intervals according to which to sort
def int_edges(pixels, img):
	edges = img.filter(ImageFilter.FIND_EDGES)
	edges = edges.convert('RGBA')
	edge_data = edges.load()

	filter_pixels = []
	edge_pixels = []
	intervals = []

	for y in range(img.size[1]):
		filter_pixels.append([])
		for x in range(img.size[0]):
			filter_pixels[y].append(edge_data[x, y])

	for y in range(len(pixels)):
		edge_pixels.append([])
		for x in range(len(pixels[0])):
			if filter_pixels[y][x][0] + filter_pixels[y][x][1] + filter_pixels[y][x][2] < threshold:
				edge_pixels[y].append(white_pixel)
			else:
				edge_pixels[y].append(black_pixel)

	for y in range(len(pixels)-1,1,-1):
		for x in range(len(pixels[0])-1,1,-1):
			if edge_pixels[y][x] == black_pixel and edge_pixels[y][x-1] == black_pixel:
				edge_pixels[y][x] = white_pixel

	for y in range(len(pixels)):
		intervals.append([])
		for x in range(len(pixels[0])):
			if edge_pixels[y][x] == black_pixel:
				intervals[y].append(x)
		intervals[y].append(len(pixels[0]))
	return(intervals)

def int_random(pixels, img):
	intervals = []

	for y in range(len(pixels)):
		intervals.append([])
		x = 0
		while True:
			width = random_width()
			x += width
			if x > len(pixels[0]):
				intervals[y].append(len(pixels[0]))
				break
			else:
				intervals[y].append(x)
	return(intervals)

def int_waves(pixels, img):
	intervals = []

	for y in range(len(pixels)):
		intervals.append([])
		x = 0
		while True:
			width = clength + random.randint(0,10)
			x += width
			if x > len(pixels[0]):
				intervals[y].append(len(pixels[0]))
				break
			else:
				intervals[y].append(x)
	return(intervals)

def int_file(pixels, img):
	intervals = []
	file_pixels = []

	img = img.convert('RGBA')
	data = img.load()
	for y in range(img.size[1]):
		file_pixels.append([])
		for x in range(img.size[0]):
			file_pixels[y].append(data[x, y])

	for y in range(len(pixels)-1,1,-1):
		for x in range(len(pixels[0])-1,1,-1):
			if file_pixels[y][x] == black_pixel and file_pixels[y][x-1] == black_pixel:
				file_pixels[y][x] = white_pixel

	for y in range(len(pixels)):
		intervals.append([])
		for x in range(len(pixels[0])):
			if file_pixels[y][x] == black_pixel:
				intervals[y].append(x)
		intervals[y].append(len(pixels[0]))

	return(intervals)

def int_file_edges(pixels, img):
	img = img.resize((len(pixels[0]), len(pixels)), Image.ANTIALIAS)
	edges = img.filter(ImageFilter.FIND_EDGES)
	edges = edges.convert('RGBA')
	edge_data = edges.load()

	filter_pixels = []
	edge_pixels = []
	intervals = []

	for y in range(img.size[1]):
		filter_pixels.append([])
		for x in range(img.size[0]):
			filter_pixels[y].append(edge_data[x, y])

	for y in range(len(pixels)):
		edge_pixels.append([])
		for x in range(len(pixels[0])):
			if filter_pixels[y][x][0] + filter_pixels[y][x][1] + filter_pixels[y][x][2] < threshold:
				edge_pixels[y].append(white_pixel)
			else:
				edge_pixels[y].append(black_pixel)

	for y in range(len(pixels)-1,1,-1):
		for x in range(len(pixels[0])-1,1,-1):
			if edge_pixels[y][x] == black_pixel and edge_pixels[y][x-1] == black_pixel:
				edge_pixels[y][x] = white_pixel

	for y in range(len(pixels)):
		intervals.append([])
		for x in range(len(pixels[0])):
			if edge_pixels[y][x] == black_pixel:
				intervals[y].append(x)
		intervals[y].append(len(pixels[0]))
	return(intervals)

def int_none(pixels, img):
	intervals = []
	for y in range(len(pixels)):
		intervals.append([len(pixels[y])])
	return(intervals)

# Sorts the image
def sort_image(pixels, intervals):
	# Hold sorted pixels
	sorted_pixels=[]
	for y in range(len(pixels)):
		row=[]
		xMin = 0
		for xMax in intervals[y]:
			interval = []
			for x in range(xMin, xMax):
				interval.append(pixels[y][x])
			if random.randint(0,100) >= randomness:
				row = row + sort_interval(interval)
			else:
				row = row + interval
			xMin = xMax
		row.append(pixels[y][0]) # wat
		sorted_pixels.append(row)
	return(sorted_pixels)

def pixel_sort(img, int_function):
	img.convert('RGBA')
	img = img.rotate(angle, expand = True)

	data = img.load()
	new = Image.new('RGBA', img.size)

	pixels = []

	for y in range(img.size[1]):
		pixels.append([])
		for x in range(img.size[0]):
			pixels[y].append(data[x, y])

	intervals = int_function(pixels, img)
	sorted_pixels = sort_image(pixels, intervals)

	for y in range(img.size[1]):
		for x in range(img.size[0]):
			new.putpixel((x, y), sorted_pixels[y][x])

	new = new.rotate(-angle)
	return new

def Pixelshift_Image(img, stype):
    # Get function to define intervals from command line arguments
    """stype; 1=random, 2=edges, 3=waves, 4=file, 5=file_edges, 0=none"""
    if stype == 'random':
        int_function = int_random
    elif stype == 'none':
        int_function = int_none
    elif stype == 'edges':
        int_function = int_edges
    elif stype == 'waves':
        int_function = int_waves
    elif stype == 'file':
        int_function = int_file
    elif stype == 'fedges':
        int_function = int_file_edges

    image = pixel_sort(img, int_function)
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
            #following expression calculates the shuffling 
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
