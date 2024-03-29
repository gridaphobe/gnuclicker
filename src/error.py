from flask.ext.restful import abort
from flask import jsonify

EBADCOURSEID = 0
EBADSTUDENTID = 1
EBADINSTRUCTORID = 2
EBADLECTUREID = 3
EBADUSERID = 4
ELECTUREMISMATCH = 5
EBADQUESTIONID = 6
EQUESTIONMISMATCH = 7
ENOACTIVEROUND = 8
EMISSINGARG = 9
EEMPTYARG = 10
ECORRECTNONSUBSET = 13
EBADCHOICEID = 14
ECHOICEMISMATCH = 15
EQUESTIONACTIVE = 16
EBADINT = 17
ENOACTIVEQUESTIONS = 18
ENOTENROLLED = 19

_ERRTEXT = {
  EBADCOURSEID: "Unknown course id %s",
  EBADSTUDENTID: "Unknown student id %s",
  EBADINSTRUCTORID: "Unknown instructor id %s",
  EBADLECTUREID: "Unknown lecture id %s",
  EBADUSERID: "Unknown user id %s",
  ELECTUREMISMATCH: "Lecture %s does not belong to class %s",
  EBADQUESTIONID: "Unknown question id %s",
  EQUESTIONMISMATCH: "Question %s does not belong to class %s",
  ENOACTIVEROUND: "No active round for question %s",
  EMISSINGARG: "Missing required parameter %s in json or the post body or the query string",
  EEMPTYARG:  "TODO",
  ECORRECTNONSUBSET: "Correct choices (%s) not a subst of all choices (%s)",
  EBADCHOICEID: "Unknown choice id %s",
  ECHOICEMISMATCH: "Choice id %s does not belong to question %s",
  EQUESTIONACTIVE: "There is already an active round for question %s",
  EBADINT: "invalid literal for int() with base 10: '%s'",
  ENOACTIVEQUESTIONS: "No active questions for class %s",
  ENOTENROLLED: "User not enrolled in course as student",
}

_ERRRETCODE = {
  EBADCOURSEID: 404,
  EBADSTUDENTID: 404,
  EBADINSTRUCTORID: 404,
  EBADLECTUREID: 404,
  EBADUSERID: 404,
  ELECTUREMISMATCH: 400,
  EBADQUESTIONID: 404,
  EQUESTIONMISMATCH : 400,
  ENOACTIVEROUND: 400,
  EMISSINGARG: 400,
  EEMPTYARG: 400,
  ECORRECTNONSUBSET: 400,
  EBADCHOICEID: 400,
  ECHOICEMISMATCH: 400,
  EQUESTIONACTIVE: 400,
  EBADINT: 400,
  ENOACTIVEQUESTIONS: 400,
  ENOTENROLLED: 400,
}

def errtext(err, *args):
  try:
    return _ERRTEXT[err] % args
  except TypeError, e:
    print _ERRTEXT[err], args
    return ""

def errretcode(err):  return _ERRRETCODE[err]
def errobj(err, *args):
  field = 'error' if (errretcode(err) == 200) else 'message'
  return { field : errtext(err, *args) }

def iserrobj(obj, err, *args):
  return obj == errobj(err, *args)

def error(err, *args):
  # if (errretcode(err) == 200):
  #   return jsonify({'error': errtext(err, *args)})
  # else:
  abort(errretcode(err), message = errtext(err, *args))

