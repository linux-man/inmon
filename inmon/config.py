#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from configparser import ConfigParser

class Config():
	def __init__(self, app_name):
		self.config = ConfigParser()
		config_path = os.path.join(os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config"), app_name)
		self.config_file = os.path.join(config_path, "preferences")
		try: self.config.read(self.config_file)
		except: pass

	def load_pos(self):
		try:
			return self.config.getint("window","left"), self.config.getint("window","top")
		except: pass

	def load_prefs(self, prefs):
		try: prefs["mouse"] = self.config.getboolean("prefs","mouse")
		except: pass
		try: prefs["ctrl"] = self.config.getboolean("prefs","ctrl")
		except: pass
		try: prefs["shift"] = self.config.getboolean("prefs","shift")
		except: pass
		try: prefs["cmd"] = self.config.getboolean("prefs","cmd")
		except: pass
		try: prefs["alt"] = self.config.getboolean("prefs","alt")
		except: pass
		try: prefs["alt_gr"] = self.config.getboolean("prefs","alt_gr")
		except: pass
		try: prefs["max"] = self.config.getint("prefs","max")
		except: pass
		try: prefs["delay"] = self.config.getfloat("prefs","delay")
		except: pass
		try: prefs["clicks"] = self.config.getboolean("prefs","clicks")
		except: pass
		try: prefs["swap"] = self.config.getboolean("prefs","swap")
		except: pass
		try: prefs["decor"] = self.config.getboolean("prefs","decor")
		except: pass
		try: prefs["bg"] = self.config.getboolean("prefs","bg")
		except: pass
		try: prefs["comb"] = self.config.getboolean("prefs","comb")
		except: pass
		try: prefs["join_alt"] = self.config.getboolean("prefs","join_alt")
		except: pass
		try: prefs["scale"] = self.config.getfloat("prefs","scale")
		except: pass
		try: prefs["theme"] = self.config.get("prefs","theme")
		except: pass
		try: prefs["dark"] = self.config.getboolean("prefs","dark")
		except: pass
		try: prefs["cmd_key"] = self.config.get("prefs","cmd_key")
		except: pass
		try: prefs["backend"] = self.config.get("prefs","backend")
		except: pass

	def save_prefs(self, left, top, prefs):
		self.config["window"] = {"left": left, "top": top}
		self.config["prefs"] = prefs
		os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
		with open(self.config_file, "w") as config_file: self.config.write(config_file)
