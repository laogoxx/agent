import os
import hashlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from typing import Dict, List
from langchain.tools import tool
from coze_coding_dev_sdk.s3 import S3SyncStorage

# 注册中文字体（使用系统自带的中文字体）
try:
    # 尝试使用常见的中文字体
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
        # 如果找不到中文字体，使用默认字体（可能不支持中文）
        print("Warning: Chinese font not found, using default font")
except Exception as e:
    print(f"Warning: Failed to register Chinese font: {e}")

@tool
def generate_opc_pdf(
    user_info: str,
    projects: str
) -> str:
    """
    生成OPC创业指导PDF文档并上传到对象存储。
    
    Args:
        user_info: 用户信息（地址、技能、经验、兴趣）
        projects: 推荐的创业项目列表（JSON字符串或格式化文本）
    
    Returns:
        str: 对象存储中PDF的下载URL
    """
    import json
    from io import BytesIO
    
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
        story.append(Paragraph("OPC超级个体创业指导手册", title_style))
        story.append(Spacer(1, 20))
        
        # 用户信息部分
        story.append(Paragraph("一、用户画像分析", heading_style))
        story.append(Paragraph(user_info.replace('\n', '<br/>'), normal_style))
        story.append(Spacer(1, 20))
        
        # 推荐项目部分
        story.append(Paragraph("二、精选创业项目推荐", heading_style))
        story.append(Paragraph("以下项目基于您的个人特点和市场趋势精选而成：", normal_style))
        story.append(Spacer(1, 10))
        
        # 尝试解析projects为JSON
        try:
            if projects.strip().startswith('[') or projects.strip().startswith('{'):
                projects_data = json.loads(projects)
                if isinstance(projects_data, list):
                    for idx, project in enumerate(projects_data, 1):
                        story.append(Paragraph(f"项目 {idx}", heading_style))
                        
                        # 项目内容表格
                        project_data = []
                        for key, value in project.items():
                            if key != 'name':
                                project_data.append([
                                    f"<b>{key}:</b>",
                                    str(value)
                                ])
                        
                        if project_data:
                            table = Table(project_data, colWidths=[2*inch, 4*inch])
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F0F8FF')),
                                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2E86AB')),
                                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont' if os.path.exists('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc') else 'Helvetica'),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                                ('TOPPADDING', (0, 0), (-1, -1), 8),
                                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
                            ]))
                            story.append(table)
                        
                        story.append(Spacer(1, 15))
                else:
                    story.append(Paragraph(projects.replace('\n', '<br/>'), normal_style))
            else:
                story.append(Paragraph(projects.replace('\n', '<br/>'), normal_style))
        except json.JSONDecodeError:
            story.append(Paragraph(projects.replace('\n', '<br/>'), normal_style))
        
        # 启动指南部分
        story.append(Paragraph("三、启动指南", heading_style))
        story.append(Paragraph("<b>1. 市场调研：</b>深入了解目标用户需求和竞争对手情况。", normal_style))
        story.append(Paragraph("<b>2. 最小可行产品（MVP）：</b>快速推出核心功能，验证市场需求。", normal_style))
        story.append(Paragraph("<b>3. 品牌建设：</b>建立专业形象，包括网站、社交媒体等。", normal_style))
        story.append(Paragraph("<b>4. 客户获取：</b>制定营销策略，快速获取首批客户。", normal_style))
        story.append(Paragraph("<b>5. 持续迭代：</b>根据用户反馈不断优化产品和服务。", normal_style))
        story.append(Spacer(1, 20))
        
        # 风险提示部分
        story.append(Paragraph("四、风险提示", heading_style))
        story.append(Paragraph("<b>1. 资金风险：</b>预留足够的启动资金，避免过早扩张。", normal_style))
        story.append(Paragraph("<b>2. 时间管理：</b>合理分配时间，避免过度承诺。", normal_style))
        story.append(Paragraph("<b>3. 法律合规：</b>了解相关法律法规，确保合规经营。", normal_style))
        story.append(Paragraph("<b>4. 竞争风险：</b>保持敏锐度，及时调整策略应对竞争。", normal_style))
        story.append(Paragraph("<b>5. 心理准备：</b>创业过程充满挑战，保持积极心态。", normal_style))
        story.append(Spacer(1, 30))
        
        # 免责声明
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#999999'),
            alignment=1,  # 居中
            fontName='ChineseFont' if os.path.exists('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc') else 'Helvetica'
        )
        story.append(Paragraph("免责声明：本指南仅供参考，具体创业决策请根据实际情况谨慎评估。", disclaimer_style))
        
        # 生成PDF
        doc.build(story)
        
        # 读取PDF文件内容
        with open(temp_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        # 计算MD5哈希（两段）
        md5_hash = hashlib.md5(pdf_content).hexdigest()[:8]
        
        # 生成文件名
        file_name = f"opc_guide_{md5_hash}.pdf"
        
        # 初始化对象存储
        storage = S3SyncStorage(
            endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
            access_key="",
            secret_key="",
            bucket_name=os.getenv("COZE_BUCKET_NAME"),
            region="cn-beijing",
        )
        
        # 上传PDF到对象存储
        key = storage.upload_file(
            file_content=pdf_content,
            file_name=file_name,
            content_type="application/pdf"
        )
        
        # 生成预签名URL（有效期24小时）
        download_url = storage.generate_presigned_url(
            key=key,
            expire_time=86400  # 24小时
        )
        
        return f"✅ PDF文档已生成！\n\n📄 下载链接（有效期24小时）：\n{download_url}\n\n💡 提示：请尽快下载保存，链接过期后将无法访问。"
        
    except Exception as e:
        return f"❌ 生成PDF失败：{str(e)}"
