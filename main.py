from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)

from linebot.exceptions import (
    InvalidSignatureError
)

from linebot.models import (
    MessageEvent,
    FollowEvent,
    TextMessage,
    TextSendMessage,
    ImageSendMessage,
    TemplateSendMessage,
    ConfirmTemplate,
    PostbackAction
)

import os

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request Body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    reply_token = event.reply_token
    user_msg = event.message.text
    user_id = event.source.user_id
    user_name = line_bot_api.get_profile(user_id).display_name

    line_bot_api.reply_message(
        reply_token,
        [TextSendMessage(
            text="{}さん\n{}".format(user_name, user_msg)
            )]
    )


@handler.add(FollowEvent)
def handle_follow_message(event):
    user_id = event.source.user_id
    reply_token = event.reply_token
    user_name = line_bot_api.get_profile(user_id).display_name

    line_bot_api.reply_message(
        reply_token,
        [TextSendMessage(text="こんにちは、{}さん！\n進捗管理くんをご利用いただきありがとうございます。".format(user_name)),
            TemplateSendMessage(alt_text="現在非対応のデバイスです。iOS版またはAndroid版のLINEをご使用ください。",
                                template=ConfirmTemplate(
                                    text="利用を開始しますか?",
                                    actions=[
                                        PostbackAction(
                                            label="Yes",
                                            display_text="はい",
                                            data="action=yes_first"
                                        ),
                                        PostbackAction(
                                            label="No",
                                            display_text="いいえ",
                                            data="action=no"
                                        )
                                    ]
        ))]
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
