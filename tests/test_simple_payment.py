"""
简单收款工具测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects')
sys.path.insert(0, project_root)

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.tools.simple_payment import SIMPLE_PAYMENT_TOOLS

def test_get_payment_qrcode():
    """测试获取收款码"""
    print("=" * 60)
    print("测试1: 获取收款码")
    print("=" * 60)
    
    try:
        # 找到get_payment_qrcode工具
        get_payment_tool = None
        for tool in SIMPLE_PAYMENT_TOOLS:
            if tool.name == "get_payment_qrcode":
                get_payment_tool = tool
                break
        
        if get_payment_tool is None:
            print("✗ 未找到get_payment_qrcode工具")
            return False
        
        # 调用工具
        result = get_payment_tool.invoke({})
        print(f"✓ 获取收款码成功")
        print(f"返回结果:\n{result}")
        return True
    except Exception as e:
        print(f"✗ 获取收款码失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_confirm_payment():
    """测试确认支付"""
    print("\n" + "=" * 60)
    print("测试2: 确认支付")
    print("=" * 60)
    
    try:
        # 找到confirm_payment工具
        confirm_tool = None
        for tool in SIMPLE_PAYMENT_TOOLS:
            if tool.name == "confirm_payment":
                confirm_tool = tool
                break
        
        if confirm_tool is None:
            print("✗ 未找到confirm_payment工具")
            return False
        
        # 调用工具
        result = confirm_tool.invoke({
            "payment_proof": "已通过微信转账支付68元",
            "contact_info": "test@example.com"
        })
        print(f"✓ 确认支付成功")
        print(f"返回结果:\n{result}")
        return True
    except Exception as e:
        print(f"✗ 确认支付失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_all():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试简单收款工具")
    print("=" * 60)
    
    results = []
    
    # 测试获取收款码
    results.append(("获取收款码", test_get_payment_qrcode()))
    
    # 测试确认支付
    results.append(("确认支付", test_confirm_payment()))
    
    # 打印测试结果摘要
    print("\n" + "=" * 60)
    print("测试结果摘要")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("\n" + "-" * 60)
    print(f"总计: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = test_all()
    sys.exit(0 if success else 1)
