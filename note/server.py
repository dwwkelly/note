import zmq
import sys
import json
from mongo_driver import mongoDB as database


class Note_Server(object):

   """ """

   def __init__(self):
      """ """

      self.zmq_threads = 1
      self.zmq_addr = "127.0.0.1"
      self.zmq_port = 5500  # FIXME - get from config file
      self.zmq_uri = "tcp://" + self.zmq_addr + ":" + str(self.zmq_port)
      self.poll_timeout = 1000  # ms

      self.context = zmq.Context.instance()
      self.receive_sock = self.context.socket(zmq.REP)
      self.receive_sock.bind(self.zmq_uri)

      self.poller = zmq.Poller()
      self.poller.register(self.receive_sock, zmq.POLLIN)

      self.db = database('noteTest')  # FIXME read config file

   def Run(self):
      """ Wait for clients to connect and service them

      :returns: None
      """

      while True:

         try:
            events = self.poller.poll()
         except KeyboardInterrupt:
            self.context.destroy()
            sys.exit()

         self.Handle_Events(events)

   def Handle_Events(self, events):
      """ Handle events from poll()

      :events: A list of tuples form zmq.poll()
      :type events: list
      :returns: None

      """
      for e in events:

         sock = e[0]
         event_type = e[1]

         if event_type == zmq.POLLIN:
            msg = sock.recv()
            reply = self.Handle_Receive(msg)
            sock.send(reply)
         elif event_type == zmq.POLLOUT:
            pass  # FIXME -- handle this correctly
         elif event_type == zmq.POLLERR:
            pass  # FIXME -- handle this correctly
         else:
            pass  # FIXME -- handle this correctly, this is an error

   def Handle_Receive(self, msg):
      """ Handle a received message.

      :param msg: the received message
      :type msg: str
      :returns: The message to reply with
      :rtype: str
      """

      msg = self.Check_Message(msg)

      if msg['type'] == "search":
         reply = self.Handle_Search(msg)
      elif msg['type'] == "NewNote":
         reply = self.Handle_NewNote(msg)
      elif msg['type'] == "get":
         reply = self.Handle_Get(msg)
      else:
         reply = {"status": "error", "object": {"msg": "unknown command"}}
         reply = json.dumps(reply)

      return reply

   def Check_Message(self, msg):
      """ Verifies the message is a valid note message """

      msg = json.loads(msg)
      return msg

   def Handle_Search(self, msg):
      """ Handle a search.

      :param msg: the received search
      :type msg: dict
      :returns: The message to reply with
      :rtype: str
      """

      search_term = msg['object']['searchTerm']
      results = self.db.searchForItem(search_term)

      reply = {"status": "OK",
               "type": "search",
               "object": {
                         "received search": msg['object']['searchTerm'],
                         "results": results}
               }

      return json.dumps(reply)

   def Handle_NewNote(self, msg):
      """ Handle a new note.

      :param msg: the received note
      :type msg: dict
      :returns: The message to reply with
      :rtype: str
      """

      reply = {"status": "OK",
               "type": "NewNote",
               "object": {
                         "received note": msg['object']['noteText'],
                         "received tags": msg['object']['tags']}
               }

      return json.dumps(reply)

   def Handle_Get(self, msg):

      reply = {"status": "OK",
               "type": "note",
               "object": {"notetext": "sad", "tags": ["1", "2"]}}

      return json.dumps(reply)
