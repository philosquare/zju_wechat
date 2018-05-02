import pymysql
from wechatpy import create_reply
from config import *


class WechatMsgHandler(object):
    def __init__(self):
        self.mysql = None

    def conn_mysql(self):
        if self.mysql is None:
            self.mysql = pymysql.connect(host=mysql_host, password=mysql_password,
                                        db='wechat_tem', charset='utf8', autocommit=True)

    def handle_msg(self, msg):
        print('received message: %s' % msg)
        if msg.type == 'text':
            ret_msg = self.handle_text_msg(msg)
        elif msg.type == 'event':
            ret_msg = self.handle_event_msg(msg)
        else:
            ret_msg = create_reply('暂不支持此类消息', message=msg).render()
        return ret_msg

    def handle_text_msg(self, msg):
        return create_reply('消息已收到', message=msg).render()

    def handle_event_msg(self, msg):
        if msg.event == 'subscribe':
            return self._handle_subscribe_event(msg)
        elif msg.event == 'unsubscribe':
            return self._handle_unsubscribe_event(msg)
        return ''

    def _handle_subscribe_event(self, msg):
        reply = create_reply('欢迎关注，你将会提前一天收到预约提醒。', message=msg)
        self.conn_mysql()
        cursor = self.mysql.cursor()
        sql = "INSERT INTO user_account (openid) values (%s) ON DUPLICATE KEY UPDATE is_followed = 1"
        cursor.execute(sql, msg.source)
        return reply.render()

    def _handle_unsubscribe_event(self, msg):
        self.conn_mysql()
        cursor = self.mysql.cursor()
        sql = "UPDATE user_account SET is_followed = 0 WHERE openid = %s"
        cursor.execute(sql, msg.source)
        return ''
