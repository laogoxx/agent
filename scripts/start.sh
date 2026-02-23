#!/bin/bash

# OPC Agent 本地启动脚本

echo "=========================================="
echo "     OPC Agent 本地启动"
echo "=========================================="
echo ""

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "❌ 错误：未找到 .env 文件"
    echo "请先复制 .env.example 为 .env 并配置"
    echo "命令：cp .env.example .env"
    echo "然后编辑：nano .env"
    exit 1
fi

# 检查Python版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到 Python3"
    echo "请先安装 Python 3.10+"
    exit 1
fi

# 检查依赖
if ! pip3 show langchain &> /dev/null; then
    echo "⚠️  警告：依赖可能未安装"
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 获取端口号
PORT=${1:-8080}

echo "🚀 启动 OPC Agent..."
echo "端口：$PORT"
echo "访问地址：http://localhost:$PORT"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""
echo "=========================================="
echo ""

# 启动服务
python3 src/main.py -m http -p $PORT
