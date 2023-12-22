from notifier.imessage import MessageSender
from notifier.utils import load_params, init_logger

# python -m test.test
if __name__ == '__main__':

    init_logger()
    conf = load_params("conf/config.yml")
    s = MessageSender(conf)
    s.send("信号标题", "晚上吃猪蹄", 'signal')
    s.send("错误标题", "错误内容", 'error')
