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
    <html>
    <head>
        <title>Student Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container mt-5">
            <h1 class="text-center mb-4">Student Dashboard</h1>
            <div class="text-center mb-3">
                <a href="{{ url_for('add_student_form') }}" class="btn btn-primary">Add Student</a>
                <a href="{{ url_for('summary') }}" class="btn btn-info text-white">Summary</a>
            </div>

            <table class="table table-bordered bg-white shadow">
                <thead class="table-dark">
                    <tr>
                        <th>ID</th><th>Name</th><th>Grade</th><th>Section</th><th>Remarks</th><th>Actions</th>
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
                            <a href="{{ url_for('edit_student_route', id=s.id) }}" class="btn btn-warning btn-sm">Edit</a>
                            <a href="{{ url_for('delete_student_route', id=s.id) }}" class="btn btn-danger btn-sm">Delete</a>
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
    <html>
    <body class="bg-light">
        <div class="container mt-5">
            <h2>Add Student</h2>
            <form action="{{ url_for('add_student_route') }}" method="POST">
                <input name="name" class="form-control mb-2" placeholder="Name" required>
                <input name="grade" type="number" class="form-control mb-2" required>
                <input name="section" class="form-control mb-2" placeholder="Section" required>
                <button class="btn btn-success">Add</button>
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

    if request.method == 'POST':
        update_student(
            id,
            request.form.get("name"),
            int(request.form.get("grade")),
            request.form.get("section")
        )
        return redirect(url_for('list_students'))

    html = """
    <html>
    <body class="bg-light">
        <div class="container mt-5">
            <h2>Edit Student</h2>
            <form method="POST">
                <input name="name" value="{{student.name}}" class="form-control mb-2">
                <input name="grade" value="{{student.grade}}" class="form-control mb-2">
                <input name="section" value="{{student.section}}" class="form-control mb-2">
                <button class="btn btn-success">Update</button>
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

    colors = ["green" if g >= 75 else "red" for g in grades]

    passed_count = len([g for g in grades if g >= 75])
    failed_count = len([g for g in grades if g < 75])
    avg = sum(grades) / len(grades) if grades else 0

    html = """
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    </head>
    <body class="text-center mt-5">
        <h2>Summary</h2>
        <p>Average: {{avg}}</p>
        <p>Passed: {{passed}}</p>
        <p>Failed: {{failed}}</p>

        <canvas id="chart"></canvas>

        <script>
        new Chart(document.getElementById('chart'), {
            type: 'bar',
            data: {
                labels: {{names|safe}},
                datasets: [{
                    data: {{grades|safe}},
                    backgroundColor: {{colors|safe}}
                }]
            }
        });
        </script>
    </body>
    </html>
    """
    return render_template_string(html, names=names, grades=grades,
                                  colors=colors, avg=avg,
                                  passed=passed_count, failed=failed_count)

if __name__ == '__main__':
    app.run(debug=True)
