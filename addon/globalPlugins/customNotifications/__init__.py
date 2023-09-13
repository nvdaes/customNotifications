# -*- coding: UTF-8 -*-

# customNotifications: a global plugin to customize toast notifications
# Copyright (C) 2023 Noelia Ruiz Martínez, other contributors
# Released under GPL 2

import wx
from typing import Callable

import addonHandler
import globalPluginHandler
import globalVars
import config
import controlTypes
import ui
import speech
import braille
from globalCommands import SCRCAT_CONFIG
from NVDAObjects.behaviors import Notification
from scriptHandler import script
from gui import mainFrame
from gui.settingsDialogs import NVDASettingsDialog
from typing import Dict

from .gui import ADDON_SUMMARY, AddonSettingsPanel

addonHandler.initTranslation()

_: Callable[[str], str]

confspec: Dict[str, str] = {
	"truncateNotifications": "boolean(default=True)",
	"startLimit": 'string(default="")',
	"endLimit": 'string(default=", ")',
	"speech": "boolean(default=True)",
	"braille": "boolean(default=True)",
}


def disableInSecureMode(decoratedCls):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls


@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):

	def __init__(self):
		super().__init__()
		config.conf.spec["customNotifications"] = confspec
		NVDASettingsDialog.categoryClasses.append(AddonSettingsPanel)
		self.oldEventAlert = Notification.event_alert
		Notification.event_alert = EnhancedNotification.event_alert

	def terminate(self):
		NVDASettingsDialog.categoryClasses.remove(AddonSettingsPanel)
		Notification.event_alert = self.oldEventAlert

	def onSettings(self, evt):
		mainFrame.popupSettingsDialog(NVDASettingsDialog, AddonSettingsPanel)

	@script(
		# Translators: message presented in input mode.
		description=_("Shows the %s settings.") % ADDON_SUMMARY,
		category=SCRCAT_CONFIG,
	)
	def script_settings(self, gesture):
		wx.CallAfter(self.onSettings, None)

	@script(
		# Translators: message presented in input mode.
		description=_("Toggles Truncate notifications option of %s.") % ADDON_SUMMARY,
		category=SCRCAT_CONFIG,
	)
	def script_toggleTruncate(self, gesture):
		truncateNotifications = config.conf["customNotifications"]["truncateNotifications"]
		if truncateNotifications:
			config.conf["customNotifications"]["truncateNotifications"] = False
			# Translators: message presented when truncate notifications are disabled.
			ui.message(_("Truncate notifications disabled"))
		else:
			config.conf["customNotifications"]["truncateNotifications"] = True
			# Translators: message presented when truncate notifications are enabled.
			ui.message(_("Truncate notifications enabled"))

	@script(
		# Translators: message presented in input mode.
		description=_("Toggles speech option of %s.") % ADDON_SUMMARY,
		category=SCRCAT_CONFIG,
	)
	def script_toggleSpeech(self, gesture):
		speech = config.conf["customNotifications"]["speech"]
		if speech:
			config.conf["customNotifications"]["speech"] = False
			# Translators: message presented when customNotifications speech is disabled.
			ui.message(_("Speech disabled for %s") % ADDON_SUMMARY)
		else:
			config.conf["customNotifications"]["speech"] = True
			# Translators: message presented when customNotifications speech is enabled.
			ui.message(_("Speech enabled for %s") % ADDON_SUMMARY)

	@script(
		# Translators: message presented in input mode.
		description=_("Toggles braille option of %s.") % ADDON_SUMMARY,
		category=SCRCAT_CONFIG,
	)
	def script_toggleBraille(self, gesture):
		braille = config.conf["customNotifications"]["braille"]
		if braille:
			config.conf["customNotifications"]["braille"] = False
			# Translators: message presented when customNotifications braille is disabled.
			ui.message(_("Braille disabled for %s") % ADDON_SUMMARY)
		else:
			config.conf["customNotifications"]["braille"] = True
			# Translators: message presented when customNotifications braille is enabled.
			ui.message(_("Braille enabled for %s") % ADDON_SUMMARY)


class EnhancedNotification(Notification):

	def event_alert(self):
		if not config.conf["presentation"]["reportHelpBalloons"]:
			return
		truncateNotifications = config.conf["customNotifications"]["truncateNotifications"]
		startLimit = config.conf["customNotifications"]["startLimit"]
		endLimit = config.conf["customNotifications"]["endLimit"]
		if truncateNotifications:
			if startLimit:
				self.name = self.name.split(startLimit, 1)[1]
			if endLimit:
				self.name = self.name.split(endLimit)[0]
		if config.conf["customNotifications"]["speech"]:
			speech.speakObject(self, reason=controlTypes.OutputReason.FOCUS)
		# Ideally, we wouldn't use getPropertiesBraille directly.
		if config.conf["customNotifications"]["braille"]:
			braille.handler.message(braille.getPropertiesBraille(name=self.name, role=self.role))
