#!/usr/bin/env python

from db_api import dbBaseClass
import pymongo
import time
import os
import sys
import subprocess as SP


class mongoDB(dbBaseClass):

    def __init__(self, dbName, uri=None):
        """
            :desc: Initialize the database driver
            :param str dbName: The name of the database in mongo
            :param str uri: The Mongo URI to use
        """
        self.dbName = dbName

        try:
            self.client = pymongo.MongoClient(uri)
        except pymongo.errors.ConnectionFailure:
            print 'ERROR: Cannot open connection to database'
            sys.exit(1)

        # Make sure that text search is enabled for this database
        adminDB = self.client['admin']
        cmd = {"getParameter": 1, "textSearchEnabled": 1}
        textSearchEnabled = adminDB.command(cmd)['textSearchEnabled']

        if not textSearchEnabled:
            adminDB.command({"setParameter": 1, "textSearchEnabled": "true"})

        # Create database
        self.noteDB = self.client[self.dbName]

        # Initialize
        query = ({"currentMax": {"$exists": True}})
        if self.noteDB.IDs.find(query).count() == 0:
            self.noteDB['IDs'].insert({"currentMax": 0})

        query = {"unusedIDs": {"$exists": True}}
        if self.noteDB.IDs.find(query).count() == 0:
            self.noteDB['IDs'].insert({"unusedIDs": []})

        if 'label' not in self.noteDB.collection_names():
            self.noteDB.create_collection('label')

    def addItem(self, itemType, itemContents, itemID=None):
        """
            :param str itemType: The type of the item, note, place, todo
            :param dict itemContents: A dictionary of the item contents
            :param int itemID: When editing a note, send the ID along with it
        """

        if itemType not in self.noteDB.collection_names():
            fields = [(ii, pymongo.TEXT) for ii in itemContents]
            self.noteDB[itemType].ensure_index(fields)

        collection = self.noteDB[itemType]

        if itemID is None:
            itemContents['timestamps'] = [time.time()]
            itemID = self.getNewID()
            itemContents["ID"] = itemID
            collection.insert(itemContents)
        else:
            _id = collection.find_one({"ID": itemID})["_id"]
            timestamps = collection.find_one({"ID": itemID})["timestamps"]
            timestamps.append(time.time())
            itemContents["timestamps"] = timestamps
            itemContents["ID"] = itemID
            collection.update({"_id": _id}, itemContents)

        return itemID

    def addLabel(self, label_name, ID):
        """

        """

        if self.getIDByLabel(label_name) is not None:
            return None

        doc = {"name": label_name, "ID": ID}
        self.noteDB['label'].insert(doc)

        return doc

    def getIDByLabel(self, label_name):
        """

        """
        doc = {"name": label_name}
        r = self.noteDB['label'].find_one(doc)

        if r is None:
            return None

        if 'ID' in r:
            return r['ID']
        else:
            return None

    def deleteLabel(self, label_name):
        """

        """

        doc = {"name": label_name}
        self.noteDB['label'].remove(doc)

        return

    def getNewID(self):
        """

            :desc: Get a new ID by either incrementing the currentMax ID
                   or using an unusedID
            :returns: A new, valid, ID
            :rval: int
        """
        idCollection = self.noteDB['IDs']
        query = {"unusedIDs": {"$exists": True}}
        unusedIDs = idCollection.find_one(query)['unusedIDs']

        if not unusedIDs:
            query = {"currentMax": {"$exists": True}}
            ID = idCollection.find_one(query)['currentMax'] + 1
            idCollection.update({"currentMax": ID - 1}, {"currentMax": ID})
        else:
            query = {"unusedIDs": {"$exists": True}}
            unusedIDs = idCollection.find_one(query)['unusedIDs']
            ID = min(unusedIDs)
            unusedIDs.remove(ID)
            idCollection.update({"unusedIDs": {"$exists": True}},
                                {"$set": {"unusedIDs": unusedIDs}})

        return int(ID)

    def getItem(self, itemID):
        """
           :desc: Given an ID return the note JSON object
                   {u'note': u'note8',
                    u'ID': 3.0,
                    u'tags': [u'8'],
                    u'timestamps': [1381719620.315899]}
           :param int itemID: The item ID, an integer
           :returns: The matching note
           :rval: int
        """
        collections = self.get_data_collections()

        for coll in collections:
            note = self.noteDB[coll].find_one({"ID": itemID})
            if note is not None:
                del note["_id"]
                note['type'] = coll
                break

        return note

    def getAllItemTypes(self):
        """
            :desc: Fetches a list of item types
            :returns: A list of item types:
            :rval: list
        """

        collections = self.noteDB.collection_names()
        return collections

    def getItemType(self, itemID):
        """
            :desc: Given an itemID, return the "type" i.e. the collection
                   it belongs to.
            :param int itemID: The item ID, an integer
            :returns: The note type
            :rval: str
        """

        collections = self.getAllItemTypes()

        for coll in collections:
            note = self.noteDB[coll].find_one({"ID": itemID})
            if note is not None:
                return coll

    def searchForItem(self, searchInfo, resultLimit=20, sortBy="relevance"):
        """
            :desc: Given a search term returns a list of results that match
                   that term:

                   [{u'score': 5.5,
                     u'obj': {u'note': u'note8',
                              u'ID': 3.0,
                              u'timestamps': [1381719620.315899]}}]
            :param str searchInfo: The search term
            :returns: A list of matching notes
            :rval: list
        """

        searchResults = []

        colls = self.get_data_collections()

        proj = {"_id": 0}
        for coll in colls:
            res = self.noteDB.command("text",
                                      coll,
                                      search=searchInfo,
                                      project=proj,
                                      limit=resultLimit)['results']
            for ii in res:
                ii['type'] = coll
            searchResults.extend(res)

        if sortBy.lower() == "date":
            k = (lambda x: max(x['obj']['timestamps']))
            searchResults = sorted(searchResults, key=k)
        elif sortBy.lower() == "id":
            k = (lambda x: x['obj']['ID'])
            searchResults = sorted(searchResults, key=k)

        return searchResults

    def deleteItem(self, itemID):
        """
           :desc: Deletes item with ID = itemID, takes care of IDs collection
           :param itemID: The item ID to delete
           :type itemID: int
           :raises: ValueError
           :returns ID: The ID of the deleted item
           :rval: int
        """
        collections = self.get_data_collections()

        query = {"currentMax": {"$exists": True}}
        currentMax = self.noteDB["IDs"].find_one(query)['currentMax']
        query = {"unusedIDs": {"$exists": True}}
        unusedIDs = self.noteDB['IDs'].find_one(query)['unusedIDs']

        if (itemID > currentMax) or (itemID in unusedIDs):
            raise ValueError("ID {0} does not exist".format(itemID))

        # Find document with ID
        for coll in collections:
            self.noteDB[coll].remove({"ID": itemID})

        if currentMax == itemID:
            self.noteDB['IDs'].update({"currentMax": currentMax},
                                      {"currentMax": currentMax - 1})
        else:
            unusedIDs.append(itemID)
            self.noteDB['IDs'].update({"unusedIDs": {"$exists": True}},
                                      {"unusedIDs": unusedIDs})

        return itemID

    def getDone(self, done):
        """
            :desc: Fetches a list of all the done ToDs
            :param bool done: done or undone?
            :returns: A list of matching IDs
            :rval: list
        """

        doneItems = self.noteDB['todo'] \
                        .find({"done": done}) \
                        .sort("date", pymongo.DESCENDING)
        IDs = [ii['ID'] for ii in doneItems]
        return IDs

    def makeBackupFile(self, dstPath, fileName):
        """
            :param str dstPath: The destination path of the backup file
            :param str fileName: The filename to use
        """

        with open(os.devnull) as devnull:
            SP.call(['mongodump', '--db', self.dbName, '--out', dstPath],
                    stdout=devnull,
                    stderr=devnull)
            SP.call(['zip',
                     '-r',
                     os.path.join(dstPath, fileName),
                     os.path.join(dstPath, self.dbName)],
                    stdout=devnull,
                    stderr=devnull)

        SP.call(['rm', '-rf', os.path.join(dstPath, self.dbName)])

    def getByTime(self, startTime=None, endTime=None):
        """
            :desc: Get all the notes in the given time window
            :param int startTime: The begining of the window
            :param int endTime: The end of the window
            :returns: A list of IDs
            :ravl: list
        """
        collections = self.get_data_collections()

        if startTime is not None:
            startTime = float(startTime)
        if endTime is not None:
            endTime = float(endTime)

        if startTime is not None and endTime is not None:
            timeQuery = {"$and": [{"timestamps": {"$gt": startTime}},
                                  {"timestamps": {"$lt": endTime}}]}
        elif startTime is not None and endTime is None:
            timeQuery = {"timestamps": {"$gt": startTime}}
        elif startTime is None and endTime is not None:
            timeQuery = {"timestamps": {"$lt": endTime}}

        IDs = []

        for coll in collections:
            docs = self.noteDB[coll].find(timeQuery, {"ID": 1, "_id": 0})
            for doc in docs:
                IDs.append(doc['ID'])

        return IDs

    def verify(self):
        """
            :desc: Verifies the integrity of the database, specifically checks
                   the values for unusedIDs and currentMax
            :returns: A boolean indicating whether the database is valid or
                      not
            :rval: bool
        """
        collections = self.get_data_collections()

        allIDs = []
        for coll in collections:
            IDs = self.noteDB[coll].find({"ID": {"$exists": True}},
                                         {"ID": 1, "_id": 0})
            for ID in IDs:
                allIDs.append(int(ID["ID"]))

        query = {"currentMax": {"$exists": True}}
        maxID = int(self.noteDB['IDs'].find_one(query)["currentMax"])
        query = {"unusedIDs": {"$exists": True}}
        unusedIDs = self.noteDB['IDs'].find_one(query)["unusedIDs"]
        unusedIDs = [int(ii) for ii in unusedIDs]

        unusedIDsMatch = True
        for ID in allIDs:
            if ID in unusedIDs:
                unusedIDsMatch = False

        maxIDMatch = True
        if maxID is not max(allIDs):
            maxIDMatch = False

        if maxIDMatch and unusedIDsMatch:
            print "Database is valid"
        elif not maxIDMatch and not unusedIDsMatch:
            print "Database not valid, max ID and unused IDs are incorrent"
        elif not maxIDMatch:
            print "Database not valid, max ID is incorrent"
        elif not unusedIDsMatch:
            print "Database not valid, unusedIDs is incorrent"

    def get_data_collections(self):
        collections = self.noteDB.collection_names()
        collections.remove(u'system.indexes')
        collections.remove(u'IDs')
        collections.remove(u'label')

        return collections
