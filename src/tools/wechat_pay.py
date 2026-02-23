"""
微信支付工具模块
支持Native支付订单创建和查询
"""

import os
import json
import logging
from typing import Dict
from langchain.tools import tool

logger = logging.getLogger(__name__)

# 全局变量，用于缓存支付客户端
_wechatpay_client = None
_payment_config = None

def load_payment_config() -> Dict:
    """
    加载支付配置

    优先级：
    1. 从config/payment_config.json文件加载
    2. 从环境变量加载

    Returns:
        Dict: 支付配置字典
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
                _payment_config = json.load(f).get("wechat_pay", {})
                logger.info("从配置文件加载微信支付配置")
                return _payment_config
        except Exception as e:
            logger.warning(f"从配置文件加载失败: {e}")

    # 从环境变量加载
    _payment_config = {
        "mchid": os.getenv("WECHAT_PAY_MCHID"),
        "appid": os.getenv("WECHAT_PAY_APPID"),
        "apiv3_key": os.getenv("WECHAT_PAY_APIV3_KEY"),
        "cert_serial_no": os.getenv("WECHAT_PAY_CERT_SERIAL_NO"),
        "private_key_path": os.getenv("WECHAT_PAY_PRIVATE_KEY_PATH"),
        "cert_dir": os.getenv("WECHAT_PAY_CERT_DIR"),
        "notify_url": os.getenv("WECHAT_PAY_NOTIFY_URL")
    }

    logger.info("从环境变量加载微信支付配置")
    return _payment_config

def get_wechatpay_client():
    """
    获取微信支付客户端

    Returns:
        WeChatPay: 微信支付客户端实例
    Raises:
        ImportError: 如果未安装wechatpayv3库
        FileNotFoundError: 如果商户私钥文件不存在
        ValueError: 如果配置不完整
    """
    global _wechatpay_client

    if _wechatpay_client is not None:
        return _wechatpay_client

    # 检查依赖
    try:
        from wechatpayv3 import WeChatPay, WeChatPayType
    except ImportError:
        raise ImportError(
            "未安装wechatpayv3库。请运行: pip install wechatpayv3\n"
            "参考文档: docs/微信支付接入指南.md"
        )

    # 加载配置
    config = load_payment_config()

    # 验证必要配置
    required_fields = ["mchid", "apiv3_key", "cert_serial_no"]
    missing_fields = [f for f in required_fields if not config.get(f)]
    if missing_fields:
        raise ValueError(
            f"微信支付配置不完整，缺少必要字段: {', '.join(missing_fields)}\n"
            "请配置config/payment_config.json或设置环境变量\n"
            "参考文档: docs/微信支付接入指南.md"
        )

    # 读取商户私钥
    private_key_path = config.get("private_key_path")
    if not private_key_path:
        raise ValueError("未配置商户私钥路径(private_key_path)")

    # 处理相对路径
    if not os.path.isabs(private_key_path):
        workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
        private_key_path = os.path.join(workspace_path, private_key_path)

    if not os.path.exists(private_key_path):
        raise FileNotFoundError(
            f"商户私钥文件不存在: {private_key_path}\n"
            "请确认证书文件已正确放置\n"
            "参考文档: docs/微信支付接入指南.md"
        )

    try:
        with open(private_key_path, 'r', encoding='utf-8') as f:
            private_key = f.read()
    except Exception as e:
        raise IOError(f"读取商户私钥文件失败: {e}")

    # 初始化客户端
    try:
        wxpay = WeChatPay(
            wechatpay_type=WeChatPayType.NATIVE,
            mchid=config.get("mchid"),
            private_key=private_key,
            cert_serial_no=config.get("cert_serial_no"),
            apiv3_key=config.get("apiv3_key"),
            appid=config.get("appid", ""),  # 可选
            notify_url=config.get("notify_url", ""),  # 可选
            cert_dir=config.get("cert_dir")  # 可选
        )
        _wechatpay_client = wxpay
        logger.info("微信支付客户端初始化成功")
        return wxpay

    except Exception as e:
        raise RuntimeError(f"初始化微信支付客户端失败: {e}")

@tool
def create_wechat_pay_order(
    out_trade_no: str,
    total: int,
    description: str
) -> str:
    """
    创建微信支付Native支付订单

    Args:
        out_trade_no: 商户订单号（需唯一，建议格式：前缀+时间戳）
        total: 订单金额，单位为分（1元=100分）
        description: 商品描述

    Returns:
        str: 支付二维码链接（code_url）或错误信息

    Example:
        >>> create_wechat_pay_order("OPC20240101001", 6800, "OPC创业指导PDF")
        "✅ 支付订单创建成功！\n\n📱 请使用微信扫描以下二维码完成支付：\n\nweixin://wxpay/bizpayurl?pr=xxxxxxxx\n\n💡 支付金额：68.00元\n📝 订单号：OPC20240101001"
    """
    try:
        wxpay = get_wechatpay_client()

        # 参数验证
        if not out_trade_no:
            return "❌ 订单号不能为空"
        if not isinstance(total, int) or total <= 0:
            return "❌ 金额必须是正整数（单位为分）"
        if not description:
            return "❌ 商品描述不能为空"

        logger.info(f"创建支付订单: 订单号={out_trade_no}, 金额={total}分, 描述={description}")

        # 调用Native支付下单接口
        response = wxpay.pay(
            description=description,
            out_trade_no=out_trade_no,
            amount={"total": total}
        )

        # 解析响应
        if response.get("code") == 200:
            result = json.loads(response.get("message", "{}"))
            code_url = result.get("code_url")

            if not code_url:
                return f"❌ 创建支付订单成功，但未获取到二维码链接"

            logger.info(f"支付订单创建成功: 订单号={out_trade_no}, code_url={code_url}")

            return (
                f"✅ 支付订单创建成功！\n\n"
                f"📱 请使用微信扫描以下二维码完成支付：\n\n"
                f"{code_url}\n\n"
                f"💡 支付金额：{total/100:.2f}元\n"
                f"📝 订单号：{out_trade_no}\n"
                f"📊 商品：{description}\n\n"
                f"支付完成后，请告诉我订单号，我将为您生成PDF文档。"
            )
        else:
            error_msg = response.get('message', '未知错误')
            logger.error(f"创建支付订单失败: 订单号={out_trade_no}, 错误={error_msg}")
            return f"❌ 创建支付订单失败：{error_msg}"

    except ImportError as e:
        logger.error(f"微信支付依赖未安装: {e}")
        return (
            f"❌ 微信支付功能未配置\n\n"
            f"错误信息：{str(e)}\n\n"
            f"请按以下步骤配置：\n"
            f"1. 安装依赖：pip install wechatpayv3\n"
            f"2. 配置支付凭证（参考文档：docs/微信支付接入指南.md）\n"
            f"3. 或继续使用模拟支付方式"
        )
    except FileNotFoundError as e:
        logger.error(f"证书文件未找到: {e}")
        return (
            f"❌ 证书文件未找到\n\n"
            f"错误信息：{str(e)}\n\n"
            f"请确认已完成微信支付配置\n"
            f"参考文档：docs/微信支付接入指南.md\n"
            f"或继续使用模拟支付方式"
        )
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        return (
            f"❌ 微信支付配置错误\n\n"
            f"错误信息：{str(e)}\n\n"
            f"请检查配置文件或环境变量\n"
            f"参考文档：docs/微信支付接入指南.md\n"
            f"或继续使用模拟支付方式"
        )
    except Exception as e:
        logger.error(f"创建支付订单时发生未知错误: {e}")
        return f"❌ 创建支付订单时发生错误：{str(e)}"

@tool
def query_wechat_pay_order(out_trade_no: str) -> str:
    """
    查询微信支付订单状态

    Args:
        out_trade_no: 商户订单号

    Returns:
        str: 订单状态信息

    Example:
        >>> query_wechat_pay_order("OPC20240101001")
        "✅ 订单查询成功\n\n📝 订单号：OPC20240101001\n📊 状态：支付成功（SUCCESS）\n💰 交易金额：68.00元"
    """
    try:
        wxpay = get_wechatpay_client()

        # 参数验证
        if not out_trade_no:
            return "❌ 订单号不能为空"

        logger.info(f"查询支付订单: 订单号={out_trade_no}")

        # 查询订单
        response = wxpay.query(out_trade_no=out_trade_no)

        if response.get("code") == 200:
            result = json.loads(response.get("message", "{}"))
            trade_state = result.get("trade_state", "UNKNOWN")
            trade_state_desc = result.get("trade_state_desc", "")
            amount_info = result.get("amount", {})
            total_amount = amount_info.get("total", 0) / 100  # 转换为元
            transaction_id = result.get("transaction_id", "")
            success_time = result.get("success_time", "")

            state_map = {
                "SUCCESS": "支付成功",
                "REFUND": "转入退款",
                "NOTPAY": "未支付",
                "CLOSED": "已关闭",
                "REVOKED": "已撤销",
                "USERPAYING": "用户支付中",
                "PAYERROR": "支付失败"
            }

            status = state_map.get(trade_state, trade_state)
            status_emoji = "✅" if trade_state == "SUCCESS" else "⏳"

            result_msg = (
                f"{status_emoji} 订单查询成功\n\n"
                f"📝 订单号：{out_trade_no}\n"
                f"📊 状态：{status}（{trade_state_desc}）\n"
                f"💰 交易金额：{total_amount:.2f}元"
            )

            if transaction_id:
                result_msg += f"\n🔑 微信订单号：{transaction_id}"

            if success_time:
                result_msg += f"\n⏰ 支付时间：{success_time}"

            logger.info(f"订单查询成功: 订单号={out_trade_no}, 状态={trade_state}")

            # 如果支付成功，返回特殊标记
            if trade_state == "SUCCESS":
                result_msg += "\n\n🎉 支付已完成！现在可以为您生成PDF文档。"

            return result_msg
        else:
            error_msg = response.get('message', '未知错误')
            logger.error(f"查询订单失败: 订单号={out_trade_no}, 错误={error_msg}")
            return f"❌ 查询订单失败：{error_msg}"

    except Exception as e:
        logger.error(f"查询订单时发生错误: {e}")
        return f"❌ 查询订单时发生错误：{str(e)}"

# 导出工具函数列表
WECHAT_PAY_TOOLS = [
    create_wechat_pay_order,
    query_wechat_pay_order
]
