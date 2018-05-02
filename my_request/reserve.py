import pymysql
import requests
from datetime import datetime

from config import *


class RequestReserve:
    def __init__(self):
        self.host = reserve_url
        self.port = reserve_port
        self.mysql = pymysql.connect(host=mysql_host, password=mysql_password,
                                     db='wechat_tem', charset='utf8', autocommit=True)

    def get_all_jobs(self):
        url = reserve_url + '/api/scheduled_jobs'
        r = requests.get(url)

    def register(self, username, password, msg):
        url = reserve_url + '/api/login_test'
        params = dict(username=username, password=password)
        response = requests.get(url, params=params)
        rd = response.json()
        if rd.get('code') == 0:
            cursor = self.mysql.cursor()
            sql = """
                    UPDATE user_account SET tem_username=%s, tem_password=%s, account_verified=1, 
                    account_update_time=%s WHERE openid=%s
                """
            cursor.execute(sql, (username, password, datetime.now(), msg.source))
            return True
        return False

    def reserve(self, instrument, reserve_date, start_time, end_time, msg):
        openid = msg.source
        cursor = self.mysql.cursor()
        sql = "select tem_username, tem_password from user_account where openid=%s"
        cursor.execute(sql, (openid,))
        username, password = cursor.fetchone()
        url = reserve_url + '/api/reserve'
        data = dict(username=username, password=password, instrument=instrument,
                    reserve_date=reserve_date, start_time=start_time, end_time=end_time)
        response = requests.post(url, data=data)
        if response.status_code != 200:
            rd = {'code': 500, 'msg': '服务器内部错误'}
        else:
            rd = response.json()
        return rd
