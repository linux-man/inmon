#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2021 Caldas Lopes
# Inmon is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your
# option) any later version.

app_name = "Inmon"
version = "0.4"

import sys
import os
import cairo
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf, Gdk, GLib
import threading
import gettext

LOCALE_DOMAIN = "inmon"
gettext.textdomain(LOCALE_DOMAIN)
_ = gettext.gettext

home = os.path.dirname(os.path.realpath(__file__))

px_height = 64

local = __name__ == '__main__'

if local:
	from config import Config
	from preferences import Preferences
	THEME_PATH = os.path.join(home, "themes")
else:
	from inmon.config import Config
	from inmon.preferences import Preferences
	THEME_PATH = os.path.join(sys.prefix, "share", "inmon", "themes")


class Inmon(Gtk.Window):
	def __init__(self):
		super().__init__(title = app_name)
		self.set_resizable(False)
		self.connect("delete-event", self.gtk_main_quit)
		self.connect("button-press-event", self.on_button_pressed)
		self.connect("motion-notify-event", self.motion_notify_event)

# Window Movement
		self.offsetx = 0
		self.offsety = 0
		self.moving = False

# Preferences
		self.ini = Config(app_name)
		try:
			left, top = self.ini.load_pos()
			self.move(left, top)
		except: pass

		self.prefs = {"mouse": True, "ctrl": True, "shift": True, "cmd": False, "alt": False, "alt_gr": False,
		"max": 6, "delay": 1.0, "clicks": False, "swap": False, "decor": False, "bg": False, "comb": False,
		"join_alt": False, "scale": 1, "theme": "classic", "dark": False, "cmd_key":"cmd", "backend": "pynput"}

		self.ini.load_prefs(self.prefs)

		self.decorated = self.prefs["decor"]
		self.background = self.prefs["bg"]
		self.mod_pressed = 0

		self.gui()

#Monitor backend
		if self.prefs["backend"] == "uinput":
			if local:
				from uinputmonitor import Monitor
			else:
				from inmon.uinputmonitor import Monitor
		else:
			if self.prefs["backend"] == "pynputevdev":
				os.environ['PYNPUT_BACKEND_KEYBOARD'] = "uinput"
				os.environ['PYNPUT_BACKEND_MOUSE'] = "dummy"

			if local:
				from pynputmonitor import Monitor
			else:
				from inmon.pynputmonitor import Monitor

		self.mon = Monitor(self.mon_callback)

# Undecorated window, transparent background
		self.set_decorated(self.decorated)
		self.set_size_request(self.get_size()[0], self.get_size()[1])
		screen = self.get_screen()
		visual = screen.get_rgba_visual()
		if visual and screen.is_composited():
			self.set_visual(visual)

		self.set_app_paintable(not self.background)
		self.set_keep_above(True)

	def on_button_pressed(self, btn, event):
		if event.type == Gdk.EventType.BUTTON_PRESS:
			if event.button == 1:
				if self.decorated:
					self.moving = False
				else:
					self.moving = True
					self.offsetx = event.x
					self.offsety = event.y
			elif event.button == 3:
				self.menu.popup_at_pointer()
			else:
				self.moving = False

	def motion_notify_event(self, widget, event):
		if self.moving:
			x = event.x_root - self.offsetx
			y = event.y_root - self.offsety
			self.move(x, y)

	def gtk_main_quit(self, *args):
		self.mon.quit()
		self.ini.save_prefs(self.get_position()[0], self.get_position()[1], self.prefs)
		Gtk.main_quit(*args)

# Drawing interface
	def gui(self):
		def load_with_dark(pixbuf):
			if self.prefs["dark"]:
				if pixbuf.get_has_alpha():
					alpha = True
					n_bytes = 4
				else:
					alpha = False
					n_bytes = 3
				raw_pixels = bytearray(pixbuf.get_pixels())
				for n in range(len(raw_pixels)):
					if (n + 1) % 4 != 0: raw_pixels[n] = 255 - raw_pixels[n]
				return GdkPixbuf.Pixbuf.new_from_data(raw_pixels, GdkPixbuf.Colorspace.RGB, alpha, 8, pixbuf.get_width(), pixbuf.get_height(), n_bytes * pixbuf.get_width())
			else: return pixbuf

		def on_menu_prefs(widget):
			dialog = Preferences(self, app_name, version, self.prefs)
			response = dialog.run()
			if response == Gtk.ResponseType.OK:
				self.prefs["mouse"] = dialog.mouse.get_active()
				self.prefs["ctrl"] = dialog.ctrl.get_active()
				self.prefs["shift"] = dialog.shift.get_active()
				self.prefs["cmd"] = dialog.cmd.get_active()
				self.prefs["alt"] = dialog.alt.get_active()
				self.prefs["alt_gr"] = dialog.alt_gr.get_active()
				self.prefs["max"] = int(dialog.max.get_value())
				self.prefs["delay"] = round(dialog.delay.get_value(), 1)
				self.prefs["decor"] = dialog.decor.get_active()
				self.prefs["bg"] = dialog.bg.get_active()
				self.prefs["clicks"] = dialog.clicks.get_active()
				self.prefs["swap"] = dialog.swap.get_active()
				self.prefs["comb"] = dialog.comb.get_active()
				self.prefs["join_alt"] = dialog.join_alt.get_active()
				self.prefs["dark"] = dialog.dark.get_active()
				self.prefs["scale"] = round(dialog.scale.get_value(), 1)
				self.prefs["theme"] = dialog.theme_combo.get_active_id()
				self.prefs["cmd_key"] = dialog.cmd_combo.get_active_id()
				self.prefs["backend"] = dialog.backend_combo.get_active_id()
				self.gui()

			dialog.destroy()

		def on_menu_deco(widget):
			self.decorated = not self.decorated
			self.set_decorated(self.decorated)

		def on_menu_bg(widget):
			self.background = not self.background
			self.set_app_paintable(not self.background)

		def on_menu_quit(widget):
			self.gtk_main_quit()

		if not(self.prefs["mouse"] or self.prefs["ctrl"] or self.prefs["shift"] or self.prefs["cmd"]
		or self.prefs["alt"] or (self.prefs["alt_gr"] and  not self.prefs["join_alt"])): self.prefs["mouse"] = True

		try: self.box.destroy()
		except: pass

		self.resize(10, 10)
		self.set_size_request(10, 10)

		self.box = Gtk.Box(spacing = 0)
		self.add(self.box)

		height = px_height * self.prefs["scale"]
		theme_path = os.path.join(THEME_PATH, self.prefs["theme"])

# Loading images
		path = os.path.join(theme_path, "large_key.svg")
		self.pixbuf_large_key = load_with_dark(GdkPixbuf.Pixbuf.new_from_file_at_scale(path, -1, height, True))

		path = os.path.join(theme_path, "key.svg")
		self.pixbuf_key = load_with_dark(GdkPixbuf.Pixbuf.new_from_file_at_scale(path, -1, height, True))

		path = os.path.join(theme_path, "mouse-indicator.svg")
		self.pixbuf_clicks = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, -1, height / 2, True)

# Draw mouse
		if self.prefs["mouse"]:
			self.mouse_overlay = Gtk.Overlay()
			self.mouse_image_bg = Gtk.Image()
			self.mouse_image = [Gtk.Image(), Gtk.Image(), Gtk.Image(), Gtk.Image(), Gtk.Image()]
			path = os.path.join(theme_path, "mouse.svg")
			pixbuf = load_with_dark(GdkPixbuf.Pixbuf.new_from_file_at_scale(path, -1, height, True))
			self.mouse_image_bg.set_from_pixbuf(pixbuf)
			self.mouse_overlay.add(self.mouse_image_bg)
			path = os.path.join(theme_path, "left-mouse.svg")
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, -1, height, True)
			self.mouse_image[0].set_from_pixbuf(pixbuf)
			self.mouse_overlay.add_overlay(self.mouse_image[0])
			path = os.path.join(theme_path, "middle-mouse.svg")
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, -1, height, True)
			self.mouse_image[1].set_from_pixbuf(pixbuf)
			self.mouse_overlay.add_overlay(self.mouse_image[1])
			path = os.path.join(theme_path, "right-mouse.svg")
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, -1, height, True)
			self.mouse_image[2].set_from_pixbuf(pixbuf)
			self.mouse_overlay.add_overlay(self.mouse_image[2])
			path = os.path.join(theme_path, "scroll-up-mouse.svg")
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, -1, height, True)
			self.mouse_image[3].set_from_pixbuf(pixbuf)
			self.mouse_overlay.add_overlay(self.mouse_image[3])
			path = os.path.join(theme_path, "scroll-dn-mouse.svg")
			pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, -1, height, True)
			self.mouse_image[4].set_from_pixbuf(pixbuf)
			self.mouse_overlay.add_overlay(self.mouse_image[4])

			self.box.pack_start(self.mouse_overlay, True, True, 0)

# Draw fixed keys
		self.fixed = {}
		for k in ["ctrl", "shift", "cmd", "alt"]:
			if self.prefs[k]:
				self.fixed[k] = self.create_button(k, True)
				self.box.pack_start(self.fixed[k], True, True, 0)

		if self.prefs["alt_gr"] and not self.prefs["join_alt"]:
			self.fixed["alt_gr"] = self.create_button("alt_gr", True)
			self.box.pack_start(self.fixed["alt_gr"], True, True, 0)

# Temporary keys
		self.temp = []
		self.temp_keys = []
		self.temp_timers = [] # Timer
		self.temp_box = Gtk.Box(spacing = 0)
		self.box.pack_start(self.temp_box, True, True, 0)
		for n in range(self.prefs["max"]):
			self.temp.append(self.create_button(None, False))
		for bt in self.temp:
			self.temp_box.pack_start(bt, True, True, 0)

		self.box.show_all()
		try:
			for img in self.mouse_image: img.hide()
		except: pass
		for value in self.fixed.values(): value.solid.hide()
		for bt in self.temp: bt.hide()

# Menu
		self.menu = Gtk.Menu()
		self.menu.attach_to_widget(self.box)
		self.menu_prefs = Gtk.MenuItem(label = _("Preferences"))
		self.menu_prefs.connect("activate", on_menu_prefs)
		self.menu.append(self.menu_prefs)
		self.menu_deco = Gtk.CheckMenuItem(label = _("Decoration"))
		self.menu_deco.set_active(self.decorated)
		self.menu_deco.connect("activate", on_menu_deco)
		self.menu.append(self.menu_deco)
		self.menu_bg = Gtk.CheckMenuItem(label = _("Background"))
		self.menu_bg.set_active(self.background)
		self.menu_bg.connect("activate", on_menu_bg)
		self.menu.append(self.menu_bg)
		self.menu_quit = Gtk.MenuItem(label = _("Quit"))
		self.menu_quit.connect("activate", on_menu_quit)
		self.menu.append(self.menu_quit)
		self.menu.show_all()

# Visible Clicks
		if self.prefs["clicks"]:
			self.clicks = Gtk.Dialog(transient_for=self)
			self.clicks.set_app_paintable(True)
			self.clicks.set_decorated(False)
			self.clicks.set_keep_above(True)
			screen = self.get_screen()
			visual = screen.get_rgba_visual()
			if visual and screen.is_composited():
				self.clicks.set_visual(visual)

			self.clicks.resize(10, 10)
			self.clicks.set_size_request(10, 10)
			self.clicks.set_resizable(False)
			img = Gtk.Image()
			img.set_from_pixbuf(self.pixbuf_clicks)
			box = self.clicks.get_content_area()
			box.add(img)

	def create_text(self, key, color, solid):
		mod_keys = {"caps_lock": "caps lk", "num_lock": "num lk", "scroll_lock": "scr lk",
		"page_up": "pg up", "page_down": "pg dn", "print_screen": "prt sc", "insert": "ins",
		"delete": "del", "tab": "\u21B9", "backspace": "\u232B", "shift": "\u21E7",
		"space": "\u2423", "enter": "\u23CE", "up": "\u2191", "down": "\u2193",
		"left": "\u2190", "right": "\u2192", "menu": "\u2630", "cmd": "cmd"}

		cmd = {"cmd":"cmd", "win":"win", "wintext":"\u229E win", "win":"\u229E", "apple":"\u2318", "diamond":"\u2756"}

		try: mod_keys["cmd"] = cmd[self.prefs["cmd_key"]]
		except: pass

		try: key = mod_keys[key]
		except: pass

		try:
			if len(key) > 1: key = key.replace("_", " ")
		except: pass

		if self.prefs["dark"]: color = 1 - color

		surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 200)
		context = cairo.Context(surface)
		# background testing
		#context.set_source_rgba(1,1,0,1)
		#context.paint()
		fontsize= 128
		context.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
		context.set_font_size(fontsize)
		(x, y, width, height, dx, dy) = context.text_extents("AWCÇJ'")
		ratio = self.pixbuf_key.get_height() * 0.5 / height
		#print(context.text_extents(key))
		(x, y, width, height, dx, dy) = context.text_extents(key)
		context.move_to(-x, -y)
		context.set_source_rgba(color, color, color, 1)
		if solid:
			context.show_text(key)
		else:
			context.text_path(key)
			context.set_line_width(2)
			context.stroke()

		pixbuf = Gdk.pixbuf_get_from_surface(surface, 0, 0, width, height)
		return pixbuf.scale_simple((self.pixbuf_large_key.get_width() * 0.6, width * ratio)[len(key) == 1], height * ratio, GdkPixbuf.InterpType.BILINEAR)

	def create_button(self, key, fixed):
		bt = Gtk.Overlay()
		bt.img = Gtk.Image()

		if key != None:
			if len(key) > 1: bt.img.set_from_pixbuf(self.pixbuf_large_key)
			else: bt.img.set_from_pixbuf(self.pixbuf_key)

		bt.add(bt.img)

# Chars Images
		if fixed:
			bt.grayed = Gtk.Image()
			if key != None: bt.grayed.set_from_pixbuf(self.create_text(key, 0.6, True))
			bt.add_overlay(bt.grayed)

		bt.solid = Gtk.Image()
		if key != None: bt.solid.set_from_pixbuf(self.create_text(key, 0, True))
		bt.add_overlay(bt.solid)
		return bt

	def mon_callback(self, device, key, pressed): #or device="move", key=x, pressed=y
		def temp_update():
			def show_temp(n, key):
				self.temp[n].img.set_from_pixbuf((self.pixbuf_key, self.pixbuf_large_key)[len(key) > 1])
				self.temp[n].solid.set_from_pixbuf(self.create_text(key, 0, True))
				self.temp[n].show()

			def hide_temp(n):
				self.temp[n].hide()

			vis_temp_keys = self.temp_keys[-self.prefs["max"]:]
			for n in range(self.prefs["max"]):
				if n < (len(vis_temp_keys)): GLib.idle_add(show_temp, n, vis_temp_keys[n])
				else: GLib.idle_add(hide_temp, n)


		def fixed_key(key, pressed):
			if pressed: GLib.idle_add(self.fixed[key].solid.show)
			else: GLib.idle_add(self.fixed[key].solid.hide)

		def click(n, pressed):
			try:
				if pressed: GLib.idle_add(self.mouse_image[n].show)
				else: GLib.idle_add(self.mouse_image[n].hide)
			except: pass

		def del_scroll(key):
			click(key, False)

		def rem_temp_key(key):
			try: self.temp_keys.remove(key)
			except: pass
			temp_update()

		def clicks(pressed):
			try:
				if pressed:
					t = threading.Timer(0.1, clicks, args = (False,))
					t.start()
				else:
					GLib.idle_add(self.clicks.move, self.mouse_x, self.mouse_y)
					GLib.idle_add(self.clicks.show_all)
					t = threading.Timer(0.3, GLib.idle_add, args = (self.clicks.hide,))
					t.start()
			except: pass

# Visible Clicks
		if self.prefs["clicks"] and device == "move":
			delta = px_height / 4 * self.prefs["scale"]
			self.mouse_x = key - delta
			self.mouse_y = pressed - delta

		if device == "mouse":
			mouse = (["left", "middle", "right", "scroll_up", "scroll_down"],
			["right", "middle", "left", "scroll_up", "scroll_down"])[self.prefs["swap"]]

			index = mouse.index(key)
			click(index, pressed)
			if self.prefs["clicks"] and pressed and index < 3: clicks(pressed)
			if "scroll" in key:
				t = threading.Timer(0.5, del_scroll, args = (index,))
				t.start()

		if device == "keyboard":
# Count modifiers
			if key in ["ctrl", "shift", "cmd", "alt", "alt_gr"]:
				if pressed: self.mod_pressed += 1
				else: self.mod_pressed -= 1

			if key == "alt_gr" and self.prefs["join_alt"]: key = "alt"
			if key in self.fixed: fixed_key(key, pressed)
			else :
				if pressed:
					if not self.prefs["comb"] or (self.prefs["comb"] and self.mod_pressed > 0): self.temp_keys.append(key)
				else:
					try:
						if self.prefs["delay"] == 0: self.temp_keys.remove(key)
						else:
							t = threading.Timer(self.prefs["delay"], rem_temp_key, args = (key,))
							t.start()
					except: pass

				temp_update()

class run:
	def __init__(self):
		app = Inmon()
		app.connect("destroy", Gtk.main_quit)
		app.show()
		Gtk.main()

if local:
	run()
