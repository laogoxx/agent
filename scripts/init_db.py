"""
数据库初始化脚本
创建客户信息相关的数据表
"""
import sys
import os

# 添加多个可能的路径到 Python 路径，确保能找到模块
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_dir = os.path.join(project_root, 'src')

# 添加项目根目录、src 目录和当前目录到 Python 路径
sys.path.insert(0, project_root)
sys.path.insert(0, src_dir)
sys.path.insert(0, script_dir)

# 确保工作目录正确
os.chdir(src_dir)

# 导入模块（使用 try-except 处理构建阶段的导入错误）
try:
    from sqlalchemy import text
    from storage.database.db import get_engine
    from storage.database.customer_models import Base
    import logging

    logger = logging.getLogger(__name__)
except ImportError as e:
    # 构建阶段可能无法导入模块，记录警告但不退出
    if __name__ != "__main__":
        # 只在导入时输出警告，不在主脚本运行时
        print(f"Warning: Import failed in build phase: {e}")
    else:
        # 作为主脚本运行时，重新抛出错误
        raise


def init_customer_tables():
    """初始化客户信息相关数据表"""
    engine = get_engine()

    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("✓ 客户信息数据表创建成功")

        # 验证表是否创建成功
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('users', 'user_profiles', 'recommendations', 'payments', 'service_records')
            """))
            tables = [row[0] for row in result.fetchall()]

            expected_tables = ['users', 'user_profiles', 'recommendations', 'payments', 'service_records']
            missing_tables = [t for t in expected_tables if t not in tables]

            if missing_tables:
                logger.warning(f"⚠️  以下表未创建: {missing_tables}")
            else:
                logger.info(f"✓ 所有数据表创建成功: {', '.join(tables)}")

        return True

    except Exception as e:
        logger.error(f"✗ 数据表创建失败: {e}")
        raise


def drop_customer_tables():
    """删除客户信息相关数据表（谨慎使用！）"""
    engine = get_engine()

    try:
        # 删除所有表
        Base.metadata.drop_all(bind=engine)
        logger.info("✓ 客户信息数据表删除成功")
        return True

    except Exception as e:
        logger.error(f"✗ 数据表删除失败: {e}")
        raise


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "init"

    if action == "init":
        print("正在初始化客户信息数据表...")
        init_customer_tables()
        print("✓ 初始化完成")
    elif action == "drop":
        print("⚠️  警告：即将删除所有客户信息数据表！")
        confirm = input("确认删除？(yes/no): ")
        if confirm.lower() == "yes":
            drop_customer_tables()
            print("✓ 删除完成")
        else:
            print("✓ 已取消")
    else:
        print(f"未知操作: {action}")
        print("可用操作: init (创建表), drop (删除表)")
