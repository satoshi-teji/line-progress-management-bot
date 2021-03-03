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

import numpy as np
import plotly.graph_objects as go
import re
import os
import urllib.parse
import datetime

import message_template as mt
import edit_db as ed


app = Flask(__name__, static_folder='images')

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]
URL = os.environ["URL"]

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)
db_editor = ed.Editor()


def make_graph(initial_date, end_date, cum, target):
    days = calc_days(initial_date, end_date)
    time = [initial_date + datetime.timedelta(days=x) for x in range(days)]
    fig = go.Figure(data=[
        go.Scatter(x=time, y=cum, name='Total'),
        go.Scatter(x=time, y=target, name='Target')
        ])
    fig.update_layout(showlegend=True)
    fig.update_layout(width=1024, height=512)
    return fig


def create_png(graph, user_id):
    url = URL + "images/{}.png".format(user_id)
    graph.write_image("images/{}.png".format(user_id), width=1024)
    return url


def get_date(datetime_data):
    return "{:04}-{:02}-{:02}".format(
        datetime_data.year, datetime_data.month, datetime_data.day)


def get_user_data(event):
    return (event.source.user_id,
            event.reply_token,
            line_bot_api.get_profile(event.source.user_id).display_name)


def calc_days(initial_date, end_date):
    days = end_date - initial_date
    return abs(days.days + 1)


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

    # dbにユーザーが登録されているかどうか
    if (not db_editor.check_user(user_id)):
        if ("利用" in user_msg and "開始" in user_msg):
            mt.start_message(line_bot_api, reply_token, user_name)
            return
        else:
            mt.invalid_message(line_bot_api, reply_token)
            return

    # dateが設定されているかどうか
    if (not db_editor.check_date(user_id)):
        mt.set_duration_message(line_bot_api, reply_token)
        return

    if (not db_editor.check_target(user_id)):
        # DBに最終目標がない
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", user_msg)
        if (len(nums) == 0):
            mt.num_error_message(line_bot_api, reply_token)
            return
        num = float(nums[0])
        _, _, initial_date, end_date, _, _ = db_editor.get_data(user_id)
        days = calc_days(initial_date, end_date)
        per_day_target = num / days
        mt.set_notification_message(line_bot_api, reply_token, initial_date.date(), end_date.date(), num, per_day_target)
        db_editor.set_target(user_id, num)
        cum_to_target = np.linspace(0, num, days)
        cum_to_target = ','.join(map(str, cum_to_target))
        db_editor.set_work_target(user_id, cum_to_target)
        db_editor.set_work(user_id, days)
        return

    if ("利用" in user_msg and "中止" in user_msg):
        mt.stop_using_message(line_bot_api, reply_token)
        db_editor.del_user(user_id)
        return

    if ("進捗" in user_msg):
        nums = re.findall(r"[-+]?\d*\.\d+|\d+", user_msg)
        if (len(nums) != 0):
            _, _, initial_date, end_date, _, _ = db_editor.get_data(user_id)
            now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
            today = datetime.date(now.year, now.month, now.day)
            index = calc_days(today, initial_date.date()) - 1
            db_editor.update(user_id, float(nums[0]), index)
            # 一緒にグラフデータも送る
            target = db_editor.get_work_target(user_id)
            cum = db_editor.get_work_cumulative(user_id)
            fig = make_graph(initial_date, end_date, cum, target)
            url = create_png(fig, user_id)
            mt.update_success_message(line_bot_api, reply_token, url)
            return

    if ("設定" in user_msg):
        _, _, initial_date, end_date, target, on_off = db_editor.get_data(user_id)
        days = calc_days(initial_date, end_date)
        per_day_target = target / days
        if on_off:
            on_off = 'オン'
        else:
            on_off = 'オフ'
        mt.setting_message(line_bot_api, reply_token, initial_date.date(), end_date.date(), target, per_day_target, on_off)
        return

    mt.help_message(line_bot_api, reply_token)


# 友達追加時のイベント
@handler.add(FollowEvent)
def handle_follow_message(event):
    user_id = event.source.user_id
    reply_token = event.reply_token
    user_name = line_bot_api.get_profile(user_id).display_name

    mt.start_message(line_bot_api, reply_token, user_name)


# ブロック時のイベント
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
        if (not db_editor.check_user(user_id)):
            mt.set_duration_message(line_bot_api, reply_token)
            db_editor.add_user(user_id)
            return
        else:
            mt.help_message(line_bot_api, reply_token)
            return
    elif (action == "set_end_day"):
        # 日付選択オブジェクト操作後の処理
        if (not db_editor.check_date(user_id)):
            initial_date = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
            initial_date = get_date(initial_date)
            end_date = event.postback.params['date']
            mt.set_target_message(line_bot_api, reply_token, end_date)
            # dbに開始日と終了日を追加
            db_editor.set_date(user_id, initial_date, end_date)
            return
        else:
            mt.help_message(line_bot_api, reply_token)
            return
    elif (action == "notification"):
        db_editor.set_notification(user_id)
        _, _, initial_date, end_date, _, _ = db_editor.get_data(user_id)
        target = db_editor.get_work_target(user_id)
        cum = db_editor.get_work_cumulative(user_id)
        fig = make_graph(initial_date, end_date, cum, target)
        url = create_png(fig, user_id)
        mt.notification_on_message(line_bot_api, reply_token, url)
        return
    elif (action == "no_notification"):
        db_editor.unset_notification(user_id)
        _, _, initial_date, end_date, _, _ = db_editor.get_data(user_id)
        target = db_editor.get_work_target(user_id)
        cum = db_editor.get_work_cumulative(user_id)
        fig = make_graph(initial_date, end_date, cum, target)
        url = create_png(fig, user_id)
        mt.notification_off_message(line_bot_api, reply_token, url)
        return
    else:
        mt.stop_setting_message(line_bot_api, reply_token)
        if (db_editor.check_user(user_id)):
            db_editor.del_user(user_id)
        return


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
