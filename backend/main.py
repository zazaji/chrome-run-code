from fastapi import FastAPI, Header, HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import subprocess
import re
import os
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from typing import List, Union
save_path='./'
ALLOWED_TOKEN = "your-token-here"

app = FastAPI()
languages={"python":"py","css":"css","javascript":"js","html":"html","markdown":"md","json":"json","yaml":"yml","text":"txt","bash":"sh","powershell":"ps1","sql":"sql","c":"c","cpp":"cpp","java":"java","kotlin":"kt","objective-c":"m","swift":"swift","typescript":"ts"}


# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 保存路径和支持语言的映射
languages = {
    "python": "py",
    "py": "py",
    "js": "js",
    "bash": "sh",
    "sh": "sh",
    "javascript": "js",
    "typescript": "ts",
    "php": "php"
}

class CodeRequest(BaseModel):
    code: str
    run: bool
    language: str  # 添加语言字段
    token: str

class Output(BaseModel):
    type: str
    data: Union[str, List[str]]  # 可以是字符串或字符串列表



def remove_non_printable_chars(text: str) -> str:
    # 替换不可见字符，但保留回车、汉字、空格等
    rtext = re.sub(r'[^\x20-\x7E\x0A\x0D\u4e00-\u9fff]', '', text)
    return rtext

@app.post("/runcode")  # 添加 token 依赖
async def run_code(code_request: CodeRequest):
    if code_request.token != ALLOWED_TOKEN:
        return {"outputs": [{"type": "error", "data": "Invalid token"}]}

    outputs: List[Output] = []
    images_count = 0  # 计数生成的图像数量

    try:
        # 提取第一行作为文件名
        first_line = code_request.code.splitlines()[0].split(' ')[-1].strip()
        filename = re.sub(r'[^A-Za-z0-9_.-]+', '_', first_line)[-20:]
        file_extension = languages.get(code_request.language.lower(), 'py')
        if filename.endswith(file_extension):
            filename = filename[:-len(file_extension)]
        source_filename = f"{save_path}{filename}.{file_extension}"
        exec_filename = f"{save_path}{filename}.out"
        save_code = code_request.code

        if code_request.language == "python" and "matplotlib.pyplot" in code_request.code:
            # 针对 Python 和 Matplotlib 的特殊处理
            code_with_saves = re.sub(
                r'plt.show\(\)',
                lambda match: 'plt.savefig(f"temp_{images_count}.png"); plt.clf(); print(f"[[[temp_{images_count}.png]]]");images_count+=1',
                code_request.code
            )
            save_code = "images_count = 0\noutputs = []\n" + code_with_saves

        if code_request.run == False:
            # 如果 run=False，只保存代码文件不执行
            with open(source_filename, 'w') as f:
                f.write(remove_non_printable_chars(code_request.code))
            return {"outputs": [{"type": "text", "data": f"{source_filename} saved successfully."}]}

        else:
            # 保存代码文件并执行
            with open(source_filename, 'w') as f:
                f.write(remove_non_printable_chars(save_code))

            # 根据语言选择执行命令
            if code_request.language in ["html","htm",'text','txt']:
                return {"outputs": [{"type": "text", "data": code_request.code.replace("<pre","<div").replace("</pre>","</div")}]}
            elif code_request.language in ["python","py"]:
                result = subprocess.run(['python3', source_filename], capture_output=True, text=True, cwd=save_path)
            elif code_request.language in ["sh","bash"]:
                result = subprocess.run(['sh', source_filename], capture_output=True, text=True, cwd=save_path)
            elif code_request.language in ["javascript","js"]:
                result = subprocess.run(['node', source_filename], capture_output=True, text=True, cwd=save_path)
            elif code_request.language == "php":
                result = subprocess.run(['php', source_filename], capture_output=True, text=True, cwd=save_path)
            elif code_request.language == "c":
                # 使用 gcc 编译 C 代码
                compile_result = subprocess.run(['gcc', source_filename, '-o', exec_filename], capture_output=True, text=True, cwd=save_path)
                if compile_result.returncode == 0:
                    result = subprocess.run([exec_filename], capture_output=True, text=True, cwd=save_path)
                else:
                    return {"outputs": [{"type": "error", "data": compile_result.stderr}]}
            elif code_request.language == "cpp":
                # 使用 g++ 编译 C++ 代码
                compile_result = subprocess.run(['g++', source_filename, '-o', exec_filename], capture_output=True, text=True, cwd=save_path)
                if compile_result.returncode == 0:
                    result = subprocess.run([exec_filename], capture_output=True, text=True, cwd=save_path)
                else:
                    return {"outputs": [{"type": "error", "data": compile_result.stderr}]}
            else:
                return {"outputs": [{"type": "error", "data": "Unsupported language."}]}

            if result.returncode == 0:
                # 解析标准输出并添加到 outputs
                stdout_lines = result.stdout.strip().splitlines()
                for line in stdout_lines:
                    outputs.append(Output(type="text", data=line))

                # 检查占位符并替换为 Base64 图像
                new_outputs = []
                for output in outputs:
                    if isinstance(output.data, str):
                        if "[[[" in output.data:
                            # 如果是图片，将其转换为 Base64 编码并添加到 outputs
                            img_filename = save_path + output.data.replace("[[[", "").replace("]]]", "")
                            if os.path.exists(img_filename):
                                # 将图像转换为 Base64 编码
                                with open(img_filename, "rb") as img_file:
                                    base64_image = base64.b64encode(img_file.read()).decode('utf-8')
                                    image_output = f"data:image/png;base64,{base64_image}"
                                    output = Output(type="image", data=image_output)
                    new_outputs.append(output)

                return {"outputs": [output.dict() for output in new_outputs]}
            else:
                # 如果执行失败，可以返回错误信息
                return {"outputs": [{"type": "error", "data": result.stderr}]}

    except Exception as e:
        return {"outputs": [{"type": "error", "data": str(e)}]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
