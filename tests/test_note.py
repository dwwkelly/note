#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_note
----------------------------------

Tests for `note` module.
"""

import os
import unittest
import subprocess as SP

from note import which
from note import scrubID


class TestNote(unittest.TestCase):

    def setUp(self):
        pass

    def test_something(self):
        pass

    def tearDown(self):
        pass

    def test_scrub_id_1(self):

        ID = scrubID(['13'])

        self.assertEqual(13, ID)

    def test_scrub_id_2(self):

        ID = scrubID([13])

        self.assertEqual(13, ID)

    def test_scrub_id_3(self):

        ID = scrubID('13')

        self.assertEqual(13, ID)

    def test_which_1(self):

        devnull = open(os.devnull, 'w')
        which_output = SP.call(['which', 'ls'],
                               stderr=devnull,
                               stdout=devnull)
        which_output = (which_output == 0)
        exists = which('ls')
        self.assertEqual(exists, which_output)
        devnull.close()

    def test_which_2(self):

        devnull = open(os.devnull, 'w')

        which_output = SP.call(['which', 'I_HOPE_THIS_DOES_NOT_EXIST'],
                               stderr=devnull)
        which_output = (which_output == 0)
        exists = which('I_HOPE_THIS_DOES_NOT_EXIST')

        self.assertEqual(exists, which_output)
