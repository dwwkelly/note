import json
import datetime
import time
import textwrap
from util import colors


class Note_Printer(object):

    def __init__(self):
        """

        """

    def __call__(self, msg):

        self.msg = json.loads(msg)
        self.status = self.msg['status']
        self.msg_type = self.msg['type']

        self.Print()

    def Print(self):
        """

        """

        if self.status == 'OK':
            self.print_OK()
        elif self.status == 'ERROR':
            self.print_error()

    def print_OK(self):
        """

        """

        self.msg_type = self.msg['type']
        # FIXME - is there a better way to do this?
        f_name = "print_{0}".format(self.msg_type)
        try:
            f = getattr(self, f_name)
        except AttributeError:
            return

        f()

    def print_error(self):
        """

        """

        s = "{0}ERROR: {1}{2}"
        s = s.format(colors['foreground red'],
                     colors['foreground black'],
                     self.msg['object']['msg'])

        print s

    def print_search(self):

        results = self.msg['object']['results']

        for res in results:

            f = getattr(self, "print_{0}".format(res['itemType']))
            f(res)

    def print_note(self, msg):

            note_text = msg['obj']['note']
            ID = msg['obj']['ID']
            timestamps = msg['obj']['timestamps']
            timestamp = time.localtime(max(timestamps))
            noteDate = time.strftime("%a, %b %d", timestamp)

            s = '{fblue}{ID} {hicolor}{fred}{date}{reset}: {note}'
            s = s.format(fblue=colors['foreground blue'],
                         ID=ID,
                         hicolor=colors['hicolor'],
                         fred=colors['foreground red'],
                         date=noteDate,
                         reset=colors['reset'],
                         note=note_text.encode('UTF-8'))

            for ii in s.split('\n'):
                print textwrap.fill(ii, width=80)

    def print_place(self, msg):

            note_text = msg['obj']['note']
            place_text = msg['obj']['place']
            address_text = msg['obj']['address']
            ID = msg['obj']['ID']
            timestamps = msg['obj']['timestamps']
            timestamp = time.localtime(max(timestamps))
            noteDate = time.strftime("%a, %b %d", timestamp)

            s = '{fblue}{ID} {hicolor}{fred}{date}{reset}: ' +\
                '{place}, {address}\n{note}'
            s = s.format(fblue=colors['foreground blue'],
                         ID=ID,
                         hicolor=colors['hicolor'],
                         fred=colors['foreground red'],
                         date=noteDate,
                         reset=colors['reset'],
                         note=note_text.encode('UTF-8'),
                         address=address_text,
                         place=place_text)

            for ii in s.split('\n'):
                print textwrap.fill(ii, width=80)

    def print_todo(self, msg):

            todo_text = msg['obj']['todo']
            done = msg['obj']['done']
            todo_date = msg['obj']['date']
            ID = msg['obj']['ID']
            timestamps = msg['obj']['timestamps']
            timestamp = time.localtime(max(timestamps))
            noteDate = time.strftime("%a, %b %d", timestamp)

            todo_date = datetime.datetime.fromtimestamp(todo_date)
            todo_date = todo_date.strftime('%Y-%m-%d')

            if done.lower() in ['false', 'no']:
                done = 'Not Done'
            elif done.lower() in ['true', 'yes']:
                done = 'Done'

            s = '{fblue}{ID} {hicolor}{fred}{date}{reset}: ' +\
                '{todo_text}\n\n{done} - {todo_date}'
            s = s.format(fblue=colors['foreground blue'],
                         ID=ID,
                         hicolor=colors['hicolor'],
                         fred=colors['foreground red'],
                         date=noteDate,
                         reset=colors['reset'],
                         todo_text=todo_text.encode('UTF-8'),
                         todo_date=todo_date,
                         done=done)

            for ii in s.split('\n'):
                print textwrap.fill(ii, width=80)

    def print_Get(self):

        print self.msg
