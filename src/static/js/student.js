(function() {
  "use strict";

  function pick(e) {
    var target = this;
    var matches = document.querySelectorAll(".student-response.active");
    for(var i = 0; i < matches.length; i++) {
      matches[i].classList.remove("active");
    }

    target.classList.add("active");
    var flower = document.getElementById("flower-gear");
    flower.classList.remove("hidden");

    // send off ajax request...
    window.setTimeout(function() {
      flower.classList.add("hidden");
    }, 1000);

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
