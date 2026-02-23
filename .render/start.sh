#!/bin/bash
set -e

# 设置 Python 路径
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# 初始化数据库（如果需要）
if [ -f "scripts/init_db.py" ]; then
    echo "初始化数据库..."
    python scripts/init_db.py init
fi

# 启动服务
echo "启动 OPC Agent 服务..."
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - main_flask:app
