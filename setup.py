"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app --iconfile images/appIcon.icns -O2
"""

from glob import glob
from setuptools import setup


APP = ['KNetConnect.py']
DATA_FILES = [
    ('images', glob('images/*.png'))
]
OPTIONS = {'argv_emulation': False}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
