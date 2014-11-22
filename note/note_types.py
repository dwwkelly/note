import re
import os
import sys
import time
import copy
import subprocess as SP
from util import which
from util import scrubID
from util import colors
from abc import ABCMeta
from abc import abstractmethod


class NoteBaseClass(object):
    __metaclass__ = ABCMeta

    """ Virtual Methods """

    @abstractmethod
    def __init__(self, db):
        """

        """
        self.homeDir = os.path.expanduser('~')
        self.tmpNote = os.path.join(self.homeDir, '.note.TMP')
        self.editor = os.getenv('EDITOR')
        self.possible_editors = ['vim', 'vi', 'nano', 'emacs']
        self.db = db

        if self.editor is None:
            self.set_editor()

        return

    def set_editor(self):
        """
        Set the text editor to use
        """
        for editor in self.possible_editors:
            if which(editor):
                self.editor = editor
                break

    @abstractmethod
    def edit(self, ID):
        """

        """
        return

    @abstractmethod
    def printItem(self, ID, color=True):
        """

        """
        return

    @abstractmethod
    def new(self, dummy=None):
        """

        """
        return

    def delete(self, ID):
        """

        """
        try:
            ID = int(ID[0])
        except TypeError:
            pass

        self.db.deleteItem(ID)

    def startEditor(self, startingLine=1):
        """

        """
        editor_paths = ['/usr/bin/vim', '/usr/local/bin/vim']
        if any([self.editor in ii for ii in editor_paths]):
            SP.call([self.editor, "+{0}".format(startingLine),
                     "-c", "startinsert", self.tmpNote])
            try:
                os.remove("{0}.swp".format(self.tmpNote))
                os.remove("{0}".format(self.tmpNote))
            except OSError:
                pass
        else:
            SP.call([self.editor, self.tmpNote])


class Note(NoteBaseClass):
    def __init__(self, db):
        """

        """
        super(Note, self).__init__(db)
        self.noteType = u"notes"
        self.noteTemplate = u"NOTE\n\n\n\nTAGS\n\n\n"
        self.noteEditTemplate = u"NOTE\n\n{0}\n\nTAGS\n\n{1}\n"

    def new(self, dummy=None):
        """

        """
        self.makeTmpFile()
        self.addByEditor()

    def edit(self, ID):
        """

        """
        ID = scrubID(ID)
        self.makeTmpFile(ID)
        self.addByEditor(ID)

    def printItem(self, ID, color=True):
        """

        """
        result = self.db.getItem(ID)
        noteText = result['noteText']
        timestamps = result['timestamps']
        timestamp = time.localtime(max(timestamps))
        noteDate = time.strftime("%a, %b %d", timestamp)
        if color:
            print u"{5}{6} {4}{2}{0}:{3} {1}".format(noteDate,
                                                     noteText,
                                                     colors['foreground red'],
                                                     colors['reset'],
                                                     colors['hicolor'],
                                                     colors['foreground blue'],
                                                     int(ID))
        else:
            s = u"{2} {0}: {1}".format(noteDate, noteText, int(ID))
            s = s.encode('utf-8')
            print s

    def processNote(self):
        """

        """

        try:
            with open(self.tmpNote) as fd:
                lines = fd.read()
        except IOError:
            print("Config file doesn't exist, exiting")
            sys.exit(-1)

        noteText = lines[lines.index('NOTE') + 4: lines.index('TAGS')]
        noteText = noteText.split('\n')
        noteText = map(lambda x: x.rstrip(), noteText)
        noteText = '\n'.join(noteText)
        noteText = re.sub(r'^\s*', '', noteText)
        noteText = re.sub(r'\s*$', '', noteText)
        self.noteText = noteText

        tags = lines[lines.index('TAGS') + 4: -1]
        tags = tags.split(',')
        tags = filter(lambda x: x != '', tags)
        tags = map(lambda x: x.rstrip(), tags)
        tags = map(lambda x: x.lstrip(), tags)
        self.tags = tags

    def makeTmpFile(self, ID=None):
        """
           @todo: Makes the temporary file for a new note or
           a note that is to be edited.

        :ID: The note ID, if given populates file with note contents,
             otherwise use template
        :returns: Nothing

        """

        fileText = ""
        if ID:
            ID = scrubID(ID)
            origNote = self.db.getItem(ID)
            origNotetext = origNote['noteText']
            origTags = ','.join(origNote['tags'])

            fileText = (self.noteEditTemplate.format(origNotetext, origTags))
            fileText = fileText.encode('utf-8')
        else:
            fileText = self.noteTemplate

        with open(self.tmpNote, 'w') as fd:
            fd.write(fileText)

    def addByEditor(self, ID=None):
        """

        """
        self.startEditor(3)
        self.processNote()

        if self.noteText:
            self.db.addItem("notes",
                            {"noteText": self.noteText, "tags": self.tags},
                            itemID=ID)


class Place(NoteBaseClass):
    """

    """

    def __init__(self, db):
        """

        """
        super(Place, self).__init__(db)
        self.noteType = u"places"
        self.noteTemplate = u"PLACE\n\n\n\nNOTES\n\n\n\n" +\
                            u"ADDRESS\n\n\n\nTAGS\n\n\n"
        self.noteEditTemplate = u"PLACE\n\n{0}\n\nNOTES\n\n{1}\n\n" +\
                                u"ADDRESS\n\n{2}\n\nTAGS\n\n{3}\n"

    def processPlace(self):
        """

        """

        try:
            with open(self.tmpNote) as fd:
                lines = fd.read()
        except IOError:
            print("Config file doesn't exist, exiting")
            sys.exit(-1)

        placeText = lines[lines.index('PLACE') + 5: lines.index('NOTES')]
        placeText = placeText.split('\n')
        placeText = map(lambda x: x.rstrip(), placeText)
        placeText = '\n'.join(placeText)
        placeText = re.sub(r'^\s*', '', placeText)
        placeText = re.sub(r'\s*$', '', placeText)
        self.placeText = placeText

        noteText = lines[lines.index('NOTES') + 5: lines.index('ADDRESS')]
        noteText = noteText.split('\n')
        noteText = map(lambda x: x.rstrip(), noteText)
        noteText = '\n'.join(noteText)
        noteText = re.sub(r'^\s*', '', noteText)
        noteText = re.sub(r'\s*$', '', noteText)
        self.noteText = noteText

        addressText = lines[lines.index('ADDRESS') + 7: lines.index('TAGS')]
        addressText = addressText.split('\n')
        addressText = map(lambda x: x.rstrip(), addressText)
        addressText = '\n'.join(addressText)
        addressText = re.sub(r'^\s*', '', addressText)
        addressText = re.sub(r'\s*$', '', addressText)
        self.addressText = addressText

        tags = lines[lines.index('TAGS') + 4: -1]
        tags = tags.split(',')
        tags = filter(lambda x: x != '', tags)
        tags = map(lambda x: x.rstrip(), tags)
        tags = map(lambda x: x.lstrip(), tags)
        self.tags = tags

    def edit(self, ID):
        """

        """
        ID = scrubID(ID)
        origNote = self.db.getItem(ID)
        origNoteText = origNote['noteText']
        origAddressText = origNote['addressText']
        origPlaceText = origNote['placeText']
        origTags = ','.join(origNote['tags'])

        editText = (self.noteEditTemplate.format(origPlaceText,
                                                 origNoteText,
                                                 origAddressText,
                                                 origTags))
        editText = editText.encode('utf-8')
        with open(self.tmpNote, 'w') as fd:
            fd.write(editText)

        self.addByEditor(ID)

    def new(self, dummy=None):
        """

        """

        with open(self.tmpNote, 'w') as fd:
            fd.write(self.noteTemplate)

        self.addByEditor()

    def printItem(self, ID, color=True):
        """

        """
        ID = scrubID(ID)
        result = self.db.getItem(ID)
        noteText = result['noteText']
        addressText = result['addressText']
        placeText = result['placeText']
        timestamps = result['timestamps']
        timestamp = time.localtime(max(timestamps))
        noteDate = time.strftime("%a, %b %d", timestamp)

        if color:
            s = u"{0}{1} {2}{3}{4}:{5}\n{6}\n{7}"
            print s.format(colors['foreground blue'],
                           int(ID),
                           colors['foreground red'],
                           colors['reset'],
                           noteDate,
                           placeText,
                           noteText,
                           addressText)
        else:
            s = u"{0} {1}: {2}\n{3}\n{4}"
            s = s.format(int(ID),
                         noteDate,
                         placeText,
                         noteText,
                         addressText)
            s = s.encode('utf-8')
            print s

    def addByEditor(self, ID=None):
        """

        """

        self.startEditor(3)
        self.processPlace()
        self.db.addItem(self.noteType, {"noteText": self.noteText,
                                        "placeText": self.placeText,
                                        "addressText": self.addressText,
                                        "tags": self.tags}, ID)


class ToDo(NoteBaseClass):

    def __init__(self, db):
        """

        """
        super(ToDo, self).__init__(db)
        self.noteType = "todos"
        self.todoTemplate = u"TODO\n\n\n\nDONE\n\n\n\nDATE - MM DD YY\n\n\n"
        self.todoEditTemplate = u"TODO\n\n{0}\n\nDONE\n\n{1}\n\n" +\
                                u"DATE - MM DD YY\n\n{2}\n\n"

    def edit(self, ID):
        """

        """
        ID = scrubID(ID)
        todo = self.db.getItem(ID)
        dateStr = time.strftime('%m %d %y', time.localtime(todo['date']))
        with open(self.tmpNote, 'w') as fd:
            fd.write(self.todoEditTemplate.format(todo['todoText'],
                                                  todo['done'],
                                                  dateStr))

        self.addByEditor(ID)

    def new(self, dummy=None):
        """

        """
        with open(self.tmpNote, 'w') as fd:
            fd.write(self.todoTemplate)

        self.addByEditor()

    def processTodo(self):
        """

        """
        try:
            with open(self.tmpNote) as fd:
                lines = fd.read()
        except IOError:
            print("Config file doesn't exist, exiting")
            sys.exit(-1)

        todoText = lines[lines.index('TODO') + 4: lines.index('DONE')]
        todoText = todoText.split('\n')
        todoText = filter(lambda x: x != '', todoText)
        todoText = map(lambda x: x.rstrip(), todoText)
        todoText = '\n'.join(todoText)
        self.todoText = todoText

        done = lines[lines.index('DONE') + 4: lines.index('DATE - MM DD YY')]
        doneText = done.split('\n')
        doneText = filter(lambda x: x != '', doneText)
        doneText = map(lambda x: x.rstrip(), doneText)
        doneText = '\n'.join(doneText)
        doneText = doneText.lower()
        dt = doneText
        first_test = ('t' in dt or 'true' in dt or 'yes' in dt)
        second_test = ('f' not in dt or 'false' not in dt or 'no' not in dt)
        if first_test and second_test:
            self.done = True
        else:
            self.done = False

        date = lines[lines.index('DATE - MM DD YY') + 15: -1]
        date = date.strip()
        self.date = time.mktime(time.strptime(date, "%m %d %y"))

    def addByEditor(self, ID=None):
        """

        """
        ID = scrubID(ID)
        self.startEditor(3)
        self.processTodo()
        self.db.addItem(self.noteType, {"todoText": self.todoText,
                                        "done": self.done,
                                        "date": self.date}, ID)

    def showDone(self, dummy=None):
        """

        """
        IDs = self.db.getDone(True)
        [self.printItem(ii) for ii in IDs]

    def showUndone(self, dummy=None):
        """

        """
        IDs = self.db.getDone(False)
        [self.printItem(ii) for ii in IDs]

    def printItem(self, ID, color=True):
        """

        """

        result = self.db.getItem(ID)
        todoText = result['todoText']
        if result['done']:
            done = "done"
        else:
            done = "not done"
        date = time.strftime("%a %b %d", time.localtime(result['date']))

        order = [todoText, done, date]
        order = [ii for ii in order if ii]  # remove all the empty strings
        resultsStr = ", ".join(order)
        timestamps = result['timestamps']
        timestamp = time.localtime(max(timestamps))
        noteDate = time.strftime("%a, %b %d", timestamp)
        if color:
            print u"{5}{6} {4}{2}{0}:{3} {1}".format(noteDate,
                                                     resultsStr,
                                                     colors['foreground red'],
                                                     colors['reset'],
                                                     colors['hicolor'],
                                                     colors['foreground blue'],
                                                     int(ID))
        else:
            s = u"{0} {1}:{2}".format(int(ID), noteDate, resultsStr)
            s = s.encode('utf-8')
            print s


class Contact(NoteBaseClass):

    def __init__(self, db):
        super(Contact, self).__init__(db)
        self.noteType = "contacts"
        self.contactTemplate = u"NAME\n\n\n\nAFFILIATION\n\n\n\nEMAIL\n\n\n\n" +\
                               u"MOBILE PHONE\n\n\n\nHOME PHONE\n\n\n\nWORK PHONE" +\
                               u"\n\n\n\nADDRESS\n\n\n"
        self.contactEditTemplate = u"NAME\n\n{0}\n\nAFFILIATION\n\n{1}\n\n" +\
                                   u"EMAIL\n\n{2}\n\nMOBILE PHONE\n\n{3}\n\n" +\
                                   u"HOME PHONE\n\n{4}\n\n" +\
                                   u"WORK PHONE\n\n{5}\n\nADDRESS\n\n\n"
        self.keys = ["NAME",
                     "AFFILIATION",
                     "EMAIL",
                     "MOBILE PHONE",
                     "HOME PHONE",
                     "WORK PHONE",
                     "ADDRESS"]
        self.contactInfo = {}

    def edit(self, ID):

        ID = scrubID(ID)
        origContact = self.db.getItem(ID)
        self.contactEditTemplate

        editText = self.contactEditTemplate.format(origContact['NAME'],
                                                   origContact['AFFILIATION'],
                                                   origContact['EMAIL'],
                                                   origContact['MOBILE PHONE'],
                                                   origContact['HOME PHONE'],
                                                   origContact['WORK PHONE'],
                                                   origContact['ADDRESS'])

        with open(self.tmpNote, 'w') as fd:
            fd.write(editText)

        self.addByEditor(ID)

    def new(self, dummy=None):
        with open(self.tmpNote, 'w') as fd:
            fd.write(self.contactTemplate)

        self.addByEditor()

    def processContact(self):
        try:
            with open(self.tmpNote) as fd:
                lines = fd.read()
        except IOError:
            print("Note file file doesn't exist, exiting")
            sys.exit(-1)

        keys = copy.deepcopy(self.keys)
        keys.reverse()

        for k in keys:
            self.contactInfo[k] = (lines.split(k)[-1]).strip()
            lines = " ".join(lines.split(k)[0:-1])

    def printItem(self, ID, color=True):
        """

        """
        result = self.db.getItem(ID)
        name = result['NAME']
        work_phone = result['WORK PHONE']
        affiliation = result['AFFILIATION']
        mobile_phone = result['MOBILE PHONE']
        address = result['ADDRESS']
        email = result['EMAIL']
        home_phone = result['HOME PHONE']

        order = [name,
                 affiliation,
                 email,
                 mobile_phone,
                 work_phone,
                 home_phone,
                 address]
        order = [ii for ii in order if ii]  # remove all the empty strings
        resultsStr = ", ".join(order)
        timestamps = result['timestamps']
        timestamp = time.localtime(max(timestamps))
        noteDate = time.strftime("%a, %b %d", timestamp)
        if color:
            print u"{5}{6} {4}{2}{0}:{3} {1}".format(noteDate,
                                                     resultsStr,
                                                     colors['foreground red'],
                                                     colors['reset'],
                                                     colors['hicolor'],
                                                     colors['foreground blue'],
                                                     int(ID))
        else:
            s = u"{0} {1}: {2}".format(int(ID), noteDate, resultsStr)
            s = s.encode('utf-8')
            print s

    def addByEditor(self, ID=None):
        """

        """
        self.startEditor(3)
        self.processContact()
        self.db.addItem("contacts", self.contactInfo)
