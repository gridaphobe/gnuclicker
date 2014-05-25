import os
import sys
import unittest
import tempfile
import json

from os.path import *

sys.path.insert(0, join(dirname(realpath(__file__)), pardir))

from config import basedir
from backend import app
from Model import db, User
from db_dummy_populate import * 
from json import dumps
from flask import jsonify

def jsonifyTime(t):     return t.strftime("%a, %d %b %Y %H:%M:%S GMT")

class MatchAny:     pass;
#
# Insure that the object obj matches the given template. Recursively
# check embedded lists and dictionaries.
#
# This function allows us to check that returned JSON matches the expectation,
# modulo differing UUIDs
#
def matches(obj, template):
    if (template == MatchAny):
        return True

    if (type(obj) != type(template)):
        return False

    if isinstance(template, list):
        if (len(obj) != len(template)):
            return False

        return reduce(lambda acc, el:   acc and el, 
            map(lambda pair:  matches(pair[0], pair[1]), zip(obj, template)),
            True)
    elif isinstance(template, dict):
        for k in template.keys():
            if (k not in obj or (not matches(obj[k], template[k]))):
                return False
        return True
    else:
        return template == obj 

class TestCase(unittest.TestCase):

    def getJSON(self, url):
        rv = self.app.get(url)
        assert rv.status_code == 200
        return json.loads(rv.data)

    def assertJSON(self, url, obj):
        json = self.getJSON(url)
        if (json != { u'res' : obj }):
            print "Error: Mismatch between expected: \n", { u'res' : obj },\
                "\n and actual: \n", json

            assert False

    def assertError(self, url, msg):
        json = self.getJSON(url)

        if ('res' in json):
            print "Expected error message: \n", msg, \
                "\n but instead got result: \n", res

        if ('error' not in json):
            print "Error is not set!"

        if (json['error'] != msg):
            print "Wrong error message expected: ", msg, " got: ", json['error']

        assert json == { u'error' : msg }

    def setUp(self):
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_CoursesListApi(self):
        # Empty courses list
        self.assertJSON("/courses", [])
        vals = dbPopulateDummyValues(db)

        # All Courses 
        self.assertJSON("/courses", 
            [{u'courseId': vals.course1.courseId, \
              u'courseTitle': u'Defense Against The Dark Arts', \
              u'instructorId': vals.course1.instructorId}, \
             {u'courseId': vals.course2.courseId, \
              u'courseTitle': u'CSE210', \
              u'instructorId': vals.course2.instructorId}])

        # All Courses for a given instructor
        self.assertJSON("/courses?instructorId=" + vals.course1.instructorId, 
            [{u'courseId': vals.course1.courseId, \
              u'courseTitle': u'Defense Against The Dark Arts', \
              u'instructorId': vals.course1.instructorId}])

        self.assertJSON("/courses?instructorId=" + vals.user3.userId, [])
        self.assertError("/courses?instructorId=" + "BADVAL", \
            "Unknown instructor id BADVAL")

        # All Courses for a given student 
        self.assertJSON("/courses?studentId=" + vals.user2.userId, 
            [{u'courseId': vals.course1.courseId, \
              u'courseTitle': u'Defense Against The Dark Arts', \
              u'instructorId': vals.course1.instructorId}])

        self.assertJSON("/courses?studentId=" + vals.user4.userId, [])
        self.assertError("/courses?studentId=" + "BADVAL", \
            "Unknown student id BADVAL")

    def test_LecturesListApi(self):
        vals = dbPopulateDummyValues(db)
        self.assertJSON("/courses/" + vals.course1.courseId + "/lectures", [])
        self.assertJSON("/courses/" + vals.course2.courseId + "/lectures", [\
            { "courseId" : vals.course2.courseId, \
              "date"     : jsonifyTime(vals.lecture1.date), \
              "lectureId": vals.lecture1.lectureId, \
              "lectureTitle" : vals.lecture1.lectureTitle
            }])
        self.assertError("/courses/BADVAL/lectures", "Unknown course id BADVAL")

if __name__ == '__main__':
    unittest.main()
