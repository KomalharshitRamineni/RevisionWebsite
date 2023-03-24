function allowDrop(ev) {
  ev.preventDefault();
}

function drag(ev) {
  ev.dataTransfer.setData("text", ev.target.id);
}

function drop(ev) {
  ev.preventDefault();
  var data = ev.dataTransfer.getData("text");
  alert(ev.target.childNodes.length);
  if (ev.target.childNodes.length == 0) {
    ev.target.appendChild(document.getElementById(data));
  }
}
function getValues() {
  event.preventDefault();
  var answers = [];
  $(".drop-section").each(function () {
    var dropedValue = $(this).find("span");
    var innerDivId = $(this).attr("id");
    var obj = new QandA(innerDivId, dropedValue.attr("id"));
    var inputValue = $(this).find('input["type:hidden"]');
    inputValue.val(obj);
    answers.push(obj);
  });
  let isEmpty = validate(answers);
  alert(isEmpty);
  if (!isEmpty) {
    $("#error-message").text("Please answer all questions by drag and drop");
  } else {
    $("#error-message").text("");
    answers.forEach((el) => alert(el.answer));
  }
}
function validate(list) {
  let isvalid = true;
  list.forEach((x) => {
    if (x.answer === null || x.answer === "" || x.answer === undefined) {
      isvalid = false;
    }
  });
  return isvalid;
}
function QandA(question, answer) {
  this.question = question;
  this.answer = answer;
}
function resetAnswerPad() {
  alert("hello");
  var container = document.getElementById("drag-container");
  container.innerHTML = html;
  $(".drop-section").find("span").remove();
}
var html;
window.onload = function () {
  html = document.getElementById("drag-container").innerHTML;
};
