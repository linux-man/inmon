#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import gettext

LOCALE_DOMAIN = "inmon"
gettext.textdomain(LOCALE_DOMAIN)
_ = gettext.gettext

class Preferences(Gtk.Dialog):
	def __init__(self, parent, app_name, version, prefs):
		super().__init__(title = _("Preferences"), transient_for = parent, flags = 0)
		self.app_name = app_name
		self.version = version
		self.add_buttons(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK)
		self.notebook = Gtk.Notebook()

		self.page1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, border_width = 10)

		self.mouse = Gtk.CheckButton(label = _("Mouse"), active = prefs["mouse"])
		self.ctrl = Gtk.CheckButton(label = _("Control"), active = prefs["ctrl"])
		self.shift = Gtk.CheckButton(label = _("Shift"), active = prefs["shift"])
		self.cmd = Gtk.CheckButton(label = _("Cmd"), active = prefs["cmd"])
		self.alt = Gtk.CheckButton(label = _("Alt"), active = prefs["alt"])
		self.alt_gr = Gtk.CheckButton(label = _("Alt Gr"), active = prefs["alt_gr"])

		grid = Gtk.Grid(column_spacing = 10, row_spacing = 10)

		grid.add(Gtk.Label(_("Max Keys")))

		self.max = Gtk.SpinButton()
		self.max.configure(Gtk.Adjustment(prefs["max"], 1.0, 12.0, 1.0, 2.0, 0.0), 0, 0)
		grid.attach(self.max, 1, 0, 1, 1)

		grid.attach(Gtk.Label(_("Key Delay")), 0, 1, 1, 1)

		self.delay = Gtk.SpinButton()
		self.delay.configure(Gtk.Adjustment(prefs["delay"], 0.0, 4.0, 0.1, 0.5, 0.0), 0, 1)
		grid.attach(self.delay, 1, 1, 1, 1)

		self.decor = Gtk.CheckButton(label = _("Window Decoration"), active = prefs["decor"])
		self.bg = Gtk.CheckButton(label = _("Window Background"), active = prefs["bg"])

		self.page1.add(self.mouse)
		self.page1.add(self.ctrl)
		self.page1.add(self.shift)
		self.page1.add(self.cmd)
		self.page1.add(self.alt)
		self.page1.add(self.alt_gr)
		self.page1.add(grid)
		self.page1.add(self.decor)
		self.page1.add(self.bg)
		self.notebook.append_page(self.page1, Gtk.Label(_("Show")))

		self.page2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, border_width = 10)

		self.clicks = Gtk.CheckButton(label = _("Visible Clicks"), active = prefs["clicks"])
		self.swap = Gtk.CheckButton(label = _("Swap Mouse Buttons"), active = prefs["swap"])
		self.comb = Gtk.CheckButton(label = _("Only Show Key Combinations"), active = prefs["comb"])
		self.join_alt = Gtk.CheckButton(label = _("Alt Gr = Alt"), active = prefs["join_alt"])
		self.dark = Gtk.CheckButton(label = _("Dark Mode"), active = prefs["dark"])

		grid = Gtk.Grid(column_spacing = 10, row_spacing = 10)

		grid.add(Gtk.Label(_("Scale")))

		self.scale = Gtk.SpinButton()
		self.scale.configure(Gtk.Adjustment(prefs["scale"], 0.5, 4.0, 0.1, 0.5, 0.0), 0, 1)
		grid.attach(self.scale, 1, 0, 1, 1)

		grid.attach(Gtk.Label(_("Theme")), 0, 1, 1, 1)

		self.theme_combo = Gtk.ComboBoxText()
		self.theme_combo.append("classic", _("Classic"))
		self.theme_combo.append("clear", _("Clear"))
		self.theme_combo.append("modern", _("Modern"))
		self.theme_combo.append("modern_2", _("Modern 2"))
		self.theme_combo.set_active_id(prefs["theme"])
		grid.attach(self.theme_combo, 1, 1, 1, 1)

		grid.attach(Gtk.Label(_("Cmd Key")), 0, 2, 1, 1)

		self.cmd_combo = Gtk.ComboBoxText()
		self.cmd_combo.append("cmd", "Cmd")
		self.cmd_combo.append("win", "Win")
		self.cmd_combo.append("wintext", "\u229E Win")
		self.cmd_combo.append("win", "\u229E")
		self.cmd_combo.append("apple", "\u2318")
		self.cmd_combo.append("diamond", "\u2756")
		self.cmd_combo.set_active_id(prefs["cmd_key"])
		grid.attach(self.cmd_combo, 1, 2, 1, 1)

		self.page2.add(self.clicks)
		self.page2.add(self.swap)
		self.page2.add(self.comb)
		self.page2.add(self.join_alt)
		self.page2.add(self.dark)
		self.page2.add(grid)
		self.notebook.append_page(self.page2, Gtk.Label(_("Misc")))

		self.page3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, border_width = 10)

		grid = Gtk.Grid(column_spacing = 10, row_spacing = 10)
		grid.add(Gtk.Label(_("Backend")))

		self.backend_combo = Gtk.ComboBoxText()
		self.backend_combo.append("pynput", "pynput")
		self.backend_combo.append("pynputevdev", "pynput-evdev")
		self.backend_combo.set_active_id(prefs["backend"])

		grid.attach(self.backend_combo, 1, 0, 1, 1)
		self.page3.add(grid)
		self.page3.add(Gtk.Label(_("Restart the application to activate the changes.")))
		self.page3.add(Gtk.Label(""))
		l = Gtk.Label(_("For Wayland, use 'pynput-evdev'. No mouse support. Install 'python3-evdev'. You must be a member of 'input' and 'tty' groups to access /dev/input: 'sudo usermod -a -G input tty USERNAME'"))
		l.set_line_wrap(True)
		l.set_max_width_chars(20)
		self.page3.add(l)
		if platform.system() == "Linux": self.notebook.append_page(self.page3, Gtk.Label(_("Interface")))

		self.page4 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, border_width = 10)

		l = Gtk.Label()
		l.set_markup("<b>" + self.app_name + "</b>")
		self.page4.add(l)
		self.page4.add(Gtk.Label(_("An Input Monitor.")))
		self.page4.add(Gtk.Label(""))

		l = Gtk.Label()
		l.set_markup("<i>" + _("Version") + " " + self.version + "</i>")
		self.page4.add(l)

		self.page4.add(Gtk.Label(""))
		self.page4.add(Gtk.Label("Copyright 2021 Caldas Lopes"))
		self.page4.add(Gtk.Label(""))

		l = Gtk.Label(_("This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version."))
		l.set_line_wrap(True)
		l.set_max_width_chars(20)
		self.page4.add(l)

		self.notebook.append_page(self.page4, Gtk.Label(_("Credits")))

		box = self.get_content_area()
		box.add(self.notebook)
		self.show_all()
