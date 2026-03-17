from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret123"

DB_NAME = 'students.db'

# ----- Initialize DB -----
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade INTEGER NOT NULL,
            section TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # default login
    cursor.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', '1234')")

    conn.commit()
    conn.close()

init_db()

# ----- DB FUNCTIONS -----
def get_all_students(search=None):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    if search:
        cursor.execute("SELECT * FROM students WHERE name LIKE ?", ('%' + search + '%',))
    else:
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

# ----- LOGIN -----
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('list_students'))
        else:
            return "Invalid credentials"

    html = """
    <html>
    <body class="bg-light text-center mt-5">
        <h2>Login</h2>
        <form method="POST">
            <input name="username" placeholder="Username" class="form-control w-25 mx-auto mb-2">
            <input name="password" type="password" placeholder="Password" class="form-control w-25 mx-auto mb-2">
            <button class="btn btn-primary">Login</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

# ----- STUDENTS -----
@app.route('/students')
def list_students():
    if 'user' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search')
    students = get_all_students(search)

    html = """
    <html>
    <head>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">

    <div class="container mt-5">
        <h1 class="text-center">Student Dashboard</h1>

        <div class="text-center mb-3">
            <a href="/add_student_form" class="btn btn-primary">Add Student</a>
            <a href="/summary" class="btn btn-info text-white">Summary</a>
            <a href="/logout" class="btn btn-danger">Logout</a>
        </div>

        <form method="GET" class="mb-3 text-center">
            <input type="text" name="search" placeholder="Search student..." class="form-control w-25 d-inline">
            <button class="btn btn-primary">Search</button>
            <a href="/students" class="btn btn-secondary">Reset</a>
        </form>

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

# ----- ADD -----
@app.route('/add_student_form')
def add_student_form():
    if 'user' not in session:
        return redirect(url_for('login'))

    html = """
    <html>
    <body class="bg-light">
        <div class="container mt-5">
            <h2>Add Student</h2>
            <form method="POST" action="/add_student">
                <input name="name" class="form-control mb-2" placeholder="Name">
                <input name="grade" type="number" class="form-control mb-2">
                <input name="section" class="form-control mb-2" placeholder="Section">
                <button class="btn btn-success">Add</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/add_student', methods=['POST'])
def add_student_route():
    add_student(
        request.form.get("name"),
        int(request.form.get("grade")),
        request.form.get("section")
    )
    return redirect(url_for('list_students'))

# ----- EDIT -----
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student_route(id):
    if 'user' not in session:
        return redirect(url_for('login'))

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

# ----- DELETE -----
@app.route('/delete_student/<int:id>')
def delete_student_route(id):
    delete_student(id)
    return redirect(url_for('list_students'))

# ----- SUMMARY -----
@app.route('/summary')
def summary():
    if 'user' not in session:
        return redirect(url_for('login'))

    students = get_all_students()
    grades = [s['grade'] for s in students]
    names = [s['name'] for s in students]
    colors = ["green" if g >= 75 else "red" for g in grades]

    passed = len([g for g in grades if g >= 75])
    failed = len([g for g in grades if g < 75])
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

        <a href="/students" class="btn btn-primary mt-3">Back</a>
    </body>
    </html>
    """
    return render_template_string(html, names=names, grades=grades,
                                  colors=colors, avg=avg,
                                  passed=passed, failed=failed)

if __name__ == '__main__':
    app.run(debug=True)
