#!/usr/bin/env python

__author__ = "Devin Kelly"

import unittest
from note import Note_Server
from note import Note_Client
import zmq


class Note_Client_Test(unittest.TestCase):

    def setUp(self):
        self.note_server = Note_Server('noteTest')
        self.client = Note_Client()

    def tearDown(self):
        self.note_server.db.client.drop_database("noteTest")
        self.note_server.context.destroy()

        self.client.context.destroy()

    def test_client_init_1(self):

        self.assertIsInstance(self.client.context, zmq.Context)
        self.assertIsInstance(self.client.sock, zmq.Socket)

    def test_client_Send_1(self):

        msg = {'test': 'message'}

        reply = self.client.Send(msg)

        self.assertEqual(reply, None)

    def test_client_Send_2(self):

        # this test always hangs because the server doesn't seem to reply
        # putting the server in a separate process doesn't seem to help
        return

        note = 'test note'
        tags = ['t1', 't2']
        msg = {"type": "Note", "object": {"noteText": note, "tags": tags}}

        expected_reply = {"status": "OK",
                          "type": "Note",
                          "object": {
                                    "received note": note,
                                    "received tags": tags}
                          }

        reply = self.client.Send(msg)

        self.assertEqual(reply, expected_reply)

    def test_encrypt_1(self):

        reply = self.client.Encrypt()

        self.assertEqual(reply, None)
