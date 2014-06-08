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

    user1 = User(userId=str(user1Id), universityId="jpesci", \
        name="Joe Pesci")
    user2 = User(userId=str(user2Id), universityId="jbiden", \
        name="Joe Biden")
    user3 = User(userId=str(user3Id), universityId="jstalin", \
        name="Joe Stalin")
    user4 = User(userId=str(user4Id), universityId="jbox", \
        name="Joe Box")

    # Add users to db session.
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)

    # Add courses. user2 and user1 teach a class each.
    datdaId = uuid.uuid4()
    leadershipId = uuid.uuid4()
    cse101Id = uuid.uuid4()

    datda = Course(courseId=str(datdaId),
      courseTitle="Defense Against The Dark Arts", instructor=user1)
    leadership = Course(courseId=str(leadershipId), courseTitle="Fearless Leadership",
      instructor=user2)
    cse101 = Course(courseId=str(cse101Id), courseTitle="CSE 101",
      instructor=user4)

    # Add courses to db session.
    db.session.add(datda)
    db.session.add(leadership)
    db.session.add(cse101)

    # Note that user3 is a student in both classes. Note that user1 is a
    # student in user2's class and vice versa.
    user3.enrolledIn.append(datda)
    user3.enrolledIn.append(leadership)
    user1.enrolledIn.append(leadership)
    user2.enrolledIn.append(datda)

    user1.enrolledIn.append(cse101)

    # Add a lecture to user2's class.
    lecture1Id = uuid.uuid4()
    lecture2Id = uuid.uuid4()
    lecture3Id = uuid.uuid4()
    lecture1 = Lecture(lectureId=str(lecture1Id), course=leadership,
      lectureTitle="Unbridled Courage", date=datetime.datetime.utcnow())

    lecture2 = Lecture(lectureId=str(lecture2Id), course=cse101,
      lectureTitle="How to Choose a Beginner's Language", date=datetime.datetime.utcnow())
    lecture3 = Lecture(lectureId=str(lecture3Id), course=cse101,
      lectureTitle="The Importance of Choosing the Right Language", date=datetime.datetime.utcnow())

    for name in ['sam', 'dimo', 'marc', 'arjun', 'danny', 'ben', 'eric']:
      uid = uuid.uuid4()
      user = User(userId = str(uid), universityId=name, name=name)
      db.session.add(user)

      user.enrolledIn.append(cse101)

    # Add lecture to db session.
    db.session.add(lecture1)
    db.session.add(lecture2)
    db.session.add(lecture3)

    # Add question to that lecture.
    q1Id = uuid.uuid4()
    q2Id = uuid.uuid4()
    q3Id = uuid.uuid4()
    q4Id = uuid.uuid4()
    q5Id = uuid.uuid4()

    question1 = Question(questionId=str(q1Id), lecture=lecture1,
      title="Instructor Scenarios",
      questionBody="What can an instructor do with Gnu/Clicker?")
    question2 = Question(questionId=str(q2Id), lecture=lecture2,
      title="Arjun raises a good point",
      questionBody="Arjun raises a good point, what is the best language for teaching Intro to Programming?")
    question3 = Question(questionId=str(q3Id), lecture=lecture2,
      title="Dimo raises a good point",
      questionBody="Dimo raises a good point, what is the best language for teaching Intro to Programming?")
    question4 = Question(questionId=str(q4Id), lecture=lecture2,
      title="Eric raises a good point",
      questionBody="Eric raises a good point, what is the best language for teaching Intro to Programming?")
    question5 = Question(questionId=str(q5Id), lecture=lecture2,
      title="Sam raises a good point",
      questionBody="Sam raises a good point, what is the best language for teaching Intro to Programming?")
    question6 = Question(questionId=str(uuid.uuid4()), lecture=lecture1,
      title="Student Scenarios",
      questionBody="What can a student do with Gnu/Clicker?")

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

    question2.tags.append(tag1)
    question2.tags.append(tag2)
    question3.tags.append(tag2)
    question4.tags = [];

    lecture1.tags.append(tag1)
    lecture1.tags.append(tag2)

    # Add question and tags to session.
    db.session.add(question1)
    db.session.add(question2)
    db.session.add(question3)
    db.session.add(question4)
    db.session.add(question5)
    db.session.add(question6)
    db.session.add(tag1)
    db.session.add(tag2)
    db.session.add(tag3)

    # Define answer choices.
    choice1Id = uuid.uuid4()
    choice2Id = uuid.uuid4()
    choice3Id = uuid.uuid4()
    choice4Id = uuid.uuid4()
    choice5Id = uuid.uuid4()
    choice6Id = uuid.uuid4()

    choice1 = Choice(choiceId=str(choice1Id), question=question1,
      choiceStr="Create a list of questions for a lecture", choiceValid=1, choiceIdx=0)
    choice2 = Choice(choiceId=str(choice2Id), question=question1,
      choiceStr="Post questions to students", choiceValid=1, choiceIdx=1)
    choice3 = Choice(choiceId=str(choice3Id), question=question1,
      choiceStr="Review student responses", choiceValid=1, choiceIdx=2)

    # Add answers to session.
    db.session.add(choice1)
    db.session.add(choice2)
    db.session.add(choice3)

    # Add answers to possible answers set.
    question1.choices.append(choice1)
    question1.choices.append(choice2)
    question1.choices.append(choice3)

    choice1 = Choice(choiceId=str(uuid.uuid4()), question=question6,
      choiceStr="(Re-)Submit a response", choiceValid=1, choiceIdx=0)
    choice2 = Choice(choiceId=str(uuid.uuid4()), question=question6,
      choiceStr="Review questions and responses", choiceValid=1, choiceIdx=1)

    # Add answers to session.
    db.session.add(choice1)
    db.session.add(choice2)

    # Add answers to possible answers set.
    question6.choices.append(choice1)
    question6.choices.append(choice2)

    for question in [question2, question3, question4, question5]:
      for idx, lang in enumerate(['Java', 'Python', 'C', 'Coq', 'Circuits']):
        choice = Choice(choiceId=str(uuid.uuid4()),
                        question=question,
                        choiceStr=lang,
                        choiceValid = 1 if (idx == 3 or idx == 4) else 0,
                        choiceIdx = idx)
        db.session.add(choice)
        question.choices.append(choice)


    # # Add one round of answers to the first question.
    # round1Id = uuid.uuid4()
    # round2Id = uuid.uuid4()

    # round1 = Round(roundId=str(round1Id), question=question1, startTime=0,
    #   endTime=10)
    # question1.rounds.append(round1)

    # round2 = Round(roundId=str(round2Id), question=question5, startTime=0,
    #   endTime=10)
    # question5.rounds.append(round2)
    # question5.activeRound = round2.roundId
    # question5.tags = []

    # # Add round to session.
    # db.session.add(round1)
    # db.session.add(round2)

    # # Add user1's and user3's responses.
    # response1Id = uuid.uuid4()
    # response3Id = uuid.uuid4()

    # response1 = Response(responseId=str(response1Id), roundFor=round1,
    #   studentId=str(user1Id), choiceId=str(choice3Id))
    # response3 = Response(responseId=str(response3Id), roundFor=round1,
    #   studentId=str(user3Id), choiceId=str(choice4Id))
    # round1.responses.append(response1)
    # round1.responses.append(response3)

    # # Add responses to session.
    # db.session.add(response1)
    # db.session.add(response3)

    db.session.commit()

    class Result:   pass
    res = Result()

    res.__dict__["user1"] = user1
    res.__dict__["user2"] = user2
    res.__dict__["user3"] = user3
    res.__dict__["user4"] = user4
    res.__dict__["course1"] = datda
    res.__dict__["course2"] = leadership
    res.__dict__["course3"] = cse101
    res.__dict__["lecture1"] = lecture1
    res.__dict__["lecture2"] = lecture2
    res.__dict__["lecture3"] = lecture3
    res.__dict__["question1"] = question1
    res.__dict__["question2"] = question2
    res.__dict__["question3"] = question3
    res.__dict__["question4"] = question4
    res.__dict__["question5"] = question5
    res.__dict__["choice1"] = choice1
    res.__dict__["choice2"] = choice2
    res.__dict__["choice3"] = choice3
    # res.__dict__["choice4"] = choice4
    # res.__dict__["choice5"] = choice5
    # res.__dict__["round1"] = round1
    # res.__dict__["round2"] = round2
    # res.__dict__["response1"] = response1
    # res.__dict__["response3"] = response3

    return res

if __name__ == '__main__':
    dbPopulateDummyValues(db)
    print("Done.")
