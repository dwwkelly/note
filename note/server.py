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

        if msg['object']['type'] == 'ID':
            reply = self.Get_By_ID(msg)
        elif msg['object']['type'] == 'done':
            reply = self.Get_Done(msg)
        elif msg['object']['type'] == 'Label':
            reply = self.Get_By_Label(msg)
        else:
            reply = {"status": "ERROR",
                     "type": "Get",
                     "object": {"msg": "Invalid Get"}}

        return json.dumps(reply)

    def Get_By_Label(self, msg):
        """

        """
        label = msg["object"]["name"]
        ID = self.db.getIDByLabel(label)
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

        return reply

    def Get_By_ID(self, msg):
        """

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

        return reply

    def Get_Done(self, msg):
        """

        :param: msg the JSON message from the client
        :returns: The reply from the db driver
        :rvalue: str
        """

        done = msg['object']['done']
        item_ids = self.db.getDone(done)

        if item_ids is []:
            if done:
                e_msg = "Could not find any done itms"
            else:
                e_msg = "Could not find any undone itms"

            reply = {"status": "ERROR",
                     "type": "Done",
                     "object": {"msg": e_msg}}
        else:
            items = []
            for ii in item_ids:
                tmp = {}
                tmp['type'] = 'todo'
                tmp['obj'] = self.db.getItem(ii)
                items.append(tmp)

            reply = {"status": "OK",
                     "type": "Done",
                     "object": items}

        return reply

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

    def Handle_Label(self, msg):
        """
            :desc: Set a label
            :param dict msg: The message received from the client
            :rval: str
            :returns: A status message (JSON serialized to a string)
        """

        obj = msg['object']
        if 'name' not in obj or 'id' not in obj:
            r_msg = {'status': 'ERROR',
                     'type': 'Label',
                     'object': {'msg': 'improper request'}}
            return json.dumps(r_msg)

        label_name = obj['name']
        label_id = obj['id']
        r_val = self.db.addLabel(label_name, label_id)

        if r_val is None:
            r_msg = {'status': 'ERROR',
                     'type': 'Label',
                     'object': {'msg': 'label already exists'}}
        else:
            r_msg = {'status': 'OK',
                     'type': 'Label',
                     'object': r_val}

        return json.dumps(r_msg)

    def Handle_Delete_Label(self, msg):
        """
            :desc: Deletes a label
            :param dic msg: The message with the instruction and the label
                            name to delete
            :rval: str
            :returns: The message from the database
        """

        try:
            label_name = msg['object']['label']
        except KeyError:
            r_msg = {'status': 'ERROR',
                     'type': 'Delete_Label',
                     'object': {'msg': 'improper request'}}
            return json.dumps(r_msg)
        else:
            r_val = {'status': 'OK',
                     'type': 'Delete',
                     'object': self.db.deleteLabel(label_name)}
            return json.dumps(r_val)
