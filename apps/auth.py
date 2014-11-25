from flask.ext.login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext.wtf import Form
from wtforms import TextField, PasswordField, validators, HiddenField, ValidationError
from wtforms import TextAreaField, BooleanField
from wtforms.validators import Required, EqualTo, Optional
from wtforms.validators import Length, Email
import logging
from model import *
import views
from flask import current_app, session, render_template, url_for, request, redirect, flash, abort, g, Blueprint
from sqlalchemy.orm import scoped_session, relation, sessionmaker
from sqlalchemy import select
import pprint 

pp = pprint.PrettyPrinter(indent=2)

auth = Blueprint('auth', __name__)

class SignupForm(Form):
    email = TextField('Email address', validators=[
            Required('Please provide a valid email address'),
            Length(min=6, message=(u'Email address too short')),
            Email(message=(u'That\'s not a valid email address.'))])
    password = PasswordField('Pick a secure password', validators=[
            Required(),
            EqualTo('confirm', message=(u'Passwords must match')),
            Length(min=6, message=(u'Please give a longer password.'))])
    confirm = PasswordField('Repeat Password')
    username = TextField('Choose your username', validators=[Required()])
    agree = BooleanField('I agree all your Terms of Services',
            validators=[Required(u'You must accept our Terms of Service')])

    def __repr__(self):
        return "<{0}:{1.username}:{1.email}>".format(SignupForm, self)

#logging
logger = logging.getLogger(__name__)

# login manager
login_manager = LoginManager()
login_manager.login_view = 'login'

@auth.before_request
def before_request():
	g.user = current_user

@login_manager.user_loader
def load_user(userid):
	return views.orm_session.query(User).get(userid)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    username = request.form['username']
    password = request.form['password']
    remember_me = False
    if 'remember_me' in request.form:
        remember_me = True
    registered_user = views.orm_session.query(User).filter_by(username=username,password=password).first()
    logger.info("Registered user = %s", registered_user)
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('login'))
    login_user(registered_user, remember = remember_me)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('views.home'))

@auth.route("/logout")
@login_required
def logout():
    user = current_user
    user.authenticated = False
    views.orm_session.add(user)
    views.orm_session.commit()
    logout_user()
    return redirect(url_for("login"))
    
@auth.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = User()
        form = SignupForm(request.form, obj=user)
        if form.validate():
            form.populate_obj(user)
            user_exist = User.query.filter_by(username=form.username.data).first()
            email_exist = User.query.filter_by(email=form.email.data).first()
            if user_exist:
                form.username.errors.append('Username already taken')
            if email_exist:
                form.email.errors.append('Email already use')
            if user_exist or email_exist:
                return render_template('signup.html', form = form, page_title = 'Signup to Courses System')
            else:
                user.authenticated = True
                views.orm_session.add(user)
                views.orm_session.commit()
                #current_user = user
                flash('Thanks for signing up.')
                return redirect(url_for('views.courses'))
        else:
            #pp.pprint(form)
            return render_template('signup.html', form = form, page_title = 'Signup to Courses System')
    return render_template('signup.html', form = SignupForm(), page_title = 'Signup to Courses System')