import os, sys, bottle
from bottle import debug, route, request, run, Bottle, static_file
from apps import model, views
from beaker.middleware import SessionMiddleware

app = bottle.app()

session_options = {
		'session.type': 'file',
		'session.cookie_expires': 300,
		'session.data_dir': './data',
		'session.auto': True
	}

app_session = SessionMiddleware(app, session_options)

@app.route('/assets/<filepath:path>')
def server_static(filepath):
    return static_file(filepath, root='assets')

@app.route('/test')
def test():
    s = request.environ.get('beaker.session')
    s['test'] = s.get('test', 0) + 1
    s.save()
    return 'Test counter: %d' % s['test']
    
run(app=app_session)
