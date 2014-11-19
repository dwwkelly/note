#!/usr/bin/env python

__author__ = "Devin Kelly"

import unittest
import note
import time
import os
import sys
from note import scrubID


class NoteDBTest(unittest.TestCase):

   def setUp(self):
      self.db = note.mongoDB('noteTest')

   def tearDown(self):
      self.db.client.drop_database("noteTest")

   def test_mongodb_create(self):

      assert self.db.noteDB['IDs'].find({"currentMax": 0}).count() == 1
      assert self.db.noteDB['IDs'].find({"unusedIDs": []}).count() == 1
      assert self.db.noteDB['IDs'].find().count() == 2

   def test_mongodb_addItem(self):
      self.db.addItem("notes", {"noteText": "this is a test note", "tags": ["one", "two"]})

      assert self.db.noteDB['notes'].find({"noteText": "this is a test note"}).count() == 1
      assert self.db.noteDB['notes'].find().count() == 1
      assert self.db.noteDB['IDs'].find({"currentMax": 1}).count() == 1
      assert self.db.noteDB['IDs'].find({"unusedIDs": []}).count() == 1
      assert self.db.noteDB['IDs'].find().count() == 2

   def test_mongodb_getItem(self):
      self.db.addItem("notes", {"noteText": "ONE", "tags": ["one"]})
      self.db.addItem("notes", {"noteText": "TWO", "tags": ["two"]})

      itemContents = self.db.getItem(1)
      assert itemContents['noteText'] == 'ONE'
      assert itemContents['tags'][0] == 'one'
      assert len(itemContents['tags']) == 1
      itemContents = self.db.getItem(2)

      assert itemContents['noteText'] == 'TWO'
      assert itemContents['tags'][0] == 'two'
      assert len(itemContents['tags']) == 1

   def test_mongodb_getItemType(self):
      self.db.addItem("notes", {"noteText": "ONE", "tags": ["one"]})
      self.db.addItem("notes", {"noteText": "TWO", "tags": ["two"]})
      self.db.addItem("todos", {"todoText": "get this done",
                                "done": "False",
                                "date": "03 24 14"})

      itemType = self.db.getItemType(1)
      assert itemType == "notes"

      itemType = self.db.getItemType(2)
      assert itemType == "notes"

      itemType = self.db.getItemType(3)
      assert itemType == "todos"

   def test_mongodb_deleteItem(self):
      self.db.addItem("notes", {"noteText": "ONE", "tags": ["one"]})
      self.db.addItem("notes", {"noteText": "TWO", "tags": ["two"]})

      assert self.db.noteDB['notes'].find({"noteText": "ONE"}).count() == 1
      assert self.db.noteDB['notes'].find({"noteText": "TWO"}).count() == 1

      self.db.deleteItem(2)

      assert self.db.noteDB['notes'].find({"noteText": "ONE"}).count() == 1
      assert self.db.noteDB['notes'].find({"noteText": "TWO"}).count() == 0

      assert self.db.noteDB['notes'].find().count() == 1
      assert self.db.noteDB['IDs'].find({"currentMax": 1}).count() == 1
      assert self.db.noteDB['IDs'].find({"unusedIDs": []}).count() == 1

   def test_mongodb_getByTime(self):
      self.db.addItem("notes", {"noteText": "ONE", "tags": ["one"]})
      self.db.addItem("notes", {"noteText": "TWO", "tags": ["two"]})

      ids = self.db.getByTime(startTime=time.time() - 1, endTime=time.time() + 1)
      assert ids == [1, 2]

      ids = self.db.getByTime(startTime=time.time() + 1, endTime=time.time() + 4)
      assert ids == []

   def test_mongodb_getDone(self):
      self.db.addItem("todos", {"todoText": "get this done",
                                "done": "False",
                                "date": "03 25 14"})
      self.db.addItem("todos", {"todoText": "get this done!",
                                "done": "True",
                                "date": "03 26 14"})
      self.db.addItem("todos", {"todoText": "get this done!!",
                                "done": "True",
                                "date": "03 27 14"})
      self.db.addItem("todos", {"todoText": "get this done!!!",
                                "done": "False",
                                "date": "03 28 14"})

      #  Use sets so order doesn't matter
      ids = self.db.getDone("True")
      assert set(ids) == set([2, 3])
      ids = self.db.getDone("False")
      assert set(ids) == set([1, 4])

   def test_mongodb_getNewID(self):
      self.db.addItem("notes", {"noteText": "ONE", "tags": ["one"]})
      self.db.addItem("notes", {"noteText": "TWO", "tags": ["two"]})
      self.db.addItem("notes", {"noteText": "THREE", "tags": ["three"]})

      assert 4 == self.db.getNewID()
      self.db.deleteItem(2)
      assert 2 == self.db.getNewID()

   def test_mongodb_makeBackupFile(self):
      self.db.addItem("notes", {"noteText": "ONE", "tags": ["one"]})
      self.db.addItem("notes", {"noteText": "TWO", "tags": ["two"]})

      self.db.makeBackupFile('/tmp', 'noteTestBackupFile.zip')

      assert os.path.isfile('/tmp/noteTestBackupFile.zip')
      os.remove('/tmp/noteTestBackupFile.zip')

   def test_mongodb_searchForItem(self):
      self.db.addItem("notes", {"noteText": "ONE", "tags": ["one"]})
      self.db.addItem("notes", {"noteText": "TWO", "tags": ["two"]})

      results = self.db.searchForItem("one")
      assert results[0]['obj']['noteText'] == "ONE"
      assert len(results) == 1

   def test_mongodb_verify(self):
      self.db.addItem("notes", {"noteText": "ONE", "tags": ["one"]})
      self.db.addItem("notes", {"noteText": "TWO", "tags": ["two"]})
      self.db.addItem("notes", {"noteText": "THREE", "tags": ["three"]})

      self.db.verify()

      if not hasattr(sys.stdout, "getvalue"):
         self.fail("need to run in buffered mode")
      output = sys.stdout.getvalue().strip()
      self.assertEquals(output, 'Database is valid')

   def test_scrub_id_1(self):

       ID = scrubID(['13'])

       self.assertEqual(13, ID)

   def test_scrub_id_2(self):

       ID = scrubID([13])

       self.assertEqual(13, ID)

   def test_scrub_id_3(self):

       ID = scrubID('13')

       self.assertEqual(13, ID)
if __name__ == "__main__":
   unittest.main(buffer=True)
