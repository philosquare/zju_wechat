import pymysql
from redis import Redis
from wechatpy import create_reply

from config import *
from my_request.reserve import RequestReserve
from resources import RedisFlow, Status, Instrument


class WechatMsgHandler(object):
    def __init__(self):
        self.mysql = None
        self.redis = Redis(redis_host, password=redis_password, decode_responses=True)

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
        openid = msg.source
        content = msg.content
        if self.redis.expire(openid, redis_expire_time) == 0:
            return create_reply('消息已收到', message=msg).render()
        status = self.redis.hget(openid, 'status')
        current = RedisFlow.get(status)
        self.redis.hmset(openid, {current.status: content, 'status': current.next_status})
        if current.is_end:
            return getattr(self, current.call)(msg)
        else:
            return create_reply(current.ret_msg, message=msg).render()

    def handle_event_msg(self, msg):
        if msg.event == 'subscribe':
            return self._handle_subscribe_event(msg)
        elif msg.event == 'unsubscribe':
            return self._handle_unsubscribe_event(msg)
        elif msg.event == 'click':
            return self._handle_click_event(msg)
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

    def handle_register_msg(self, msg):
        openid = msg.source
        username, password = self.redis.hmget(
            openid, Status.REGISTER_USERNAME, Status.REGISTER_PASSWORD)
        reserve = RequestReserve()
        if reserve.register(username, password, msg):
            self.redis.delete(openid)
            return create_reply('帐号绑定成功！', message=msg).render()
        self.redis.hset(openid, 'status', Status.REGISTER_USERNAME)
        return create_reply('用户名或密码错误！\n请重新输入用户名', message=msg).render()

    def handle_reserve_msg(self, msg):
        openid = msg.source
        instrument, reserve_date, start_time, end_time = self.redis.hmget(
            openid, Status.RESERVE_INSTRUMENT, Status.RESERVE_DATE,
            Status.RESERVE_START_TIME, Status.RESERVE_END_TIME)
        self.redis.delete(openid)
        reserve = RequestReserve()
        rd = reserve.reserve(instrument, reserve_date, start_time, end_time, msg)
        if rd.get('code') == 0:
            trigger_time = rd.get('trigger_time')
            return create_reply('预约设定成功，将在 %s 开始预约' % trigger_time, msg).render()
        err_msg = '预约出错！' + rd.get('msg', '未知错误')
        return create_reply(err_msg, msg).render()

    def _handle_click_event(self, msg):
        if msg.key == 'REGISTER':
            self.redis.hset(msg.source, 'status', Status.REGISTER_USERNAME)
            self.redis.expire(msg.source, redis_expire_time)
            return create_reply('请输入易约用户名', message=msg).render()
        if msg.key in ['RESERVE_NF20', 'RESERVE_OF20', 'RESERVE_FIB']:
            self.conn_mysql()
            cursor = self.mysql.cursor()
            sql = "select account_verified from user_account where openid=%s"
            cursor.execute(sql, (msg.source,))
            verified, = cursor.fetchone()
            if verified == 0:
                return create_reply('请先绑定帐号，再进行预约。', msg).render()
            instrument = {'RESERVE_NF20': Instrument.New_F20.value,
                          'RESERVE_OF20': Instrument.Old_F20.value,
                          'RESERVE_FIB': Instrument.FIB.value}.get(msg.key)
            self.redis.hmset(msg.source,
                             {Status.RESERVE_INSTRUMENT: instrument, 'status': Status.RESERVE_DATE})
            self.redis.expire(msg.source, redis_expire_time)
            instrument_name = {'RESERVE_NF20': '新F20',
                               'RESERVE_OF20': '老F20',
                               'RESERVE_FIB': 'FIB'}.get(msg.key)
            return create_reply(
                '正在预约仪器：%s\n请输入实验日期 例如：2018-01-01' % instrument_name, msg).render()
        return ''
