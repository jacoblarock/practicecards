from flask import Flask, make_response, render_template, request, redirect, url_for
import sqlite3
import pickle
import os
from base64 import b64encode, b64decode
import random
import string

# create the flask app
app = Flask(__name__)

# read the header and footer from the templates folder
header = open("templates/header.html").read()
footer = open("templates/footer.html").read()

# global variables
setname = ""
set_id = 0
questions = []
user_id = 0
session_token = "JUNK"

# create the database connection
dbfile = "./practicecards.db"
def create_connection(dbfile):
    con = sqlite3.connect(dbfile)
    return con, con.cursor()

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
    if request.cookies.get("sessionId") != session_token:
        return header + render_template("index-logged-out.html") + footer
    else:
        return header + render_template("index.html") + footer

@app.route("/login")
def login(fail = False):
    if fail:
        return header + render_template("login.html") + footer
    else:
        return header + render_template("login.html") + footer

@app.route("/authenticate", methods=["POST"])
def authenticate():
    success = False
    if request.method == "POST":
        global user_id
        con, cur = create_connection(dbfile)
        users = [user for user in cur.execute("SELECT * FROM users;")]
        for user in users:
            if user[1] == request.form["username"] and user[2] == request.form["password"]:
                user_id = user[0]
                success = True
    if success:
        global session_token
        session_token = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=40))
        resp = make_response("<script>window.location.href = '/'</script>")
        resp.set_cookie("sessionId", session_token)
        return resp
    else:
        return login(success)

@app.route("/register")
def register():
    return header + render_template("register.html") + footer

@app.route("/create_user", methods=["POST"])
def create_user():
    if request.method == "POST":
        global user_id
        con, cur = create_connection(dbfile)
        max_id = cur.execute("SELECT MAX(u_id) FROM users;").fetchone()[0]
        print(f"INSERT INTO users VALUES ({int(max_id) + 1}, '{request.form["username"]}', '{request.form["password"]}');")
        cur.execute(f"INSERT INTO users VALUES ({int(max_id) + 1}, '{request.form["username"]}', '{request.form["password"]}');")
        global session_token
        session_token = "".join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=40))
        resp = make_response("<script>window.location.href = '/'</script>")
        resp.set_cookie("sessionId", session_token)
        return resp
    return "<script>window.location.href = '/register'</script>"


# edit page, where the user can create a new set or edit an existing one
@app.route("/edit")
def edit():
    if request.cookies.get("sessionId") != session_token:
        return "<script>window.location.href = '/login'</script>"
    return header + render_template("edit.html") + footer

# editor page for the user to edit the questions in a set
@app.route("/editor", methods=["POST"])
def editor():
    global questions
    global setname
    global set_id
    if request.cookies.get("sessionId") != session_token:
        return "<script>window.location.href = '/login'</script>"
    con, cur = create_connection(dbfile)
    max_id = cur.execute("SELECT MAX(d_id) FROM decks;").fetchone()[0]
    # if the user has selected a set, load the questions from the file
    if request.method == "POST":
        # try case create
        try:
            setname = request.form["filename"]
            questions = [{"type": "flashcard", "question": "", "answer": {"flashcard": "", "test": []}}]
            set_id = int(max_id) + 1
            cur.execute(f"INSERT INTO decks VALUES ({set_id}, {user_id}, '', '{setname}');")
            con.commit()
        except:
            # try case open
            try:
                set_id = request.form["id"] # sets the global variable
                set_rows = cur.execute(f"SELECT d_questions FROM decks WHERE d_id={set_id} AND d_user_ref={user_id};")
                set_data = set_rows.fetchone()
                questions = pickle.loads(b64decode(set_data[0].encode("utf-8")))
            except:
                pass
    # clean the questions for json
    clean_questions(questions)
    return header + render_template("editor.html", data=questions) + footer

# save the data from the editor page
@app.route("/save_data", methods=["POST"])
def save_data():
    if request.cookies.get("sessionId") != session_token:
        return "<script>window.location.href = '/login'</script>"
    if request.method == "POST":
        global questions
        global setname
        con, cur = create_connection(dbfile)
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
        cur.execute(f"UPDATE decks SET d_questions = '{b64encode(pickle.dumps(questions)).decode("utf-8")}' WHERE d_id = {str(set_id)};")
        con.commit()
    return render_template("save_data.html")

# call openset with is_editor set to true
@app.route("/open_editor")
def open_editor():
    if request.cookies.get("sessionId") != session_token:
        return render_template("<script>window.location.href = '/login'</script>")
    return openset(True) # open a set of cards  

@app.route("/open")
def openset(is_editor: bool):
    # depending on input, set the action to /editor or /practice
    if request.cookies.get("sessionId") != session_token:
        return "<script>window.location.href = '/login'</script>"
    if is_editor:
        action = "/editor"
    else:
        action = "/practice"
    page = header
    con, cur = create_connection(dbfile)
    questionsets = [line for line in cur.execute(f"SELECT d_id, d_name FROM decks WHERE d_user_ref={user_id};")]
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
    if request.cookies.get("sessionId") != session_token:
        return "<script>window.location.href = '/login'</script>"
    page = header
    page += "<form method='post' action='/editor'>"
    page += "<input name='filename'><br>"
    page += "<button type='submit' class='btn btn-primary ml-0'>create</button>"
    return page + footer

# create a new local file for the set of cards
@app.route("/create_file", methods=["POST"])
def create_file():
    if request.cookies.get("sessionId") != session_token:
        return "<script>window.location.href = '/login'</script>"
    if request.method == "POST":
        global setname
        global questions
        global set_id
        con, cur = create_connection(dbfile)
        max_id = cur.execute("SELECT MAX(d_id) FROM decks;").fetchone()[0]
        setname = request.form["filename"] + ".data"
        questions = [{"type": "flashcard", "question": "", "answer": {"flashcard": "", "test": []}}]
    return editor()

# open the practice page with the selected set of cards
@app.route("/open_practice")
def open_practice():
    if request.cookies.get("sessionId") != session_token:
        return "<script>window.location.href = '/login'</script>"
    return openset(False)

# practice page, where the user can practice the selected set of cards
@app.route("/practice", methods=['POST'])
def practice():
    if request.cookies.get("sessionId") != session_token:
        return "<script>window.location.href = '/login'</script>"
    if request.method == "POST":
        global questions
        con, cur = create_connection(dbfile)
        set_id = request.form["id"] # sets the global variable
        set_rows = cur.execute("SELECT d_questions FROM decks WHERE d_id=" + set_id )
        set_data = set_rows.fetchone()
        questions = pickle.loads(b64decode(set_data[0].encode("utf-8")))
    clean_questions(questions)
    return header + render_template("practice.html", data=questions) + footer

if __name__ == "__main__":
    app.run()
