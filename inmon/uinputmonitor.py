#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib
from multiprocessing import Pipe, Process

try:
	import inmon.keyboard as keyboard
	import inmon.mouse as mouse
except:
	import keyboard
	import mouse

class Monitor():
	def __init__(self, callback):
		self.pressed = []
		self.callback = callback
		keyboard.hook(self.on_keyboard)
		#Mouse hook started as a Process because of segmentation fault (core dumped) when calling Gtk.menu popup
		self.parent_conn, self.child_conn = Pipe(duplex=False)
		self.m = Process(target=self.mouse_process, args=())
		self.m.start()
		self.child_conn.close()
		GLib.io_add_watch(self.parent_conn.fileno(), GLib.IO_IN, self.read_mouse)

	def on_keyboard(self, event):
		key_code = event.name.replace(" ", "_")
		key_code = {55: "num_*", 71: "num_7", 72: "num_8", 73: "num_9", 74: "num_-", 75: "num_4",
		76: "num_5", 77: "num_6", 78: "num_+", 79: "num_1", 80: "num_2", 81: "num_3", 82: "num_0",
		83: "num_.", 96: "enter", 98: "num_/", 99: "prt_sc"}.get(int(event.scan_code), key_code)

		if key_code != "unknown":
			if key_code == "alt" and event.scan_code in [125, 126]: key_code = "cmd"
			if len(key_code) == 1: key_code = key_code.upper()
			if event.event_type == "down":
				if not(key_code in self.pressed):
					self.pressed.append(key_code)
					self.callback("keyboard", key_code, True)
			else:
				try: self.pressed.remove(key_code)
				except: pass
				self.callback("keyboard", key_code, False)

	def mouse_process(self):
		mouse.hook(self.on_mouse)
		mouse.wait(button=None)

	def read_mouse(self, source, condition):
		assert self.parent_conn.poll()
		i = self.parent_conn.recv()
		self.callback(i[0], i[1], i[2])
		return True

	def on_mouse(self, event):
		if isinstance(event, mouse.ButtonEvent):
			if event.button != "?":
				self.child_conn.send(["mouse", event.button, event.event_type == "down"])
		elif isinstance(event, mouse.MoveEvent):
				self.child_conn.send(["move", event.x, event.y])
		elif isinstance(event, mouse.WheelEvent):
				self.child_conn.send(["mouse", ("scroll_down", "scroll_up")[event.delta > 0], True])

	def quit(self):
		self.m.terminate()
