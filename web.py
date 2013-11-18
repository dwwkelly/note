#!/usr/bin/env python

import time
from flask import Flask
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
    <link href="static/bootstrap/dist/css/bootstrap.css" rel="stylesheet">
    <link href="static/bootstrap/examples/starter-template/starter-template.css" rel="stylesheet">
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
            <li><a href="New">New</a></li>
            <li><a href="Search">Search</a></li>
          </ul>
        </div>
      </div>
    </div>

    <div class="container">

      <div class="starter-template">
"""
htmlEnd = """
      </div>

    </div>

    <script src="static/jquery-1.10.2.min.js"></script>
    <script src="static/bootstrap/dist/js/bootstrap.min.js"></script>
  </body>
</html>
"""


@app.route('/Search', methods=["GET", "POST"])
def search():
   if request.method == "GET":
      s = htmlStart
      s += "<form action=\"Search\" method=\"POST\" enctype=\"multipart/form-data\" class=\"form-horizontal\" role=\"form\">" +\
           "   <div class=\"form-group\">" +\
           "      <label for=\"Search\" class=\"col-sm-2 control-label\"></label>" +\
           "      <div class=\"col-sm-10\">" +\
           "         <input type=\"text\" class=\"form-control\" name=\"term\">" +\
           "      </div>" +\
           "   </div>" +\
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


@app.route('/New', methods=["GET", "POST"])
def New():
   s = htmlStart
   if request.method == "GET":
      s += "<form action=New enctype=\"multipart/form-data\" method=\"POST\">" +\
           "noteText: <input type=\"text\" name=\"noteText\"><br>" +\
           "tags: <input type=\"text\" name=\"tags\"><br>" +\
           "<input type=\"submit\" value=\"Submit\">" +\
           "</form>"
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
