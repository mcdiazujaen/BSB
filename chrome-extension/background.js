function postData(url, data) {
  chrome.tabs.create(
    { url: chrome.runtime.getURL("post.html") },
    function(tab) {
      var handler = function(tabId, changeInfo) {
        if(tabId === tab.id && changeInfo.status === "complete"){
          chrome.tabs.onUpdated.removeListener(handler);
          chrome.tabs.sendMessage(tabId, {url: url, data: data});
        }
      }

      // in case we're faster than page load (usually):
      chrome.tabs.onUpdated.addListener(handler);
      // just in case we're too late with the listener:
      chrome.tabs.sendMessage(tab.id, {url: url, data: data});
    }
  );
}

chrome.browserAction.onClicked.addListener(function(tab) {
  chrome.tabs.executeScript({
    code: 'window.getSelection().toString();'
  }, function(text) {
    var encoded_text = window.btoa(unescape(encodeURIComponent( text )));
    //alert(text + "\n--------------------\n" + encoded_text);
    postData("http://localhost:5000/parse", { "t": encoded_text });
    // var serviceCall = 'http://localhost:5000/parse?t=' + text;
    // chrome.tabs.create({url: serviceCall});
  });
});
