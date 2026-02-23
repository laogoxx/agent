"""
客户信息管理工具
"""
import json
from typing import Dict, Any, Optional
from langchain.tools import tool, ToolRuntime

from storage.database.customer_crud import (
    save_customer_info,
    save_payment_and_service,
    get_customer_summary,
    create_recommendation,
    update_service_record
)


@tool
def save_user_info(
    contact_info: str,
    target_city: str,
    skills: str,
    work_experience: str,
    interests: str,
    risk_tolerance: str,
    time_commitment: str,
    startup_budget: float,
    runtime: ToolRuntime = None
) -> str:
    """
    保存用户信息和创业偏好

    Args:
        contact_info: 联系方式（邮箱/手机号/微信号）
        target_city: 目标城市
        skills: 专业技能
        work_experience: 工作经验
        interests: 个人兴趣
        risk_tolerance: 风险承受能力
        startup_budget: 启动资金
        risk_tolerance: 风险承受能力
        time_commitment: 时间投入

    Returns:
        str: 保存结果信息

    Example:
        >>> save_user_info(
        ...     contact_info="user@example.com",
        ...     target_city="杭州",
        ...     skills="写作",
        ...     work_experience="3年内容运营",
        ...     interests="内容创作",
        ...     risk_tolerance="中等",
        ...     time_commitment="每周20小时",
        ...     startup_budget=10
        ... )
    """
    result = save_customer_info(
        contact_info=contact_info,
        target_city=target_city,
        skills=skills,
        work_experience=work_experience,
        interests=interests,
        risk_tolerance=risk_tolerance,
        time_commitment=time_commitment,
        startup_budget=startup_budget
    )

    return f"""✅ **用户信息保存成功！**

📋 **保存的用户信息**：
- 联系方式：{result['contact_info']}
- 用户ID：{result['user_id']}
- 档案ID：{result['profile_id']}

📍 **创业信息**：
- 目标城市：{target_city}
- 专业技能：{skills}
- 启动资金：{startup_budget}万元

这些信息已保存到数据库，后续可以用于：
- 个性化推荐
- 数据分析
- 客户管理"""


@tool
def save_payment_and_pdf(
    contact_info: str,
    amount: float,
    payment_proof: str,
    pdf_url: str,
    payment_method: str = "微信支付",
    runtime: ToolRuntime = None
) -> str:
    """
    保存支付信息和PDF下载链接

    Args:
        contact_info: 联系方式
        amount: 支付金额
        payment_proof: 支付凭证
        pdf_url: PDF下载链接
        payment_method: 支付方式（默认：微信支付）

    Returns:
        str: 保存结果信息

    Example:
        >>> save_payment_and_pdf(
        ...     contact_info="user@example.com",
        ...     amount=68.00,
        ...     payment_proof="已通过微信转账支付",
        ...     pdf_url="https://storage.example.com/pdf/xxx.pdf"
        ... )
    """
    result = save_payment_and_service(
        contact_info=contact_info,
        amount=amount,
        payment_method=payment_method,
        payment_proof=payment_proof,
        pdf_url=pdf_url,
        group_joined=False
    )

    return f"""✅ **支付信息保存成功！**

💰 **支付记录**：
- 支付金额：¥{amount:.2f}
- 支付方式：{payment_method}
- 支付凭证：{payment_proof}
- 支付ID：{result['payment_id']}

📄 **服务记录**：
- PDF下载链接：{pdf_url}
- 服务记录ID：{result['service_record_id']}

📊 **用户信息**：
- 用户ID：{result['user_id']}
- 联系方式：{contact_info}

这些信息已保存到数据库，便于后续查询和管理。"""


@tool
def mark_user_joined_group(
    contact_info: str,
    runtime: ToolRuntime = None
) -> str:
    """
    标记用户已加入企业微信群

    Args:
        contact_info: 联系方式

    Returns:
        str: 更新结果信息

    Example:
        >>> mark_user_joined_group(contact_info="user@example.com")
    """
    from storage.database.customer_crud import (
        get_user_by_contact,
        get_user_service_record,
        update_service_record
    )

    user = get_user_by_contact(contact_info)
    if not user:
        return f"⚠️ **未找到用户**：联系方式 {contact_info} 不存在，请先保存用户信息"

    service_record = get_user_service_record(user.id)
    if not service_record:
        return f"⚠️ **未找到服务记录**：用户 {contact_info} 尚未完成支付，无法标记入群"

    if service_record.group_joined:
        return f"ℹ️ **用户已入群**：用户 {contact_info} 已经在 {service_record.group_joined_at} 入群"

    update_service_record(service_record.id, group_joined=True)

    return f"""✅ **入群标记成功！**

🎉 **用户信息**：
- 联系方式：{contact_info}
- 用户ID：{user.id}
- 服务记录ID：{service_record.id}

📊 **状态更新**：
- 入群状态：已加入
- 入群时间：已记录

用户已成功加入企业微信群！"""


@tool
def get_customer_info(
    contact_info: str,
    runtime: ToolRuntime = None
) -> str:
    """
    查询客户完整信息

    Args:
        contact_info: 联系方式

    Returns:
        str: 客户信息详情

    Example:
        >>> get_customer_info(contact_info="user@example.com")
    """
    summary = get_customer_summary(contact_info)

    if not summary:
        return f"⚠️ **未找到客户**：联系方式 {contact_info} 不存在"

    result = f"""📋 **客户信息查询结果**

👤 **基本信息**：
- 用户ID：{summary['user']['id']}
- 联系方式：{summary['user']['contact_info']}
- 创建时间：{summary['user']['created_at']}
- 最后活跃：{summary['user']['last_active_at']}

"""

    if summary['profile']:
        result += f"""📝 **创业信息**：
- 目标城市：{summary['profile'].get('target_city', '未填写')}
- 专业技能：{summary['profile'].get('skills', '未填写')}
- 工作经验：{summary['profile'].get('work_experience', '未填写')}
- 个人兴趣：{summary['profile'].get('interests', '未填写')}
- 风险承受：{summary['profile'].get('risk_tolerance', '未填写')}
- 时间投入：{summary['profile'].get('time_commitment', '未填写')}
- 启动资金：{summary['profile'].get('startup_budget', '未填写')}万元

"""

    if summary['recommendations']:
        result += f"🎯 **推荐项目**：共 {len(summary['recommendations'])} 个\n"
        for rec in summary['recommendations']:
            result += f"- {rec['project_name']}：{rec['estimated_income']}\n"

    if summary['payments']:
        result += f"\n💰 **支付记录**：共 {len(summary['payments'])} 笔\n"
        for pay in summary['payments']:
            result += f"- ¥{pay['amount']}（{pay['payment_status']}）- {pay['created_at']}\n"

    if summary['service_record']:
        result += f"\n📄 **服务记录**：\n"
        if summary['service_record']['pdf_url']:
            result += f"- PDF下载链接：{summary['service_record']['pdf_url']}\n"
        if summary['service_record']['group_joined']:
            result += f"- 已入群（{summary['service_record']['group_joined_at']}）\n"
        else:
            result += f"- 未入群\n"

    return result


@tool
def save_recommendations(
    contact_info: str,
    project_name: str,
    core_advantage: str,
    estimated_income: str,
    startup_cost: str,
    ai_tools: str,
    runtime: ToolRuntime = None
) -> str:
    """
    保存推荐项目信息

    Args:
        contact_info: 联系方式
        project_name: 项目名称
        core_advantage: 核心优势
        estimated_income: 预期收入
        startup_cost: 启动成本
        ai_tools: AI工具推荐（JSON字符串）

    Returns:
        str: 保存结果信息

    Example:
        >>> save_recommendations(
        ...     contact_info="user@example.com",
        ...     project_name="知识付费创作者",
        ...     core_advantage="写作+AI，开发知识课程",
        ...     estimated_income="保守20万/理想80万",
        ...     startup_cost="中",
        ...     ai_tools='{"tools": [{"name": "文心一言", "score": 4.8}]}'
        ... )
    """
    from storage.database.customer_crud import get_user_by_contact

    user = get_user_by_contact(contact_info)
    if not user:
        return f"⚠️ **未找到用户**：联系方式 {contact_info} 不存在，请先保存用户信息"

    try:
        ai_tools_dict = json.loads(ai_tools) if ai_tools else None
    except json.JSONDecodeError:
        ai_tools_dict = None

    recommendation = create_recommendation(
        user_id=user.id,
        project_name=project_name,
        core_advantage=core_advantage,
        estimated_income=estimated_income,
        startup_cost=startup_cost,
        ai_tools=ai_tools_dict
    )

    return f"""✅ **推荐项目保存成功！**

🎯 **项目信息**：
- 项目名称：{project_name}
- 核心优势：{core_advantage}
- 预期收入：{estimated_income}
- 启动成本：{startup_cost}
- 推荐ID：{recommendation.id}

📊 **用户信息**：
- 用户ID：{user.id}
- 联系方式：{contact_info}

推荐项目已保存到数据库，便于后续查询和统计。"""

fix: 更新 customer_db_tools.py，移除 new_context 导入
