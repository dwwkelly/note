#!/usr/bin/env python

import time
from flask import Flask
from flask import url_for
from flask import request
from n import mongoDB
app = Flask(__name__)

__author__ = "Devin Kelly"

htmlStart = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="">
    <meta name="author" content="">
    <link rel="shortcut icon" href="/docs-assets/ico/favicon.png">

    <title>Note</title>
    <link href="static/dist/css/bootstrap.css" rel="stylesheet">
    <link href="static/note.css" rel="stylesheet">
    <script src="static/jquery-1.10.2.js"></script>
    <script src="static/dist/js/bootstrap.js"></script>
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
          <a class="navbar-brand" href="/">Note</a>
        </div>
        <div class="collapse navbar-collapse">
          <ul class="nav navbar-nav">
            <li class="active"><a href="Notes">Notes</a></li>
            <li class="dropdown">
               <a href="NewNote" class="dropdown-toggle" data-toggle="dropdown">New<b class="caret"></b></a>
               <ul class="dropdown-menu">
                  <li><a href="NewNote">Note</a></li>
                  <li><a href="Todo">Todo</a></li>
                  <li><a href="Contact">Contact</a></li>
               </ul>
            </li>
            <li><a href="Search">Search</a></li>
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
      s = htmlStart
      s += "<form action=\"Search\" method=\"POST\" enctype=\"multipart/form-data\" class=\"form-inline\" role=\"form\">" +\
           "   <div class=\"form-group\">" +\
           "      <label for=\"Search\" class=\"col-sm-2 control-label\"></label>" +\
           "      <div class=\"col-sm-10\">" +\
           "         <input type=\"text\" class=\"form-control\" name=\"term\">" +\
           "      </div>" +\
           "   </div>" +\
           "<br><br>" +\
           "   <div class=\"form-group\">" +\
           "      <div class=\"col-sm-offset-2 col-sm-10\">" +\
           "         <button type=\"Search\" class=\"btn btn-default\">Search</button>" +\
           "      </div>" +\
           "   </div>" +\
           "</form>"
      s += htmlEnd
   elif request.method == "POST":
      term = request.form["term"]
      db = mongoDB("note")
      results = db.searchForItem(term)

      s = htmlStart
      for item in results:
         ID = item['obj'][u"ID"]
         item = db.getItem(ID)
         s += "<div id=\"searchResult\">"
         for k in item.keys():
            s += str(k) + ": " + str(item[k]) + "<br>"
         s += "</div>"
      s += htmlEnd
   else:
      s = "not valid"

   return s


@app.route('/', methods=["GET", "POST"])
def start():
   if request.method == "GET":
      s = "<form action=index enctype=\"multipart/form-data\" method=\"POST\">" +\
          "ID: <input type=\"text\" name=\"id\"><br>" +\
          "<input type=\"submit\" value=\"Submit\">" +\
          "</form></html>"
   elif request.method == "POST":
      ID = request.form["id"]
      ID = int(ID)
      db = mongoDB("note")
      item = db.getItem(ID)
      s = "<html>"
      for k in item.keys():
         s += str(k) + ": " + str(item[k]) + "<br>"
      s = s + "</html>"

   else:
      s = "not valid"

   return s


@app.route('/Notes', methods=["GET"])
def Notes():
   s = htmlStart
   fourWeeks = 4.0 * 7.0 * 24.0 * 60.0 * 60.0
   now = time.time()
   fourWeeksAgo = now - fourWeeks
   db = mongoDB("note")
   items = db.getByTime(startTime=fourWeeksAgo, endTime=now)

   for item in items:
      info = db.getItem(item)
      for k in info.keys():
         s += str(k) + ": " + str(info[k])
      s += "<br>"

   s + htmlEnd

   return s


@app.route('/NewNote', methods=["GET", "POST"])
def NewNote():
   url_for('static', filename='jquery-1.10.2.js')
   url_for('static', filename='dist/js/bootstrap.js')

   s = htmlStart
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

   elif request.method == "POST":
      tags = request.form["tags"]
      noteText = request.form["noteText"]
      s += noteText + "<br>"
      s += tags + "<br>"

   s + htmlEnd
   return s


def main():
   app.run()

if __name__ == "__main__":
   main()
