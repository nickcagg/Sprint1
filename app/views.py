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

import csv

# App main route + generic routing
@app.route('/')
def index():
    if not session.get('student_id'):
        session["student_id"] = 'none'
        session["isLoggedIn"] = False

    if session["student_id"] == 'none':
        return redirect(url_for('login'))

    else:
        return redirect(url_for('student_dashboard', sid=session["student_id"])) if session['isProfessor'] == False else redirect(url_for('professorHome', pid=session["student_id"]))

    return render_template('peerevalform.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/professorDashboard/<pid>')
def professorHome(pid):
    sql = "SELECT COUNT(DISTINCT Student.Student_ID) AS Count_Students_Enrolled, (SELECT COUNT(Course_ID) FROM Course WHERE Professor_ID = %s) AS Count_Courses_Taught FROM Student JOIN Student_Course ON Student.Student_ID = Student_Course.Student_ID JOIN Course ON Student_Course.Course_ID = Course.Course_ID WHERE Course.Professor_ID = %s;"
    cursor.execute(sql, [pid, pid])

    result = cursor.fetchone()

    sql = "SELECT Course.Course_ID, Course.CourseCode, Course.CourseName, COUNT(`Groups`.Group_ID) AS 'GroupCount' FROM Course LEFT JOIN `Groups` ON `Groups`.Course_ID = Course.Course_ID WHERE Course.Professor_ID = %s GROUP BY Course.Course_ID, Course.CourseCode, Course.CourseName;"
    cursor.execute(sql, [pid])

    courses=cursor.fetchall()

    
    return render_template('profdashboard.html', activeCourses=result['Count_Students_Enrolled'], totalStudents=result['Count_Courses_Taught'], courses=courses)



def checkProfessorRegister(email, pwd):

    sql = "select * from Professor where Email=%s and Password=%s;"
    cursor.execute(sql, [email, pwd])
    result = cursor.fetchone()

    if result is None:
        return False
    
    else:
        setUserInfo(result['Professor_ID'], result['FirstName'], result['LastName'], email, isProf=True)
        return result['Professor_ID']

@app.route('/userLogin', methods=["POST"])
def userLogin():

    email = request.form.get("email")
    pwd = request.form.get("password")

    sql = "select * from Student where Email=%s and Password=%s;"

    cursor.execute(sql, [email, pwd])
    result = cursor.fetchone()

    if result is None:
        isProfessor = checkProfessorRegister(email, pwd)


        return redirect(url_for('login')) if not isProfessor else redirect(url_for('professorHome', pid=isProfessor))
    else:
        setUserInfo(result["Student_ID"], result["FirstName"], result["LastName"], result["Email"], isProf=False)
        
        return redirect(url_for("student_dashboard", sid=session["student_id"]))

@app.route('/studentdashboard/<sid>')
def student_dashboard(sid):

    if not session.get('student_id') or session["student_id"] == 'none':
        return redirect(url_for('login'))
    
    else:

        sql = "SELECT c.CourseName, g.GroupName, pe.*, DATEDIFF(pe.Due_Date, CURDATE()) AS Days_Until_Due FROM Peer_Evaluation pe JOIN `Groups` g ON pe.Group_ID = g.Group_ID JOIN Course c ON g.Course_ID = c.Course_ID JOIN Student_Groups sg ON g.Group_ID = sg.Group_ID WHERE sg.Student_ID = %s;"

        cursor.execute(sql, [session["student_id"]])

        evalInfo = cursor.fetchall()    
        evalList = []

        #                                                                                   LOOK AT THIS STUFF ??????????????????????////

        for eval in evalInfo:
            eid = eval["Evaluation_ID"]
            sql = "select * from Evaluation_Result where Evaluation_ID=%s and Evaluator_ID=%s;"
            cursor.execute(sql, [eid, sid])   
            results = cursor.fetchall()
            if results is None:
                pass
            else:
                evalList.append(eval)


        return render_template('studentdashboard.html', sid=sid, evalLinks=evalList)

@app.route('/eval/<eid>/<gid>')
def eval(eid, gid):
    if not session.get('student_id') or session["student_id"] == 'none':
        return redirect(url_for('login'))
    
    else:
        sql = "SELECT s.Student_ID, s.FirstName, s.LastName, sg.Group_ID FROM Student s JOIN Student_Groups sg ON s.Student_ID = sg.Student_ID WHERE sg.Group_ID = %s AND s.Student_ID <> %s;"
        cursor.execute(sql, [gid, session["student_id"]])
        peeps = cursor.fetchall()

        return render_template('peerevalform.html', peeps=peeps, eid=eid)

@app.route('/submitPeerEvaluation/<eid>', methods=['POST'])
def submitEval(eid):
    # get the form results
    evaluated = int(request.form.get('evaluated'))
    evaluator = session["student_id"]
    date = datetime.now()
    intel_creativity = int(request.form.get('intelCreative'))
    interpersonal = int(request.form.get('interpersonal'))
    disciplinary = int(request.form.get('disciplinary'))
    citizenship = int(request.form.get('citizenship'))
    mastery = int(request.form.get('mastery'))
    comments = request.form.get('comments')

    # database connection setup
    # insert data into Evaluation_Result
    
    GLOs = [intel_creativity, interpersonal, disciplinary, citizenship, mastery]
    i = 0

    for score in GLOs:
        i += 1
        
        sql = '''
            INSERT INTO Evaluation_Result (Evaluation_ID, Evaluator_ID, Evaluated_ID, GLO_ID, Score, Date_Time, Course_ID) 
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        '''
        try:
            cursor.execute(sql, [eid, evaluator, evaluated, i, score, date, 1])
            db.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
            db.rollback()        

    return redirect(url_for('student_dashboard', sid=session["student_id"]))


@app.route('/readcsv')
def studentsimporting():

    return "dick"

# @app.route('/addstudents')


@app.route('/loggingout')
def logout():
    session["student_id"] = None
    session["fname"] = None
    session["lname"] = None
    session['email'] = None
    session['isLoggedIn'] = False

    return redirect(url_for('login'))


def setUserInfo(id, fname, lname, email, isProf):
    session["student_id"] = id
    session["fname"] = fname
    session["lname"] = lname
    session['email'] = email
    session['isLoggedIn'] = True
    session['isProfessor'] = isProf

def stopDatabase():
    cursor.close()
    db.close()