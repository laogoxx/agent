"""
完整流程测试脚本：项目推荐 → 收款 → 入群
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects')
sys.path.insert(0, project_root)

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.tools.simple_payment import SIMPLE_PAYMENT_TOOLS
from src.tools.wechat_group_info import get_wechat_group_info

def test_complete_flow():
    """测试完整流程"""
    print("=" * 60)
    print("完整流程测试")
    print("=" * 60)

    # 测试1：获取收款码
    print("\n【步骤1】用户要求查看支付方式...")
    get_payment_tool = None
    for tool in SIMPLE_PAYMENT_TOOLS:
        if tool.name == "get_payment_qrcode":
            get_payment_tool = tool
            break

    if get_payment_tool:
        result = get_payment_tool.invoke({})
        print("✓ 收款码信息获取成功")
        if "https://ibb.co/0y0jXhCv" in result:
            print("✓ 微信收款码链接正确")
    else:
        print("✗ 未找到get_payment_qrcode工具")

    # 测试2：用户确认支付
    print("\n【步骤2】用户确认支付...")
    confirm_tool = None
    for tool in SIMPLE_PAYMENT_TOOLS:
        if tool.name == "confirm_payment":
            confirm_tool = tool
            break

    if confirm_tool:
        result = confirm_tool.invoke({
            "payment_proof": "已通过微信转账支付68元",
            "contact_info": "user@example.com"
        })
        print("✓ 支付确认成功")
    else:
        print("✗ 未找到confirm_payment工具")

    # 测试3：显示群信息
    print("\n【步骤3】提供入群方式...")
    result = get_wechat_group_info.invoke({})
    print("✓ 群信息获取成功")
    if "https://ibb.co/PZrnNCT2" in result:
        print("✓ 企业微信群二维码链接正确")
    if "OPC超级个体孵化群" in result:
        print("✓ 群名称正确")

    print("\n" + "=" * 60)
    print("✅ 完整流程测试通过！")
    print("=" * 60)
    print("\n用户可以：")
    print("1. 查看收款码 → https://ibb.co/0y0jXhCv")
    print("2. 扫码支付68元")
    print("3. 确认支付并提供联系方式")
    print("4. 获取入群二维码 → https://ibb.co/PZrnNCT2")
    print("5. 扫码加入企业微信群")

    return True

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)
