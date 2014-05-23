#!/usr/bin/env python

from __init__ import db
from Model import *

# Query users.
print("Querying users")
users = User.query.all()
for user in users:
  print("User: %s" % (user.name))
  print("University ID: %s" % (user.universityId))
  print("User ID: %s" % (user.userId))
  print()

print("Querying courses")
courses = Course.query.all()
for course in courses:
  print("Course ID: %s" % (course.courseId))
  print("Course Title: %s" % (course.courseTitle))
  print("Instructor: %s" % (course.instructor.name))
  enrolledStudents = " ".join([student.name for student in course.students])
  print("Students: %s" % (enrolledStudents))
  print("Lectures:")
  for lecture in course.lectures:
    print("\tLecture Title: %s" % (lecture.lectureTitle))
    for question in lecture.questions:
      print("\tQuestion: %s (%s): %s" % (question.title, question.questionId, question.questionBody))
      allChoices = "[ %s ]" % (" ".join([choice.choiceStr for choice in
        question.choices]))
      correctChoices = "[ %s ]" % (" ".join([choice.choiceStr for choice in
        question.choices if choice.choiceValid != 0]))
      print("\tChoices: %s Correct: %s" % (allChoices, correctChoices))
      for answerRound in question.rounds:
        print("\tResults for round start: %d finish: %d" % (answerRound.startTime,
          answerRound.endTime))
        for response in answerRound.responses:
          studentName = User.query.get(response.studentId).name
          responseTxt = Choice.query.get(response.choiceId).choiceStr
          print("\tResponse: %s : %s" % (studentName, responseTxt))
  print()
