import tornado.ioloop
import tornado.web
from hashlib import sha1
import os
import time
from hash_ring import HashRing

memcache_servers = ['192.168.0.246:11212','192.168.0.247:11212','192.168.0.249:11212']
weights = {
    '192.168.0.246:11212': 2,
    '192.168.0.247:11212': 2,
    '192.168.0.249:11212': 1
}

ring = HashRing(memcache_servers, weights)


create_session_id = lambda: sha1(bytes('%s%s' % (os.urandom(16), time.time()), encoding='utf-8')).hexdigest()


class Gnn(object):

    container = {
        # '03d025bb5ac29c24c9ca2257634b9b85b2454fb2':{'user':'aa','permission':'xx'},
        # '03d025bb5ac29c24c9csdfsdfsdfsdf85b2454fb2':{'user':'xx','permission':'asdfasdf'}
    }

    def __init__(self, handler):
        """
        self.handler.set_cookie()
        self.handler.get_cookie()
        :param handler:
        """
        self.handler = handler

        random_str = self.handler.get_cookie('_xxxxxxx_')
        if not random_str:
            random_str = create_session_id()
            self.container[random_str] = {}
        else:
            if random_str not in self.container:
                random_str = create_session_id()
                self.container[random_str] = {}
        self.random_str = random_str

        self.handler.set_cookie('_xxxxxxx_', random_str, max_age=60)

    def __getitem__(self, item):
        # import redis
        # host, port = ring.get_node(self.random_str).split(':')
        # conn = redis.Redis(host=host, port=port)
        # return conn.hget(self.random_str, item)
        return self.container[self.random_str].get(item)

    def __setitem__(self, key, value):

        # import redis
        # host, port = ring.get_node(self.random_str).split(':')
        # conn = redis.Redis(host=host, port=port)
        # conn.hset(self.random_str, key, value)
        self.container[self.random_str][key] = value

    def __delitem__(self, key):
        # import redis
        # host, port = ring.get_node(self.random_str).split(':')
        # conn = redis.Redis(host=host, port=port)
        # conn.hdel(self.random_str, key)

        if self.container[self.random_str].get(key):
            del self.container[self.random_str][key]

    def delete(self):
        del self.container[self.random_str]


class SessionHandler(object):
    def initialize(self):
        self.session = Gnn(self)


class LoginHandler(SessionHandler, tornado.web.RequestHandler):

    def get(self):
        self.render('login.html')

    def post(self):
        user = self.get_argument('user')
        pwd = self.get_argument('pwd')
        if user == 'alex' and pwd == '123':
            self.session['user_info'] = user
            self.redirect('/index/')


class IndexHandler(SessionHandler, tornado.web.RequestHandler):

    def get(self):
        user = self.session['user_info']
        if not user:
            self.redirect('/login')
            return

        self.write('登录成功%s' % user)


settings = {
    'template_path': 'templates',
    'static_path': 'staticccccc',
    'static_url_prefix': '/xxx/',
    "cookie_secret": 'asdfasdfdfdfsdfsdfsdf'
}
application = tornado.web.Application([
    (r"/login", LoginHandler),
    (r"/index", IndexHandler),
], **settings)

if __name__ == "__main__":
    # 创建socket对象
    application.listen(8888)
    # conn,add = socket.accept()
    tornado.ioloop.IOLoop.instance().start()