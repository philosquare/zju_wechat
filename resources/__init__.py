from enum import Enum, unique


@unique
class Instrument(Enum):
    F20 = 'F20'
    New_F20 = 'NEW_F20'
    Old_F20 = 'OLD_F20'
    FIB = 'FIB'


class Status(object):
    REGISTER_USERNAME = 'register_username'
    REGISTER_PASSWORD = 'register_password'
    RESERVE_DATE = 'reserve_date'
    RESERVE_START_TIME = 'reserve_start_time'
    RESERVE_END_TIME = 'reserve_end_time'
    RESERVE_INSTRUMENT = 'reserve_instrument'


class RedisFlow(object):

    class Current(object):
        def __init__(self, status, is_end, ret_msg='', next_status='', call=None):
            self.status = status
            self.ret_msg = ret_msg
            self.is_end = is_end
            self.next_status = next_status
            self.call = call

    flow = {
        Status.REGISTER_USERNAME:
            Current(Status.REGISTER_USERNAME, False, '请输入密码', Status.REGISTER_PASSWORD),
        Status.REGISTER_PASSWORD:
            Current(Status.REGISTER_PASSWORD, True, call='handle_register_msg'),
        Status.RESERVE_DATE:
            Current(Status.RESERVE_DATE, False, '请输入实验开始时间 例如：9:30', Status.RESERVE_START_TIME),
        Status.RESERVE_START_TIME:
            Current(Status.RESERVE_START_TIME, False, '请输入实验结束时间', Status.RESERVE_END_TIME),
        Status.RESERVE_END_TIME:
            Current(Status.RESERVE_END_TIME, True, call='handle_reserve_msg')
    }

    @staticmethod
    def get(status):
        return RedisFlow.flow.get(status)
