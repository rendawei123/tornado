import tornado.ioloop
import tornado.web
import copy
import re


class Field(object):
    def __init__(self, name, required):
        self.required = required
        self.status = True
        self.error = None
        self.value = None
        self.name = name


class CharField(Field):

    def valid(self, input_value):
        self.value = input_value
        if self.required:
            if not input_value:
                self.status = False
                self.error = {'required': '不能为空'}
                return

        # self.value = input_value

    def __str__(self):
        return '<input type="text" name="%s" value="%s">' % (self.name, self.value)


class EmailField(Field):
    REX = '^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+'

    def valid(self, input_value):
        self.value = input_value
        if self.required:
            if not input_value:
                self.status = False
                self.error = {'required': '邮箱不能为空'}
                return

        if not re.match(EmailField.REX, input_value):
            print(input_value)
            self.status = False
            self.error = {'invalid': '邮箱格式错误'}
            return

        # self.value = input_value

    def __str__(self):
        return '<input type="text" name="%s" value="%s">' % (self.name, self.value)


class Form(object):
    def __init__(self, handler):
        self.handler = handler  # handler里面封装的是接收到的字段
        fields = {}
        for k, v in self.__class__.__dict__.items():
            if isinstance(v, Field):
                fields[k] = copy.deepcopy(v)  # 为了保证用户之间的独立性，相互不干扰

        self.fields = fields
        self.errors = {}
        self.cleaned_data = {}

    def is_valid(self):
        flag = True

        for name, field in self.fields.items():   # name,field分别为字典名和字段对象
            # 获取前端发过来的字段
            input_value = self.handler.get_body_argument(name)
            # if field.required:
            #     if not input_value:
            #         flag = False
            #         self.errors[name] = {'required': '必填'}
            #     else:
            #         self.cleaned_data[name] = input_value
            # else:
            #     self.cleaned_data[name] = input_value
            field.valid(input_value)
            if not field.status:
                flag = False
                self.errors[name] = field.error
            self.cleaned_data[name] = field.value

        return flag


class LoginForm(Form):
    user = CharField(name='user', required=True)
    email = EmailField(name='email', required=True)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        form = LoginForm(self)

        self.render('index1.html', form=form)

    def post(self, *args, **kwargs):
        # user = self.get_body_argument('user')  # 获取请求体里面的东西
        # email = self.get_body_argument('email')
        form = LoginForm(self)
        if form.is_valid():
            print(form.cleaned_data)
        else:
            print(form.errors)
        # self.write('post请求成功')
        self.render('index1.html', form=form)

settings = {
    'template_path': 'templates',
}

application = tornado.web.Application([
    (r"/index", MainHandler),
], **settings)

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
