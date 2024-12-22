from flask import Flask, render_template

app = Flask(__name__)

projects = [
    {"customer": "ABC Corp", "projectType": "Web Development"},
    {"customer": "XYZ Inc", "projectType": "Mobile Application"},
    {"customer": "DEF Ltd", "projectType": "Database Migration"}
]

@app.route("/")
def hello_world():
    return render_template('projectList.html',projects=projects)



@app.route("/htmx")
def hello_world():
    return render_template('projectList.html',projects=projects)
