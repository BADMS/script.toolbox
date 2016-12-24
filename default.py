import sys
import os
import xbmc
import xbmcgui
import xbmcaddon

ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_LANGUAGE = ADDON.getLocalizedString
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_DATA_PATH = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID))
HOME = xbmcgui.Window(10000)
sys.path.append(xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'lib')))

from Utils import *


class Main:

    def __init__(self):
        log("version %s started" % ADDON_VERSION)
        self._init_vars()
        self._parse_argv()
        if self.infos:
            self._StartInfoActions()
        if self.control == "plugin":
            xbmcplugin.endOfDirectory(self.handle)
        if not xbmcvfs.exists(ADDON_DATA_PATH):
            # addon data path does not exist...create it
            xbmcvfs.mkdir(ADDON_DATA_PATH)
        while self.daemon and not xbmc.abortRequested:
            self.show_now = xbmc.getInfoLabel("ListItem.TVShowTitle")
            if self.show_now != self.show_prev and xbmc.getInfoLabel("ListItem.Property(WatchedEpisodes)") != self.show_watched:
                self.show_watched = xbmc.getInfoLabel("ListItem.Property(WatchedEpisodes)")
                self.show_prev = self.show_now
                Show_Percentage()
            if not HOME.getProperty("cpa_daemon_set") == 'None':
                self.image_now_cpa = xbmc.getInfoLabel("ListItem.Art(poster)")
                if xbmc.getCondVisibility("String.IsEqual(ListItem.DBTYPE,episode)"):
                    self.image_now_cpa = xbmc.getInfoLabel("ListItem.Art(thumb)")
                if xbmc.getCondVisibility("Window.IsActive(movieinformation)") and xbmc.getCondVisibility("String.IsEqual(ListItem.DBTYPE,episode)"):
                    self.image_now_cpa = xbmc.getInfoLabel("ListItem.Art(poster)")
                if self.image_now_cpa == '' and xbmc.getInfoLabel("ListItem.Art(season.poster)") != '':
                    self.image_now_cpa = xbmc.getInfoLabel("ListItem.Art(season.poster)")
                elif self.image_now_cpa == '' and xbmc.getInfoLabel("ListItem.Art(tvshow.poster)") != '':
                    self.image_now_cpa = xbmc.getInfoLabel("ListItem.Art(tvshow.poster)")
                elif self.image_now_cpa == '' and xbmc.getInfoLabel("ListItem.Art(thumb)") != '':
                    self.image_now_cpa = xbmc.getInfoLabel("ListItem.Art(thumb)")
                elif self.image_now_cpa == '' and xbmc.getInfoLabel("ListItem.Icon") != '':
                    self.image_now_cpa = xbmc.getInfoLabel("ListItem.Icon")
                elif self.image_now_cpa == '' and HOME.getProperty("cpa_daemon_fallback") != '':
                    self.image_now_cpa = HOME.getProperty("cpa_daemon_fallback")
                if self.image_now_cpa != self.image_prev_cpa:
                    try:
                        self.image_prev_cpa = self.image_now_cpa
                        HOME.setProperty('ImageUpdating', '0')
                        if HOME.getProperty("cpa_daemon_set") == 'Blur':
                            image, imagecolor = Filter_Image(self.image_now_cpa, self.radius)
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", imagecolor)
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(imagecolor))
                        elif HOME.getProperty("cpa_daemon_set") == 'Pixelate':
                            image = Filter_Pixelate(self.image_now_cpa, self.pixels)
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                        elif HOME.getProperty("cpa_daemon_set") == 'Posterize':
                            image = Filter_Posterize(self.image_now_cpa, self.bits)
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                        elif HOME.getProperty("cpa_daemon_set") == 'Distort':
                            image = Filter_Distort(self.image_now_cpa, self.delta_x, self.delta_y)
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                        elif HOME.getProperty("cpa_daemon_set") == 'Two tone':
                            image = Filter_Twotone(self.image_now_cpa, self.black, self.white)
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                        elif HOME.getProperty("cpa_daemon_set") == 'Shift block':
                            image = Filter_Shiftblock(self.image_now_cpa)
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                        elif HOME.getProperty("cpa_daemon_set") == 'Pixel none':
                            image = Filter_Pixelshift(self.image_now_cpa, "none")
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                        elif HOME.getProperty("cpa_daemon_set") == 'Pixel waves':
                            image = Filter_Pixelshift(self.image_now_cpa, "waves")
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                        elif HOME.getProperty("cpa_daemon_set") == 'Pixel random':
                            image = Filter_Pixelshift(self.image_now_cpa, "random")
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                        elif HOME.getProperty("cpa_daemon_set") == 'Pixel file':
                            image = Filter_Pixelshift(self.image_now_cpa, "file")
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                        elif HOME.getProperty("cpa_daemon_set") == 'Pixel edges':
                            image = Filter_Pixelshift(self.image_now_cpa, "edges")
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                        elif HOME.getProperty("cpa_daemon_set") == 'Pixel fedges':
                            image = Filter_Pixelshift(self.image_now_cpa, "fedges")
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                        elif HOME.getProperty("cpa_daemon_set") == 'Fake light':
                            image = Filter_Fakelight(self.image_now_cpa, pixels=192)
                            HOME.setProperty('ImageFiltercpa', image)
                            HOME.setProperty("ImageColorcpa", Random_Color())
                            HOME.setProperty("ImageCColorcpa", Complementary_Color(HOME.getProperty("ImageColorcpa")))
                    except:
                        log("Could not process image for cpa daemon")
                    HOME.setProperty('ImageUpdating', '1')
            if not HOME.getProperty("cfa_daemon_set") == 'None':
                self.image_now_cfa = xbmc.getInfoLabel("ListItem.Art(fanart)")
                if self.image_now_cfa != self.image_prev_cfa:
                    try:
                        self.image_prev_cfa = self.image_now_cfa
                        HOME.setProperty('ImageUpdating', '0')
                        if HOME.getProperty("cfa_daemon_set") == 'Blur':
                            image, imagecolor = Filter_Image(self.image_now_cfa, self.radius)
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", imagecolor)
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(imagecolor))
                        elif HOME.getProperty("cfa_daemon_set") == 'Pixelate':
                            image = Filter_Pixelate(self.image_now_cfa, self.pixels)
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                        elif HOME.getProperty("cfa_daemon_set") == 'Posterize':
                            image = Filter_Posterize(self.image_now_cfa, self.bits)
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                        elif HOME.getProperty("cfa_daemon_set") == 'Distort':
                            image = Filter_Distort(self.image_now_cfa, self.delta_x, self.delta_y)
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                        elif HOME.getProperty("cfa_daemon_set") == 'Two tone':
                            image = Filter_Twotone(self.image_now_cfa, self.black, self.white)
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                        elif HOME.getProperty("cfa_daemon_set") == 'Shift block':
                            image = Filter_Shiftblock(self.image_now_cfa)
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                        elif HOME.getProperty("cfa_daemon_set") == 'Pixel none':
                            image = Filter_Pixelshift(self.image_now_cfa, "none")
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                        elif HOME.getProperty("cfa_daemon_set") == 'Pixel waves':
                            image = Filter_Pixelshift(self.image_now_cfa, "waves")
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                        elif HOME.getProperty("cfa_daemon_set") == 'Pixel random':
                            image = Filter_Pixelshift(self.image_now_cfa, "random")
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                        elif HOME.getProperty("cfa_daemon_set") == 'Pixel file':
                            image = Filter_Pixelshift(self.image_now_cfa, "file")
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                        elif HOME.getProperty("cfa_daemon_set") == 'Pixel edges':
                            image = Filter_Pixelshift(self.image_now_cfa, "edges")
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                        elif HOME.getProperty("cfa_daemon_set") == 'Pixel fedges':
                            image = Filter_Pixelshift(self.image_now_cfa, "fedges")
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                        elif HOME.getProperty("cfa_daemon_set") == 'Fake light':
                            image = Filter_Fakelight(self.image_now_cfa, pixels=192)
                            HOME.setProperty('ImageFiltercfa', image)
                            HOME.setProperty("ImageColorcfa", Random_Color())
                            HOME.setProperty("ImageCColorcfa", Complementary_Color(HOME.getProperty("ImageColorcfa")))
                    except:
                        log("Could not process image for cfa daemon")
                    HOME.setProperty('ImageUpdating', '1')
            if not HOME.getProperty("cha_daemon_set") == 'None':
                self.image_now_cha = xbmc.getInfoLabel("Control.GetLabel(7977)")
                if self.image_now_cha != self.image_prev_cha:
                    try:
                        self.image_prev_cha = self.image_now_cha
                        HOME.setProperty('ImageUpdating', '0')
                        imagecolor = Color_Only(self.image_now_cha)
                        HOME.setProperty("ImageColorcha", imagecolor)
                        HOME.setProperty("ImageCColorcha", Complementary_Color(imagecolor))
                        HOME.setProperty('ImageUpdating', '1')
                    except:
                        log("Could not process image for cha daemon")
            self.image_now = xbmc.getInfoLabel("Player.Art(thumb)")
            self.image_now_fa = xbmc.getInfoLabel("MusicPlayer.Property(Fanart_Image)")
            if self.image_now != self.image_prev and xbmc.Player().isPlayingAudio():
                try:
                    self.image_prev = self.image_now
                    image, imagecolor = Filter_Image(self.image_now, self.radius)
                    HOME.setProperty('ImageFilter1', image)
                    HOME.setProperty("ImageColor1", imagecolor)
                    image = Filter_Pixelate(self.image_now, self.pixels)
                    HOME.setProperty('ImageFilter2', image)
                    HOME.setProperty("ImageColor2", Random_Color())
                    image = Filter_Posterize(self.image_now, self.bits)
                    HOME.setProperty('ImageFilter3', image)
                    HOME.setProperty("ImageColor3", Random_Color())
                    image = Filter_Twotone(self.image_now, self.black, self.white)
                    HOME.setProperty('ImageFilter4', image)
                    HOME.setProperty("ImageColor4", Random_Color())
                    image = Filter_Distort(self.image_now, self.delta_x, self.delta_y)
                    HOME.setProperty('ImageFilter5', image)
                    HOME.setProperty("ImageColor5", Random_Color())
                except:
                    log("Could not process image for f daemon")
            if self.image_now_fa != self.image_prev_fa and xbmc.Player().isPlayingAudio():
                try:
                    self.image_prev_fa = self.image_now_fa
                    image, imagecolor = Filter_Image(self.image_now_fa, self.radius)
                    HOME.setProperty('ImageFilterfa1', image)
                    HOME.setProperty("ImageColorfa1", imagecolor)
                    image = Filter_Pixelate(self.image_now_fa, self.pixels)
                    HOME.setProperty('ImageFilterfa2', image)
                    HOME.setProperty("ImageColorfa2", Random_Color())
                    image = Filter_Posterize(self.image_now_fa, self.bits)
                    HOME.setProperty('ImageFilterfa3', image)
                    HOME.setProperty("ImageColorfa3", Random_Color())
                    image = Filter_Twotone(self.image_now_fa, self.black, self.white)
                    HOME.setProperty('ImageFilterfa4', image)
                    HOME.setProperty("ImageColorfa4", Random_Color())
                    image = Filter_Distort(self.image_now_fa, self.delta_x, self.delta_y)
                    HOME.setProperty('ImageFilterfa5', image)
                    HOME.setProperty("ImageColorfa5", Random_Color())
                except:
                    log("Could not process image for fa daemon")
            xbmc.sleep(300)

    def _StartInfoActions(self):
        for info in self.infos:
            if info == 'randomcolor':
                imagecolor = Random_Color()
                HOME.setProperty(self.prefix + "ImageColor", imagecolor)
                HOME.setProperty(self.prefix + "ImageCColor", Complementary_Color(imagecolor))
            elif info == 'percentage':
                Show_Percentage()
            elif info == 'bluronly':
                HOME.clearProperty(self.prefix + 'ImageFilter')
                image = Filter_ImageOnly(self.id, self.radius)
                HOME.setProperty(self.prefix + 'ImageFilter', image)
            elif info == 'blur':
                HOME.clearProperty(self.prefix + 'ImageFilter')
                image, imagecolor = Filter_Image(self.id, self.radius)
                HOME.setProperty(self.prefix + 'ImageFilter', image)
                HOME.setProperty(self.prefix + "ImageColor", imagecolor)
                HOME.setProperty(self.prefix + "ImageCColor", Complementary_Color(imagecolor))
            elif info == 'pixelate':
                imagecolor = Random_Color()
                HOME.setProperty(self.prefix + "ImageColor", imagecolor)
                HOME.setProperty(self.prefix + "ImageCColor", Complementary_Color(imagecolor))
                image = Filter_Pixelate(self.id, self.pixels)
                if image != "":
                    HOME.setProperty(self.prefix + 'ImageFilter', image)
            elif info == 'twotone':
                image = Filter_Twotone(self.id, self.black, self.white)
                HOME.setProperty(self.prefix + 'ImageFilter', image)
            elif info == 'posterize':
                image = Filter_Posterize(self.id, self.bits)
                HOME.setProperty(self.prefix + 'ImageFilter', image)
            elif info == 'fakelight':
                image = Filter_Fakelight(self.id, self.pixels)
                HOME.setProperty(self.prefix + 'ImageFilter', image)
            elif info == 'distort':
                image = Filter_Distort(self.id, self.delta_x, self.delta_y)
                HOME.setProperty(self.prefix + 'ImageFilter', image)
            elif info == 'shiftblock':
                image = Filter_Shiftblock(self.id, self.blocksize, self.sigma, self.iterations)
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
        self.bits = 2
        self.pixels = 20
        self.container = 518
        self.black = "#000000"
        self.white = "#FFFFFF"
        self.delta_x = 50
        self.delta_y = 90
        self.blocksize = 192
        self.sigma = 0.05
        self.iterations = 1920
        self.daemon = False
        self.show_now = ""
        self.image_now = ""
        self.image_now_fa = ""
        self.image_now_cfa = ""
        self.image_now_cpa = ""
        self.image_now_cha = ""
        self.show_prev = ""
        self.image_prev = ""
        self.image_prev_fa = ""
        self.image_prev_cfa = ""
        self.image_prev_cpa = ""
        self.image_prev_cha = ""
        self.show_watched = ""
        self.autoclose = ""

    def _parse_argv(self):
        args = sys.argv
        for arg in args:
            arg = arg.replace("'\"", "").replace("\"'", "")
            if arg == 'script.colorbox':
                continue
            elif arg.startswith('info='):
                self.infos.append(arg[5:])
            elif arg.startswith('id='):
                self.id = RemoveQuotes(arg[3:])
            elif arg.startswith('dbid='):
                self.dbid = int(arg[5:])
            elif arg.startswith('daemon='):
                self.daemon = True
            elif arg.startswith('prefix='):
                self.prefix = arg[7:]
                if not self.prefix.endswith("."):
                    self.prefix = self.prefix + "."
            elif arg.startswith('radius='):
                self.radius = int(arg[7:])
            elif arg.startswith('pixels='):
                self.pixels = int(arg[7:])
            elif arg.startswith('bits='):
                self.bits = int(arg[5:])
            elif arg.startswith('black='):
                self.black = RemoveQuotes(arg[6:])
            elif arg.startswith('white='):
                self.white = RemoveQuotes(arg[6:])
            elif arg.startswith('delta_x='):
                self.delta_x = int(arg[8:])
            elif arg.startswith('delta_y='):
                self.delta_y = int(arg[8:])
            elif arg.startswith('blocksize='):
                self.blocksize = int(arg[10:])
            elif arg.startswith('sigma='):
                self.sigma = int(arg[6:])
            elif arg.startswith('iterations='):
                self.iterations = int(arg[11:])
            elif arg.startswith('container='):
                self.container = RemoveQuotes(arg[10:])

class ColorBoxMonitor(xbmc.Monitor):

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
