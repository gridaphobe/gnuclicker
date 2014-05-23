#!/usr/bin/python

from __init__ import db
from Model import *
import uuid

'''
Create dummy objects to populate the database for testing.
'''
user1Id = uuid.uuid4()
user2Id = uuid.uuid4()
user3Id = uuid.uuid4()

user1 = User(userId=user1Id, universityId="A12345678", name="Joe Pesci")
user2 = User(userId=user2Id, universityId="B12345678", name="Joe Biden")
user3 = User(userId=user3Id, universityId="C12345678", name="Joe Stalin")

db.session.add(user1)
db.session.add(user2)
db.session.add(user3)

db.session.commit()

users = User.query.all()
for user in users:
  print(user)
