import debugpy

try:
    debugpy.listen(("localhost", 5678))  # 监听本地的5678端口
    print("调试器已就绪，等待VS Code连接...")
    # debugpy.wait_for_client()  # 等待调试器连接
except Exception as e:
    print("调试器启动失败：{0}".format(e))
