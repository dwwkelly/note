# -*- coding: utf-8 -*-

__author__ = 'Devin Kelly'
__email__ = 'dwwkelly@fastmail.fm'
__version__ = '0.2'

from server import Note_Server
from client import Note_Client

from util import which
from util import scrubID

from mongo_driver import mongoDB

from note_printer import Note_Printer

assert mongoDB
assert which
assert scrubID
assert Note_Client
assert Note_Server
assert Note_Printer
