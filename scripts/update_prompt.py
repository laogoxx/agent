"""
更新agent_llm_config.json中的System Prompt
增加数据库工具的描述
"""
import json

config_path = "config/agent_llm_config.json"

# 读取配置文件
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 在System Prompt的"可用工具"部分添加数据库工具
old_tools_section = """- `get_wechat_group_info()`: 获取微信群信息
  - 返回: 微信群加入方式和入群须知

# 输出格式"""

new_tools_section = """- `get_wechat_group_info()`: 获取微信群信息
  - 返回: 微信群加入方式和入群须知

- `save_user_info(contact_info, target_city, skills, work_experience, interests, risk_tolerance, time_commitment, startup_budget)`: 保存用户信息和创业偏好
  - contact_info: 联系方式（邮箱/手机号/微信号）
  - target_city: 目标城市
  - skills: 专业技能
  - work_experience: 工作经验
  - interests: 个人兴趣
  - risk_tolerance: 风险承受能力
  - time_commitment: 时间投入
  - startup_budget: 启动资金（万元）
  - 返回: 保存结果信息

- `save_payment_and_pdf(contact_info, amount, payment_proof, pdf_url, payment_method)`: 保存支付信息和PDF下载链接
  - contact_info: 联系方式
  - amount: 支付金额
  - payment_proof: 支付凭证
  - pdf_url: PDF下载链接
  - payment_method: 支付方式（默认：微信支付）
  - 返回: 保存结果信息

- `mark_user_joined_group(contact_info)`: 标记用户已加入企业微信群
  - contact_info: 联系方式
  - 返回: 更新结果信息

- `get_customer_info(contact_info)`: 查询客户完整信息
  - contact_info: 联系方式
  - 返回: 客户信息详情

- `save_recommendations(contact_info, project_name, core_advantage, estimated_income, startup_cost, ai_tools)`: 保存推荐项目信息
  - contact_info: 联系方式
  - project_name: 项目名称
  - core_advantage: 核心优势
  - estimated_income: 预期收入
  - startup_cost: 启动成本
  - ai_tools: AI工具推荐（JSON字符串）
  - 返回: 保存结果信息

# 输出格式"""

# 替换System Prompt中的工具描述
config['sp'] = config['sp'].replace(old_tools_section, new_tools_section)

# 保存更新后的配置
with open(config_path, 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=4)

print("✓ System Prompt更新完成，已添加数据库工具描述")
