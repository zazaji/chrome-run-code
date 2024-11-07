document.addEventListener("DOMContentLoaded", () => {
  const saveButton = document.getElementById("save");
  const addressInput = document.getElementById("serverAddress");
  const tokenInput = document.getElementById("token");
  const isLocalSelect = document.getElementById("isLocal"); // 修改变量名

  // 加载保存的服务器地址和 token
  chrome.storage.sync.get(["serverAddress", "token", "isLocal"], (data) => {
    if (data.serverAddress) {
      addressInput.value = data.serverAddress;
    }
    if (data.token) {
      tokenInput.value = data.token;
    }
    if (data.isLocal) {
      isLocalSelect.value = data.isLocal; // 使用修改后的变量名
    }
  });

  // 保存服务器地址和 token
  saveButton.addEventListener("click", () => {
    const serverAddress = addressInput.value;
    const token = tokenInput.value;
    const isLocal = isLocalSelect.value; // 使用修改后的变量名
    chrome.storage.sync.set({ serverAddress, token, isLocal }, () => {
      alert("Server address and token saved!");
    });
  });
});
