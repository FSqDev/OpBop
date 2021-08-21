// background.js

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.get("blackList", (data) => {
    if (data.blackList == null) {
      chrome.storage.sync.set({ blackList: [] });
    }
  })
  console.log('started');
});