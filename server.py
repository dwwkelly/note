#!/usr/bin/env python

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import daemon
import os
import json
from web import app
import argparse


def parseArgs():

   parser = argparse.ArgumentParser(description='Note Web App')
   parser.add_argument('-F', action='store_true', help="Run WebApp in foreground (don't daemonize)", default=False)
   parser.add_argument('-f', type=str, help="Set config file", default=os.path.expanduser('~/.note.conf'))

   args = parser.parse_args()
   return args


def main():

   args = parseArgs()
   foreground = args.F
   configFile = args.f

   with open(configFile) as fd:
      config = json.loads(fd.read())

   try:
      port = config['server']['port']
   except:
      port = 5000

   try:
      certfile = config['server']['ssl']['certfile']
      keyfile = config['server']['ssl']['keyfile']
      serverSSLOptions = {"certfile": certfile, "keyfile": keyfile}
      if not (os.path.exists(certfile) and os.path.exists(keyfile)):
         raise IOError
   except:
      certfile = None
      keyfile = None
      serverSSLOptions = None

   try:
      listenIP = config['server']['listenIP']
   except:
      listenIP = "127.0.0.1"

   def startServer():
      http_server = HTTPServer(WSGIContainer(app), ssl_options=serverSSLOptions)
      http_server.listen(port, address=listenIP)
      IOLoop.instance().start()

   if foreground:
      startServer()
   else:
      with daemon.DaemonContext():
         startServer()


if __name__ == '__main__':
   main()
