# ⚡ Render 部署快速开始（10分钟搞定）

本指南帮助你在10分钟内完成 OPC Agent 的 Render 部署。

---

## 🎯 部署流程概览

```
准备项目 → 推送 GitHub → 创建 Render 项目 → 配置数据库 → 完成
```

---

## 🚀 快速部署（3个命令）

### 第1步：准备项目（2分钟）

```bash
# 运行准备脚本
bash scripts/prepare_render.sh

# 提交代码
git add .
git commit -m "准备 Render 部署"
git push
```

### 第2步：创建 Render 项目（5分钟）

1. 访问 https://dashboard.render.com
2. 点击 "New +" → "New Blueprint"
3. 连接 GitHub，选择你的仓库
4. Render 会自动读取 `render.yaml` 配置
5. 点击 "Apply" 开始部署

### 第3步：配置环境变量（3分钟）

1. 进入创建的 Web Service
2. 找到 "Environment" 标签页
3. 添加以下环境变量：

```
COZE_WORKLOAD_IDENTITY_API_KEY=你的API_Key
COZE_INTEGRATION_MODEL_BASE_URL=你的Base_URL
```

4. 点击 "Save Changes" 重新部署

**完成！** 🎉

---

## 📝 详细步骤

### 1️⃣ 准备项目

#### 运行准备脚本

```bash
cd /workspace/projects
bash scripts/prepare_render.sh
```

这个脚本会自动创建：
- ✅ Flask 应用入口 (`src/main_flask.py`)
- ✅ 启动脚本 (`.render/start.sh`)
- ✅ Render 配置文件 (`render.yaml`)
- ✅ 环境变量模板 (`render_env.txt`)

#### 更新环境变量

编辑 `render_env.txt`，填入你的 API Key：

```bash
nano render_env.txt
```

修改以下内容：
```
COZE_WORKLOAD_IDENTITY_API_KEY=你的真实API_Key
COZE_INTEGRATION_MODEL_BASE_URL=你的真实Base_URL
```

保存退出（Ctrl+X, Y, Enter）。

#### 提交代码

```bash
git add .
git commit -m "准备 Render 部署"
git push
```

---

### 2️⃣ 在 Render 上创建项目

#### 方式A：使用 Blueprint（推荐）

1. 访问 https://dashboard.render.com
2. 点击 "New +" → "New Blueprint"
3. 授权访问你的 GitHub
4. 选择 OPC Agent 的仓库
5. Render 会自动识别 `render.yaml` 配置
6. 检查配置，点击 "Apply"

**等待部署完成**（约3-5分钟）。

#### 方式B：手动创建

**步骤 1：创建 PostgreSQL 数据库**

1. 点击 "New +" → "PostgreSQL"
2. 配置：

```
Name: opc-agent-db
Database: opc_agent
User: opc_user
Region: Singapore
Plan: Free
```

3. 点击 "Create Database"
4. 复制 "Internal Database URL"

**步骤 2：创建 Web Service**

1. 点击 "New +" → "Web Service"
2. 连接 GitHub，选择仓库
3. 配置：

```
Name: opc-agent
Region: Singapore
Branch: main
Runtime: Python 3
Build Command: pip install -r requirements.txt && python scripts/init_db.py init
Start Command: bash .render/start.sh
```

4. 点击 "Create Web Service"

**步骤 3：配置环境变量**

进入 Web Service → Environment，添加：

```
DATABASE_URL=刚才复制的数据库连接字符串
WECHAT_QRCODE_URL=https://ibb.co/0y0jXhCv
WECHAT_GROUP_QRCODE_URL=https://ibb.co/PZrnNCT2
PAYMENT_PRICE=68.00
PRODUCT_NAME=OPC创业指导PDF
COZE_WORKLOAD_IDENTITY_API_KEY=你的API_Key
COZE_INTEGRATION_MODEL_BASE_URL=你的Base_URL
```

---

### 3️⃣ 验证部署

#### 检查部署状态

在 Render 控制台查看：
- Web Service 状态应为 "Live"
- 数据库状态应为 "Available"

#### 测试服务

**方式1：浏览器访问**

打开浏览器，访问：
```
https://opc-agent.onrender.com
```

应该看到 "OPC 超级个体孵化助手" 页面。

**方式2：API 测试**

```bash
# 健康检查
curl https://opc-agent.onrender.com/api/health

# 聊天测试
curl -X POST https://opc-agent.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "你好，我想做创业"}'
```

---

## 🔧 常见问题速查

### Q: 部署失败，提示 "Build failed"

**A**: 检查以下几点：
1. `requirements.txt` 是否包含所有依赖
2. `src/main_flask.py` 是否存在
3. `render.yaml` 格式是否正确

查看构建日志：
```
Render 控制台 → Web Service → Logs
```

### Q: 服务启动失败

**A**:
1. 检查 `.render/start.sh` 是否有执行权限
2. 检查端口号配置（必须使用 `$PORT`）
3. 查看错误日志

### Q: 数据库连接失败

**A**:
1. 确认 `DATABASE_URL` 环境变量是否正确
2. 确认数据库是否在运行
3. 确认数据库区域与 Web Service 相同

### Q: 如何更新代码？

**A**:
```bash
# 本地修改代码
git add .
git commit -m "更新功能"
git push

# Render 会自动重新部署
```

---

## 💰 费用说明

Render 免费层包含：
- ✅ 750 小时/月（足够小型应用）
- ✅ 512MB 内存
- ✅ 256MB PostgreSQL 存储
- ✅ 100GB 带宽

**预计费用**：$0/月（小型应用）

如果超出免费层：
- Web Service：约 $0.02/GB 小时
- PostgreSQL：约 $0.05/GB 月

---

## 📚 更多资源

- 详细教程：`docs/Render部署指南.md`
- Render 官方文档：https://render.com/docs
- Render 免费层：https://render.com/docs/free

---

## ✅ 检查清单

部署完成后，确认：

- [ ] Web Service 状态为 "Live"
- [ ] 数据库状态为 "Available"
- [ ] 健康检查通过（访问 `/api/health`）
- [ ] 聊天接口正常工作
- [ ] 环境变量配置正确

---

## 🎉 完成！

你的 OPC Agent 已成功部署到 Render！

**访问地址**：
- 主页：`https://opc-agent.onrender.com`
- API：`https://opc-agent.onrender.com/api/health`

**后续优化**：
- 配置自定义域名
- 配置自动扩展
- 设置告警通知
- 优化性能和成本

---

## 🆘 获取帮助

遇到问题？

1. 查看详细教程：`docs/Render部署指南.md`
2. 查看 Render 日志
3. 查看 Render 官方文档
4. 联系 Render 支持

祝部署顺利！🚀