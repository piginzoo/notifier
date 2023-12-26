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
    # msg = df2msg(df,max_length=4000)
    #
    # imessage.send("测试企业微信", msg, 'info', imessage.CHANNEL_WEIXIN)
    #
    # # imessage.send("测试plusplus", msg, 'info', imessage.CHANNEL_PLUSPLUS)
    #
    # imessage.send("测试邮件", msg, 'info', imessage.CHANNEL_EMAIL)

    names={'code': '股票','action': '买卖','amount': '金额', 'position':'股数','create_date': '创建','target_date': '目标','done_datetime':'执行'}

    df1 = df[(df.action=='buy')&(df.status=='done')].drop(['signal_score','status','action','position'],axis=1)
    df2 = df[(df.action=='sell')&(df.status=='done')].drop(['signal_score','status','action','amount'],axis=1)
    df3 = df[(df.action=='buy')&(df.status=='pending')].drop(['signal_score','status','action','position'],axis=1)
    df4 = df[(df.action=='sell')&(df.status=='pending')].drop(['signal_score','status','action','amount'],axis=1)
    imessage.send("买成功的股票", df1.rename(columns=names), 'info', imessage.CHANNEL_WEIXIN)
    imessage.send("卖成功的股票", df2.rename(columns=names), 'info', imessage.CHANNEL_WEIXIN)
    imessage.send("没买进来的股票", df3.rename(columns=names), 'info', imessage.CHANNEL_WEIXIN)
    imessage.send("没卖出去的股票", df4.rename(columns=names), 'info', imessage.CHANNEL_WEIXIN)
