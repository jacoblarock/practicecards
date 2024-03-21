// define variables used for question generation
var questions = {}
// get page element
var page = document.getElementById("main");
// universal question index
var i = 0;

function generateQuestion(qNumber, type, question, answer) {
    var questionElem = document.createElement("div");
    questionElem.setAttribute("id", `question${qNumber}`);
    questionElem.setAttribute("class", "smooth");
    typeTest = type == "test" ? "selected" : "";
    typeFlashcard = type == "flashcard" ? "selected" : "";
    questionElem.innerHTML += `<h3 id='header-${qNumber}'>Question ${qNumber+1}:</h3>`;
    questionElem.innerHTML += `<select class="form-select form-select-lg mb-3" name="t-${qNumber}" id='t-${qNumber}'><option value="flashcard" ${typeFlashcard}>Flashcard</option><option value="test" ${typeTest}>Test</option></select>`;
    questionElem.innerHTML += "<p>question: ";
    questionElem.innerHTML += `<textarea class="form-control" rows='5' style='width: 100%;' name='q-${qNumber}' id='q-${qNumber}'>${question}</textarea>`;
    questionElem.innerHTML += "</p>";
    questionElem.innerHTML += "<p>answer: ";
    questionElem.innerHTML += `<textarea class="form-control" rows='5' style='width: 100%;' name='a-${qNumber}' id='a-${qNumber}'>${answer}</textarea>`;
    questionElem.innerHTML += "</p>";
    questionElem.innerHTML += `<a onclick='removeQuestion(${qNumber})' class='btn btn-danger ml-0' id='remove-${qNumber}'>remove</a>`
    questionElem.innerHTML += "<br><br>";
    questionElem.addEventListener("keyup", event => {
        questionText = document.getElementById(`q-${qNumber}`).value;
        answerText = document.getElementById(`a-${qNumber}`).value;
        splitQuestion = questionText.split("\n");
        splitAnswer = answerText.split("\n");
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
        }
    });
    page.appendChild(questionElem);
}

// generate buttons to add new question and save data
function generateButtons() {
    var buttons = document.createElement("div");
    buttons.setAttribute("id", "buttons")
    buttons.innerHTML += "<br><button id='save' type='submit' class='btn btn-primary ml-0'>save</button>&nbsp;&nbsp;";
    buttons.innerHTML += "<button id='add' onclick='addQuestion()' class='btn btn-primary ml-0'>add new question</button>";
    page.appendChild(buttons)
}


// add new empty question
function addQuestion() {

    document.getElementById("buttons").remove();
    generateQuestion(i, "flashcard", "", "");

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



function init(data) {
    // get question data from page 
    questions = data; 
    // display questions in question data on page
    for(i = 0; i < questions.length; i++){
        generateQuestion(i, questions[i].type, questions[i].question, questions[i].answer);
    };

    generateButtons();
    console.log("test");
}

