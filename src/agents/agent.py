import os
import json
import logging
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from storage.memory.memory_saver import get_memory_saver
from tools.pdf_generator_simple import generate_opc_pdf_simple
from tools.simple_payment import SIMPLE_PAYMENT_TOOLS
from tools.wechat_group_info import get_wechat_group_info
from tools.customer_db_tools import (
    save_user_info,
    save_payment_and_pdf,
    mark_user_joined_group,
    get_customer_info,
    save_recommendations
)

logger = logging.getLogger(__name__)

LLM_CONFIG = "config/agent_llm_config.json"

# 默认保留最近 20 轮对话 (40 条消息)
MAX_MESSAGES = 40

def _windowed_messages(old, new):
    """滑动窗口: 只保留最近 MAX_MESSAGES 条消息"""
    combined = add_messages(old, new)
    # 确保返回的是列表类型
    if not isinstance(combined, list):
        return [combined]
    return combined[-MAX_MESSAGES:] if len(combined) > MAX_MESSAGES else combined

class AgentState(MessagesState):
    messages: Annotated[list[AnyMessage], _windowed_messages]

# 欢迎消息（当用户未主动提问时自动发送）
WELCOME_MESSAGE = """🔥 2025年，你是否也有这样的焦虑？

❌ 35岁职场危机越来越近，裁员潮一波接一波
❌ 工资涨幅跑不赢通胀，存款缩水
❌ 每天加班到深夜，却看不到未来
❌ 想改变，但不知道从哪里开始
❌ 看着别人副业月入过万，自己却毫无头绪

---

🚀 但你有没有发现，身边越来越多的人开始做OPC（超级个体）？

**这些真实案例就在你身边：**
- 小张，30岁，程序员 → AI提示词工程师，月收入3万+
- 小李，28岁，财务 → 自媒体账号，粉丝10万，月广告收入2万
- 小王，35岁，传统销售 → 个人IP打造，年入50万+
- 小陈，32岁，普通宝妈 → 在线课程，月收入1.5万

**这，就是OPC创业的红利！**

---

🎯 为什么现在是OPC创业的黄金时期？

✅ **技术门槛降低**：AI工具让一个人可以干10个人的活
✅ **市场碎片化**：小众需求爆发，精准变现更容易
✅ **平台红利期**：短视频、知识付费、直播带货流量巨大
✅ **成本低风险小**：轻资产运营，试错成本极低
✅ **收入不封顶**：没有职场天花板，完全看你的能力

---

💡 **我是谁？为什么能帮你？**

我是你的OPC超级个体孵化助手。

我由**超过10年创业经验的产品经理**打造而来，深度研究了**100个OPC成功案例**，覆盖了IT、内容创作、电商、咨询、教育等20+个领域。

我会**深度分析你的个人特点**：
- 你的专业技能如何转化为创业优势
- 你所在城市的商业机会和竞争格局
- 适合你的创业赛道和变现模式
- 从0到1的详细执行路径

---

🤔 **想不想知道：**

1️⃣ 以你的技能和经验，最适合做什么OPC项目？
2️⃣ 你所在的城市，有哪些未被发现的商业机会？
3️⃣ 如何在3个月内，从0开始实现月入过万？
4️⃣ 具体需要准备什么？有哪些坑要避开？

**别再焦虑了，行动起来！**

告诉我：
- 📍 **你在哪个城市？**
- 💼 **你会什么技能？**
- 🎯 **你想通过OPC解决什么问题？**

我会为你量身定制创业方案，并对接资源孵化群，全程陪伴你从0到1！

---

💬 **现在就开始吧，告诉我你的情况，我们一起开启你的OPC创业之旅！**"""

def get_welcome_message() -> str:
    """获取欢迎消息，可以从配置文件或环境变量读取"""
    # 优先从环境变量读取
    welcome_msg = os.getenv("AGENT_WELCOME_MESSAGE", "")
    if welcome_msg:
        return welcome_msg
    # 否则使用默认欢迎语
    return WELCOME_MESSAGE

def build_agent(ctx=None):
    # 使用相对路径，适配不同环境（本地、Render等）
    # config_path 会相对于当前工作目录解析
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), LLM_CONFIG)

    # 如果相对路径不存在，尝试从项目根目录读取
    if not os.path.exists(config_path):
        config_path = LLM_CONFIG

    logger.info(f"Loading config from: {config_path}")
    logger.info(f"Current working directory: {os.getcwd()}")
    logger.info(f"Config file exists: {os.path.exists(config_path)}")

    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = json.load(f)

    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    base_url = os.getenv("COZE_INTEGRATION_MODEL_BASE_URL")

    llm = ChatOpenAI(
        model=cfg['config'].get("model"),
        api_key=api_key,
        base_url=base_url,
        temperature=cfg['config'].get('temperature', 0.7),
        streaming=True,
        timeout=cfg['config'].get('timeout', 600),
        extra_body={
            "thinking": {
                "type": cfg['config'].get('thinking', 'disabled')
            }
        },
        default_headers={}  # 生产环境不需要特殊的 headers
    )

    # 导入所有工具
    tools = [
        generate_opc_pdf_simple,  # 使用简化版 PDF 生成工具
        *SIMPLE_PAYMENT_TOOLS,  # 添加收款工具（get_payment_qrcode, confirm_payment）
        get_wechat_group_info,
        # 数据库工具
        save_user_info,
        save_payment_and_pdf,
        mark_user_joined_group,
        get_customer_info,
        save_recommendations
    ]

    return create_agent(
        model=llm,
        system_prompt=cfg.get("sp"),
        tools=tools,
        checkpointer=get_memory_saver(),
        state_schema=AgentState,
    )
