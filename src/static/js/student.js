(function() {
  "use strict";

  var timer;

  function pick(e) {
    var target = this;
    var answer = target.id.substring(7,8);
    var choiceId = target.id.substring(9);
    var matches = document.querySelectorAll(".student-response.active");
    for(var i = 0; i < matches.length; i++) {
      matches[i].classList.remove("active");
    }

    target.classList.add("active");
    var submitting = document.getElementById("submitting");
    var submitted  = document.getElementById("submitted");
    var submitted_answer = document.getElementById("submitted-answer");
    submitting.classList.remove("hidden");
    submitted.classList.add("hidden");

    console.log(target);

    // send off ajax request...
    $.post("/courses/" + courseId + "/question/" + questionId + "/respond",
           {"choiceId": choiceId},
           function (data) {
             submitting.classList.add("hidden");
             submitted_answer.innerHTML = answer;
             submitted.classList.remove("hidden");
           });

    e.stopPropagation();
    e.preventDefault();
  }

  window.addEventListener("load", function() {
    var matches = document.querySelectorAll(".student-response");

    if ((timer = document.getElementById("timer"))) {
      // active round
      for (var i = 0; i < matches.length; i++) {
        matches[i].addEventListener("click", pick);
      }
      window.setInterval(function() { timer.innerHTML = 1 + parseInt(timer.innerHTML)}, 1000);
    }
  });
})();
