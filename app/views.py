# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Flask modules
from flask   import Flask, render_template, request, redirect, url_for, flash, session
from jinja2  import TemplateNotFound


# App modules
from app import app, db, cursor
# from app.models import Profiles

# Other inputs
from datetime import datetime

# App main route + generic routing
@app.route('/')
def index():
    if not session.get('student_id'):
        session["student_id"] = 'none'

    if session["student_id"] == 'none':
        return redirect(url_for('login'))

    else:
        return redirect(url_for('student_dashboard', sid=session["student_id"]))

    return render_template('peerevalform.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/userLogin', methods=["POST"])
def userLogin():

    email = request.form.get("email")
    pwd = request.form.get("password")

    sql = "select * from Student where Email=%s and Password=%s;"

    cursor.execute(sql, [email, pwd])
    result = cursor.fetchone()

    if result is None:
        return redirect(url_for('login'))
    else:
        session["student_id"] = result["Student_ID"]
        
        return redirect(url_for("student_dashboard", sid=session["student_id"]))


@app.route('/studentdashboard/<sid>')
def student_dashboard(sid):

    return render_template('studentdashboard.html', sid=sid)

@app.route('/eval')
def eval():
    return render_template('peerevalform.html')

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


