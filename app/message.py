#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bottle import request

# Flush message control
def set_message(status, message):
	session = request.environ.get('beaker.session')
	session[status] = message
	session.save()

def success(message):
	set_message("success", message)
	
def error(message):
	set_message("error", message)

def get_message(status, once=False):
	session = request.environ.get('beaker.session')
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