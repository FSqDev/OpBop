// background.js

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.get("blackList", (data) => {
    if (data.blackList == undefined) {
      chrome.storage.sync.set({ blackList: [] });
    }
  })
  console.log('started');
});