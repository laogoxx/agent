"""
客户信息CRUD操作
"""
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from storage.database.db import get_session
from storage.database.customer_models import User, UserProfile, Recommendation, Payment, ServiceRecord

logger = logging.getLogger(__name__)


# ==================== 用户操作 ====================

def create_user(contact_info: str) -> User:
    """创建用户"""
    with get_session() as session:
        user = User(contact_info=contact_info)
        session.add(user)
        session.commit()
        session.refresh(user)
        logger.info(f"✓ 创建用户成功: {contact_info}")
        return user


def get_user_by_id(user_id: int) -> Optional[User]:
    """根据ID获取用户"""
    with get_session() as session:
        return session.query(User).filter(User.id == user_id).first()


def get_user_by_contact(contact_info: str) -> Optional[User]:
    """根据联系方式获取用户"""
    with get_session() as session:
        return session.query(User).filter(User.contact_info == contact_info).first()


def update_user_last_active(user_id: int):
    """更新用户最后活跃时间"""
    with get_session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.last_active_at = datetime.now()
            session.commit()
            logger.debug(f"✓ 更新用户活跃时间: {user_id}")


# ==================== 用户档案操作 ====================

def create_user_profile(
    user_id: int,
    target_city: Optional[str] = None,
    skills: Optional[str] = None,
    work_experience: Optional[str] = None,
    interests: Optional[str] = None,
    risk_tolerance: Optional[str] = None,
    time_commitment: Optional[str] = None,
    startup_budget: Optional[float] = None
) -> UserProfile:
    """创建用户档案"""
    with get_session() as session:
        profile = UserProfile(
            user_id=user_id,
            target_city=target_city,
            skills=skills,
            work_experience=work_experience,
            interests=interests,
            risk_tolerance=risk_tolerance,
            time_commitment=time_commitment,
            startup_budget=startup_budget
        )
        session.add(profile)
        session.commit()
        session.refresh(profile)
        logger.info(f"✓ 创建用户档案成功: user_id={user_id}")
        return profile


def get_user_profile(user_id: int) -> Optional[UserProfile]:
    """获取用户档案"""
    with get_session() as session:
        return session.query(UserProfile).filter(UserProfile.user_id == user_id).first()


def update_user_profile(
    user_id: int,
    target_city: Optional[str] = None,
    skills: Optional[str] = None,
    work_experience: Optional[str] = None,
    interests: Optional[str] = None,
    risk_tolerance: Optional[str] = None,
    time_commitment: Optional[str] = None,
    startup_budget: Optional[float] = None
) -> Optional[UserProfile]:
    """更新用户档案"""
    with get_session() as session:
        profile = session.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if profile:
            if target_city is not None:
                profile.target_city = target_city
            if skills is not None:
                profile.skills = skills
            if work_experience is not None:
                profile.work_experience = work_experience
            if interests is not None:
                profile.interests = interests
            if risk_tolerance is not None:
                profile.risk_tolerance = risk_tolerance
            if time_commitment is not None:
                profile.time_commitment = time_commitment
            if startup_budget is not None:
                profile.startup_budget = startup_budget
            session.commit()
            session.refresh(profile)
            logger.info(f"✓ 更新用户档案成功: user_id={user_id}")
            return profile
        return None


# ==================== 推荐操作 ====================

def create_recommendation(
    user_id: int,
    project_name: Optional[str] = None,
    core_advantage: Optional[str] = None,
    estimated_income: Optional[str] = None,
    startup_cost: Optional[str] = None,
    ai_tools: Optional[Dict[str, Any]] = None
) -> Recommendation:
    """创建推荐记录"""
    with get_session() as session:
        recommendation = Recommendation(
            user_id=user_id,
            project_name=project_name,
            core_advantage=core_advantage,
            estimated_income=estimated_income,
            startup_cost=startup_cost,
            ai_tools=ai_tools
        )
        session.add(recommendation)
        session.commit()
        session.refresh(recommendation)
        logger.info(f"✓ 创建推荐记录成功: user_id={user_id}, project={project_name}")
        return recommendation


def get_recommendations(user_id: int) -> List[Recommendation]:
    """获取用户的所有推荐记录"""
    with get_session() as session:
        return session.query(Recommendation).filter(Recommendation.user_id == user_id).all()


# ==================== 支付操作 ====================

def create_payment(
    user_id: int,
    amount: float,
    payment_method: Optional[str] = None,
    payment_proof: Optional[str] = None,
    transaction_id: Optional[str] = None,
    payment_status: str = 'pending'
) -> Payment:
    """创建支付记录"""
    with get_session() as session:
        payment = Payment(
            user_id=user_id,
            amount=amount,
            payment_method=payment_method,
            payment_proof=payment_proof,
            transaction_id=transaction_id,
            payment_status=payment_status
        )
        session.add(payment)
        session.commit()
        session.refresh(payment)
        logger.info(f"✓ 创建支付记录成功: user_id={user_id}, amount={amount}")
        return payment


def update_payment_status(payment_id: int, status: str) -> Optional[Payment]:
    """更新支付状态"""
    with get_session() as session:
        payment = session.query(Payment).filter(Payment.id == payment_id).first()
        if payment:
            payment.payment_status = status
            session.commit()
            session.refresh(payment)
            logger.info(f"✓ 更新支付状态成功: payment_id={payment_id}, status={status}")
            return payment
        return None


def get_payment(payment_id: int) -> Optional[Payment]:
    """获取支付记录"""
    with get_session() as session:
        return session.query(Payment).filter(Payment.id == payment_id).first()


def get_user_payments(user_id: int) -> List[Payment]:
    """获取用户的所有支付记录"""
    with get_session() as session:
        return session.query(Payment).filter(Payment.user_id == user_id).all()


# ==================== 服务记录操作 ====================

def create_service_record(
    user_id: int,
    payment_id: Optional[int] = None,
    pdf_url: Optional[str] = None,
    group_joined: bool = False
) -> ServiceRecord:
    """创建服务记录"""
    with get_session() as session:
        record = ServiceRecord(
            user_id=user_id,
            payment_id=payment_id,
            pdf_url=pdf_url,
            group_joined=group_joined
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        logger.info(f"✓ 创建服务记录成功: user_id={user_id}")
        return record


def update_service_record(
    record_id: int,
    pdf_url: Optional[str] = None,
    group_joined: Optional[bool] = None
) -> Optional[ServiceRecord]:
    """更新服务记录"""
    with get_session() as session:
        record = session.query(ServiceRecord).filter(ServiceRecord.id == record_id).first()
        if record:
            if pdf_url is not None:
                record.pdf_url = pdf_url
            if group_joined is not None:
                record.group_joined = group_joined
                if group_joined and not record.group_joined_at:
                    record.group_joined_at = datetime.now()
            session.commit()
            session.refresh(record)
            logger.info(f"✓ 更新服务记录成功: record_id={record_id}")
            return record
        return None


def get_user_service_record(user_id: int) -> Optional[ServiceRecord]:
    """获取用户的服务记录"""
    with get_session() as session:
        return session.query(ServiceRecord).filter(ServiceRecord.user_id == user_id).first()


# ==================== 组合操作 ====================

def save_customer_info(
    contact_info: str,
    target_city: Optional[str] = None,
    skills: Optional[str] = None,
    work_experience: Optional[str] = None,
    interests: Optional[str] = None,
    risk_tolerance: Optional[str] = None,
    time_commitment: Optional[str] = None,
    startup_budget: Optional[float] = None
) -> Dict[str, Any]:
    """
    保存完整客户信息（用户+档案）

    Returns:
        Dict containing user_id and profile_id
    """
    # 创建或获取用户
    user = get_user_by_contact(contact_info)
    if not user:
        user = create_user(contact_info)

    # 创建或更新用户档案
    profile = get_user_profile(user.id)
    if profile:
        profile = update_user_profile(
            user.id,
            target_city=target_city,
            skills=skills,
            work_experience=work_experience,
            interests=interests,
            risk_tolerance=risk_tolerance,
            time_commitment=time_commitment,
            startup_budget=startup_budget
        )
    else:
        profile = create_user_profile(
            user.id,
            target_city=target_city,
            skills=skills,
            work_experience=work_experience,
            interests=interests,
            risk_tolerance=risk_tolerance,
            time_commitment=time_commitment,
            startup_budget=startup_budget
        )

    # 更新最后活跃时间
    update_user_last_active(user.id)

    return {
        'user_id': user.id,
        'profile_id': profile.id,
        'contact_info': user.contact_info
    }


def save_payment_and_service(
    contact_info: str,
    amount: float,
    payment_method: Optional[str] = None,
    payment_proof: Optional[str] = None,
    pdf_url: Optional[str] = None,
    group_joined: bool = False
) -> Dict[str, Any]:
    """
    保存支付信息和服务记录

    Returns:
        Dict containing payment_id and service_record_id
    """
    # 获取或创建用户
    user = get_user_by_contact(contact_info)
    if not user:
        user = create_user(contact_info)

    # 创建支付记录
    payment = create_payment(
        user.id,
        amount=amount,
        payment_method=payment_method,
        payment_proof=payment_proof,
        payment_status='paid'  # 假设已确认支付
    )

    # 创建服务记录
    service_record = create_service_record(
        user.id,
        payment_id=payment.id,
        pdf_url=pdf_url,
        group_joined=group_joined
    )

    # 更新最后活跃时间
    update_user_last_active(user.id)

    return {
        'user_id': user.id,
        'payment_id': payment.id,
        'service_record_id': service_record.id
    }


def get_customer_summary(contact_info: str) -> Optional[Dict[str, Any]]:
    """
    获取客户完整信息摘要

    Returns:
        Dict containing all customer information
    """
    user = get_user_by_contact(contact_info)
    if not user:
        return None

    profile = get_user_profile(user.id)
    recommendations = get_recommendations(user.id)
    payments = get_user_payments(user.id)
    service_record = get_user_service_record(user.id)

    return {
        'user': user.to_dict(),
        'profile': profile.to_dict() if profile else None,
        'recommendations': [r.to_dict() for r in recommendations],
        'payments': [p.to_dict() for p in payments],
        'service_record': service_record.to_dict() if service_record else None
    }
