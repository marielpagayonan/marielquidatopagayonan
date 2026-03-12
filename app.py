from flask import Flask, render_template_string, request
app = Flask(__name__)
@app.route('/')
def home():
    return '<h2>Welcome to my Flask API! Go to /student?grade=90</h2>'
@app.route('/student')
def student():
    # Get grade from query parameter (default 90)
    grade = int(request.args.get('grade', 90))
    name = "Charlie Tadlas Goro Jr"
    section = "Zechariah"
    remarks = "Pass" if grade >= 75 else "Fail"
    # Enhanced HTML output
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Student Info</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; }}
            .card {{ max-width: 500px; margin: 50px auto; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
            .badge-pass {{ background-color: #28a745; }}
            .badge-fail {{ background-color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="card text-center">
            <h3 class="mb-3">Student Information</h3>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Section:</strong> {section}</p>
            <p><strong>Grade:</strong> {grade}</p>
            <p><strong>Remarks:</strong> 
                <span class="badge {'badge-pass' if remarks=='Pass' else 'badge-fail'}">{remarks}</span>
            </p>
        </div>
    </body>
    </html>
    """
    return html
if __name__ == '__main__':
    app.run(debug=True)
