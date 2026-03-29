#!/bin/bash
# 训练服务启动脚本。
#
# 这个文件负责把运行环境准备和服务启动动作串起来。
# 当前逻辑很简单：
# 1. 尝试激活虚拟环境，确保依赖从项目环境中加载
# 2. 统一通过 uvicorn 启动 FastAPI 服务
# 3. 对开发和生产模式使用相同启动路径，便于部署环境保持一致
set -e

app_env=${1:-development}

if [ -f "bin/activate" ]; then
  . bin/activate
fi

run_app() {
  # 这里把真正的服务启动动作收敛到一个函数里，便于后续扩展参数。
  exec uvicorn app:app --host 0.0.0.0 --port 3001
}

if [ "$app_env" = "production" ] || [ "$app_env" = "prod" ]; then
  echo "Production environment detected"
  run_app
else
  echo "Development environment detected"
  run_app
fi
