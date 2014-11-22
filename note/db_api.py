from abc import ABCMeta, abstractmethod


class dbBaseClass:
    __metaclass__ = ABCMeta

    @abstractmethod
    def addItem(self, itemType, itemContents):
        pass

    @abstractmethod
    def getItem(self, itemID):
        pass

    @abstractmethod
    def searchForItem(self, searchInfo):
        pass

    @abstractmethod
    def deleteItem(self, itemID):
        pass

    @abstractmethod
    def makeBackupFile(self):
        pass
