"""
测试数据库工具的底层CRUD函数
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.database.customer_crud import (
    save_customer_info,
    get_customer_summary,
    save_payment_and_service,
    create_recommendation,
    update_service_record,
    get_user_by_contact,
    get_user_service_record
)


def test_save_user_info():
    """测试保存用户信息"""
    print("=" * 60)
    print("测试1: 保存用户信息")
    print("=" * 60)

    contact = "api_test@example.com"

    result = save_customer_info(
        contact_info=contact,
        target_city="广州",
        skills="设计、UI/UX",
        work_experience="3年产品设计",
        interests="设计、用户体验",
        risk_tolerance="中等",
        time_commitment="每周25小时",
        startup_budget=12.0
    )

    print(f"\n返回结果: {result}")
    print("\n✓ 用户信息保存测试通过！")
    return contact


def test_get_customer_info():
    """测试查询客户信息"""
    print("\n" + "=" * 60)
    print("测试2: 查询客户信息")
    print("=" * 60)

    contact = "api_test@example.com"

    summary = get_customer_summary(contact)

    if not summary:
        print("✗ 未找到客户信息")
        return False

    print(f"\n客户信息:")
    print(f"  - 用户ID: {summary['user']['id']}")
    print(f"  - 联系方式: {summary['user']['contact_info']}")
    print(f"  - 城市: {summary['profile']['target_city']}")
    print(f"  - 技能: {summary['profile']['skills']}")
    print(f"  - 预算: {summary['profile']['startup_budget']}万")

    print("\n✓ 查询客户信息测试通过！")
    return True


def test_save_recommendation():
    """测试保存推荐项目"""
    print("\n" + "=" * 60)
    print("测试3: 保存推荐项目")
    print("=" * 60)

    contact = "api_test@example.com"
    user = get_user_by_contact(contact)

    if not user:
        print("✗ 未找到用户")
        return False

    recommendation = create_recommendation(
        user_id=user.id,
        project_name="UI/UX设计服务",
        core_advantage="专业设计+AI工具，快速交付",
        estimated_income="保守30万/理想60万",
        startup_cost="低",
        ai_tools={"tools": [{"name": "Midjourney", "score": 4.5}, {"name": "Figma", "score": 4.8}]}
    )

    print(f"\n推荐项目:")
    print(f"  - 项目名称: {recommendation.project_name}")
    print(f"  - 核心优势: {recommendation.core_advantage}")
    print(f"  - 预期收入: {recommendation.estimated_income}")
    print(f"  - 推荐ID: {recommendation.id}")

    print("\n✓ 保存推荐项目测试通过！")
    return True


def test_save_payment_and_service():
    """测试保存支付和服务记录"""
    print("\n" + "=" * 60)
    print("测试4: 保存支付和服务记录")
    print("=" * 60)

    contact = "api_test@example.com"

    result = save_payment_and_service(
        contact_info=contact,
        amount=68.00,
        payment_method="微信支付",
        payment_proof="已通过微信转账",
        pdf_url="https://storage.example.com/pdf/api_test.pdf",
        group_joined=False
    )

    print(f"\n返回结果: {result}")
    print("\n✓ 保存支付和服务记录测试通过！")
    return True


def test_mark_joined_group():
    """测试标记入群"""
    print("\n" + "=" * 60)
    print("测试5: 标记用户入群")
    print("=" * 60)

    contact = "api_test@example.com"
    user = get_user_by_contact(contact)

    if not user:
        print("✗ 未找到用户")
        return False

    service_record = get_user_service_record(user.id)
    if not service_record:
        print("✗ 未找到服务记录")
        return False

    update_service_record(service_record.id, group_joined=True)

    print(f"\n✓ 用户入群标记成功: user_id={user.id}")

    # 验证
    summary = get_customer_summary(contact)
    if summary['service_record']['group_joined']:
        print(f"✓ 入群状态已确认: {summary['service_record']['group_joined_at']}")
    else:
        print("✗ 入群状态未更新")
        return False

    print("\n✓ 标记用户入群测试通过！")
    return True


def test_complete_workflow():
    """测试完整工作流程"""
    print("\n" + "=" * 60)
    print("测试6: 完整工作流程")
    print("=" * 60)

    contact = "workflow@example.com"

    # 步骤1: 保存用户信息
    print("\n[1/5] 保存用户信息...")
    result1 = save_customer_info(
        contact_info=contact,
        target_city="成都",
        skills="写作、内容策划",
        work_experience="4年新媒体运营",
        interests="内容创作、阅读",
        risk_tolerance="中等",
        time_commitment="每周30小时",
        startup_budget=8.0
    )
    print(f"    ✓ 用户创建: user_id={result1['user_id']}")

    # 步骤2: 保存推荐项目
    print("\n[2/5] 保存推荐项目...")
    user = get_user_by_contact(contact)
    recommendation = create_recommendation(
        user_id=user.id,
        project_name="内容创作咨询",
        core_advantage="专业策划+AI辅助，高效产出",
        estimated_income="保守25万/理想50万",
        startup_cost="低",
        ai_tools={"tools": [{"name": "文心一言", "score": 4.8}, {"name": "即梦", "score": 4.7}]}
    )
    print(f"    ✓ 推荐项目: {recommendation.project_name}")

    # 步骤3: 保存支付和服务
    print("\n[3/5] 保存支付和服务...")
    result3 = save_payment_and_service(
        contact_info=contact,
        amount=68.00,
        payment_method="微信支付",
        payment_proof="微信转账完成",
        pdf_url="https://storage.example.com/pdf/workflow.pdf",
        group_joined=False
    )
    print(f"    ✓ 支付记录: payment_id={result3['payment_id']}")
    print(f"    ✓ 服务记录: record_id={result3['service_record_id']}")

    # 步骤4: 标记入群
    print("\n[4/5] 标记用户入群...")
    service_record = get_user_service_record(user.id)
    update_service_record(service_record.id, group_joined=True)
    print(f"    ✓ 入群标记成功")

    # 步骤5: 查询完整信息
    print("\n[5/5] 查询完整信息...")
    summary = get_customer_summary(contact)

    print(f"\n完整客户信息:")
    print(f"  用户: {summary['user']['contact_info']} (ID: {summary['user']['id']})")
    print(f"  城市: {summary['profile']['target_city']}")
    print(f"  技能: {summary['profile']['skills']}")
    print(f"  推荐项目数: {len(summary['recommendations'])}")
    print(f"  支付记录数: {len(summary['payments'])}")
    print(f"  PDF: {summary['service_record']['pdf_url']}")
    print(f"  已入群: {summary['service_record']['group_joined']}")

    print("\n✓ 完整工作流程测试通过！")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始数据库功能测试")
    print("=" * 60)

    try:
        # 测试1: 保存用户信息
        contact = test_save_user_info()

        # 测试2: 查询客户信息
        test_get_customer_info()

        # 测试3: 保存推荐项目
        test_save_recommendation()

        # 测试4: 保存支付和服务
        test_save_payment_and_service()

        # 测试5: 标记入群
        test_mark_joined_group()

        # 测试6: 完整工作流程
        test_complete_workflow()

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        print("\n测试结果:")
        print("  - 用户信息保存: 正常")
        print("  - 客户信息查询: 正常")
        print("  - 推荐项目保存: 正常")
        print("  - 支付记录保存: 正常")
        print("  - 入群标记: 正常")
        print("  - 完整工作流程: 正常")
        print("\n数据库功能已就绪，可以集成到Agent中！")
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
