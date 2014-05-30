(function() {
  "use strict";

  var timer;

  function ajax(url, onCompleted, verb, data) {
    // defaults
    onCompleted = onCompleted || function () {};
    verb = verb || 'GET';
    data = data || {};

    var httpRequest;
    if (window.XMLHttpRequest) { // Mozilla, Safari, ...
      httpRequest = new XMLHttpRequest();
    } else if (window.ActiveXObject) { // IE
      try {
        httpRequest = new ActiveXObject("Msxml2.XMLHTTP");
      }
      catch (e) {
        try {
          httpRequest = new ActiveXObject("Microsoft.XMLHTTP");
        }
        catch (e) {}
      }
    }

    if (!httpRequest) {
      console.log('Giving up :( Cannot create an XMLHTTP instance');
      return false;
    }
    httpRequest.onreadystatechange = function () {
      if (httpRequest.readyState === 4) {
        onCompleted(httpRequest);
      }
    };
    httpRequest.open(verb, url);
    if (data) {
      httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
      var msg = '';
      for (var key in data) {
        msg += '&' + key + '=' + encodeURIComponent(data[key]);
      }
      msg = msg.substring(1);
      console.log(msg);
      httpRequest.send(msg);
    } else {
      httpRequest.send();
    }
    return true;
  }

  function clearSubmit() {
    var ids = ["submitting", "submitted", "submitted-error"];
    for (var i = 0; i < ids.length; i++) {
      document.getElementById(ids[i]).classList.add("hidden");
    }
  }

  function pick(e) {
    var target = this;
    var answer = target.id.substring(7,8);
    var choiceId = target.id.substring(9);
    var matches = document.querySelectorAll(".student-response.active");
    for(var i = 0; i < matches.length; i++) {
      matches[i].classList.remove("active");
    }

    var submitting = document.getElementById("submitting");
    var submitted  = document.getElementById("submitted");
    var submitted_error = document.getElementById("submitted-error");
    var submitted_answer = document.getElementById("submitted-answer");

    target.classList.add("active");
    clearSubmit();
    submitting.classList.remove("hidden");
    submitted.classList.add("hidden");

    ajax("/courses/" + courseId + "/question/" + questionId + "/respond",
         function (req) {
           clearSubmit();
           if (req.status === 200) {
             submitted_answer.innerHTML = answer;
             submitted.classList.remove("hidden");
           } else {
             submitted_error.classList.remove("hidden");
           }
         }, 'POST', {"choiceId": choiceId});

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
