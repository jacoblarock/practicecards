var questionHeader = document.getElementById("questionHeader");
var questionBody = document.getElementById("questionBody");
var testChoices = document.getElementById("testChoices");
var answerText = document.getElementById("answer");
var qIndex = 0;
// get question data from python
var questions = {};

// shuffle questions
function shuffleArray(array) {
    for (var i = array.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var temp = array[i];
        array[i] = array[j];
        array[j] = temp;
    }
}
// show question
function showFront() {
    var questionType = questions[qIndex]["type"];
    var currentQuestion = questions[qIndex]["question"].split("\n");
    if (questionType == "flashcard") {
        testChoices.innerHTML = "";
        answerText.innerText = "";
        questionHeader.innerText = currentQuestion[0];
        questionBody.innerText = currentQuestion.slice(1).join("\n");
    } else if (questionType == "test") {
        var choices = currentQuestion.slice(1);
        shuffleArray(choices);
        var choiceHTML = "";
        questionHeader.innerText = currentQuestion[0];
        answerText.innerText = "";
        questionBody.innerText = "";
        for (var i = 0; i < choices.length; i++) {
            choiceHTML += "<input type='checkbox' class='form-check-input' name='choice' id='" + choices[i].replace("☑ ", "") + "'>&nbsp;&nbsp;" + choices[i].replace("☑ ", "") + "<br>";
        }
        testChoices.innerHTML = choiceHTML;
    }
}
// show answer
function showBack() {
    var questionType = questions[qIndex]["type"];
    if (questionType == "flashcard") {
        answerText.innerText = questions[qIndex]["answer"];
    } else if (questionType == "test") {
        var choices = document.getElementsByName("choice");
        var correct = true;
        for (var i = 0; i < choices.length; i++) {
            if (choices[i].checked != questions[qIndex]["answer"].includes(choices[i].id)) {
                correct = false;
            }
        }
        if (correct) {
            answerText.innerText = "Correct!";
        } else {
            answerText.innerText = "Incorrect!";
        }
    }
}
// show next question
function next() {
    if(qIndex < questions.length - 1) {
        qIndex++;
    }
    showFront();
}
// show previous question
function prev() {
    if(qIndex > 0) {
        qIndex--;
    }
    showFront();
}
// initialize
function init(data) {
    questions = data;
    shuffleArray(questions);
    showFront();
}
