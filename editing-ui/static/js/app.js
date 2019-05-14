(function(){'use strict';if(typeof global === "undefined" && typeof window !== "undefined") {
	window.global = window;
}

function copyIPNSToClipboard() {
  var ipns_input = document.getElementById("ipns-full-address");
  ipns_input.select();
  document.execCommand("copy");
  alert("Link copied to clipboard: " + ipns_input.value);
}window.copyIPNSToClipboard = copyIPNSToClipboard;}());