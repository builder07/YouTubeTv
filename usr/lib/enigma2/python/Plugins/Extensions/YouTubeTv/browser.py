import os
import struct
from enigma import eConsoleAppContainer, getDesktop
from Components.VolumeControl import VolumeControl
from Components.config import config
import datasocket


class Browser:
    def __init__(self):
        self.onUrlChanged = []
        self.onUrlInfoChanged = []
        self.onMediaUrlChanged = []
        self.onExit = []
        self.onStopPlaying = []
        self.onPausePlaying = []
        self.onResumePlaying = []
        self.onSkip = []
        self.commandserver = None

    def connectedClients(self):
        return self.commandserver.connectedClients()

    def start(self):
        if not self.commandserver:
            size_w = getDesktop(0).size().width()
            size_h = getDesktop(0).size().height()
            self.commandserver = datasocket.CommandServer()
            datasocket.onCommandReceived.append(self.onCommandReceived)
            datasocket.onBrowserClosed.append(self.onBrowserClosed)
            container = eConsoleAppContainer()
            if config.plugins.YouTubeTv.egl.value == True:
                container.execute("/usr/share/netflix/prepare.sh;export LD_LIBRARY_PATH=/usr/share/netflix/lib/hisi3798mv200/:/usr/share/netflix/lib/hisi3798mv200/nss:/usr/share/netflix/;netflix --user-agent='Mozilla/5.0 (SMART-TV; Linux; Tizen 5.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/2.2 Chrome/63.0.3239.84 TV Safari/537.36' --no-sandbox --no-zygote --ozone-platform=egl --enable-spatial-navigation %s"%config.plugins.YouTubeTv.presets[config.plugins.YouTubeTv.preset.value].portal.value)
            else:
                container.execute("/usr/share/netflix/prepare.sh;export LD_LIBRARY_PATH=/usr/share/netflix/lib/hisi3798mv200/:/usr/share/netflix/lib/hisi3798mv200/nss:/usr/share/netflix/;netflix --user-agent='Mozilla/5.0 (SMART-TV; Linux; Tizen 5.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/2.2 Chrome/63.0.3239.84 TV Safari/537.36' --no-sandbox --no-zygote --disable-gpu --enable-spatial-navigation %s"%config.plugins.YouTubeTv.presets[config.plugins.YouTubeTv.preset.value].portal.value)

    def stop(self):
        if self.commandserver:
            self.commandserver = None

    def onCommandReceived(self, cmd, data):
        if cmd == 1000:
            for x in self.onMediaUrlChanged:
                x(data)
        elif cmd == 1001:
            for x in self.onStopPlaying:
                x()
        elif cmd == 1002:
            # pause
            for x in self.onPausePlaying:
                x()
        elif cmd == 1003:
            # resume
            for x in self.onResumePlaying:
                x()
        elif cmd == 1005:
            for x in self.onSkip:
                x(struct.unpack('!I', data))
        elif cmd == 1100:
            VolumeControl.instance and VolumeControl.instance.volUp()
        elif cmd == 1101:
            VolumeControl.instance and VolumeControl.instance.volDown()
        elif cmd == 1102:
            VolumeControl.instance and VolumeControl.instance.volMute()
        elif cmd == 1999:
            for x in self.onExit:
                x()

    def onBrowserClosed(self):
        self.commandserver = None
        for x in self.onExit:
            x()

    def sendCommand(self, cmd, data=''):
        if self.commandserver is not None:
            self.commandserver.sendCommand(cmd, data)

    def sendUrl(self, url):
        pass

    def StopMediaPlayback(self):
        if config.plugins.Stalker.boxkey.value == True:
            self.sendCommand(1002)
        else:
            self.sendCommand(5)
