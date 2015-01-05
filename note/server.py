import zmq
import sys
import json
from mongo_driver import mongoDB as database


class Note_Server(object):

    """ """

    def __init__(self, db_name='note'):
        """

        """

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

        self.db = database(db_name)  # FIXME read config file

    def Run(self):
        """
        Wait for clients to connect and service them

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
        """
        Handle events from poll()

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
        """
        Handle a received message.

        :param msg: the received message
        :type msg: str
        :returns: The message to reply with
        :rtype: str
        """

        msg = self.Check_Message(msg)
        msg_type = msg['type']

        f_name = "Handle_{0}".format(msg_type)
        try:
            f = getattr(self, f_name)
        except AttributeError:
            f = self.Handle_ERROR(msg)
        reply = f(msg)

        return reply

    def Check_Message(self, msg):
        """
        Verifies the message is a valid note message
        """

        msg = json.loads(msg)
        return msg

    def Handle_Search(self, msg):
        """
        Handle a search.

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

    def Handle_Note(self, msg):
        """ Handle a new note.

        :param msg: the received note
        :type msg: dict
        :returns: The message to reply with
        :rtype: str
        """

        note_text = msg['object']['note']
        note_tags = msg['object']['tags']

        if 'ID' in msg['object']:
            note_id = msg['object']['ID']
            self.db.addItem("note", {"note": note_text,
                                     "tags": note_tags},
                            note_id)
        else:
            note_id = self.db.addItem("note", {"note": note_text,
                                               "tags": note_tags})

        reply = {"status": "OK",
                 "type": "Note",
                 "object": {
                           "received note": msg['object']['note'],
                           "received tags": msg['object']['tags'],
                           "ID": note_id}
                 }

        return json.dumps(reply)

    def Handle_Get(self, msg):
        """

        :param: msg the JSON message from the client
        :returns: The reply from the db driver
        :rvalue: str
        """

        ID = msg['object']['id']
        item = self.db.getItem(ID)

        if item is None:
            reply = {"status": "ERROR",
                     "type": "Get",
                     "object": {"msg": "Item does not exist",
                                "ID": ID}}
        else:
            reply = {"status": "OK",
                     "type": "Get",
                     "object": item}

        return json.dumps(reply)

    def Handle_Done(self, msg):
        """

        :param: msg the JSON message from the client
        :returns: The reply from the db driver
        :rvalue: str
        """

        done = msg['object']['done']
        items = self.db.getDone(done)

        if items is []:
            if done:
                e_msg = "Could not find any done itms"
            else:
                e_msg = "Could not find any undone itms"

            reply = {"status": "ERROR",
                     "type": "Done",
                     "object": {"msg": e_msg}}
        else:
            reply = {"status": "OK",
                     "type": "Done",
                     "object": items}

        return json.dumps(reply)

    def Handle_Delete(self, msg):
        """

        :param: msg the JSON message from the client
        :returns: The reply from the db driver
        :rvalue: str
        """

        ID = msg['object']['id']
        try:
            reply = {"status": "OK",
                     "type": "Delete",
                     "object": self.db.deleteItem(ID)}
        except ValueError:
            e_msg = "Object with ID {0} does not exist".format(ID)
            reply = {"status": "ERROR",
                     "type": "Delete",
                     "object": {"msg": e_msg}}

        return json.dumps(reply)

    def Handle_ERROR(self, msg):
        reply = {"status": "ERROR",
                 "object": {"msg": "unknown command"},
                 "type": "ERROR MSG"}
        reply = json.dumps(reply)

        return reply

    def Handle_Place(self, msg):

        place = msg['object']['place']
        address = msg['object']['address']
        note = msg['object']['note']
        tags = msg['object']['tags']

        if 'ID' in msg['object']:
            note_id = msg['object']['ID']
            self.db.addItem("place", {"note": note,
                                      "address": address,
                                      "place": place,
                                      "tags": tags},
                            note_id)
        else:
            note_id = self.db.addItem("place", {"note": note,
                                                "address": address,
                                                "place": place,
                                                "tags": tags})

        reply = {"status": "OK",
                 "type": "Place",
                 "object": {
                           "received note": msg['object']['note'],
                           "received tags": msg['object']['tags'],
                           "ID": note_id}
                 }

        return json.dumps(reply)

    def Handle_Todo(self, msg):

        todo = msg['object']['todo']
        done = msg['object']['done']
        date = msg['object']['date']
        tags = msg['object']['tags']

        if done.lower() == 'no' or done.lower() == 'false':
            done = False
        else:
            done = True

        if 'ID' in msg['object']:
            note_id = msg['object']['ID']
            self.db.addItem("todo", {"todo": todo,
                                     "done": done,
                                     "date": date,
                                     "tags": tags},
                            note_id)
        else:
            note_id = self.db.addItem("todo", {"todo": todo,
                                               "done": done,
                                               "date": date,
                                               "tags": tags})

        reply = {"status": "OK",
                 "type": "Todo",
                 "object": {"todo": todo,
                            "done": done,
                            "date": date,
                            "tags": tags,
                            "ID": note_id}
                 }

        return json.dumps(reply)
