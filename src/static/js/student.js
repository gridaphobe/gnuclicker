(function() {
  "use strict";

  // hard-coded defaults...
  var userId     = "fea31132-33ca-400f-a170-4308e5aeec6d";
  var courseId   = "7620cfb2-1ca8-469b-ae53-e77e5c2f79d1";
  var questionId = "7b49eed0-6ee7-4d4f-b81e-fd8516edcaac";

  function pick(e) {
    var target = this;
    var answer = target.id.substring(7);
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
           answer,
           function (data) {
             submitting.classList.add("hidden");
             submitted_answer.innerHTML = answer;
             submitted.classList.remove("hidden");
           });

    // window.setTimeout(function() {
    //   submitting.classList.add("hidden");
    // }, 1000);

    e.stopPropagation();
    e.preventDefault();
  }

  window.addEventListener("load", function() {
    var matches = document.querySelectorAll(".student-response");
    for(var i = 0; i < matches.length; i++) {
      matches[i].addEventListener("click", pick);
    }
  });
})();
