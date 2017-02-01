import os, sys
import hashlib
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

ADDON = xbmcaddon.Addon()
ADDON_VERSION = ADDON.getAddonInfo('version')
ADDON_LANGUAGE = ADDON.getLocalizedString
ADDON_PATH = ADDON.getAddonInfo('path').decode("utf-8")
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_DATA_PATH = os.path.join(xbmc.translatePath("special://profile/addon_data/%s" % ADDON_ID))
HOME = xbmcgui.Window(10000)

sys.path.append(xbmc.translatePath(os.path.join(ADDON_PATH, 'resources', 'lib')))

from Utils import *

ColorBox_function_map = {
        'blur': blur,
        'pixelate': pixelate,
        'shiftblock': shiftblock,
        'pixelnone': pixelnone,
        'pixelwaves': pixelwaves,
        'pixelrandom': pixelrandom,
        'pixelfile': pixelfile,
        'pixelfedges': pixelfedges,
        'pixeledges': pixeledges,
        'fakelight': fakelight,
        'twotone': twotone,
        'posterize': posterize,
        'distort': distort
}


class ColorBoxMain:

    def __init__(self):
        log("version %s started" % ADDON_VERSION)
        self._init_vars()
        self._parse_argv()
        HOME.setProperty("OldImageColorcpa", "FF000000")
        HOME.setProperty("ImageColorcpa", "FF000000")
        HOME.setProperty("OldImageCColorcpa", "FF000000")
        HOME.setProperty("ImageCColorcpa", "FF000000")
        HOME.setProperty("OldImageColorcfa", "FF000000")
        HOME.setProperty("ImageColorcfa", "FF000000")
        HOME.setProperty("OldImageCColorcfa", "FF000000")
        HOME.setProperty("ImageCColorcfa", "FF000000")
        HOME.setProperty("OldImageColorcha", "FF000000")
        HOME.setProperty("ImageColorcha", "FF000000")
        HOME.setProperty("OldImageCColorcha", "FF000000")
        HOME.setProperty("ImageCColorcha", "FF000000")
        if not xbmcvfs.exists(ADDON_DATA_PATH):
            # addon data path does not exist...create it
            xbmcvfs.mkdir(ADDON_DATA_PATH)
        if self.infos:
            self._StartInfoActions()
        if self.control == "plugin":
            xbmcplugin.endOfDirectory(self.handle)
        while self.daemon and not xbmc.abortRequested:
            self.show_now = xbmc.getInfoLabel("ListItem.TVShowTitle")
            if self.show_now != self.show_prev and xbmc.getInfoLabel("ListItem.Property(WatchedEpisodes)") != self.show_watched:
                self.show_watched = xbmc.getInfoLabel("ListItem.Property(WatchedEpisodes)")
                self.show_prev = self.show_now
                Show_Percentage()
            cpa_daemon_set = HOME.getProperty("cpa_daemon_set")
            if not cpa_daemon_set == 'None':
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
                        HOME.setProperty("OldImageColorcpa", HOME.getProperty("ImageColorcpa"))
                        HOME.setProperty("OldImageCColorcpa", HOME.getProperty("ImageCColorcpa"))
                        HOME.setProperty('DaemonPosterImageUpdating', '0')
                        HOME.setProperty('ImageFiltercpa', ColorBox_function_map[cpa_daemon_set](self.image_now_cpa))
                        HOME.setProperty('Imagecpa', self.image_now_cpa)
                        HOME.setProperty('DaemonPosterImageUpdating', '1')
                        Color_Only(self.image_now_cpa, "ImageColorcpa", "ImageCColorcpa")
                    except:
                        log("Could not process image for cfa daemon")
            cfa_daemon_set = HOME.getProperty("cfa_daemon_set")
            #curr_window = xbmc.getInfoLabel("Window.Property(xmlfile)")
            if not cfa_daemon_set == 'None':
                self.image_now_cfa = xbmc.getInfoLabel("ListItem.Art(fanart)")
                if self.image_now_cfa != self.image_prev_cfa:
                    try:
                        self.image_prev_cfa = self.image_now_cfa
                        HOME.setProperty("OldImageColorcfa", HOME.getProperty("ImageColorcfa"))
                        HOME.setProperty("OldImageCColorcfa", HOME.getProperty("ImageCColorcfa"))
                        HOME.setProperty('DaemonFanartImageUpdating', '0')
                        HOME.setProperty('ImageFiltercfa', ColorBox_function_map[cfa_daemon_set](self.image_now_cfa))
                        HOME.setProperty('DaemonFanartImageUpdating', '1')
                        Color_Only(self.image_now_cfa, "ImageColorcfa", "ImageCColorcfa")
                    except:
                        log("Could not process image for cfa daemon")
            if not HOME.getProperty("cha_daemon_set") == 'None':
                self.image_now_cha = xbmc.getInfoLabel("Control.GetLabel(7977)")
                if self.image_now_cha != self.image_prev_cha:
                    try:
                        self.image_prev_cha = self.image_now_cha
                        HOME.setProperty("OldImageColorcha", HOME.getProperty("ImageColorcha"))
                        HOME.setProperty("OldImageCColorcha", HOME.getProperty("ImageCColorcha"))
                        #HOME.setProperty('DaemonFanartCCUpdating', '0')
                        #HOME.setProperty('DaemonFanartCCUpdating', '1')
                        Color_Only(self.image_now_cha, "ImageColorcha", "ImageCColorcha")
                    except:
                        log("Could not process image for cha daemon")
            xbmc.sleep(100)

    def _StartInfoActions(self):
        for info in self.infos:
            if info == 'randomcolor':
                HOME.setProperty(self.prefix + "ImageColor", Random_Color())
                HOME.setProperty(self.prefix + "ImageCColor", Complementary_Color(HOME.getProperty(self.prefix + "ImageColor")))
            elif info == 'percentage':
                Show_Percentage()
            elif info == 'ptype':
                Pixelshift_Set_Type(self.ptype)
            elif info != '':
                HOME.setProperty(self.prefix + 'ManualImageUpdating', '0')
                HOME.setProperty(self.prefix + 'ImageFilter', ColorBox_function_map[info](self.id))                
                HOME.setProperty(self.prefix + 'ManualImageUpdating', '1')
                imagecolor, cimagecolor = Color_Only_Manual(self.id)
                HOME.setProperty(self.prefix + "ImageColor", imagecolor)
                HOME.setProperty(self.prefix + "ImageCColor", cimagecolor)

    def _init_vars(self):
        self.window = xbmcgui.Window(10000)  # Home Window
        self.control = None
        self.infos = []
        self.id = ""
        self.dbid = ""
        self.ptype = "none"
        self.prefix = ""
        self.radius = 10
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
                self.var1 = int(arg[7:])
            elif arg.startswith('pixels='):
                self.var1 = int(arg[7:])
            elif arg.startswith('bits='):
                self.var1 = int(arg[5:])
            elif arg.startswith('black='):
                self.var1 = RemoveQuotes(arg[6:])
            elif arg.startswith('white='):
                self.var2 = RemoveQuotes(arg[6:])
            elif arg.startswith('delta_x='):
                self.var1 = int(arg[8:])
            elif arg.startswith('delta_y='):
                self.var2 = int(arg[8:])
            elif arg.startswith('blocksize='):
                self.var1 = int(arg[10:])
            elif arg.startswith('sigma='):
                self.var2 = int(arg[6:])
            elif arg.startswith('iterations='):
                self.var3 = int(arg[11:])
            elif arg.startswith('ptype='):
                self.ptype = arg[6:]

class ColorBoxMonitor(xbmc.Monitor):

    def __init__(self, *args, **kwargs):
        xbmc.Monitor.__init__(self)

    def onPlayBackStarted(self):
        pass
        # HOME.clearProperty(self.prefix + 'ImageFilter')
        # Notify("test", "test")
        # image, imagecolor, cimagecolor = Filter_blur(self.id, self.radius)
        # HOME.setProperty(self.prefix + 'ImageFilter', image)
        # HOME.setProperty(self.prefix + "ImageColor", imagecolor)


if __name__ == "__main__":
    ColorBoxMain()
log('finished')