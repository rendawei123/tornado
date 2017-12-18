### websocket

##### 什么是websocket？

websocket就是一种协议，当作为客户端的浏览器访问服务端的时候，一旦链接上就不断开，可以持续发送数据

##### django可以做吗？

Django默认不支持websocket协议，但是有第三方插件，Django Channels可以实现，tornado默认支持

##### 有什么用？

可以做web聊天室

##### 有啥缺点？

缺点就是兼容性不好，现在主流的浏览器都支持，但是，想腾讯这种用户基数太大的应用，他们考虑的更多的是兼容性，一般一些用户量小的，想用新技术的公司都会选择websocket来做

##### 那腾讯他们如何做的？

他们用的是常轮巡，也就是说请求发送过去之后不断开等一段时间，这段时间有消息立马发送，如果没有消息，断开再链接，再等一段时间，轮巡是一值循环，websocket是一直不断开

##### 原理

在建立链接的时候，浏览器给服务器发送websocket请求，服务器接收到之后，取出请求中的魔法字符串，然后进行加密，加密完之后再回给浏览器，浏览器进行认证，如果认证成功，则说明符合websocket协议，如果验证不成功，断开






