# -*- coding: UTF-8 -*-
# customNotifications: a global plugin to customize toast notifications
# Copyright (C) 2023 Noelia Ruiz Martínez, other contributors
# Released under GPL 2

import wx

import addonHandler
import globalPluginHandler
import config
import controlTypes
import speech
import braille
from globalCommands import SCRCAT_CONFIG
from NVDAObjects.behaviors import Notification
from scriptHandler import script
from gui import NVDASettingsDialog, mainFrame
from typing import Dict

from .gui import ADDON_SUMMARY, AddonSettingsPanel

addonHandler.initTranslation()

confspec: Dict[str, str] = {
	"truncateNotifications": "boolean(default=True)",
	"endLimit": 'string(default=", ")',
	"speech": "boolean(default=True)",
	"braille": "boolean(default=True)",
}


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
		mainFrame._popupSettingsDialog(NVDASettingsDialog, AddonSettingsPanel)

	@script(
		# Translators: message presented in input mode.
		description=_("Shows the %s settings.") % ADDON_SUMMARY,
		category=SCRCAT_CONFIG,
	)
	def script_settings(self, gesture):
		wx.CallAfter(self.onSettings, None)


class EnhancedNotification(Notification):	

	def event_alert(self):
		if not config.conf["presentation"]["reportHelpBalloons"]:
			return
		truncateNotifications = config.conf["customNotifications"]["truncateNotifications"]
		endLimit = config.conf["customNotifications"]["endLimit"]
		if truncateNotifications and endLimit:
			self.name = self.name.split(endLimit)[0]
		if config.conf["customNotifications"]["speech"]:
			speech.speakObject(self, reason=controlTypes.OutputReason.FOCUS)
		# Ideally, we wouldn't use getPropertiesBraille directly.
		if config.conf["customNotifications"]["braille"]:
			braille.handler.message(braille.getPropertiesBraille(name=self.name, role=self.role))
