#!/bin/bash
# 测试 Flask 应用
# 在本地运行 Flask 应用进行测试

set -e

echo "========================================"
echo "Flask 应用测试工具"
echo "========================================"
echo ""

# 检查是否在项目根目录
if [ ! -f "src/main_flask.py" ]; then
    echo "❌ 错误: 未找到 src/main_flask.py"
    echo "请先运行: bash scripts/prepare_render.sh"
    exit 1
fi

# 设置环境变量
export PYTHONPATH=/workspace/projects:$PYTHONPATH
export PORT=5000

# 启动 Flask 应用
echo "🚀 启动 Flask 应用..."
echo "   - 端口: 5000"
echo "   - 健康检查: http://localhost:5000/api/health"
echo ""

# 后台启动 Flask 应用
python -m flask --app src.main_flask:app run --host=0.0.0.0 --port=5000 &
FLASK_PID=$!

# 等待应用启动
echo "⏳ 等待应用启动..."
sleep 5

# 测试健康检查
echo ""
echo "📋 测试健康检查..."
HEALTH_RESPONSE=$(curl -s http://localhost:5000/api/health)
echo "   响应: $HEALTH_RESPONSE"

if [ "$HEALTH_RESPONSE" == '{"status": "ok", "service": "opc-agent"}' ]; then
    echo "   ✅ 健康检查通过"
else
    echo "   ❌ 健康检查失败"
    kill $FLASK_PID
    exit 1
fi

# 测试聊天接口
echo ""
echo "📋 测试聊天接口..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}')

echo "   响应: $CHAT_RESPONSE"

if echo "$CHAT_RESPONSE" | grep -q "success"; then
    echo "   ✅ 聊天接口正常"
else
    echo "   ❌ 聊天接口失败"
    kill $FLASK_PID
    exit 1
fi

echo ""
echo "========================================"
echo "✅ Flask 应用测试通过！"
echo "========================================"
echo ""
echo "📝 测试结果："
echo "   - 健康检查: ✅"
echo "   - 聊天接口: ✅"
echo ""
echo "🌐 访问地址："
echo "   - 主页: http://localhost:5000"
echo "   - API: http://localhost:5000/api/health"
echo ""
echo "⏹️  停止服务: Ctrl+C 或 kill $FLASK_PID"
echo ""
echo "========================================"

# 保持服务运行
echo "⏳ 服务运行中... (按 Ctrl+C 停止)"
wait $FLASK_PID
