(function() {
  function dropdown(e) {
    var target = this;
    var obj = this.querySelector(".dropdown");
    while(obj.nodeType != 1)
      obj = obj.nextSibling;

    obj.classList.toggle("show");
    obj.parentNode.classList.toggle("sel");

    target.removeEventListener("click", dropdown);
    document.addEventListener("click", function handler() {
      obj.classList.toggle("show");
      obj.parentNode.classList.toggle("sel");

      document.removeEventListener("click", handler);
      target.addEventListener("click", dropdown);
    });

    e.stopPropagation();
    e.preventDefault();
  }

  window.addEventListener("load", function() {
    var matches = document.querySelectorAll(".dropdown-expand");
    for(var i = 0; i < matches.length; i++) {
      matches[i].addEventListener("click", dropdown);
    }
  });
})();
