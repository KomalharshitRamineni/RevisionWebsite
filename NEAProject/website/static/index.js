$(function () {
  // alert("hello");
  // let form = $("#quiz-section").find("#mc-form");
  // form.addEventListener("submit", function (event) {
  //   event.preventDefault();
  //   alert("Event listening");
  // });
  //var form = $("#mc-form");
  $("form").on("submit", function (e) {
    alert("Hello from form submit");

    //let formData = new FormData(document.querySelector("form"));
    // let x = formData.serilize();
    // alert(x);
    //alert(formData);
    $.ajax({
      type: "post",
      url: "/multiplayerQuiz/1",
      data: $(this).serialize(),
      Headers: { csrf_token: $(this).find('input[name="csrf_token"]').val() },
      success: function (data) {
        alert(data);
        console.log("get info");
        $("#quiz-section").html(data);
      },
    });
    e.preventDefault();
  });
});
