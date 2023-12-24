# 说明

这是一个简单的发送接口，可以发送邮件、微信（通过plusplus实现）、企业微信3个渠道。
目前主要用于，量化消息的推送。

为了统一，我设计了3个组：info，error，signal，分别用于：
- info：一般的成交消息，细节等，用于自己查看交易信息
- signal：只推送简洁的消息，用于其他朋友订阅信号用
- error：一些异常和错误的推送

目前支持的渠道和信息类型有：

```python
# 信息类型
SIGNAL = 'signal'
ERROR = 'error'
INFO = 'info'

# 渠道
CHANNEL_WEIXIN = 'weixin'
CHANNEL_EMAIL = 'email'
CHANNEL_PLUSPLUS = 'plusplus'
CHANNEL_ALL = 'all'
```

按照下面的详细配置，配置conf/config.yml，主要设置day_max参数，防止超发。

# 额外配置

1、[企业微信](https://developer.work.weixin.qq.com/document/path/90236#%E6%96%87%E6%9C%AC%E6%B6%88%E6%81%AF)

需要在PC端企业微信，创建3个群组，分别是"量化信息、异常报警、买卖信号"，
在每个群组内，创建一个群机器人，每个机器人都会生成一个webhook地址，
把这个地址，放到配置中：
```text
    signal: 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxxxxxxxxxxx'
    info: 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=yyyyyyyyyyyy'
    error: 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=zzzzzzzzzzzz'
```

2、邮箱

需要到QQ邮箱的设置>账号>"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"中，
开启服务，并获得授权码，然后修改配置文件：
```text
    host: 'smtp.qq.com'
    uid: 'xxxxxx@qq.com' # 发送的邮箱
    pwd: 'xxxxxxxx' # 授权码
    email:
        info: 'xxx@abc.com,yyy@abc.com' # 接收人的邮箱地址
        signal: ''
        error: ''
```
并且修改，email中接收人的邮箱地址。

3、plusplus

[Plusplus](https://www.pushplus.plus/)是一个三方帮助推送微信消息的api服务，每天有200个免费推送。
进入后台的 发送消息>一对多消息。
创建3个群组，分别是"量化信息、异常报警、买卖信号"，编码为"info,error,signal"。
然后使用群组生成的二维码，扫码加入群组。加入群组的微信使用人，将来就可以接收到消息了。

使用刚才配置群组界面下提供的token，配置token：
```text
plusplus:
    token: 'xxxxxxxxxxxxxx'
```
# 测试

运行 `python -m test.test`，完成测试。

# 使用

## 安装

首先需要安装，clone到本地，然后运行：
```commandline
python setup.py install
```

## 引用

在其他程序中，如果要引用这个消息发送，可以使用以下代码

1、在主程序启动的入口处，初始化imessage
```python
# 一定要先调用这句话'imessage._init()'，进行初始化，原因是需要初始化全局变量
from notifier import imessage
from notifier.utils import load_params, init_logger
init_logger()
conf = load_params("conf/config.yml")
imessage._init(conf)
```

2、然后，在任何地方，只需要调用 send方法即可

```python
from notifier import imessage

# 测试类型为info的消息，发送给所有的3个渠道
imessage.send("测试全部发送info", "晚上吃猪蹄", 'info')

# 测试类型为error的消息，发送给所有的3个渠道
imessage.send("测试全部发送error", "晚上不吃猪蹄", 'error')

# 测试类型为signal的消息，发送给所有的3个渠道
imessage.send("测试全部发送error", "晚上不吃猪蹄", 'signal')

# 测试类型为info的消息，仅发送邮件渠道
imessage.send("测试email", "我是邮件", 'info', imessage.CHANNEL_EMAIL)

# 测试类型为signal的消息，仅发送plusplus渠道
imessage.send("测试plus", "我是plus", 'signal', imessage.CHANNEL_PLUSPLUS)

# 测试类型为error的消息，仅发送企业微信渠道
imessage.send("测试企业微信", "我是企业微信", 'error', imessage.CHANNEL_WEIXIN)
```
# 总结

搞这个很简单的一个发送，简简单单的完成消息的推送，不整那么复杂，需要的，clone后自己魔改