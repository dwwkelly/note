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
from flask import url_for
from flask import request
from flask import Response
from functools import wraps
from n import mongoDB

app = Flask(__name__)

db = mongoDB("note")

htmlStart = u"""
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">

    <title>Note</title>
    <link href="/static/dist/css/bootstrap.css" rel="stylesheet">
    <link href="/static/note.css" rel="stylesheet">
    <link href="/static/datepicker/css/datepicker.css" rel="stylesheet">
    <script src="/static/jquery-1.10.2.js"></script>
    <script src="/static/dist/js/bootstrap.js"></script>
    <script src="/static/datepicker/js/bootstrap-datepicker.js"></script>
  </head>

  <body>

    <div class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
          <a class="navbar-brand" href="Notes">Note</a>
        </div>
        <div class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li class="active"><a href="{0}">{0}</a></li>
            <li class="dropdown">
               <a href="NewNote" class="dropdown-toggle" data-toggle="dropdown">New<b class="caret"></b></a>
               <ul class="dropdown-menu">
                  <li><a href="NewNote">Note</a></li>
                  <li><a href="NewTodo">Todo</a></li>
                  <li><a href="NewContact">Contact</a></li>
               </ul>
            </li>
            <li><a href="Search">Search</a></li>
            <li><a href="Delete">Delete</a></li>
          </ul>
        </div>
      </div>
    </div>

    <div class="container">

      <div class="note-template">
"""
htmlEnd = u"""
      </div>

    </div>

  </body>
</html>
"""


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


@app.route(r'/Note/Search', methods=["GET", "POST"])
@requires_auth
def search():
   if request.method == "GET":
      s = htmlStart.format("Search")
      s += u"""<form action="Search" method="POST" enctype="multipart/form-data" class="form-inline" role="form">
              <div class="form-group">
                 <label for="Search" class="col-sm-2 control-label"></label>
                 <div class="col-sm-10">
                    <input type="text" class="form-control" name="term">
                    <input type="hidden" class="form-control" name="api" value="false">
                 </div>
              </div>
           <br><br>
              <div class="form-group">
                 <div class="col-sm-offset-2 col-sm-10">
                    <button type="Search" class="btn btn-default">Search</button>
                 </div>
              </div>
           </form>
         """
      s += htmlEnd
   elif request.method == "POST" and request.form["api"] == "false":
      term = request.form["term"]
      results = db.searchForItem(term)

      s = htmlStart.format("Search")
      for item in results:
         ID = item['obj'][u"ID"]
         item = db.getItem(ID)
         s += u'<div class="devintron">'
         s += genHTML(int(ID))
         s += u'</div>'
      s += htmlEnd
   elif request.method == "POST" and request.form["api"] == "true":
      term = request.form["term"]
      s = json.dumps(db.searchForItem(term))
   else:
      s = "not valid"

   s = addLinks(s)
   return s


@app.route('/Note/Delete', methods=["GET", "POST"])
@requires_auth
def Delete():
   if request.method == "GET":
      s = htmlStart.format("Delete")
      s += u"""<form action="Delete" method="POST" enctype="multipart/form-data" class="form-inline" role="form">
              <div class="form-group">
                 <label for="Delete" class="col-sm-2 control-label"></label>
                 <div class="col-sm-10">
                    <input type="text" class="form-control" name="ID">
                    <input type="hidden" class="form-control" name="api" value="false">
                 </div>
              </div>
           <br><br>
              <div class="form-group">
                 <div class="col-sm-offset-2 col-sm-10">
                    <button type="Delete" class="btn btn-default">Delete</button>
                 </div>
              </div>
           </form>
         """
      s += htmlEnd
   elif request.method == "POST" and request.form["api"] == "false":
      ID = int(request.form["ID"])
      db.deleteItem(ID)

      s = htmlStart.format("Delete")
      s += u"Item ID={0} deleted".format(ID)
      s += htmlEnd
   elif request.method == "POST" and request.form["api"] == "true":
      ID = int(request.form["ID"])
      result = db.deleteItem(ID)
      retVal = {"result": result, "ID": ID}
      s = json.dumps(retVal)
   else:
      s = u"not valid"

   return s


@app.route('/Note', methods=["GET"])
@requires_auth
def start():
   s = htmlStart.format("Notes")
   s += htmlEnd

   return s


@app.route('/Note/Notes', methods=["GET"])
@requires_auth
def Notes():
   s = htmlStart.format("Notes")
   fourWeeks = 4.0 * 7.0 * 24.0 * 60.0 * 60.0
   now = time.time()
   fourWeeksAgo = now - fourWeeks
   items = db.getByTime(startTime=fourWeeksAgo, endTime=now)

   for ID in items:
      s += '<div class="devintron">'
      s += genHTML(int(ID))
      s += '</div>'

   s += htmlEnd

   s = addLinks(s)

   return s


@app.route('/Note/NewNote', methods=["GET", "POST"])
@requires_auth
def NewNote():
   url_for('static', filename='jquery-1.10.2.js')
   url_for('static', filename='dist/js/bootstrap.js')

   s = htmlStart.format("New Note")
   if request.method == "GET":
      s += u"""
           <form action="NewNote" method="POST" enctype="multipart/form-data" class="form-horizontal" role="form">
              <div class="row">
                  <div class="col-sm-12">
                     <div class="form-group">
                        <label for="Note" class="control-label"></label>
                        <textarea class="form-control" name="noteText" placeholder="Note" rows="3"></textarea>
                     </div>
                  </div>
              </div>
              <div class="row">
                  <div class="col-sm-12">
                     <div class="form-group">
                        <label for="Tags" class="control-label"></label>
                        <input type="text" class="form-control" name="tags" placeholder="Tags">
                        <input type="hidden" class="form-control" name="api" value="false">
                     </div>
                  </div>
              </div>
              <div class="row">
                  <div class="form-group">
                     <div class="col-sm-12">
                        <button type="Note" class="btn btn-default">Add Note</button>
                     </div>
                  </div>
              </div>
           </form>"""

   elif request.method == "POST" and request.form["api"] == "false":
      tags = request.form["tags"]
      noteText = request.form["noteText"]
      db.addItem("notes", {"noteText": noteText, "tags": tags})
      s += u"Note added<br><br>"
      s += noteText + u"<br>"
      s += tags + u"<br>"
      s + htmlEnd
   elif request.method == "POST" and request.form["api"] == "true":
      noteText = request.form["noteText"]
      tags = request.form["tags"].split(",")
      note = {"noteText": noteText, "tags": tags, "timestamp": time.time()}
      db.addItem("notes", {"noteText": noteText, "tags": tags})
      s = json.dumps(note)
   return s


@app.route('/Note/NewContact', methods=["GET", "POST"])
@requires_auth
def NewContact():
   url_for('static', filename='jquery-1.10.2.js')
   url_for('static', filename='dist/js/bootstrap.js')

   s = htmlStart.format("New Contact")
   if request.method == "GET":
      s += u"""
           <form action="NewContact" method="POST" enctype="multipart/form-data" class="form-horizontal" role="form">
           <input type="hidden" class="form-control" name="api" value="false">

              <div class="row">
                  <div class="col-xs-12 col-sm-4">
                     <div class="form-group">
                        <label for="Name" class="control-label"></label>
                        <input type="text" class="form-control" name="name" placeholder="Name">
                     </div>
                  </div>
                  <div class="col-xs-12 col-sm-4">
                     <div class="form-group">
                        <label for="Affiliation" class="control-label"></label>
                        <input type="text" class="form-control" name="affiliation" placeholder="Affiliation">
                     </div>
                  </div>
                  <div class="col-sm-4">
                     <div class="form-group">
                        <label for="EMail" class="control-label"></label>
                        <input type="text" class="form-control" name="email" placeholder="EMail">
                     </div>
                  </div>
              </div>

              <div class="row">
                  <div class="col-xs-12 col-sm-4">
                     <div class="form-group">
                        <label for="Mobile Phone" class="control-label"></label>
                        <input type="text" class="form-control" name="mobile" placeholder="Mobile Phone">
                     </div>
                  </div>
                  <div class="col-xs-12 col-sm-4">
                     <div class="form-group">
                        <label for="Work Phone" class="control-label"></label>
                        <input type="text" class="form-control" name="work" placeholder="Work Phone">
                     </div>
                  </div>
                  <div class="col-sm-4">
                     <div class="form-group">
                        <label for="Home Phone" class="control-label"></label>
                        <input type="text" class="form-control" name="home" placeholder="Home Phone">
                     </div>
                  </div>
              </div>

              <div class="row">
                  <div class="col-sm-12">
                     <div class="form-group">
                        <label for="Address" class="control-label"></label>
                        <input type="text" class="form-control" name="address" placeholder="Address">
                     </div>
                  </div>
              </div>


              <div class="row">
                  <div class="form-group">
                     <div class="col-sm-12">
                        <button type="Contact" class="btn btn-default">Add Contact</button>
                     </div>
                  </div>
              </div>
           </form>"""
      s += htmlEnd
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

      s += u"Note added<br><br>"
      s += name + u"<br>"
      s += affiliation + u"<br>"
      s += email + u"<br>"
      s += work + u"<br>"
      s += home + u"<br>"
      s += mobile + u"<br>"
      s += address + u"<br>"
   elif request.method == "POST" and request.form["api"] == "true":
      contactText = request.form["contactText"]
      tags = request.form["tags"].split(",")
      contact = {"contactText": contactText, "tags": tags, "timestamp": time.time()}
      s = json.dumps(contact)
   return s


@app.route('/Note/NewTodo', methods=["GET", "POST"])
@requires_auth
def NewTodo():
   url_for('static', filename='jquery-1.10.2.js')
   url_for('static', filename='dist/js/bootstrap.js')
   url_for('static', filename='datepicker/js/bootstrap-datepicker.js')

   s = htmlStart.format("New Todo")
   if request.method == "GET":
      s += u"""
           <form action="NewTodo" method="POST" enctype="multipart/form-data" class="form-horizontal" role="form">
              <input type="hidden" class="form-control" name="api" value="false">
              <div class="row">
                  <div class="col-sm-12">
                     <div class="form-group">
                        <label for="Todo" class="control-label"></label>
                        <textarea class="form-control" name="todoText" placeholder="Todo" rows="3"></textarea>
                     </div>
                  </div>
              </div>
              <div class="row">
                  <div class="col-sm-6">
                     <div class="btn-group" data-toggle="buttons">
                        <label class="btn btn-primary">
                           <input type="radio" name="options" value="done">Done
                        </label>
                        <label class="btn btn-primary">
                           <input type="radio" name="options" value="undone">Not Done
                        </label>
                     </div>
                  </div>
                  <div class="col-sm-6">
                     <input type="text" class="datepicker" name="date" placeholder="Date">
                  </div>
              </div>
              <div class="row">
                  <div class="form-group">
                     <div class="col-sm-12">
                        <button type="Todo" class="btn btn-default">Add Todo</button>
                     </div>
                  </div>
              </div>
           </form>

           </div>

           </div>

           <script>
              $(document).ready(function() {
                    $('.datepicker').datepicker();
                    });
           </script>

         </body>
         </html>
         """
   elif request.method == "POST" and request.form["api"] == "false":
      todoText = request.form["todoText"]
      done = str(request.form['options'])
      date = request.form['date']

      if done == "done":
         done = True
      else:
         done = False

      db.addItem("todos", {"todoText": todoText, "done": done, "date": time.mktime(time.strptime(date, "%m/%d/%Y"))})

      s += todoText + u"<br>"
      s += str(done) + u"<br>"
      s += str(date) + u"<br>"
      s + htmlEnd
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
