(function() {
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

  window.addEventListener("load", function() {
    var matches = document.querySelectorAll(".questions > .item");
    for(var i = 0; i < matches.length; i++) {
      matches[i].addEventListener("click", expand);
    }
  });
})();
