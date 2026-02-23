# 🚀 Render 部署指南（免费云部署）

本指南帮助你使用 **Render** 平台免费部署 OPC 超级个体孵化助手。

---

## 📋 什么是 Render？

Render 是一个现代化的云平台，提供：
- ✅ **永久免费层**：适用于小型应用
- ✅ **一键部署**：支持从 GitHub 自动部署
- ✅ **自动 HTTPS**：免费 SSL 证书
- ✅ **自动扩展**：根据流量自动扩容
- ✅ **数据库支持**：提供 PostgreSQL 数据库

---

## ⚡ 快速开始（5分钟部署）

### 步骤1：准备项目代码

#### 1.1 创建 Flask 应用入口

创建文件 `src/main_flask.py`：

```python
from flask import Flask, request, jsonify
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agents.agent import build_agent
from langgraph.checkpoint.memory import MemorySaver

app = Flask(__name__)

# 初始化 Agent
agent = build_agent()
checkpointer = MemorySaver()

@app.route('/')
def index():
    """主页"""
    return """
    <h1>OPC 超级个体孵化助手</h1>
    <p>服务运行正常！</p>
    <p>API 端点：POST /api/chat</p>
    """

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天接口"""
    try:
        data = request.json
        message = data.get('message', '')

        if not message:
            return jsonify({'error': '请提供消息内容'}), 400

        # 调用 Agent
        config = {"configurable": {"thread_id": "default"}}
        response = agent.invoke({"messages": [message]}, config)

        # 提取回复
        reply = response['messages'][-1].content

        return jsonify({
            'success': True,
            'reply': reply
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

#### 1.2 更新 requirements.txt

确保包含 Flask：

```bash
echo "flask==3.0.0" >> requirements.txt
echo "gunicorn==21.2.0" >> requirements.txt
```

#### 1.3 创建 runtime.txt（可选）

指定 Python 版本：

```bash
echo "python-3.11.8" > runtime.txt
```

#### 1.4 创建 .render 目录和启动脚本

```bash
mkdir -p .render
```

创建 `.render/start.sh`：

```bash
#!/bin/bash
set -e

# 设置 Python 路径
export PYTHONPATH=/opt/render/project/src:$PYTHONPATH

# 启动服务
gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 src.main_flask:app
```

```bash
chmod +x .render/start.sh
```

---

### 步骤2：准备环境变量

#### 2.1 在本地创建 .env 文件

```bash
cat > .env << EOF
# 数据库配置（使用 Render PostgreSQL）
DATABASE_URL=postgresql://用户名:密码@主机:端口/数据库名

# 微信支付配置
WECHAT_QRCODE_URL=https://ibb.co/0y0jXhCv
WECHAT_GROUP_QRCODE_URL=https://ibb.co/PZrnNCT2

# 产品配置
PAYMENT_PRICE=68.00
PRODUCT_NAME=OPC创业指导PDF

# 模型配置（环境变量会自动加载）
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
COZE_INTEGRATION_MODEL_BASE_URL=your_base_url
EOF
```

#### 2.2 创建 Render 环境变量模板

```bash
cat > render_env.txt << EOF
# 数据库配置（Render PostgreSQL）
DATABASE_URL=postgresql://用户名:密码@主机:端口/数据库名

# 微信支付配置
WECHAT_QRCODE_URL=https://ibb.co/0y0jXhCv
WECHAT_GROUP_QRCODE_URL=https://ibb.co/PZrnNCT2

# 产品配置
PAYMENT_PRICE=68.00
PRODUCT_NAME=OPC创业指导PDF

# 模型配置
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
COZE_INTEGRATION_MODEL_BASE_URL=your_base_url
EOF
```

---

### 步骤3：推送到 GitHub

#### 3.1 初始化 Git 仓库（如果还没有）

```bash
cd /workspace/projects
git init
git add .
git commit -m "Initial commit: OPC 超级个体孵化助手"
```

#### 3.2 推送到 GitHub

```bash
# 添加远程仓库
git remote add origin https://github.com/你的用户名/你的仓库名.git

# 推送代码
git branch -M main
git push -u origin main
```

---

### 步骤4：在 Render 上创建项目

#### 4.1 注册 Render 账号

1. 访问 https://render.com
2. 点击 "Sign Up" 注册账号（支持 GitHub 登录）
3. 验证邮箱

#### 4.2 创建新的 Web Service

1. 登录后，点击 "New +" → "Web Service"
2. 选择 GitHub 仓库
3. 选择刚才推送的仓库
4. 配置以下参数：

```
Name: opc-agent
Region: Singapore (或离你最近的区域)
Branch: main
Runtime: Python 3
Build Command: pip install -r requirements.txt && python scripts/init_db.py init
Start Command: bash .render/start.sh
```

5. 点击 "Create Web Service"

#### 4.3 配置环境变量

在创建过程中或创建后，进入 "Environment" 标签页，添加以下环境变量：

```
# 数据库配置（稍后配置）
DATABASE_URL=postgresql://用户名:密码@主机:端口/数据库名

# 微信支付配置
WECHAT_QRCODE_URL=https://ibb.co/0y0jXhCv
WECHAT_GROUP_QRCODE_URL=https://ibb.co/PZrnNCT2

# 产品配置
PAYMENT_PRICE=68.00
PRODUCT_NAME=OPC创业指导PDF

# 模型配置
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key
COZE_INTEGRATION_MODEL_BASE_URL=your_base_url
```

---

### 步骤5：创建 PostgreSQL 数据库

#### 5.1 创建数据库

1. 在 Render 控制台，点击 "New +" → "PostgreSQL"
2. 配置数据库：

```
Name: opc-agent-db
Database: opc_agent
User: opc_user
Region: 与 Web Service 相同区域
Plan: Free (免费层)
```

3. 点击 "Create Database"

#### 5.2 获取数据库连接字符串

1. 进入数据库详情页面
2. 找到 "Connections" 部分
3. 复制 "Internal Database URL"

示例格式：
```
postgresql://opc_user:xxxxx@dpg-xxxxx.oregon-postgres.render.com/opc_agent
```

#### 5.3 更新 Web Service 环境变量

1. 回到 Web Service 设置页面
2. 找到 "Environment" 标签页
3. 更新 `DATABASE_URL` 环境变量为刚才复制的连接字符串
4. 点击 "Save Changes"
5. 触发重新部署

---

### 步骤6：验证部署

#### 6.1 检查部署状态

1. 在 Render 控制台查看 Web Service 状态
2. 等待部署完成（约3-5分钟）
3. 状态变为 "Live" 表示部署成功

#### 6.2 测试服务

**方式1：通过 Render 提供的 URL 测试**

```bash
# 获取服务 URL（在 Render 控制台查看）
curl https://opc-agent.onrender.com/api/health

# 测试聊天接口
curl -X POST https://opc-agent.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，我想做创业"}'
```

**方式2：通过浏览器测试**

1. 访问 `https://opc-agent.onrender.com`
2. 应该看到 "OPC 超级个体孵化助手" 页面

---

## 🔧 高级配置

### 配置自定义域名

#### 1. 购买域名

在阿里云、腾讯云或 Namecheap 购买域名。

#### 2. 在 Render 配置自定义域名

1. 进入 Web Service 设置页面
2. 找到 "Custom Domains" 部分
3. 点击 "Add Domain"
4. 输入你的域名（如：`agent.yourdomain.com`）
5. Render 会提供 DNS 记录

#### 3. 配置 DNS

在你的域名注册商处添加 DNS 记录：

```
类型: CNAME
主机记录: agent
记录值: opc-agent.onrender.com
TTL: 600
```

等待 DNS 生效（通常需要10-30分钟）。

---

### 配置健康检查

在 Render 控制台，进入 "Advanced" 设置：

```
Health Check Path: /api/health
Health Check Interval: 30s
Health Check Timeout: 10s
Health Check Threshold: 3
```

---

### 配置自动扩展

1. 进入 "Scaling" 标签页
2. 配置扩展规则：

```
Min Instances: 1
Max Instances: 10
Target CPU: 70%
Target Memory: 70%
```

---

## 💰 费用说明

### Render 免费层

| 资源 | 免费额度 |
|------|---------|
| Web Service | 750 小时/月 |
| CPU | 0.1 核 |
| 内存 | 512MB |
| PostgreSQL | 256MB 存储 |
| 带宽 | 100GB/月 |

### 超出免费层

如果超出免费额度，Render 按实际使用计费：
- Web Service：约 $0.02/GB 小时
- PostgreSQL：约 $0.05/GB 月
- 带宽：约 $0.10/GB

**预计费用**（小型应用）：$5-10/月

---

## 📊 监控和日志

### 查看日志

1. 进入 Web Service 页面
2. 点击 "Logs" 标签
3. 实时查看应用日志

### 查看指标

1. 进入 "Metrics" 标签
2. 查看 CPU、内存、响应时间等指标

### 设置告警

1. 进入 "Alerts" 标签
2. 配置告警规则（如：CPU > 90%）

---

## 🔒 安全建议

1. **启用 HTTPS**：Render 自动提供免费 SSL 证书
2. **环境变量**：敏感信息（API Key、数据库密码）通过环境变量配置
3. **数据库安全**：使用强密码，限制访问 IP
4. **定期更新**：及时更新依赖包

---

## 🐛 常见问题

### Q1：部署失败，构建错误

**A**：检查以下几点：
- `requirements.txt` 是否完整
- Python 版本是否正确
- 启动命令是否正确

查看构建日志：
```
Render 控制台 → Web Service → Logs
```

### Q2：服务启动失败

**A**：检查以下内容：
- 端口是否正确（使用 `$PORT` 环境变量）
- 数据库连接是否正常
- 依赖是否正确安装

查看运行日志：
```
tail -f /var/log/opc-agent.out.log
```

### Q3：数据库连接失败

**A**：
1. 检查 `DATABASE_URL` 是否正确
2. 确认数据库是否已创建
3. 确认数据库是否在运行

### Q4：服务响应慢

**A**：
1. 检查免费层限制（512MB 内存可能不够）
2. 考虑升级到付费计划
3. 优化代码和数据库查询

### Q5：如何更新代码

**A**：
```bash
# 本地修改代码
git add .
git commit -m "Update code"
git push

# Render 会自动检测更新并重新部署
```

---

## 📚 参考资源

- Render 官方文档：https://render.com/docs
- Render Python 部署指南：https://render.com/docs/deploy-python
- Render 免费层说明：https://render.com/docs/free

---

## ✅ 部署检查清单

部署完成后，确认以下内容：

- [ ] Web Service 状态为 "Live"
- [ ] 数据库已创建并运行正常
- [ ] 健康检查通过（`/api/health` 返回 200）
- [ ] 聊天接口正常工作
- [ ] 环境变量配置正确
- [ ] HTTPS 证书正常
- [ ] 日志正常输出，无错误

---

## 🎉 完成！

恭喜你，OPC 超级个体孵化助手已成功部署到 Render！

现在你可以：
1. 通过浏览器访问服务
2. 测试聊天功能
3. 集成到你的网站或应用
4. 配置自定义域名
5. 监控服务运行状态

如有问题，请参考 Render 官方文档或联系 Render 支持。