from my_request.wechat import WechatHandler


def remind_reserve(instrument):
    template_msg = WechatHandler()
    template_msg.remind_reserve(instrument)
