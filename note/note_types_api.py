import re
import sys
import time
import copy
from util import scrubID
from util import colors
from note_api import NoteBaseClass


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
