# OPC创业指导助手

基于AI的OPC（一人公司）超级个体孵化助手，帮助用户发现、规划和启动适合的创业项目。

---

## 🌟 功能特性

- ✅ 智能对话交互
- ✅ 创业项目推荐（基于用户画像）
- ✅ AI工具推荐（含评分系统）
- ✅ PDF创业指导文档生成
- ✅ 微信支付收款（个人收款码）
- ✅ 企业微信群入群邀请
- ✅ 主动欢迎功能

---

## 🚀 快速开始

### 方式1：本地运行（测试）

**Linux/Mac:**
```bash
./scripts/start.sh
```

**Windows:**
```bash
双击运行 start.bat
```

访问：`http://localhost:8080`

---

### 方式2：云服务器部署（推荐）⭐

**快速部署（5分钟）:**

1. 购买云服务器（阿里云/腾讯云 2核2G，¥60/月）
2. 连接服务器：`ssh root@你的服务器IP`
3. 上传项目：`scp -r /workspace/projects/* root@你的服务器IP:/opt/opc-agent/`
4. 运行部署：`cd /opt/opc-agent && ./scripts/deploy.sh`
5. 配置环境变量：`nano /opt/opc-agent/.env`
6. 重启服务：`supervisorctl restart opc-agent`
7. 访问服务：`http://你的服务器IP:8080`

详细步骤请查看：[快速部署指南.md](docs/快速部署指南.md)

---

## 📋 环境要求

- Python 3.10+
- pip（Python包管理器）
- `.env` 文件（配置收款码和群二维码）

---

## 🔧 配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

复制配置模板：
```bash
cp .env.example .env
```

编辑配置：
```bash
nano .env
```

必需配置：
```bash
WECHAT_QRCODE_URL=https://你的微信收款码链接
WECHAT_GROUP_QRCODE_URL=https://你的群二维码链接
PAYMENT_PRICE=68.00
```

### 3. 运行测试

```bash
# 测试收款工具
python tests/test_simple_payment.py

# 测试群工具
python tests/test_wechat_group_info.py

# 测试完整流程
python tests/test_complete_flow.py
```

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [快速部署指南.md](docs/快速部署指南.md) | 5分钟快速部署（推荐新手） |
| [部署指南.md](docs/部署指南.md) | 完整部署指南（所有方式） |
| [部署准备完成.md](docs/部署准备完成.md) | 部署准备和后续维护 |
| [配置完成总结.md](docs/配置完成总结.md) | 配置说明和维护指南 |
| [收款功能使用指南.md](docs/收款功能使用指南.md) | 收款功能详细说明 |
| [主动欢迎功能说明.md](docs/主动欢迎功能说明.md) | 欢迎功能详细说明 |
| [功能更新总结.md](docs/功能更新总结.md) | 功能更新历史 |

---

## 🛠️ 脚本

| 脚本 | 说明 |
|------|------|
| [scripts/deploy.sh](scripts/deploy.sh) | 云服务器一键部署 |
| [scripts/start.sh](scripts/start.sh) | 本地启动（Linux/Mac） |
| [scripts/start.bat](scripts/start.bat) | 本地启动（Windows） |

---

## 📊 项目结构

```
.
├── config/                    # 配置文件
│   ├── agent_llm_config.json # Agent配置
│   └── payment_config.json.example # 支付配置模板
├── docs/                      # 文档
│   ├── 快速部署指南.md
│   ├── 部署指南.md
│   └── ...
├── scripts/                   # 脚本
│   ├── deploy.sh             # 部署脚本
│   ├── start.sh              # 启动脚本（Linux/Mac）
│   └── start.bat             # 启动脚本（Windows）
├── src/                       # 源代码
│   ├── agents/               # Agent代码
│   │   └── agent.py          # 主Agent
│   ├── storage/              # 存储层
│   │   └── memory/           # 内存存储
│   └── tools/                # 工具
│       ├── pdf_generator.py  # PDF生成
│       ├── simple_payment.py # 收款功能
│       └── wechat_group_info.py # 群信息
├── tests/                     # 测试
│   ├── test_simple_payment.py
│   ├── test_wechat_group_info.py
│   ├── test_complete_flow.py
│   └── demo_auto_welcome.py
├── .env.example               # 环境变量模板
├── .env                       # 环境变量（需自行创建）
├── requirements.txt           # 依赖
└── README.md                  # 本文件
```

---

## 💡 使用流程

### 用户使用流程

1. 用户打开对话框
2. Agent主动欢迎（介绍自己）
3. 用户咨询创业问题
4. Agent收集用户信息
5. Agent推荐创业项目
6. Agent推荐AI工具
7. 用户要求查看支付方式
8. Agent显示收款码
9. 用户扫码支付
10. 用户告知支付凭证
11. Agent确认支付并生成PDF
12. Agent显示入群二维码
13. 用户扫码加入群
14. 享受持续服务

---

## 🔧 维护

### 常用命令

```bash
# 服务管理（云服务器）
supervisorctl status      # 查看状态
supervisorctl restart    # 重启服务
supervisorctl stop       # 停止服务

# 日志查看（云服务器）
tail -f /var/log/opc-agent.out.log    # 应用日志
tail -f /var/log/opc-agent.err.log    # 错误日志

# 本地测试
python tests/test_complete_flow.py    # 完整流程测试
```

### 定期维护

- **每日**：检查服务状态、查看日志
- **每周**：检查群二维码有效期（7天）
- **每月**：更新系统、备份数据

### 更新二维码

企业微信群二维码每7天过期，需要更新：

```bash
# 1. 在企业微信中重新生成群二维码
# 2. 上传到ImgBB，复制链接

# 3. 编辑.env文件
nano /opt/opc-agent/.env

# 4. 更新 WECHAT_GROUP_QRCODE_URL

# 5. 重启服务
supervisorctl restart opc-agent
```

---

## 🎯 推荐配置

### 测试环境
- CPU：1核
- 内存：2GB
- 价格：约30-50元/月

### 生产环境
- CPU：2核
- 内存：4GB
- 带宽：3Mbps
- 价格：约60-100元/月

### 推荐云服务商

| 服务商 | 配置 | 价格 |
|--------|------|------|
| 阿里云 | 2核2G | ¥60/月 |
| 腾讯云 | 2核2G | ¥50/月 |
| 华为云 | 2核2G | ¥60/月 |

---

## ❓ 常见问题

### Q：服务启动失败？

A：查看错误日志
```bash
tail -f /var/log/opc-agent.err.log
```

常见原因：
- 依赖未安装：`pip install -r requirements.txt`
- .env配置错误：检查配置文件格式
- 端口被占用：修改端口或停止占用进程

### Q：无法访问服务？

A：检查以下几点：
- 服务是否正常运行：`supervisorctl status`
- 防火墙是否开放端口：`ufw status`
- 安全组是否开放8080端口（云服务商控制台）

### Q：二维码不显示？

A：检查.env配置：
```bash
cat .env | grep QRCODE_URL
```

确保链接正确且可以公开访问。

---

## 📞 获取帮助

### 文档

- [快速部署指南](docs/快速部署指南.md) - 5分钟快速部署
- [部署指南](docs/部署指南.md) - 完整部署指南
- [配置完成总结](docs/配置完成总结.md) - 配置说明

### 测试

```bash
# 完整流程测试
python tests/test_complete_flow.py

# 欢迎功能演示
python tests/demo_auto_welcome.py
```

---

## 📝 更新日志

### v1.0.0 (2025-01-23)

- ✅ 完成Agent对话功能
- ✅ 完成项目推荐功能
- ✅ 完成AI工具推荐（含评分系统）
- ✅ 完成PDF生成功能
- ✅ 完成微信收款功能
- ✅ 完成企业微信群功能
- ✅ 完成主动欢迎功能
- ✅ 完成部署脚本和文档

---

## 🎉 开始使用

1. **选择部署方式**
   - 测试：本地运行
   - 正式：云服务器部署

2. **配置服务**
   - 配置收款码
   - 配置群二维码
   - 测试功能

3. **开始运营**
   - 分享给用户
   - 收集反馈
   - 持续优化

---

**祝你创业成功！** 🚀💪

如有任何问题，请查看文档或联系技术支持。
