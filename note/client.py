import os
import re
import zmq
import sys
import time
import json
import argparse
import datetime


class Note_Client(object):

   """ This is the client side library to interact with the note server """

   def __init__(self):
      """ Initialize the client, mostly ZMQ setup"""

      self.server_addr = "127.0.0.1"
      self.server_port = 5500  # FIXME - get from config file
      self.server_uri = "tcp://"
      self.server_uri = self.server_uri + self.server_addr
      self.server_uri = self.server_uri + ":"
      self.server_uri = self.server_uri + str(self.server_port)
      self.poll_timeout = 1000  # ms

      self.context = zmq.Context.instance()
      self.sock = self.context.socket(zmq.REQ)
      self.sock.connect(self.server_uri)

   def Send(self, msg):
      """ Add a note to the database on the server
      :param msg: The text of the note.
      :type msg: str
      :param tags: A list of tags to associate with the note.
      :type tags: list
      :returns: The message from the server
      :rtype: str
      """
      if 'type' not in msg:
         return

      self.sock.send(json.dumps(msg))
      msg = self.sock.recv()
      return msg

   def Encrypt(self):
      """

      """

      return

   def Handle_Reply(self, msg):
      """ Handle the reply from the server, just print for now.
      :param msg: The reply.
      :type msg: str
      :returns: None
      """

      try:
         msg = json.loads(msg)
      except ValueError:
         print "invalid reply"  # FIXME -- error

      print msg
