#!/usr/bin/env python
# -*- coding: utf-8 -*-

from flask import request
import pprint
# Flush message control

pp = pprint.PrettyPrinter(indent=2)

def set_message(status, message):
	pp.pprint(request.environ)  #print out the object
	session = request.environ['beaker.session']
	session[status] = message
	session.save()

def success(message):
	set_message("success", message)
	
def error(message):
	set_message("error", message)

def get_message(status, once=False):
	session = request.environ['beaker.session']
	value = session.get(status, 0)
	
	if once is True:
		session[status] = ""
		session.save()
	
	return value
	
def flush_message():
	return {
		"success": get_message("success", True),
		"error": get_message("error", True)
	}