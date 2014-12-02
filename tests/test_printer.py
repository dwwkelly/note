#!/usr/bin/env python

__author__ = "Devin Kelly"

import unittest
import note
import sys
import json
from StringIO import StringIO
from note import colors


class NotePrinterTest(unittest.TestCase):

    def setUp(self):
        self.printer = note.Note_Printer()
        self.output = StringIO()
        self.saved_stdout = sys.stdout
        sys.stdout = self.output

    def tearDown(self):
        self.output.close()
        sys.stdout = self.saved_stdout

    def test_printer_search_1(self):

        msg = {"status": "OK",
               "object": {"received search": "asd",
                          "results": [{"score": 1.1,
                                       "obj": {"note": "asd",
                                               "tags": ["123"],
                                               "ID": 18,
                                               "timestamps": [1417140705.90]},
                                       "itemType": "note"}]},
               "type": "search"}

        self.printer(json.dumps(msg))

        expected = "{fblue}18 {hicolor}{fred}Thu, Nov 27{reset}: asd\n"
        expected = expected.format(fblue=colors['foreground blue'],
                                   hicolor=colors['hicolor'],
                                   fred=colors['foreground red'],
                                   reset=colors['reset'])

        self.assertEqual(self.output.getvalue(), expected)
        self.assertIsInstance(self.printer, note.Note_Printer)

    def test_printer_search_2(self):

        msg = {"status": "OK",
               "object": {"received search": "asd",
                          "results": [{"score": 1.1,
                                       "obj": {"note": "asd",
                                               "tags": ["123"],
                                               "ID": 18,
                                               "timestamps": [1411105705.9]},
                                       "itemType": "note"},
                                      {"score": 1.4,
                                      "obj": {"note": "asd 2",
                                              "tags": ["123"],
                                              "ID": 1,
                                              "timestamps": [1411105605.9]},
                                       "itemType": "note"}
                                      ]},
               "type": "search"}

        self.printer(json.dumps(msg))

        expected_1 = "{fblue}18 {hicolor}{fred}Fri, Sep 19{reset}: asd\n"
        expected_1 = expected_1.format(fblue=colors['foreground blue'],
                                       hicolor=colors['hicolor'],
                                       fred=colors['foreground red'],
                                       reset=colors['reset'])
        expected_2 = "{fblue}1 {hicolor}{fred}Fri, Sep 19{reset}: asd 2\n"
        expected_2 = expected_2.format(fblue=colors['foreground blue'],
                                       hicolor=colors['hicolor'],
                                       fred=colors['foreground red'],
                                       reset=colors['reset'])

        expected = expected_1 + expected_2
        self.assertEqual(self.output.getvalue(), expected)
        self.assertIsInstance(self.printer, note.Note_Printer)

    def test_error_1(self):

        msg = {"status": "ERROR",
               "object": {"msg": "test message"},
               "type": "search"}

        self.printer(json.dumps(msg))

        s = "{0}ERROR: {1}{2}\n"
        s = s.format(colors['foreground red'],
                     colors['foreground black'],
                     msg['object']['msg'])

        self.assertEqual(self.output.getvalue(), s)

    def test_OK_1(self):
        msg = {"status": "OK",
               "object": {"received search": "asd",
                          "results": [{"score": 1.1,
                                       "obj": {"note": "asd",
                                               "tags": ["123"],
                                               "ID": 18,
                                               "timestamps": [1417140705.90]},
                                       "itemType": "note"}]},
               "type": "WRONG"}

        rval = self.printer(json.dumps(msg))

        self.assertEqual(self.output.getvalue(), '')
        self.assertEqual(rval, None)
