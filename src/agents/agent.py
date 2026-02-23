import os
import json
import logging
from typing import Annotated
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage
from coze_coding_utils.runtime_ctx.context import default_headers, new_context
from storage.memory.memory_saver import get_memory_saver
from tools.pdf_generator import generate_opc_pdf
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
WELCOME_MESSAGE = """你好！我是OPC超级个体孵化助手。我们深度研究了100个超级个体成功案例，并针对全国主要城市的市场环境进行了充分调研。基于这些数据和经验，我可以为你推荐最适合的创业方向，并提供资源对接孵化群的持续支持。

为了给你精准匹配创业项目，请告诉我以下信息：

1. 你的常住地址或计划创业的城市是哪里？
2. 你拥有哪些专业技能？比如编程、设计、写作、营销、摄影等？
3. 能简单介绍一下你的工作经验吗？包括所在行业、职位和工作年限？
4. 你的个人兴趣和爱好是什么？比如是否喜欢内容创作、手工制作、社交活动等？

💡 你也可以直接告诉我你想了解的内容，比如：
- "我想做XX类型的创业"
- "帮我推荐适合我的创业项目"
- "我想了解AI工具推荐"

期待你的回复！"""

def get_welcome_message() -> str:
    """获取欢迎消息，可以从配置文件或环境变量读取"""
    # 优先从环境变量读取
    welcome_msg = os.getenv("AGENT_WELCOME_MESSAGE", "")
    if welcome_msg:
        return welcome_msg
    # 否则使用默认欢迎语
    return WELCOME_MESSAGE

def build_agent(ctx=None):
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, LLM_CONFIG)

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
        default_headers=default_headers(ctx) if ctx else {}
    )

    # 导入所有工具
    tools = [
        generate_opc_pdf,
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
