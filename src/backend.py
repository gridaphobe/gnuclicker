#! /usr/bin/env python
from flask import Flask, jsonify, make_response
from flask.ext.restful import Api, Resource, reqparse
from flask.ext.sqlalchemy import SQLAlchemy
import uuid
import config
from Model import db, User, Course, Lecture, Question, Choice, Tag, Response, \
                  Round
from __init__ import app
import datetime
import time
from copy import copy
from common import *
from error import *

api = Api(app)

def getArg(args, name):
  return args.get(name, None)

def objectify3(o, t):
  if (isinstance(t, tuple)):
    res = {}
    for k in t:
      if (isinstance(k, tuple)):
        res[k[0]] = objectify3(getattr(o, k[0]), k[1])
      else:
        res[k] = getattr(o, k)
    return res
  elif (isinstance(t, list)):
    return map(lambda x: objectify3(x, t[0]), o)
  else:
    return o
    
# jsonify() seems to insist that no arrays can be used as top-level
# json objects. To satisfy it, for now wrap everything in a top-level
# { res: ... } object
def myJson(o): 
    return jsonify(res = objectify(o))

def myJson3(o, t): 
    return jsonify(res = objectify3(o, t))

class CoursesListApi(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('studentId', type=str)
    self.reqparse.add_argument('instructorId', type=str)
    super(CoursesListApi, self).__init__()

  def get(self):
    '''
    Return all courses matching the given student and instructor id filters.
    '''
    args = self.reqparse.parse_args()
    studentId = getArg(args, "studentId")
    instructorId = getArg(args, "instructorId")

    if (studentId):
      student = User.query.get(studentId)
      if (student == None):
        return error(EBADSTUDENTID, studentId)

    if (instructorId):
      instructor = User.query.get(instructorId)
      if (instructor == None):
        return error(EBADINSTRUCTORID, instructorId)
        
    res = None

    if (studentId and instructorId):
      # Return any classes thought by instructor and taken by student
      res = student.enrolledIn.filter(Course.instructorId == instructorId)
    elif (studentId):
      # Return any classes taken by student
      res = student.enrolledIn
    elif (instructorId):
      # Return any classes thought by instructor 
      res = instructor.instructs
    else:
      # Return all classes
      res = Course.query.all()

    return myJson3(res, [("courseId", "courseTitle", "instructorId")])
 
api.add_resource(CoursesListApi, '/courses', endpoint='courses_list')

class LecturesListApi(Resource):
  def get(self, courseId):
    '''
    Return all lectures for the given course.
    '''
    course = Course.query.get(courseId)
    if course:
      return myJson3(course.lectures, [('courseId', 'lectureTitle', \
        'lectureId', 'date' )])
    else:
      return error(EBADCOURSEID, courseId)


api.add_resource(LecturesListApi, '/courses/<string:courseId>/lectures',
  endpoint='lectures_list')

class CourseStudentManifestApi(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('lectureId', type=str)
    super(CourseStudentManifestApi, self).__init__()

  def get(self, courseId):
    '''
    Return all students enrolled in course (if no lecture specified) or all
    students attending lecture (if lecture specified).
    '''
    args = self.reqparse.parse_args()
    lectureId = getArg(args, "lectureId")
    course = Course.query.get(courseId)
    userDesc = [( 'userId' , 'universityId', 'name' )]

    if (course == None):
      return error(EBADCOURSEID, courseId)

    if lectureId is None:
      # Return all students enrolled in class.
      return myJson3(course.students, userDesc)
    else:
      # Return all students attending a lecture.
      lecture = Lecture.query.get(lectureId)

      if (not lecture):
        return error(EBADLECTUREID, lectureId)

      if lecture.course != course:
        # Invalid lecture for this course.
        return error(ELECTUREMISMATCH, lectureId, courseId)

      students = set()
      for question in lecture.questions:
        for answerRound in question.rounds:
          for response in answerRound.responses:
            students.add(User.query.get(response.studentId))

      return myJson3(list(students), userDesc)

api.add_resource(CourseStudentManifestApi,
  '/courses/<string:courseId>/students', endpoint='course_student_manifest')

class UserApi(Resource):
  def get(self, userId):
    '''
    Return user details for specified user.
    '''
    user = User.query.get(userId)
    if (user):
      return myJson3(user, ( 'userId', 'universityId', 'name' ))
    else:
      return error(EBADUSERID, userId)

api.add_resource(UserApi, '/users/<string:userId>', endpoint='user')

class QuestionsApi(Resource):
  def __init__(self):
    # Arguments for get()
    self.getReqparse = reqparse.RequestParser()
    self.getReqparse.add_argument('lectureId', type=str)
    self.getReqparse.add_argument('tag', type=str, action='append')
    self.getReqparse.add_argument('questionId', type=str)

    # Arguments for post()
    self.postReqparse = reqparse.RequestParser()
    self.postReqparse.add_argument('lectureId', type=str, required=True)
    self.postReqparse.add_argument('title', type=str, required=True)
    self.postReqparse.add_argument('body', type=str, required=True)
    self.postReqparse.add_argument('choices', type=str, required=True,
      action='append')
    self.postReqparse.add_argument('correct-choices', type=str, required=True,
      action='append')
    self.postReqparse.add_argument('tag', type=str, action='append')

    super(QuestionsApi, self).__init__()

  def get(self, courseId):
    '''
    Return all questions, matching the lecture id if provided, and all of the
    provided tags.
    '''
    args = self.getReqparse.parse_args()
    lectureId = getArg(args, "lectureId")
    rawTags = getArg(args, "tag")
    questionId = getArg(args, 'questionId')
    tags = set(rawTags if rawTags else [])
    course = Course.query.get(courseId)
    qDesc = [('questionId', 'lectureId', 'title', \
      'questionBody', ('tags', [('tagId', 'tagText')]), 'activeRound')]

    if course == None:
      return error(EBADCOURSEID, courseId)

    if questionId != None:
      question = Question.query.get(questionId)
      
      if (question == None):
        return error(EBADQUESTIONID, questionId)

      return myJson3([question], qDesc)

    if lectureId is None:
      # Get all questions for course across all lectures.
      questions = []
      for lecture in course.lectures:
        for question in lecture.questions:
          if tags is None:
            questions.append(question)
          else:
            questionTags = set([tag.tagText for tag in question.tags])
            if tags <= questionTags:
              questions.append(question)
      return myJson3(questions, qDesc)
    else:
      lecture = Lecture.query.get(lectureId)
      if (not lecture):
        return error(EBADLECTUREID, lectureId)
      if lecture.course != course:
        return error(ELECTUREMISMATCH, lectureId, courseId)
      if tags is None:
        return myJson3(lecture.questions, qDesc)
      else:
        questions = []
        for question in lecture.questions:
          questionTags = set([tag.tagText for tag in question.tags])

          if tags <= questionTags:
            questions.append(question)
        return myJson3(questions, qDesc)

  def post(self, courseId):
    '''
    Add a question with the specified parameters.
    '''
    args = self.postReqparse.parse_args()
    lectureId = getArg(args, "lectureId")
    title = getArg(args, "title")
    body = getArg(args, "body")
    choices = nonempty(getArg(args, "choices"))
    correctChoices = nonempty(getArg(args, "correct-choices"))
    tags = getArg(args, "tag")

    # Check that the answer choices are valid.
    if choices is None or len(choices) == 0:
      return error(EMISSINGARG, "choices")
    if correctChoices is None or len(correctChoices) == 0:
      return error(EMISSINGARG, "correct-choices")
    choices = set(choices)
    correctChoices = set(correctChoices)
    if not correctChoices <= choices:
      return error(ECORRECTNONSUBSET, ppset(correctChoices), ppset(choices))

    # First check that lecture ID is valid.
    course = Course.query.get(courseId)
    if course == None:
      return error(EBADCOURSEID, courseId)

    lecture = Lecture.query.get(lectureId)

    if lecture is None:
      return error(EBADLECTUREID, lectureId)

    if lecture.course != course:
      return error(ELECTUREMISMATCH, lectureId, courseId)

    # Create a question.
    question = Question(questionId=str(uuid.uuid4()), lecture=lecture,
      title=title, questionBody=body)
    db.session.add(question)

    # Handle tags.
    if tags is not None:
      for tagText in tags:
        # Find or create.
        tags = list(Tag.query.filter(Tag.tagText == tagText))
        tag = None

        if len(tags) == 0:
          tag = Tag(tagId=str(uuid.uuid4()), tagText=tagText)
          db.session.add(tag)
        else:
          tag = tags[0]

        question.tags.append(tag)

    # Answer choices.
    for choice in choices:
      if choice in correctChoices:
        choiceValid = 1
      else:
        choiceValid = 0
      choiceObj = Choice(choiceId=str(uuid.uuid4()), question=question,
        choiceStr=choice, choiceValid=choiceValid)
      db.session.add(choiceObj)

    # Alright, commit to db.
    db.session.commit()
    return myJson3(question, ('questionId', 'lectureId', 'title', \
      'questionBody', \
      ('choices', [('choiceId', 'choiceValid', 'choiceStr')]), 
      ('correctChoices', [('choiceId', 'choiceValid', 'choiceStr')]), ))

api.add_resource(QuestionsApi, '/courses/<string:courseId>/questions')

class EditQuestionApi(Resource):
  def __init__(self):
    # Arguments for put()
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('lectureId', type=str)
    self.reqparse.add_argument('title', type=str, required=True)
    self.reqparse.add_argument('body', type=str, required=True)
    self.reqparse.add_argument('choices', type=str, required=True,
      action='append')
    self.reqparse.add_argument('correct-choices', type=str, required=True,
      action='append')
    super(EditQuestionApi, self).__init__()

  def put(self, courseId, questionId):
    '''
    Update the specified question with the specified parameters.
    '''
    course = Course.query.get(courseId)

    if (not course):
      return error(EBADCOURSEID, courseId)

    question = Question.query.get(questionId)
    if (not question):
      return error(EBADQUESTIONID, questionId)
    # Check that the question belongs to the course.
    if question.lecture.course != course:
      return error(EQUESTIONMISMATCH, questionId, courseId)

    # Parse arguments.
    args = self.reqparse.parse_args()
    lectureId = getArg(args, "lectureId")
    title = getArg(args, "title")
    body = getArg(args, "body")
    choices = nonempty(getArg(args, "choices"))
    correctChoices = nonempty(getArg(args, "correct-choices"))
    tags = getArg(args, "tag")


    # Check that the answer choices are valid.
    if choices is None or len(choices) == 0:
      return error(EMISSINGARG, "choices")
    if correctChoices is None or len(correctChoices) == 0:
      return error(EMISSINGARG, "correct-choices")
    choices = set(choices)
    correctChoices = set(correctChoices)
    if not correctChoices <= choices:
      return error(ECORRECTNONSUBSET, ppset(correctChoices), ppset(choices))

    # Check lecture.
    if (lectureId and lectureId != question.lectureId):
      # Remove the question from current lecture and move it to new lecture.
      currLecture = question.lecture
      newLecture = Lecture.query.get(lectureId)
      if newLecture.course != course:
        return None
      currLecture.questions.remove(question)
      newLecture.questions.append(question)

    # Set title, body, choices and correct choices.
    question.title = title
    question.questionBody = body

    # Remove all current choices.
    for choice in question.choices:
      db.session.delete(choice)

    # Recreate choices.
    for choice in choices:
      if choice in correctChoices:
        choiceValid = 1
      else:
        choiceValid = 0
      choiceObj = Choice(choiceId=str(uuid.uuid4()), question=question,
        choiceStr=choice, choiceValid=choiceValid)
      db.session.add(choiceObj)

    # Alright, commit.
    db.session.commit()
    return myJson3(question, ('questionId', 'lectureId', 'title', \
      'questionBody', \
      ('choices', [('choiceId', 'choiceValid', 'choiceStr')]), 
      ('correctChoices', [('choiceId', 'choiceValid', 'choiceStr')]), ))


api.add_resource(EditQuestionApi,
  '/courses/<string:courseId>/questions/<string:questionId>',
  endpoint='edit_question')

class ResponseRoundsApi(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('studentId', type=str)

  def get(self, courseId, questionId):
    '''
    Return responses for all rounds for given class and question, optionally
    filtering on student id.
    '''
    course = Course.query.get(courseId)
    question = Question.query.get(questionId)
    args = self.reqparse.parse_args()
    studentId = getArg(args, "studentId")

    if (not course):
      return error(EBADCOURSEID, courseId)

    if (not question):
      return error(EBADQUESTIONID, questionId)

    # Verify that the question's lecture is associated with the course.
    if (question.lecture.course != course):
      return error(EQUESTIONMISMATCH, questionId, courseId)

    responses = []

    if studentId is None:
      # Get all responses for this question for all rounds.
      for answerRound in question.rounds:
        responses.extend(answerRound.responses)
    else:
      for answerRound in question.rounds:
        responses.extend([response for response in answerRound.responses
          if response.studentId == studentId])

    return myJson3(responses, \
      [('responseId', 'roundId', 'studentId', 'choiceId')])

api.add_resource(ResponseRoundsApi,
  '/courses/<string:courseId>/questions/<string:questionId>/responses',
  endpoint='response_rounds')

class ResponseApi(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('choiceId', type=str, required=True)
    super(ResponseApi, self).__init__()

  def getSomeStudentInCourse(self, course):
    # XXX Temporary hack till we have user logins.
    return course.students[0]

  def post(self, courseId, questionId):
    '''
    Given the course and question, note that the current user submitted the
    specified answer.
    '''
    course = Course.query.get(courseId)
    question = Question.query.get(questionId)
    args = self.reqparse.parse_args()
    choiceId = getArg(args, "choiceId")

    if (not course):  return error(EBADCOURSEID, courseId)
    if (not question):  return error(EBADQUESTIONID, questionId)

    # Check that the question belongs to the course.
    if question.lecture.course != course:
      return error(EQUESTIONMISMATCH, questionId, courseId)

    # Check if there's  an active round.
    if question.activeRound == None or question.activeRound == "":
      return error(ENOACTIVEROUND, questionId) 

    choice = Choice.query.get(choiceId)
    if (not choice):
      return error(EBADCHOICEID, choiceId)

    # Make sure choice corresponds to question.
    if choice.question != question:
      return error(ECHOICEMISMATCH, choiceId, questionId)

    # TODO: Once user logins/identities are implemented, we'll pull the student
    # ID from the session. For now, we hardcode it as being the answer
    # for...some random student in the class.
    student = self.getSomeStudentInCourse(course)

    # Alright, record the answer for this round for this question.
    args = self.reqparse.parse_args()
    response = Response(
      responseId=str(uuid.uuid4()),
      roundFor=Round.query.get(question.activeRound),
      studentId=student.userId,
      choiceId=choice.choiceId)
    db.session.add(response)
    db.session.commit()

    return myJson3(response, ('responseId', 'roundId', 'studentId', 'choiceId'))

api.add_resource(ResponseApi,
  '/courses/<string:courseId>/question/<string:questionId>/respond',
  endpoint='response')

class RoundStartApi(Resource):
  def post(self, courseId, questionId):
    '''
    Given the course id and question, start a round of questioning.
    '''
    course = Course.query.get(courseId)
    question = Question.query.get(questionId)

    if (not course):
      return error(EBADCOURSEID, courseId)

    if (not question):
      return error(EBADQUESTIONID, questionId)

    # Check that the question belongs to the course.
    if question.lecture.course != course:
      return error(EQUESTIONMISMATCH, questionId, courseId)

    # Check if there's already an active round.
    if question.activeRound != "" and question.activeRound != None:
      return error(EQUESTIONACTIVE, questionId)

    # Alright, create a round starting *now*, ending unspecified, add it to the
    # table of rounds, and set it as the active round for the question.
    # TODO(dimo): Should the end time really be unspecified here?
    now = int(time.time())
    answerRound = Round(roundId=str(uuid.uuid4()), questionId=questionId,
      startTime=now, endTime=-1)
    question.activeRound = answerRound.roundId
    db.session.add(answerRound)
    # Done, return round.
    return myJson3(answerRound, ('roundId', 'questionId', 'startTime', \
      'endTime', ('responses', [('responseId', 'roundId', 'studentId', 'choiceId')])))

api.add_resource(RoundStartApi,
  '/courses/<string:courseId>/question/<string:questionId>/start',
  endpoint='start_round')

class RoundEndApi(Resource):
  def post(self, courseId, questionId):
    '''
    Given the course id and question, end the round of questioning.
    '''
    course = Course.query.get(courseId)
    question = Question.query.get(questionId)

    if (not course):
      return error(EBADCOURSEID, courseId)

    if (not question):
      return error(EBADQUESTIONID, questionId)

    # Check that the question belongs to the course.
    if question.lecture.course != course:
      return error(EQUESTIONMISMATCH, questionId, courseId)

    # Check if there's no active round.
    if question.activeRound == "" or question.activeRound == None:
      return error(ENOACTIVEROUND, questionId)

    # Alright, close this round.
    now = int(time.time())
    answerRound = Round.query.get(question.activeRound)
    answerRound.endTime = now
    question.activeRound = ""
    db.session.commit()
    return myJson3(answerRound, ('roundId', 'questionId', 'startTime', \
      'endTime', ('responses', [('responseId', 'roundId', 'studentId', 'choiceId')])))

api.add_resource(RoundEndApi,
  '/courses/<string:courseId>/question/<string:questionId>/end',
  endpoint='end_round')

class LecturesApi(Resource):
  def __init__(self):
    self.postReqparse = reqparse.RequestParser()
    self.postReqparse.add_argument('title', type=str)
    self.postReqparse.add_argument('date', type=int)
    super(LecturesApi, self).__init__()

  def get(self, courseId):
    '''
    Get all lectures for course.
    '''
    course = Course.query.get(courseId)
    return myJson(course.lectures)

  def post(self, courseId):
    '''
    Add a lecture with specified title and date.
    '''
    args = self.postReqparse.parse_args()
    title = getArg(args, "title")
    date = datetime.datetime.fromtimestamp(int(getArg(args, "date")))
    course = Course.query.get(courseId)
    lecture = Lecture(lectureId=str(uuid.uuid4()), course=course,
      lectureTitle=title, date=date)
    db.session.add(lecture)
    db.session.commit()
    return myJson(lecture)

api.add_resource(LecturesApi, '/courses/<string:courseId>/lectures',
  endpoint='lectures')

class LectureDetailsApi(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('title', type=str)
    self.reqparse.add_argument('date', type=int)
    super(LectureDetailsApi, self).__init__()

  def get(self, courseId, lectureId):
    '''
    Get lecture details.
    '''
    course = Course.query.get(courseId)
    lecture = Lecture.query.get(lectureId)
    if lecture.course != course:
      return None
    return myJson(lecture)

  def put(self, courseId, lectureId):
    '''
    Update lecture details.
    '''
    args = self.reqparse.parse_args()
    title = getArg(args, "title")
    date = datetime.datetime.fromtimestamp(int(getArg(args, "date")))
    course = Course.query.get(courseId)
    lecture = Lecture.query.get(lectureId)
    if lecture.course != course:
      return None
    # Update details.
    lecture.title = title
    lecture.date = date
    db.session.commit()
    return myJson(lecture)

api.add_resource(LectureDetailsApi,
  '/courses/<string:courseId>/lectures/<string:lectureId>',
  endpoint='lecture_details')

class GradesApi(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('studentId', type=str)
    self.reqparse.add_argument('lectureId', type=str)
    self.reqparse.add_argument('questionId', type=str)
    self.reqparse.add_argument('displayRound', type=str)
    super(GradesApi, self).__init__()

  def get(self, courseId):
    '''
    Return grades for course, filtering optionally on student, lecture, question
    and response type (first round/last round/all rounds).
    '''
    # TODO: Implement
    # Do this at end once we have the semantics/UI nailed down.
    return None

api.add_resource(GradesApi, '/courses/<string:courseId>/grades',
  endpoint='grades')

if __name__ == '__main__':
    app.run()
