import os
import hashlib
import json
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, List
from langchain.tools import tool

# 注册中文字体（使用系统自带的中文字体）
try:
    font_paths = [
        '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
    ]
    for font_path in font_paths:
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
            break
    else:
        print("Warning: Chinese font not found, using default font")
except Exception as e:
    print(f"Warning: Failed to register Chinese font: {e}")

def analyze_city(city: str, user_skills: str, user_experience: str, user_interests: str) -> str:
    """
    分析城市环境（简化版，不使用 LLM）

    Args:
        city: 城市名称
        user_skills: 用户技能
        user_experience: 用户经验
        user_interests: 用户兴趣

    Returns:
        str: 城市分析结果（JSON格式）
    """
    # 返回默认城市分析
    return json.dumps({
        "population": f"{city}作为重要城市，人口密集，消费能力强，年轻群体占比高。",
        "industry": f"{city}产业结构多元化，涵盖科技、金融、文化、服务业等多个领域。",
        "business": f"{city}商业环境成熟，产业链完整，创业生态活跃。",
        "policy": f"{city}政府大力支持创新创业，提供多项优惠政策和资金扶持。",
        "opportunities": "数字化升级、新消费、科技服务等领域机会众多。",
        "recommendations": "结合当地产业特色，发挥自身优势，选择合适的创业方向。"
    }, ensure_ascii=False)

@tool
def generate_opc_pdf_simple(
    user_info: str,
    city: str,
    projects: str
) -> str:
    """
    生成OPC创业指导PDF文档（简化版，不上传对象存储）。

    Args:
        user_info: 用户信息（地址、技能、经验、兴趣）
        city: 用户所在城市
        projects: 推荐的创业项目列表（JSON字符串或格式化文本）

    Returns:
        str: PDF 文件路径
    """
    # 解析用户信息
    user_data = {
        "city": city,
        "skills": "",
        "experience": "",
        "interests": ""
    }

    # 确保user_info是字符串
    if isinstance(user_info, dict):
        if isinstance(user_info.get("user_info"), str):
            user_info_str = user_info.get("user_info", "")
        else:
            user_info_str = str(user_info)
    elif isinstance(user_info, list):
        user_info_str = " ".join(str(item) for item in user_info)
    else:
        user_info_str = user_info

    # 从user_info中提取信息
    if isinstance(user_info_str, str) and ("地址" in user_info_str or "城市" in user_info_str):
        for line in user_info_str.split('\n'):
            if isinstance(line, str):
                if "地址" in line or "城市" in line:
                    user_data["city"] = line.split("：")[-1].strip() if "：" in line else city
                elif "技能" in line:
                    user_data["skills"] = line.split("：")[-1].strip() if "：" in line else line
                elif "经验" in line:
                    user_data["experience"] = line.split("：")[-1].strip() if "：" in line else line
                elif "兴趣" in line:
                    user_data["interests"] = line.split("：")[-1].strip() if "：" in line else line

    # 城市深度分析
    city_analysis_json = analyze_city(
        user_data["city"],
        user_data["skills"],
        user_data["experience"],
        user_data["interests"]
    )

    # 尝试解析城市分析JSON
    try:
        city_analysis = json.loads(city_analysis_json)
        if isinstance(city_analysis, dict):
            city_analysis = {k: str(v) for k, v in city_analysis.items()}
    except:
        city_analysis = {
            "population": f"{user_data['city']}人口密集，消费能力强。",
            "industry": f"{user_data['city']}产业结构多元化。",
            "business": f"{user_data['city']}商业环境成熟。",
            "policy": f"{user_data['city']}政府支持创新创业。",
            "opportunities": "数字化、新消费等领域机会多。",
            "recommendations": "结合当地特色，发挥自身优势。"
        }

    # 创建临时PDF文件
    temp_pdf_path = "/tmp/opc_guide.pdf"

    try:
        # 创建PDF文档
        doc = SimpleDocTemplate(
            temp_pdf_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # 获取样式
        styles = getSampleStyleSheet()

        # 定义自定义样式
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            fontName='ChineseFont' if os.path.exists('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc') else 'Helvetica-Bold'
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#444444'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='ChineseFont' if os.path.exists('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc') else 'Helvetica-Bold'
        )

        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=8,
            leading=16,
            fontName='ChineseFont' if os.path.exists('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc') else 'Helvetica'
        )

        # 构建文档内容
        story = []

        # 标题
        story.append(Paragraph(f"{user_data['city']}OPC超级个体创业指导手册", title_style))
        story.append(Spacer(1, 20))

        # 用户画像分析
        story.append(Paragraph("一、用户画像分析", heading_style))
        story.append(Paragraph(user_info.replace('\n', '<br/>'), normal_style))
        story.append(Spacer(1, 20))

        # 城市环境深度分析
        story.append(PageBreak())
        story.append(Paragraph(f"二、{user_data['city']}创业环境深度分析", heading_style))
        story.append(Paragraph(f"<b>人口结构：</b>{city_analysis.get('population', '')}", normal_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>产业结构：</b>{city_analysis.get('industry', '')}", normal_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>商业环境：</b>{city_analysis.get('business', '')}", normal_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>政府政策：</b>{city_analysis.get('policy', '')}", normal_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>创业机会：</b>{city_analysis.get('opportunities', '')}", normal_style))
        story.append(Spacer(1, 8))
        story.append(Paragraph(f"<b>针对性建议：</b>{city_analysis.get('recommendations', '')}", normal_style))
        story.append(Spacer(1, 20))

        # 推荐创业项目
        story.append(PageBreak())
        story.append(Paragraph("三、精选创业项目推荐", heading_style))
        story.append(Paragraph(f"以下项目基于您的个人特点和{user_data['city']}的市场环境精选而成：", normal_style))
        story.append(Spacer(1, 10))
        story.append(Paragraph(projects.replace('\n', '<br/>'), normal_style))
        story.append(Spacer(1, 20))

        # 针对性启动指南
        story.append(Paragraph("四、针对性启动指南", heading_style))
        story.append(Paragraph(f"基于{user_data['city']}的市场环境，建议按以下步骤启动：", normal_style))
        story.append(Paragraph(f"<b>1. 市场调研：</b>深入了解{user_data['city']}目标用户需求和本地竞争对手情况。", normal_style))
        story.append(Paragraph(f"<b>2. 最小可行产品（MVP）：</b>快速推出核心功能，在{user_data['city']}市场进行验证。", normal_style))
        story.append(Paragraph(f"<b>3. 品牌建设：</b>建立专业形象，针对{user_data['city']}用户特点设计营销策略。", normal_style))
        story.append(Paragraph(f"<b>4. 客户获取：</b>利用{user_data['city']}本地资源和渠道，快速获取首批客户。", normal_style))
        story.append(Paragraph(f"<b>5. 持续迭代：</b>根据{user_data['city']}市场反馈不断优化产品和服务。", normal_style))

        # 生成PDF
        doc.build(story)

        return f"✅ PDF文档已生成！\n\n📄 文件路径：{temp_pdf_path}\n\n💡 提示：当前为简化版本，PDF保存在服务器上。"

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"❌ 生成PDF失败：{str(e)}\n\n详细信息：\n{error_details}"

  feat: 添加 pdf_generator_simple.py，简化 PDF 生成
