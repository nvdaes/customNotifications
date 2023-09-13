# -*- coding: UTF-8 -*-
# customNotifications: a global plugin to customize toast notifications
# Copyright (C) 2023 Noelia Ruiz Martínez, other contributors
# Released under GPL 2

import wx
from typing import Callable

import config
import gui
from gui import guiHelper
from gui.settingsDialogs import SettingsPanel
import addonHandler

addonHandler.initTranslation()

ADDON_SUMMARY = addonHandler.getCodeAddon().manifest["summary"]

_: Callable[[str], str]


class AddonSettingsPanel(SettingsPanel):

	title = ADDON_SUMMARY

	def makeSettings(self, settingsSizer):
		sHelper = guiHelper.BoxSizerHelper(self, sizer=settingsSizer)
		# Translators: label of a dialog.
		self.truncateNotificationsCheckBox = sHelper.addItem(wx.CheckBox(self, label=_("&Truncate notifications")))
		self.truncateNotificationsCheckBox.SetValue(config.conf["customNotifications"]["truncateNotifications"])
		# Translators: label of a dialog.
		startLimitLabel = _("Type the characters to be used as the &start limit of notifications")
		self.startLimitEdit = sHelper.addLabeledControl(startLimitLabel, wx.TextCtrl)
		self.startLimitEdit.SetValue(config.conf["customNotifications"]["startLimit"])
		# Translators: label of a dialog.
		endLimitLabel = _("Type the characters to be used as the end &limit of notifications")
		self.endLimitEdit = sHelper.addLabeledControl(endLimitLabel, wx.TextCtrl)
		self.endLimitEdit.SetValue(config.conf["customNotifications"]["endLimit"])
		# Translators: label of a dialog.
		outputModesLabel = _("Sele&ct output modes for notifications")
		outputModesChoices = [
			# Translators: label of a dialog.
			_("Speech"),
			# Translators: label of a dialog.
			_("Braille"),
		]
		self.outputModesList = sHelper.addLabeledControl(
			outputModesLabel, gui.nvdaControls.CustomCheckListBox, choices=outputModesChoices
		)
		checkedItems = []
		if config.conf["customNotifications"]["speech"]:
			checkedItems.append(0)
		if config.conf["customNotifications"]["braille"]:
			checkedItems.append(1)
		self.outputModesList.CheckedItems = checkedItems
		self.outputModesList.Select(0)
		# Translators: label of a dialog.
		testLabel = _("Type the text to show a test &notification")
		self.testEdit = sHelper.addLabeledControl(testLabel, wx.TextCtrl)
		self.testEdit.Bind(wx.EVT_TEXT, self.onTestEditChange)
		buttonHelper = guiHelper.ButtonHelper(wx.VERTICAL)
		# Translators: label of a dialog.
		self.testButton = buttonHelper.addButton(self, label=_("&Show test notification"))
		self.testButton.Bind(wx.EVT_BUTTON, self.onShow)
		self.testButton.Disable()

	def onTestEditChange(self, evt):
		self.testButton.Enabled = len(self.testEdit.GetValue()) > 0

	def onShow(self, evt):
		notification = wx.adv.NotificationMessage(title=ADDON_SUMMARY, message=self.testEdit.GetValue())
		notification.Show()

	def onSave(self):
		config.conf["customNotifications"]["truncateNotifications"] = self.truncateNotificationsCheckBox.GetValue()
		config.conf["customNotifications"]["startLimit"] = self.startLimitEdit.GetValue()
		config.conf["customNotifications"]["endLimit"] = self.endLimitEdit.GetValue()
		config.conf["customNotifications"]["speech"] = self.outputModesList.IsChecked(0)
		config.conf["customNotifications"]["braille"] = self.outputModesList.IsChecked(1)
