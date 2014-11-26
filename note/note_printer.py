from util import colors

class Note_Printer(object):

    def __init__(self, msg):
        """

        """

        self.msg_json = msg
        self.status = self.msg['status']
        self.msg_type = self.msg['type']

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


        msg_type = self.msg['type']
        # FIXME - is there a better way to do this?
        f_name = "print_{0}".format(self.msg_type)
        f = getattr(f_name)
        f()

    def print_NewNote(self):
        """

        """

        ID = self.msg['object']
        s = "{red}{ID}\n{black} {msg}"
        s = s.format(colors['foreground red'])

    def print_ERROR(self):
        """

        """

        s = "{0}ERROR:{1}{2}"
        s.format(colors['foreground red'],
                 colors['foreground black'],
                 self.msg['msg'])

        print s
