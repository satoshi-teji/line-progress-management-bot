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

import re
import os
import datetime
import urllib.parse

app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

pre_action = ""


def get_user_data(event):
    return (event.source.user_id,
            event.reply_token,
            line_bot_api.get_profile(event.source.user_id).display_name)


def get_date(datetime_data):
    return "{:04}-{:02}-{:02}".format(
        datetime_data.year, datetime_data.month, datetime_data.day)


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
    global pre_action

    if (pre_action == "set_end_day"):
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", user_msg)
        if (len(nums) == 0):
            line_bot_api.reply_message(
                reply_token,
                [
                    TextSendMessage(
                        text="数値を入力してください。設定を中止する場合は「設定中止」とメッセージを送信してください。"
                    )]
            )
        num = float(nums[0])
        line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="最終目標を {}に設定しました。\n一日あたりの目標を設定します。一日あたりの目標をメッセージで送信してください。\n自動で設定したい場合は0を送信してください。".format(num)
                )]
        )
        pre_action = "target"
        return
    elif (pre_action == "target"):
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", user_msg)
        if (len(nums) == 0):
            line_bot_api.reply_message(
                reply_token,
                [
                    TextSendMessage(
                        text="数値を入力してください。設定を中止する場合は「設定中止」とメッセージを送信してください。"
                    )]
            )
        num = float(nums[0])
        line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="一日あたりの目標を {}に設定しました。\n以下の設定で利用を開始します。".format(num)
                ),
                TextSendMessage(
                    text="期間: {} ~ {}\n最終目標: {}\n一日あたり: {}".format('a', 'b', 1, 2)
                ),
                TemplateSendMessage(alt_text="毎日21時に進捗状況グラフを送りますか?",
                                    template=ConfirmTemplate(
                                        text="毎日21時に進捗状況グラフを送りますか?\n設定してもしなくても「進捗状況」とメッセージを送信することで任意の時間に受信が可能です。",
                                        actions=[
                                            PostbackAction(
                                                label="Yes",
                                                display_text="はい",
                                                data="action=nortification"
                                            ),
                                            PostbackAction(
                                                label="No",
                                                display_text="いいえ",
                                                data="action=no_nortification"
                                            )]
                                        )
                                    )
            ]
        )
        pre_action = "per_day"
        return

    if ("設定" in user_msg and "中止" in user_msg):
        line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="設定を中止しました。"
                )]
        )
        pre_action = ""

    if ("利用" in user_msg and "開始" in user_msg):
        line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="こんにちは、{}さん！\n進捗管理くんをご利用いただきありがとうございます。".format(user_name)
                    ),
                TemplateSendMessage(alt_text="利用を開始しますか?",
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
    else:
        line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="「利用開始」とメッセージを送信することで初期設定を行います。\n必要なくなった場合はブロックしてください。ブロックを解除することで利用を再開できます。"
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
        [
            TextSendMessage(text="こんにちは、{}さん！\n進捗管理くんをご利用いただきありがとうございます。".format(user_name)),
            TemplateSendMessage(alt_text="利用を開始しますか?",
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
    global pre_action

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
                        label="日付を選択",
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
            [
                TextSendMessage(text="期限を選択してください。(最大90日先まで選択可能)"),
                date_picker
            ]
        )
    elif (action == "set_end_day"):
        end_date = event.postback.params['date']
        line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="期限を{}に設定しました。\n最終目標を設定します。最終目標をメッセージで送信してください。(整数で送信してください。)".format(end_date)
                )]
        )
        pre_action = action
    elif (action == "nortification"):
        line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="通知設定をオンにしました。\nこれで設定は完了です。\n「進捗 3ページ」のようにメッセージを送信することでその日の進捗を更新できます。"
                )
            ]
        )
    elif (action == "no_nortification"):
        line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="通知設定はオフです。\n「進捗状況」とメッセージを送信することでグラフはいつでも受信可能です。\nこれで設定は完了です。\n「進捗 3ページ」のようにメッセージを送信することでその日の進捗を更新できます。"
                )
            ]
        )
    else:
        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text="設定を中止します。")
        )


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
