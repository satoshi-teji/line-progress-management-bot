from linebot.models import (
    TextMessage,
    TextSendMessage,
    ImageSendMessage,
    TemplateSendMessage,
    ConfirmTemplate,
    ButtonsTemplate,
    PostbackAction,
    DatetimePickerTemplateAction
)

import datetime


def get_date(datetime_data):
    return "{:04}-{:02}-{:02}".format(
        datetime_data.year, datetime_data.month, datetime_data.day)


def help_message(line_bot_api, reply_token):
    line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="現在進捗管理を行っています。\n設定がみたい場合は「設定」と送信してください。\n利用を中止する場合は「利用中止」と送信してください。\n「進捗 3回」のように送信することで今日の進捗を更新します。\n進捗をグラフでみたい場合は「グラフ」と送信してください。"
                )]
    )
    return


def start_message(line_bot_api, reply_token, user_name):
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
    return


def invalid_message(line_bot_api, reply_token):
    line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="「利用開始」とメッセージを送信することで初期設定を行います。\n必要なくなった場合はブロックしてください。ブロックを解除することで利用を再開できます。"
                )]
    )
    return


def stop_using_message(line_bot_api, reply_token):
    line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="利用を中止しました。"
                )]
    )
    return


def stop_setting_message(line_bot_api, reply_token):
    line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="設定を中止しました。"
                )]
    )
    return


def setting_message(
        line_bot_api,
        reply_token,
        initial_date,
        end_date,
        target,
        per_day,
        on_off):
    line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="設定はこのようになっています。\n期間: {} ~ {}\n最終目標: {}\n一日あたり: {}\n通知 {}".format(
                        initial_date, end_date, target, per_day, on_off))
            ]
    )
    return


def set_notification_message(
        line_bot_api,
        reply_token,
        initial_date,
        end_date,
        target,
        per_day):
    line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="期間: {} ~ {}\n最終目標: {}\n一日あたり: {}".format(
                        initial_date, end_date, target, per_day)
                ),
                TemplateSendMessage(alt_text="毎日21時に進捗状況グラフを送りますか?",
                                    template=ConfirmTemplate(
                                        text="毎日21時に進捗状況グラフを送りますか?\n設定してもしなくても「進捗状況」とメッセージを送信することで任意の時間に受信が可能です。",
                                        actions=[
                                            PostbackAction(
                                                label="Yes",
                                                display_text="はい",
                                                data="action=notification"
                                            ),
                                            PostbackAction(
                                                label="No",
                                                display_text="いいえ",
                                                data="action=no_notification"
                                            )]
                                        )
                                    )
            ]
    )
    return


def notification_on_message(line_bot_api, reply_token, url):
    line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="通知設定をオンにしました。\nこれで設定は完了です。\n「進捗 3ページ」のようにメッセージを送信することでその日の進捗を更新できます。"
                ),
                ImageSendMessage(
                    original_content_url=url,
                    preview_image_url=url
                ),
                TextSendMessage(
                    text="青色の線が赤色の線に近づくように頑張りましょう！！"
                )
            ]
    )


def notification_off_message(line_bot_api, reply_token, url):
    line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="通知設定をオフにしました。\nこれで設定は完了です。\n「進捗 3ページ」のようにメッセージを送信することでその日の進捗を更新できます。"
                ),
                ImageSendMessage(
                    original_content_url=url,
                    preview_image_url=url
                ),
                TextSendMessage(
                    text="青色の線が赤色の線に近づくように頑張りましょう！！"
                )
            ]
    )


def set_duration_message(line_bot_api, reply_token):
    # 確実に日本時間での時間を取得する
    initial_date = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    limit_date = initial_date + datetime.timedelta(days=90)
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
                        initial_date+datetime.timedelta(days=30)
                        ),
                    min=get_date(initial_date),
                    max=get_date(limit_date)
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


def num_error_message(line_bot_api, reply_token):
    line_bot_api.reply_message(
                reply_token,
                [
                    TextSendMessage(
                        text="数値を入力してください。設定を中止する場合は「設定中止」とメッセージを送信してください。"
                    )]
    )
    return


def set_target_message(line_bot_api, reply_token, end_date):
    line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="期限を{}に設定しました。\n最終目標を設定します。最終目標をメッセージで送信してください。(整数で送信してください。)".format(end_date)
                )]
    )


def update_success_message(line_bot_api, reply_token, url):
    line_bot_api.reply_message(
            reply_token,
            [
                TextSendMessage(
                    text="今日の進捗を更新しました"
                ),
                ImageSendMessage(
                    original_content_url=url,
                    preview_image_url=url
                )
                ]
    )
