#!/usr/bin/env python

__author__ = "Devin Kelly"
from flask import Flask
from jinja2 import Environment
from jinja2 import FileSystemLoader


app = Flask(__name__)


j2_env = Environment(loader=FileSystemLoader('templates'), trim_blocks=True)


@app.route(r'/search')
def f1():
   t = j2_env.get_template('search.html')
   pages = {"cmd": {"link": "search", "name": "Search"}, "title": "Search Title"}
   return t.render(p=pages)


@app.route(r'/newNote')
def f2():
   t = j2_env.get_template('newNote.html')
   pages = {"cmd": {"link": "newNote", "name": "New Note"}, "title": "New Note Title"}
   return t.render(p=pages)


@app.route(r'/newContact')
def f3():
   t = j2_env.get_template('newContact.html')
   pages = {"cmd": {"link": "newContact", "name": "New Contact"}, "title": "New Contact Title"}
   return t.render(p=pages)


@app.route(r'/newTodo')
def f4():
   t = j2_env.get_template('newTodo.html')
   pages = {"cmd": {"link": "newTodo", "name": "New Todo"}, "title": "New Todo Title"}
   return t.render(p=pages)


@app.route(r'/delete')
def f5():
   t = j2_env.get_template('delete.html')
   pages = {"cmd": {"link": "delete", "name": "Delete"}, "title": "Delete Title"}
   return t.render(p=pages)


@app.route(r'/note')
def f6():
   t = j2_env.get_template('base.html')
   pages = {"cmd": {"link": "note", "name": "Note"}, "title": "Note Title"}
   return t.render(p=pages)


def main():
   app.run(debug=True)

if __name__ == "__main__":
   main()
