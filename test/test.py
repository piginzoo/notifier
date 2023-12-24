import time

from notifier import imessage
from notifier.utils import load_params, init_logger

# python -m test.test
if __name__ == '__main__':

    init_logger()
    conf = load_params("conf/config.yml")
    # 使用前一定要初始化，里面需要初始化全局变量
    imessage._init(conf)

    # 测试info发送
    imessage.send("测试全部发送info", "晚上吃猪蹄", 'info')
    time.sleep(3)

    # 测试error发送
    imessage.send("测试全部发送error", "晚上不吃猪蹄", 'error')

    # 测试
    imessage.send("测试email", "我是邮件", 'info', imessage.CHANNEL_EMAIL)

    imessage.send("测试plus", "我是plus", 'info', imessage.CHANNEL_PLUSPLUS)

    imessage.send("测试企业微信", "我是企业微信", 'error', imessage.CHANNEL_WEIXIN)
