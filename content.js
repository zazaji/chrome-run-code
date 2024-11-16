// Helper function to extract code content, with improved error handling
//
let webClass = "";
function extractCodeContent(codeElement) {
  const table = codeElement.querySelector("table.hljs-ln");
  if (table) {
    let codeLines = [];
    const rows = table.querySelectorAll("tr");
    rows.forEach((row) => {
      const codeLine = row.querySelector(".hljs-ln-code");
      if (codeLine) {
        codeLines.push(codeLine.textContent);
      }
    });
    return codeLines.join("\n");
  }

  const parentDiv = codeElement.closest("div.code-block__code");
  if (parentDiv) {
    return codeElement.textContent.trim();
  }
  const codeSpans = codeElement.querySelectorAll("span.linenumber");
  codeSpans.forEach((span) => span.remove()); // 移除所有行号
  const codeLeft = codeElement.querySelectorAll("div.left-part");
  codeLeft.forEach((span) => span.remove()); // 移除所有行号
  // 修改完善：避免直接修改DOM字符串，改为创建新的DOM元素并插入<br>标签
  //
  const rightPart = codeElement.querySelector("div.right-part");
  let textContent = "";
  if (rightPart) {
    rightPart.querySelectorAll("div").forEach((div) => {
      textContent += div.textContent + "\n";
    });
  } else {
    textContent = codeElement.textContent.trim();
  }
  return textContent;
}

// Detects the language of the code block
function detectCodeLanguage(preElement) {
  const codeElement = preElement.querySelector("code");
  if (codeElement) {
    const classList = codeElement.classList;
    for (let className of classList) {
      if (className.startsWith("language-")) {
        return className.replace("language-", "");
      }
    }
  }

  const parentDiv = preElement.closest("div");
  if (parentDiv) {
    // console.log(parentDiv);
    const langDiv = parentDiv.querySelector(
      ".code-lang, .language, .top .language ",
    );
    if (langDiv && langDiv.textContent.trim()) {
      console.log(langDiv.textContent.trim().toLowerCase());
      return langDiv.textContent.trim().toLowerCase();
    }
  }
  // console.log("123456");
  const parentParentDiv = parentDiv ? parentDiv.parentElement : null;

  if (parentParentDiv) {
    // console.log(parentParentDiv);
    const langDiv = parentParentDiv.querySelector(
      "span.tongyi-design-highlighter-lang",
    );

    if (langDiv && langDiv.textContent.trim()) {
      return langDiv.textContent.trim().toLowerCase();
    }
  }
  const codeText = codeElement ? codeElement.textContent : "";

  // 取前10行
  const lines = codeText.split("\n").slice(0, 10).join("\n");

  // 正则表达式匹配
  const isPython = /\bdef\b|\nimport\b|\bprint\(\b/.test(lines);
  const isHTML = /<html|<body|<iframe/.test(lines);
  const isSh = /\bcd\b|\bgit\b|\bpython\b|\bwget\b|\bmkdir\b|\bls\b/.test(
    lines,
  );

  // console.log(isPython, isHTML, isSh);
  if (isPython) {
    return "python";
  } else if (isHTML) {
    return "html";
  } else if (isSh) {
    return "sh";
  }

  return null;
}

// Function to create and display the modal window for code editing
// Function to create and display the modal window for code editing
function createEditModal(codeContent, saveCallback) {
  // Create the modal elements
  const modal = document.createElement("div");
  modal.classList.add("custom-modal");
  modal.style.position = "fixed";
  modal.style.top = "0";
  modal.style.left = "0";
  modal.style.width = "100vw";
  modal.style.height = "100vh";
  modal.style.backgroundColor = "rgba(0, 0, 0, 0.5)";
  modal.style.zIndex = "9999";
  modal.style.display = "flex";
  modal.style.justifyContent = "center";
  modal.style.alignItems = "center";

  const modalContent = document.createElement("div");
  modalContent.classList.add("custom-modal-content");
  modalContent.style.backgroundColor = "#808080";
  modalContent.style.padding = "20px";
  modalContent.style.borderRadius = "8px";
  modalContent.style.width = "80%";
  modalContent.style.maxHeight = "80%";
  modalContent.style.overflowY = "auto";

  // Create a textarea to edit the code
  const textArea = document.createElement("textarea");
  textArea.value = codeContent;
  textArea.style.width = "100%";
  textArea.style.height = "400px";
  textArea.style.fontSize = "16px";
  textArea.style.backgroundColor = "#808080";
  textArea.style.color = "#fff";
  textArea.style.fontFamily = "monospace";

  // Append textarea to modal content
  modalContent.appendChild(textArea);

  // Set focus to the textarea to activate virtual keyboard on mobile
  textArea.focus();

  // Also listen to touch events to ensure mobile compatibility
  textArea.addEventListener("touchstart", () => textArea.focus());

  // Button container
  const buttonContainer = document.createElement("div");
  buttonContainer.style.marginTop = "10px";
  buttonContainer.style.display = "flex";
  buttonContainer.style.justifyContent = "space-between";

  // Accept button
  const acceptButton = document.createElement("button");
  acceptButton.innerText = "Accept";
  acceptButton.style.padding = "10px";
  acceptButton.style.backgroundColor = "#4CAF50";
  acceptButton.style.color = "#fff";
  acceptButton.style.border = "none";
  acceptButton.style.borderRadius = "4px";
  acceptButton.addEventListener("click", () => {
    const updatedCode = textArea.value;
    saveCallback(updatedCode);
    document.body.removeChild(modal); // Close the modal
  });
  buttonContainer.appendChild(acceptButton);

  // Cancel button
  const cancelButton = document.createElement("button");
  cancelButton.innerText = "Cancel";
  cancelButton.style.padding = "10px";
  cancelButton.style.backgroundColor = "#f44336";
  cancelButton.style.color = "#fff";
  cancelButton.style.border = "none";
  cancelButton.style.borderRadius = "4px";
  cancelButton.addEventListener("click", () => {
    document.body.removeChild(modal); // Close the modal
  });
  buttonContainer.appendChild(cancelButton);

  // Append button container to modal content
  modalContent.appendChild(buttonContainer);

  // Append modal content to modal and add modal to the body
  modal.appendChild(modalContent);
  document.body.appendChild(modal);
}

// Function to add the Run, Save, and Edit buttons to code blocks
function addRenderButtonToCode(codeElement, filenameElement = null) {
  let language = null;
  let containerDiv = null;

  if (filenameElement) {
    language = filenameElement.split(".")[1];
    containerDiv = codeElement.closest("div");
  } else {
    containerDiv = codeElement.closest("pre");
    if (!containerDiv || containerDiv.querySelector(".custom-render-button")) {
      return;
    }
    language = detectCodeLanguage(containerDiv);
  }

  const buttonContainer = document.createElement("div");
  buttonContainer.classList.add(
    "button-container",
    "absolute",
    "bottom-1",
    "right-1",
    "flex",
    "space-x-2",
    "items-center",
  );

  if (
    ["css", "csv", "txt", "md", "yaml", "json", "ini", "xml"].includes(language)
  ) {
    const saveButton = document.createElement("div");
    saveButton.innerHTML = "☌ Save";
    saveButton.classList.add("custom-render-button", "run-save-button");

    const editButton = document.createElement("div");
    editButton.innerHTML = "✎ Edit";
    editButton.classList.add("custom-render-button", "edit-button");

    buttonContainer.appendChild(saveButton);
    buttonContainer.appendChild(editButton);

    containerDiv.style.position = "relative";
    containerDiv.appendChild(buttonContainer);

    saveButton.addEventListener("click", () => {
      const codeContent = extractCodeContent(codeElement);
      sendCodeToServer(codeContent, 0, containerDiv, language);
    });

    editButton.addEventListener("click", () => {
      const codeContent = extractCodeContent(codeElement);
      createEditModal(codeContent, (updatedCode) => {
        codeElement.textContent = updatedCode;
      });
    });
  }

  if (
    [
      "python",
      "py",
      "js",
      "javascript",
      "html",
      "md",
      "markdown",
      "vue",
      "gitignore",
      "bash",
      "sh",
      "cmd",
      "shell",
      "php",
      "java",
    ].includes(language)
  ) {
    const runButton = document.createElement("div");
    runButton.innerHTML = "☛ Run";
    runButton.classList.add("custom-render-button", "run-save-button");

    const saveButton = document.createElement("div");
    saveButton.innerHTML = "☌ Save";
    saveButton.classList.add("custom-render-button", "run-save-button");

    const editButton = document.createElement("div");
    editButton.innerHTML = "✎ Edit";
    editButton.classList.add("custom-render-button", "edit-button");

    buttonContainer.appendChild(runButton);
    buttonContainer.appendChild(saveButton);
    buttonContainer.appendChild(editButton);

    containerDiv.style.position = "relative";

    containerDiv.appendChild(buttonContainer);

    runButton.addEventListener("click", () => {
      // console.log("run", codeElement);
      const codeContent = extractCodeContent(codeElement);
      sendCodeToServer(codeContent, 1, containerDiv, language);
    });

    saveButton.addEventListener("click", () => {
      const codeContent = extractCodeContent(codeElement);
      sendCodeToServer(codeContent, 0, containerDiv, language);
    });

    editButton.addEventListener("click", () => {
      const codeContent = extractCodeContent(codeElement);
      createEditModal(codeContent, (updatedCode) => {
        codeElement.textContent = updatedCode;
      });
    });
  }
}

// Function to send code content to the server
function sendCodeToServer(codeContent, runParam, containerDiv, language) {
  chrome.storage.sync.get(["serverAddress", "token", "isLocal"], (data) => {
    const serverAddress = data.serverAddress || "http://localhost:8000/runcode";
    const isLocal = data.isLocal || true;
    const token = data.token || "";
    let resultDiv = containerDiv.querySelector(".custom-result-div");
    if (resultDiv) {
      resultDiv.innerHTML = "";
    } else {
      resultDiv = document.createElement("div");
      resultDiv.classList.add(
        "custom-result-div",
        "border",
        "border-gray-400",
        "font-mono",
      );
      resultDiv.style.backgroundColor = "rgba(128, 128, 128, 0.1)";
      containerDiv.appendChild(resultDiv);
    }
    fetch(serverAddress, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        // Authorization: `Bearer ${token}`, // 添加 token 认证
      },
      body: JSON.stringify({
        token: token, // 添加 token 认证
        code: codeContent,
        run: runParam,
        language: language,
        isLocal: isLocal,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        resultDiv.innerHTML = "";
        if (data.outputs && data.outputs.length > 0) {
          data.outputs.forEach((output) => {
            if (output.type === "image") {
              const img = document.createElement("img");
              img.src = output.data;
              img.style.maxWidth = "100%";
              img.alt = "Output Image";
              resultDiv.appendChild(img);
            } else if (output.type === "text") {
              const textOutput = document.createElement("div");
              textOutput.innerHTML = output.data;
              if (language === "html") {
                textOutput.innerHTML = textOutput.innerHTML.replace(
                  "/static/",
                  `${serverAddress}/../static/`,
                );
              }
              resultDiv.appendChild(textOutput);
            } else if (output.type === "html") {
              const htmlOutput = document.createElement("div");
              htmlOutput.innerHTML = output.data;
              resultDiv.appendChild(htmlOutput);
            } else if (output.type === "error") {
              const errorOutput = document.createElement("div");
              errorOutput.innerHTML = `<strong>Error:</strong> ${output.data}`;
              errorOutput.style.color = "red";
              resultDiv.appendChild(errorOutput);
            }
          });
        } else {
          resultDiv.innerHTML = "No output returned";
        }
      })
      .catch((error) => {
        resultDiv.innerHTML = `Error: ${error.message}`;
      });
  });
}

function extractLanguageAndCode() {
  const divcodeElements = document.querySelectorAll("div.highlight pre");
  if (divcodeElements.length > 0) {
    divcodeElements.forEach((codeElement) => {
      let lang = "lang. ";
      codeElement.parentElement.classList.add("hljs");
      const classList = codeElement.parentElement.classList;
      for (let className of classList) {
        if (className.startsWith("highlight-source-")) {
          lang = className.replace("highlight-source-", "lang.");
        }
      }
      addRenderButtonToCode(codeElement.parentElement, lang);
    });
  }

  const codeElements = document.querySelectorAll("pre code");
  // console.log(codeElements);
  if (codeElements.length > 0) {
    codeElements.forEach((codeElement) => {
      divcode = codeElement.querySelector("div.code-wrapper");
      if (divcode) {
        divcode.classList.add("hljs");
        addRenderButtonToCode(divcode);
      } else {
        addRenderButtonToCode(codeElement);
      }
    });
  }

  // 支持github;
  const textareaElement = document.querySelector(
    'textarea[data-testid="read-only-cursor-text-area"]',
  );
  if (textareaElement) {
    const filenameElement = document.querySelector(
      '[data-testid="breadcrumbs-filename"] h1',
    ).textContent;
    addRenderButtonToCode(textareaElement, filenameElement);
  }
}

// Add mutation observer to detect dynamically added code blocks
// const observer = new MutationObserver((mutations) => {
//   setTimeout(() => {
//     extractLanguageAndCode();
//   }, 2000);
// });
//
//
let isExtracting = false; // 标志变量，防止多次调用 extractLanguageAndCode

const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
      // 检查是否有新节点被添加
      if (!isExtracting) {
        isExtracting = true;
        requestAnimationFrame(() => {
          setTimeout(() => {
            extractLanguageAndCode();
          }, 2000);
          isExtracting = false;
        });
      }
    }
  });
});

function addButtonToTextarea(textarea) {
  // 创建按钮
  const button = document.createElement("button");
  button.innerText = "⚙️"; // 使用特殊符号
  button.style.position = "absolute";
  button.style.left = "-20px";
  button.style.bottom = "-20px";
  button.style.color = "grey";
  button.style.border = "none";
  button.style.zIndex = "999";

  // 设置按钮点击事件
  button.addEventListener("click", extractLanguageAndCode);

  // 添加按钮到 textarea 的父元素中
  textarea.style.position = "relative"; // 设置 textarea 父元素的相对定位
  textarea.parentElement.appendChild(button);
}

const config = { childList: true, subtree: true };
observer.observe(document.body, config);
document.querySelectorAll("textarea").forEach((textarea) => {
  addButtonToTextarea(textarea);
});
// window.addEventListener("load", extractLanguageAndCode);
