from flask import Flask, render_template
import sqlite3
from prettytable import PrettyTable

app = Flask(__name__)

@app.route('/instructors')
def instructors_summary():

    DB_FILE = "/Users/alexbehrman/Documents/HW/SSW810-DataRepo/810_startup.db"
    query = "select i.CWID, i.NAME, i.DEPT, g.COURSE, count(g.COURSE) as ENROLLMENT from HW11_Instructors i join HW11_Grades g on i.CWID = g.INSTRUCTOR_CWID group by g.COURSE order by i.CWID"
    db = sqlite3.connect(DB_FILE)
    results = db.execute(query)

    data = [{'cwid': cwid, 'name': name, 'department': department, 'courses': courses, 'students': students}
            for cwid, name, department, courses, students in results]

    db.close()

    return render_template('instructor_table.html',
                            title='Stevens Repository',
                            table_title='Instructor Summary',
                            instructors=data)

app.run(debug=True)