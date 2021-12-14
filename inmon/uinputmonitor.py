#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Another backend (incomplete)
# Waiting for https://github.com/boppreh/mouse fixed
try:
	import inmon.keyboard
	import inmon.mouse
except:
	import keyboard
	import mouse

class Monitor():
	def __init__(self, callback):
		self.pressed = []
		self.callback = callback
		keyboard.hook(self.on_keyboard)
		mouse.hook(self.on_mouse)

	def on_keyboard(self, event):
		key_code = event.name.replace(" ", "_")
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

	def on_mouse(self, event):
		if isinstance(event, mouse.ButtonEvent):
			if event.button != "?":
				self.callback("mouse", event.button, event.event_type == "down")
