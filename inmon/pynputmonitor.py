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
					if int(key.vk) == 55: key_code = "num_*"
					if int(key.vk) == 71: key_code = "num_7"
					if int(key.vk) == 72: key_code = "num_8"
					if int(key.vk) == 73: key_code = "num_9"
					if int(key.vk) == 74: key_code = "num_-"
					if int(key.vk) == 75: key_code = "num_4"
					if int(key.vk) == 76: key_code = "num_5"
					if int(key.vk) == 77: key_code = "num_6"
					if int(key.vk) == 78: key_code = "num_+"
					if int(key.vk) == 79: key_code = "num_1"
					if int(key.vk) == 80: key_code = "num_2"
					if int(key.vk) == 81: key_code = "num_3"
					if int(key.vk) == 82: key_code = "num_0"
					if int(key.vk) == 83: key_code = "num_."
					if int(key.vk) == 96: key_code = "enter"
					if int(key.vk) == 98: key_code = "num_/"
					if int(key.vk) == 127: key_code = "menu"
				if int(key.vk) == 65027: key_code = "alt_gr"
				if int(key.vk) == 65437: key_code = "num_5" # num 5
				if int(key.vk) == 65056: key_code = "tab" # shift+tab

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
		if dy > 0: self.callback("mouse", "scroll_down", True)
		else: self.callback("mouse", "scroll_up", True)

	def on_move(self, x, y):
		self.callback("move", x, y)
