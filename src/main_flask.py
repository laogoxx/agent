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
            .share-button {
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
                white-space: nowrap;
            }
            .share-button:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: scale(1.05);
            }
            .success-cases-carousel {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 15px;
                overflow: hidden;
            }
            .carousel-container {
                position: relative;
            }
            .carousel-track {
                display: flex;
                transition: transform 0.5s ease-in-out;
            }
            .carousel-item {
                min-width: 100%;
                padding: 0 10px;
            }
            .carousel-card {
                background: white;
                border-radius: 12px;
                padding: 20px;
                color: #333;
            }
            .carousel-card h3 {
                margin-bottom: 10px;
                color: #667eea;
                font-size: 18px;
            }
            .carousel-card .case-info {
                display: flex;
                gap: 20px;
                margin-bottom: 15px;
            }
            .carousel-card .case-info span {
                background: #f0f0f0;
                padding: 5px 12px;
                border-radius: 15px;
                font-size: 13px;
            }
            .carousel-card .highlight {
                background: #fff3cd;
                color: #856404;
                padding: 10px;
                border-radius: 8px;
                margin-bottom: 10px;
                font-weight: 600;
            }
            .carousel-controls {
                display: flex;
                justify-content: center;
                gap: 10px;
                margin-top: 15px;
            }
            .carousel-btn {
                background: rgba(255, 255, 255, 0.3);
                border: none;
                color: white;
                width: 36px;
                height: 36px;
                border-radius: 50%;
                cursor: pointer;
                font-size: 16px;
                transition: all 0.3s;
            }
            .carousel-btn:hover {
                background: rgba(255, 255, 255, 0.5);
                transform: scale(1.1);
            }
            .carousel-indicators {
                display: flex;
                justify-content: center;
                gap: 8px;
                margin-top: 10px;
            }
            .indicator {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.4);
                cursor: pointer;
                transition: all 0.3s;
            }
            .indicator.active {
                background: white;
                transform: scale(1.2);
            }
            .guide-tips {
                background: #e7f3ff;
                border-left: 4px solid #2196F3;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 8px;
            }
            .guide-tips h4 {
                color: #1976D2;
                margin-bottom: 10px;
                font-size: 15px;
            }
            .guide-tips ul {
                margin: 0;
                padding-left: 20px;
            }
            .guide-tips li {
                color: #0d47a1;
                margin-bottom: 5px;
                font-size: 14px;
            }
            .modal-overlay {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.5);
                z-index: 1000;
                align-items: center;
                justify-content: center;
            }
            .modal-overlay.active {
                display: flex;
            }
            .modal-content {
                background: white;
                border-radius: 20px;
                padding: 30px;
                max-width: 500px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
            }
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            .modal-header h2 {
                margin: 0;
                color: #333;
                font-size: 20px;
            }
            .modal-close {
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                color: #999;
            }
            .modal-close:hover {
                color: #333;
            }
            .share-poster {
                margin-bottom: 20px;
            }
            .share-poster img {
                width: 100%;
                border-radius: 10px;
            }
            .share-actions {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .share-btn {
                padding: 12px 20px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
            }
            .share-btn.wechat {
                background: #07c160;
                color: white;
            }
            .share-btn.moment {
                background: #07c160;
                color: white;
            }
            .share-btn.copy {
                background: #f0f0f0;
                color: #333;
            }
            .share-btn:hover {
                opacity: 0.9;
                transform: scale(1.02);
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
                <button class="share-button" onclick="openShareModal()">
                    📤 分享
                </button>
            </div>

            <div class="chat-messages" id="chatMessages">
                <!-- 引导提示 -->
                <div class="guide-tips">
                    <h4>💡 快速开始</h4>
                    <ul>
                        <li>告诉我你的城市、技能和经验，我会为你定制创业方案</li>
                        <li>查看成功案例轮播，了解其他人如何实现月入过万</li>
                        <li>点击右上角分享按钮，推荐给有需要的朋友</li>
                    </ul>
                </div>

                <!-- 成功案例轮播 -->
                <div class="success-cases-carousel">
                    <div class="carousel-container">
                        <div class="carousel-track" id="carouselTrack">
                            <div class="carousel-item">
                                <div class="carousel-card">
                                    <h3>🎯 小张 - AI提示词工程师</h3>
                                    <div class="case-info">
                                        <span>30岁</span>
                                        <span>北京</span>
                                        <span>程序员转型</span>
                                    </div>
                                    <div class="highlight">✨ 薪资翻3倍，月收入3万+</div>
                                    <p>从程序员转型，利用AI工具帮助企业优化工作流程</p>
                                </div>
                            </div>
                            <div class="carousel-item">
                                <div class="carousel-card">
                                    <h3>🎯 小李 - 自媒体达人</h3>
                                    <div class="case-info">
                                        <span>28岁</span>
                                        <span>上海</span>
                                        <span>财务转型</span>
                                    </div>
                                    <div class="highlight">✨ 从0到10万粉丝，月广告收入2万</div>
                                    <p>分享职场干货，快速积累粉丝，实现副业变现</p>
                                </div>
                            </div>
                            <div class="carousel-item">
                                <div class="carousel-card">
                                    <h3>🎯 小王 - 个人IP打造</h3>
                                    <div class="case-info">
                                        <span>35岁</span>
                                        <span>深圳</span>
                                        <span>销售转型</span>
                                    </div>
                                    <div class="highlight">✨ 成功转型创业，年入50万+</div>
                                    <p>通过短视频打造个人品牌，转型为商业顾问</p>
                                </div>
                            </div>
                            <div class="carousel-item">
                                <div class="carousel-card">
                                    <h3>🎯 小陈 - 在线课程</h3>
                                    <div class="case-info">
                                        <span>32岁</span>
                                        <span>杭州</span>
                                        <span>宝妈创业</span>
                                    </div>
                                    <div class="highlight">✨ 副业超过主业，月收入1.5万</div>
                                    <p>将育儿经验转化为在线课程，帮助更多宝妈</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="carousel-controls">
                        <button class="carousel-btn" onclick="prevSlide()">◀</button>
                        <button class="carousel-btn" onclick="nextSlide()">▶</button>
                    </div>
                    <div class="carousel-indicators" id="carouselIndicators">
                        <div class="indicator active" onclick="goToSlide(0)"></div>
                        <div class="indicator" onclick="goToSlide(1)"></div>
                        <div class="indicator" onclick="goToSlide(2)"></div>
                        <div class="indicator" onclick="goToSlide(3)"></div>
                    </div>
                </div>

                <!-- 欢迎消息 -->
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

            // 轮播功能
            let currentSlide = 0;
            const totalSlides = 4;
            const track = document.getElementById('carouselTrack');
            const indicators = document.querySelectorAll('.indicator');

            function updateCarousel() {
                track.style.transform = `translateX(-${currentSlide * 100}%)`;
                indicators.forEach((ind, index) => {
                    ind.classList.toggle('active', index === currentSlide);
                });
            }

            function nextSlide() {
                currentSlide = (currentSlide + 1) % totalSlides;
                updateCarousel();
            }

            function prevSlide() {
                currentSlide = (currentSlide - 1 + totalSlides) % totalSlides;
                updateCarousel();
            }

            function goToSlide(index) {
                currentSlide = index;
                updateCarousel();
            }

            // 自动轮播（每5秒切换）
            setInterval(nextSlide, 5000);

            // 分享功能
            function openShareModal() {
                document.getElementById('shareModal').classList.add('active');
            }

            function closeShareModal() {
                document.getElementById('shareModal').classList.remove('active');
            }

            function copyShareText(platform) {
                const shareTexts = {
                    wechat: "🚀 OPC 超级个体孵化助手\\n\\n研究发现100个OPC成功案例，\\n10年产品经理打造，帮你定制专属创业方案！\\n\\n立即体验：https://opc-agent.onrender.com",
                    weibo: "🚀 OPC 超级个体孵化助手\\n\\n研究发现100个OPC成功案例，\\n10年产品经理打造，帮你定制专属创业方案！\\n\\n立即体验：https://opc-agent.onrender.com\\n\\n#OPC创业 #超级个体 #副业增收",
                    default: "🚀 OPC 超级个体孵化助手\\n\\n研究发现100个OPC成功案例，\\n10年产品经理打造，帮你定制专属创业方案！\\n\\n立即体验：https://opc-agent.onrender.com"
                };

                const text = shareTexts[platform] || shareTexts.default;

                // 复制到剪贴板
                if (navigator.clipboard && navigator.clipboard.writeText) {
                    navigator.clipboard.writeText(text).then(() => {
                        alert('文案已复制到剪贴板！');
                    }).catch(err => {
                        // 如果clipboard API失败，使用传统方法
                        const textarea = document.createElement('textarea');
                        textarea.value = text;
                        textarea.style.position = 'fixed';
                        textarea.style.opacity = '0';
                        document.body.appendChild(textarea);
                        textarea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textarea);
                        alert('文案已复制到剪贴板！');
                    });
                } else {
                    // 传统方法
                    const textarea = document.createElement('textarea');
                    textarea.value = text;
                    textarea.style.position = 'fixed';
                    textarea.style.opacity = '0';
                    document.body.appendChild(textarea);
                    textarea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textarea);
                    alert('文案已复制到剪贴板！');
                }
            }

            // 点击模态框外部关闭
            document.getElementById('shareModal').addEventListener('click', function(e) {
                if (e.target === this) {
                    closeShareModal();
                }
            });
        </script>

        <!-- 分享弹窗 -->
        <div class="modal-overlay" id="shareModal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>📤 分享给朋友</h2>
                    <button class="modal-close" onclick="closeShareModal()">×</button>
                </div>
                <div class="share-poster">
                    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='400' height='400'%3E%3Crect width='400' height='400' fill='%23667eea'/%3E%3Ctext x='50%25' y='40%25' text-anchor='middle' fill='white' font-size='24' font-family='Arial'%3E🚀 OPC 超级个体孵化助手%3C/text%3E%3Ctext x='50%25' y='60%25' text-anchor='middle' fill='white' font-size='16' font-family='Arial'%3E扫码立即体验%3C/text%3E%3Crect x='150' y='250' width='100' height='100' fill='white'/%3E%3C/svg%3E" alt="分享海报">
                </div>
                <div class="share-actions">
                    <button class="share-btn wechat" onclick="copyShareText('wechat')">
                        💬 复制微信分享文案
                    </button>
                    <button class="share-btn moment" onclick="copyShareText('weibo')">
                        📱 复制微博分享文案
                    </button>
                    <button class="share-btn copy" onclick="copyShareText('default')">
                        📋 复制通用文案
                    </button>
                </div>
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
