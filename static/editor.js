// define variables used for question generation
var questions = {}
// get page element
var page = document.getElementById("main");
// universal question index
var i = 0;

function generateQuestion(qNumber, type, question, answer) {
    var answerString = JSON.stringify(answer).replace(/\\n/g, "\\n")
                           .replace(/\\'/g, "\\'")
                           .replace(/\\"/g, '\\"')
                           .replace(/\\&/g, "\\&")
                           .replace(/\\r/g, "\\r")
                           .replace(/\\t/g, "\\t")
                           .replace(/\\b/g, "\\b")
                           .replace(/\\f/g, "\\f");
    var questionElem = document.createElement("div");
    questionElem.setAttribute("id", `question${qNumber}`);
    questionElem.setAttribute("class", "smooth");
    typeTest = type == "test" ? "selected" : "";
    typeFlashcard = type == "flashcard" ? "selected" : "";
    questionElem.innerHTML += `<h3 id='header-${qNumber}'>Question ${qNumber+1}:</h3>`;
    questionElem.innerHTML += `<select class="form-select form-select-lg mb-3" name="t-${qNumber}" id='t-${qNumber}' onChange="handleTypeChange(${qNumber})"><option value="flashcard" ${typeFlashcard}>Flashcard</option><option value="test" ${typeTest}>Test</option></select>`;
    questionElem.innerHTML += "<p>question: ";
    questionElem.innerHTML += `<textarea class="form-control" rows='5' style='width: 100%;' name='q-${qNumber}' id='q-${qNumber}' onkeyup="handleQuestionTextChange(${qNumber}, '${type}', '${question}')">${question}</textarea>`;
    questionElem.innerHTML += "</p>";
    questionElem.innerHTML += "<p>answer: </p>";
    questionElem.innerHTML += `<div id="ac-${qNumber}"></div><br>`;
    questionElem.innerHTML += `<a onclick='removeQuestion(${qNumber})' class='btn btn-danger ml-0' id='remove-${qNumber}'>remove</a>`
    questionElem.innerHTML += "<br><br>";
    page.appendChild(questionElem);
    fillAnswerContainer(qNumber, type, question, answer);
}

// generate buttons to add new question and save data
function generateButtons() {
    var buttons = document.createElement("div");
    buttons.setAttribute("id", "buttons");
    buttons.innerHTML += "<br><button id='save' type='submit' class='btn btn-primary ml-0'>save</button>&nbsp;&nbsp;";
    buttons.innerHTML += "<button id='add' onclick='addQuestion()' class='btn btn-primary ml-0'>add new question</button>";
    page.appendChild(buttons)
}


// add new empty question
function addQuestion() {

    document.getElementById("buttons").remove();
    generateQuestion(i, "flashcard", "", {"flashcard": "", "test": Array(0)});

    i++;
    generateButtons();
}

// remove question on click of remove button
function removeQuestion(number) {
    document.getElementById(`question${number}`).style.transform = "scale(0)";
    setTimeout(() => {
        document.getElementById(`question${number}`).remove();
        for (let index = number+1; index < i; index++) {
            document.getElementById(`question${index}`).setAttribute("id", `question${index-1}`);
            document.getElementById(`header-${index}`).innerHTML = `Question ${index}:`;
            document.getElementById(`header-${index}`).setAttribute("id", `header-${index-1}`);
            document.getElementById(`t-${index}`).setAttribute("name", `t-${index-1}`);
            document.getElementById(`t-${index}`).setAttribute("id", `t-${index-1}`);
            document.getElementById(`q-${index}`).setAttribute("name", `q-${index-1}`);
            document.getElementById(`q-${index}`).setAttribute("id", `q-${index-1}`);
            document.getElementById(`a-${index}`).setAttribute("name", `a-${index-1}`);
            document.getElementById(`a-${index}`).setAttribute("id", `a-${index-1}`);
            document.getElementById(`remove-${index}`).setAttribute("onclick", `removeQuestion(${index-1})`);
            document.getElementById(`remove-${index}`).setAttribute("id", `remove-${index-1}`);
        }
        i--;
    }, 200);
}

function fillAnswerContainer(qNumber, type, question, answer) {
    var answerContainer = document.getElementById("ac-" + qNumber);
    if (type == "flashcard") {
        answerContainer.innerHTML = `<textarea class="form-control" rows='5' style='width: 100%;' name='a-${qNumber}' id='a-${qNumber}'>${answer["flashcard"]}</textarea>`;
    } else if (type == "test") {
        updateTestAnswer(qNumber, type, question);
    }
}

function handleTypeChange(qNumber) {
    var answer = {"flashcard": "", "test": Array(0)};
    if (qNumber < questions.length) {
        answer = questions[qNumber]["answer"];
    }
    var questionText = document.getElementById(`q-${qNumber}`).value;
    var state = document.getElementById("t-" + qNumber).value;
    var answerContainer = document.getElementById("ac-" + qNumber);
    handleQuestionTextChange(qNumber, state, questionText);
    questionText = document.getElementById(`q-${qNumber}`).value;
    if (document.getElementById(`t-${qNumber}`).value == "flashcard") {
        var splitQuestion = questionText.split("\n");
        for (let qindex = 1; qindex < splitQuestion.length; qindex++) {
            if (splitQuestion[qindex].startsWith("☑ ")) {
                splitQuestion[qindex] = splitQuestion[qindex].substring(2);
            }
        }
        questionText = splitQuestion.join("\n");
        document.getElementById(`q-${qNumber}`).value = questionText;
    }
    fillAnswerContainer(qNumber, state, questionText, answer);
}

function updateTestAnswer(qNumber, type, question) {
    var answerContainer = document.getElementById("ac-" + qNumber);
    answerContainer.innerHTML = "";
    splitQuestion = question.split("\n");
    for (let i = 1; i < splitQuestion.length; i++) {
        var questionText = splitQuestion[i].substring(2);
        var answer = {"flashcard": "", "test": Array(0)};
        if (qNumber < questions.length) {
            answer = questions[qNumber]["answer"];
        }
        var checked = answer["test"].includes(questionText) ? "checked" : "";
        answerContainer.innerHTML += `<div class="form-check form-check-inline"><input class="form-check-input" type="checkbox" name="at-${qNumber}-${i}" id="at-${qNumber}-${i}" value="${questionText}" ${checked}><label class="form-check-label" for="at-${qNumber}-${i}">${questionText}</label></div><br>`;
    }
}

function handleQuestionTextChange(qNumber, type, question) {
    var questionText = document.getElementById(`q-${qNumber}`).value;
    var splitQuestion = questionText.split("\n");
    if (document.getElementById(`t-${qNumber}`).value == "test") {
        for (let qindex = 1; qindex < splitQuestion.length; qindex++) {
            if (splitQuestion[qindex].length == 1) {
                splitQuestion.splice(qindex, 1);
            }
            else if (!splitQuestion[qindex].startsWith("☑ ")) {
                splitQuestion[qindex] = "☑ " + splitQuestion[qindex];
            }
        }
        document.getElementById(`q-${qNumber}`).value = splitQuestion.join("\n");
        updateTestAnswer(qNumber, type, questionText);
    }
}

function init(data) {
    // get question data from page 
    questions = data; 
    // display questions in question data on page
    for(i = 0; i < questions.length; i++){
        generateQuestion(i, questions[i].type, questions[i].question, questions[i].answer);
    };

    generateButtons();
}