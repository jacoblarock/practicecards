from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pickle
import os

# create the flask app
app = Flask(__name__)

# read the header and footer from the templates folder
header = open("templates/header.html").read()
footer = open("templates/footer.html").read()

# global variables
setname = ""
questions = []
user_id = 0

# create the database connection
dbfile = "./practicecards.db"
def create_cursor(dbfile):
    con = sqlite3.connect(dbfile)
    return con.cursor()
    

# replace newlines for json
def clean_questions(questions):
    for i in range(len(questions)):
        questions[i]["question"] = questions[i]["question"].replace("\r\n", "\\n")
        questions[i]["answer"]["flashcard"] = questions[i]["answer"]["flashcard"].replace("\r\n", "\\n")
        questions[i]["question"] = questions[i]["question"].replace("\"", "'")
        questions[i]["answer"]["flashcard"] = questions[i]["answer"]["flashcard"].replace("\"", "\\\"")

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
    global setname
    cur = create_cursor(dbfile)
    # if the user has selected a set, load the questions from the file
    if request.method == "POST":
        # try case create
        try:
            setname = request.form["filename"]
            questions = [{"type": "flashcard", "question": "", "answer": {"flashcard": "", "test": []}}]
        except:
            # try case open
            try:
                set_id = request.form["id"]
                set_rows = cur.execute("SELECT d_questions FROM decks WHERE d_id=" + str(set_id))
                set_data = set_rows.fetchone()
                # questions = pickle.load(f)
            except:
                pass
    # clean the questions for json
    clean_questions(questions)
    return header + render_template("editor.html", data=questions) + footer

# save the data from the editor page
@app.route("/save_data", methods=["POST"])
def save_data():
    if request.method == "POST":
        global questions
        global setname
        questions = []
        # get the data from the form and save it to the questions list
        for name in request.form:
            data = request.form[name]
            name = name.split("-")
            while int(name[1]) >= len(questions):
                questions.append({"type": "", "question": "", "answer": {"flashcard": "", "test": []}})
            if name[0] == "t":
                questions[int(name[1])]["type"] = data
            if name[0] == "q":
                questions[int(name[1])]["question"] = data
            if name[0] == "a":
                questions[int(name[1])]["answer"]["flashcard"] = data
            if name[0] == "at":
                questions[int(name[1])]["answer"]["test"].append(data)
        # save the questions to the file
        with open(setname, "wb") as f:
            pickle.dump(questions, f)
    return render_template("save_data.html")

# call openset with is_editor set to true
@app.route("/open_editor")
def open_editor():
    return openset(True)

# open a set of cards  
@app.route("/open")
def openset(is_editor: bool):
    # depending on input, set the action to /editor or /practice
    if is_editor:
        action = "/editor"
    else:
        action = "/practice"
    page = header
    cur = create_cursor(dbfile)
    questionsets = [line for line in cur.execute("SELECT d_id, d_name FROM decks;")]
    print(questionsets)
    # find all the files with the .data extension
    page += "<center><h1>Open a set of cards</h1></center><br><br>"
    page += "<div class='form-check center shadow' style='width: 50%; padding: 30px'>"
    page += f"<form method='post' action='{action}'>"
    for set_data in questionsets:
        page += "<p>"
        page += f"<input type='radio' class='form-check-input' name='id' id='{set_data[0]}' value='{set_data[0]}'>"
        page += f"<label class='form-check-label' for='{set_data[0]}'>{set_data[1]}</label><br>"
        page += "</p>"
    page += "<button type='submit' class='btn btn-primary ml-0'>open</button>"
    page += "</form>"
    page += "</div>"
    return page + footer

# create a new set of cards
@app.route("/create")
def create():
    page = header
    page += "<form method='post' action='/editor'>"
    page += "<input name='filename'><br>"
    page += "<button type='submit' class='btn btn-primary ml-0'>create</button>"
    return page + footer

# create a new local file for the set of cards
@app.route("/create_file", methods=["POST"])
def create_file():
    if request.method == "POST":
        global setname
        global questions
        setname = request.form["filename"] + ".data"
        questions = [{"type": "flashcard", "question": "", "answer": {"flashcard": "", "test": []}}]
    return editor(true)

# open the practice page with the selected set of cards
@app.route("/open_practice")
def open_practice():
    return openset(False)

# practice page, where the user can practice the selected set of cards
@app.route("/practice", methods=['POST'])
def practice():
    if request.method == "POST":
        filename = request.form["file"]
    with open(filename, "rb") as f:
        questions = pickle.load(f)
    clean_questions(questions)
    return header + render_template("practice.html", data=questions) + footer

if __name__ == "__main__":
    app.run()
