from flask import Flask, request, jsonify
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.agent import build_agent
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
    # 生产环境：关闭调试模式，使用多线程
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
