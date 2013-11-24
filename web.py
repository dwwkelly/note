#!/usr/bin/env python

import time
import json
import re
from flask import Flask
from flask import url_for
from flask import request
from n import mongoDB
app = Flask(__name__)

db = mongoDB("note")

__author__ = "Devin Kelly"
__todo__ = """
-make a decent way to display notes when searching, maybe use angular.js?
-add ability to delete
"""

htmlStart = """
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
htmlEnd = """
      </div>

    </div>

  </body>
</html>
"""


@app.route('/Search', methods=["GET", "POST"])
def search():
   if request.method == "GET":
      s = htmlStart.format("Search")
      s += """<form action="Search" method="POST" enctype="multipart/form-data" class="form-inline" role="form">
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

         s += '<div class="devintron">'
         #s += "<p>"
         ##s += "<div id=\"searchResult\">"
         #for k in item.keys():
         #   s += str(k).lower() + ": " + re.sub("\n", "<br>", str(item[k]))
         #   s += "<br>"
         #s += "</p>"
         s += genHTML(int(ID))
         print genHTML(int(ID))
         s += '</div>'
         #s += "</div>"
      s += htmlEnd
   elif request.method == "POST" and request.form["api"] == "true":
      term = request.form["term"]
      s = json.dumps(db.searchForItem(term))
   else:
      s = "not valid"

   return s


@app.route('/Delete', methods=["GET", "POST"])
def Delete():
   if request.method == "GET":
      s = htmlStart.format("Delete")
      s += """<form action="Delete" method="POST" enctype="multipart/form-data" class="form-inline" role="form">
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
      s += "Item ID={0} deleted".format(ID)
      s += htmlEnd
   elif request.method == "POST" and request.form["api"] == "true":
      ID = int(request.form["ID"])
      result = db.deleteItem(ID)
      retVal = {"result": result, "ID": ID}
      s = json.dumps(retVal)
   else:
      s = "not valid"

   return s


@app.route('/', methods=["GET"])
def start():
   s = htmlStart.format("Notes")
   s += htmlEnd

   return s


@app.route('/Notes', methods=["GET"])
def Notes():
   s = htmlStart.format("Notes")
   fourWeeks = 4.0 * 7.0 * 24.0 * 60.0 * 60.0
   now = time.time()
   fourWeeksAgo = now - fourWeeks
   items = db.getByTime(startTime=fourWeeksAgo, endTime=now)

   for item in items:
      info = db.getItem(item)
      s += '<div class="devintron">'
      s += "<p>"
      for k in info.keys():
         s += str(k) + ": " + re.sub("\n", "<br>", str(info[k]))
         s += "<br>"
      s += "</p>"
      s += '</div>'

   s + htmlEnd

   return s


@app.route('/NewNote', methods=["GET", "POST"])
def NewNote():
   url_for('static', filename='jquery-1.10.2.js')
   url_for('static', filename='dist/js/bootstrap.js')

   s = htmlStart.format("New Note")
   if request.method == "GET":
      s += """
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
      s += "Note added<br><br>"
      s += noteText + "<br>"
      s += tags + "<br>"
      s + htmlEnd
   elif request.method == "POST" and request.form["api"] == "true":
      noteText = request.form["noteText"]
      tags = request.form["tags"].split(",")
      note = {"noteText": noteText, "tags": tags, "timestamp": time.time()}
      db.addItem("notes", {"noteText": noteText, "tags": tags})
      s = json.dumps(note)
   return s


@app.route('/NewContact', methods=["GET", "POST"])
def NewContact():
   url_for('static', filename='jquery-1.10.2.js')
   url_for('static', filename='dist/js/bootstrap.js')

   s = htmlStart.format("New Contact")
   if request.method == "GET":
      s += """
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

      s += "Note added<br><br>"
      s += name + "<br>"
      s += affiliation + "<br>"
      s += email + "<br>"
      s += work + "<br>"
      s += home + "<br>"
      s += mobile + "<br>"
      s += address + "<br>"
   elif request.method == "POST" and request.form["api"] == "true":
      contactText = request.form["contactText"]
      tags = request.form["tags"].split(",")
      contact = {"contactText": contactText, "tags": tags, "timestamp": time.time()}
      s = json.dumps(contact)
   return s


@app.route('/NewTodo', methods=["GET", "POST"])
def NewTodo():
   url_for('static', filename='jquery-1.10.2.js')
   url_for('static', filename='dist/js/bootstrap.js')
   url_for('static', filename='datepicker/js/bootstrap-datepicker.js')

   s = htmlStart.format("New Todo")
   if request.method == "GET":
      s += """
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

      s += todoText + "<br>"
      s += str(done) + "<br>"
      s += str(date) + "<br>"
      s + htmlEnd
   elif request.method == "POST" and request.form["api"] == "true":
      todoText = request.form["todoText"]
      tags = request.form["tags"].split(",")
      todo = {"todoText": todoText, "tags": tags, "timestamp": time.time()}
      s = json.dumps(todo)
   return s


def genHTML(ID):

   itemType = db.getItemType(ID)
   item = db.getItem(ID)

   if itemType == "todos":
      s = "<p>"
      s += re.sub("\n", "<br>", str(item['todoText']))
      s += "</p>"

      s += "<p>"
      if item['done']:
         s += 'done'
      else:
         s += 'not done'
      s += '</p>'

   elif itemType == "notes":
      s = "<p>"
      s += re.sub("\n", "<br>", str(item['noteText']))
      s += "</p>"

   elif itemType == "contact":
      s = "<p>"
      s += item['NAME'] + "<br>"
      s += item['EMAIL'] + "<br>"
      s += item['AFFILIATION'] + "<br>"
      s += item['MOBILE'] + "<br>"
      s += item['HOME'] + "<br>"
      s += item['WORK'] + "<br>"
      s += item['ADDRESS'] + "<br>"
      s += "</p>"

   return s


def main():
   app.run(host="0.0.0.0")

if __name__ == "__main__":
   main()
