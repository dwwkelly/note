import json
import time
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
                     self.msg['msg'])

        print s

    def print_search(self):

        results = self.msg['object']['results']

        for res in results:
            note_text = res['obj']['noteText']
            # tags = res['obj']['tags']
            ID = res['obj']['ID']
            timestamps = res['obj']['timestamps']
            timestamp = time.localtime(max(timestamps))
            noteDate = time.strftime("%a, %b %d", timestamp)

            s = '{fblue}{ID} {hicolor}{fred}{date}{reset}: {noteText}'
            s = s.format(fblue=colors['foreground blue'],
                         ID=ID,
                         hicolor=colors['hicolor'],
                         fred=colors['foreground red'],
                         date=noteDate,
                         reset=colors['reset'],
                         noteText=note_text.encode('UTF-8'))

            print s
