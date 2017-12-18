### Tornado

##### 什么是异步非阻塞

就是服务端在遇到IO阻塞的时候，cpu空闲下来了，在这段时间cpu可以发送其他的请求

异步非阻塞实例

```python
class AsyncHandler(tornado.web.RequestHandler):
    @gen.coroutine
    def get(self):
        future = Future()
        tornado.ioloop.IOLoop.current().add_timeout(time.time() + 5, self.doing)
        yield future


    def doing(self, *args, **kwargs):
        self.write('async')
        self.finish()
```

tornado如果想要实现异步非阻塞，必须如下操作

1. 添加装饰器
2. yield future对象
3. future必须要有回调函数
4. 回调函数是执行set_result来检测的（tornado不用自己写）

其本质就是一个Future对象下面的set_result("laksdjfl")什么时候执行前面在时间阻塞的时候，当时间结束之后会自动执行set_result，网络IO的话，当请求回来的时候也是自动执行set_result

##### 自定义异步非阻塞框架

参考tornado的异步非阻塞

效果：希望一个线程在空闲（IO阻塞）时间去执行一些其他操作

如果这样，当请求过来了，我们就应该进行判断，如果请求是一个一般的简单强求，我们就直接返回数据，但是如果这是一个复杂的IO请求的话，我们就应该先把这个请求放在某地让他执行，然后自己干其他的事情，当我们检测到请求执行完后，再将结果返回给用户。这样就能同时执行多个请求了

##### 链接数据库

如果把tornado当作一般的web框架，链接数据库的时候和其他的一样使用pymysql或者sqlachemy

如果要使用异步非阻塞功能，就要使用Tornado-MySQL的插件

```python
"""
需要先安装支持异步操作Mysql的类库： 
    Tornado-MySQL： https://github.com/PyMySQL/Tornado-MySQL#installation
    
    pip3 install Tornado-MySQL

"""

import tornado.web
from tornado import gen

import tornado_mysql
from tornado_mysql import pools

POOL = pools.Pool(
    dict(host='127.0.0.1', port=3306, user='root', passwd='123', db='cmdb'),
    max_idle_connections=1,
    max_recycle_sec=3)


@gen.coroutine
def get_user_by_conn_pool(user):
    cur = yield POOL.execute("SELECT SLEEP(%s)", (user,))
    row = cur.fetchone()
    raise gen.Return(row)


@gen.coroutine
def get_user(user):
    conn = yield tornado_mysql.connect(host='127.0.0.1', port=3306, user='root', passwd='123', db='cmdb',
                                       charset='utf8')
    cur = conn.cursor()
    # yield cur.execute("SELECT name,email FROM web_models_userprofile where name=%s", (user,))
    yield cur.execute("select sleep(10)")
    row = cur.fetchone()
    cur.close()
    conn.close()
    raise gen.Return(row)


class LoginHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('login.html')

    @gen.coroutine
    def post(self, *args, **kwargs):
        user = self.get_argument('user')
        data = yield gen.Task(get_user, user)
        if data:
            print(data)
            self.redirect('http://www.oldboyedu.com')
        else:
            self.render('login.html')


application = tornado.web.Application([
    (r"/login", LoginHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
```

##### 什么是IO多路复用

io多路复用就是使用select/poll/epoll + socket来检测是否发生变化，是的socket的最大使用，select效率最低，他在内部使用轮巡来检测，并且最大支持1024，但是epoll使用linux特有的边缘出发，也就是回调函数来检测

用在客户端可以在爬虫中使用，用在服务端可以检测请求