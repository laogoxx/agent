#!/bin/bash
# 一键推送代码到 GitHub
# 用法：bash scripts/push_to_github.sh https://github.com/用户名/仓库名.git

set -e

echo "========================================"
echo "GitHub 代码推送工具"
echo "========================================"
echo ""

# 检查是否提供了仓库地址
if [ -z "$1" ]; then
    echo "❌ 错误: 请提供 GitHub 仓库地址"
    echo ""
    echo "用法:"
    echo "  bash scripts/push_to_github.sh https://github.com/你的用户名/你的仓库名.git"
    echo ""
    echo "示例:"
    echo "  bash scripts/push_to_github.sh https://github.com/zhangsan/opc-agent.git"
    echo ""
    echo "如何获取仓库地址:"
    echo "  1. 打开你的 GitHub 仓库"
    echo "  2. 点击绿色的 'Code' 按钮"
    echo "  3. 复制 HTTPS 地址"
    echo ""
    exit 1
fi

GITHUB_REPO_URL="$1"

# 验证仓库地址格式
if [[ ! $GITHUB_REPO_URL =~ ^https://github\.com/.*\.git$ ]]; then
    echo "❌ 错误: 仓库地址格式不正确"
    echo ""
    echo "正确的格式应该是:"
    echo "  https://github.com/用户名/仓库名.git"
    echo ""
    echo "你输入的地址:"
    echo "  $GITHUB_REPO_URL"
    echo ""
    exit 1
fi

# 提取仓库信息
REPO_NAME=$(basename -s .git "$GITHUB_REPO_URL")
USERNAME=$(basename $(dirname "$GITHUB_REPO_URL"))

echo "📋 仓库信息:"
echo "   用户名: $USERNAME"
echo "   仓库名: $REPO_NAME"
echo "   完整地址: $GITHUB_REPO_URL"
echo ""

# 确认操作
read -p "确认推送代码到这个仓库？(yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ 已取消操作"
    exit 0
fi

echo ""
echo "========================================"
echo "开始推送代码..."
echo "========================================"
echo ""

# 步骤1: 检查是否有远程仓库
echo "📝 [1/6] 检查远程仓库配置..."
if git remote get-url origin &>/dev/null; then
    EXISTING_REMOTE=$(git remote get-url origin)
    echo "   发现已有远程仓库: $EXISTING_REMOTE"
    read -p "   是否替换为新的仓库？(yes/no): " replace_remote
    if [ "$replace_remote" = "yes" ]; then
        git remote remove origin
        echo "   ✓ 已移除旧的远程仓库"
    else
        echo "   ⚠️  使用现有远程仓库"
        GITHUB_REPO_URL="$EXISTING_REMOTE"
    fi
fi

# 步骤2: 添加远程仓库
if ! git remote get-url origin &>/dev/null; then
    echo "📝 [2/6] 添加远程仓库..."
    git remote add origin "$GITHUB_REPO_URL"
    echo "   ✓ 远程仓库添加成功"
else
    echo "📝 [2/6] 跳过（远程仓库已存在）"
fi

# 步骤3: 验证远程仓库
echo "📝 [3/6] 验证远程仓库..."
git remote -v
echo "   ✓ 远程仓库验证成功"

# 步骤4: 添加所有文件
echo ""
echo "📝 [4/6] 添加所有文件..."
git add .
echo "   ✓ 文件添加成功"

# 步骤5: 提交代码
echo "📝 [5/6] 提交代码..."
if git diff --cached --quiet; then
    echo "   ℹ️  没有需要提交的更改"
else
    git commit -m "准备 Render 部署"
    echo "   ✓ 代码提交成功"
fi

# 步骤6: 推送到 GitHub
echo "📝 [6/6] 推送到 GitHub..."
echo ""
echo "⏳ 正在推送，请稍候..."
echo ""

# 尝试推送
if git branch -M main 2>/dev/null || git checkout -b main 2>/dev/null; then
    if git push -u origin main; then
        echo ""
        echo "========================================"
        echo "✅ 代码推送成功！"
        echo "========================================"
        echo ""
        echo "📝 仓库地址:"
        echo "   $GITHUB_REPO_URL"
        echo ""
        echo "🎉 下一步:"
        echo "   1. 访问你的 GitHub 仓库"
        echo "   2. 访问 https://dashboard.render.com"
        echo "   3. 点击 New + → New Blueprint"
        echo "   4. 选择你的仓库并创建项目"
        echo ""
        echo "📚 详细教程:"
        echo "   查看 docs/Render快速开始.md"
        echo ""
    else
        echo ""
        echo "========================================"
        echo "❌ 推送失败"
        echo "========================================"
        echo ""
        echo "可能的原因:"
        echo "  1. 仓库地址错误"
        echo "  2. 需要身份验证（用户名和 Token）"
        echo "  3. 网络问题"
        echo ""
        echo "📖 如何解决:"
        echo "  1. 检查仓库地址是否正确"
        echo "  2. 如果要求输入密码，请使用 GitHub Personal Access Token"
        echo "  3. Token 获取地址: https://github.com/settings/tokens"
        echo ""
        echo "🆘 需要帮助？"
        echo "   查看文档: docs/GitHub推送代码指南.md"
        echo ""
        exit 1
    fi
else
    echo "❌ 无法创建或切换到 main 分支"
    exit 1
fi
