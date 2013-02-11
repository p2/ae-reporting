#!/usr/bin/python
#
#  Run locally


import wsgi

wsgi.application.run(host='localhost', port=8080)
