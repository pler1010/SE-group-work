import subprocess
import sys
import os
import importlib

def check_and_install_dependencies():
    """检查并安装所需的依赖"""
    required_packages = [
        "Flask==2.0.1",
        "Werkzeug==2.0.1",
        "numpy",
        "opencv-python"
    ]
    
    for package in required_packages:
        package_name = package.split('==')[0]
        try:
            importlib.import_module(package_name.lower().replace('-', '_'))
            print(f"✓ {package_name} 已安装")
        except ImportError:
            print(f"⚠ 正在安装 {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✓ {package} 安装成功")
            except subprocess.CalledProcessError:
                print(f"✗ 无法安装 {package}")
                return False
    return True

if __name__ == "__main__":
    print("正在检查依赖...")
    if check_and_install_dependencies():
        print("所有依赖已安装，正在启动应用...")
        try:
            from app import app
            app.run(debug=True)
        except Exception as e:
            print(f"启动应用时出错: {e}")
    else:
        print("某些依赖安装失败，请手动安装依赖后再尝试运行应用。")
