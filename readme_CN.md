#

## 概述

chrome插件，可以在浏览器中直接执行和编辑代码。此外，还能保存代码和编辑代码再运行的功能。

## 功能特点

- **运行代码**：执行支持语言的代码片段并显示结果。
- **保存代码**：将代码片段发送到服务器进行存储或进一步处理。
- **编辑代码**：在浏览器中打开模态框以直接编辑代码片段。
- **多语言支持**：检测并支持多种编程语言，包括 Python、JavaScript、HTML、Bash 和 PHP，你可以定制自己的后端来实现。
- **动态 DOM 更新**：自动为动态插入的代码块添加功能。

## 安装步骤

1. 克隆此仓库：
   ```bash
   git clone https://github.com/zazaji/chrome-run-code.git
   ```
2. 进入backend目录，并运行sh run.sh，为了安全起见，建议在docker中运行。
3. 打开 Chrome 并导航到 `chrome://extensions/`。
4. 通过在右上角切换“开发者模式”来启用开发者模式。
5. 点击“加载已解压的扩展程序”，选择插件所在的目录。

## 使用方法

1. 导航到包含代码片段的网页（例如文档或教程）。
2. 插件会自动在代码块旁边添加“run”、“save”和“edit”按钮。
3. 点击“run”以执行代码，结果将显示在代码块下方。
4. 点击“save”以将代码发送到配置的服务器。
5. 点击“edit”以在模态弹出框中修改代码，然后接受更改，更改后的内容在页面上显示，并且可以点击run运行修改后的代码。

## 截图

![截图](images/github.png)

![截图](images/yiyan.jpg)

![截图](images/qwen.jpg)

![截图](images/kimi.png)

![截图](images/graph.jpg)

![截图](images/edit.jpg)

## 配置选项

- 服务器地址可以使用 Chrome 的存储 API 进行配置，默认为 `http://localhost:8000/runcode`。需要与后端服务的token一致。
- 配置服务器进行安全通信的认证令牌。需要与后端服务的token一致。

## 许可证

此项目根据 MIT 许可证。
