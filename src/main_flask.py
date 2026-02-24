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
    """主页 - 聊天界面"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OPC 超级个体孵化助手</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .chat-container {
                width: 100%;
                max-width: 800px;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
                display: flex;
                flex-direction: column;
                height: 90vh;
                max-height: 800px;
            }
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px 25px;
                display: flex;
                align-items: center;
                gap: 15px;
            }
            .chat-header h1 {
                font-size: 24px;
                font-weight: 600;
            }
            .chat-header .status {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 14px;
                opacity: 0.9;
            }
            .chat-header .status-dot {
                width: 10px;
                height: 10px;
                background: #4CAF50;
                border-radius: 50%;
                animation: pulse 2s infinite;
            }
            @keyframes pulse {
                0%, 100% { opacity: 1; }
                50% { opacity: 0.5; }
            }
            .chat-messages {
                flex: 1;
                overflow-y: auto;
                padding: 25px;
                background: #f8f9fa;
            }
            .message {
                display: flex;
                margin-bottom: 20px;
                animation: fadeIn 0.3s ease-in;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .message.user {
                justify-content: flex-end;
            }
            .message.assistant {
                justify-content: flex-start;
            }
            .message-bubble {
                max-width: 70%;
                padding: 15px 20px;
                border-radius: 20px;
                line-height: 1.6;
                word-wrap: break-word;
            }
            .message.user .message-bubble {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-bottom-right-radius: 5px;
            }
            .message.assistant .message-bubble {
                background: white;
                color: #333;
                border: 2px solid #e9ecef;
                border-bottom-left-radius: 5px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }
            .message-bubble pre {
                background: #2d2d2d;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 8px;
                overflow-x: auto;
                margin: 10px 0;
                font-size: 14px;
            }
            .message-bubble code {
                background: #f4f4f4;
                color: #d63384;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 14px;
            }
            .chat-input-area {
                padding: 20px 25px;
                background: white;
                border-top: 2px solid #e9ecef;
            }
            .chat-input-wrapper {
                display: flex;
                gap: 12px;
                align-items: flex-end;
            }
            .chat-input {
                flex: 1;
                padding: 15px 20px;
                border: 2px solid #e9ecef;
                border-radius: 25px;
                font-size: 16px;
                font-family: inherit;
                resize: none;
                outline: none;
                transition: border-color 0.3s;
                min-height: 52px;
                max-height: 150px;
            }
            .chat-input:focus {
                border-color: #667eea;
            }
            .send-button {
                width: 52px;
                height: 52px;
                border: none;
                border-radius: 50%;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                font-size: 20px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .send-button:hover {
                transform: scale(1.05);
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            }
            .send-button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            .typing-indicator {
                display: none;
                padding: 15px 20px;
                margin-bottom: 20px;
                background: white;
                border-radius: 20px;
                border-bottom-left-radius: 5px;
                border: 2px solid #e9ecef;
                width: fit-content;
            }
            .typing-indicator.active {
                display: block;
            }
            .typing-indicator span {
                display: inline-block;
                width: 8px;
                height: 8px;
                background: #667eea;
                border-radius: 50%;
                margin: 0 3px;
                animation: typing 1.4s infinite ease-in-out;
            }
            .typing-indicator span:nth-child(1) { animation-delay: 0s; }
            .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
            .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
            @keyframes typing {
                0%, 60%, 100% { transform: translateY(0); }
                30% { transform: translateY(-10px); }
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h1>🚀 OPC 超级个体孵化助手</h1>
                <div class="status">
                    <div class="status-dot"></div>
                    <span>在线</span>
                </div>
            </div>

            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    <div class="message-bubble">
                        🔥 2025年，你是否也有这样的焦虑？<br><br>
                        ❌ 35岁职场危机越来越近，裁员潮一波接一波<br>
                        ❌ 工资涨幅跑不赢通胀，存款缩水<br>
                        ❌ 每天加班到深夜，却看不到未来<br>
                        ❌ 想改变，但不知道从哪里开始<br>
                        ❌ 看着别人副业月入过万，自己却毫无头绪<br><br>
                        ---<br><br>
                        🚀 但你有没有发现，身边越来越多的人开始做OPC（超级个体）？<br><br>
                        <strong>这些真实案例就在你身边：</strong><br>
                        - 小张，30岁，程序员 → AI提示词工程师，月收入3万+<br>
                        - 小李，28岁，财务 → 自媒体账号，粉丝10万，月广告收入2万<br>
                        - 小王，35岁，传统销售 → 个人IP打造，年入50万+<br>
                        - 小陈，32岁，普通宝妈 → 在线课程，月收入1.5万<br><br>
                        <strong>这，就是OPC创业的红利！</strong><br><br>
                        ---<br><br>
                        🎯 为什么现在是OPC创业的黄金时期？<br><br>
                        ✅ <strong>技术门槛降低</strong>：AI工具让一个人可以干10个人的活<br>
                        ✅ <strong>市场碎片化</strong>：小众需求爆发，精准变现更容易<br>
                        ✅ <strong>平台红利期</strong>：短视频、知识付费、直播带货流量巨大<br>
                        ✅ <strong>成本低风险小</strong>：轻资产运营，试错成本极低<br>
                        ✅ <strong>收入不封顶</strong>：没有职场天花板，完全看你的能力<br><br>
                        ---<br><br>
                        💡 <strong>我是谁？为什么能帮你？</strong><br><br>
                        我是你的OPC超级个体孵化助手。<br><br>
                        我由<strong>超过10年创业经验的产品经理</strong>打造而来，深度研究了<strong>100个OPC成功案例</strong>，覆盖了IT、内容创作、电商、咨询、教育等20+个领域。<br><br>
                        我会<strong>深度分析你的个人特点</strong>：<br>
                        - 你的专业技能如何转化为创业优势<br>
                        - 你所在城市的商业机会和竞争格局<br>
                        - 适合你的创业赛道和变现模式<br>
                        - 从0到1的详细执行路径<br><br>
                        ---<br><br>
                        🤔 <strong>想不想知道：</strong><br><br>
                        1️⃣ 以你的技能和经验，最适合做什么OPC项目？<br>
                        2️⃣ 你所在的城市，有哪些未被发现的商业机会？<br>
                        3️⃣ 如何在3个月内，从0开始实现月入过万？<br>
                        4️⃣ 具体需要准备什么？有哪些坑要避开？<br><br>
                        <strong>别再焦虑了，行动起来！</strong><br><br>
                        告诉我：<br>
                        - 📍 <strong>你在哪个城市？</strong><br>
                        - 💼 <strong>你会什么技能？</strong><br>
                        - 🎯 <strong>你想通过OPC解决什么问题？</strong><br><br>
                        我会为你量身定制创业方案，并对接资源孵化群，全程陪伴你从0到1！<br><br>
                        ---<br><br>
                        💬 <strong>现在就开始吧，告诉我你的情况，我们一起开启你的OPC创业之旅！</strong>
                    </div>
                </div>
            </div>

            <div class="typing-indicator" id="typingIndicator">
                <span></span>
                <span></span>
                <span></span>
            </div>

            <div class="chat-input-area">
                <div class="chat-input-wrapper">
                    <textarea
                        class="chat-input"
                        id="messageInput"
                        placeholder="输入你的消息..."
                        rows="1"
                        onkeydown="handleKeyDown(event)"
                    ></textarea>
                    <button class="send-button" id="sendButton" onclick="sendMessage()">
                        ➤
                    </button>
                </div>
            </div>
        </div>

        <script>
            const chatMessages = document.getElementById('chatMessages');
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const typingIndicator = document.getElementById('typingIndicator');

            function addMessage(content, isUser) {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message ' + (isUser ? 'user' : 'assistant');
                
                const bubble = document.createElement('div');
                bubble.className = 'message-bubble';
                bubble.innerHTML = content.replace(/\\n/g, '<br>');
                
                messageDiv.appendChild(bubble);
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function showTyping() {
                typingIndicator.classList.add('active');
                chatMessages.appendChild(typingIndicator);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            function hideTyping() {
                typingIndicator.classList.remove('active');
            }

            async function sendMessage() {
                const message = messageInput.value.trim();
                if (!message) return;

                // 添加用户消息
                addMessage(message, true);
                messageInput.value = '';
                messageInput.style.height = '52px';

                // 显示输入指示器
                showTyping();
                sendButton.disabled = true;

                try {
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });

                    const data = await response.json();
                    
                    hideTyping();

                    if (data.success) {
                        addMessage(data.reply, false);
                    } else {
                        addMessage('抱歉，发生了错误：' + data.error, false);
                    }
                } catch (error) {
                    hideTyping();
                    addMessage('抱歉，连接服务器时发生了错误。', false);
                } finally {
                    sendButton.disabled = false;
                    messageInput.focus();
                }
            }

            function handleKeyDown(event) {
                if (event.key === 'Enter' && !event.shiftKey) {
                    event.preventDefault();
                    sendMessage();
                }
            }

            // 自动调整输入框高度
            messageInput.addEventListener('input', function() {
                this.style.height = '52px';
                this.style.height = Math.min(this.scrollHeight, 150) + 'px';
            });
        </script>
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
