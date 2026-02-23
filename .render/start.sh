#!/bin/bash

# 设置 Python 路径
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# 进入项目根目录
cd /opt/render/project

# 初始化数据库（即使失败也继续启动服务）
if [ -f "scripts/init_db.py" ]; then
    echo "初始化数据库..."
    if python scripts/init_db.py init; then
        echo "✓ 数据库初始化成功"
    else
        echo "⚠️  数据库初始化失败，但继续启动服务..."
    fi
fi

# 启动服务
echo "启动 OPC Agent 服务..."
# 使用 python -m 方式启动 gunicorn，避免模块导入问题
python -m gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - src.main_flask:app
