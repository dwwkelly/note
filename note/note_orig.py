#!/usr/bin/env python

__author__ = "Devin Kelly"
__email__ = "dwwkelly@fastmail.fm"
__version__ = 0.1
__todo__ = '''
-add support for dropbox/box backups
-make install command that copies template files to home
-import contacts from google -
   https://developers.google.com/google-apps/contacts/v3/
-switch to a SQL database?
-add goodreads book
'''

__added_features__ = '''
-make a note info command which shows note, tags and all other metadata
-add ability to change todo state
-add ability to edit note/todo/contact
-add a verify command that checks IDs collection against other collections
   for consistency
-add ability to delete note/todo/contact
-add system for handling contact (email, phone, address, etc)
-complete encrpytion implementation
-fine tune search
-possibly rewrite code to take utilize inheritance
-when editing a note, should the timestamp be the original, the newest or a
   list of all edits?
'''

import subprocess
import argparse
import os
import re
import sys
import time
import copy
import subprocess as SP
import pymongo
import shutil
import json
import datetime
import calendar
from abc import ABCMeta, abstractmethod

try:
   import gnupg
except ImportError:
   pass

try:
   import dropbox
except ImportError:
   pass


RS = "\033[0m"     # reset
HC = "\033[1m"     # hicolor
UL = "\033[4m"     # underline
INV = "\033[7m"    # invert foreground and background
FBLK = "\033[30m"
FRED = "\033[31m"
FGRN = "\033[32m"
FYEL = "\033[33m"
FBLE = "\033[34m"
FMAG = "\033[35m"
FCYN = "\033[36m"
FWHT = "\033[37m"
BBLK = "\033[40m"
BRED = "\033[41m"
BGRN = "\033[42m"
BYEL = "\033[43m"
BBLE = "\033[44m"
BMAG = "\033[45m"
BCYN = "\033[46m"
BWHT = "\033[47m"


def main():

   runner = Runner()
   runner.start()


def scrubID(ID):

   if type(ID) == list:
      return int(ID[0])
   elif type(ID) == str:
      return int(ID)
   elif type(ID) == int:
      return ID
   else:
      return None


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


class mongoDB(dbBaseClass):

   def __init__(self, dbName, uri=None):
      """

      """
      self.dbName = dbName

      if uri:
         self.client = pymongo.MongoClient(uri)
      else:
         self.client = pymongo.MongoClient()
      adminDB = self.client['admin']
      cmd = {"getParameter": 1, "textSearchEnabled": 1}
      textSearchEnabled = adminDB.command(cmd)['textSearchEnabled']

      if not textSearchEnabled:
         adminDB.command({"setParameter": 1, "textSearchEnabled": "true"})

      self.noteDB = self.client[self.dbName]

      if self.noteDB.IDs.find({"currentMax": {"$exists": True}}).count() == 0:
         self.noteDB['IDs'].insert({"currentMax": 0})

      if self.noteDB.IDs.find({"unusedIDs": {"$exists": True}}).count() == 0:
         self.noteDB['IDs'].insert({"unusedIDs": []})

   def addItem(self, itemType, itemContents, itemID=None):
      """
         itemType really means the collection name or table name
      """
      collection = self.noteDB[itemType]
      Weights = {ii: 1 for ii in itemContents.keys()}
      if collection.name not in self.noteDB.collection_names():
         collection.create_index([(collection.name, "text"), ("tags", "text")],
                                 weights=Weights)

      if itemID is None:
         itemContents['timestamps'] = [time.time()]
         itemContents["ID"] = self.getNewID()
         collection.insert(itemContents)
      else:
         _id = collection.find_one({"ID": itemID})["_id"]
         timestamps = collection.find_one({"ID": itemID})["timestamps"]
         timestamps.append(time.time())
         itemContents["timestamps"] = timestamps
         itemContents["ID"] = itemID
         collection.update({"_id": _id}, itemContents)

   def getNewID(self):
      """
         Get a new ID by either incrementing the currentMax ID
         or using an unusedID
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
         Given an ID return the note JSON object

         {u'noteText': u'note8',
          u'ID': 3.0,
          u'tags': [u'8'],
          u'timestamps': [1381719620.315899]}

      """
      collections = self.noteDB.collection_names()
      collections.remove(u'system.indexes')
      collections.remove(u'IDs')

      for coll in collections:
         note = self.noteDB[coll].find_one({"ID": itemID})
         if note is not None:
            del note["_id"]
            break

      return note

   def getAllItemTypes(self):
      """

      """

      collections = self.noteDB.collection_names()
      collections.remove(u'system.indexes')
      collections.remove(u'IDs')
      return collections

   def getItemType(self, itemID):
      """
         Given an itemID, return the "type" i.e. the collection it belongs to.
      """

      collections = self.getAllItemTypes()

      for coll in collections:
         note = self.noteDB[coll].find_one({"ID": itemID})
         if note is not None:
            return coll

   def searchForItem(self, searchInfo, resultLimit=20, sortBy="relevance"):
      """
      Given a search term returns a list of results that match that term:

         [{u'score': 5.5,
           u'obj': {u'noteText': u'note8',
                    u'ID': 3.0,
                    u'timestamps': [1381719620.315899]}}]

      """

      searchResults = []

      colls = self.noteDB.collection_names()
      colls.remove(u'system.indexes')
      colls.remove(u'IDs')

      proj = {"_id": 0}
      for coll in colls:
         res = self.noteDB.command("text",
                                   coll,
                                   search=searchInfo,
                                   project=proj,
                                   limit=resultLimit)['results']
         for ii in res:
            ii['itemType'] = coll
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
         Deletes item with ID = itemID, takes care of IDs collection
      """
      collections = self.noteDB.collection_names()
      collections.remove(u'system.indexes')
      collections.remove(u'IDs')

      query = {"currentMax": {"$exists": True}}
      currentMax = self.noteDB["IDs"].find_one(query)['currentMax']
      query = {"unusedIDs": {"$exists": True}}
      unusedIDs = self.noteDB['IDs'].find_one(query)['unusedIDs']

      if (itemID > currentMax) or (itemID in unusedIDs):
         print(u"Item {0} does not exist".format(itemID))
         sys.exit(1)

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

   def getDone(self, done):

      doneItems = self.noteDB['todos'] \
                      .find({"done": done}) \
                      .sort("date", pymongo.DESCENDING)
      IDs = [ii['ID'] for ii in doneItems]
      return IDs

   def makeBackupFile(self, dstPath, fileName):

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
      collections = self.noteDB.collection_names()
      collections.remove(u'system.indexes')
      collections.remove(u'IDs')

      startTime = float(startTime)
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
      collections = self.noteDB.collection_names()
      collections.remove(u'system.indexes')
      collections.remove(u'IDs')

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


def sqliteDB(dbBaseClass):

   def __init__(self):

      return

   def addItem(self, itemType, itemContents):

      return

   def getItem(self, itemID):

      return

   def searchForItem(self, searchInfo):

      return

   def deleteItem(self, itemID):

      return

   def makeBackupFile(self):

      return


class NoteBaseClass(object):
   __metaclass__ = ABCMeta

   """ Virtual Methods """

   @abstractmethod
   def __init__(self, db):
      self.homeDir = os.path.expanduser('~')
      self.tmpNote = os.path.join(self.homeDir, '.note.TMP')
      self.editor = os.getenv('EDITOR')
      self.db = db
      return

   @abstractmethod
   def edit(self, ID):
      return

   @abstractmethod
   def printItem(self):
      return

   @abstractmethod
   def new(self):
      return

   """ Concrete Methods """

   def delete(self, ID):
      """

      """
      try:
         ID = int(ID[0])
      except TypeError:
         pass

      self.db.deleteItem(ID)

   def startEditor(self, startingLine=1):
      if self.editor == "/usr/bin/vim" or self.editor == '/usr/local/bin/vim':
         subprocess.call([self.editor, "+{0}".format(startingLine),
                          "-c", "startinsert", self.tmpNote])
         try:
            os.remove("{0}.swp".format(self.tmpNote))
            os.remove("{0}".format(self.tmpNote))
         except OSError:
            pass
      else:
         subprocess.call([self.editor, self.tmpNote])


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
      result = self.db.getItem(ID)
      noteText = result['noteText']
      timestamps = result['timestamps']
      timestamp = time.localtime(max(timestamps))
      noteDate = time.strftime("%a, %b %d", timestamp)
      if color:
         print u"{5}{6} {4}{2}{0}:{3} {1}".format(noteDate,
                                                  noteText,
                                                  FRED,
                                                  RS,
                                                  HC,
                                                  FBLE,
                                                  int(ID))
      else:
         s = u"{2} {0}: {1}".format(noteDate, noteText, int(ID))
         s = s.encode('utf-8')
         print s

   def processNote(self):

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
      """@todo: Makes the temporary file for a new note or
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
      self.startEditor(3)
      self.processNote()

      if self.noteText:
         self.db.addItem("notes",
                         {"noteText": self.noteText, "tags": self.tags},
                         itemID=ID)


class Place(NoteBaseClass):
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
      ID = scrubID(ID)
      result = self.db.getItem(ID)
      noteText = result['noteText']
      addressText = result['addressText']
      placeText = result['placeText']
      timestamps = result['timestamps']
      timestamp = time.localtime(max(timestamps))
      noteDate = time.strftime("%a, %b %d", timestamp)

      if color:
         print u"{0}{1} {2}{3}{4}:{5}\n{6}\n{7}".format(FBLE,
                                                        int(ID),
                                                        FRED,
                                                        RS,
                                                        noteDate,
                                                        placeText,
                                                        noteText,
                                                        addressText)
      else:
         s = u"{0} {1}: {2}\n{3}\n{4}".format(int(ID),
                                              noteDate,
                                              placeText,
                                              noteText,
                                              addressText)
         s = s.encode('utf-8')
         print s

   def addByEditor(self, ID=None):

      self.startEditor(3)
      self.processPlace()
      self.db.addItem(self.noteType, {"noteText": self.noteText,
                                      "placeText": self.placeText,
                                      "addressText": self.addressText,
                                      "tags": self.tags}, ID)


class ToDo(NoteBaseClass):

   def __init__(self, db):
      super(ToDo, self).__init__(db)
      self.noteType = "todos"
      self.todoTemplate = u"TODO\n\n\n\nDONE\n\n\n\nDATE - MM DD YY\n\n\n"
      self.todoEditTemplate = u"TODO\n\n{0}\n\nDONE\n\n{1}\n\n" +\
                              u"DATE - MM DD YY\n\n{2}\n\n"

   def edit(self, ID):
      ID = scrubID(ID)
      todo = self.db.getItem(ID)
      dateStr = time.strftime('%m %d %y', time.localtime(todo['date']))
      with open(self.tmpNote, 'w') as fd:
         fd.write(self.todoEditTemplate.format(todo['todoText'],
                                               todo['done'],
                                               dateStr))

      self.addByEditor(ID)

   def new(self, dummy=None):
      with open(self.tmpNote, 'w') as fd:
         fd.write(self.todoTemplate)

      self.addByEditor()

   def processTodo(self):
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
      if ('t' in dt or 'true' in dt or 'yes' in dt) and \
         ('f' not in dt or 'false' not in dt or 'no' not in dt):
         self.done = True
      else:
         self.done = False

      date = lines[lines.index('DATE - MM DD YY') + 15: -1]
      date = date.strip()
      self.date = time.mktime(time.strptime(date, "%m %d %y"))

   def addByEditor(self, ID=None):
      ID = scrubID(ID)
      self.startEditor(3)
      self.processTodo()
      self.db.addItem(self.noteType, {"todoText": self.todoText,
                                      "done": self.done,
                                      "date": self.date}, ID)

   def showDone(self, dummy=None):
      IDs = self.db.getDone(True)
      [self.printItem(ii) for ii in IDs]

   def showUndone(self, dummy=None):
      IDs = self.db.getDone(False)
      [self.printItem(ii) for ii in IDs]

   def printItem(self, ID, color=True):

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
                                                  FRED,
                                                  RS,
                                                  HC,
                                                  FBLE,
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
                                                  FRED,
                                                  RS,
                                                  HC,
                                                  FBLE,
                                                  int(ID))
      else:
         s = u"{0} {1}: {2}".format(int(ID), noteDate, resultsStr)
         s = s.encode('utf-8')
         print s

   def addByEditor(self, ID=None):
      self.startEditor(3)
      self.processContact()
      self.db.addItem("contacts", self.contactInfo)


class Runner(object):

   def __init__(self):

      self.dbName = 'note'
      self.db = mongoDB(self.dbName)

      note = Note(self.db)
      todo = ToDo(self.db)
      place = Place(self.db)
      contact = Contact(self.db)
      self.itemTypes = {"notes": note,
                        "todos": todo,
                        "contacts": contact,
                        "places": place}

   def start(self):

      note = Note(self.db)
      todo = ToDo(self.db)
      place = Place(self.db)
      contact = Contact(self.db)
      self.itemTypes = {"notes": note,
                        "todos": todo,
                        "contacts": contact,
                        "places": place}

      self.commands = dict()
      self.commands['add'] = note.new
      self.commands['search'] = self.search
      self.commands['delete'] = note.delete
      self.commands['edit'] = note.edit
      self.commands['place'] = place.new

      self.commands['contact'] = contact.new
      self.commands['todo'] = todo.new
      self.commands['showDone'] = todo.showDone
      self.commands['showUndone'] = todo.showUndone
      self.commands['backup'] = self.backup
      self.commands['encrypt'] = self.encrypt
      self.commands['dropbox'] = self.pushToDropbox
      self.commands['lastMonth'] = self.lastMonth
      self.commands['thisMonth'] = self.thisMonth
      self.commands['info'] = self.info
      self.commands['verifyDB'] = self.verify
      self.commands['sID'] = self.search
      self.commands['sdate'] = self.search
      self.commands['srelevance'] = self.search

      self.parseOpts()

      if self.command in ['edit', 'delete', 'e', 'D']:
         itemType = self.db.getItemType(int(self.commandArgs[0]))
         self.commands['delete'] = self.itemTypes[itemType].delete
         self.commands['edit'] = self.itemTypes[itemType].edit

      # These are undocumented shortcuts
      self.commands['a'] = self.commands['add']
      self.commands['s'] = self.commands['search']
      self.commands['D'] = self.commands['delete']
      self.commands['e'] = self.commands['edit']
      self.commands['p'] = self.commands['place']

      self.commands['t'] = self.commands['todo']
      self.commands['d'] = self.commands['showDone']
      self.commands['u'] = self.commands['showUndone']
      self.commands['c'] = self.commands['contact']
      self.commands['b'] = self.commands['backup']
      self.commands['E'] = self.encrypt
      self.commands['i'] = self.info
      self.commands['V'] = self.verify

      with open(self.configFile, 'r') as fd:
         self.config = json.loads(fd.read())

      try:
         self.commands[self.command](self.commandArgs)
      except KeyError:
         print u"{0} does not exist".format(self.command)
         sys.exit(0)

   def search(self, searchTerm, color=True):
      searchTerm = searchTerm[0]

      if self.command == 'sID':
         sortBy = 'id'
      elif self.command == 'sdate':
         sortBy = 'date'
      else:
         sortBy = 'relevance'

      results = self.db.searchForItem(searchTerm, sortBy=sortBy)

      # FIXME This needs changing to be more generic
      for item in results:
         ID = item['obj'][u"ID"]
         itemType = self.db.getItemType(ID)
         self.itemTypes[itemType].printItem(ID, color=color)

   def parseOpts(self):
      parser = argparse.ArgumentParser(description="note")

      defaultConfigPath = os.path.expanduser('~/.config/note.json')
      parser.add_argument('--configFile', type=str, help='Path to config file',
                          default=defaultConfigPath)

      commandHelp = 'note: eligible commands are: {0}'
      commandHelp = commandHelp.format(', '.join(self.commands))
      parser.add_argument('command', metavar='cmd', type=str, nargs='+',
                          help=commandHelp)

      args = parser.parse_args()

      self.configFile = args.configFile
      self.command = args.command[0]

      self.commandArgs = args.command[1:]

   def backup(self, dst):

      if not dst:
         dst = '/tmp'
      else:
         dst = dst[0]

      self.backupName = 'note_backup.zip'
      self.db.makeBackupFile(dst, self.backupName)
      if dst is "/tmp":
         pwd = os.getcwd()
         shutil.move(os.path.join(dst, self.backupName),
                     os.path.join(pwd, self.backupName))

   def encrypt(self, dst):

      self.backup(dst)
      if not dst:
         dst = os.getcwd()
      else:
         dst = dst[0]

      self.initGPG()
      backupGPG = os.path.join(dst, 'note_backup.gpg')
      backupFile = os.path.join(dst, self.backupName)
      if self.key is not None:
         stream = open(backupFile, "rb")
         self.gpg.encrypt_file(stream,
                               [self.key['fingerprint']],
                               output=backupGPG)
         SP.call(['rm', '-rf', backupFile])
         print u"Encrypted Backup: {0}".format(backupGPG)
      else:
         print u"Could not encrpyt: {0}".format(backupFile)

      return backupGPG

   def initGPG(self):
      try:
         self.gpg = gnupg.GPG()
      except NameError:
         self.gpg = None
         self.key = None
         return

      private_keys = self.gpg.list_keys(True)
      usable_keys = []
      for key in private_keys:
         if time.time() < key['expires']:
            usable_keys.append(key)

      print u"Select key:"
      counter = 0
      for key in usable_keys:
         s = u"[{0}] Fingerprint: {1}, Key Length: {2}, UIDs: {3}"
         s = s.format(counter, key['fingerprint'], key['length'], key['uids'])
         print s
         counter = counter + 1

      data = int(sys.stdin.readline())

      if data == 0:
         self.key = None
      else:
         self.key = usable_keys[data - 1]

   def pushToDropbox(self, backupFile=None):

      token = self.config['dropbox']['token']

      gpgFile = self.encrypt([])

      client = dropbox.client.DropboxClient(token)

      with open(gpgFile) as f:
         response = client.put_file('/note_backup.gpg', f)
      print u"uploaded:", response

   def lastMonth(self, null=None):
      now = datetime.datetime.now()

      if now.month == 1:
         month = 12
         year = now.year - 1
      else:
         month = now.month - 1
         year = now.year

      # gets the number of days in a month
      day = calendar.monthrange(year, month)[1]

      firstOfMonth = datetime.datetime(year,
                                       month,
                                       day=1,
                                       hour=0,
                                       minute=0,
                                       second=0)
      endOfMonth = datetime.datetime(year,
                                     month,
                                     day=day,
                                     hour=23,
                                     minute=59,
                                     second=59)

      startTime = firstOfMonth.strftime('%s.%f')
      endTime = endOfMonth.strftime('%s.%f')

      IDs = self.db.getByTime(startTime=startTime, endTime=endTime)

      for ID in IDs:
         itemType = self.db.getItemType(ID)
         self.itemTypes[itemType].printItem(ID)

   def thisMonth(self, null=None):
      now = datetime.datetime.now()
      firstOfMonth = datetime.datetime(now.year,
                                       now.month,
                                       day=1,
                                       hour=0,
                                       minute=0,
                                       second=0)

      startTime = firstOfMonth.strftime('%s.%f')
      endTime = now.strftime('%s.%f')

      IDs = self.db.getByTime(startTime=startTime, endTime=endTime)

      for ID in IDs:
         itemType = self.db.getItemType(ID)
         self.itemTypes[itemType].printItem(ID)

   def info(self, ID):
      ID = scrubID(ID)

      info = self.db.getItem(ID)

      if not info:
         print 'No Results'
         return

      print u"{red}ID: {reset} {ID}".format(red=FRED, reset=RS, ID=int(ID))
      del info['ID']

      for k in info.keys():
         print u"{red}{key}: {reset} {value}".format(red=FRED,
                                                     reset=RS,
                                                     value=info[k],
                                                     key=k)

   def verify(self, null=None):

      self.db.verify()


if __name__ == '__main__':
   main()
