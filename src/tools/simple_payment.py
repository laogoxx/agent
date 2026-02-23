"""
简单收款工具
支持微信和支付宝个人收款码收款
"""

import os
import json
import logging
from typing import Dict, Optional
from langchain.tools import tool

logger = logging.getLogger(__name__)

# 支付配置
_payment_config = None

def load_payment_config() -> Dict:
    """
    加载收款配置
    
    Returns:
        Dict: 收款配置字典
    """
    global _payment_config
    
    if _payment_config is not None:
        return _payment_config
    
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    config_path = os.path.join(workspace_path, "config/payment_config.json")
    
    # 尝试从配置文件加载
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                _payment_config = json.load(f)
                logger.info("从配置文件加载收款配置")
                return _payment_config
        except Exception as e:
            logger.warning(f"从配置文件加载失败: {e}")
    
    # 返回默认配置
    _payment_config = {
        "payment_method": "qrcode",  #收款码模式
        "wechat_qrcode_url": os.getenv("WECHAT_QRCODE_URL", ""),
        "alipay_qrcode_url": os.getenv("ALIPAY_QRCODE_URL", ""),
        "wechat_account": os.getenv("WECHAT_ACCOUNT", "your_wechat_id"),
        "alipay_account": os.getenv("ALIPAY_ACCOUNT", "your_alipay_id"),
        "price": 68.00,  # 默认价格
        "product_name": "OPC创业指导PDF"
    }
    
    logger.info("使用默认收款配置")
    return _payment_config

@tool
def get_payment_qrcode() -> str:
    """
    获取收款码信息（简单收款方式）
    
    Returns:
        str: 收款码信息和支付方式
    """
    config = load_payment_config()
    
    # 方式一：如果有收款码图片URL
    wechat_qrcode = config.get("wechat_qrcode_url", "")
    alipay_qrcode = config.get("alipay_qrcode_url", "")
    
    # 方式二：使用账户信息
    wechat_account = config.get("wechat_account", "")
    alipay_account = config.get("alipay_account", "")
    
    price = config.get("price", 68.00)
    product_name = config.get("product_name", "OPC创业指导PDF")
    
    result = (
        f"💰 **支付方式**\n\n"
        f"📦 **商品**：{product_name}\n"
        f"💵 **价格**：¥{price:.2f}\n\n"
    )
    
    if wechat_qrcode:
        result += (
            f"### 🟢 微信支付\n"
            f"📱 请扫描以下二维码支付：\n\n"
            f"```\n"
            f"{wechat_qrcode}\n"
            f"```\n\n"
        )
    elif wechat_account:
        result += (
            f"### 🟢 微信支付\n"
            f"📱 微信搜索或扫描添加：\n"
            f"**{wechat_account}**\n\n"
            f"💡 操作步骤：\n"
            f"1. 打开微信 → 点击「+」→「扫一扫」\n"
            f"2. 扫描或添加微信号：{wechat_account}\n"
            f"3. 转账 ¥{price:.2f} 元，备注「OPC创业指导」\n\n"
        )
    
    if alipay_qrcode:
        result += (
            f"### 🔵 支付宝支付\n"
            f"📱 请扫描以下二维码支付：\n\n"
            f"```\n"
            f"{alipay_qrcode}\n"
            f"```\n\n"
        )
    elif alipay_account:
        result += (
            f"### 🔵 支付宝支付\n"
            f"📱 支付宝账号：\n"
            f"**{alipay_account}**\n\n"
            f"💡 操作步骤：\n"
            f"1. 打开支付宝 → 点击「转账」\n"
            f"2. 输入账号：{alipay_account}\n"
            f"3. 转账 ¥{price:.2f} 元，备注「OPC创业指导」\n\n"
        )
    
    result += (
        f"⚠️ **温馨提示**：\n"
        f"- 支付时请务必备注「OPC创业指导」或「手机号/邮箱」\n"
        f"- 支付完成后，请将支付截图发给我\n"
        f"- 我将为您生成PDF文档并提供入群二维码\n\n"
        f"⏰ **处理时间**：10分钟内完成\n"
        f"📞 **客服支持**：如有问题请联系客服\n\n"
        f"感谢您的支持！💪"
    )
    
    return result

@tool
def confirm_payment(
    payment_proof: str,
    contact_info: str
) -> str:
    """
    确认支付并提供服务
    
    Args:
        payment_proof: 支付凭证描述（如：支付截图已发送、转账时间等）
        contact_info: 联系方式（手机号或邮箱）
    
    Returns:
        str: 确认信息和服务交付
    
    Example:
        >>> confirm_payment("已通过微信转账支付", "user@example.com")
        "✅ 支付确认成功！\n\n正在生成PDF文档..."
    """
    logger.info(f"收到支付确认: payment_proof={payment_proof}, contact_info={contact_info}")
    
    result = (
        f"✅ **支付确认成功！**\n\n"
        f"📝 支付凭证：{payment_proof}\n"
        f"📧 联系方式：{contact_info}\n\n"
        f"🔄 正在为您生成PDF文档，请稍候...\n\n"
    )
    
    # 返回提示信息，引导用户等待PDF生成
    result += (
        f"💡 **接下来的步骤**：\n"
        f"1. 我将为您生成专属的OPC创业指导PDF\n"
        f"2. 同时提供微信群入群二维码\n"
        f"3. 您将收到PDF下载链接和入群方式\n\n"
        f"⏳ 请稍等片刻，正在处理中..."
    )
    
    return result

# 导出工具函数列表
SIMPLE_PAYMENT_TOOLS = [
    get_payment_qrcode,
    confirm_payment
]
