from flask import Flask, request
from wechatpy import parse_message
from wechatpy.utils import check_signature
from wechatpy.exceptions import InvalidSignatureException

import config
from msg_handler import WechatMsgHandler
from my_request.wechat import WechatHandler

app = Flask(__name__)


@app.route('/test')
def test_index():
    token = config.test_token
    echostr = request.args.get('echostr', None)
    timestamp = request.args.get('timestamp')
    nonce = request.args.get('nonce')
    signature = request.args.get('signature')
    try:
        check_signature(token, signature, timestamp, nonce)
        return echostr
    except InvalidSignatureException:
        return 'invalid signature'


@app.route('/test', methods=['POST'])
def test_post():
    msg = parse_message(request.data)
    msg_handler = WechatMsgHandler()
    ret_msg = msg_handler.handle_msg(msg)
    return ret_msg

if __name__ == '__main__':
    wechatHandler = WechatHandler()
    wechatHandler.insert_followers()
    import scheduler
    app.run(host='0.0.0.0', port=5177, debug=False, threaded=True)
