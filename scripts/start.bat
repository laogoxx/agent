@echo off
REM OPC Agent Windows 启动脚本

echo ==========================================
echo      OPC Agent 本地启动
echo ==========================================
echo.

REM 检查.env文件
if not exist ".env" (
    echo ❌ 错误：未找到 .env 文件
    echo 请先复制 .env.example 为 .env 并配置
    echo 命令：copy .env.example .env
    echo 然后编辑：notepad .env
    pause
    exit /b 1
)

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到 Python
    echo 请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 获取端口号
set PORT=%1
if "%PORT%"=="" set PORT=8080

echo 🚀 启动 OPC Agent...
echo 端口：%PORT%
echo 访问地址：http://localhost:%PORT%
echo.
echo 按 Ctrl+C 停止服务
echo.
echo ==========================================
echo.

REM 启动服务
python src\main.py -m http -p %PORT%

pause
