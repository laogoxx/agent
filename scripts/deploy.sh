#!/bin/bash

# OPC Agent 一键部署脚本
# 适用于 Ubuntu 20.04+

set -e

echo "========================================================"
echo "     OPC Agent 一键部署脚本"
echo "========================================================"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用root用户运行此脚本${NC}"
    exit 1
fi

# 显示安装信息
echo -e "${GREEN}开始安装 OPC Agent...${NC}"
echo "安装目录：/opt/opc-agent"
echo "端口：8080"
echo ""

# 更新系统
echo -e "${YELLOW}1. 更新系统...${NC}"
apt update && apt upgrade -y

# 安装Python
echo -e "${YELLOW}2. 安装Python 3.10+...${NC}"
apt install python3.10 python3-pip python3-venv -y

# 创建项目目录
echo -e "${YELLOW}3. 创建项目目录...${NC}"
mkdir -p /opt/opc-agent
cd /opt/opc-agent

# 创建虚拟环境
echo -e "${YELLOW}4. 创建虚拟环境...${NC}"
python3 -m venv venv
source venv/bin/activate

# 升级pip
echo -e "${YELLOW}5. 升级pip...${NC}"
pip install --upgrade pip

# 安装依赖
echo -e "${YELLOW}6. 安装Python依赖...${NC}"
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo -e "${RED}错误：未找到 requirements.txt 文件${NC}"
    echo "请先将项目文件上传到 /opt/opc-agent 目录"
    exit 1
fi

# 配置环境变量
echo -e "${YELLOW}7. 配置环境变量...${NC}"
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}已创建 .env 文件，请手动编辑配置${NC}"
        echo "编辑命令：nano /opt/opc-agent/.env"
    else
        echo -e "${RED}错误：未找到 .env.example 文件${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}.env 文件已存在${NC}"
fi

# 安装supervisor
echo -e "${YELLOW}8. 安装supervisor...${NC}"
pip install supervisor

# 创建supervisor配置
echo -e "${YELLOW}9. 配置supervisor...${NC}"
mkdir -p /etc/supervisor/conf.d

cat > /etc/supervisor/conf.d/opc-agent.conf <<EOF
[program:opc-agent]
command=/opt/opc-agent/venv/bin/python /opt/opc-agent/src/main.py -m http -p 8080
directory=/opt/opc-agent
user=root
autostart=true
autorestart=true
startretries=3
stderr_logfile=/var/log/opc-agent.err.log
stdout_logfile=/var/log/opc-agent.out.log
EOF

# 配置防火墙
echo -e "${YELLOW}10. 配置防火墙...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 8080/tcp
    echo -e "${GREEN}已允许 8080 端口${NC}"
else
    echo -e "${YELLOW}ufw 未安装，跳过防火墙配置${NC}"
fi

# 启动服务
echo -e "${YELLOW}11. 启动服务...${NC}"
supervisord -c /etc/supervisor/supervisord.conf
supervisorctl update
supervisorctl start opc-agent

# 等待服务启动
sleep 5

# 检查服务状态
echo -e "${YELLOW}12. 检查服务状态...${NC}"
if supervisorctl status opc-agent | grep -q "RUNNING"; then
    echo -e "${GREEN}✓ 服务启动成功！${NC}"
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    echo "查看日志：tail -f /var/log/opc-agent.err.log"
    exit 1
fi

# 完成
echo ""
echo "========================================================"
echo -e "${GREEN}     部署完成！${NC}"
echo "========================================================"
echo ""
echo "服务地址："
echo "  http://$(curl -s ifconfig.me):8080"
echo ""
echo "常用命令："
echo "  查看状态：supervisorctl status"
echo "  重启服务：supervisorctl restart opc-agent"
echo "  停止服务：supervisorctl stop opc-agent"
echo "  查看日志：tail -f /var/log/opc-agent.out.log"
echo ""
echo "下一步："
echo "  1. 编辑 .env 文件配置：nano /opt/opc-agent/.env"
echo "  2. 重启服务：supervisorctl restart opc-agent"
echo "  3. 访问服务测试"
echo ""
echo -e "${YELLOW}注意：请先编辑 .env 文件配置收款码和群二维码！${NC}"
echo "========================================================"
