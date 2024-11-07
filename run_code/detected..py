result = {"returncode": 0, "stdout": "Dangerous command detected.", "stderr": "Dangerous command detected."}

if result["returncode"] == 0:
    print("Command executed successfully.")
else:
    print("Command failed with return code:", result["returncode"])
    print("Error message:", result["stderr"])