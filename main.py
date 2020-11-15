
import os
import sys
import wsgiref.simple_server
from argparse import ArgumentParser

from builtins import bytes
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)
from linebot.utils import PY3

# get channel_secret and channel_access_token from your environment variable
YOUR_CHANNEL_SECRET = os.getenv('a2fc5a0a1e8b9172eb03deb54b87952c')
YOUR_CHANNEL_ACCESS_TOKEN = os.getenv('3/ejprz9CBzClM1nXMfFcSMVUHIiGoz+Uj3LqqqoPXmIJQdtNFLDemvT/bd0kgLVUIVtQSXmieW2yUabTnXx+IOuoj6UiH11eeMEmR1alA+gnDzYy42GSJAltcRPofgKu/VKtHgkGPRhE+eC19yERQdB04t89/1O/w1cDnyilFU=')
if YOUR_CHANNEL_SECRET is None:
    print('Specify YOUR_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if YOUR_CHANNEL_ACCESS_TOKEN is None:
    print('Specify YOUR_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(YOUR_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(YOUR_CHANNEL_SECRET)


def application(environ, start_response):
    # check request path
    if environ['PATH_INFO'] != '/callback':
        start_response('404 Not Found', [])
        return create_body('Not Found')

    # check request method
    if environ['REQUEST_METHOD'] != 'POST':
        start_response('405 Method Not Allowed', [])
        return create_body('Method Not Allowed')

    # get X-Line-Signature header value
    signature = environ['HTTP_X_LINE_SIGNATURE']

    # get request body as text
    wsgi_input = environ['wsgi.input']
    content_length = int(environ['CONTENT_LENGTH'])
    body = wsgi_input.read(content_length).decode('utf-8')

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        start_response('400 Bad Request', [])
        return create_body('Bad Request')

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=event.message.text)
        )

    start_response('200 OK', [])
    return create_body('OK')


def create_body(text):
    if PY3:
        return [bytes(text, 'utf-8')]
    else:
        return text


if __name__ == '__main__':
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-p', '--port', type=int, default=8000, help='port')
    options = arg_parser.parse_args()

    httpd = wsgiref.simple_server.make_server('', options.port, application)
    httpd.serve_forever()
