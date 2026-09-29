"""
校园消费记账系统 - 桌面应用启动器
使用pywebview将Web应用包装为桌面应用
"""
import webview
import subprocess
import sys
import os
import time
import threading
import socket


def wait_for_port(port, host='127.0.0.1', timeout=5.0):
    """等待端口可用"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def start_backend():
    """启动FastAPI后端"""
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'],
        cwd=backend_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def start_frontend_dev():
    """启动前端开发服务器"""
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=frontend_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )


def create_window():
    """创建桌面窗口"""
    # 等待后端启动
    if not wait_for_port(8000):
        print("后端启动失败")
        sys.exit(1)

    # 开发模式使用localhost:5173，生产模式使用打包的HTML
    if os.environ.get('DEV_MODE'):
        url = 'http://localhost:5173'
        # 等待前端开发服务器
        if not wait_for_port(5173):
            print("前端开发服务器启动失败")
            sys.exit(1)
    else:
        # 生产模式：构建前端并使用打包的HTML
        frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
        dist_dir = os.path.join(frontend_dir, 'dist')
        
        if not os.path.exists(dist_dir):
            print("请先构建前端：cd frontend && npm run build")
            sys.exit(1)
        
        index_path = os.path.join(dist_dir, 'index.html')
        url = f'file://{index_path}'

    window = webview.create_window(
        title='校园消费记账系统',
        url=url,
        width=1200,
        height=800,
        min_size=(800, 600),
        resizable=True,
        text_select=True
    )
    
    return window


def main():
    """主函数"""
    print("正在启动校园消费记账系统...")
    
    # 启动后端
    start_backend()
    print("✓ 后端服务已启动")
    
    # 开发模式下启动前端开发服务器
    if os.environ.get('DEV_MODE'):
        start_frontend_dev()
        print("✓ 前端开发服务器已启动")
    
    # 创建并显示窗口
    window = create_window()
    print("✓ 桌面窗口已创建")
    
    # 启动webview
    webview.start()
    
    print("应用已关闭")


if __name__ == '__main__':
    main()
