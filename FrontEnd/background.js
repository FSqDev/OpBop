// background.js

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.get(["blackList", "disableReliabilityWarning"], (data) => {
    if (data.blackList == undefined) {
      chrome.storage.sync.set({ blackList: [] });
    }
    if (data.disableReliabilityWarning == undefined) {
      chrome.storage.sync.set({disableReliabilityWarning: false})
    }
  })
  console.log('started');
});