import json
import logging
import requests
import smtplib
from email.header import Header
from email.mime.text import MIMEText

from notifier.utils import today

logger = logging.getLogger(__name__)

SIGNAL = 'signal'
ERROR = 'error'
INFO = 'info'

CHANNEL_WEIXIN = 'weixin'
CHANNEL_EMAIL = 'email'
CHANNEL_PLUSPLUS = 'plusplus'
CHANNEL_ALL = 'all'


def _init(conf):
    global _SENDERS
    _SENDERS = {
        'weixin': WeixinMessager(conf),
        'plusplus': PlusMessager(conf),
        'email': MailMessager(conf)
        # 'qxweixin': QYWeixinMessager(conf),
    }


def send(title, msg, group, channel=CHANNEL_ALL):
    if group not in [SIGNAL, ERROR, INFO]:
        logger.warning("发送的目标群组，必须是%r之一", [SIGNAL, ERROR, INFO])
        return

    if channel not in [CHANNEL_ALL, CHANNEL_WEIXIN, CHANNEL_EMAIL, CHANNEL_PLUSPLUS]:
        logger.warning("目标发送的渠道[%s]，必须是%r之一", channel,
                       [CHANNEL_ALL, CHANNEL_WEIXIN, CHANNEL_EMAIL, CHANNEL_PLUSPLUS])
        return

    global _SENDERS
    for name, messager in _SENDERS.items():

        # 如果渠道匹配，或者，渠道为全渠道，则发送
        if channel == name or channel == CHANNEL_ALL:
            # 为了防止被封，设置一个当日计数器，超过不发
            if messager.get_count() > messager.conf[name].day_max: return

            # 发送，如果成功发送，则计数
            if messager.send(title, msg, group):
                messager.count()
                logger.debug("渠道[%s]消息总数：%d个", name, messager.get_count())


class Messager():
    def __init__(self, conf):
        self.conf = conf
        self.counter = {}

    def count(self):
        if self.counter.get(today(), None) is None:
            self.counter[today()] = 1
        else:
            self.counter[today()] += 1

    def get_count(self):
        if self.counter.get(today(), None) is None:
            return 0
        else:
            return self.counter[today()]

    def send(self, title, msg, group):
        pass


class PlusMessager(Messager):
    def send(self, title, msg, group='info'):

        try:
            # http://www.pushplus.plus/doc/guide/api.htm
            url = 'http://www.pushplus.plus/send'
            data = {
                "token": self.conf['plusplus']['token'],
                "title": title,
                "content": msg,
                "topic": group
            }
            body = json.dumps(data).encode(encoding='utf-8')
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=body, headers=headers)
            data = response.json()
            if data and data.get("code", None) and data["code"] == 200:
                return True
            if data and data.get("code", None):
                logger.warning("发往PlusPlus消息错误: code=%r, msg=%s, token=%s, topic=%s",
                               data['code'], data['msg'], self.conf['plusplus']['token'][:10] + "...", group)
            else:
                logger.warning("发往PlusPlus消息错误: 返回为空")
            return False
        except Exception:
            logger.exception("发往PlusPlus消息发生异常", msg)
            return False


class MailMessager(Messager):
    def send(self, title, msg, group):

        try:
            uid = self.conf['email']['uid']
            pwd = self.conf['email']['pwd']
            host = self.conf['email']['host']
            email = self.conf['email']['email'][group]

            receivers = email.split(",")  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

            # 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
            message = MIMEText(msg, 'plain', 'utf-8')
            message['From'] = uid  # 发送者
            message['To'] = email  # 接收者
            message['Subject'] = Header(f'{title} - {group}', 'utf-8')

            # logger.info("发送邮件[%s]:[%s:%s]", host,uid,pwd)
            smtp = smtplib.SMTP_SSL(host)
            smtp.login(uid, pwd)
            smtp.sendmail(uid, receivers, message.as_string())
            logger.info("发往[%s]的邮件通知完成，标题：%s", email, title)
            return True
        except smtplib.SMTPException:
            logger.exception("发往[%s]的邮件出现异常，标题：%s", email, email)
            return False


class QYWeixinMessager(Messager):
    """
    reference: https://blog.51cto.com/xdgy/5854364
    通过企业微信的message api给自己发消息：
    1、创建一个应用：https://work.weixin.qq.com/wework_admin/
    2、通过一下代码给这个应用发消息
    3、别忘了需要配置这个应用的可信ip（ip不能经常变）

    这个要求太高，已经废弃了，ip保证不了
    """

    def send(self, title, msg, group):
        try:
            logger.info("开始推送企业微信[类别:%s]消息", group)
            secret = self.conf['qyweixin']['secret']
            corp_id = self.conf['qyweixin']['corp_id']
            agent_id = self.conf['qyweixin']['agent_id']

            # 1、获得access_token：
            url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={secret}"
            resp = requests.get(url)
            result = resp.json()
            if result["errcode"] == 0:
                access_token = result["access_token"]
            else:
                logger.error('获得企业微信的access_token失败')
                return

            url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
            # print(url)
            post_data = {
                # @all向该企业应用的全部成员发送；指定接收消息的成员，成员ID列表（多个接收者用‘|’分隔，最多支持1000个）
                # 具体类型可以查阅官方网站：https://developer.work.weixin.qq.com/document/path/90236
                # 代码支持类型：文本消息（text），文本卡片消息（textcard），图文消息（news），markdown消息（markdown）
                # content    是    文本内容，最长不超过4096个字节，必须是utf8编码
                "touser": "@all",
                "msgtype": 'text',
                "agentid": agent_id,
                "text": {
                    "content": f"标题:{title}:\n内容:\n{msg[:4096]}"
                }
            }
            # headers = {'Content-Type': 'application/json'}
            json_data = json.dumps(post_data)
            resp = requests.post(url, data=json_data)  # , headers=headers)
            # print(resp.json())
            logger.info("发往企业微信消息[%s]的通知完成", group)
            return True
        except Exception:
            logger.exception("发往企业微信消息[%s][%s...]，发生异常", group, msg[:200])
            return False


class WeixinMessager(Messager):
    def send(self, title, msg, group):
        """
        接口文档：https://developer.work.weixin.qq.com/document/path/91770?version=4.0.6.90540
        """
        try:
            # logger.info("开始推送企业微信[类别:%s]消息", group)
            url = self.conf['weixin'][group]
            # content    是    文本内容，最长不超过4096个字节，必须是utf8编码
            post_data = {
                "msgtype": "text",
                "text": {
                    "content": f"标题:{title}:\n内容:\n{msg[:4096]}"
                }
            }
            headers = {'Content-Type': 'application/json'}
            requests.post(url, json=post_data, headers=headers)
            logger.info("发往企业微信机器人[%s]的通知完成", group)
            return True
        except Exception:
            logger.exception("发往企业微信机器人[%s]的消息[%s...]，发生异常", group, msg[:200])
            return False
