import sys
import os
import xbmc
import xbmcgui
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_LANGUAGE = ADDON.getLocalizedString
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")
EXTRAFANART_LIMIT = 4
EXTRATHUMB_LIMIT = 4
HOME = xbmcgui.Window(10000)
sys.path.append(xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'lib')))

from Utils import *


class Main:

    def __init__(self):
        log("version %s started" % ADDON_VERSION)
        xbmc.executebuiltin('SetProperty(colorbox_running,True,home)')
        self._init_vars()
        self._parse_argv()
        if self.infos:
            self._StartInfoActions()
        elif not len(sys.argv) > 1:
            self._selection_dialog()
        if self.control == "plugin":
            xbmcplugin.endOfDirectory(self.handle)
        xbmc.executebuiltin('ClearProperty(colorbox_running,home)')
        while self.daemon and not xbmc.abortRequested:
            self.image_now = xbmc.getInfoLabel("Player.Art(thumb)")
            if self.image_now != self.image_prev:
                self.image_prev = self.image_now
                image, imagecolor = Filter_Image(self.image_now, self.radius)
                HOME.setProperty(self.prefix + 'ImageFilter', image)
                HOME.setProperty(self.prefix + "ImageColor", imagecolor)
            else:
                xbmc.sleep(300)

    def _StartInfoActions(self):
        for info in self.infos:
            if info == 'blur':
                HOME.clearProperty(self.prefix + 'ImageFilter')
                log("Blur image %s with radius %i" % (self.id, self.radius))
                image, imagecolor = Filter_Image(self.id, self.radius)
                HOME.setProperty(self.prefix + 'ImageFilter', image)
                HOME.setProperty(self.prefix + "ImageColor", imagecolor)
            elif info == 'pixelate':
		image, imagecolor = Filter_Pixelate(self.id, self.pixels)
		log("Pixelate image %s with pixels %i" % (self.id, self.pixels))
		HOME.setProperty(self.prefix + 'ImageFilter', image)
		HOME.setProperty(self.prefix + "ImageColor", imagecolor)
		HOME.setProperty(self.prefix + 'ImageUpdating', '1')
            elif info == 'twotone':
		image = Filter_Twotone(self.id, self.black, self.white)
		log("Twotone image %s with color1 %s color2 %s" % (self.id, self.black, self.white))
		HOME.setProperty(self.prefix + 'ImageFilter', image)
		HOME.setProperty(self.prefix + 'ImageUpdating', '1')

    def _init_vars(self):
        self.window = xbmcgui.Window(10000)  # Home Window
        self.control = None
        self.infos = []
        self.id = ""
        self.dbid = ""
        self.prefix = ""
        self.radius = 5
        self.pixels = 20
        self.black = "#000000"
        self.white = "#FFFFFF"
        self.daemon = False
        self.image_now = ""
        self.image_prev = ""
        self.autoclose = ""
        # self.Monitor = colorboxMonitor(self)

    def _parse_argv(self):
        args = sys.argv
        for arg in args:
            arg = arg.replace("'\"", "").replace("\"'", "")
            log(arg)
            if arg == 'script.colorbox':
                continue
            elif arg.startswith('info='):
                self.infos.append(arg[5:])
            elif arg.startswith('id='):
                self.id = RemoveQuotes(arg[3:])
            elif arg.startswith('dbid='):
                self.dbid = int(arg[5:])
            elif arg.startswith('prefix='):
                self.prefix = arg[7:]
                if not self.prefix.endswith("."):
                    self.prefix = self.prefix + "."
            elif arg.startswith('radius='):
                self.radius = int(arg[7:])
            elif arg.startswith('pixels='):
                self.pixels = int(arg[7:])
            elif arg.startswith('black='):
                self.black = int(arg[6:])
            elif arg.startswith('white='):
                self.white = int(arg[6:])


class colorboxMonitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)

    def onPlayBackStarted(self):
        pass
        # HOME.clearProperty(self.prefix + 'ImageFilter')
        # Notify("test", "test")
        # image, imagecolor = Filter_Image(self.id, self.radius)
        # HOME.setProperty(self.prefix + 'ImageFilter', image)
        # HOME.setProperty(self.prefix + "ImageColor", imagecolor)


if __name__ == "__main__":
    Main()
log('finished')
