"""
客户信息数据模型
用于存储用户信息、创业信息、推荐记录、支付记录、服务记录
"""
import datetime
from sqlalchemy import BigInteger, DateTime, Integer, String, Text, Boolean, DECIMAL, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column
from typing import Optional, Dict, Any

from storage.database.shared.model import Base


class User(Base):
    """用户基本信息表"""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    contact_info: Mapped[str] = mapped_column(String(255), nullable=False, comment="联系方式（邮箱/手机号/微信号）")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    last_active_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), comment="最后活跃时间")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'contact_info': self.contact_info,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_active_at': self.last_active_at.isoformat() if self.last_active_at else None,
        }


class UserProfile(Base):
    """用户创业信息表"""
    __tablename__ = 'user_profiles'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID")
    target_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="目标城市")
    skills: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="专业技能")
    work_experience: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="工作经验")
    interests: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="个人兴趣")
    risk_tolerance: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="风险承受能力")
    time_commitment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="时间投入")
    startup_budget: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 2), nullable=True, comment="启动资金")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_city': self.target_city,
            'skills': self.skills,
            'work_experience': self.work_experience,
            'interests': self.interests,
            'risk_tolerance': self.risk_tolerance,
            'time_commitment': self.time_commitment,
            'startup_budget': float(self.startup_budget) if self.startup_budget else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Recommendation(Base):
    """推荐记录表"""
    __tablename__ = 'recommendations'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID")
    project_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="项目名称")
    core_advantage: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="核心优势")
    estimated_income: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, comment="预期收入")
    startup_cost: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment="启动成本")
    ai_tools: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True, comment="AI工具推荐（JSON格式）")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_name': self.project_name,
            'core_advantage': self.core_advantage,
            'estimated_income': self.estimated_income,
            'startup_cost': self.startup_cost,
            'ai_tools': self.ai_tools,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class Payment(Base):
    """支付记录表"""
    __tablename__ = 'payments'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID")
    amount: Mapped[float] = mapped_column(DECIMAL(10, 2), nullable=False, comment="支付金额")
    payment_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="支付方式")
    payment_proof: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="支付凭证")
    payment_status: Mapped[str] = mapped_column(String(20), default='pending', comment="支付状态：pending/paid/refunded")
    transaction_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="交易ID")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'amount': float(self.amount),
            'payment_method': self.payment_method,
            'payment_proof': self.payment_proof,
            'payment_status': self.payment_status,
            'transaction_id': self.transaction_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class ServiceRecord(Base):
    """服务记录表"""
    __tablename__ = 'service_records'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="用户ID")
    payment_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, comment="支付ID")
    pdf_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="PDF下载链接")
    group_joined: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否已入群")
    group_joined_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True), nullable=True, comment="入群时间")
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'payment_id': self.payment_id,
            'pdf_url': self.pdf_url,
            'group_joined': self.group_joined,
            'group_joined_at': self.group_joined_at.isoformat() if self.group_joined_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
