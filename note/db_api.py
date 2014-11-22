from abc import ABCMeta, abstractmethod


class dbBaseClass:
    __metaclass__ = ABCMeta

    @abstractmethod
    def addItem(self, itemType, itemContents, itemID=None):
        pass

    @abstractmethod
    def getItem(self, itemID):
        pass

    @abstractmethod
    def searchForItem(self, searchInfo, resultLimit=20, sortBy="relevance"):
        pass

    @abstractmethod
    def deleteItem(self, itemID):
        pass

    @abstractmethod
    def makeBackupFile(self, dstPath, fileName):
        pass
