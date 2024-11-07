from fastapi import FastAPI, Header, HTTPException,Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from types import SimpleNamespace
import subprocess
import re
import os
import matplotlib.pyplot as plt
import base64
import time
from io import BytesIO
from typing import List, Union
ALLOWED_TOKEN = "Wh0arey0u"
TIMEOUT_DURATION = 120  # 设置运行子进程超时时间，单位为秒

app = FastAPI()
save_path = "../run_code/"  # 修改为你的保存路径
static_folder='../run_code/'
if not(os.path.exists(save_path)):
    os.mkdir(save_path)
if not(os.path.exists(static_folder)):
    os.mkdir(static_folder)

app.mount("/static", StaticFiles(directory=static_folder), name="static")

languages={"python":"py","css":"css","javascript":"js","html":"html","markdown":"md","json":"json","yaml":"yml","text":"txt","bash":"sh","powershell":"ps1","sql":"sql","c":"c","cpp":"cpp","java":"java","kotlin":"kt","objective-c":"m","swift":"swift","typescript":"ts"}


# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str
    run: bool
    isLocal:bool
    language: str
    token: str

class Output(BaseModel):
    type: str
    data: Union[str, List[str]]  # 可以是字符串或字符串列表



def remove_non_printable_chars(text: str) -> str:
    # 替换不可见字符，但保留回车、汉字、空格等
    rtext = re.sub(r'[^\x20-\x7E\x0A\x0D\u4e00-\u9fff]', '', text)
    return rtext




def save_file_with_directory(path, content):
    # 分离出目录和文件名
    directory, filename = os.path.split(path)

    # 如果目录不为空，则创建所需的所有目录
    if directory:
        os.makedirs(directory, exist_ok=True)

    # 在指定的目录下创建文件并写入内容
    with open(os.path.join(directory, filename), 'w') as file:
        file.write(content)

@app.post("/runcode")  # 添加 token 依赖
async def run_code(code_request: CodeRequest):
    save_path = "../run_code/"  # 修改为你的保存路径

    if code_request.token != ALLOWED_TOKEN:
        return {"outputs": [{"type": "error", "data": "Invalid token"}]}

    outputs: List[Output] = []
    images_count = 0  # 计数生成的图像数量
    print(code_request.isLocal)

    if 1:
    # try:
        # 提取第一行作为文件名
        first_line = code_request.code.splitlines()[0].split(' ')[-1].strip()
        filename = re.sub(r'[^A-Za-z0-9_\\\-\/\.]+', '', first_line)[-100:]
        file_extension = languages.get(code_request.language.lower(), 'py')
        print(file_extension)
        if filename.endswith(file_extension):
            filename = filename[:-len(file_extension)-1]
        if filename.startswith('/') or filename.startswith('~/') :
            save_path=""
        if filename=="":filename="temp/"+str(int(time.time()))
        source_filename = f"{save_path}{filename}.{file_extension}"
        exec_filename = f"{save_path}{filename}.out"
        save_code = code_request.code

        if code_request.isLocal==False and code_request.language == "python" and "matplotlib.pyplot" in code_request.code:
            # 针对 Python 和 Matplotlib 的特殊处理
            code_with_saves = re.sub(
                r'plt.show\(\)',
                lambda match: 'plt.savefig(f"temp_{images_count}.png"); plt.clf(); print(f"[[[temp_{images_count}.png]]]");',
                code_request.code
            )
            save_code = "images_count = 0\noutputs = []\n" + code_with_saves

            # save_code =add_global_images_count(code_request.code)

        if code_request.run == False:
            # 如果 run=False，只保存代码文件不执行、
            save_file_with_directory(source_filename, remove_non_printable_chars(code_request.code))

            return {"outputs": [{"type": "text", "data": f"{source_filename} saved successfully."}]}

        else:
            # 保存代码文件并执行
            save_file_with_directory(source_filename, remove_non_printable_chars(save_code))

            # 根据语言选择执行命令
            if file_extension in ["html","htm",'text','txt']:
                print(code_request.isLocal)
                if  code_request.isLocal:
                    return {"outputs": [{"type": "text", "data":f"<a href='/static/{source_filename}' target='_blank'>Click to view</a>"}]}
                else:
                    return {"outputs": [{"type": "text", "data": code_request.code.replace("<pre","<div").replace("</pre>","</div")}]}
            elif file_extension in ["python","py"]:
                print('file_extension',file_extension)

                result = subprocess.run(['python3', source_filename], capture_output=True, text=True,cwd=save_path, timeout=TIMEOUT_DURATION )
            elif file_extension in ["sh","bash"]:
                print('file_extension')
                print(file_extension)
                if "rm -" in code_request.code:
                    result_dict= {"returncode":0,"stdout":"Dangerous command detected.","stderr":"ERROR."}
                    result=SimpleNamespace(**result_dict)
                else:
                    result = subprocess.run(['sh', source_filename], capture_output=True, text=True,cwd=save_path, timeout=TIMEOUT_DURATION )
            elif file_extension in ["javascript","js"]:
                result = subprocess.run(['node', source_filename], capture_output=True, text=True,cwd=save_path, timeout=TIMEOUT_DURATION )
            elif file_extension == "php":
                result = subprocess.run(['php', source_filename], capture_output=True, text=True,cwd=save_path, timeout=TIMEOUT_DURATION )
            elif file_extension == "c":
                # 使用 gcc 编译 C 代码
                compile_result = subprocess.run(['gcc', source_filename, '-o', exec_filename], capture_output=True, text=True,cwd=save_path, timeout=TIMEOUT_DURATION )
                if compile_result.returncode == 0:
                    result = subprocess.run([exec_filename], capture_output=True, text=True,cwd=save_path, timeout=TIMEOUT_DURATION )
                else:
                    return {"outputs": [{"type": "error", "data": compile_result.stderr}]}
            elif file_extension == "cpp":
                # 使用 g++ 编译 C++ 代码
                compile_result = subprocess.run(['g++', source_filename, '-o', exec_filename], capture_output=True, text=True,cwd=save_path, timeout=TIMEOUT_DURATION )
                if compile_result.returncode == 0:
                    result = subprocess.run([exec_filename], capture_output=True, text=True,cwd=save_path, timeout=TIMEOUT_DURATION )
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

                print(new_outputs)
                return {"outputs": [output.dict() for output in new_outputs]}
            else:
                # 如果执行失败，可以返回错误信息
                return {"outputs": [{"type": "error", "data": result.stderr}]}

    # except Exception as e:
    #     return {"outputs": [{"type": "error", "data": str(e)}]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
