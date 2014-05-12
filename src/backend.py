from flask import Flask, jsonify, make_response
import uuid

app = Flask(__name__)

questions = [
    {
        'id': u'7d108fd4-9ac3-4a8e-9960-cb271f0de56b',
        'lid': u'9dd18dcf-5479-47d4-bb79-d3aaf0ebd03f',
        'title': u'Queue insertion',
        'body': u'Where does the element get inserted into the queue?',
        'choices': ['The front', 'The end', 'The middle', 'type error', 'invalid operation'],
        'correctSet': ['The end'],
        'rounds': []
    },
    {
        'id': u'4a0bd7a6-0534-424b-ac3f-6bc53e306ce6',
        'lid': u'61231c5a-6803-4f1a-a49f-ba74d0d86457',
        'title': u'Stacks vs Queues',
        'body': u'What is the difference between a stack and a queue',
        'choices': ['FIFO vs LIFO',
                    'Stacks are trees',
                    'Queues are heaps',
                    'Stacks are randomized but queues are deterministic',
                    'They are the same'],
        'correctSet': ['FIFO vs LIFO'],
        'rounds': []
    }
]

@app.route('/classes/<string:class_id>/questions', methods = ['GET'])
def get_questions(class_id):
    # we should use class_id, but I'm not bothering for the quick in memory
    # version 
    # currently always returns all questions
    
    print class_id

    return jsonify({'questions': questions})

@app.route('/classes/<string:class_id>/questions/<string:question_id>', methods = ['GET'])
def get_question(class_id, question_id):
    # we should use class_id, but I'm not bothering for the quick in memory
    # version 
    
    question = filter(lambda t: t['id'] == question_id, questions)

    if len(question) == 0:
        abort(404)

    return jsonify({'questions': question[0]})\

# TODO handle PUT, POST, DELETE for questions

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify( {'error' : 'Not found' } ), 404)

if __name__ == '__main__':
    app.run()
