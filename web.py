#!/usr/bin/env python

__author__ = "Devin Kelly"
__todo__ = """
"""

import time
import json
import re
import os
import sys
from flask import Flask
from flask import request
from flask import Response
from jinja2 import Environment
from jinja2 import FileSystemLoader
from functools import wraps
from n import mongoDB

app = Flask(__name__)
app.debug = True
db = mongoDB("note")
j2_env = Environment(loader=FileSystemLoader('templates'), trim_blocks=True)


def check_auth(username, password):
   """This function is called to check if a username /
   password combination is valid.
   """

   with open(os.path.expanduser("~/.note.conf")) as fd:
      config = json.loads(fd.read())

   try:
      u = config['server']['login']['username']
      p = config['server']['login']['password']
   except:
      print "cannot start server"
      sys.exit(1)

   return username == u and password == p


def authenticate():
   """Sends a 401 response that enables basic auth"""
   return Response(
      'Could not verify your access level for that URL.\n'
      'You have to login with proper credentials', 401,
      {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
   with open(os.path.expanduser("~/.note.conf")) as fd:
      config = json.loads(fd.read())

   try:
      login = config['server']['login']
      if 'username' in login.keys() and 'password' in login.keys():
         authOn = True
      else:
         authOn = False

   except KeyError:
      authOn = False

   if authOn:

      @wraps(f)
      def decorated(*args, **kwargs):
         auth = request.authorization
         if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
         return f(*args, **kwargs)
   else:

      @wraps(f)
      def decorated(*args, **kwargs):
            return f(*args, **kwargs)

   return decorated


@app.route(r'/search', methods=["GET", "POST"])
@requires_auth
def search():

   if request.method == "GET":
      pages = {"cmd": {"link": "search", "name": "Search"}, "title": "Search"}
      t = j2_env.get_template('search.html')
      s = t.render(p=pages)
   elif request.method == "POST" and request.form["api"] == "false":
      pages = {"cmd": {"link": "search", "name": "Search Result"}, "title": "Search Result"}
      t = j2_env.get_template('searchResult.html')

      term = request.form["term"]
      results = db.searchForItem(term)
      resultsHTML = []
      for item in results:
         ID = int(item['obj'][u"ID"])
         resultsHTML.append(genHTML(ID))

      s = t.render(p=pages, searchResults=resultsHTML)
   elif request.method == "POST" and request.form["api"] == "true":
      term = request.form["term"]
      s = json.dumps(db.searchForItem(term))
   else:
      s = "not valid"

   s = addLinks(s)
   return s


@app.route('/delete', methods=["GET", "POST"])
@requires_auth
def Delete():
   pages = {"cmd": {"link": "delete", "name": "Delete"}, "title": "Delete"}
   if request.method == "GET":
      t = j2_env.get_template('delete.html')
      s = t.render(p=pages)
   elif request.method == "POST" and request.form["api"] == "false":
      ID = int(request.form["ID"])
      db.deleteItem(ID)
      t = j2_env.get_template('deleted.html')
      s = t.render(p=pages, itemID=ID)
   elif request.method == "POST" and request.form["api"] == "true":
      ID = int(request.form["ID"])
      result = db.deleteItem(ID)
      retVal = {"result": result, "ID": ID}
      s = json.dumps(retVal)
   else:
      s = u"not valid"

   return s


@app.route('/note', methods=["GET"])
@requires_auth
def start():
   pages = {"cmd": {"link": "note", "name": "Note"}, "title": "Note"}
   t = j2_env.get_template('note.html')
   s = t.render(p=pages)
   return s


@app.route('/notes', methods=["GET"])
@requires_auth
def Notes():
   fourWeeks = 4.0 * 7.0 * 24.0 * 60.0 * 60.0
   now = time.time()
   fourWeeksAgo = now - fourWeeks
   items = db.getByTime(startTime=fourWeeksAgo, endTime=now)
   pages = {"cmd": {"link": "search", "name": "Search Result"}, "title": "Search Result"}
   t = j2_env.get_template('searchResult.html')

   resultsHTML = []
   for ID in items:
      tmpHTML = addLinks(genHTML(ID))
      resultsHTML.append(tmpHTML)

   s = t.render(p=pages, searchResults=resultsHTML)
   return s


@app.route('/newNote', methods=["GET", "POST"])
@requires_auth
def NewNote():

   pages = {"cmd": {"link": "newNote", "name": "New Note"}, "title": "New Note"}
   if request.method == "GET":
      t = j2_env.get_template('newNote.html')
      s = t.render(p=pages)
   elif request.method == "POST" and request.form["api"] == "false":
      tags = request.form["tags"]
      noteText = request.form["noteText"]
      db.addItem("notes", {"noteText": noteText, "tags": tags})

      t = j2_env.get_template('noteAdded.html')
      s = t.render(p=pages, noteText=noteText, tags=tags )

   elif request.method == "POST" and request.form["api"] == "true":
      noteText = request.form["noteText"]
      tags = request.form["tags"].split(",")
      note = {"noteText": noteText, "tags": tags, "timestamp": time.time()}
      db.addItem("notes", {"noteText": noteText, "tags": tags})
      s = json.dumps(note)
   return s


@app.route('/newContact', methods=["GET", "POST"])
@requires_auth
def NewContact():
   pages = {"cmd": {"link": "newContact", "name": "New Contact"}, "title": "New Contact"}
   if request.method == "GET":
      t = j2_env.get_template('newContact.html')
      s = t.render(p=pages)
   elif request.method == "POST" and request.form["api"] == "false":
      name = request.form["name"]
      affiliation = request.form["affiliation"]
      email = request.form["email"]
      work = request.form["work"]
      home = request.form["home"]
      mobile = request.form["mobile"]
      address = request.form["address"]

      contactInfo = {"NAME": name,
                     "WORK PHONE": work,
                     "AFFILIATION": affiliation,
                     "MOBILE PHONE": mobile,
                     "ADDRESS": address,
                     "EMAIL": email,
                     "HOME PHONE": home}
      db.addItem("contacts", contactInfo)
      t = j2_env.get_template('contactAdded.html')
      s = t.render(p=pages, contact=contactInfo)
   elif request.method == "POST" and request.form["api"] == "true":
      contactText = request.form["contactText"]
      tags = request.form["tags"].split(",")
      contact = {"contactText": contactText, "tags": tags, "timestamp": time.time()}
      s = json.dumps(contact)
   return s


@app.route('/newTodo', methods=["GET", "POST"])
@requires_auth
def NewTodo():

   pages = {"cmd": {"link": "newTodo", "name": "New ToDo"}, "title": "New ToDo"}
   if request.method == "GET":
      t = j2_env.get_template('newTodo.html')
      s = t.render(p=pages)
   elif request.method == "POST" and request.form["api"] == "false":
      todoText = request.form["todoText"]
      done = str(request.form['options'])
      date = request.form['date']
      done = (done == "done")

      todoItem = {"todoText": todoText, "done": done, "date": time.mktime(time.strptime(date, "%m/%d/%Y"))}
      db.addItem("todos", todoItem)
      todoItem['done'] = str(todoItem['done'])
      todoItem['date'] = str(todoItem['date'])
      t = j2_env.get_template('todoAdded.html')
      s = t.render(p=pages, todo=todoItem)
   elif request.method == "POST" and request.form["api"] == "true":
      todoText = request.form["todoText"]
      tags = request.form["tags"].split(",")
      todo = {"todoText": todoText, "tags": tags, "timestamp": time.time()}
      db.addItem("todos", {"todoText": todoText, "done": done, "date": time.mktime(time.strptime(date, "%m/%d/%Y"))})
      s = json.dumps(todo)
   return s


def genHTML(ID):

   itemType = db.getItemType(ID)
   item = db.getItem(ID)

   s = u""
   if itemType == "todos":
      s += u"<p>"
      s += re.sub("\n", "<br>", str(item['todoText']))
      s += u"</p>"
      s += u"<br>"
      s += u"<p>"
      if item["done"]:
         s += "done"
      else:
         s += u"not done"
      s += u"</p>"
      s += u"<br>"
      s += u"<p>"
      s += u'ID: {0}'.format(ID)
      s += u"</p>"

   elif itemType == "notes":
      s += u"<p>"
      s += re.sub(u"\n", u"<br>", item['noteText'])
      s += u"</p>"
      s += u"<br>"
      s += u"<p>"
      s += u'ID: {0}'.format(ID)
      s += u"</p>"

   elif itemType == "contact":
      s += u"<p>"
      s += item['NAME'] + u"<br>"
      s += item['EMAIL'] + u"<br>"
      s += item['AFFILIATION'] + u"<br>"
      s += item['MOBILE'] + u"<br>"
      s += item['HOME'] + u"<br>"
      s += item['WORK'] + u"<br>"
      s += item['ADDRESS'] + u"<br>"
      s += u"</p>"
      s += u"<br>"
      s += u"<p>"
      s += u'ID: {0}'.format(ID)
      s += u"</p>"

   return s


def addLinks(s):

   part1 = re.compile(r"(^|)(([\w]+?://[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)
   part2 = re.compile(r"#(^|)(((www|ftp)\.[\w\#$%&~.\-;:=,?@\[\]+]*)(/[\w\#$%&~/.\-;:=,?@\[\]+]*)?)", re.IGNORECASE | re.DOTALL)

   s = part1.sub(r'\1<a href="\2">\3</a>', s)
   s = part2.sub(r'\1<a href="http:/\2">\3</a>', s)

   return s


def main():
   app.run()

if __name__ == "__main__":
   main()
