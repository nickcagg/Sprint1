# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask   import Flask, render_template, request, redirect, url_for, flash
from jinja2  import TemplateNotFound
import pymysql

# App modules
from app import app
# from app.models import Profiles

# Other inputs
from datetime import datetime

# App main route + generic routing
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/submitPeerEvaluation', methods=['POST'])
def submitEval():
    # get the form results
    evaluated = int(request.form.get('evaluated'))
    evaluator = int(request.form.get('evaluator'))
    date = datetime.now()
    time_management = int(request.form.get('timeManagement'))
    leadership = int(request.form.get('leadership'))
    communication = int(request.form.get('communication'))
    work_ethic = int(request.form.get('workEthic'))
    score = int(request.form.get('score'))
    comments = request.form.get('comments')

    # database connection setup
    db = pymysql.connect(
        host='35.245.249.29',
        port=3306,
        user='admin',
        password='SMUGroup3',
        charset="utf8mb4",
        database='PeerEvaluationDB',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = db.cursor()

    # insert data into Evaluation_Result
    sql = '''
        INSERT into Evaluation_Result (Evaluator_Student_ID, Evaluated_Student_ID, GLO_ID, Score, Date_Time, Evaluation_ID)
        VALUES (%s, %s, %s, %s, %s, %s)
    '''
    try:
        cursor.execute(sql, [evaluator, evaluated, 1, score, date, 1])
        db.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()

    cursor.close()
    db.close()

    return "Evaluation Submitted"


