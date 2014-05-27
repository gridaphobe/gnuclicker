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
from error import *

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
    def _assertSuccess(self, rv):
        self._assertCode(rv, 200)
        ret = json.loads(rv.data)

        if ('res' not in ret):
            print 'Expected json return, instead got: ', ret
            assert False

        return ret['res']

    def _assertCode(self, rv, code):
        if (rv.status_code != code):
          print "Expected HTTP response %d instead got response %d: %s" % \
            (code, rv.status_code, rv.data)
        assert rv.status_code == code 

    def _assertCodeAndError(self, rv, code, msg = None):
        self._assertCode(rv, code)
        if (msg != None):
          res = json.loads(rv.data)
          if (code == 200):
            if ('error' not in res):
              print "Missing error field in return"
            if (res['error'] != msg):
              print "Wrong error message: expected ", msg, " got ", \
                res['error']
            assert res == { u'error' : msg }
          else:
            if ('message' not in res):
              print "Missing message field in return"
            if (res['message'] != msg):
              print "Wrong error message: expected ", msg, " got ", \
                res['message']
            assert res == { u'message' : msg }

    def _assertError(self, rv, err, *args):
        self._assertCode(rv, errretcode(err))
        ret = json.loads(rv.data)

        if (not iserrobj(ret, err, *args)):
          print "\nExpected error:", errobj(err, *args), "but got", ret
          assert False

# Raw getters
    def getJSON(self, url):
        return self._assertSuccess(self.app.get(url))

    def putJSON(self, url):
        return self._assertSuccess(self.app.put(url))

    def postJSON(self, url):
        return self._assertSuccess(self.app.post(url))

# Assert success
    def assertJSON(self, url, obj):
        json = self.getJSON(url)
        if (not equalModuloOrder(json, obj)):
            print "Error: Mismatch between expected: \n", obj,\
                "\n and actual: \n", json

            assert False

    def assertErrorGet(self, url, err, *args):
        self._assertError(self.app.get(url), err, *args)

    def assertErrorPut(self, url, err, *args):
        self._assertError(self.app.put(url), err, *args)

    def assertErrorPost(self, url, err, *args):
        self._assertError(self.app.post(url), err, *args)

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
        self.assertErrorGet("/courses?instructorId=" + "BADVAL", \
            EBADINSTRUCTORID, "BADVAL")

        # All Courses for a given student 
        self.assertJSON("/courses?studentId=" + vals.user2.userId, 
            [{u'courseId': vals.course1.courseId, \
              u'courseTitle': u'Defense Against The Dark Arts', \
              u'instructorId': vals.course1.instructorId}])

        self.assertJSON("/courses?studentId=" + vals.user4.userId, [])
        self.assertErrorGet("/courses?studentId=" + "BADVAL", \
            EBADSTUDENTID, "BADVAL")

    def test_LecturesListApi(self):
        vals = dbPopulateDummyValues(db)
        self.assertJSON("/courses/" + vals.course1.courseId + "/lectures", [])
        self.assertJSON("/courses/" + vals.course2.courseId + "/lectures", [\
            { "courseId" : vals.course2.courseId, \
              "date"     : jsonifyTime(vals.lecture1.date), \
              "lectureId": vals.lecture1.lectureId, \
              "lectureTitle" : vals.lecture1.lectureTitle
            }])
        self.assertErrorGet("/courses/BADVAL/lectures", EBADCOURSEID, "BADVAL")

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

        self.assertErrorGet("/courses/BADVAL/students", EBADCOURSEID, "BADVAL")

        self.assertErrorGet("/courses/" + vals.course1.courseId + \
            "/students?lectureId=BADVAL", EBADLECTUREID, "BADVAL")

        self.assertErrorGet("/courses/" + vals.course1.courseId + \
            "/students?lectureId=" + vals.lecture3.lectureId, ELECTUREMISMATCH,\
            vals.lecture3.lectureId, vals.course1.courseId)

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

        self.assertErrorGet("/users/BADVAL", EBADUSERID, "BADVAL")

    def test_QuestionApi_get(self):
        vals = dbPopulateDummyValues(db)
        self.assertErrorGet("/courses/BADVAL/questions", EBADCOURSEID, "BADVAL")

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

        self.assertErrorGet("/courses/" + vals.course3.courseId + \
            "/questions?lectureId=BADVAL", EBADLECTUREID, "BADVAL")

        self.assertErrorGet("/courses/" + vals.course3.courseId + \
            "/questions?lectureId=" + vals.lecture1.lectureId, \
            ELECTUREMISMATCH, vals.lecture1.lectureId, vals.course3.courseId)

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
        self.assertErrorPost('/courses/BADVAL/questions', EMISSINGARG, \
          'lectureId')
        self.assertErrorPost('/courses/BADVAL/questions?lectureId=A', \
          EMISSINGARG, 'title')
        self.assertErrorPost('/courses/BADVAL/questions?lectureId=A'+ 
            '&title=B', EMISSINGARG, 'body')
        self.assertErrorPost('/courses/BADVAL/questions?lectureId=A'+ 
            '&title=B&body=C', EMISSINGARG, 'choices')
        self.assertErrorPost('/courses/BADVAL/questions?lectureId=A'+ 
            '&title=B&body=C&choices=D', EMISSINGARG, 'correct-choices')

        # Non-existing course
        self.assertErrorPost('/courses/BADVAL/questions?lectureId=A'+
          '&title=B&body=C&choices=D&correct-choices=D', EBADCOURSEID, "BADVAL")

        # Invalid choices/correct choices
        self.assertErrorPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=A'+
          '&title=B&body=C&choices=&correct-choices=D', EMISSINGARG, 'choices')

        self.assertErrorPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=A'+
          '&title=B&body=C&choices=D&correct-choices=', EMISSINGARG, \
          'correct-choices')

        self.assertErrorPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=A'+
          '&title=B&body=C&choices=A&choices=B&correct-choices=D', \
          ECORRECTNONSUBSET, 'D', 'A,B')

        # Bad lecture Ids
        self.assertErrorPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId='+
          '&title=B&body=C&choices=A&choices=B&correct-choices=B', \
           EBADLECTUREID, '')

        self.assertErrorPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=BADVAL'+
          '&title=B&body=C&choices=A&choices=B&correct-choices=B', \
           EBADLECTUREID, 'BADVAL')

        self.assertErrorPost('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture1.lectureId +
          '&title=B&body=C&choices=A&choices=B&correct-choices=B', \
          ELECTUREMISMATCH, vals.lecture1.lectureId, vals.course3.courseId)

        q1 = self.postJSON('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture3.lectureId +
          '&title=B&body=C&choices=A&choices=B&correct-choices=B')

        def q(m):
            return { 'questionId': m['questionId'], 'title': m['title'], \
                'questionBody': m['questionBody'], 'lectureId': m['lectureId']}

        self.assertJSON('/courses/' + vals.course3.courseId + \
          '/questions?lectureId=' + vals.lecture3.lectureId, [ q(q1) ])

        q2 = self.postJSON('/courses/' + vals.course3.courseId + \
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
        self.assertErrorPut('/courses/BADVAL/questions/BADID', EBADCOURSEID,
          "BADVAL")
        self.assertErrorPut('/courses/' + vals.course3.courseId + \
          '/questions/BADID', EBADQUESTIONID, "BADID")
        self.assertErrorPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question1.questionId, EQUESTIONMISMATCH,
          vals.question1.questionId, vals.course3.courseId)

        # Missing Arguments
        self.assertErrorPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId, EMISSINGARG, 'title') 

        self.assertErrorPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo', \
          EMISSINGARG, 'body')

        self.assertErrorPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo&body=Bar', \
          EMISSINGARG, 'choices')

        self.assertErrorPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo&body=Bar' + \
          '&choices=&correct-choices=', EMISSINGARG, 'choices')

        self.assertErrorPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo&body=Bar' + \
          '&choices=A', EMISSINGARG, 'correct-choices')

        self.assertErrorPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo&body=Bar' + \
          '&choices=A&correct-choices=', EMISSINGARG, 'correct-choices')

        self.assertErrorPut('/courses/' + vals.course3.courseId + \
          '/questions/' + vals.question3.questionId + '?title=Foo&body=Bar' + \
          '&choices=A&correct-choices=D', ECORRECTNONSUBSET, 'D', 'A') 

        # Create a question
        q1 = self.putJSON('/courses/' + vals.course2.courseId + \
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
        self.assertErrorGet('/courses/BADVAL/questions/BADID/responses',
          EBADCOURSEID, 'BADVAL')

        self.assertErrorGet('/courses/' + vals.course2.courseId + \
          '/questions/BADID/responses', EBADQUESTIONID, 'BADID')

        self.assertErrorGet('/courses/' + vals.course2.courseId + \
          '/questions/' + vals.question4.questionId + '/responses', \
          EQUESTIONMISMATCH, vals.question4.questionId, vals.course2.courseId)

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

    def test_ResponseApi(self):
        vals = dbPopulateDummyValues(db)
        # Bad courseId or questionId
        self.assertErrorPost(\
          '/courses/BADVAL/question/BADID/respond?choiceId=', EBADCOURSEID,
          'BADVAL')

        self.assertErrorPost('/courses/' + vals.course2.courseId + \
          '/question/BADID/respond?choiceId=', EBADQUESTIONID, 'BADID')

        self.assertErrorPost('/courses/' + vals.course2.courseId + \
          '/question/' + vals.question4.questionId + '/respond?choiceId=', \
          EQUESTIONMISMATCH, vals.question4.questionId, vals.course2.courseId)

        # No choiceId
        self.assertErrorPost('/courses/' + vals.course2.courseId + \
          '/question/' + vals.question1.questionId + '/respond', EMISSINGARG,
          'choiceId')

        # Bad choiceId
        self.assertErrorPost('/courses/' + vals.course2.courseId + \
          '/question/' + vals.question1.questionId + '/respond?choiceId=', \
          EBADCHOICEID, '')

        self.assertErrorPost('/courses/' + vals.course2.courseId + \
          '/question/' + vals.question1.questionId + '/respond?choiceId=BOO',
          EBADCHOICEID, 'BOO')

        self.assertErrorPost('/courses/' + vals.course2.courseId + \
          '/question/' + vals.question1.questionId + '/respond?choiceId=' + \
          vals.choice5.choiceId, ECHOICEMISMATCH, vals.choice5.choiceId,
          vals.question1.questionId)

        # No active round
        """
        self.assertErrorPost('/courses/' + vals.course2.courseId + \
          '/question/' + vals.question1.questionId + '/respond?choiceId=' + \
           vals.choice1.choiceId, 
          'No active round for question %s' % \
          vals.question4.questionId)
        """

    def test_RoundStartApi(self):
        vals = dbPopulateDummyValues(db)

    def test_RoundEndApi(self):
        vals = dbPopulateDummyValues(db)

    def test_LecturesApi(self):
        vals = dbPopulateDummyValues(db)

    def test_LecturesDetailsApi(self):
        vals = dbPopulateDummyValues(db)
        

if __name__ == '__main__':
    unittest.main()
