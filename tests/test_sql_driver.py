#!/usr/bin/env python

__author__ = "Devin Kelly"

import unittest
import note


class NoteSQLDBTest(unittest.TestCase):

    def setUp(self):

        self.db = note.sqliteDB()

    def test_sql_init_1(self):

        self.assertIsInstance(self.db, note.sqliteDB)

    def test_sql_addItem_1(self):
        self.db.addItem("note", {"note": "this is a test note",
                                 "tags": ["one", "two"]})

        self.assertIsInstance(self.db, note.sqliteDB)

    def test_sql_getItem_1(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})

        itemContents = self.db.getItem(1)

        self.assertEqual(itemContents, None)
        self.assertIsInstance(self.db, note.sqliteDB)

    def test_sql_searchForItem_1(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})

        results = self.db.searchForItem("one")

        self.assertEqual(results, None)
        self.assertIsInstance(self.db, note.sqliteDB)

    def test_sql_deleteItem_1(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})

        reply = self.db.deleteItem(1)

        self.assertEqual(reply, None)
        self.assertIsInstance(self.db, note.sqliteDB)

    def test_sql_makeBackupFile_1(self):

        self.db.makeBackupFile()

        self.assertIsInstance(self.db, note.sqliteDB)
