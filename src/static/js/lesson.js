(function() {
  function ajax(url, onCompleted, verb, data) {
    // defaults
    onCompleted = onCompleted || function () {};
    verb = verb || 'GET';

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
      httpRequest.send(msg);
    } else {
      httpRequest.send();
    }
    return true;
  }

  function expand(e) {
    var target = this;
    var obj = this.nextSibling;
    while(obj.nodeType != 1)
      obj = obj.nextSibling;

    target.classList.toggle("sel");
    obj.classList.toggle("hide");

    e.stopPropagation();
    e.preventDefault();
  }

  function togglePoll(e) {
    var target = this.parentElement.parentElement,
        open   = target.querySelector(".open-poll"),
        close  = target.querySelector(".close-poll"),
        alert  = document.getElementById("alert");

    var url;
    if (open.classList.contains("hidden")) {
      url = close.action;
    } else {
      url = open.action;
    }

    ajax(url, function(request) {
      if (request.status < 400) {
        open.classList.toggle("hidden");
        close.classList.toggle("hidden");
        alert.querySelector("a").text = target.parentElement.previousElementSibling.text;
        alert.classList.toggle("hidden");
      }
    }, "POST");

    e.stopPropagation();
    e.preventDefault();
    return false;
  }

  window.addEventListener("load", function() {
    var i;
    var matches = document.querySelectorAll(".questions > .item");
    for(i = 0; i < matches.length; i++) {
      matches[i].addEventListener("click", expand);
    }
    matches = document.querySelectorAll(".questions > .question > .buttons > form > button");
    for(i = 0; i < matches.length; i++) {
      matches[i].addEventListener("click", togglePoll);
    }
  });
})();
