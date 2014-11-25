from datetime import datetime
from flask import current_app, Blueprint
from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from backports.pbkdf2 import pbkdf2_hmac, compare_digest


db = SQLAlchemy()

model = Blueprint('model', __name__)

class CRUDMixin(object):
	"""General CRUD class"""
	__table_args__ = {'extend_existing':True}

	id = db.Column(db.Integer, primary_key=True)

	@classmethod
	def create(cls, commit=True, **kwargs):
		instance = cls(**kwargs)
		return instance.save(commit=commit)

	@classmethod
	def get(cls, id):
		return cls.query.get(id)

	@classmethod
	def get_or_404(cls, id):
		return cls.query.get_or_404(id)

	def update(self, commit=True, **kwargs):
		for attr, value in kwargs.iteritems():
			setattr(self, attr, value)
		return commit and self.save() or self

	def save(self, commit=True):
		db.session.add(self)
		if commit:
			db.session.commit()
		return self

	def delete(self, commit=True):
		db.session.delete(self)
		return commit and db.session.commit()

# for login
class User(db.Model, UserMixin):
	__tablename__ = 'users'
	id = db.Column('user_id', db.Integer, primary_key=True)
	username = db.Column('username', db.String(30), unique=True, index=True)
	password = db.Column('password', db.String(12))
	confirm = db.Column('confirm', db.String(12))
	email = db.Column('email', db.String(50), unique=True, index=True)
	registered_on = db.Column('registered_on', db.DateTime)

	def __init__(self, username='', password='', email='', confirm=''):
		self.username = username
		self.password = password
		self.email = email
		self.confirm = confirm
		self.registered_on = datetime.utcnow()

	def is_authenticated(self):
		return True

	def is_active(self):
		pass

	def is_anonymous(self):
		pass
		
	def get_id(self):
		return unicode(self.id)

	def _hash_password(self, password):
		rounds = current_app.config.get("HASH_ROUNDS", 100000)
		buff = pbkdf2_hmac("sha512", pwd, salt, iterations=rounds)

	def __repr__(self):
		return "<{0}:{1.username}:{1.email}".format(User, self)

class Course(db.Model):
	__tablename__ = 'course'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	subjects = db.relationship('Subject', secondary='course_subject_link')
	students = db.relationship('Student', secondary='course_student_link')
	active = db.Column(db.Boolean)
	def __repr__(self):
		return "<{0}:{1.name}:{1.subjects!r}:{1.students!r}>".format(Course, self)

class Subject(db.Model):
	__tablename__ = 'subject'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	duration = db.Column(db.Integer) # number of hours
	tier = db.Column(db.Integer)
	active = db.Column(db.Boolean)
	courses = db.relationship('Course', secondary='course_subject_link')

	def __repr__(self):
		return u"<{0}:{1.name}:{1.duration}:{1.courses!r}>".format(Subject, self)

class CourseSubjectLink(db.Model):
	__tablename__ = 'course_subject_link'
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
	subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), primary_key=True)

class Teacher(db.Model):
	__tablename__ = 'teacher'
	id = db.Column(db.Integer, primary_key=True)
	firstname = db.Column(db.String(255), nullable=False)
	lastname = db.Column(db.String(255), nullable=False)
	birthdate = db.Column(db.Date)
	visa_status = db.Column(db.String(255))
	nationality = db.Column(db.String(255))
	salary_per_hour = db.Column(db.Integer)
	active = db.Column(db.Boolean)

	def __repr__(self):
		return "<{0}:{1.firstname}:{1.lastname}>".format(Teacher, self)

class Student(db.Model):
	__tablename__ = 'student'
	id = db.Column(db.Integer, primary_key=True)
	firstname = db.Column(db.String(255), nullable=False)
	lastname = db.Column(db.String(255), nullable=False)
	birthdate = db.Column(db.Date)
	level = db.Column(db.String(255))
	paid = db.Column(db.Boolean)
	paid_date = db.Column(db.DateTime)
	#payment_methods = db.relationship('PaymentMethod', secondary='course_student_link')
	courses = db.relationship('Course', secondary='course_student_link')
	active = db.Column(db.Boolean)

	def __repr__(self):
		return "<{0}:{1.firstname}:{1.lastname}>".format(Student, self)

class CourseStudentLink(db.Model):
	__tablename__ = 'course_student_link'
	course_id = db.Column(db.Integer, db.ForeignKey('course.id'), primary_key=True)
	student_id = db.Column(db.Integer, db.ForeignKey('student.id'), primary_key=True)
	payment_method_id = db.Column(db.Integer, db.ForeignKey('payment_method.id'), primary_key=True)

class PaymentMethod(db.Model):
	__tablename__ = 'payment_method'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(255), nullable=False)
	students = db.relationship('Student', secondary='course_student_link')
	active = db.Column(db.Boolean)
