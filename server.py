#!/usr/bin/env python

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import daemon
from web import app

with daemon.DaemonContext():
   http_server = HTTPServer(WSGIContainer(app))
   http_server.listen(5000)
   IOLoop.instance().start()
