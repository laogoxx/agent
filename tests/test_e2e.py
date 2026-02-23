"""
完整端到端测试
测试Agent是否能够正确调用数据库工具
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_agent_tools():
    """测试Agent工具是否可用"""
    print("=" * 60)
    print("测试1: 检查Agent工具注册")
    print("=" * 60)

    from src.agents.agent import build_agent

    # 构建Agent
    agent = build_agent()

    # 检查工具列表
    tool_names = [tool.name for tool in agent.tools]

    print(f"\n已注册的工具 ({len(tool_names)}个):")
    for i, name in enumerate(tool_names, 1):
        print(f"  {i}. {name}")

    # 检查数据库工具
    required_tools = [
        'save_user_info',
        'save_payment_and_pdf',
        'mark_user_joined_group',
        'get_customer_info',
        'save_recommendations'
    ]

    missing_tools = [t for t in required_tools if t not in tool_names]

    if missing_tools:
        print(f"\n✗ 缺少数据库工具: {missing_tools}")
        return False
    else:
        print(f"\n✓ 所有数据库工具已注册")
        return True


def test_basic_crud():
    """测试基础CRUD操作"""
    print("\n" + "=" * 60)
    print("测试2: 基础CRUD操作")
    print("=" * 60)

    from src.storage.database.customer_crud import (
        save_customer_info,
        get_customer_summary,
        save_payment_and_service,
        get_user_by_contact
    )

    # 测试用户信息保存
    contact = "e2e_test@example.com"
    print(f"\n[1/3] 保存用户信息...")

    result = save_customer_info(
        contact_info=contact,
        target_city="深圳",
        skills="Python、全栈开发",
        work_experience="5年软件开发",
        interests="AI应用开发",
        risk_tolerance="高",
        time_commitment="全职",
        startup_budget=25.0
    )
    print(f"  ✓ 用户创建: user_id={result['user_id']}")

    # 测试客户信息查询
    print(f"\n[2/3] 查询客户信息...")
    summary = get_customer_summary(contact)

    if not summary:
        print(f"  ✗ 查询失败")
        return False

    print(f"  ✓ 查询成功: 城市={summary['profile']['target_city']}, 预算={summary['profile']['startup_budget']}万")

    # 测试支付和服务记录
    print(f"\n[3/3] 保存支付和服务...")
    result2 = save_payment_and_service(
        contact_info=contact,
        amount=68.00,
        payment_method="微信支付",
        payment_proof="已支付",
        pdf_url="https://example.com/pdf/test.pdf",
        group_joined=True
    )
    print(f"  ✓ 保存成功: payment_id={result2['payment_id']}")

    print("\n✓ 基础CRUD操作测试通过")
    return True


def test_pdf_generator():
    """测试PDF生成功能"""
    print("\n" + "=" * 60)
    print("测试3: PDF生成功能")
    print("=" * 60)

    from tools.pdf_generator import generate_opc_pdf

    user_info = {
        "target_city": "杭州",
        "skills": "写作、编辑",
        "work_experience": "3年内容运营",
        "interests": "内容创作",
        "risk_tolerance": "中等",
        "time_commitment": "每周20小时",
        "startup_budget": 10.0
    }

    projects = [
        {
            "name": "知识付费创作者",
            "advantage": "写作+AI，开发知识课程",
            "income": "保守20万/理想80万",
            "cost": "中"
        },
        {
            "name": "内容咨询服务",
            "advantage": "专业策划+高效执行",
            "income": "保守25万/理想50万",
            "cost": "低"
        },
        {
            "name": "新媒体运营",
            "advantage": "数据驱动+精准投放",
            "income": "保守15万/理想40万",
            "cost": "低"
        }
    ]

    print(f"\n生成PDF文档...")
    try:
        pdf_url = generate_opc_pdf(user_info, projects)
        print(f"  ✓ PDF生成成功")
        print(f"  URL: {pdf_url}")
        return True
    except Exception as e:
        print(f"  ✗ PDF生成失败: {e}")
        return False


def test_payment_tool():
    """测试收款工具"""
    print("\n" + "=" * 60)
    print("测试4: 收款工具")
    print("=" * 60)

    from tools.simple_payment import get_payment_qrcode, confirm_payment

    print(f"\n[1/2] 获取收款码...")
    try:
        result = get_payment_qrcode()
        print(f"  ✓ 收款码获取成功")
        print(f"  内容预览: {result[:100]}...")
    except Exception as e:
        print(f"  ✗ 收款码获取失败: {e}")
        return False

    print(f"\n[2/2] 确认支付...")
    try:
        result = confirm_payment(
            payment_proof="微信转账截图",
            contact_info="test@example.com"
        )
        print(f"  ✓ 支付确认成功")
        print(f"  内容预览: {result[:100]}...")
    except Exception as e:
        print(f"  ✗ 支付确认失败: {e}")
        return False

    print("\n✓ 收款工具测试通过")
    return True


def test_group_info():
    """测试微信群信息"""
    print("\n" + "=" * 60)
    print("测试5: 微信群信息")
    print("=" * 60)

    from tools.wechat_group_info import get_wechat_group_info

    print(f"\n获取微信群信息...")
    try:
        result = get_wechat_group_info()
        print(f"  ✓ 群信息获取成功")
        print(f"  内容预览: {result[:100]}...")
        return True
    except Exception as e:
        print(f"  ✗ 群信息获取失败: {e}")
        return False


def run_complete_test():
    """运行完整测试"""
    print("\n" + "=" * 60)
    print("开始端到端测试")
    print("=" * 60)

    results = {}

    # 测试1: Agent工具注册
    results['agent_tools'] = test_agent_tools()

    # 测试2: 基础CRUD操作
    results['basic_crud'] = test_basic_crud()

    # 测试3: PDF生成
    results['pdf_generator'] = test_pdf_generator()

    # 测试4: 收款工具
    results['payment_tool'] = test_payment_tool()

    # 测试5: 微信群信息
    results['group_info'] = test_group_info()

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {test_name}: {status}")

    print("\n" + "=" * 60)
    if passed == total:
        print(f"✓ 所有测试通过！ ({passed}/{total})")
        print("=" * 60)
        print("\n系统已就绪，可以进行生产部署！")
        return True
    else:
        print(f"✗ 部分测试失败 ({passed}/{total})")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = run_complete_test()
    sys.exit(0 if success else 1)
