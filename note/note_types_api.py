import os
import subprocess as SP
from util import which
from abc import ABCMeta
from abc import abstractmethod


class NoteBaseClass(object):
    __metaclass__ = ABCMeta

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
