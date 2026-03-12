from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import os
app = Flask(__name__)
DB_NAME = 'students.db'
# ----- Initialize the database -----
def init_db():
    if not os.path.exists(DB_NAME):
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                grade INTEGER NOT NULL,
                section TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
init_db()
# ----- Helper functions -----
def get_all_students():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "grade": r[2], "section": r[3]} for r in rows]
def get_student_by_id(student_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id=?", (student_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "name": row[1], "grade": row[2], "section": row[3]}
    return None
def add_student(name, grade, section):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, grade, section) VALUES (?, ?, ?)", (name, grade, section))
    conn.commit()
    conn.close()
def update_student(student_id, name, grade, section):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE students SET name=?, grade=?, section=? WHERE id=?", (name, grade, section, student_id))
    conn.commit()
    conn.close()
def delete_student(student_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
    conn.commit()
    conn.close()
# ----- Routes -----
@app.route('/')
def home():
    return redirect(url_for('list_students'))
@app.route('/students')
def list_students():
    students = get_all_students()
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Student Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <h1 class="mb-4 text-center">Student Dashboard</h1>
            <div class="text-center mb-4">
                <a href="/add_student_form" class="btn btn-primary">Add New Student</a>
                <a href="/summary" class="btn btn-info text-white">View Summary</a>
            </div>
            <table class="table table-striped table-bordered bg-white shadow-sm">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Grade</th>
                        <th>Section</th>
                        <th>Remarks</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                {% for s in students %}
                    <tr>
                        <td>{{s.id}}</td>
                        <td>{{s.name}}</td>
                        <td>{{s.grade}}</td>
                        <td>{{s.section}}</td>
                        <td>
                            {% if s.grade >= 75 %}
                                <span class="badge bg-success">Pass</span>
                            {% else %}
                                <span class="badge bg-danger">Fail</span>
                            {% endif %}
                        </td>
                        <td>
                            <a href="/edit_student/{{s.id}}" class="btn btn-warning btn-sm">Edit</a>
                            <a href="/delete_student/{{s.id}}" class="btn btn-danger btn-sm">Delete</a>
                        </td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, students=students)
@app.route('/add_student_form')
def add_student_form():
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Add Student</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <h2 class="text-center mb-4">Add New Student</h2>
            <form action="/add_student" method="POST" class="bg-white p-4 shadow-sm rounded">
                <div class="mb-3">
                    <label class="form-label">Name:</label>
                    <input type="text" name="name" class="form-control" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Grade:</label>
                    <input type="number" name="grade" class="form-control" min="0" max="100" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Section:</label>
                    <input type="text" name="section" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-success">Add Student</button>
                <a href="/students" class="btn btn-secondary">Back to List</a>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)
@app.route('/add_student', methods=['POST'])
def add_student_route():
    name = request.form.get("name")
    grade = int(request.form.get("grade"))
    section = request.form.get("section")
    add_student(name, grade, section)
    return redirect(url_for('list_students'))
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student_route(id):
    student = get_student_by_id(id)
    if not student:
        return "Student not found", 404
    if request.method == 'POST':
        name = request.form.get("name")
        grade = int(request.form.get("grade"))
        section = request.form.get("section")
        update_student(id, name, grade, section)
        return redirect(url_for('list_students'))
 html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Edit Student</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <h2 class="text-center mb-4">Edit Student</h2>
            <form method="POST" class="bg-white p-4 shadow-sm rounded">
                <div class="mb-3">
                    <label class="form-label">Name:</label>
                    <input type="text" name="name" class="form-control" value="{{student.name}}" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Grade:</label>
                    <input type="number" name="grade" class="form-control" value="{{student.grade}}" min="0" max="100" required>
                </div>
                <div class="mb-3">
                    <label class="form-label">Section:</label>
                    <input type="text" name="section" class="form-control" value="{{student.section}}" required>
                </div>
                <button type="submit" class="btn btn-success">Update Student</button>
                <a href="/students" class="btn btn-secondary">Back to List</a>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html, student=student)
@app.route('/delete_student/<int:id>')
def delete_student_route(id):
    delete_student(id)
    return redirect(url_for('list_students'))
@app.route('/summary')
def summary():
    students = get_all_students()
    grades = [s['grade'] for s in students]
    names = [s['name'] for s in students]
    passed_count = len([g for g in grades if g >= 75])
    failed_count = len([g for g in grades if g < 75])
    avg = sum(grades) / len(grades) if grades else 0
html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Summary</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="bg-light">
        <div class="container mt-5 text-center">
            <h2>Performance Summary</h2>
            <ul class="list-group mt-4 w-50 mx-auto shadow-sm">
                <li class="list-group-item">Average Grade: {{avg:.2f}}</li>
                <li class="list-group-item">Passed: {{passed_count}}</li>
                <li class="list-group-item">Failed: {{failed_count}}</li>
            </ul>
            <canvas id="gradeChart" class="mt-4" width="400" height="200"></canvas>
            <a href="/students" class="btn btn-primary mt-4">Back to Dashboard</a>
        </div>
        <script>
            const ctx = document.getElementById('gradeChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: {{names | safe}},
                    datasets: [{
                        label: 'Grades',
                        data: {{grades | safe}},
                        backgroundColor: {{['green' if g >=75 else 'red' for g in grades] | safe}},
                        borderColor: 'black',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: { y: { beginAtZero: true, max: 100 } }
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(html, grades=grades, names=names,
                                  passed_count=passed_count, failed_count=failed_count, avg=avg)
if __name__ == '__main__':
    app.run(debug=True)
