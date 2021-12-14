#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys, os, glob
import setuptools
from setuptools import setup
from subprocess import call

def find_mo_files():
    data_files = []
    for mo in glob.glob(os.path.join(MO_DIR, '*', 'inmon.mo')):
        lang = os.path.basename(os.path.dirname(mo))
        dest = os.path.join('share', 'locale', lang, 'LC_MESSAGES/')
        data_files.append((dest, [mo]))
    return data_files

PO_DIR = 'po'
MO_DIR = os.path.join('data', 'po')

def themes_files(directory):
    data_files = []
    paths = []
    for (path, directories, filenames) in os.walk(os.path.join('inmon', 'themes', directory)):
        for filename in filenames:
            print(filename)
            paths.append(os.path.join(path, filename))
    data_files.append((os.path.join('share/inmon/themes', directory), paths))
    return data_files

exec_file = 'data/inmon'
data_files = [
		('share/icons/hicolor/128x128/apps/', ['data/128/inmon.png']),
		('share/icons/hicolor/64x64/apps/', ['data/64/inmon.png']),
		('share/icons/hicolor/32x32/apps/', ['data/32/inmon.png']),
		('share/applications/', ['data/inmon.desktop']),
		('bin/', [exec_file])]

for po in glob.glob(os.path.join(PO_DIR, '*.po')):
	lang = os.path.basename(po[:-3])
	mo = os.path.join(MO_DIR, lang, 'inmon.mo')
	target_dir = os.path.dirname(mo)
	if not os.path.isdir(target_dir):
		os.makedirs(target_dir)
	try:
		return_code = call(['msgfmt', '-o', mo, po])
	except OSError:
		print('Translation not available, please install gettext')
		break
	if return_code:
		raise Warning('Error when building locales')

data_files.extend(find_mo_files())
data_files.extend(themes_files('classic'))
data_files.extend(themes_files('clear'))
data_files.extend(themes_files('modern'))
data_files.extend(themes_files('modern_2'))

setup(name='inmon',
	version='0.3',
	description='An Input Monitor',
	author='Caldas Lopes',
	author_email='joao.caldas.lopes@gmail.com',
	url='https://launchpad.net/~caldas-lopes/+archive/ppa',
	license='GPL-3',
	packages=setuptools.find_packages(),
	data_files=data_files,
	)
