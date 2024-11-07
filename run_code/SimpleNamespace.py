from types import SimpleNamespace

# 原始字典
result_dict = {"returncode": 0, "stdout": "Dangeetected.", "stderr": "Dangerousected."}

# 将字典转换为对象
result = SimpleNamespace(**result_dict)

# 检查返回码
if result.returncode == 0:
    print("Command sfully.")
    print("Output:", result.stdout)
else:
    print("Command failed with return code:", result.returncode)
    print("Error message:", result.stderr)