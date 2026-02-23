"""
企业微信群工具测试脚本
"""
import sys
import os

# 添加项目根目录到Python路径
project_root = os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects')
sys.path.insert(0, project_root)

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.tools.wechat_group_info import get_wechat_group_info

def test_get_wechat_group_info():
    """测试获取企业微信群信息"""
    print("=" * 60)
    print("测试：获取企业微信群信息")
    print("=" * 60)

    try:
        # 调用工具
        result = get_wechat_group_info.invoke({})
        print(f"✓ 获取企业微信群信息成功")
        print(f"\n返回结果:\n{result}\n")

        # 检查是否包含二维码链接
        if "https://ibb.co/PZrnNCT2" in result:
            print("✓ 群二维码链接正确显示")
        else:
            print("✗ 群二维码链接未正确显示")

        # 检查是否包含群名称
        if "OPC超级个体孵化群" in result:
            print("✓ 群名称正确显示")
        else:
            print("✗ 群名称未正确显示")

        return True
    except Exception as e:
        print(f"✗ 获取企业微信群信息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_get_wechat_group_info()
    sys.exit(0 if success else 1)
