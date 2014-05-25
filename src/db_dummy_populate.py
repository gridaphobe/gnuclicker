#!/usr/bin/env python

from __init__ import db
from Model import *
import uuid
import datetime

'''
Create dummy objects to populate the database for testing.
'''
def dbPopulateDummyValues(db):
    # Dummy users.
    user1Id = uuid.uuid4()
    user2Id = uuid.uuid4()
    user3Id = uuid.uuid4()
    user4Id = uuid.uuid4()

    user1 = User(userId=str(user1Id), universityId="A12345678", \
        name="Joe Pesci")
    user2 = User(userId=str(user2Id), universityId="B12345678", \
        name="Joe Biden")
    user3 = User(userId=str(user3Id), universityId="C12345678", \
        name="Joe Stalin")
    user4 = User(userId=str(user4Id), universityId="C12345679", \
        name="Joe Box")

    # Add users to db session.
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)

    # Add courses. user2 and user1 teach a class each.
    course1Id = uuid.uuid4()
    course2Id = uuid.uuid4()
    course1 = Course(courseId=str(course1Id), \
      courseTitle="Defense Against The Dark Arts", instructor=user1)
    course2 = Course(courseId=str(course2Id), courseTitle="CSE210",\
      instructor=user2)

    # Add courses to db session.
    db.session.add(course1)
    db.session.add(course2)

    # Note that user3 is a student in both classes. Note that user1 is a
    # student in user2's class and vice versa.
    user3.enrolledIn.append(course1)
    user3.enrolledIn.append(course2)
    user1.enrolledIn.append(course2)
    user2.enrolledIn.append(course1)

    # Add a lecture to user2's class.
    lecture1Id = uuid.uuid4()
    lecture1 = Lecture(lectureId=str(lecture1Id), course=course2,
      lectureTitle="Administrivia", date=datetime.datetime.utcnow())

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

    class Result:   pass
    res = Result()

    res.__dict__["user1"] = user1
    res.__dict__["user2"] = user2
    res.__dict__["user3"] = user3
    res.__dict__["user4"] = user4
    res.__dict__["course1"] = course1
    res.__dict__["course2"] = course2
    res.__dict__["lecture1"] = lecture1
    res.__dict__["question1"] = question1
    res.__dict__["choice1"] = choice1
    res.__dict__["choice2"] = choice2
    res.__dict__["choice3"] = choice3
    res.__dict__["choice4"] = choice4
    res.__dict__["round1"] = round1
    res.__dict__["response1"] = response1
    res.__dict__["response3"] = response3

    # Add responses to session.
    db.session.add(response1)
    db.session.add(response3)
    db.session.commit()

    return res 

if __name__ == '__main__':
    dbPopulateDummyValues(db)
    print("Done.")
