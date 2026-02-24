import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import base64
import logging

logger = logging.getLogger(__name__)

# 图片尺寸配置
POSTER_WIDTH = 600
POSTER_HEIGHT = 800
QR_CODE_SIZE = 200
PADDING = 40


def generate_share_poster(share_url: str, base_url: str = "https://opc-agent.onrender.com") -> str:
    """
    生成分享海报（带二维码）

    Args:
        share_url: 分享链接
        base_url: 基础URL（用于生成二维码）

    Returns:
        str: Base64编码的图片数据
    """
    try:
        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(share_url or base_url)
        qr.make(fit=True)

        # 创建二维码图片
        qr_img = qr.make_image(fill_color="#667eea", back_color="white")

        # 创建海报画布
        poster = Image.new('RGB', (POSTER_WIDTH, POSTER_HEIGHT), color='white')
        draw = ImageDraw.Draw(poster)

        # 尝试加载中文字体
        try:
            # 优先使用系统字体
            font_paths = [
                '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
                '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
                '/System/Library/Fonts/PingFang.ttc',
                '/System/Library/Fonts/STHeiti Light.ttc',
                'C:\\Windows\\Fonts\\msyh.ttc',
                'C:\\Windows\\Fonts\\simhei.ttf',
            ]

            font_large = None
            font_medium = None
            font_small = None

            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        font_large = ImageFont.truetype(font_path, 32)
                        font_medium = ImageFont.truetype(font_path, 24)
                        font_small = ImageFont.truetype(font_path, 18)
                        break
                    except:
                        continue

            # 如果加载失败，使用默认字体
            if font_large is None:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()

        except Exception as e:
            logger.warning(f"Failed to load Chinese font: {e}, using default font")
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # 绘制标题
        title = "🚀 OPC 超级个体孵化助手"
        title_bbox = draw.textbbox((0, 0), title, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (POSTER_WIDTH - title_width) // 2
        draw.text((title_x, PADDING), title, fill="#333", font=font_large)

        # 绘制二维码（居中）
        # 将二维码转换为PIL Image
        qr_buffer = BytesIO()
        qr_img.save(qr_buffer, format='PNG')
        qr_buffer.seek(0)
        qr_pil = Image.open(qr_buffer).convert('RGB')
        qr_resized = qr_pil.resize((QR_CODE_SIZE, QR_CODE_SIZE))
        qr_x = (POSTER_WIDTH - QR_CODE_SIZE) // 2
        qr_y = 120
        poster.paste(qr_resized, (qr_x, qr_y))

        # 绘制二维码下方文字
        qr_text = "扫码立即开启你的OPC创业之旅"
        qr_text_bbox = draw.textbbox((0, 0), qr_text, font=font_medium)
        qr_text_width = qr_text_bbox[2] - qr_text_bbox[0]
        qr_text_x = (POSTER_WIDTH - qr_text_width) // 2
        draw.text((qr_text_x, qr_y + QR_CODE_SIZE + 15), qr_text, fill="#666", font=font_medium)

        # 绘制分割线
        line_y = qr_y + QR_CODE_SIZE + 60
        draw.line([(PADDING, line_y), (POSTER_WIDTH - PADDING, line_y)], fill="#e9ecef", width=2)

        # 绘制特色点
        features = [
            "✨ 研究了100个成功案例",
            "🎯 10年产品经理打造",
            "🌟 个性化创业方案定制",
            "💡 助你3个月月入过万",
        ]

        feature_y = line_y + 30
        for feature in features:
            feature_bbox = draw.textbbox((0, 0), feature, font=font_small)
            feature_width = feature_bbox[2] - feature_bbox[0]
            feature_x = (POSTER_WIDTH - feature_width) // 2
            draw.text((feature_x, feature_y), feature, fill="#555", font=font_small)
            feature_y += 35

        # 绘制底部背景
        footer_y = feature_y + 30
        footer_height = 80
        footer_rect = [(0, footer_y), (POSTER_WIDTH, POSTER_HEIGHT)]
        draw.rectangle(footer_rect, fill="#667eea")

        # 绘制底部文字
        footer_text = "扫码体验 · 开启你的创业之旅"
        footer_text_bbox = draw.textbbox((0, 0), footer_text, font=font_medium)
        footer_text_width = footer_text_bbox[2] - footer_text_bbox[0]
        footer_text_x = (POSTER_WIDTH - footer_text_width) // 2
        footer_text_y = footer_y + (footer_height - (footer_text_bbox[3] - footer_text_bbox[1])) // 2
        draw.text((footer_text_x, footer_text_y), footer_text, fill="white", font=font_medium)

        # 转换为Base64
        buffer = BytesIO()
        poster.save(buffer, format='PNG')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        return f"data:image/png;base64,{image_base64}"

    except Exception as e:
        logger.error(f"Failed to generate share poster: {e}")
        raise


def get_share_text(share_url: str = None) -> dict:
    """
    获取分享文案

    Args:
        share_url: 分享链接

    Returns:
        dict: 包含不同平台的分享文案
    """
    base_url = share_url or "https://opc-agent.onrender.com"

    return {
        "wechat_moment": f"""我发现了一个超棒的OPC创业助手！
研究了100个成功案例，10年产品经理打造，
帮我定制了专属创业方案，3个月就能月入过万！

扫码体验 👇
{base_url}""",
        "wechat_friend": f"""🚀 OPC 超级个体孵化助手

研究发现100个OPC成功案例，
10年产品经理打造，帮你定制专属创业方案！

立即体验：{base_url}

#OPC创业 #超级个体 #副业增收""",
        "weibo": f"""🚀 OPC 超级个体孵化助手

研究发现100个OPC成功案例，
10年产品经理打造，帮你定制专属创业方案！

立即体验：{base_url}

#OPC创业 #超级个体 #副业增收 #创业干货""",
        "default": f"""🚀 OPC 超级个体孵化助手

研究发现100个OPC成功案例，
10年产品经理打造，帮你定制专属创业方案！

立即体验：{base_url}"""
    }
