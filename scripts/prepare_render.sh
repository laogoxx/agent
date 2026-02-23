#!/bin/bash
# Render 部署准备脚本
# 此脚本会自动准备 Render 部署所需的所有文件

set -e

echo "========================================"
echo "Render 部署准备工具"
echo "========================================"
echo ""

# 检查是否在项目根目录
if [ ! -f "requirements.txt" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 1. 检查 requirements.txt
echo "📝 [1/7] 检查 requirements.txt..."
if ! grep -q "flask" requirements.txt; then
    echo "   添加 Flask 依赖..."
    echo "flask==3.0.0" >> requirements.txt
fi

if ! grep -q "gunicorn" requirements.txt; then
    echo "   添加 Gunicorn 依赖..."
    echo "gunicorn==21.2.0" >> requirements.txt
fi
echo "   ✅ requirements.txt 已更新"

# 2. 创建 Flask 应用入口
echo "📝 [2/7] 创建 Flask 应用入口..."
cat > src/main_flask.py << 'EOF'
from flask import Flask, request, jsonify
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.agent import build_agent
from langgraph.checkpoint.memory import MemorySaver

app = Flask(__name__)

# 初始化 Agent
agent = None
checkpointer = None

def init_agent():
    """初始化 Agent（延迟加载）"""
    global agent, checkpointer
    if agent is None:
        agent = build_agent()
        checkpointer = MemorySaver()
    return agent

@app.route('/')
def index():
    """主页"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OPC 超级个体孵化助手</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                background-color: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
            }
            .status {
                color: #4CAF50;
                font-weight: bold;
            }
            .api-info {
                background-color: #f9f9f9;
                padding: 15px;
                border-radius: 5px;
                margin-top: 20px;
            }
            code {
                background-color: #f0f0f0;
                padding: 2px 5px;
                border-radius: 3px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 OPC 超级个体孵化助手</h1>
            <p class="status">✅ 服务运行正常</p>

            <div class="api-info">
                <h3>📡 API 端点</h3>
                <p><strong>POST /api/chat</strong> - 聊天接口</p>
                <pre><code>curl -X POST /api/chat \\
  -H "Content-Type: application/json" \\
  -d '{"message": "你好，我想做创业"}'</code></pre>

                <p><strong>GET /api/health</strong> - 健康检查</p>
                <pre><code>curl /api/health</code></pre>
            </div>
        </div>
    </body>
    </html>
    """

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口"""
    try:
        data = request.json
        message = data.get('message', '')

        if not message:
            return jsonify({'error': '请提供消息内容'}), 400

        # 初始化 Agent
        current_agent = init_agent()

        # 调用 Agent
        config = {"configurable": {"thread_id": "default"}}
        response = current_agent.invoke({"messages": [message]}, config)

        # 提取回复
        reply = response['messages'][-1].content

        return jsonify({
            'success': True,
            'reply': reply
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'service': 'opc-agent'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
EOF
echo "   ✅ src/main_flask.py 已创建"

# 3. 创建 runtime.txt
echo "📝 [3/7] 创建 runtime.txt..."
echo "python-3.11.8" > runtime.txt
echo "   ✅ runtime.txt 已创建"

# 4. 创建 .render 目录和启动脚本
echo "📝 [4/7] 创建 Render 启动脚本..."
mkdir -p .render

cat > .render/start.sh << 'EOF'
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
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile - src.main_flask:app
EOF

chmod +x .render/start.sh
echo "   ✅ .render/start.sh 已创建"

# 5. 创建 Render 环境变量模板
echo "📝 [5/7] 创建 Render 环境变量模板..."
cat > render_env.txt << 'EOF'
# ========================================
# Render 环境变量配置
# ========================================
# 在 Render 控制台的 Environment 中添加这些变量

# 数据库配置（创建 PostgreSQL 后，将 Internal Database URL 填入）
DATABASE_URL=postgresql://用户名:密码@主机:端口/数据库名

# 微信支付配置
WECHAT_QRCODE_URL=https://ibb.co/0y0jXhCv
WECHAT_GROUP_QRCODE_URL=https://ibb.co/PZrnNCT2

# 产品配置
PAYMENT_PRICE=68.00
PRODUCT_NAME=OPC创业指导PDF

# 模型配置（从你的开发环境获取）
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key_here
COZE_INTEGRATION_MODEL_BASE_URL=your_base_url_here
EOF
echo "   ✅ render_env.txt 已创建"

# 6. 创建 Render 配置文件（render.yaml）
echo "📝 [6/7] 创建 render.yaml..."
cat > render.yaml << 'EOF'
services:
  - type: web
    name: opc-agent
    env: python
    runtime: python-3.11.8
    buildCommand: pip install -r requirements.txt && python scripts/init_db.py init
    startCommand: bash .render/start.sh
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: opc-agent-db
          property: connectionString
      - key: WECHAT_QRCODE_URL
        value: https://ibb.co/0y0jXhCv
      - key: WECHAT_GROUP_QRCODE_URL
        value: https://ibb.co/PZrnNCT2
      - key: PAYMENT_PRICE
        value: 68.00
      - key: PRODUCT_NAME
        value: OPC创业指导PDF
    healthCheckPath: /api/health

databases:
  - name: opc-agent-db
    databaseName: opc_agent
    user: opc_user
EOF
echo "   ✅ render.yaml 已创建"

# 7. 创建 Procfile（传统方式）
echo "📝 [7/7] 创建 Procfile..."
cat > Procfile << 'EOF'
web: bash .render/start.sh
EOF
echo "   ✅ Procfile 已创建"

echo ""
echo "========================================"
echo "✅ Render 部署准备完成！"
echo "========================================"
echo ""
echo "📋 已创建的文件："
echo "   - src/main_flask.py (Flask 应用入口)"
echo "   - runtime.txt (Python 版本)"
echo "   - .render/start.sh (启动脚本)"
echo "   - render_env.txt (环境变量模板)"
echo "   - render.yaml (Render 配置文件)"
echo "   - Procfile (进程配置)"
echo ""
echo "📖 下一步操作："
echo ""
echo "1. 配置环境变量："
echo "   编辑 render_env.txt，填入正确的 API Key 和数据库 URL"
echo ""
echo "2. 提交代码到 GitHub："
echo "   git add ."
echo "   git commit -m '准备 Render 部署'"
echo "   git push"
echo ""
echo "3. 在 Render 上创建项目："
echo "   - 访问 https://dashboard.render.com"
echo "   - 点击 New + → New Blueprint"
echo "   - 选择你的 GitHub 仓库"
echo "   - Render 会自动读取 render.yaml 配置"
echo ""
echo "4. 或者手动创建："
echo "   - 创建 Web Service"
echo "   - 创建 PostgreSQL 数据库"
echo "   - 配置环境变量"
echo ""
echo "📚 详细教程："
echo "   查看 docs/Render部署指南.md"
echo ""
echo "========================================"
