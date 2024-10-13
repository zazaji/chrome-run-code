// options.js
document.addEventListener("DOMContentLoaded", () => {
  const saveButton = document.getElementById("save");
  const addressInput = document.getElementById("serverAddress");
  const tokenInput = document.getElementById("token"); // 新增 token 输入框

  // 加载保存的服务器地址和 token
  chrome.storage.sync.get(["serverAddress", "token"], (data) => {
    if (data.serverAddress) {
      addressInput.value = data.serverAddress;
    }
    if (data.token) {
      tokenInput.value = data.token; // 加载已保存的 token
    }
  });

  // 保存服务器地址和 token
  saveButton.addEventListener("click", () => {
    const serverAddress = addressInput.value;
    const token = tokenInput.value; // 获取 token 的值
    chrome.storage.sync.set({ serverAddress, token }, () => {
      alert("Server address and token saved!");
    });
  });
});
