#! /usr/bin/env python
from flask import Flask, jsonify, make_response
from flask.ext.restful import Api, Resource, reqparse
from flask.ext.sqlalchemy import SQLAlchemy
import uuid
import config
from Model import db, User, Course
from __init__ import app
import datetime
from copy import copy

api = Api(app)

def getArg(args, name):
  return args.get(name, None)

def objectify(o):
  if (isinstance(o, list)):
    return map(lambda x: objectify(x), o)
  elif (hasattr(o, "__dict__")):
    res = copy(o.__dict__)
    if ("_sa_instance_state" in res):
        del res["_sa_instance_state"]
    return res
  else:
    return res

# jsonify() seems to insist that no arrays can be used as top-level
# json objects. To satisfy it, for now wrap everything in a top-level
# { res: ... } object
def myJson(o): return jsonify(res = objectify(o))

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

    res = None

    if (studentId and instructorId):
      # Return any classes thought by instructor and taken by student
      res = User.query.get(studentId).enrolledIn.filter(\
        Course.instructorId == instructorId)
    elif (studentId):
      # Return any classes thought by instructor and taken by student
      res = User.query.get(studentId).enrolledIn
    elif (instructorId):
      # Return any classes thought by instructor and taken by student
      res = User.query.get(instructorId).instructs
    else:
      # Return all classes
      res = Course.query.all()

    return myJson(res)

api.add_resource(CoursesListApi, '/courses', endpoint='courses_list')

class LecturesListApi(Resource):
  def get(self, courseId):
    '''
    Return all lectures for the given course.
    '''
    course = Course.query.get(courseId)
    return myJson(course.lectures)

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
    if lectureId is None:
      # Return all students enrolled in class.
      return myJson(course.students)
    else:
      # Return all students attending a lecture.
      lecture = Lecture.query.get("lectureId")
      if lecture.course != course:
        # Invalid lecture for this course.
        return None
      students = set()
      for question in lecture.questions:
        for answerRound in question.rounds:
          for response in answerRound.responses:
            students.add(response.studentId)

      return myJson(students)

api.add_resource(CourseStudentManifestApi,
  '/courses/<string:courseId>/students', endpoint='course_student_manifest')

class UserApi(Resource):
  def get(self, userId):
    '''
    Return user details for specified user.
    '''
    return myJson(User.query.get(userId))

api.add_resource(UserApi, '/users/<string:userId>', endpoint='user')

class QuestionsApi(Resource):
  def __init__(self):
    # Arguments for get()
    self.getReqparse = reqparse.RequestParser()
    self.getReqparse.add_argument('lectureId', type=str)
    self.getReqparse.add_argument('tag', type=str, action='append')

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
    tags = set(getArg(args, "tag"))
    course = Course.query.get(courseId)

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
      return myJson(questions)
    else:
      lecture = Lecture.query.get(lectureId)
      if lecture.course != course:
        return None
      if tags is None:
        return myJson(lecture.questions)
      else:
        questions = []
        for question in lecture.questions:
          questionTags = set([tag.tagText for tag in question.tags])
          if tags <= questionTags:
            questions.append(question)
        return myJson(questions)

  def post(self, courseId):
    '''
    Add a question with the specified parameters.
    '''
    args = self.postReqparse.parse_args()
    lectureId = getArg(args, "lectureId")
    title = getArg(args, "title")
    body = getArg(args, "body")
    choices = getArg(args, "choices")
    correctChoices = getArg(args, "correct-choices")
    tags = getArg(args, "tag")

    # Check that the answer choices are valid.
    if choices is None or len(choices) == 0:
      return None
    if correctChoices is None or len(correctChoices) == 0:
      return None
    choices = set(choices)
    correctChoices = set(correctChoices)
    if not correctChoices <= choices:
      return None

    # First check that lecture ID is valid.
    course = Course.query.get(courseId)
    lecture = Lecture.query.get(lectureId)
    if lecture is None or lecture.course != course:
      return None

    # Create a question.
    question = Question(questionId=str(uuid.uuid4()), lecture=lecture,
      title=title, questionBody=body)
    db.session.add(question)

    # Handle tags.
    if tags is not None:
      for tagText in tags:
        # Find or create.
        tag = Tag.query.all().filter(Tag.tagText == tagText)
        if tag is None:
          tag = Tag(tagId=str(uuid.uuid4()), tagText=tag)
          db.session.add(tag)
        question.tags.append(tag)

    # Answer choices.
    for choice in choices:
      if choice in correctChoices:
        choiceValid = 1
      else:
        choiceValid = 0
      choiceObj = Choice(choiceId=str(uuid.uuid4()), question=question,
        choiceStr=choice, choiceValid=choiceValid)
      db.session.add(choice)

    # Alright, commit to db.
    db.session.commit()
    return myJson(question)

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
    courseId = Course.query.get(courseId)
    question = Question.query.get(questionId)
    # Check that the question belongs to the course.
    if question.lecture.course != course:
      return None

    # Parse arguments.
    args = self.reqparse.parse_args()
    lectureId = getArg(args, "lectureId")
    title = getArg(args, "title")
    body = getArg(args, "body")
    choices = getArg(args, "choices")
    correctChoices = getArg(args, "correct-choices")
    tags = getArg(args, "tag")

    # Check that the answer choices are valid.
    if choices is None or len(choices) == 0:
      return None
    if correctChoices is None or len(correctChoices) == 0:
      return None
    choices = set(choices)
    correctChoices = set(correctChoices)
    if not correctChoices <= choices:
      return None

    # Check lecture.
    if lectureId != question.lectureId:
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
      db.session.add(choice)

    # Alright, commit.
    db.session.commit()
    return myJson(question)

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

    # Verify that the question's lecture is associated with the course.
    if (question.lecture.course != course):
      return None
    responses = []
    if studentId is None:
      # Get all responses for this question for all rounds.
      for answerRound in question.rounds:
        responses.extend(answerRound.responses)
    else:
      for answerRound in question.rounds:
        responses.extend([response for response in answerRound.responses
          if response.studentId == studentId])
    return myJson(responses)

api.add_resource(ResponseRoundsApi,
  '/courses/<string:courseId>/questions/<string:questionId>/responses',
  endpoint='response_rounds')

class ResponseApi(Resource):
  def __init__(self):
    self.reqparse = reqparse.RequestParser()
    self.reqparse.add_argument('responseId', type=str, required=True)
    super(ResponseApi, self).__init__()

  def post(self, courseId, questionId):
    '''
    Given the course and question, note that the current user submitted the
    specified answer.
    '''
    # TODO: Implement.
    # Student response to question is recorded as part of current round (current
    # round is set via call to round start api).
    # If no round is active, data is discarded.
    return None

api.add_resource(ResponseApi,
  '/courses/<string:courseId>/question/<string:questionId>/respond',
  endpoint='response')

class RoundStartApi(Resource):
  def post(self, courseId, questionId):
    '''
    Given the course id and question, start a round of questioning.
    '''
    # TODO: Implement.
    # If round already active, return error. Else start round.
    return None

api.add_resource(RoundStartApi,
  '/courses/<string:courseId>/question/<string:questionId>/start',
  endpoint='start_round')

class RoundEndApi(Resource):
  def post(self, courseId, questionId):
    '''
    Given the course id and question, end the round of questioning.
    '''
    # TODO: Implement.
    # If round not active, return error, else end round. Need to determine where
    # this state should live.
    return None

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
