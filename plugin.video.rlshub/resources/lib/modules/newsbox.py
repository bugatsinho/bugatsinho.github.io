# -*- coding: utf-8 -*-

import pyxbmct, re
from resources.lib.modules import control, client
from random import choice

ADDON = control.addon()
FANART = ADDON.getAddonInfo('fanart')
ICON = ADDON.getAddonInfo('icon')
NAME = ADDON.getAddonInfo('name')

class Prompt(pyxbmct.AddonDialogWindow):

    def __init__(self):

        # noinspection PyArgumentList
        super(Prompt, self).__init__('ReleseBB News - Updates - Help')

        self.changelog_button = None
        self.disclaimer_button = None
        self.close_button = None
        self.external_label = None
        self.description = None
        self.donation_button = None
        self.debrid_button = None
        self.facebook_button = None
        self.twitter_button = None
        self.setGeometry(854, 480, 8, 5)
        self.set_controls()
        self.connect(pyxbmct.ACTION_NAV_BACK, self.close)
        self.set_navigation()

    def set_controls(self):

        image = pyxbmct.Image(FANART, aspectRatio=2)
        self.placeControl(image, 0, 0, 5, 5)
        # Note
        self.description = pyxbmct.Label('Developer: Bugatsinho', alignment=2)
        self.placeControl(self.description, 5, 0, 2, 5)
        # Telegram Button
        self.tele_button = pyxbmct.Button('[COLOR gold]Telegram Link[/COLOR]')
        self.placeControl(self.tele_button, 6, 0, 1, 1)
        self.connect(self.tele_button, lambda: control.open_web_browser('http://bit.ly/bug_telegram'))
        # Paypal button
        self.debrid_button = pyxbmct.Button('[COLOR gold]RDebrid Link[/COLOR]')
        self.placeControl(self.debrid_button, 6, 1, 1, 1)
        self.connect(self.debrid_button, lambda: control.open_web_browser('http://bit.ly/RDedlink'))
        # Donation button
        self.donation_button = pyxbmct.Button('[COLOR gold]Donation Link[/COLOR]')
        self.placeControl(self.donation_button, 6, 2, 1, 1)
        self.connect(self.donation_button, lambda: control.open_web_browser('https://pastebin.com/raw/9J1KGKsj'))
        # Twitter button
        self.twitter_button = pyxbmct.Button('[COLOR gold]Twitter Link[/COLOR]')
        self.placeControl(self.twitter_button, 6, 3, 1, 1)
        self.connect(self.twitter_button, lambda: control.open_web_browser('https://twitter.com/bugatsinho'))
        # GitHub button
        self.github_button = pyxbmct.Button('[COLOR gold]GitHub Link[/COLOR]')
        self.placeControl(self.github_button, 6, 4, 1, 1)
        self.connect(self.github_button, lambda: control.open_web_browser('https://github.com/bugatsinho/bugatsinho.github.io/tree/master/plugin.video.rlshub'))
        # Close button
        self.close_button = pyxbmct.Button('[COLOR gold]CLOSE[/COLOR]')
        self.placeControl(self.close_button, 7, 2)
        self.connect(self.close_button, self.close)
        # Changelog button
        self.changelog_button = pyxbmct.Button('[COLOR gold]NEWS & UPDATES[/COLOR]')
        self.placeControl(self.changelog_button, 7, 0, 1, 2)
        self.connect(self.changelog_button, lambda: news())#https://pastebin.com/raw/mpgxNy2V
        # Disclaimer button
        self.disclaimer_button = pyxbmct.Button('[COLOR gold]DISCLAIMER[/COLOR]')
        self.placeControl(self.disclaimer_button, 7, 3, 1, 2)
        self.connect(self.disclaimer_button, lambda: disclaimer())

    def set_navigation(self):
        self.tele_button.controlRight(self.debrid_button)
        self.tele_button.controlDown(self.changelog_button)

        self.donation_button.controlRight(self.twitter_button)
        self.donation_button.controlDown(self.close_button)
        self.donation_button.controlLeft(self.debrid_button)

        self.debrid_button.controlLeft(self.tele_button)
        self.debrid_button.controlDown(self.close_button)
        self.debrid_button.controlRight(self.donation_button)

        self.github_button.controlDown(self.disclaimer_button)
        self.github_button.controlLeft(self.twitter_button)

        self.twitter_button.controlLeft(self.donation_button)
        self.twitter_button.controlDown(self.disclaimer_button)
        self.twitter_button.controlRight(self.github_button)


        self.close_button.controlLeft(self.changelog_button)
        self.close_button.controlRight(self.disclaimer_button)
        self.close_button.controlUp(self.donation_button)

        self.changelog_button.controlRight(self.close_button)
        self.changelog_button.controlUp(self.donation_button)

        self.disclaimer_button.controlLeft(self.close_button)
        self.disclaimer_button.controlUp(choice([self.github_button, self.twitter_button]))

        self.setFocus(self.close_button)


def welcome():

    window = Prompt()
    window.doModal()

    del window


def disclaimer():

    try:
        text = control.addonInfo('disclaimer').decode('utf-8')
    except (UnicodeEncodeError, UnicodeDecodeError, AttributeError):
        text = control.addonInfo('disclaimer')

    control.dialog.textviewer(control.addonInfo('name') + ' ' + 'Disclaimer', text)


def news():
    _news = client.request('https://pastebin.com/raw/mpgxNy2V')
    control.dialog.textviewer(control.addonInfo('name') + ' ' + 'News & Updates', _news.encode('utf-8'))
