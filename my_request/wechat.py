import pymysql
from redis import Redis
from wechatpy import WeChatClient, create_reply
from wechatpy.session.redisstorage import RedisStorage

from config import *
from resources import Instrument


class WechatHandler(object):
    def __init__(self):
        self.redis_client = Redis(host=redis_host, password=redis_password)
        self.session_interface = RedisStorage(self.redis_client, prefix="wechatpy")
        self.wechat_client = WeChatClient(appid, secret, session=self.session_interface)
        self.template_id = {Instrument.F20: template_id_remind_f20,
                            Instrument.FIB: template_id_remind_fib}
        self.mysql = pymysql.connect(host=mysql_host, password=mysql_password,
                                     db='wechat_tem', charset='utf8', autocommit=True)

    def remind_reserve(self, instrument):
        template_id = self.template_id[instrument]
        sql = "select openid from user_account where is_followed = 1"
        cursor = self.mysql.cursor()
        cursor.execute(sql)
        for openid, in cursor.fetchall():
            self.wechat_client.message.send_template(openid, template_id, '')

    def get_followers(self):
        ret = self.wechat_client.user.get_followers()
        return ret.get('data', {}).get('openid', [])

    def insert_followers(self):
        sql = "INSERT INTO user_account (openid) values (%s) ON DUPLICATE KEY UPDATE is_followed = 1"
        cursor = self.mysql.cursor()
        for openid in self.get_followers():
            cursor.execute(sql, (openid,))
