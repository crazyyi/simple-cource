# -*- coding: utf-8 -*-

import message
import codecs
from model import *
from flask import Flask, request, redirect, render_template, session, g, url_for, Blueprint
import jinja2
from sqlalchemy.orm import scoped_session, relation, sessionmaker
from sqlalchemy import select, create_engine
import datetime
import sys
from flask.ext.login import login_required, current_user
import logging
from os.path import join, dirname


views = Blueprint('views', __name__)

#logging
logger = logging.getLogger(__name__)

# utf-8 unicode required
reload(sys)
sys.setdefaultencoding("utf-8")

# ORM Session
_cwd = dirname(__file__)
engine = create_engine('sqlite:///' + join(_cwd, 'database/courses.sqlite'))
Session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
orm_session = Session()
orm_session._model_changes = {} # flask.ext.sqlalchemy added attribute

@views.route('/test')
@login_required
def test():
    session = request.environ['beaker.session']
    session['test'] = session.get('test', 0) + 1
    session.save()
    return 'Test counter: %d' % session['test']

@views.before_request
def before_request():
    g.user = current_user

@views.route('/')
def home():
	return render_template('home.html')

@views.route('/courses')
def courses():
	courses = orm_session.query(Course).order_by('-id')
	return render_template('courses.html', courses=courses)

# New
@views.route('/new-course', methods=['POST'])
def new_course():
	name = request.form["name"].decode("utf-8")

	if len(name) > 0:
		record = Course(name=name, active=True)

		orm_session.add(record)
		orm_session.commit()

		message.success("sucessful!")
	else:
		message.error("Failed!")

	return redirect(url_for('courses'))

@views.route('/update-course/<int:id>', methods=['POST'])
def update_course(id):
	course = orm_session.query(Course).filter(Course.id == id).first()

	name = request.form["name"].decode("utf-8")

	if course:
		course.name = name
		orm_session.add(course)
		orm_session.commit()
	else:
		message.error("Failed")

	return redirect(url_for("home"))

# Delete
@views.route('/delete-course/<int:id>')
def delete(id):
	find_students = select([CourseStudentLink.course_id, CourseStudentLink.student_id]).select_from(CourseStudentLink.__table__).where(CourseStudentLink.course_id == id)

	rs = orm_session.execute(find_students)
	student = rs.fetchone()

	if student:
		message.error(u"还有学生选了这门课")
	else:
		course = orm_session.query(Course).filter(Course.id==id).first()
		logger.info("course name: %s", course)

		if course:
			orm_session.delete(course)
			orm_session.commit()

	return redirect(url_for('courses'))

@views.route('/edit-course/<int:id>')
def edit_course(id):
	course = orm_session.query(Course).filter(Course.id == id).first()
	logger.info("editing course: %s", course)

	if course:
		message.success("successful!")
		return render_template('edit-course.html', course=course)
	else:
		message.error("Failed!")
		return redirect(url_for("courses"))

@views.route('/subjects')
def list_subjects():
	subjects = orm_session.query(Subject).order_by('-id')

	return render_template('subjects.html', subjects=subjects)

@views.route('/edit-subject/<int:id>')
def edit_subject(id):
	subject = orm_session.query(Subject).filter(Subject.id == id).first()

	if subject:
		message.success("successful!")
		return render_template('edit-subject.html', subject=subject)
	else:
		message.error("Failed!")
		return redirect("/")

@views.route('/delete-subject/<int:id>')
def delete_subject(id):
	subject = orm_session.query(Subject).filter(Subject.id == id).first()
	if subject:
		message.success("successful!")
		orm_session.delete(subject)
		orm_session.commit()
	else:
		message.error("Failed!")
	
	return redirect('/subjects')

@views.route('/new-subject', methods=['POST'])
def new_subject():
	subject_name = request.form["name"].decode("utf-8")
	duration = request.form["duration"].decode("utf-8")
	tier = request.form["tier"].decode("utf-8")

	if len(subject_name) >0 and len(duration) > 0 and tier:
		subject = Subject(name=subject_name, duration=duration, tier=tier)
		orm_session.add(subject)
		orm_session.commit()
		message.success("successful!")
	else:
		message.error("Failed!")
	
	return redirect('/subjects')

@views.route('/update-subject/<int:id>', methods=['POST'])
def update_subject(id):
	subject = orm_session.query(Subject).filter(Subject.id==id).first()
	logger.info("Subject object = %s", subject)
	name = request.form["name"].decode("utf-8")
	duration = request.form["duration"].decode("utf-8")
	if subject:
		logger.info("Subject name = %s and duration = %s.\n", \
		 "textfield name = %s, textfield duration = %s\n",
			subject.name, subject.duration, name ,duration)
		if subject.name != name:
			subject.name = name
		if subject.duration != duration:
			subject.duration = duration
		orm_session.add(subject)
		orm_session.commit()
		message.success("successful")
	else:
		message.error("Failed!")

	return redirect('/subjects')
	
### Operations for students

@views.route('/students')
def list_students():
	students = orm_session.query(Student).order_by('-id')
	return render_template('students.html', students=students)

@views.route('/new-student', methods=['POST'])
def new_student():
	firstname = request.form["firstname"].decode("utf-8")
	lastname = request.form["lastname"].decode("utf-8")
	
	if request.form["paid"] == 'on':
		paid = True
	else:
		paid = False

	if len(firstname) > 0 and len(lastname) > 0:
		record = Student(firstname=firstname, lastname=lastname, paid=paid, active=True)

		orm_session.add(record)
		orm_session.commit()

		message.success("sucessful!")
	else:
		message.error("Failed!")

	return edirect("/students")

@views.route('/edit-student/<int:id>')
def edit_student(id):
	student = orm_session.query(Student).filter(Student.id==id).first()

	if student:
		logger.info("student = %s", student)
		message.success("successful!")
		return render_template('edit-student.html', student=student)
	else:
		message.error("Failed!")
		return redirect("/students")

@views.route('/delete-student/<int:id>')
def delete_student(id):
	student = orm_session.query(Student).filter(Student.id==id).first()

	if student:
		logger.info("student = %s", student)
		orm_session.delete(student)
		orm_session.commit()
		orm_session.close()
		message.success("sucessful!")
	else:
		message.error(u"找不到记录")

	return redirect('/students')

@views.route('/update-student/<int:id>', methods=['POST'])
def update_student(id):
	student = orm_session.query(Student).filter(Student.id==id).first()

	name = request.form["name"].decode("utf-8")

	if student:
		student.name = name
		orm_session.add(student)
		orm_session.commit()
		message.success("successful")
	else:
		message.error("Failed")

	return redirect("students")

def validate_birthdate(birthdate):
	if len(birthdate) > 0:
		birthdate = datetime.datetime.strptime(birthdate, "%Y-%m-%d")
	else:
		message.error("Birth date should not be empty.")

def validate_form_field_not_empty(firstname, lastname, birthdate):
	return len(firstname) > 0 and len(lastname) > 0 and birthdate is not None


### Teacher opeartions
@views.route('/teachers')
def list_teachers():
	teachers = orm_session.query(Teacher).order_by('-id')
	return render_template('teachers.html', teachers=teachers)

@views.route('/new-teacher', methods=['POST'])
def new_teacher():
	firstname = request.form["firstname"].decode("utf-8")
	lastname = request.form["lastname"].decode("utf-8")
	birthdate = request.form["birthdate"].decode("utf-8")

	validate_birthdate(birthdate)

	nationality = request.form["nationality"].decode("utf-8")
	visa_status = request.form["visa_status"].decode("utf-8")
	salary_per_hour = request.form["salary_per_hour"].decode("utf-8")
	if validate_form_field_not_empty(firstname, lastname, birthdate):
		record = Teacher(firstname=firstname, lastname=lastname, \
			birthdate=birthdate, nationality=nationality, visa_status=visa_status, \
			salary_per_hour = salary_per_hour, active=True)

		orm_session.add(record)
		orm_session.commit()

		message.success("sucessful")
	else:
		message.error("Failed!")

	return redirect(url_for("teachers"))

@views.route('/delete-teacher/<int:id>')
def delete_teacher(id):
	teacher = orm_session.query(Teacher).filter(Teacher.id==id).first()

	if teacher:
		logger.info("deleting teacher %s", teacher)
		orm_session.delete(teacher)
		orm_session.commit()
		orm_session.close()
		message.success("successful!")
	else:
		message.error(u"找不到记录")

	return redirect(url_for("teachers"))

@views.route('/edit-teacher/<int:id>')
def edit_teacher(id):
	teacher = orm_session.query(Teacher).filter(Teacher.id==id).first()

	if teacher:
		logger.info("Editing teacher %s", teacher)
		message.success("successful")
		return render_template('edit-teacher.html', teacher=teacher)
	else:
		message.error("Failed!")
		return redirect(url_for("teachers"))

@views.route('/update-teacher/<int:id>', methods=['POST'])
def update_teacher(id):
	teacher = orm_session.query(Teacher).filter(Teacher.id==id).first()

	firstname = request.form["firstname"].decode("utf-8")
	lastname = request.form["lastname"].decode("utf-8")
	birthdate = request.form["birthdate"].decode("utf-8")

	validate_birthdate(birthdate)

	nationality = request.form["nationality"].decode("utf-8")
	visa_status = request.form["visa_status"].decode("utf-8")
	salary_per_hour = request.form["salary_per_hour"].decode("utf-8")

	if validate_form_field_not_empty(firstname, lastname, birthdate):
		logger.info("Teacher's name is %s", firstname + ' ' + lastname)
		teacher.firstname = firstname
		teacher.lastname = lastname
		teacher.birthdate = birthdate
		teacher.nationality = nationality
		teacher.visa_status = visa_status
		teacher.salary_per_hour = salary_per_hour
		orm_session.add(teacher)
		orm_session.commit()
		message.success("successful")
	else:
		message.error("Failed")

	return redirect("teachers")

@views.route('/aboutus')
def about():
	return render_template('aboutus.html')

@views.route('/contact')
def contact():
	return render_template('contact_us.html')

@views.errorhandler(404)
def pageNotFound(error):
    return "page not found"
