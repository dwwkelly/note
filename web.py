#!/usr/bin/env python

from flask import Flask
from flask import request
from n import mongoDB
app = Flask(__name__)

__author__ = "Devin Kelly"


@app.route('/index', methods=["GET", "POST"])
def start():

   if request.method == "GET":
      s = "<html><form>" + \
          "ID: <input type=\"text\" name=\"id\"><br>" +\
          "<input type=\"submit\" value=\"Submit\">" +\
          "</form></html>"

   elif request.method == "POST":
      ID = request.form["id"]
      db = mongoDB()
      s = db.getItem(ID)
   else:
      s = "not valid"

   return s


def main():
   app.run()

if __name__ == "__main__":
   main()
