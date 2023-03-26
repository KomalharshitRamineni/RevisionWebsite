$(function () {
  $("#form-submit").on("click", function (e) {
    e.preventDefault();
    alert("Hello from form submit");
    $.ajax({
      type: "post",
      url: "/ajaxtest",
      data: $("#test-form").serialize(),
      //Headers: { csrf_token: $(this).find('input[name="csrf_token"]').val() },
      success: function (data) {
        var divEl = document.getElementById("ajax-target1");
        alert(divEl.attr("id"));
        alert(data);
        $("#ajax-target1").html(data);
      },
    });
    e.preventDefault();
  });
});
