import datetime
import logging
import os
import sys
import time

import yaml

logger = logging.getLogger(__name__)


class AttributeDict(dict):

    def __init__(self, _dict):
        """_dict是一个字典"""
        for k, v in _dict.items():
            if type(v) == dict:
                self.__setitem__(k, AttributeDict(v))
            else:
                self.__setitem__(k, v)

    """
    class AttributeDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    data=AttributeDict()
    data['a']='a'
    pickle.dump(data, open("test.txt","wb"))
    # 程序报错：
    # KeyError: '__getstate__'
    # 如何修复？
    修复：必须从新定义__getstate__和__setstate__
    """
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__.update(d)

    # __getattr__ = dict.__getitem__
    def __getattr__(self, name):
        """重载这个方法，是为了防止KeyError，而只返回None"""
        try:
            return self[name]
        except KeyError:
            return None

    def copy(self):
        """默认的copy会返回dict，我要的是AttributeDict"""
        return AttributeDict(super().copy())



def load_params(name='params.yml'):
    if not os.path.exists(name):
        raise ValueError(f"参数文件[{name}]不存在，请检查路径")
    params = yaml.load(open(name, 'r', encoding='utf-8'), Loader=yaml.FullLoader)
    params = AttributeDict(params)
    return params

def init_logger(file=False, simple=False, log_level=logging.DEBUG):
    print("开始初始化日志：file=%r, simple=%r" % (file, simple))

    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger('matplotlib.font_manager').disabled = True
    logging.getLogger('matplotlib.colorbar').disabled = True
    logging.getLogger('matplotlib').disabled = True
    logging.getLogger('fontTools.ttLib.ttFont').disabled = True
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('asyncio').disabled = True

    if simple:
        formatter = logging.Formatter('%(message)s')
    else:
        formatter = logging.Formatter('%(asctime)s.%(msecs)03d|%(levelname)s|%(filename)s:%(lineno)d: %(message)s',
                                      datefmt='%H:%M:%S')

    root_logger = logging.getLogger()
    root_logger.setLevel(level=log_level)

    def is_any_handler(handlers, cls):
        for t in handlers:
            if type(t) == cls: return True
        return False

    # 加入控制台
    if not is_any_handler(root_logger.handlers, logging.StreamHandler):
        stream_handler = logging.StreamHandler(sys.stdout)
        root_logger.addHandler(stream_handler)
        print("日志：创建控制台处理器")

    # 加入日志文件
    if file and not is_any_handler(root_logger.handlers, logging.FileHandler):
        if not os.path.exists("./logs"): os.makedirs("./logs")
        filename = "./logs/{}.log".format(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
        t_handler = logging.FileHandler(filename, encoding='utf-8')
        root_logger.addHandler(t_handler)
        print("日志：创建文件处理器", filename)

    handlers = root_logger.handlers
    for handler in handlers:
        handler.setLevel(level=log_level)
        handler.setFormatter(formatter)

def df2msg(df,max_length):
    """
    把dataframe转成可发送的消息
    按照max_lengthe分割消息
    :return:
    """
    list = df.to_dict('records')
    s = ''
    msg = []
    for dict in list:
        dict_str_list = [f'{k}:{v}'for k,v in dict.items()]
        one = "\n".join(dict_str_list)
        # 如果串超了最大长度，那么存到数组中，再重头开始一个新的串
        if len(s+one)>max_length:
            msg.append(s)
            s = one + "\n\n"
        else:
            s+= one + "\n\n"
    msg.append(s)

    return msg

def today():
    now = datetime.datetime.now()
    return datetime.datetime.strftime(now, "%Y%m%d")

