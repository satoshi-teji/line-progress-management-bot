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
    PostbackEvent,
    TextMessage,
    TextSendMessage,
    ImageSendMessage,
    TemplateSendMessage,
    ConfirmTemplate,
    ButtonsTemplate,
    PostbackAction,
    DatetimePickerTemplateAction
)

import os
import datetime
import urllib.parse

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


def get_user_data(event):
    return (event.source.user_id,
            event.reply_token,
            line_bot_api.get_profile(event.source.user_id).display_name)


def get_date(datetime_data):
    return "{:04}-{:02}-{:02}".format(datetime_data.year, datetime_data.month, datetime_data.day)


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


# メッセージが送られた時のイベント
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id, reply_token, user_name = get_user_data(event)
    user_msg = event.message.text

    line_bot_api.reply_message(
        reply_token,
        [TextSendMessage(
            text="{}さん\n{}".format(user_name, user_msg)
            )]
    )


# 友達追加時のイベント
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
                                        )]
                                    )
                                )]
    )


# POSTBACK時のイベント
@handler.add(PostbackEvent)
def handle_postback(event):
    user_id, reply_token, user_name = get_user_data(event)
    data = urllib.parse.parse_qs(event.postback.data)
    action = data["action"][0]

    if (action == "yes_first"):
        # 確実に日本時間での時間を取得する
        initial_day = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        limit = initial_day + datetime.timedelta(days=90)
        date_picker = TemplateSendMessage(
            alt_text="終了予定日を設定",
            template=ButtonsTemplate(
                title="終了予定日",
                text="終了予定日を設定します。",
                actions=[
                    DatetimePickerTemplateAction(
                        label="end_day",
                        data="action=set_end_day",
                        mode="date",
                        initial=get_date(
                            initial_day+datetime.timedelta(days=30)
                            ),
                        min=get_date(initial_day),
                        max=get_date(limit)
                    )
                ])
        )
        line_bot_api.reply_message(
            reply_token,
            [TextSendMessage(text="利用を開始します。期限を選択してください。(最大90日先まで選択可能)"),
                date_picker]
        )
    else:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=str(data))
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
