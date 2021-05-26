from  flask import Flask , render_template, request, jsonify
from  flask_sqlalchemy import SQLAlchemy
from  flask_marshmallow import Marshmallow
from  flask_cors import CORS

import os
import re
import random

# init app
app = Flask(__name__)
CORS(app)


#init db
basedir = os.path.abspath(os.path.dirname(__file__))

print("os.environ.get('DATABASE_URL') ==> " + str(os.environ.get('DATABASE_URL')))
db_url = os.environ.get('DATABASE_URL')

if db_url != None and db_url.startswith("postgres://"):
     db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#init ma
ma = Marshmallow(app)

class Questions(db.Model):
    
    id = db.Column(db.Integer, db.Identity(start=38, cycle=True), primary_key=True)
    chapter = db.Column(db.Integer)
    topic = db.Column(db.String(30))
    question = db.Column(db.String(100),nullable=False)
    answer = db.Column(db.String(50),nullable=False)

    def __init__ (self, chapter, topic, question, answer):
        self.chapter = chapter
        self.topic = topic
        self.question = question
        self.answer = answer

# question schema
class QuestionSchema(ma.Schema):
    class Meta:
        fields = ('id','chapter','topic','question','answer')

question_schema = QuestionSchema()
questions_schema = QuestionSchema(many=True)

@app.route('/')
def index():
    return render_template('index.html')

# api: insert a new question
@app.route('/api-question',methods=['POST'])
def add_question():
    chapter = request.json['chapter']
    topic = request.json['topic']
    question = request.json['question']
    answer = request.json['answer']

    new_question = Questions(chapter,topic,question,answer)
    db.session.add(new_question)
    db.session.commit()

    return question_schema.jsonify(new_question)

# api: delete question
@app.route('/api-delete/<id>',methods=['DELETE'])
def delete_question(id):
    question_to_delete = Questions.query.get(id)
    db.session.delete(question_to_delete)
    db.session.commit()
    return 'element id = ' + id + ' deleted' 

@app.route('/add-questions')
def add_questions():
    all_questions = Questions.query.order_by(Questions.id.desc()).all()
    result = questions_schema.dump(all_questions)
    return render_template('add-questions.html',data=result)

@app.route('/get-questions',methods=['GET'])
def get_questions():
    all_questions = Questions.query.all()
    result = questions_schema.dump(all_questions)
    print(result)
    return jsonify(result)

@app.route('/test-exams',methods=['GET'])
def get_examtest():
    # get all available id on the table questions
    ids = db.engine.execute('select id from questions')
    idsList = [row[0] for row in ids]
    
    # get list of 10 random id
    i = 0
    questionsId = set()
    print(type(questionsId))
    while len(questionsId) < 10 :
        questionsId.add(random.choice(idsList))
            
    # query on the random list
    random_questions = Questions.query.filter(Questions.id.in_(questionsId))
    result = questions_schema.dump(random_questions)

   
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
