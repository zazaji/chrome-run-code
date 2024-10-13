chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (
    tab.url &&
    !tab.url.startsWith("vivaldi://") &&
    !tab.url.startsWith("chrome://") &&
    !tab.url.startsWith("chrome-extension://")
  ) {
    if (changeInfo.status === "complete") {
      chrome.scripting
        .insertCSS({
          target: { tabId: tabId },
          css: `
      .custom-render-div{
        border: #444444;
      }`,
        })
        .then(() => {
          console.log("CSS injected successfully.", tab.url);
        })
        .catch((error) => {
          console.error("Error injecting CSS1:", tab.url, error);
        });
    }
  }
});
// chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
//   if (changeInfo.status === "complete" && /^http/.test(tab.url)) {
//     // 当页面加载完成时，注入 content.js 的逻辑
//     chrome.scripting.executeScript(
//       {
//         target: { tabId: tabId },
//         files: ["content.js"],
//       },
//       () => {
//         console.log("Injected content script.");
//       },
//     );
//   }
// });
