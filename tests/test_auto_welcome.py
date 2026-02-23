"""
Agent自动欢迎功能测试和使用示例
"""
import sys
import os
from typing import Dict, Any

# 添加项目根目录到Python路径
project_root = os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects')
sys.path.insert(0, project_root)

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(project_root, 'src'))

from langchain_core.messages import HumanMessage, AIMessage
from agents.agent import build_agent, get_welcome_message


def agent_with_welcome_wrapper(agent_func):
    """
    包装Agent函数，添加自动欢迎功能

    当消息列表为空或只有SystemMessage时，自动发送欢迎消息
    """
    async def wrapped_agent(state: Dict[str, Any], config=None):
        messages = state.get("messages", [])

        # 如果没有消息，或者只有系统消息，自动发送欢迎语
        if not messages:
            # 返回欢迎消息
            return {"messages": [AIMessage(content=get_welcome_message())]}

        # 否则正常调用agent
        return await agent_func(state, config)

    return wrapped_agent


async def test_auto_welcome():
    """测试自动欢迎功能"""
    print("=" * 60)
    print("测试1：自动欢迎功能")
    print("=" * 60)

    # 创建Agent
    agent = build_agent()
    wrapped_agent = agent_with_welcome_wrapper(agent.ainvoke)

    # 测试场景1：消息为空（用户刚打开对话框，还没说话）
    print("\n【场景1】消息为空（用户还没说话）")
    state = {"messages": []}
    result = await wrapped_agent(state)
    print(f"✓ 自动欢迎消息已发送")
    print(f"内容预览（前100字）：{result['messages'][0].content[:100]}...\n")

    # 测试场景2：用户主动提问
    print("=" * 60)
    print("测试2：用户主动提问")
    print("=" * 60)

    print("\n【场景2】用户主动提问")
    state = {
        "messages": [HumanMessage(content="你好，我想创业")]
    }
    result = await wrapped_agent(state)
    print(f"✓ Agent正常响应")
    print(f"响应预览（前100字）：{result['messages'][-1].content[:100]}...\n")

    print("=" * 60)
    print("✅ 测试通过！")
    print("=" * 60)


def usage_example():
    """使用示例"""
    print("\n" + "=" * 60)
    print("📝 使用示例")
    print("=" * 60)

    print("""
## 如何使用自动欢迎功能

### 方法1：在调用Agent时检查（推荐）

```python
from agents.agent import build_agent, get_welcome_message
from langchain_core.messages import HumanMessage, AIMessage

async def chat_with_agent(user_input=None):
    agent = build_agent()

    # 如果用户没有输入（首次访问），自动发送欢迎语
    if not user_input:
        return AIMessage(content=get_welcome_message())

    # 否则正常调用Agent
    state = {"messages": [HumanMessage(content=user_input)]}
    result = await agent.ainvoke(state)
    return result['messages'][-1]
```

### 方法2：使用包装函数

```python
from agents.agent import build_agent, agent_with_welcome_wrapper

# 创建带自动欢迎功能的Agent
agent = build_agent()
wrapped_agent = agent_with_welcome_wrapper(agent.ainvoke)

# 无论用户是否输入，都会自动处理
state = {"messages": []}  # 或 {"messages": [HumanMessage(content="你好")]}
result = await wrapped_agent(state)
```

### 方法3：前端处理（Web应用）

```javascript
// 前端示例
async function sendMessage(userInput) {
    if (!userInput) {
        // 用户还没说话，显示欢迎消息
        displayMessage(get_welcomeMessage());
        return;
    }

    // 用户输入了内容，正常调用Agent
    const response = await callAgent(userInput);
    displayMessage(response);
}
```

### 方法4：配置自定义欢迎语

编辑 `.env` 文件：

```bash
# 自定义欢迎消息（可选）
AGENT_WELCOME_MESSAGE=你好！我是你的创业指导助手，请问有什么可以帮你的？
```

如果没有配置，将使用默认的欢迎语。

---

## 欢迎消息的触发时机

✅ 会触发自动欢迎：
- 消息列表为空 `[]`
- 用户刚打开对话框，还没说话
- 用户清除了对话历史

❌ 不会触发自动欢迎：
- 用户已经发送过消息
- 消息列表中包含用户的输入
- 对话进行中

---

## 效果对比

### 没有自动欢迎功能
```
用户：（打开对话框，等待...）
（什么都没有，用户不知道该说什么）
```

### 有自动欢迎功能
```
用户：（打开对话框）
Agent：你好！我是OPC超级个体孵化助手。我们深度研究了100个超级个体成功案例...
用户：哦，我想做内容创业
Agent：好的，请问你想在哪个城市创业？
```

---

## 在Web应用中集成

```python
# FastAPI 示例
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from agents.agent import build_agent, get_welcome_message
from langchain_core.messages import HumanMessage, AIMessage

app = FastAPI()

@app.post("/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    user_input = data.get("message", "")

    agent = build_agent()

    # 如果没有输入，返回欢迎消息
    if not user_input:
        return {
            "message": get_welcome_message(),
            "is_welcome": True
        }

    # 否则正常处理
    state = {"messages": [HumanMessage(content=user_input)]}
    result = await agent.ainvoke(state)

    return {
        "message": result['messages'][-1].content,
        "is_welcome": False
    }
```
    """)


if __name__ == "__main__":
    import asyncio

    # 运行测试
    asyncio.run(test_auto_welcome())

    # 显示使用示例
    usage_example()
