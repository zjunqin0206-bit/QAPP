"""
示例 HTTP 服务文件。

这个文件是远程项目初始化时自带的最小示例服务，
作用是演示如何用 Python 标准库启动一个简单的 HTTPServer。
当前真实训练服务已经迁移到 app.py + FastAPI，
因此这个文件更多保留为最小示例，不承担主业务逻辑。
"""

from http.server import BaseHTTPRequestHandler, HTTPServer


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """
    最小请求处理器。

    这个类的实现思路是只覆盖 GET 请求，
    并返回固定的 Hello World 内容，用来说明标准库 HTTPServer 的基本响应流程。
    """

    def do_GET(self):
        """
        处理 GET 请求。

        这个函数的实现思路是按最小流程返回 200 状态码、响应头和固定响应体，
        不引入路由分发或业务判断，保持示例代码足够简单。
        """
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"Hello, World!")


def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    """
    启动示例 HTTP 服务。

    这个函数的实现思路是把服务地址、处理器类型和启动动作集中到一个入口中，
    使文件既可被直接运行，也可被外部调用作为最小示例服务。
    """
    server_address = ("", 8080)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == "__main__":
    run()
