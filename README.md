# LINE 進捗管理くん のソースコード
友達追加用QRコード
![QRコード](https://raw.githubusercontent.com/satoshi-teji/line-progress-management-bot/main/doc/images/QR.png)
***
## 機能
期間、目標設定を行うと1日当たりに産むべき進捗を計算する。\
また日々の進捗を更新することで目標とどれだけ差があるかをグラフで可視化する。
## 改善したいところ
heroku上で動作しているため時間が経つとスリープしてしまいbotからの返信に時間がかかる。\
進捗管理中に送るメッセージをButtons Templateを使って実装する。



### TODO
特定の時間になったらその日の進捗の有無を聞くメッセージの送信を行うようにする。\
期間が終わった後の機能の追加
