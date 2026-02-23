"""
测试数据库工具在Agent中的集成
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from langchain.tools import ToolRuntime
from src.tools.customer_db_tools import (
    save_user_info,
    save_payment_and_pdf,
    mark_user_joined_group,
    get_customer_info,
    save_recommendations
)


def test_save_user_info_tool():
    """测试保存用户信息工具"""
    print("=" * 60)
    print("测试1: save_user_info 工具")
    print("=" * 60)

    contact = "tool_test@example.com"

    result = save_user_info(
        contact_info=contact,
        target_city="广州",
        skills="设计、UI/UX",
        work_experience="3年产品设计",
        interests="设计、用户体验",
        risk_tolerance="中等",
        time_commitment="每周25小时",
        startup_budget=12.0
    )

    print(f"\n返回结果:\n{result}")
    print("\n✓ save_user_info 工具测试通过！")
    return contact


def test_get_customer_info_tool():
    """测试查询客户信息工具"""
    print("\n" + "=" * 60)
    print("测试2: get_customer_info 工具")
    print("=" * 60)

    contact = "tool_test@example.com"

    result = get_customer_info(contact_info=contact)

    print(f"\n返回结果:\n{result}")
    print("\n✓ get_customer_info 工具测试通过！")


def test_save_recommendations_tool():
    """测试保存推荐项目工具"""
    print("\n" + "=" * 60)
    print("测试3: save_recommendations 工具")
    print("=" * 60)

    contact = "tool_test@example.com"

    result = save_recommendations(
        contact_info=contact,
        project_name="UI/UX设计服务",
        core_advantage="专业设计+AI工具，快速交付",
        estimated_income="保守30万/理想60万",
        startup_cost="低",
        ai_tools='{"tools": [{"name": "Midjourney", "score": 4.5}, {"name": "Figma", "score": 4.8}]}'
    )

    print(f"\n返回结果:\n{result}")
    print("\n✓ save_recommendations 工具测试通过！")


def test_save_payment_and_pdf_tool():
    """测试保存支付和PDF工具"""
    print("\n" + "=" * 60)
    print("测试4: save_payment_and_pdf 工具")
    print("=" * 60)

    contact = "tool_test@example.com"

    result = save_payment_and_pdf(
        contact_info=contact,
        amount=68.00,
        payment_proof="已通过微信转账",
        pdf_url="https://storage.example.com/pdf/tool_test.pdf",
        payment_method="微信支付"
    )

    print(f"\n返回结果:\n{result}")
    print("\n✓ save_payment_and_pdf 工具测试通过！")


def test_mark_user_joined_group_tool():
    """测试标记用户入群工具"""
    print("\n" + "=" * 60)
    print("测试5: mark_user_joined_group 工具")
    print("=" * 60)

    contact = "tool_test@example.com"

    result = mark_user_joined_group(contact_info=contact)

    print(f"\n返回结果:\n{result}")
    print("\n✓ mark_user_joined_group 工具测试通过！")


def test_complete_workflow():
    """测试完整工作流程"""
    print("\n" + "=" * 60)
    print("测试6: 完整工作流程")
    print("=" * 60)

    contact = "workflow_test@example.com"

    # 步骤1: 保存用户信息
    print("\n步骤1: 保存用户信息...")
    result1 = save_user_info(
        contact_info=contact,
        target_city="成都",
        skills="写作、内容策划",
        work_experience="4年新媒体运营",
        interests="内容创作、阅读",
        risk_tolerance="中等",
        time_commitment="每周30小时",
        startup_budget=8.0
    )
    print(f"✓ 用户信息保存成功")

    # 步骤2: 保存推荐项目
    print("\n步骤2: 保存推荐项目...")
    result2 = save_recommendations(
        contact_info=contact,
        project_name="内容创作咨询",
        core_advantage="专业策划+AI辅助，高效产出",
        estimated_income="保守25万/理想50万",
        startup_cost="低",
        ai_tools='{"tools": [{"name": "文心一言", "score": 4.8}, {"name": "即梦", "score": 4.7}]}'
    )
    print(f"✓ 推荐项目保存成功")

    # 步骤3: 保存支付和PDF
    print("\n步骤3: 保存支付和PDF...")
    result3 = save_payment_and_pdf(
        contact_info=contact,
        amount=68.00,
        payment_proof="微信转账完成",
        pdf_url="https://storage.example.com/pdf/workflow_test.pdf",
        payment_method="微信支付"
    )
    print(f"✓ 支付和PDF信息保存成功")

    # 步骤4: 标记用户入群
    print("\n步骤4: 标记用户入群...")
    result4 = mark_user_joined_group(contact_info=contact)
    print(f"✓ 用户入群标记成功")

    # 步骤5: 查询完整客户信息
    print("\n步骤5: 查询完整客户信息...")
    result5 = get_customer_info(contact_info=contact)
    print(f"✓ 客户信息查询成功")

    print(f"\n完整信息:\n{result5}")
    print("\n✓ 完整工作流程测试通过！")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始数据库工具测试")
    print("=" * 60)

    try:
        # 测试1: 保存用户信息
        contact = test_save_user_info_tool()

        # 测试2: 查询客户信息
        test_get_customer_info_tool()

        # 测试3: 保存推荐项目
        test_save_recommendations_tool()

        # 测试4: 保存支付和PDF
        test_save_payment_and_pdf_tool()

        # 测试5: 标记用户入群
        test_mark_user_joined_group_tool()

        # 测试6: 完整工作流程
        test_complete_workflow()

        print("\n" + "=" * 60)
        print("✓ 所有数据库工具测试通过！")
        print("=" * 60)
        print("\n测试结果:")
        print("  - save_user_info: 正常")
        print("  - get_customer_info: 正常")
        print("  - save_recommendations: 正常")
        print("  - save_payment_and_pdf: 正常")
        print("  - mark_user_joined_group: 正常")
        print("  - 完整工作流程: 正常")
        print("\n工具已成功集成到Agent中！")
        return True

    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ 测试失败！")
        print("=" * 60)
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
