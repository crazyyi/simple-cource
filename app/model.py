from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

Base = declarative_base()

class Course(Base):
	__tablename__ = 'course'
	id = Column(Integer, primary_key=True)
	name = Column(String(255), nullable=False)
	subjects = relationship('Subject', secondary='course_subject_link')
	students = relationship('Student', secondary='course_student_link')
	active = Column(Boolean)
	def __repr__(self):
		return "<{0}:{1.name}:{1.subjects!r}:{1.students!r}>".format(Course, self)

class Subject(Base):
	__tablename__ = 'subject'
	id = Column(Integer, primary_key=True)
	name = Column(String(255), nullable=False)
	duration = Column(Integer) # number of hours
	tier = Column(Integer)
	active = Column(Boolean)
	courses = relationship('Course', secondary='course_subject_link')
	def __repr__(self):
		return "<{0}:{1.name}:{1.courses.!r}>".format(Subject, self)

class CourseSubjectLink(Base):
	__tablename__ = 'course_subject_link'
	course_id = Column(Integer, ForeignKey('course.id'), primary_key=True)
	subject_id = Column(Integer, ForeignKey('subject.id'), primary_key=True)

class Teacher(Base):
	__tablename__ = 'teacher'
	id = Column(Integer, primary_key=True)
	firstname = Column(String(255), nullable=False)
	lastname = Column(String(255), nullable=False)
	birthdate = Column(Date)
	visa_status = Column(String(255))
	nationality = Column(String(255))
	salary_per_hour = Column(Integer)
	active = Column(Boolean)

	def __repr__(self):
		return "<{0}:{1.firstname}:{1.lastname}>".format(Teacher, self)

class Student(Base):
	__tablename__ = 'student'
	id = Column(Integer, primary_key=True)
	firstname = Column(String(255), nullable=False)
	lastname = Column(String(255), nullable=False)
	birthdate = Column(Date)
	level = Column(String(255))
	paid = Column(Boolean)
	paid_date = Column(DateTime)
	#payment_methods = relationship('PaymentMethod', secondary='course_student_link')
	courses = relationship('Course', secondary='course_student_link')
	active = Column(Boolean)

	def __repr__(self):
		return "<{0}:{1.firstname}:{1.lastname}>".format(Student, self)

class CourseStudentLink(Base):
	__tablename__ = 'course_student_link'
	course_id = Column(Integer, ForeignKey('course.id'), primary_key=True)
	student_id = Column(Integer, ForeignKey('student.id'), primary_key=True)
	payment_method_id = Column(Integer, ForeignKey('payment_method.id'), primary_key=True)

class PaymentMethod(Base):
	__tablename__ = 'payment_method'
	id = Column(Integer, primary_key=True)
	name = Column(String(255), nullable=False)
	students = relationship('Student', secondary='course_student_link')
	active = Column(Boolean)

engine = create_engine('sqlite:///database/courses.sqlite', echo=True)
Base.metadata.create_all(engine)
