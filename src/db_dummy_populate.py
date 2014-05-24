#!/usr/bin/env python

from __init__ import db
from Model import *
import uuid

'''
Create dummy objects to populate the database for testing.
'''

# Dummy users.
user1Id = uuid.uuid4()
user2Id = uuid.uuid4()
user3Id = uuid.uuid4()

user1 = User(userId=str(user1Id), universityId="A12345678", name="Joe Pesci")
user2 = User(userId=str(user2Id), universityId="B12345678", name="Joe Biden")
user3 = User(userId=str(user3Id), universityId="C12345678", name="Joe Stalin")

# Add users to db session.
db.session.add(user1)
db.session.add(user2)
db.session.add(user3)

# Add courses. user2 and user1 teach a class each.
course1Id = uuid.uuid4()
course2Id = uuid.uuid4()
course1 = Course(courseId=str(course1Id), courseTitle="Defense Against The Dark Arts",
  instructor=user1)
course2 = Course(courseId=str(course2Id), courseTitle="CSE210",
  instructor=user2)

# Add courses to db session.
db.session.add(course1)
db.session.add(course2)

# Note that user3 is a student in both classes. Note that user1 is a student in
# user2's class and vice versa.
user3.enrolledIn.append(course1)
user3.enrolledIn.append(course2)
user1.enrolledIn.append(course2)
user2.enrolledIn.append(course1)

# Add a lecture to user2's class.
lecture1Id = uuid.uuid4()
lecture1 = Lecture(lectureId=str(lecture1Id), course=course2,
  lectureTitle="Administrivia")

# Add lecture to db session.
db.session.add(lecture1)

# Add question to that lecture.
q1Id = uuid.uuid4()
question1 = Question(questionId=str(q1Id), lecture=lecture1,
  title="Bro, do you even aerodynamic lift?",
  questionBody="What is the unladen airspeed of a swallow?")

# Create tags
tag1Id = uuid.uuid4()
tag2Id = uuid.uuid4()
tag3Id = uuid.uuid4()
tag1 = Tag(tagId=str(tag1Id), tagText="much_tag")
tag2 = Tag(tagId=str(tag2Id), tagText="wow")
tag3 = Tag(tagId=str(tag3Id), tagText="such_question")

# Associate tags with question and lecture.
question1.tags.append(tag3)
question1.tags.append(tag2)
lecture1.tags.append(tag1)
lecture1.tags.append(tag2)

# Add question and tags to session.
db.session.add(question1)
db.session.add(tag1)
db.session.add(tag2)
db.session.add(tag3)

# Define answer choices.
choice1Id = uuid.uuid4()
choice2Id = uuid.uuid4()
choice3Id = uuid.uuid4()
choice4Id = uuid.uuid4()

choice1 = Choice(choiceId=str(choice1Id), question=question1,
  choiceStr="European", choiceValid=0)
choice2 = Choice(choiceId=str(choice2Id), question=question1,
  choiceStr="African", choiceValid=0)
choice3 = Choice(choiceId=str(choice3Id), question=question1,
  choiceStr="AAAAARGGGHHHH", choiceValid=1)
choice4 = Choice(choiceId=str(choice4Id), question=question1,
  choiceStr="5 mph", choiceValid=1)

# Add answers to session.
db.session.add(choice1)
db.session.add(choice2)
db.session.add(choice3)
db.session.add(choice4)

# Add answers to possible answers set.
question1.choices.append(choice1)
question1.choices.append(choice2)
question1.choices.append(choice3)
question1.choices.append(choice4)

# Add one round of answers to the first question.
round1Id = uuid.uuid4()
round1 = Round(roundId=str(round1Id), question=question1, startTime=0,
  endTime=10)
question1.rounds.append(round1)

# Add round to session.
db.session.add(round1)

# Add user1's and user3's responses.
response1Id = uuid.uuid4()
response3Id = uuid.uuid4()

response1 = Response(responseId=str(response1Id), roundFor=round1,
  studentId=str(user1Id), choiceId=str(choice3Id))
response3 = Response(responseId=str(response3Id), roundFor=round1,
  studentId=str(user3Id), choiceId=str(choice4Id))
round1.responses.append(response1)
round1.responses.append(response3)

# Add responses to session.
db.session.add(response1)
db.session.add(response3)
db.session.commit()

print("Done.")
