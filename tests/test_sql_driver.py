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

        self.assertIsInstance(self.db, note.sqliteDB)

    def test_sql_getItem_1(self):

        self.assertIsInstance(self.db, note.sqliteDB)

    def test_sql_searchForItem_1(self):

        self.assertIsInstance(self.db, note.sqliteDB)

    def test_sql_deleteItem_1(self):

        self.assertIsInstance(self.db, note.sqliteDB)

    def test_sql_makeBackupFile_1(self):

        self.assertIsInstance(self.db, note.sqliteDB)
