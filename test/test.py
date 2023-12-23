from notifier import imessage
from notifier.utils import load_params, init_logger

# python -m test.test
if __name__ == '__main__':

    init_logger()
    conf = load_params("conf/config.yml")
    imessage._init(conf)

    imessage.send("信号标题", "晚上吃猪蹄", 'info')
    imessage.send("信号标题", "晚上吃猪蹄", 'info')
