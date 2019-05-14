export function copyIPNSToClipboard() {
  var ipns_input = document.getElementById("ipns-full-address")
  ipns_input.select();
  document.execCommand("copy");
  alert("Link copied to clipboard: " + ipns_input.value);
};
