//var i = setInterval(IntervalChecking, 100);

function checkEvent(str) {
  str.trim();
  var pattern = /[^0-9a-z]/i;
  if (pattern.test(str)) {
    return false;
  }
  return true;
}

function checkUrl(str) {}
  str.trim();
  pattern = /(http|https)\/\//;
}

function $(x) {
  return document.getElementById(x);
}

function IntervalChecking() {

}