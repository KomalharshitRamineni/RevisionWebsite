function myFunction() {
  $.ajax({
    type: "GET",
    url: "/ajaxtest",
    success: function (data) {
      console.log("get info");
      $("#ajax-target").html(data);
    },
  });
}
