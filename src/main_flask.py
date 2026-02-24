from flask import Flask, request, jsonify
import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from agents.agent import build_agent
from langgraph.checkpoint.memory import MemorySaver
from tools.share_tool import generate_share_poster, get_share_text

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
                position: relative;
            }
            .chat-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px 25px;
                display: flex;
                align-items: center;
                justify-content: space-between;
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
                border: none;
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                cursor: pointer;
                font-size: 14px;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                gap: 6px;
            }
            .share-button:hover {
                background: rgba(255, 255, 255, 0.3);
                transform: translateY(-2px);
            }
            
            /* 成功案例轮播 */
            .success-cases {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 20px 25px;
                border-bottom: 2px solid #e9ecef;
            }
            .success-cases-title {
                font-size: 16px;
                font-weight: 600;
                color: #667eea;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .carousel-container {
                position: relative;
                overflow: hidden;
            }
            .carousel-track {
                display: flex;
                transition: transform 0.5s ease-in-out;
                gap: 15px;
            }
            .case-card {
                min-width: calc(100% - 30px);
                background: white;
                border-radius: 12px;
                padding: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                border-left: 4px solid #667eea;
            }
            .case-card h3 {
                font-size: 16px;
                color: #333;
                margin-bottom: 8px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .case-card .highlight {
                color: #667eea;
                font-weight: 600;
            }
            .case-card .info {
                font-size: 13px;
                color: #666;
                margin-bottom: 8px;
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
            }
            .case-card .info span {
                background: #f0f0f0;
                padding: 4px 10px;
                border-radius: 20px;
            }
            .case-card .description {
                font-size: 13px;
                color: #555;
                line-height: 1.5;
            }
            .carousel-nav {
                display: flex;
                justify-content: center;
                gap: 8px;
                margin-top: 12px;
            }
            .carousel-dot {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #ccc;
                cursor: pointer;
                transition: all 0.3s;
            }
            .carousel-dot.active {
                background: #667eea;
                transform: scale(1.2);
            }
            .carousel-arrow {
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: rgba(102, 126, 234, 0.9);
                color: white;
                border: none;
                font-size: 16px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s;
                z-index: 10;
            }
            .carousel-arrow:hover {
                background: #5568d3;
                transform: translateY(-50%) scale(1.1);
            }
            .carousel-arrow.prev {
                left: 5px;
            }
            .carousel-arrow.next {
                right: 5px;
            }
            
            /* 聊天消息区域 */
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
            
            /* 引导式提问 */
            .guided-questions {
                padding: 15px 25px 5px 25px;
                background: white;
            }
            .guided-questions-title {
                font-size: 13px;
                color: #666;
                margin-bottom: 10px;
                font-weight: 500;
            }
            .question-buttons {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            .question-button {
                flex: 1;
                min-width: 280px;
                padding: 12px 15px;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border: 2px solid #e9ecef;
                border-radius: 12px;
                cursor: pointer;
                transition: all 0.3s;
                text-align: left;
            }
            .question-button:hover {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-color: #667eea;
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            .question-button .title {
                font-size: 14px;
                font-weight: 600;
                color: #333;
                margin-bottom: 4px;
            }
            .question-button:hover .title {
                color: white;
            }
            .question-button .hint {
                font-size: 12px;
                color: #666;
                line-height: 1.4;
            }
            .question-button:hover .hint {
                color: rgba(255, 255, 255, 0.9);
            }
            
            /* 聊天输入区域 */
            .chat-input-area {
                padding: 15px 25px 20px 25px;
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
            
            /* 分享弹窗 */
            .share-modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                z-index: 1000;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .share-modal.active {
                display: flex;
            }
            .share-modal-content {
                background: white;
                border-radius: 20px;
                padding: 30px;
                max-width: 500px;
                width: 100%;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                animation: slideUp 0.3s ease-out;
            }
            @keyframes slideUp {
                from { transform: translateY(50px); opacity: 0; }
                to { transform: translateY(0); opacity: 1; }
            }
            .share-modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 25px;
            }
            .share-modal-header h2 {
                font-size: 24px;
                color: #333;
            }
            .share-close-button {
                background: none;
                border: none;
                font-size: 28px;
                color: #999;
                cursor: pointer;
                transition: color 0.3s;
            }
            .share-close-button:hover {
                color: #333;
            }
            .share-section {
                margin-bottom: 25px;
            }
            .share-section-title {
                font-size: 16px;
                font-weight: 600;
                color: #667eea;
                margin-bottom: 15px;
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .share-qr-preview {
                background: #f8f9fa;
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                margin-bottom: 15px;
            }
            .share-qr-preview img {
                max-width: 100%;
                border-radius: 8px;
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            }
            .share-buttons {
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            .share-action-button {
                flex: 1;
                min-width: 120px;
                padding: 12px 20px;
                border: none;
                border-radius: 25px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            .share-action-button.primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .share-action-button.secondary {
                background: #f8f9fa;
                color: #667eea;
                border: 2px solid #667eea;
            }
            .share-action-button:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            .share-link-box {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
                display: flex;
                gap: 10px;
                align-items: center;
            }
            .share-link-text {
                flex: 1;
                font-size: 14px;
                color: #555;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }
            .share-text-box {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 12px;
                padding: 15px;
                max-height: 150px;
                overflow-y: auto;
            }
            .share-text-content {
                font-size: 14px;
                color: #555;
                line-height: 1.6;
                white-space: pre-wrap;
                word-break: break-word;
            }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="chat-header">
                <h1>🚀 OPC 超级个体孵化助手</h1>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div class="status">
                        <div class="status-dot"></div>
                        <span>在线</span>
                    </div>
                    <button class="share-button" onclick="openShareModal()">
                        <span>📤</span>
                        <span>分享</span>
                    </button>
                </div>
            </div>

            <div class="success-cases">
                <div class="success-cases-title">
                    <span>🏆</span>
                    <span>成功案例</span>
                </div>
                <div class="carousel-container" id="carousel">
                    <button class="carousel-arrow prev" onclick="prevSlide()">&#10094;</button>
                    <div class="carousel-track" id="carouselTrack"></div>
                    <button class="carousel-arrow next" onclick="nextSlide()">&#10095;</button>
                </div>
                <div class="carousel-nav" id="carouselNav"></div>
            </div>

            <div class="chat-messages" id="chatMessages">
                <div class="message assistant">
                    <div class="message-bubble" id="welcomeMessage"></div>
                </div>
            </div>

            <div class="typing-indicator" id="typingIndicator">
                <span></span>
                <span></span>
                <span></span>
            </div>

            <div class="guided-questions">
                <div class="guided-questions-title">💡 不知从何开始？试试这些：</div>
                <div class="question-buttons">
                    <button class="question-button" onclick="sendQuickMessage('我每天加班到深夜，工资却涨得慢。想改变但不知道从哪里开始...')">
                        <div class="title">😰 职场焦虑</div>
                        <div class="hint">我每天加班到深夜，工资却涨得慢。想改变但不知道从哪里开始...</div>
                    </button>
                    <button class="question-button" onclick="sendQuickMessage('我有写作/设计/编程等技能，想利用业余时间做副业增收...')">
                        <div class="title">💡 技能变现</div>
                        <div class="hint">我有写作/设计/编程等技能，想利用业余时间做副业增收...</div>
                    </button>
                </div>
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

        <!-- 分享弹窗 -->
        <div class="share-modal" id="shareModal" onclick="closeShareModalOutside(event)">
            <div class="share-modal-content" onclick="event.stopPropagation()">
                <div class="share-modal-header">
                    <h2>📤 分享给朋友</h2>
                    <button class="share-close-button" onclick="closeShareModal()">&times;</button>
                </div>

                <div class="share-section">
                    <div class="share-section-title">📱 二维码分享图片</div>
                    <div class="share-qr-preview">
                        <img id="shareQrImage" src="" alt="分享二维码">
                    </div>
                    <div class="share-buttons">
                        <button class="share-action-button primary" onclick="downloadQrImage()">
                            <span>⬇️</span>
                            <span>下载图片</span>
                        </button>
                    </div>
                </div>

                <div class="share-section">
                    <div class="share-section-title">🔗 分享链接</div>
                    <div class="share-link-box">
                        <div class="share-link-text" id="shareLinkText">https://opc-agent.onrender.com</div>
                        <button class="share-action-button secondary" onclick="copyLink()">
                            <span>📋</span>
                            <span>复制</span>
                        </button>
                    </div>
                </div>

                <div class="share-section">
                    <div class="share-section-title">📝 分享文案</div>
                    <div class="share-text-box">
                        <div class="share-text-content" id="shareTextContent"></div>
                    </div>
                    <div class="share-buttons" style="margin-top: 15px;">
                        <button class="share-action-button primary" onclick="copyShareText()">
                            <span>📋</span>
                            <span>复制文案</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>

        <script>
            const chatMessages = document.getElementById('chatMessages');
            const messageInput = document.getElementById('messageInput');
            const sendButton = document.getElementById('sendButton');
            const typingIndicator = document.getElementById('typingIndicator');
            
            // 成功案例轮播
            let successCases = [];
            let currentSlide = 0;
            let autoSlideInterval;

            async function loadSuccessCases() {
                try {
                    const response = await fetch('/api/success-cases');
                    successCases = await response.json();
                    renderCarousel();
                    startAutoSlide();
                } catch (error) {
                    console.error('加载成功案例失败:', error);
                }
            }

            function renderCarousel() {
                const track = document.getElementById('carouselTrack');
                const nav = document.getElementById('carouselNav');
                
                // 渲染案例卡片
                track.innerHTML = successCases.map(caseItem => `
                    <div class="case-card">
                        <h3>
                            <span class="highlight">${caseItem.name}</span>
                            <span style="font-weight: normal; font-size: 14px; color: #666;">| ${caseItem.age}岁</span>
                        </h3>
                        <div class="info">
                            <span>🔄 ${caseItem.before} → ${caseItem.after}</span>
                            <span>💰 ${caseItem.income}</span>
                            <span>📍 ${caseItem.city}</span>
                            <span>⏱️ ${caseItem.period}</span>
                        </div>
                        <div class="description">${caseItem.description}</div>
                    </div>
                `).join('');
                
                // 渲染导航点
                nav.innerHTML = successCases.map((_, index) => `
                    <div class="carousel-dot ${index === currentSlide ? 'active' : ''}" onclick="goToSlide(${index})"></div>
                `).join('');
                
                updateCarouselPosition();
            }

            function updateCarouselPosition() {
                const track = document.getElementById('carouselTrack');
                const dots = document.querySelectorAll('.carousel-dot');
                const cardWidth = track.children[0].offsetWidth + 15;
                track.style.transform = `translateX(-${currentSlide * cardWidth}px)`;
                
                dots.forEach((dot, index) => {
                    dot.classList.toggle('active', index === currentSlide);
                });
            }

            function nextSlide() {
                currentSlide = (currentSlide + 1) % successCases.length;
                updateCarouselPosition();
                resetAutoSlide();
            }

            function prevSlide() {
                currentSlide = (currentSlide - 1 + successCases.length) % successCases.length;
                updateCarouselPosition();
                resetAutoSlide();
            }

            function goToSlide(index) {
                currentSlide = index;
                updateCarouselPosition();
                resetAutoSlide();
            }

            function startAutoSlide() {
                autoSlideInterval = setInterval(nextSlide, 5000);
            }

            function resetAutoSlide() {
                clearInterval(autoSlideInterval);
                startAutoSlide();
            }

            // 加载欢迎消息
            async function loadWelcomeMessage() {
                try {
                    const response = await fetch('/api/welcome');
                    const data = await response.json();
                    document.getElementById('welcomeMessage').innerHTML = data.message.replace(/\\n/g, '<br>');
                } catch (error) {
                    console.error('加载欢迎消息失败:', error);
                }
            }

            // 分享功能
            let shareData = null;

            async function openShareModal() {
                try {
                    // 加载分享数据
                    if (!shareData) {
                        const response = await fetch('/api/share');
                        shareData = await response.json();
                    }
                    
                    // 更新UI
                    document.getElementById('shareQrImage').src = shareData.qr_image;
                    document.getElementById('shareLinkText').textContent = shareData.link;
                    document.getElementById('shareTextContent').textContent = shareData.text;
                    
                    // 显示弹窗
                    document.getElementById('shareModal').classList.add('active');
                } catch (error) {
                    console.error('加载分享数据失败:', error);
                    alert('加载分享数据失败，请重试');
                }
            }

            function closeShareModal() {
                document.getElementById('shareModal').classList.remove('active');
            }

            function closeShareModalOutside(event) {
                if (event.target === document.getElementById('shareModal')) {
                    closeShareModal();
                }
            }

            function downloadQrImage() {
                const img = document.getElementById('shareQrImage');
                const link = document.createElement('a');
                link.href = img.src;
                link.download = 'opc-agent-share.png';
                link.click();
            }

            function copyLink() {
                const linkText = document.getElementById('shareLinkText').textContent;
                navigator.clipboard.writeText(linkText).then(() => {
                    alert('链接已复制到剪贴板！');
                }).catch(err => {
                    console.error('复制失败:', err);
                    alert('复制失败，请手动复制');
                });
            }

            function copyShareText() {
                const shareText = document.getElementById('shareTextContent').textContent;
                navigator.clipboard.writeText(shareText).then(() => {
                    alert('分享文案已复制到剪贴板！');
                }).catch(err => {
                    console.error('复制失败:', err);
                    alert('复制失败，请手动复制');
                });
            }

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

            function sendQuickMessage(message) {
                messageInput.value = message;
                sendMessage();
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

            // 初始化
            window.onload = function() {
                loadSuccessCases();
                loadWelcomeMessage();
            };
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

@app.route('/api/success-cases', methods=['GET'])
def get_success_cases():
    """获取成功案例"""
    try:
        cases_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'success_cases.json')
        with open(cases_path, 'r', encoding='utf-8') as f:
            cases = json.load(f)
        return jsonify(cases)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/welcome', methods=['GET'])
def get_welcome():
    """获取欢迎消息"""
    try:
        from agents.agent import get_welcome_message
        return jsonify({'message': get_welcome_message()})
    except Exception as e:
        return jsonify({'message': '你好！我是OPC超级个体孵化助手。'}), 500

@app.route('/api/share', methods=['GET'])
def get_share():
    """获取分享数据（二维码和文案）"""
    try:
        # 获取分享链接
        share_url = request.host_url if request.host_url else "https://opc-agent.onrender.com"
        
        # 生成二维码图片
        qr_image = generate_share_poster(share_url)
        
        # 获取分享文案
        share_texts = get_share_text(share_url)
        
        return jsonify({
            'link': share_url,
            'qr_image': qr_image,
            'text': share_texts['wechat_friend']  # 默认使用微信好友文案
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({'status': 'ok', 'service': 'opc-agent'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
