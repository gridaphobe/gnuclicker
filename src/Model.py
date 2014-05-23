'''
Model.py

Describes all types for Gnuclicker.
'''
from flask.ext.sqlalchemy import SQLAlchemy
from __init__ import db

# Many to many table for tracking user enrollment in course as student.
enrollments = db.Table('enrollments',
  db.Column('student_id', db.String, db.ForeignKey('user.userId')),
  db.Column('course_id', db.String, db.ForeignKey('course.courseId'))
)

class User(db.Model):
  '''
  Describes a user in the system. A user may either be a teacher or a student in
  relation to a course; for example, teach one course, and be enrolled in two.
  However, a user cannot be both a teacher and a student for the same course.


  Fields:
  userId: UUID Primary Key.
  universityId : String, represents student/instructor ID in university.
  name: User's name.
  enrolledIn : courses that the User is enrolled in as a student.
  instructs : courses that the User instructs.
  '''
  userId = db.Column(db.String, primary_key = True)
  universityId = db.Column(db.String)
  name = db.Column(db.String)
  enrolledIn = db.relationship('Course', secondary=enrollments,
    backref='students')
  instructs = db.relationship('Course', backref='instructor')

  def __iter__(self):
    yield ('userId', self.userId)
    yield ('universityId', self.universityId)
    yield ('name', self.name)
    yield ('enrolledIn', self.enrolledIn)
    yield ('instructs', self.instructs)

class Course(db.Model):
  '''
  A course has a title and a single instructor. Multiple students are enrolled
  in a class (see the 'students' backref). A course is associated with multiple
  lectures.

  Fields:
  courseId : UUID Primary Key.
  courseTitle : Course Title.
  instructorId : ID for instructor of course. Instructor is a user.
  lectures : A course has many lectures. A lecture has one course.
  '''
  courseId = db.Column(db.String, primary_key = True)
  courseTitle = db.Column(db.String)
  instructorId = db.Column(db.String, db.ForeignKey('user.userId'))
  lectures = db.relationship('Lecture', backref='course')

  def __iter__(self):
    yield ('courseId', self.courseId)
    yield ('courseTitle', self.courseTitle)
    yield ('instructorId', self.instructorId)
    yield ('lectures', self.lectures)

class Lecture(db.Model):
  '''
  A lecture is associated with a course. It contains multiple questions.

  Fields:
  lectureId : UUID Primary Key.
  courseId : ID for course of lecture.
  questions : A lecture has many questions. A question has one lecture.
  '''
  lectureId = db.Column(db.String, primary_key = True)
  courseId = db.Column(db.String, db.ForeignKey('course.courseId'))
  lectureTitle = db.Column(db.String)
  questions = db.relationship('Question', backref='lecture')

class Question(db.Model):
  '''
  A question is associated with a lecture. It has a title, a body, multiple
  answer choices, a subset of correct answer choices, and multiple potential
  rounds of responses.

  Fields:
  questionId : UUID Primary Key.
  lectureId : ID for lecture question is associated with.
  title : Short title of question.
  questionBody : One to one relationship with question body.
  choices : One to one relationship with answer choices.
  correctChoices : One to one relationship with correct answers.
  rounds : One question has many rounds. Round has one question.
  '''
  questionId = db.Column(db.String, primary_key = True)
  lectureId = db.Column(db.String, db.ForeignKey('lecture.lectureId'))
  title = db.Column(db.String)
  questionBody = db.Column(db.String)
  choices = db.relationship('Choice', backref='question')
  correctChoices = db.relationship('Choice')
  rounds = db.relationship('Round', backref='question')

class Choice(db.Model):
  '''
  An answer choice is a string. It is associated with a question.

  Fields:
  choiceId : UUID Primary Key.
  questionId : Question that this choice is associated with.
  choiceStr : Possible response to question.
  '''
  choiceId = db.Column(db.String, primary_key = True)
  questionId = db.Column(db.String, db.ForeignKey('question.questionId'))
  choiceStr = db.Column(db.String)

class Round(db.Model):
  '''
  A round is associated with a question. It has a start time, an end time, and a
  set of responses from students.

  Fields:
  roundID : UUID Primary Key.
  startTime : Integer seconds from epoch.
  endTime : Integer seconds from epoch.
  questionId : Question being asked in round.
  responses : One round, many responses.
  '''
  roundId = db.Column(db.String, primary_key = True)
  questionId = db.Column(db.String, db.ForeignKey('question.questionId'))
  startTime = db.Column(db.Integer)
  endTime = db.Column(db.Integer)
  responses = db.relationship('Response', backref='roundFor')

class Response(db.Model):
  '''
  A response is associated with a round, a student, and the answer choice they
  selected.

  Fields:
  responseId : UUID Primary key.
  roundId: round this response is associated with.
  studentId : student that submitted this response.
  choiceId : choice picked by student.
  '''
  responseId = db.Column(db.String, primary_key = True)
  roundId = db.Column(db.String, db.ForeignKey('round.roundId'))
  studentId = db.Column(db.String, db.ForeignKey('user.userId'))
  choiceId = db.Column(db.String, db.ForeignKey('choice.choiceId'))

