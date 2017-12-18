import tornado.web
import tornado.ioloop
import time
from tornado import gen

from tornado.concurrent import Future
from tornado import httpclient  # 发送http请求的模块


class MainHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        print('开始')
        future = Future()
        # 暂停10秒中执行done回调函数
        # tornado.ioloop.IOLoop.current().add_timeout(time.time() + 10, self.done)
        # yield future
        http = httpclient.AsyncHTTPClient()
        yield http.fetch('https://cn.bing.com/', self.done)

    def done(self):
        self.write('返回内容')
        self.finish()


settings = {
    'templates_path': 'templates',
    'static_path': 'static',
}


application = tornado.web.Application([
    (r"/index", MainHandler),
], **settings)


if __name__ == '__main__':
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()