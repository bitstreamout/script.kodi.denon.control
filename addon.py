import xbmc
import xbmcgui
from xbmcaddon import Addon
import http.client as httplib

try: #PY2 / PY3
    from urllib2 import Request, urlopen
    from urllib2 import URLError
    from urllib import urlencode
except ImportError:
    from urllib.request import Request, urlopen
    from urllib.error import URLError
    from urllib.parse import urlencode

__addon__ = Addon()
ADDON_ID = __addon__.getAddonInfo('id')
KODI_VERSION_MAJOR = int(xbmc.getInfoLabel('System.BuildVersion')[0:2])

monitor = xbmc.Monitor()

from settings import Settings

def log(msg):
    xbmc.log("%s: %s" %(ADDON_ID, msg))

class DenonControlPlayer(xbmc.Player):
    target = '/SETUP/AUDIO/AUDYSSEY/s_audio.asp'
    STATE_VIDEO = 1
    STATE_MUSIC = 2

    def __init__(self, settings, *args, **kwargs):
        assert isinstance(settings, Settings)
        
        self.settings = settings
        self.last_state = 0
        super(DenonControlPlayer, self).__init__(*args, **kwargs)
        
    def onAVStarted(self):
        if self.isPlayingVideo():
            if self.last_state != self.STATE_VIDEO:
                self.apply_video_settings()
                self.last_state = self.STATE_VIDEO
        elif self.isPlayingAudio():
            if self.last_state != self.STATE_MUSIC:
                self.apply_music_settings()
                self.last_state = self.STATE_MUSIC

    def apply_music_settings(self):
        """
        Adjusts the receiver sound settings for playing music
        """
        log("apply music settings")
        try:
            connection = httplib.HTTPConnection(self.settings.avr_ip)
            if self.settings.music_audyssey_enable:
                data = {
                    'setPureDirectOn': 'OFF',
                    'setSetupLock': 'OFF',
                    'listRoomEq': self.settings.music_audyssey_mode,
                    'listRoomEqValue': 'Set',       
                    'radioDynamicEq': self.settings.music_audyssey_dyneq,
                    'radioDynamicVol': self.settings.music_audyssey_dynvol,
                }
                log(data)
                connection.request("POST", self.target, urlencode(data))
                connection.getresponse()

            elif self.settings.music_graphic_eq_change:
                # Make sure Audyssey is off in EQ mode
                data = {
                    'setPureDirectOn': 'OFF',
                    'setSetupLock': 'OFF',
                    'listRoomEq': 'OFF',
                    'listRoomEqValue': 'Set'
                }
                log(data)
                connection.request("POST", self.target, urlencode(data))
                connection.getresponse()
                
                data = {
                    'setPureDirectOn': 'OFF',
                    'setSetupLock': 'OFF',
                    'radioGraphicEQ': self.settings.music_graphic_eq_mode
                }
                log(data)
                connection.request("POST", self.target, urlencode(data))
                connection.getresponse()

        except Exception as error:
            xbmc.log(ADDON_ID +': ' + str(error), xbmc.LOGERROR)


    def apply_video_settings(self):
        """
        Adjusts the receiver sound settings for playing videos
        """
        log("apply video settings")
        try:
            connection = httplib.HTTPConnection(self.settings.avr_ip)
            if self.settings.video_audyssey_enable:
                data = {
                    'setPureDirectOn': 'OFF',
                    'setSetupLock': 'OFF',
                    'listRoomEq': self.settings.video_audyssey_mode,
                    'listRoomEqValue': 'Set',       
                    'radioDynamicEq': self.settings.video_audyssey_dyneq,
                    'radioDynamicVol': self.settings.video_audyssey_dynvol,
                }
                log(data)
                connection.request("POST", self.target, urlencode(data))
                connection.getresponse()
            
            elif self.settings.video_graphic_eq_change:
                # Make sure Audyssey is off in EQ mode
                data = {
                    'setPureDirectOn': 'OFF',
                    'setSetupLock': 'OFF',
                    'listRoomEq': 'OFF',
                    'listRoomEqValue': 'Set'
                }
                log(data)
                connection.request("POST", self.target, urlencode(data))
                connection.getresponse()
                
                data = {
                    'setPureDirectOn': 'OFF',
                    'setSetupLock': 'OFF',
                    'radioGraphicEQ': self.settings.video_graphic_eq_mode
                }
                log(data)
                connection.request("POST", self.target, urlencode(data))
                connection.getresponse()

        except Exception as error:
            xbmc.log(ADDON_ID +': ' + str(error), xbmc.LOGERROR)

def abort_requested():
    if KODI_VERSION_MAJOR > 13:
        return monitor.abortRequested()
    return xbmc.abortRequested

def wait_for_abort(seconds):
    if KODI_VERSION_MAJOR > 13:
        return monitor.waitForAbort(seconds)
    for _ in range(0, seconds * 1000 / 200):
        if xbmc.abortRequested:
            return True
        xbmc.sleep(200)
    return False

def main():
    s = Settings()
    player = None

    while not abort_requested():
        if player is None:
            # Initialization only works with kwargs
            player = DenonControlPlayer(settings=s)
        if wait_for_abort(100):
            # Abort was requested while waiting. We should exit
            break

if __name__ == '__main__':
    main()
