import os, sys, bottle
from beaker.middleware import SessionMiddleware
from bottle import debug, route, run, default_app

from app import model, views

@bottle.route('/assets/<filepath:path>')
def server_static(filepath):
    return bottle.static_file(filepath, root='assets')

# Boot
if __name__ == '__main__':
	debug(True)

	app = default_app()

	session_options = {
		'session.type': 'file',
		'session.cookie_expires': 300,
		'session.data_dir': './data',
		'session.auto': True
	}
	app = SessionMiddleware(app, session_options)
	run(host='localhost', port=8080, reloader=True, app=app)
