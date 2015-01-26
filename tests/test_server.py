#!/usr/bin/env python

__author__ = "Devin Kelly"

import json
import unittest
from note import Note_Server


class Note_Server_Test(unittest.TestCase):

    def setUp(self):
        self.note_server = Note_Server('noteTest')

        note_1 = {"note": "note 1",
                  "tags": ["t1", "t2"]}
        note_2 = {"note": "note 2",
                  "tags": ["t3", "t4"]}

        self.note_server.db.addItem('note', note_1)
        self.note_server.db.addItem('note', note_2)

    def tearDown(self):
        self.note_server.db.client.drop_database("noteTest")
        self.note_server.context.destroy()

    def test_Handle_Get_1(self):
        msg = {"type": "Get", "object": {"type": "ID", "id": 1}}
        reply = self.note_server.Handle_Get(msg)
        reply = json.loads(reply)

        self.assertEquals(reply['object']['note'], 'note 1')
        self.assertEquals(reply['object']['tags'], ['t1', 't2'])
        self.assertEquals(reply['type'], 'Get')
        self.assertEquals(reply['status'], 'OK')

    def test_Handle_Get_2(self):
        msg = {"type": "Get", "object": {"type": "ID", "id": 2}}
        reply = self.note_server.Handle_Get(msg)
        reply = json.loads(reply)

        self.assertEquals(reply['object']['note'], 'note 2')
        self.assertEquals(reply['object']['tags'], ['t3', 't4'])
        self.assertEquals(reply['type'], 'Get')
        self.assertEquals(reply['status'], 'OK')

    def test_Handle_Get_3(self):
        msg = {"type": "Get", "object": {"type": "ID", "id": 3}}
        reply = self.note_server.Handle_Get(msg)
        reply = json.loads(reply)

        expected = {u'msg': u'Item does not exist', u'ID': 3}
        self.assertEquals(reply['object'], expected)
        self.assertEquals(reply['type'], 'Get')
        self.assertEquals(reply['status'], 'ERROR')

    def test_Handle_Search_1(self):
        searchTerm = '"note 1"'
        msg = {"type": "Search", "object": {"searchTerm": searchTerm}}
        reply = self.note_server.Handle_Search(msg)
        reply = json.loads(reply)

        results = reply['object']['results']
        self.assertEquals(results[0]['obj']['note'], 'note 1')
        self.assertEquals(results[0]['obj']['ID'], 1)
        self.assertEquals(results[0]['obj']['tags'], ['t1', 't2'])
        self.assertEquals(results[0]['type'], 'note')
        self.assertEquals(reply['object']['received search'], '"note 1"')
        self.assertEquals(reply['type'], 'search')
        self.assertEquals(reply['status'], 'OK')
        self.assertEquals(self.note_server.db.noteDB['IDs'].find().count(), 2)

    def test_Handle_Search_2(self):
        searchTerm = '"note 2"'
        msg = {"type": "Search", "object": {"searchTerm": searchTerm}}
        reply = self.note_server.Handle_Search(msg)
        reply = json.loads(reply)

        results = reply['object']['results']
        self.assertEquals(results[0]['obj']['note'], 'note 2')
        self.assertEquals(results[0]['obj']['ID'], 2)
        self.assertEquals(results[0]['obj']['tags'], ['t3', 't4'])
        self.assertEquals(results[0]['type'], 'note')
        self.assertEquals(reply['object']['received search'], '"note 2"')
        self.assertEquals(reply['type'], 'search')
        self.assertEquals(reply['status'], 'OK')
        self.assertEquals(self.note_server.db.noteDB['IDs'].find().count(), 2)

    def test_Handle_Search_3(self):
        searchTerm = '"note 3"'
        msg = {"type": "Search", "object": {"searchTerm": searchTerm}}
        reply = self.note_server.Handle_Search(msg)
        reply = json.loads(reply)

        results = reply['object']['results']
        self.assertEquals(results, [])
        self.assertEquals(reply['object']['received search'], '"note 3"')
        self.assertEquals(reply['type'], 'search')
        self.assertEquals(reply['status'], 'OK')
        self.assertEquals(self.note_server.db.noteDB['IDs'].find().count(), 2)

    def test_Handle_Note_1(self):

        note = 'note 3'
        tags = ['t4', 't5']
        msg = {"type": "Note", "object": {"note": note, "tags": tags}}

        reply = self.note_server.Handle_Note(msg)
        reply = json.loads(reply)

        self.assertEquals(reply['object']['received note'], note)
        self.assertEquals(reply['object']['received tags'], tags)
        self.assertEquals(reply['type'], 'Note')
        self.assertEquals(reply['status'], 'OK')
        note_count = self.note_server.db.noteDB['note'].find().count()
        self.assertEquals(note_count, 3)

    def test_Handle_Note_2(self):

        note = 'note 3'
        tags = ['t4', 't5']
        msg = {"type": "Note", "object": {"note": note, "tags": tags}}

        reply = self.note_server.Handle_Note(msg)
        reply = json.loads(reply)

        self.assertEquals(reply['object']['received note'], note)
        self.assertEquals(reply['object']['received tags'], tags)
        self.assertEquals(reply['type'], 'Note')
        self.assertEquals(reply['status'], 'OK')
        note_count = self.note_server.db.noteDB['note'].find().count()
        self.assertEquals(note_count, 3)

        note = 'note 4'
        tags = ['t6', 't7']
        msg = {"type": "Note", "object": {"note": note, "tags": tags}}

        reply = self.note_server.Handle_Note(msg)
        reply = json.loads(reply)

        self.assertEquals(reply['object']['received note'], note)
        self.assertEquals(reply['object']['received tags'], tags)
        self.assertEquals(reply['type'], 'Note')
        self.assertEquals(reply['status'], 'OK')
        note_count = self.note_server.db.noteDB['note'].find().count()
        self.assertEquals(note_count, 4)

    def test_Handle_Delete_1(self):

        msg = {"type": "Delete", "object": {"id": 1}}

        reply = self.note_server.Handle_Delete(msg)
        reply = json.loads(reply)

        self.assertEqual(reply['status'], 'OK')
        self.assertEqual(reply['type'], 'Delete')
        self.assertEqual(reply['object'], 1)
        note_count = self.note_server.db.noteDB['note'].find().count()
        self.assertEquals(note_count, 1)

    def test_Handle_Delete_2(self):

        msg = {"type": "Delete", "object": {"id": 1}}

        reply = self.note_server.Handle_Delete(msg)
        reply = json.loads(reply)

        self.assertEqual(reply['status'], 'OK')
        self.assertEqual(reply['type'], 'Delete')
        self.assertEqual(reply['object'], 1)
        note_count = self.note_server.db.noteDB['note'].find().count()
        self.assertEquals(note_count, 1)

        msg = {"type": "Delete", "object": {"id": 2}}

        reply = self.note_server.Handle_Delete(msg)
        reply = json.loads(reply)

        self.assertEqual(reply['status'], 'OK')
        self.assertEqual(reply['type'], 'Delete')
        self.assertEqual(reply['object'], 2)
        note_count = self.note_server.db.noteDB['note'].find().count()
        self.assertEquals(note_count, 0)

    def test_Handle_Delete_3(self):

        note = 'note 3'
        tags = ['t4', 't5']
        msg = {"type": "Note", "object": {"note": note, "tags": tags}}

        self.note_server.Handle_Note(msg)

        msg = {"type": "Delete", "object": {"id": 2}}

        reply = self.note_server.Handle_Delete(msg)
        reply = json.loads(reply)

        query = {'unusedIDs': {'$exists': True}}
        unusedIDs = self.note_server.db.noteDB['IDs'].find(query)[0]
        query = {'currentMax': {'$exists': True}}
        currentMax = self.note_server.db.noteDB['IDs'].find(query)[0]

        self.assertEqual(reply['status'], 'OK')
        self.assertEqual(reply['type'], 'Delete')
        self.assertEqual(reply['object'], 2)
        self.assertEqual(unusedIDs['unusedIDs'], [2])
        self.assertEqual(currentMax['currentMax'], 3)

    def test_Handle_Label_1(self):

        msg = {'type': 'label',
               'object': {'name': 'test_label', 'id': 1}
               }
        self.note_server.Handle_Label(msg)

        query = {'name': 'test_label'}
        label = self.note_server.db.noteDB['label'].find(query)

        self.assertEqual(label[0]['name'], 'test_label')
        self.assertEqual(label[0]['ID'], 1)

    def test_Handle_Label_2(self):

        msg = {'type': 'label',
               'object': {'name': 'test_label_1', 'id': 1}
               }
        self.note_server.Handle_Label(msg)

        msg = {'type': 'label',
               'object': {'name': 'test_label_2', 'id': 2}
               }
        self.note_server.Handle_Label(msg)

        query = {'name': 'test_label_1'}
        label = self.note_server.db.noteDB['label'].find(query)

        self.assertEqual(label[0]['name'], 'test_label_1')
        self.assertEqual(label[0]['ID'], 1)

        query = {'name': 'test_label_2'}
        label = self.note_server.db.noteDB['label'].find(query)

        self.assertEqual(label[0]['name'], 'test_label_2')
        self.assertEqual(label[0]['ID'], 2)

    def test_Handle_Label_3(self):

        msg = {'type': 'label',
               'object': {'name': 'test_label_1', 'id': 1}
               }
        self.note_server.Handle_Label(msg)

        msg = {'type': 'label',
               'object': {'name': 'test_label_2', 'id': 1}
               }
        self.note_server.Handle_Label(msg)

        query = {'name': 'test_label_1'}
        label = self.note_server.db.noteDB['label'].find(query)

        self.assertEqual(label[0]['name'], 'test_label_1')
        self.assertEqual(label[0]['ID'], 1)

        query = {'name': 'test_label_2'}
        label = self.note_server.db.noteDB['label'].find(query)

        self.assertEqual(label[0]['name'], 'test_label_2')
        self.assertEqual(label[0]['ID'], 1)

    def test_Handle_Label_4(self):

        msg = {'type': 'label',
               'object': {'name': 'test_label_1', 'id': 1}
               }
        self.note_server.Handle_Label(msg)

        msg = {'type': 'label',
               'object': {'name': 'test_label_1', 'id': 2}
               }
        reply = self.note_server.Handle_Label(msg)

        expected = {'status': 'ERROR',
                    'type': 'Label',
                    'object': {'msg': 'label already exists'}}

        self.assertEqual(expected, json.loads(reply))
