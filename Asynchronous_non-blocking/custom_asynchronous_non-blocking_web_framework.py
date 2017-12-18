import socket
import select
from types import GeneratorType


class Request(object):
    def __init__(self, data):
        head_body = data.decode('utf-8')  # 转化为str类型
        header_str, body_str = head_body.split('\r\n\r\n')  # 将请求头和请求体分割
        header_list = header_str.split('\r\n')  # 将请求头的数据与数据分开
        # 由于第一个比较特殊，将他们再次分开,分别是请求方式，url和协议
        method, url, protocol = header_list[0].split(' ')

        # 将请求头封装进字典
        header_dict = {}
        for i in range(1, len(header_list)):
            k, v = header_list[i].split(':', 1)
            header_dict[k] = v

        # print(method, url, protocol, header_dict)
        self.method = method
        self.url = url
        self.headers = header_dict
        self.body = body_str


class Response(object):
    def __init__(self, data):
        self.data = data
        self.base_data = 'HTTP/1.1 200 OK\r\n\r\n' \
                         '<html><head><meta charset="UTF-8"><title>Title</title>' \
                         '</head><body><h1>{0}</h1></body></html>'

    def render(self):
        return self.base_data.format(self.data).encode('utf-8')


class Future(object):
    def __init__(self):
        self.status = False
        self.data = None

    def set_result(self, data):
        self.status = True
        self.data = data


def index(request):
    fur = Future()
    yield fur
    # return Response('首页')


def login(request):
    return Response('登录')

routers = [
    ['/index', index],
    ['/login', login]
]

server = socket.socket()
server.setblocking(False)  # 不阻塞
# 不加下面这句的话回报OSError: [Errno 48] Address already in use错误
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('127.0.0.1', 8001))
server.listen(5)

inputs = [server, ]
client_future = {}  # 测试用

# 用于检测socket是否发生变化
while True:
    # rList,wList, eList分别监听inputs，[], []里面是否发生变化，比如监听inputs,inputs里面谁有变化，rList里面就是谁
    rList, wList, eList = select.select(inputs, [], [], 0.005)   # 最多阻塞0.005秒
    # 获得input里面有变化的，循环input
    for sk in rList:
        # 如果有请求到来，并且是服务端，建立链接
        if sk == server:
            conn, addr = sk.accept()
            # 将客户端也加入被监听的行列
            inputs.append(conn)
        else:
            # 接受已经成功链接的客户端发来请求头，然后返回success，断开链接，然后删除客户端
            head_body_bytes = sk.recv(8096)  # bytes类型
            request = Request(head_body_bytes)  # 这样request里面就封装来method，url，header

            view_method = None
            for url_func in routers:
                if url_func[0] == request.url:
                    view_method = url_func[1]
                    break

            if not view_method:
                # response = b'HTTP/1.1 200 OK\r\n\r\n<html><body><h1>404</h1></body></html>'
                response = Response(404)
            else:
                response = view_method(request)

            if isinstance(response, GeneratorType):  # 如果是生成器，说明是异步非阻塞
                fur = response.__next__()  # 获取Future对象
                # 发起一次IO请求，并且加入到select中，进行检测是否已经发生变化
                # 假设请求发送过去来，链接还没有断开，线程还是在循环接受，其他请求还是能检测到
                client_future[sk] = fur

            else:  # 否则就是一般的请求
                sk.sendall(response.render())
                sk.close()
                inputs.remove(sk)

    for sk, future in client_future.items():
        if not future.status:  # 如果没人改他的值，说明请求没有结束
            continue

        # 否则，说明返回值了
        sk.sendall(future.data)
        # 发送过后应该关闭通道，删除inputs和client_future里面的sk
        sk.close()
        inputs.remove(sk)
        # 删除client_future里面的值，但是在循环过程中不能删
