$(function () {
  $("#flipcard").on("click", function (e) {
    alert($(this).attr("name"));
    var action = $(this).attr("name");
    $(this).attr("name", action == "question" ? "answer" : "question");
    alert($(this).attr("name"));
  });
});
