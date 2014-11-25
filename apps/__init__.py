from flask import Flask
from flask.sessions import SessionInterface
from beaker.middleware import SessionMiddleware
from os.path import join, dirname
from flask.ext.migrate import Migrate
import pprint
pp = pprint.PrettyPrinter(indent=2)

app = Flask(__name__)

_cwd = dirname(__file__)

app.config.update(
# Statement for enabling the development environment
	DEBUG = True,

	# Define the database - we are working with
	# SQLite for this example
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(_cwd, 'database/courses.sqlite'),
	DATABASE_CONNECT_OPTIONS = {},

	# Application threads. A common general assumption is
	# using 2 per available processor cores - to handle
	# incoming requests using one and performing background
	# operations using the other.
	THREADS_PER_PAGE = 2,

	# Enable protection agains *Cross-site Request Forgery (CSRF)*
	CSRF_ENABLED     = True,

	# Use a secure, unique and absolutely secret key for
	# signing the data. 
	CSRF_SESSION_KEY = "secret",

	# Sessions variables are stored client side, on the users browser
	# the content of the variables is encrypted, so users can't
	# actually see it. They could edit it, but again, as the content
	# wouldn't be signed with this hash key, it wouldn't be valid
	# You need to set a scret key (random text) and keep it secret
	SECRET_KEY = 'F12Zr47j\3yX R~X@H!jmM]Lwf/,?KT',

	# Propagate exceptions
	PROPAGATE_EXCEPTIONS = True
)

from .views import views
from .model import model, db
from .auth import auth, login_manager

db.init_app(app)

app.register_blueprint(views)
app.register_blueprint(model)
app.register_blueprint(auth)

migrate = Migrate(app, db)

login_manager.init_app(app)

session_opts = {
    'session.type': 'file',
    'session.url': '127.0.0.1:11211',
    'session.data_dir': './data',
}

app.wsgi_app = SessionMiddleware(app.wsgi_app, session_opts)



