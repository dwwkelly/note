#!/usr/bin/env python

__author__ = "Devin Kelly"
__todo__ = """
"""

import time
import json
import os
import sys
import argparse
import markdown
from flask import Flask
from flask import request
from flask import Response
from flask import render_template
from flask import Markup
from functools import wraps
from note import mongoDB

app = Flask(__name__)
app.jinja_env.trim_blocks = True
db = mongoDB("note")


def parseArgs():
   parser = argparse.ArgumentParser(description='Run Note Web Server')
   parser.add_argument('--debug', '-d', default=False, action='store_true',
                       help='Turn on debug mode')

   args = parser.parse_args()

   return args


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
   return Response('Could not verify your access level for that URL.\n'
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
      s = render_template('search.html', p=pages)
   elif request.method == "POST" and request.form["api"] == "false":
      pages = {"cmd": {"link": "search", "name": "Search Result"},
               "title": "Search Result"}
      term = request.form["term"]
      s = request.form['options']
      results = db.searchForItem(term, sortBy=s)
      for r in results:
         r['obj']['noteText'] = Markup(markdown.markdown(r['obj']['noteText']))
      s = render_template('searchResult.html', p=pages, searchResults=results)
   elif request.method == "POST" and request.form["api"] == "true":
      term = request.form["term"]
      s = json.dumps(db.searchForItem(term))
   else:
      s = "not valid"

   return s


@app.route(r'/newPlace', methods=["GET", "POST"])
@requires_auth
def newPlace():
   if request.method == "GET":
      pages = {"cmd": {"link": "newPlace", "name": "New Place"},
               "title": "New Place"}
      s = render_template('newPlace.html', p=pages)
   elif request.method == "POST" and request.form["api"] == "false":
      pages = {"cmd": {"link": "newPlace", "name": "Place Added"}, "title":
               "Place Added"}
      loc = request.form["location"]
      tags = request.form["tags"]
      noteText = request.form["noteText"]
      place = {"location": loc, "noteText": noteText, "tags": tags}
      s = render_template('placeAdded.html', p=pages, placeInfo=place)
   elif request.method == "POST" and request.form["api"] == "true":
      term = request.form["term"]
      s = json.dumps(db.searchForItem(term))
   else:
      s = "not valid"

   return s


@app.route('/delete', methods=["GET", "POST"])
@requires_auth
def Delete():
   pages = {"cmd": {"link": "delete", "name": "Delete"}, "title": "Delete"}
   if request.method == "GET":
      s = render_template('delete.html', p=pages)
   elif request.method == "POST" and request.form["api"] == "false":
      ID = int(request.form["ID"])
      db.deleteItem(ID)
      s = render_template('deleted.html', p=pages, itemID=ID)
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
   s = render_template('note.html', p=pages)
   return s


@app.route('/notes', methods=["GET"])
@requires_auth
def Notes():
   # FIXME -- this function needs a template
   fourWeeks = 4.0 * 7.0 * 24.0 * 60.0 * 60.0
   now = time.time()
   fourWeeksAgo = now - fourWeeks
   items = db.getByTime(startTime=fourWeeksAgo, endTime=now)
   pages = {"cmd": {"link": "search", "name": "Search Result"},
            "title": "Search Result"}

   resultsHTML = []

   s = render_template('searchResult.html', p=pages, searchResults=resultsHTML)
   return s


@app.route('/newNote', methods=["GET", "POST"])
@requires_auth
def NewNote():

   pages = {"cmd": {"link": "newNote", "name": "New Note"},
            "title": "New Note"}
   if request.method == "GET":
      s = render_template('newNote.html', p=pages)
   elif request.method == "POST" and request.form["api"] == "false":
      tags = request.form["tags"]
      noteText = request.form["noteText"]
      db.addItem("notes", {"noteText": noteText, "tags": tags})
      s = render_template('noteAdded.html',
                          p=pages,
                          noteText=noteText,
                          tags=tags)
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
   pages = {"cmd": {"link": "newContact", "name": "New Contact"},
            "title": "New Contact"}
   if request.method == "GET":
      s = render_template('newContact.html', p=pages)
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
      s = render_template('contactAdded.html', p=pages, contact=contactInfo)
   elif request.method == "POST" and request.form["api"] == "true":
      contactText = request.form["contactText"]
      tags = request.form["tags"].split(",")
      contact = {"contactText": contactText,
                 "tags": tags,
                 "timestamp": time.time()}
      s = json.dumps(contact)
   return s


@app.route('/newTodo', methods=["GET", "POST"])
@requires_auth
def NewTodo():

   pages = {"cmd": {"link": "newTodo", "name": "New ToDo"},
            "title": "New ToDo"}
   if request.method == "GET":
      s = render_template('newTodo.html', p=pages)
   elif request.method == "POST" and request.form["api"] == "false":
      todoText = request.form["todoText"]
      done = str(request.form['options'])
      date = request.form['date']
      done = (done == "done")

      todoItem = {"todoText": todoText,
                  "done": done,
                  "date": time.mktime(time.strptime(date, "%m/%d/%Y"))}
      db.addItem("todos", todoItem)
      todoItem['done'] = str(todoItem['done'])
      todoItem['date'] = str(todoItem['date'])
      s = render_template('todoAdded.html', p=pages, todo=todoItem)
   elif request.method == "POST" and request.form["api"] == "true":
      todoText = request.form["todoText"]
      tags = request.form["tags"].split(",")
      todo = {"todoText": todoText, "tags": tags, "timestamp": time.time()}
      dateStr = time.mktime(time.strptime(date, "%m/%d/%Y"))
      db.addItem("todos", {"todoText": todoText,
                           "done": done,
                           "date": dateStr})
      s = json.dumps(todo)
   return s


def main():
   with open(os.path.expanduser("~/.note.conf")) as fd:
      config = json.loads(fd.read())
   try:
      addr = config['server']['address']
   except:
      addr = "127.0.0.1"
      print("Address not found using ", addr)
   args = parseArgs()
   if args.debug:
      app.debug = True
   app.run(host=addr)

if __name__ == "__main__":
   main()
