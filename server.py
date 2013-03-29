#!/usr/bin/python
#
#  Run locally


import wsgi
import logging

if wsgi.DEBUG:
	logging.basicConfig(level=logging.DEBUG)
	wsgi.app.run(host='0.0.0.0', port=8008, reloader=True)
else:
	logging.basicConfig(level=logging.WARNING)
	wsgi.app.run(host='0.0.0.0', port=8008)
