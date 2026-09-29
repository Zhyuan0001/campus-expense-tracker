"""
校园消费记账系统 - 便携版启动器
打包为独立可执行文件
"""
import webview
import subprocess
import sys
import os
import time
import socket


def get_resource_path(relative_path):
    """获取资源路径（兼容PyInstaller打包）"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的路径
        return os.path.join(sys._MEIPASS, relative_path)
    # 开发环境路径
    return os.path.join(os.path.dirname(__file__), relative_path)


def wait_for_port(port, host='127.0.0.1', timeout=10.0):
    """等待端口可用"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def start_backend():
    """启动FastAPI后端"""
    # 打包环境：将backend目录加入sys.path以便导入main模块
    if hasattr(sys, '_MEIPASS'):
        backend_dir = os.path.join(sys._MEIPASS, 'backend')
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)

        import multiprocessing

        def run_server():
            import uvicorn
            from main import app
            uvicorn.run(app, host='127.0.0.1', port=8000, log_level='error')

        process = multiprocessing.Process(target=run_server, daemon=True)
        process.start()
    else:
        # 开发环境：启动子进程
        backend_dir = get_resource_path('backend')
        process = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', '8000'],
            cwd=backend_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    return process


def create_window():
    """创建桌面窗口"""
    # 等待后端启动
    if not wait_for_port(8000):
        print("后端启动失败")
        sys.exit(1)
    
    # 使用打包的前端文件
    dist_dir = get_resource_path('frontend/dist')
    
    if not os.path.exists(dist_dir):
        print(f"前端文件未找到: {dist_dir}")
        sys.exit(1)
    
    index_path = os.path.join(dist_dir, 'index.html')
    url = f'file://{index_path}'
    
    window = webview.create_window(
        title='校园消费记账系统 v2.0',
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
    process = start_backend()
    print("✓ 后端服务已启动")
    
    # 创建并显示窗口
    window = create_window()
    print("✓ 桌面窗口已创建")
    
    # 启动webview
    webview.start()
    
    print("应用已关闭")


if __name__ == '__main__':
    main()
