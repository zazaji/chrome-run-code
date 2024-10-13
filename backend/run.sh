#!/bin/bash
# 请先安装 uvicorn等依赖
#pip install uvicorn fastapi pydantic matplotlib，以及后面会用到的
uvicorn main:app --host 0.0.0.0 --port 8000
