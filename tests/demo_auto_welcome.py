"""
简单的主动欢迎功能演示
"""
import sys
import os
import asyncio

# 添加项目根目录到Python路径
project_root = os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects')
sys.path.insert(0, project_root)

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(project_root, 'src'))

from agents.agent import get_welcome_message

def demo_auto_welcome():
    """演示主动欢迎功能"""
    print("=" * 70)
    print("🎬 Agent主动欢迎功能演示")
    print("=" * 70)

    print("\n【场景描述】")
    print("用户打开对话框，还没有说话")
    print("--------------------------------------------------")

    print("\n【Agent自动发送欢迎消息】")
    print("--------------------------------------------------")
    welcome_msg = get_welcome_message()
    print(welcome_msg)

    print("\n【用户看到欢迎消息后...】")
    print("--------------------------------------------------")
    print("用户：哦，我想做内容创业，擅长写作")
    print("\n（此时Agent会继续正常对话）")

    print("\n【提示】")
    print("--------------------------------------------------")
    print("1. 这个欢迎消息会自动发送，无需用户触发")
    print("2. 欢迎消息可以自定义，编辑 .env 文件中的 AGENT_WELCOME_MESSAGE")
    print("3. 可以在Web应用中集成，页面加载时自动显示")
    print("4. 参考文档：docs/主动欢迎功能说明.md")

    print("\n" + "=" * 70)
    print("✅ 演示完成！")
    print("=" * 70)

if __name__ == "__main__":
    demo_auto_welcome()
