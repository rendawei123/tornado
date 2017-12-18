import tornado.ioloop
import tornado.web


class Input(object):
    def __init__(self, val):
        self.val = val

    # 如果对象中有__str__方法，那么在前端显示的时候都显示的是__str__下面的数据
    def __str__(self):
        return '<input type="text" name="n1" value="{0}">'.format(self.val)


class MainHandler(tornado.web.RequestHandler):
    def get(self):

        form_list = [
            Input('alex'),
            Input('tom')
        ]

        self.render('index.html', **{'form_list': form_list})


settings = {
    'template_path': 'templates',
}

application = tornado.web.Application([
    (r"/index", MainHandler),
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
