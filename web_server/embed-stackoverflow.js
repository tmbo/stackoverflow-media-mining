(function(){

  window.renderIntoElement = function(selector, url) {

    var container = document.querySelector(selector);
    if (container) {

      var css = "         \
        html, body {      \
          height: 100%;   \
        }                 \
        .chromeless {     \
          width: 100%;    \
          height: 100%;   \
          left: 0px;      \
          top: 0px;       \
          border: 0px;    \
          margin: 0px;    \
          padding: 0px;   \
        }                 \
      "
      // Insert CSS
      var style = document.createElement("style");
      style.type = "text/css";
      style.innerHTML = css;
      document.getElementsByTagName("head")[0].appendChild(style);

      // Insert iFrame
      var html = "<iframe class='chromeless' src='" + url + " '>"
      container.insertAdjacentHTML("beforeend", html);


    } else {
      console.error("Couldn't find element.");
    }

  }


})()