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
    UnfollowEvent,
    TextMessage
)

import message_template as mt
import re
import os
import urllib.parse
import datetime
import edit_db as ed


app = Flask(__name__)

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
dbname = 'db/user_data.db'
db_editor = ed.Editor(dbname)


def get_date(datetime_data):
    return "{:04}-{:02}-{:02}".format(
        datetime_data.year, datetime_data.month, datetime_data.day)


def get_user_data(event):
    return (event.source.user_id,
            event.reply_token,
            line_bot_api.get_profile(event.source.user_id).display_name)


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

    if (not db_editor.check_user(user_id)):
        if ("利用" in user_msg and "開始" in user_msg):
            mt.start_message(line_bot_api, reply_token, user_name)
            return
        else:
            mt.invalid_message(line_bot_api, reply_token)
            return

    if (not db_editor.check_target(user_id)):
        # DBに最終目標がない
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", user_msg)
        if (len(nums) == 0):
            mt.num_error_message(line_bot_api, reply_token)
            return
        num = float(nums[0])
        mt.set_per_day_target_message(line_bot_api, reply_token, num)
        db_editor.set_target(user_id, num)
        return
    elif (not db_editor.check_per_day_target(user_id)):
        # DBに一日あたりの目標がない
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", user_msg)
        if (len(nums) == 0):
            mt.num_error_message(line_bot_api, reply_token)
            return
        num = float(nums[0])
        db_editor.set_per_day_target(user_id, num)
        _, _, initial_date, end_date, target, per_day_target, _ = db_editor.get_data(user_id)
        mt.set_notification_message(line_bot_api, reply_token, num,
                                    initial_date, end_date, target,
                                    per_day_target)
        return

    if ("利用" in user_msg and "中止" in user_msg):
        mt.stop_using_message(line_bot_api, reply_token)
        db_editor.del_user(user_id)
        return

    if ("設定" in user_msg):
        _, _, initial_date, end_date, target, per_day_target, _ = db_editor.get_data(user_id)
        mt.set_notification_message(line_bot_api, reply_token, num,
                                    initial_date, end_date, target,
                                    per_day_target)
        mt.setting_message(line_bot_api, reply_token)
    mt.help_message(line_bot_api, reply_token)


# 友達追加時のイベント
@handler.add(FollowEvent)
def handle_follow_message(event):
    user_id = event.source.user_id
    reply_token = event.reply_token
    user_name = line_bot_api.get_profile(user_id).display_name

    mt.start_message(line_bot_api, reply_token, user_name)


@handler.add(UnfollowEvent)
def handle_unfollow_message(event):
    user_id = event.source.user_id
    db_editor.del_user(user_id)

# POSTBACK時のイベント
@handler.add(PostbackEvent)
def handle_postback(event):
    user_id, reply_token, user_name = get_user_data(event)
    data = urllib.parse.parse_qs(event.postback.data)
    action = data["action"][0]

    if (action == "yes_first"):
        # 利用開始時の処理
        # 日付選択オブジェクトを送って終了
        mt.set_duration_message(line_bot_api, reply_token)
        db_editor.add_user(user_id)
    elif (action == "set_end_day"):
        # 日付選択オブジェクト操作後の処理
        initial_date = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
        initial_date = get_date(initial_date)
        end_date = event.postback.params['date']
        mt.set_target_message(line_bot_api, reply_token, end_date)
        # dbに開始日と終了日を追加
        db_editor.set_date(user_id, initial_date, end_date)
    elif (action == "notification"):
        mt.notification_on_message(line_bot_api, reply_token)
    elif (action == "no_notification"):
        mt.notification_off_message(line_bot_api, reply_token)
    else:
        mt.stop_setting_message(line_bot_api, reply_token)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
