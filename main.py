from flask import Flask, render_template, request
import pickle
import os

# create the flask app
app = Flask(__name__)

# read the header and footer from the templates folder
header = open("templates/header.html").read()
footer = open("templates/footer.html").read()

# global variables
filename = ""
questions = []

# remove empty questions and replace newlines for json
def clean_questions():
    global questions
    for question in questions:
        question["question"] = question["question"].replace("\r\n", "\\n")
        question["answer"] = question["answer"].replace("\r\n", "\\n")
        if question["type"] == "flashcard" and question["question"] == "" and question["answer"] == "":
            questions.remove({"type": "flashcard", "question": "", "answer": ""})
        if question["type"] == "test" and question["question"] == "" and question["answer"] == "":
            questions.remove({"type": "test", "question": "", "answer": ""})

# index page
@app.route("/")
def index():
    return header + render_template("index.html") + footer

# edit page, where the user can create a new set or edit an existing one
@app.route("/edit")
def edit():
    return header + render_template("edit.html") + footer

# editor page for the user to edit the questions in a set
@app.route("/editor", methods=["POST"])
def editor():
    global questions
    global filename
    # if the user has selected a set, load the questions from the file
    if request.method == "POST":
        try:
            filename = request.form["file"]
            with open(filename, "rb") as f:
                questions = pickle.load(f)
        except:
            pass
    # clean the questions for json
    clean_questions()
    return header + render_template("editor.html", data=questions) + footer

# save the data from the editor page
@app.route("/save_data", methods=["POST"])
def save_data():
    if request.method == "POST":
        global questions
        questions = []
        # get the data from the form and save it to the questions list
        for name in request.form:
            data = request.form[name]
            while int(name[2:]) >= len(questions):
                questions.append({"type": "", "question": "", "answer": ""})
            if name[0] == "t":
                questions[int(name[2:])]["type"] = data
            if name[0] == "q":
                questions[int(name[2:])]["question"] = data
            if name[0] == "a":
                questions[int(name[2:])]["answer"] = data
        clean_questions()
        print(questions)
        # save the questions to the file
        with open(filename, "wb") as f:
            pickle.dump(questions, f)
    return edit()

# call openset with is_editor set to true
@app.route("/open_editor")
def open_editor():
    return openset(True)

# open a set of cards  
@app.route("/open")
def openset(is_editor):
    if is_editor:
        action = "/editor"
    else:
        action = "/practice"
    page = header
    files = os.listdir()
    questionsets = []
    for file in files:
        if file[-5:] == ".data":
            questionsets.append(file)
    page += f"<form method='post' action='{action}'>"
    for file in questionsets:
        page += "<p>"
        page += f"<input type='radio' class='form-check-input' name='file' id='{file}' value='{file}'>"
        page += f"<label class='form-check-label' for='{file}'>{file[:-5]}</label><br>"
        page += "</p>"
    page += "<button type='submit' class='btn btn-primary ml-0'>open</button>"
    return page + footer

# create a new set of cards
@app.route("/create")
def create():
    page = header
    page += "<form method='post' action='/create_file'>"
    page += "<input name='filename'><br>"
    page += "<button type='submit' class='btn btn-primary ml-0'>create</button>"
    return page + footer

# create a new local file for the set of cards
@app.route("/create_file", methods=["POST"])
def create_file():
    if request.method == "POST":
        global filename
        global questions
        filename = request.form["filename"] + ".data"
        questions = [{"type": "flashcard", "question": "", "answer": ""}]
    return editor()

# open the practice page with the selected set of cards
@app.route("/open_practice")
def open_practice():
    return openset(False)

# practice page, where the user can practice the selected set of cards
@app.route("/practice", methods=['GET', 'POST'])
def practice():
    if request.method == "POST":
        filename = request.form["file"]
    with open(filename, "rb") as f:
        questions = pickle.load(f)
    return header + render_template("practice.html", data=questions) + footer

if __name__ == "__main__":
    app.run(debug=True)