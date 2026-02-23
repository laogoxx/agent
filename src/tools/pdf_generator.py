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
    使用大模型分析城市环境
    
    Args:
        city: 城市名称
        user_skills: 用户技能
        user_experience: 用户经验
        user_interests: 用户兴趣
    
    Returns:
        str: 城市分析结果（JSON格式）
    """
    try:
        ctx = new_context(method="analyze_city")
        client = LLMClient(ctx=ctx)
        
        system_prompt = """你是一位专业的城市创业分析师，擅长分析城市环境对创业的影响。
请分析指定城市的人口结构、产业结构、商业环境和政府政策，并给出针对性的创业建议。
输出格式为JSON，包含以下字段：
- population: 人口结构分析
- industry: 产业结构分析
- business: 商业环境分析
- policy: 政府政策支持
- opportunities: 创业机会
- recommendations: 针对性建议"""
        
        user_prompt = f"""请分析{city}的创业环境，特别是针对以下背景的创业者：
技能：{user_skills}
经验：{user_experience}
兴趣：{user_interests}

请提供详细的城市分析和针对性的创业建议，返回JSON格式。"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        response = client.invoke(messages=messages, temperature=0.7)
        
        # 提取文本内容
        if isinstance(response.content, str):
            return response.content
        elif isinstance(response.content, list):
            if response.content and isinstance(response.content[0], str):
                return " ".join(response.content)
            else:
                text_parts = []
                for item in response.content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text_parts.append(item.get("text", ""))
                return " ".join(text_parts)
        return str(response.content)
        
    except Exception as e:
        print(f"Error analyzing city: {e}")
        # 返回默认分析
        return json.dumps({
            "population": f"{city}作为一线城市，人口密集，消费能力强，年轻群体占比高。",
            "industry": f"{city}产业结构多元化，涵盖科技、金融、文化、服务业等多个领域。",
            "business": f"{city}商业环境成熟，产业链完整，创业生态活跃。",
            "policy": f"{city}政府大力支持创新创业，提供多项优惠政策和资金扶持。",
            "opportunities": "数字化升级、新消费、科技服务等领域机会众多。",
            "recommendations": "结合当地产业特色，发挥自身优势，选择合适的创业方向。"
        }, ensure_ascii=False)

@tool
def generate_opc_pdf(
    user_info: str,
    city: str,
    projects: str
) -> str:
    """
    生成OPC创业指导PDF文档并上传到对象存储，包含城市深度分析。
    
    Args:
        user_info: 用户信息（地址、技能、经验、兴趣）
        city: 用户所在城市
        projects: 推荐的创业项目列表（JSON字符串或格式化文本）
    
    Returns:
        str: 对象存储中PDF的下载URL
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
        # 如果是字典，直接使用其中的值
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
        # 确保所有值都是字符串
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
        
        subheading_style = ParagraphStyle(
            'CustomSubheading',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#666666'),
            spaceAfter=10,
            spaceBefore=15,
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
        
        # 第一部分：用户画像分析
        story.append(Paragraph("一、用户画像分析", heading_style))
        story.append(Paragraph(user_info.replace('\n', '<br/>'), normal_style))
        story.append(Spacer(1, 20))
        
        # 第二部分：城市环境深度分析
        story.append(PageBreak())
        story.append(Paragraph(f"二、{user_data['city']}创业环境深度分析", heading_style))
        
        # 2.1 人口结构
        story.append(Paragraph("2.1 人口结构分析", subheading_style))
        story.append(Paragraph(city_analysis.get("population", ""), normal_style))
        story.append(Spacer(1, 10))
        
        # 2.2 产业结构
        story.append(Paragraph("2.2 产业结构分析", subheading_style))
        story.append(Paragraph(city_analysis.get("industry", ""), normal_style))
        story.append(Spacer(1, 10))
        
        # 2.3 商业环境
        story.append(Paragraph("2.3 商业环境分析", subheading_style))
        story.append(Paragraph(city_analysis.get("business", ""), normal_style))
        story.append(Spacer(1, 10))
        
        # 2.4 政府政策
        story.append(Paragraph("2.4 政府政策支持", subheading_style))
        story.append(Paragraph(city_analysis.get("policy", ""), normal_style))
        story.append(Spacer(1, 10))
        
        # 2.5 创业机会
        story.append(Paragraph("2.5 创业机会分析", subheading_style))
        story.append(Paragraph(city_analysis.get("opportunities", ""), normal_style))
        story.append(Spacer(1, 10))
        
        # 2.6 针对性建议
        story.append(Paragraph("2.6 针对性建议", subheading_style))
        story.append(Paragraph(city_analysis.get("recommendations", ""), normal_style))
        story.append(Spacer(1, 20))
        
        # 第三部分：推荐创业项目
        story.append(PageBreak())
        story.append(Paragraph("三、精选创业项目推荐", heading_style))
        story.append(Paragraph(f"以下项目基于您的个人特点和{user_data['city']}的市场环境精选而成：", normal_style))
        story.append(Spacer(1, 10))
        
        # 尝试解析projects为JSON
        try:
            if projects.strip().startswith('[') or projects.strip().startswith('{'):
                projects_data = json.loads(projects)
                if isinstance(projects_data, list):
                    for idx, project in enumerate(projects_data, 1):
                        story.append(Paragraph(f"项目 {idx}", subheading_style))
                        
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
        
        # 第四部分：启动指南（针对性）
        story.append(PageBreak())
        story.append(Paragraph("四、针对性启动指南", heading_style))
        story.append(Paragraph(f"基于{user_data['city']}的市场环境，建议按以下步骤启动：", normal_style))
        story.append(Paragraph(f"<b>1. 市场调研：</b>深入了解{user_data['city']}目标用户需求和本地竞争对手情况。", normal_style))
        story.append(Paragraph(f"<b>2. 最小可行产品（MVP）：</b>快速推出核心功能，在{user_data['city']}市场进行验证。", normal_style))
        story.append(Paragraph(f"<b>3. 品牌建设：</b>建立专业形象，针对{user_data['city']}用户特点设计营销策略。", normal_style))
        story.append(Paragraph(f"<b>4. 客户获取：</b>利用{user_data['city']}本地资源和渠道，快速获取首批客户。", normal_style))
        story.append(Paragraph(f"<b>5. 持续迭代：</b>根据{user_data['city']}市场反馈不断优化产品和服务。", normal_style))
        story.append(Spacer(1, 20))
        
        # 第五部分：AI工具推荐
        story.append(Paragraph("五、AI工具推荐", heading_style))
        story.append(Paragraph("以下是适合OPC使用的AI/Agent工具，可大幅提升效率：", normal_style))
        story.append(Spacer(1, 10))
        
        # AI工具列表（分类展示，带评分）
        ai_tools = [
            # 大模型类
            ("文心一言（国产）", "百度", "文案生成/多模态创作", "免费/付费", "大模型", "4.8", "4.7", "4.9"),
            ("通义千问（国产）", "阿里", "文档分析/长文本生成", "免费/付费", "大模型", "4.7", "4.8", "4.8"),
            ("智谱清言（国产）", "智谱AI", "代码生成/逻辑推理", "免费/付费", "大模型", "4.6", "4.7", "4.7"),
            ("Copy.ai（可选）", "Copy.ai", "营销文案/广告创意", "付费", "大模型", "4.5", "4.3", "4.2"),
            ("Kimi（国产）", "月之暗霞", "超长文本阅读/总结", "免费/付费", "大模型", "4.7", "4.5", "4.8"),
            
            # 图像/视频生成类
            ("即梦（国产）", "字节跳动", "AI短视频自动生成", "免费/付费", "视频生成", "4.8", "4.5", "4.9"),
            ("ImagineArt（可选）", "ImagineArt", "AI图像创作/设计", "免费/付费", "图像生成", "4.3", "4.4", "4.5"),
            ("HeyGen（可选）", "HeyGen", "AI数字人视频制作", "付费", "视频生成", "4.5", "4.6", "4.0"),
            ("Runway（可选）", "Runway", "AI视频编辑/特效", "付费", "视频生成", "4.4", "4.7", "3.8"),
            ("文心一格（国产）", "百度", "AI绘画/海报设计", "免费/付费", "图像生成", "4.5", "4.4", "4.8"),
            ("Midjourney（可选）", "Midjourney", "顶级AI绘画/设计", "付费", "图像生成", "4.2", "4.9", "3.5"),
            ("剪映AI（国产）", "字节跳动", "AI视频剪辑/字幕", "免费/付费", "视频生成", "4.9", "4.5", "4.9"),
            ("Canva AI（可选）", "Canva", "智能设计工具", "免费/付费", "图像生成", "4.8", "4.3", "4.7"),
            
            # Agent/自动化类
            ("Coze（国产）", "字节跳动", "AI Agent工作流", "免费", "Agent平台", "4.9", "4.6", "5.0"),
            ("CrewAI", "开源工具", "多Agent协作编排", "免费/付费", "Agent平台", "4.2", "4.5", "4.8"),
            ("AutoGen", "微软", "多Agent对话系统", "免费", "Agent平台", "4.0", "4.4", "5.0"),
            ("n8n", "开源工具", "工作流自动化/集成", "免费/付费", "自动化", "4.3", "4.6", "4.7"),
            ("Make（可选）", "Make", "可视化工作流自动化", "付费", "自动化", "4.7", "4.5", "4.1"),
            ("OpenCompass", "开源工具", "大模型评测/开发", "免费", "Agent平台", "4.1", "4.3", "5.0"),
            ("Dify", "开源工具", "AI应用快速开发", "免费/付费", "Agent平台", "4.5", "4.6", "4.8"),
            ("FastGPT（国产）", "开源工具", "知识库问答系统", "免费/付费", "Agent平台", "4.6", "4.4", "4.9"),
            ("Gumloop", "开源工具", "可视化业务流程自动化", "免费/付费", "自动化", "4.4", "4.5", "4.6"),
            
            # 数据管理类
            ("飞书多维表格（国产）", "字节跳动", "数据管理/协作", "免费/付费", "数据管理", "4.8", "4.7", "4.9"),
            ("Notion（可选）", "Notion", "知识管理/协作", "免费/付费", "数据管理", "4.6", "4.5", "4.3"),
            ("Airtable（可选）", "Airtable", "在线数据库/表格", "免费/付费", "数据管理", "4.5", "4.6", "4.2"),
        ]
        
        ai_tool_data = [["工具名称", "开发商", "核心功能", "收费方式", "类别", "易用性", "功能完整度", "性价比"]]
        for tool in ai_tools:
            ai_tool_data.append(list(tool))
        
        ai_table = Table(ai_tool_data, colWidths=[1.6*inch, 1.0*inch, 1.6*inch, 0.8*inch, 0.8*inch, 0.6*inch, 0.7*inch, 0.6*inch])
        ai_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'ChineseFont' if os.path.exists('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc') else 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
        ]))
        story.append(ai_table)
        story.append(Spacer(1, 10))
        
        # 评分说明
        rating_explain_style = ParagraphStyle(
            'RatingExplain',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#555555'),
            leftIndent=10,
            fontName='ChineseFont' if os.path.exists('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc') else 'Helvetica'
        )
        story.append(Paragraph("<b>评分说明：</b>", rating_explain_style))
        story.append(Paragraph("• <b>易用性</b>：工具的学习曲线和操作便捷度（1-5分，5分最高）", rating_explain_style))
        story.append(Paragraph("• <b>功能完整度</b>：工具功能的丰富程度和实用性（1-5分，5分最高）", rating_explain_style))
        story.append(Paragraph("• <b>性价比</b>：工具的功能与价格比例（1-5分，5分最高）", rating_explain_style))
        story.append(Paragraph("• 评分基于用户反馈和专家评估，仅供参考", rating_explain_style))
        story.append(Spacer(1, 20))
        
        # 第六部分：风险提示
        story.append(Paragraph("六、风险提示", heading_style))
        story.append(Paragraph("<b>1. 资金风险：</b>预留足够的启动资金，避免过早扩张。", normal_style))
        story.append(Paragraph("<b>2. 时间管理：</b>合理分配时间，避免过度承诺。", normal_style))
        story.append(Paragraph(f"<b>3. 法律合规：</b>了解{user_data['city']}相关法律法规，确保合规经营。", normal_style))
        story.append(Paragraph(f"<b>4. 竞争风险：</b>保持敏锐度，及时调整策略应对{user_data['city']}市场竞争。", normal_style))
        story.append(Paragraph("<b>5. 心理准备：</b>创业过程充满挑战，保持积极心态。", normal_style))
        story.append(Spacer(1, 30))
        
        # 免责声明
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#999999'),
            alignment=1,
            fontName='ChineseFont' if os.path.exists('/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc') else 'Helvetica'
        )
        story.append(Paragraph("免责声明：本指南仅供参考，具体创业决策请根据实际情况谨慎评估。", disclaimer_style))
        
        # 生成PDF
        doc.build(story)
        
        # 读取PDF文件内容
        with open(temp_pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        # 计算MD5哈希
        md5_hash = hashlib.md5(pdf_content).hexdigest()[:8]
        
        # 生成文件名（只包含英文和数字，避免中文字符）
        city_english = "unknown"
        if user_data["city"] == "北京":
            city_english = "beijing"
        elif user_data["city"] == "上海":
            city_english = "shanghai"
        elif user_data["city"] == "广州":
            city_english = "guangzhou"
        elif user_data["city"] == "深圳":
            city_english = "shenzhen"
        elif user_data["city"] == "杭州":
            city_english = "hangzhou"
        elif user_data["city"] == "成都":
            city_english = "chengdu"
        elif user_data["city"] == "武汉":
            city_english = "wuhan"
        elif user_data["city"] == "西安":
            city_english = "xian"
        else:
            # 其他城市，使用拼音首字母
            city_english = "city"
        
        file_name = f"opc_guide_{city_english}_{md5_hash}.pdf"
        
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
            expire_time=86400
        )
        
        return f"✅ PDF文档已生成！\n\n📄 下载链接（有效期24小时）：\n{download_url}\n\n💡 提示：请尽快下载保存，链接过期后将无法访问。"
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return f"❌ 生成PDF失败：{str(e)}\n\n详细信息：\n{error_details}"
