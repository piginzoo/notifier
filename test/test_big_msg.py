import pandas as pd

from notifier import imessage
from notifier.utils import load_params, init_logger, df2msg

# python -m test.test_big_msg
if __name__ == '__main__':

    init_logger()
    conf = load_params("conf/config.yml")
    # 使用前一定要初始化，里面需要初始化全局变量
    imessage._init(conf)

    df = pd.read_csv("test/order.csv")
    msg = df2msg(df,max_length=4000)

    imessage.send("测试企业微信", msg, 'info', imessage.CHANNEL_WEIXIN)

    imessage.send("测试plusplus", msg, 'info', imessage.CHANNEL_PLUSPLUS)

    imessage.send("测试邮件", msg, 'info', imessage.CHANNEL_EMAIL)
