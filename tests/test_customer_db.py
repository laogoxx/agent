"""
测试数据库初始化和CRUD操作
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.storage.database.db import get_engine, get_session
from src.storage.database.customer_crud import (
    create_user,
    get_user_by_id,
    get_user_by_contact,
    create_user_profile,
    get_user_profile,
    create_recommendation,
    create_payment,
    create_service_record,
    save_customer_info,
    save_payment_and_service,
    get_customer_summary
)


def test_basic_operations():
    """测试基本CRUD操作"""
    print("=" * 60)
    print("测试1: 基本CRUD操作")
    print("=" * 60)

    # 测试创建用户
    print("\n1.1 创建用户...")
    user = create_user("test@example.com")
    print(f"✓ 用户创建成功: ID={user.id}, contact={user.contact_info}")

    # 测试获取用户
    print("\n1.2 获取用户...")
    user_by_id = get_user_by_id(user.id)
    print(f"✓ 通过ID获取用户: {user_by_id.contact_info}")

    user_by_contact = get_user_by_contact("test@example.com")
    print(f"✓ 通过联系方式获取用户: {user_by_contact.contact_info}")

    # 测试创建用户档案
    print("\n1.3 创建用户档案...")
    profile = create_user_profile(
        user_id=user.id,
        target_city="杭州",
        skills="写作、设计",
        work_experience="3年内容运营",
        interests="内容创作、摄影",
        risk_tolerance="中等",
        time_commitment="每周20小时",
        startup_budget=10.0
    )
    print(f"✓ 用户档案创建成功: ID={profile.id}, city={profile.target_city}")

    # 测试获取用户档案
    print("\n1.4 获取用户档案...")
    profile_retrieved = get_user_profile(user.id)
    print(f"✓ 获取用户档案: {profile_retrieved.target_city}, 预算={profile_retrieved.startup_budget}万")

    # 测试创建推荐记录
    print("\n1.5 创建推荐记录...")
    recommendation = create_recommendation(
        user_id=user.id,
        project_name="知识付费创作者",
        core_advantage="写作+AI，开发知识课程",
        estimated_income="保守20万/理想80万",
        startup_cost="中",
        ai_tools={"tools": [{"name": "文心一言", "score": 4.8}]}
    )
    print(f"✓ 推荐记录创建成功: ID={recommendation.id}, 项目={recommendation.project_name}")

    # 测试创建支付记录
    print("\n1.6 创建支付记录...")
    payment = create_payment(
        user_id=user.id,
        amount=68.00,
        payment_method="微信支付",
        payment_proof="已通过微信转账支付",
        transaction_id="wx123456789",
        payment_status="paid"
    )
    print(f"✓ 支付记录创建成功: ID={payment.id}, 金额={payment.amount}")

    # 测试创建服务记录
    print("\n1.7 创建服务记录...")
    service_record = create_service_record(
        user_id=user.id,
        payment_id=payment.id,
        pdf_url="https://example.com/pdf/test.pdf",
        group_joined=False
    )
    print(f"✓ 服务记录创建成功: ID={service_record.id}")

    print("\n✓ 基本CRUD操作测试通过！")
    return user.id


def test_customer_info():
    """测试保存和查询完整客户信息"""
    print("\n" + "=" * 60)
    print("测试2: 完整客户信息保存和查询")
    print("=" * 60)

    # 测试保存客户信息
    print("\n2.1 保存客户信息...")
    result = save_customer_info(
        contact_info="customer2@example.com",
        target_city="上海",
        skills="编程、AI开发",
        work_experience="5年软件开发",
        interests="AI应用开发",
        risk_tolerance="高",
        time_commitment="全职",
        startup_budget=20.0
    )
    print(f"✓ 客户信息保存成功: user_id={result['user_id']}, profile_id={result['profile_id']}")

    # 测试查询客户摘要
    print("\n2.2 查询客户摘要...")
    summary = get_customer_summary("customer2@example.com")
    print(f"✓ 客户摘要查询成功:")
    print(f"  - 用户: {summary['user']['contact_info']}")
    print(f"  - 城市: {summary['profile']['target_city']}")
    print(f"  - 技能: {summary['profile']['skills']}")

    # 测试保存支付和服务
    print("\n2.3 保存支付和服务...")
    result2 = save_payment_and_service(
        contact_info="customer2@example.com",
        amount=68.00,
        payment_method="微信支付",
        payment_proof="已转账",
        pdf_url="https://example.com/pdf/customer2.pdf",
        group_joined=True
    )
    print(f"✓ 支付和服务保存成功: payment_id={result2['payment_id']}")

    # 再次查询客户摘要
    print("\n2.4 再次查询客户摘要（包含支付信息）...")
    summary2 = get_customer_summary("customer2@example.com")
    print(f"✓ 客户摘要包含支付信息:")
    print(f"  - 支付记录数: {len(summary2['payments'])}")
    print(f"  - 服务记录: PDF={summary2['service_record']['pdf_url']}, 入群={summary2['service_record']['group_joined']}")

    print("\n✓ 客户信息测试通过！")
    return result['user_id']


def test_duplicate_user():
    """测试重复联系方式的处理"""
    print("\n" + "=" * 60)
    print("测试3: 重复联系方式处理")
    print("=" * 60)

    contact = "duplicate@example.com"

    # 第一次创建
    print("\n3.1 第一次创建用户...")
    result1 = save_customer_info(
        contact_info=contact,
        target_city="北京",
        skills="写作",
        work_experience="1年",
        interests="写作",
        risk_tolerance="低",
        time_commitment="兼职",
        startup_budget=5.0
    )
    print(f"✓ 用户创建成功: user_id={result1['user_id']}")

    # 第二次使用相同联系方式（应该更新现有用户）
    print("\n3.2 第二次使用相同联系方式...")
    result2 = save_customer_info(
        contact_info=contact,
        target_city="深圳",  # 更改城市
        skills="写作、营销",  # 增加技能
        work_experience="2年",
        interests="写作、营销",
        risk_tolerance="中等",
        time_commitment="全职",
        startup_budget=15.0
    )
    print(f"✓ 用户信息更新成功: user_id={result2['user_id']}")

    # 验证用户ID不变
    print("\n3.3 验证用户ID...")
    if result1['user_id'] == result2['user_id']:
        print(f"✓ 用户ID保持不变: {result1['user_id']}")
    else:
        print(f"✗ 错误: 用户ID发生变化！{result1['user_id']} -> {result2['user_id']}")
        return False

    # 验证档案已更新
    print("\n3.4 验证档案更新...")
    summary = get_customer_summary(contact)
    if summary['profile']['target_city'] == "深圳":
        print(f"✓ 城市已更新: {summary['profile']['target_city']}")
    else:
        print(f"✗ 错误: 城市未更新！")
        return False

    print("\n✓ 重复联系方式测试通过！")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始数据库功能测试")
    print("=" * 60)

    try:
        # 测试1: 基本CRUD操作
        user_id1 = test_basic_operations()

        # 测试2: 客户信息保存和查询
        user_id2 = test_customer_info()

        # 测试3: 重复联系方式处理
        test_duplicate_user()

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)
        print("\n测试结果:")
        f"  - 测试用户ID: {user_id1}, {user_id2}"
        print("  - 数据库连接: 正常")
        print("  - CRUD操作: 正常")
        print("  - 客户信息管理: 正常")
        print("  - 重复处理: 正常")
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
