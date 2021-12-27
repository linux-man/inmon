#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#from pprint import pprint

try:
	from inmon.pynput import keyboard
	from inmon.pynput import mouse
except:
	from pynput import keyboard
	from pynput import mouse

class Monitor():
	def __init__(self, callback):
		self.pressed = []
		self.callback = callback
		self.k_listener = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
		self.k_listener.start()
		self.m_listener = mouse.Listener(on_click=self.on_click, on_scroll=self.on_scroll, on_move=self.on_move)
		self.m_listener.start()
		#pprint(vars(keyboard.Key))


	def decode_key(self, key):
		#pprint(vars(key))
		key_code = None
		if hasattr(key, "char"):
			if key.char != None:
				key_code = key.char.upper()
				if not hasattr(key, "_kernel_name") and hasattr(key, "vk") and key.vk == None: key_code = "num_" + key_code
			elif hasattr(key, "vk") and key.vk != None:
				if hasattr(key, "_kernel_name"): # uinput backend
					key_code = {55: "num_*", 71: "num_7", 72: "num_8", 73: "num_9", 74: "num_-", 75: "num_4",
					76: "num_5", 77: "num_6", 78: "num_+", 79: "num_1", 80: "num_2", 81: "num_3", 82: "num_0",
					83: "num_.", 96: "enter", 98: "num_/", 127: "menu"}.get(int(key.vk), key_code)

				key_code = {65027: "alt_gr", 65437: "num_5", 65056: "tab"}.get(int(key.vk), key_code)

		elif hasattr(key, "_name_"):
			key_code = key._name_

		try: # key_code can still be None
			if key_code == "alt_r": key_code = "alt_gr"
			if key_code[-2:] == "_r" or key_code[-2:] == "_l": key_code = key_code[0:-2] # Normalize _r keys
		except: pass
		return key_code

	def on_press(self, key):
		key_code = self.decode_key(key)
		if key_code != None and not(key_code in self.pressed):
			self.pressed.append(key_code)
			self.callback("keyboard", key_code, True)

	def on_release(self, key):
		key_code = self.decode_key(key)
		if key_code != None:
			try: self.pressed.remove(key_code)
			except: pass
			self.callback("keyboard", key_code, False)

	def on_click(self, x, y, button, pressed):
		self.callback("mouse", button._name_, pressed)

	def on_scroll(self, x, y, dx, dy):
		self.callback("mouse", ("scroll_down", "scroll_up")[dy > 0], True)

	def on_move(self, x, y):
		self.callback("move", x, y)

	def quit(self):
		pass
