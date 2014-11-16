// ==UserScript==
// @name        StackOverflow Prototype
// @namespace   SOP
// @include     http://stackoverflow.com/*
// @version     1
// @grant       none
// ==/UserScript==

var $ = unsafeWindow.jQuery;

$(document).ready(function(){

  var $div = $("<div>").html("You have an open <a href='http://stackoverflow.com/questions/26777362/forge-facebook-logout-is-not-clearing-the-token'>question</a>. Consider accepting an answer or setting a bounty. We predict that you will get an answer within 27 minutes of setting a bounty.")

  $notify = $("#notify-container")
    .css({"position" :"static"})
    .append($div)
    .animate({"height": "30px"}, 1000)

})
