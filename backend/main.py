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
import platform
from  hashlib import md5
from config import *

app = FastAPI()


if not(os.path.exists(SAVE_PATH)):
    os.mkdir(SAVE_PATH)
if not(os.path.exists(os.path.join(SAVE_PATH,TEMP_FOLDER))):
    os.mkdir(os.path.join(SAVE_PATH,TEMP_FOLDER))

app.mount("/static", StaticFiles(directory=SAVE_PATH), name="static")


languages={"vue":"vue","python":"py","py":"py","css":"css","javascript":"js","js":"js","html":"html","markdown":"md","json":"json","yaml":"yml","text":"txt","bash":"sh","sh":"sh","shell":"sh","bat":"cmd","cmd":"cmd","powershell":"cmd","sql":"sql","c":"c","cpp":"cpp","java":"java","kotlin":"kt","objective-c":"m","swift":"swift","typescript":"ts"}
error_pyfilenames=['','pygame','os', 're', 'sys', 'time', 'subprocess', 'platform', 'os', 're', 'time', 'subprocess', 'platform', 'numpy', 'pandas', 'matplotlib', 'PIL', 'cv2', 'torch', 'tensorflow', 'keras', 'sklearn', 'scipy', 'seaborn', 'nltk', 'jieba', 'wordcloud', 'plotly', 'base64', 'io',
        'json', 'yaml', 'csv', 'random', 'math', 'datetime', 'shutil', 'glob', 'argparse', 'logging', 'functools', 'itertools', 'collections', 'operator', 'statistics', 'string', 're', 'urllib', 'http', 'socket', 'ssl', 'hashlib']
# print(languages.get("html".lower(), 'py'))

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 保存路径和支持语言的映射


class CodeRequest(BaseModel):
    code: str
    run: bool
    isLocal:bool
    language: str  # 添加语言字段
    token: str

class Output(BaseModel):
    type: str
    data: Union[str, List[str]]  # 可以是字符串或字符串列表



def remove_non_printable_chars(text: str) -> str:
    # 替换不可见字符，但保留回车、汉字、空格等
    rtext = re.sub(r'[^\x20-\x7E\x0A\x0D\u4e00-\u9fff]', '', text)
    return rtext


def get_file_extension():
    if platform.system() == 'Windows':
        return "cmd"
    else:
        return "sh"

def save_file_with_directory(path, content):
    # 分离出目录和文件名
    directory, filename = os.path.split(path)

    # 如果目录不为空，则创建所需的所有目录
    if directory:
        os.makedirs(directory, exist_ok=True)

    # 在指定的目录下创建文件并写入内容
    with open(os.path.join(directory, filename), 'w',encoding='utf-8') as file:
        file.write(content)

def get_filename_from_code(save_code,file_extension):
    first_line = save_code.splitlines()[0]
    if first_line.startswith("import ") or first_line.startswith("from "):
        filename = TEMP_FOLDER + md5(save_code.encode('utf-8')).hexdigest()[:8]
    elif first_line.startswith("<!DOCTYPE") and file_extension=="html":
        filename = ""
    # elif first_line.startswith("/*") and file_extension=="css":
    #     filename = ""
    else:
        if file_extension in ['html','vue']:first_line=first_line.replace("<!--","").replace("-->","")
        print('sssss',file_extension,first_line.strip())
        filename = re.sub(r'[^A-Za-z0-9_\\\-\/\.]+', '', first_line.strip().split(' ')[-1])[-100:]
        if filename.endswith(file_extension):
            filename = filename[:-len(file_extension)-1]

    if filename.split("/")[-1]=="" or (filename.split("/")[-1] in error_pyfilenames and file_extension!="py"):
        filename=TEMP_FOLDER+md5(save_code.encode('utf-8')).hexdigest()[:8]
    print(first_line,filename)
    return filename

def replace_show_plot(code):
    # 针对 Python 和 Matplotlib 的特殊处理
    code_with_saves = re.sub(
        r'plt.show\(\)',
        lambda match: 'plt.savefig(f"temp_{images_count}.png"); plt.clf(); print(f"[[[temp_{images_count}.png]]]");',
        code
    )
    save_code= "images_count = 0\noutputs = []\n" + code_with_saves
    # save_code =add_global_images_count(code_request.code)
    return save_code

def replace_base64_images(outputs):
    # 检查占位符并替换为 Base64 图像
    new_outputs = []
    for output in outputs:
        if isinstance(output.data, str):
            if "[[[" in output.data:
                # 如果是图片，将其转换为 Base64 编码并添加到 outputs
                img_filename = os.path.join(SAVE_PATH, output.data.replace("[[[", "").replace("]]]", ""))
                if os.path.exists(img_filename):
                    # 将图像转换为 Base64 编码
                    with open(img_filename, "rb") as img_file:
                        base64_image = base64.b64encode(img_file.read()).decode('utf-8')
                        image_output = f"data:image/png;base64,{base64_image}"
                        output = Output(type="image", data=image_output)
        new_outputs.append(output)
    return new_outputs

@app.post("/runcode")  # 添加 token 依赖
async def run_code(code_request: CodeRequest):
    if code_request.token != ALLOWED_TOKEN:
        return {"outputs": [{"type": "error", "data": "Invalid token"}]}

    global SAVE_PATH
    global TEMP_FOLDER
    outputs: List[Output] = []
    images_count = 0  # 计数生成的图像数量
    # print(code_request.isLocal)

    if 1:
    # try:
        print(code_request.language)
        file_extension = languages.get(code_request.language.lower(), 'py')
        if file_extension=="sh":
            file_extension=get_file_extension()
        save_code = code_request.code
        # print(file_extension)
        filename=get_filename_from_code(save_code,file_extension)

        source_filename = os.path.join(SAVE_PATH,f"{filename}.{file_extension}")
        print(source_filename)
        exec_filename = os.path.join(SAVE_PATH,f"{filename}.out")

        if code_request.isLocal==False and code_request.language == "python" and "matplotlib.pyplot" in save_code:
            save_code=replace_show_plot(save_code)
            # print(save_code)

        if code_request.run == False:
            # 如果 run=False，只保存代码文件不执行
            save_file_with_directory(source_filename, remove_non_printable_chars(code_request.code))

            return {"outputs": [{"type": "text", "data": f"{source_filename} saved successfully."}]}

        else:
            # 保存代码文件并执行
            save_file_with_directory(source_filename, remove_non_printable_chars(save_code))

            # 根据语言选择执行命令
            if file_extension in ["html","htm",'text','txt']:
                print(code_request.isLocal)
                if  code_request.isLocal:
                    print(source_filename)
                    source_filename=source_filename.replace("../runcode/","").replace(SAVE_PATH,"")

                    return {"outputs": [{"type": "text", "data":f"<a href='/static/{source_filename}' target='_blank'>Click to view</a>"}]}
                else:
                    return {"outputs": [{"type": "text", "data": code_request.code.replace("<pre","<div").replace("</pre>","</div")}]}
            elif file_extension in ["python","py"]:
                result = subprocess.run(['python', source_filename], capture_output=True, text=True,cwd=SAVE_PATH, timeout=TIMEOUT_DURATION )
            elif file_extension=="sh":
                if "rm -" in code_request.code:
                    result= {"returncode":0,"stdout":"Dangerous command detected.","stderr":"Dangerous command detected."}
                    result=SimpleNamespace(**result)
                else:
                    result = subprocess.run(['sh', source_filename], capture_output=True, text=True,cwd=SAVE_PATH, timeout=TIMEOUT_DURATION )
            elif file_extension=="cmd":
                if "del-" in code_request.code:
                    result= {"returncode":0,"stdout":"Dangerous command detected.","stderr":"Dangerous command detected."}
                    result=SimpleNamespace(**result)
                else:
                    result = subprocess.run(['cmd','/c', source_filename], capture_output=True, text=True,cwd=SAVE_PATH, timeout=TIMEOUT_DURATION )


            elif file_extension in ["ts","js"]:
                result = subprocess.run(['node', source_filename], capture_output=True, text=True,cwd=SAVE_PATH, timeout=TIMEOUT_DURATION )
            elif file_extension == "php":
                result = subprocess.run(['php', source_filename], capture_output=True, text=True,cwd=SAVE_PATH, timeout=TIMEOUT_DURATION )
            elif file_extension == "c":
                # 使用 gcc 编译 C 代码
                compile_result = subprocess.run(['gcc', source_filename, '-o', exec_filename], capture_output=True, text=True,cwd=SAVE_PATH, timeout=TIMEOUT_DURATION )
                if compile_result.returncode == 0:
                    result = subprocess.run([exec_filename], capture_output=True, text=True,cwd=SAVE_PATH, timeout=TIMEOUT_DURATION )
                else:
                    return {"outputs": [{"type": "error", "data": compile_result.stderr}]}
            elif file_extension == "cpp":
                # 使用 g++ 编译 C++ 代码
                compile_result = subprocess.run(['g++', source_filename, '-o', exec_filename], capture_output=True, text=True,cwd=SAVE_PATH, timeout=TIMEOUT_DURATION )
                if compile_result.returncode == 0:
                    result = subprocess.run([exec_filename], capture_output=True, text=True,cwd=SAVE_PATH, timeout=TIMEOUT_DURATION )
                else:
                    return {"outputs": [{"type": "error", "data": compile_result.stderr}]}
            else:
                return {"outputs": [{"type": "error", "data": "Unsupported language."}]}

            if result.returncode == 0:
                # 解析标准输出并添加到 outputs
                stdout_lines = result.stdout.strip().splitlines()
                for line in stdout_lines:
                    outputs.append(Output(type="text", data=line))
                new_outputs=replace_base64_images(outputs)
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
