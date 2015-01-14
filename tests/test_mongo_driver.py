#!/usr/bin/env python

__author__ = "Devin Kelly"

import unittest
import note
import time
import os
import sys


class NoteDBTest(unittest.TestCase):

    def setUp(self):
        self.db = note.mongoDB('noteTest')

    def tearDown(self):
        self.db.client.drop_database("noteTest")

    def test_mongodb_create_1(self):

        assert self.db.noteDB['IDs'].find({"currentMax": 0}).count() == 1
        assert self.db.noteDB['IDs'].find({"unusedIDs": []}).count() == 1
        assert self.db.noteDB['IDs'].find().count() == 2

    def test_mongodb_create_2(self):

        self.db = note.mongoDB('noteTest', "mongodb://localhost:27017")
        assert self.db.noteDB['IDs'].find({"currentMax": 0}).count() == 1
        assert self.db.noteDB['IDs'].find({"unusedIDs": []}).count() == 1
        assert self.db.noteDB['IDs'].find().count() == 2

    def test_mongodb_addItem_1(self):
        self.db.addItem("note", {"note": "this is a test note",
                                 "tags": ["one", "two"]})

        result = {"note": "this is a test note"}
        assert self.db.noteDB['note'].find(result).count() == 1
        assert self.db.noteDB['note'].find().count() == 1

        assert self.db.noteDB['IDs'].find({"currentMax": 1}).count() == 1
        assert self.db.noteDB['IDs'].find({"unusedIDs": []}).count() == 1
        assert self.db.noteDB['IDs'].find().count() == 2

    def test_mongodb_addItem_2(self):
        self.db.addItem("note", {"note": "this is a test note",
                                 "tags": ["one", "two"]})
        result = {"note": "this is a test note"}
        assert self.db.noteDB['note'].find(result).count() == 1
        assert self.db.noteDB['note'].find().count() == 1

        self.db.addItem("note", {"note": "this is a second test note",
                                 "tags": ["three", "four"]}, 1)

        result = {"note": "this is a second test note"}
        assert self.db.noteDB['note'].find(result).count() == 1
        result = {"tags": ["three", "four"]}
        assert self.db.noteDB['note'].find(result).count() == 1

        assert self.db.noteDB['note'].find().count() == 1
        assert self.db.noteDB['IDs'].find({"currentMax": 1}).count() == 1
        assert self.db.noteDB['IDs'].find({"unusedIDs": []}).count() == 1
        assert self.db.noteDB['IDs'].find().count() == 2

    def test_mongodb_getItem(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})

        itemContents = self.db.getItem(1)
        assert itemContents['note'] == 'ONE'
        assert itemContents['tags'][0] == 'one'
        assert len(itemContents['tags']) == 1
        itemContents = self.db.getItem(2)

        assert itemContents['note'] == 'TWO'
        assert itemContents['tags'][0] == 'two'
        assert len(itemContents['tags']) == 1

    def test_mongodb_getItemType(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})
        self.db.addItem("todo", {"todoText": "get this done",
                                 "done": "False",
                                 "date": "03 24 14"})

        itemType = self.db.getItemType(1)
        assert itemType == "note"

        itemType = self.db.getItemType(2)
        assert itemType == "note"

        itemType = self.db.getItemType(3)
        assert itemType == "todo"

    def test_mongodb_deleteItem_1(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})

        assert self.db.noteDB['note'].find({"note": "ONE"}).count() == 1
        assert self.db.noteDB['note'].find({"note": "TWO"}).count() == 1

        self.db.deleteItem(2)

        assert self.db.noteDB['note'].find({"note": "ONE"}).count() == 1
        assert self.db.noteDB['note'].find({"note": "TWO"}).count() == 0

        assert self.db.noteDB['note'].find().count() == 1
        assert self.db.noteDB['IDs'].find({"currentMax": 1}).count() == 1
        assert self.db.noteDB['IDs'].find({"unusedIDs": []}).count() == 1

    def test_mongodb_deleteItem_2(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})

        assert self.db.noteDB['note'].find({"note": "ONE"}).count() == 1
        assert self.db.noteDB['note'].find({"note": "TWO"}).count() == 1

        with self.assertRaises(ValueError):
            self.db.deleteItem(100)

        assert self.db.noteDB['note'].find({"note": "ONE"}).count() == 1
        assert self.db.noteDB['note'].find({"note": "TWO"}).count() == 1

        assert self.db.noteDB['note'].find().count() == 2
        assert self.db.noteDB['IDs'].find({"currentMax": 2}).count() == 1
        assert self.db.noteDB['IDs'].find({"unusedIDs": []}).count() == 1

    def test_mongodb_getByTime(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})

        ids = self.db.getByTime(startTime=time.time() - 1,
                                endTime=time.time() + 1)
        assert ids == [1, 2]

        ids = self.db.getByTime(startTime=time.time() + 1,
                                endTime=time.time() + 4)
        assert ids == []

    def test_mongodb_getDone(self):
        self.db.addItem("todo", {"todoText": "get this done",
                                 "done": "False",
                                 "date": "03 25 14"})
        self.db.addItem("todo", {"todoText": "get this done!",
                                 "done": "True",
                                 "date": "03 26 14"})
        self.db.addItem("todo", {"todoText": "get this done!!",
                                 "done": "True",
                                 "date": "03 27 14"})
        self.db.addItem("todo", {"todoText": "get this done!!!",
                                 "done": "False",
                                 "date": "03 28 14"})

        #  Use sets so order doesn't matter
        ids = self.db.getDone("True")
        assert set(ids) == set([2, 3])
        ids = self.db.getDone("False")
        assert set(ids) == set([1, 4])

    def test_mongodb_getNewID(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})
        self.db.addItem("note", {"note": "THREE", "tags": ["three"]})

        assert 4 == self.db.getNewID()
        self.db.deleteItem(2)
        assert 2 == self.db.getNewID()

    def test_mongodb_makeBackupFile(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})

        self.db.makeBackupFile('/tmp', 'noteTestBackupFile.zip')

        assert os.path.isfile('/tmp/noteTestBackupFile.zip')
        os.remove('/tmp/noteTestBackupFile.zip')

    def test_mongodb_searchForItem_1(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})

        results = self.db.searchForItem("one")
        assert results[0]['obj']['note'] == "ONE"
        assert len(results) == 1

    def test_mongodb_searchForItem_2(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})
        self.db.addItem("note", {"note": "ONE THREE",
                                 "tags": ["one", "three"]})

        results = self.db.searchForItem("one", sortBy="date")
        assert results[0]['obj']['note'] == "ONE"
        assert results[0]['obj']['tags'] == ["one"]
        assert results[1]['obj']['note'] == "ONE THREE"
        assert results[1]['obj']['tags'] == ["one", "three"]
        assert len(results) == 2

    def test_mongodb_searchForItem_3(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})
        self.db.addItem("note", {"note": "ONE THREE",
                                 "tags": ["one", "three"]})

        results = self.db.searchForItem("one", sortBy="id")
        assert results[0]['obj']['note'] == "ONE"
        assert results[0]['obj']['tags'] == ["one"]
        assert results[1]['obj']['note'] == "ONE THREE"
        assert results[1]['obj']['tags'] == ["one", "three"]
        assert len(results) == 2

    def test_mongodb_verify(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})
        self.db.addItem("note", {"note": "THREE", "tags": ["three"]})

        from StringIO import StringIO

        try:
            saved_stdout = sys.stdout
            out = StringIO()
            sys.stdout = out
            self.db.verify()
            output = out.getvalue().strip()
        finally:
            sys.stdout = saved_stdout
        self.assertEquals(output, 'Database is valid')

    def test_mongodb_get_by_time_1(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        t1 = time.time()
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})

        results = self.db.getByTime(startTime=t1)
        self.assertEqual(results, [2])
        self.assertEqual(len(results), 1)

    def test_mongodb_get_by_time_2(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        t1 = time.time()
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})

        results = self.db.getByTime(endTime=t1)
        self.assertEqual(results, [1])
        self.assertEqual(len(results), 1)

    def test_mongodb_add_label_1(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})
        self.db.addLabel("testLabel", 1)
        self.db.addLabel("anothertestLabel", 2)

        results = self.db.getIDBytLabel("testLabel")
        self.assertEqual(results, 1)

        results = self.db.getIDBytLabel("anothertestLabel")
        self.assertEqual(results, 2)

    def test_mongodb_add_label_2(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})
        self.db.addLabel("testLabel", 1)
        results = self.db.addLabel("testLabel", 1)
        self.assertEqual(results, None)
        results = self.db.addLabel("testLabel", 2)
        self.assertEqual(results, None)

    def test_mongodb_delete_label(self):
        self.db.addItem("note", {"note": "ONE", "tags": ["one"]})
        self.db.addItem("note", {"note": "TWO", "tags": ["two"]})
        self.db.addLabel("testLabel", 1)

        results = self.db.getIDBytLabel("testLabel")
        self.assertEqual(results, 1)

        self.db.deleteLabel('testLabel')
        results = self.db.getIDBytLabel("testLabel")
        self.assertEqual(results, None)
