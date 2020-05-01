from . import _
from Components.ActionMap import NumberActionMap, ActionMap
from Components.ConfigList import ConfigListScreen
from Components.config import config, ConfigSubList, ConfigSubsection, ConfigYesNo, getConfigListEntry, ConfigInteger, ConfigText
from Components.Harddisk import harddiskmanager
from Components.Label import Label
from Components.PluginComponent import plugins
from Components.Sources.StaticText import StaticText
from Components.Sources.Boolean import Boolean
from Components.Pixmap import Pixmap
from enigma import iServiceInformation, eTimer, eConsoleAppContainer
from Plugins.Plugin import PluginDescriptor
from Screens.Console import Console
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from youtubetv import YouTubeTvTVWindow
import os, time
import datetime

NUMBER_OF_PRESETS = 6
config.plugins.YouTubeTv = ConfigSubsection()
config.plugins.YouTubeTv.ntpurl = ConfigText(default = '')
config.plugins.YouTubeTv.showinextensions = ConfigYesNo(default = True)
config.plugins.YouTubeTv.showinmenu = ConfigYesNo(default = True)
config.plugins.YouTubeTv.autostart = ConfigYesNo(default = False)
config.plugins.YouTubeTv.egl = ConfigYesNo(default = True)
config.plugins.YouTubeTv.preset = ConfigInteger(default = 0)
config.plugins.YouTubeTv.presets = ConfigSubList()

for x in range(NUMBER_OF_PRESETS):
	preset = ConfigSubsection()
	preset.portal = ConfigText(default = 'http://')
	config.plugins.YouTubeTv.presets.append(preset)
config.plugins.YouTubeTv.presets[0].portal.value = 'https://www.youtube.com/tv'


class YouTubeTvEd(Screen, ConfigListScreen):
	skin = """
		<screen name="YouTubeTvEd" position="center,center" size="710,450" title="YouTubeTv Setup">
			<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />
			<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
			<ePixmap pixmap="skin_default/buttons/green.png" position="150,0" size="140,40" alphatest="on" />
			<widget source="key_green" render="Label" position="150,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
			<widget name="config" position="5,50" size="700,250" zPosition="1" scrollbarMode="showOnDemand" />
		</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, self.session)
		Screen.setTitle(self, _("YouTubeTv Setup"))

		self.list = []
		ConfigListScreen.__init__(self, self.list, session = self.session)
		self.loadPortals()

		self["key_red"] = StaticText(_("Cancel"))
		self["key_green"] = StaticText(_("Save"))
		self.configfound = False

		self["actions"] = NumberActionMap(["SetupActions", "ColorActions", 'VirtualKeyboardActions'],
		{
			"ok": self.ok,
			"back": self.close,
			"cancel": self.close,
			"red": self.close,
			"green": self.save,
			"showVirtualKeyboard": self.KeyText,
		}, -2)
		self["VirtualKB"].setEnabled(False)
		self.setupTimer = eTimer()
		self.setupTimer.callback.append(self.setupCallback)
		self.setupTimer.start(1)
		if not self.selectionChanged in self["config"].onSelectionChanged:
			self["config"].onSelectionChanged.append(self.selectionChanged)
		self.selectionChanged()
		self.onLayoutFinish.append(self.setWindowTitle)

	def setupCallback(self):
		pass

	def VirtualKeyBoardCallback(self, callback = None):
		if callback is not None and len(callback):
			self["config"].getCurrent()[1].setValue(callback)
			self["config"].invalidate(self["config"].getCurrent())

	def KeyText(self):
		if self["config"].getCurrentIndex() < NUMBER_OF_PRESETS:
			self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title = self["config"].getCurrent()[0], text = self["config"].getCurrent()[1].value)

	def confirmationConfig(self, result):
		if result:
			data = open(self.path, "r").read()
			if len(data):
				data = data.split('\n')
				for x in data:
					y = x.split(' ')
					if len(y) == 3:
						if y[0] == 'portal':
							config.plugins.YouTubeTv.presets[int(y[1])].portal.value = y[2]
							config.plugins.YouTubeTv.presets[int(y[1])].save()
				config.plugins.YouTubeTv.save()
				self.loadPortals()

	def selectionChanged(self):
		if self["config"].getCurrent():
			if isinstance(self["config"].getCurrent()[1], ConfigText):
				if self.has_key("VKeyIcon"):
					self["VirtualKB"].setEnabled(True)
					self["VKeyIcon"].boolean = True
				if self.has_key("HelpWindow"):
					if self["config"].getCurrent()[1].help_window and self["config"].getCurrent()[1].help_window.instance is not None:
						helpwindowpos = self["HelpWindow"].getPosition()
						from enigma import ePoint
						self["config"].getCurrent()[1].help_window.instance.move(ePoint(helpwindowpos[0],helpwindowpos[1]))
					else:
						if self.has_key("VKeyIcon"):
							self["VirtualKB"].setEnabled(False)
							self["VKeyIcon"].boolean = False
		else:
			if self.has_key("VKeyIcon"):
				self["VirtualKB"].setEnabled(False)
				self["VKeyIcon"].boolean = False


	def loadPortals(self):
		self.list = []
		self.name = []
		for x in range(NUMBER_OF_PRESETS):
			self.name.append(ConfigText(default = config.plugins.YouTubeTv.presets[x].portal.value, fixed_size = False))
			if config.plugins.YouTubeTv.preset.value == x:
				self.list.append(getConfigListEntry(">> " + _("WEB URL") + (" %d" % (x + 1)), self.name[x]))
			else:
				self.list.append(getConfigListEntry(_("WEB URL") + (" %d" % (x + 1)), self.name[x]))
		self.list.append(getConfigListEntry(_("Show YouTubeTv in Mainmenu"), config.plugins.YouTubeTv.showinmenu))
		self.list.append(getConfigListEntry(_("Start YouTubeTv with enigma2 (Autostart)"), config.plugins.YouTubeTv.autostart))
		self.list.append(getConfigListEntry(_("Use EGL Hardware acceleration"), config.plugins.YouTubeTv.egl))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def setWindowTitle(self):
		file_name = "/usr/share/netflix/html/netflix_plugin.js"
		if os.path.isfile(file_name):
			time_ob = time.localtime(os.path.getmtime(file_name))
			version = "{}.{}.{}".format(time_ob.tm_year , time_ob.tm_mon , time_ob.tm_mday)
			self.setTitle(_("YouTubeTv Setup (Version: %s)"%version))

	def ok(self):
		if self["config"].getCurrentIndex() < NUMBER_OF_PRESETS:
			self.session.openWithCallback(self.confirmationResult, MessageBox, _("Set this as default?"))

	def confirmationResult(self, result):
		if result:
			config.plugins.YouTubeTv.preset.value = self["config"].getCurrentIndex()
			for x in range(NUMBER_OF_PRESETS):
				config.plugins.YouTubeTv.presets[x].portal.value = self.name[x].value
				config.plugins.YouTubeTv.presets[x].save()
			config.plugins.YouTubeTv.save()
			self.loadPortals()

	def save(self):
		config.plugins.YouTubeTv.save()
		self.close()

def setup(session, **kwargs):
	session.open(YouTubeTvEd)

def autostart(session, **kwargs):
	global g_timerinstance
	global g_session
	g_session = session
	g_timerinstance = eTimer()
	g_timerinstance.callback.append(timerCallback)
	g_timerinstance.start(1000)

def timerCallback():
	global g_timerinstance
	global g_session
	g_timerinstance.stop()
	left = open("/proc/stb/fb/dst_left", "r").read()
	width = open("/proc/stb/fb/dst_width", "r").read()
	top = open("/proc/stb/fb/dst_top", "r").read()
	height = open("/proc/stb/fb/dst_height", "r").read()

	g_session.open(YouTubeTvTVWindow, left, top, width, height)

def main(session, **kwargs):
	left = open("/proc/stb/fb/dst_left", "r").read()
	width = open("/proc/stb/fb/dst_width", "r").read()
	top = open("/proc/stb/fb/dst_top", "r").read()
	height = open("/proc/stb/fb/dst_height", "r").read()

	session.open(YouTubeTvTVWindow, left, top, width, height)

def startMenu(menuid):
	if menuid != "mainmenu":
		return []
	return [(_("YouTubeTv"), main, "YouTubeTv Plugin", 80)]


def Plugins(**kwargs):
	from enigma import getDesktop
	if getDesktop(0).size().width() <= 1280:
		youtubetv = 'youtubetv_HD.png'
	else:
		youtubetv = 'youtubetv_FHD.png'
	menus = []
	menus.append(PluginDescriptor(name=_('YouTubeTv Setup'), description=_('YouTubeTv Setup'), where=PluginDescriptor.WHERE_PLUGINMENU, icon=youtubetv, fnc=setup))
	if config.plugins.YouTubeTv.showinextensions.value:
		menus.append(PluginDescriptor(name= _("YouTubeTv"), description = _("YouTubeTv"), where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc = main))
	if config.plugins.YouTubeTv.showinmenu.value:
		menus.append(PluginDescriptor(name=_("YouTubeTv"), description = _("YouTubeTv"), where = PluginDescriptor.WHERE_MENU, fnc = startMenu))
	if config.plugins.YouTubeTv.autostart.value:
		menus.append(PluginDescriptor(where=PluginDescriptor.WHERE_SESSIONSTART, fnc=autostart))
	return menus
