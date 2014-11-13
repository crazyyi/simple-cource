# -*- coding: utf-8 -*-

import message
import logging
from model import *
from bottle import TEMPLATE_PATH, route, redirect, request, jinja2_view, jinja2_template as template
from sqlalchemy.orm import relation, sessionmaker
from sqlalchemy import select
import datetime

TEMPLATE_PATH.append('./templates')
# Log
logging.basicConfig(format='localhost -- [%(asctime)s]%(message)s', level=logging.DEBUG)
log = logging.getLogger(__name__)

# ORM Session
session_maker = sessionmaker(bind=engine)
orm_session = session_maker()

@route('/')
@route('/courses')
@jinja2_view('home.html')
def home():
	courses = orm_session.query(Course).order_by('-id')
	return {'courses':courses}

# New
@route('/new-course', method='POST')
@jinja2_view('new-course.html')
def new_course():
	name = request.forms.get("name").decode("utf-8")

	if len(name) > 0:
		record = Course(name=name, active=True)

		orm_session.add(record)
		orm_session.commit()

		message.success("sucessful!")
	else:
		message.error("Failed!")

	redirect("/")

@route('/update-course/:id', method='POST')
def update_course(id):
	course = orm_session.query(Course).filter(Course.id == id).first()

	name = request.forms.get("name").decode("utf-8")

	if course:
		course.name = name
		orm_session.add(course)
		orm_session.commit()
	else:
		message.error("Failed")
	redirect("/")

# Delete
@route('/delete-course/:id')
def delete(id):
	find_students = select([CourseStudentLink.course_id, CourseStudentLink.student_id]).select_from(CourseStudentLink.__table__).where(CourseStudentLink.course_id == id)

	rs = orm_session.execute(find_students)
	student = rs.fetchone()

	if student:
		message.error(u"还有学生选了这门课")
	else:
		course = orm_session.query(Course).filter(Course.id==id).first()
		log.info("course name: %s", course)

		if course:
			orm_session.delete(course)
			orm_session.commit()

	redirect("/")

@route('/edit-course/:id')
@jinja2_view('edit-course.html')
def edit_course(id):
	course = orm_session.query(Course).filter(Course.id == id).first()
	log.info("editing course: %s", course)

	if course:
		message.success("successful!")
		return {'course':course}
	else:
		message.error("Failed!")
		redirect('/')

@route('/subjects')
@jinja2_view('subjects.html')
def list_subjects():
	subjects = orm_session.query(Subject).order_by('-id')

	return {'subjects': subjects}

@route('/edit-subject/:id')
@jinja2_view('edit-subject.html')
def edit_subject(id):
	subject = orm_session.query(Subject).filter(Subject.id == id).first()

	if subject:
		message.success("successful!")
		return {'subject': subject}
	else:
		message.error("Failed!")
		redirect('/')

@route('/delete-subject/:id')
def delete_subject(id):
	subject = orm_session.query(Subject).filter(Subject.id == id).first()
	if subject:
		message.success("successful!")
		orm_session.delete(subject)
		orm_session.commit()
	else:
		message.error("Failed!")
	
	redirect('/subjects')

@route('/new-subject', method='POST')
def new_subject():
	subject_name = request.forms.get("name").decode("utf-8")
	duration = request.forms.get("duration").decode("utf-8")
	tier = request.forms.get("tier").decode("utf-8")

	if len(subject_name) >0 and len(duration) > 0 and tier:
		subject = Subject(name=subject_name, duration=duration, tier=tier)
		orm_session.add(subject)
		orm_session.commit()
		message.success("successful!")
	else:
		message.error("Failed!")
	
	redirect('/subjects')

@route('/update-subject/:id', method='POST')
def update_subject(id):
	subject = orm_session.query(Subject).filter(Subject.id==id).first()
	log.info("Subject object = %s", subject)
	name = request.forms.get("name").decode("utf-8")
	duration = request.forms.get("duration").decode("utf-8")
	if subject:
		log.info("Subject name = %s and duration = %s.\n textfield name = %s, textfield duration = %s\n",
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

	redirect('/subjects')
	
### Operations for students

@route('/students')
@jinja2_view('students.html')
def list_students():
	students = orm_session.query(Student).order_by('-id')
	return {'students':students}

@route('/new-student', method='POST')
@jinja2_view('students.html')
def new_student():
	firstname = request.forms.get("firstname").decode("utf-8")
	lastname = request.forms.get("lastname").decode("utf-8")
	
	if request.forms.get("paid") == 'on':
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

	redirect("/students")

@route('/edit-student/:id')
@jinja2_view('edit-student.html')
def edit_student(id):
	student = orm_session.query(Student).filter(Student.id==id).first()

	if student:
		log.info("student = %s", student)
		message.success("successful!")
		return {'student':student}
	else:
		message.error("Failed!")
		redirect("/students")

@route('/delete-student/:id')
def delete_student(id):
	student = orm_session.query(Student).filter(Student.id==id).first()

	if student:
		log.info("student = %s", student)
		orm_session.delete(student)
		orm_session.commit()
		orm_session.close()
		message.success("sucessful!")
	else:
		message.error(u"找不到记录")

	redirect('/students')


### Teacher opeartions
@route('/teachers')
@jinja2_view('teachers.html')
def list_teachers():
	teachers = orm_session.query(Teacher).order_by('-id')
	return {'teachers':teachers}

@route('/new-teacher', method='POST')
def new_teacher():
	firstname = request.forms.get("firstname").decode("utf-8")
	lastname = request.forms.get("lastname").decode("utf-8")
	birthdate = request.forms.get("birthdate").decode("utf-8")

	if len(birthdate) > 0:
		birthdate = datetime.datetime.strptime(birthdate, "%Y-%m-%d")
	else:
		message.error("Birth date should not be empty.")

	nationality = request.forms.get("nationality").decode("utf-8")
	visa_status = request.forms.get("visa_status").decode("utf-8")
	salary_per_hour = request.forms.get("salary_per_hour").decode("utf-8")
	if len(firstname) > 0 and len(lastname) > 0 and birthdate is not None:
		record = Teacher(firstname=firstname, lastname=lastname, \
			birthdate=birthdate, nationality=nationality, visa_status=visa_status, \
			salary_per_hour = salary_per_hour, active=True)

		orm_session.add(record)
		orm_session.commit()

		message.success("sucessful")
	else:
		message.error("Failed!")

	redirect("/teachers")

@route('/delete-teacher/:id')
def delete_teacher(id):
	teacher = orm_session.query(Teacher).filter(Teacher.id==id).first()

	if teacher:
		log.info("deleting teacher %s", teacher)
		orm_session.delete(teacher)
		orm_session.commit()
		orm_session.close()
		message.success("successful!")
	else:
		message.error(u"找不到记录")

	redirect("/teachers")

@route('/edit-teacher/:id')
@jinja2_view('edit-teacher.html')
def edit_teacher(id):
	teacher = orm_session.query(Teacher).filter(Teacher.id==id).first()

	if teacher:
		log.info("Editing teacher %s", teacher)
		message.success("successful")
		return {'teacher':teacher}
	else:
		message.error("Failed!")
		redirect("/teachers")
