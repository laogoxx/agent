#!/bin/bash

# 设置 Python 路径
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# 进入 src 目录
cd /opt/render/project/src

# 初始化数据库（即使失败也继续启动服务）
if [ -f "../scripts/init_db.py" ]; then
    echo "初始化数据库..."
    if python ../scripts/init_db.py init; then
        echo "✓ 数据库初始化成功"
    else
        echo "⚠️  数据库初始化失败，但继续启动服务..."
    fi
fi

# 启动服务 - 直接使用 Python 运行 Flask
echo "启动 OPC Agent 服务..."
python main_flask.py
