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

#
# Equal Modulo Order
#
def equalModuloOrder(obj, template):
    if isinstance(template, list):
        if (not isinstance(obj, list) or len(obj) != len(template)):
            return False

        template.sort()
        obj.sort()
        return reduce(lambda acc, el:   acc and el, 
            map(lambda pair:  equalModuloOrder(pair[0], pair[1]),\
                zip(obj, template)), True)
    elif isinstance(template, dict):
        if (not isinstance(obj, dict)):
            return False 

        for k in template.keys():
            if not equalModuloOrder(obj[k], template[k]):
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
        if ('res' not in json):
            print 'Expected json return, instead got: ', json
            assert False
        if (not equalModuloOrder(json, { u'res' : obj })):
            print "Error: Mismatch between expected: \n", { u'res' : obj },\
                "\n and actual: \n", json

            assert False

    def post(self, url):
        rv = self.app.post(url)
        assert rv.status_code == 200
        return json.loads(rv.data)['res']

    def put(self, url):
        rv = self.app.put(url)
        assert rv.status_code == 200
        return json.loads(rv.data)['res']

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

    def assertFailPost(self, url, code, msg = None):
        rv = self.app.post(url)
        if (rv.status_code != code):
          print "Expected status code %d but instead got %d\n" % \
            (code, rv.status_code)
          assert(False)
        res = json.loads(rv.data)
        if (msg and res != { 'message': msg }):
          print "Expected error message \n", msg, "\n but got: \n", \
            res['message'], '\n'
          assert(False)

    def assertFailPut(self, url, code, msg = None):
        rv = self.app.put(url)
        if (rv.status_code != code):
          print "Expected status code %d but instead got %d\n" % \
            (code, rv.status_code)
          assert(False)

        if (msg):
          res = json.loads(rv.data)
          if (res != { 'message': msg }):
            print "Expected error message \n", msg, "\n but got: \n", \
              res['message'], '\n'
            assert(False)

    def assertFailGet(self, url, code, msg = None):
        rv = self.app.get(url)
        if (rv.status_code != code):
          print "Expected status code %d but instead got %d\n" % \
            (code, rv.status_code)
          assert(False)

        if (msg):
          res = json.loads(rv.data)
          if (res != { 'message': msg }):
            print "Expected error message \n", msg, "\n but got: \n", \
              res['message'], '\n'
            assert(False)

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
              u'instructorId': vals.course2.instructorId},
             {u'courseId': vals.course3.courseId, \
              u'courseTitle': vals.course3.courseTitle, \
              u'instructorId': vals.course3.instructorId}])

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

    def test_CourseStudentManifestApi(self):
        vals = dbPopulateDummyValues(db)
        self.assertJSON("/courses/" + vals.course1.courseId + "/students", [\
            { 'universityId': vals.course1.students[0].universityId,
              'userId': vals.course1.students[0].userId,
              'name': vals.course1.students[0].name,
            },
            { 'universityId': vals.course1.students[1].universityId,
              'userId': vals.course1.students[1].userId,
              'name': vals.course1.students[1].name,
            }])

        self.assertError("/courses/BADVAL/students", "Unknown course id BADVAL")

        self.assertError("/courses/" + vals.course1.courseId + \
            "/students?lectureId=BADVAL", \
            "Unknown lecture id BADVAL for course %s" % (vals.course1.courseId))

        self.assertJSON("/courses/" + vals.course2.courseId + \
            "/students?lectureId=" + vals.lecture1.lectureId, [\
            { 'universityId': vals.course2.students[1].universityId,
              'userId': vals.course2.students[1].userId,
              'name': vals.course2.students[1].name,
            },
            { 'universityId': vals.course2.students[0].universityId,
              'userId': vals.course2.students[0].userId,
              'name': vals.course2.students[0].name,
            }])

    def test_UserApi(self):
        vals = dbPopulateDummyValues(db)
        self.assertJSON("/users/" + vals.user1.userId,
            {
                'userId': vals.user1.userId,
                'universityId': vals.user1.universityId,
                'name': vals.user1.name,
            })

        self.assertError("/users/BADVAL", "Unknown user id BADVAL")

    def test_QuestionApi_get(self):
        vals = dbPopulateDummyValues(db)
        self.assertError("/courses/BADVAL/questions",\
            "Unknown course id BADVAL")

        def q(m):
            return { 'questionId': m.questionId, 'title': m.title, \
                'tags': list(map(lambda t: \
                    { 'tagId': t.tagId, 'tagText': t.tagText }, m.tags)), \
                'questionBody': m.questionBody, 'lectureId': m.lectureId }

        self.assertJSON("/courses/" + vals.course3.courseId + "/questions", \
            [q(vals.question2), q(vals.question3), q(vals.question4) ])

        self.assertJSON("/courses/" + vals.course3.courseId + \
            "/questions?lectureId=" + vals.lecture2.lectureId, \
            [q(vals.question2), q(vals.question3), q(vals.question4) ])

        self.assertJSON("/courses/" + vals.course3.courseId + \
            "/questions?lectureId=" + vals.lecture3.lectureId, \
            [])

        self.assertError("/courses/" + vals.course3.courseId + \
            "/questions?lectureId=BADVAL", \
            "Unknown lecture id BADVAL")

        self.assertError("/courses/" + vals.course3.courseId + \
            "/questions?lectureId=" + vals.lecture1.lectureId, \
            "Lecture %s belongs to different course" % vals.lecture1.lectureId)

        self.assertJSON("/courses/" + vals.course3.courseId + \
            "/questions?lectureId=" + vals.lecture2.lectureId + "&tag=BADTAG",\
            [])

        self.assertJSON("/courses/" + vals.course3.courseId + \
            "/questions?lectureId=" + vals.lecture2.lectureId + '&tag=wow',\
            [q(vals.question2), q(vals.question3) ])

        self.assertJSON("/courses/" + vals.course3.courseId + \
            "/questions?lectureId=" + vals.lecture2.lectureId + \
            '&tag=much_tag',
            [q(vals.question2) ])

        self.assertJSON("/courses/" + vals.course3.courseId + \
            "/questions?lectureId=" + vals.lecture2.lectureId + \
            '&tag=much_tag&tag=wow',
            [q(vals.question2) ])

        self.assertJSON("/courses/" + vals.course3.courseId + \
            "/questions?lectureId=" + vals.lecture2.lectureId + \
            '&tag=much_tag&tag=BADTAG',
            [])


    def test_QuestionApi_post(self):
        vals = dbPopulateDummyValues(db)

        # Missing Parameters
        self.assertFailPost('/courses/BADVAL/questions', 400)
        self.assertFailPost('/courses/BADVAL/questions?lectureId=A', 400)
        self.assertFailPost('/courses/BADVAL/questions?lectureId=A'+ 
            '&title=B', 400)
        self.assertFailPost('/courses/BADVAL/questions?lectureId=A'+ 
            '&title=B&body=C', 400)
        self.assertFailPost('/courses/BADVAL/questions?lectureId=A'+ 
            '&title=B&body=C&choices=D', 400)

        # Non-existing course
        self.assertFailPost('/courses/BADVAL/questions?lectureId=A'+
          '&title=B&body=C&choices=D&correct-choices=D', 400, \
          "Unknown course id BADVAL")

        # Invalid choices/correct choices
        self.assertFailPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=A'+
          '&title=B&body=C&choices=&correct-choices=D', 400, \
          "Invalid choices")

        self.assertFailPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=A'+
          '&title=B&body=C&choices=D&correct-choices=', 400, \
          "Invalid correct choices")

        self.assertFailPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=A'+
          '&title=B&body=C&choices=A&choices=B&correct-choices=D', 400, \
          "Correct choices not a subset of all choices")

        # Bad lecture Ids
        self.assertFailPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId='+
          '&title=B&body=C&choices=A&choices=B&correct-choices=B', 400, \
          "Unknown lecture id ")

        self.assertFailPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=BADVAL'+
          '&title=B&body=C&choices=A&choices=B&correct-choices=B', 400, \
          "Unknown lecture id BADVAL")

        self.assertFailPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture1.lectureId +
          '&title=B&body=C&choices=A&choices=B&correct-choices=B', 400, \
          "Lecture id %s is for a different course" % vals.lecture1.lectureId)

        q1 = self.post('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture3.lectureId +
          '&title=B&body=C&choices=A&choices=B&correct-choices=B')

        def q(m):
            return { 'questionId': m['questionId'], 'title': m['title'], \
                'questionBody': m['questionBody'], 'lectureId': m['lectureId']}

        self.assertJSON('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture3.lectureId, [ q(q1) ])

        q2 = self.post('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture3.lectureId + \
          '&title=B&body=C&choices=A&choices=B&correct-choices=B' + \
          '&tag=WOO&tag=HOO')

        self.assertJSON('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture3.lectureId, [ q(q1), q(q2) ])

        self.assertJSON('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture3.lectureId + \
          '&tag=WOO', [ q(q2) ])

        self.assertJSON('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture3.lectureId + \
          '&tag=HOO', [ q(q2) ])

        self.assertJSON('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture3.lectureId + \
          '&tag=HOO&tag=WOO', [ q(q2) ])

        self.assertJSON('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture3.lectureId + \
          '&tag=BOO', [ ])

    def test_EditQuestionApi(self):
        vals = dbPopulateDummyValues(db)
        def q(m):
            return { 'questionId': m['questionId'], 'title': m['title'], \
                'questionBody': m['questionBody'], 'lectureId': m['lectureId']}


        # Bad courseId or questionId
        self.assertFailPut('/courses/BADVAL/questions/BADID', 400, \
          'Unknown course BADVAL')
        self.assertFailPut('/courses/' + vals.course3.courseId + \
          '/questions/BADID', 400, "Unknown question id BADID")
        self.assertFailPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question1.questionId, \
          400, 'Question id %s corresponds to a different course' % \
          vals.question1.questionId)

        # Missing Arguments
        self.assertFailPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId, 400, '')

        self.assertFailPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo', 400, '')

        self.assertFailPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo&body=Bar', \
          400, '')

        self.assertFailPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo&body=Bar' + \
          '&choices=&correct-choices=', 400, 'Missing choices')

        self.assertFailPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo&body=Bar' + \
          '&choices=A', 400, '')

        self.assertFailPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo&body=Bar' + \
          '&choices=A&correct-choices=', 400, 'Missing correct choices')

        self.assertFailPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo&body=Bar' + \
          '&choices=A&correct-choices=D', 400, '')

        # Create a question
        q1 = self.put('/courses/' + vals.course2.courseId + \
          '/questions/' + vals.question1.questionId + '?title=Foo&body=Bar' + \
          '&choices=A&correct-choices=A')

        # TODO: What is the behavior of this api on puting:
        # 1) If a given field (e.g. tags) is not specified, does the old value
        # remain?
        # 2) When specifying tags, do they get appended? Or overried existing
        # tags?

        # Edit a previously existing question

    def test_ResponseRoundsApi(self):
        vals = dbPopulateDummyValues(db)

        # Bad courseId or questionId
        self.assertError('/courses/BADVAL/questions/BADID/responses', \
          'Unknown course id BADVAL')

        self.assertError('/courses/' + vals.course2.courseId + \
          '/questions/BADID/responses', 'Unknown question id BADID')

        self.assertError('/courses/' + vals.course2.courseId + \
          '/questions/' + vals.question4.questionId + '/responses', \
          'Question id %s is for a different course' % \
          vals.question4.questionId)

        # Question with no rounds
        self.assertJSON('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question4.questionId + '/responses', [])

        def r(resp):
          return {'roundId': resp.roundId, 'choiceId': resp.choiceId,\
                  'studentId': resp.studentId, 'responseId': resp.responseId}
        
        # All responses for a given question
        self.assertJSON('/courses/' + vals.course2.courseId + \
          '/questions/' + vals.question1.questionId + '/responses', \
          [ r(vals.response1), r(vals.response3) ])

        # All responses for a given question for a given student id
        self.assertJSON('/courses/' + vals.course2.courseId + \
          '/questions/' + vals.question1.questionId + '/responses?studentId=' +\
          vals.user1.userId, [ r(vals.response1) ])

        

if __name__ == '__main__':
    unittest.main()
