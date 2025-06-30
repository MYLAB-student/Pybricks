# ===========================================
#  ハブ横向き取り付けでも前進する最小コード
# ===========================================
from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis, Direction, Stop
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase

# ───────────────────────────────────────────
# 1) ハブの向きを宣言 ★USB の向きを合わせる★
#    ・LED/ボタン面は上なので top_side=Axis.Z のまま
#    ・USB ポートが
#        ├ 右側を向く → front_side=Axis.X
#        └ 左側を向く → front_side=-Axis.X
# ───────────────────────────────────────────
hub = PrimeHub(top_side=Axis.Z,
               front_side=Axis.X)      # ←必要なら「-Axis.X」に

# ───────────────────────────────────────────
# 2) モーターの極性を宣言 ★タイヤが“前”へ回る向きか確認★
#    左ホイールを run(200) で回したとき
#        ├ 前へ進む → Direction.CLOCKWISE
#        └ 後ろへ進む → Direction.COUNTERCLOCKWISE
#    ※右ホイールは左右対称なので左右で逆になることが多い
# ───────────────────────────────────────────
left  = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
right = Motor(Port.B, positive_direction=Direction.CLOCKWISE)


# ロボットパラメータ（実測に合わせると直進精度↑）
robot = DriveBase(left, right, wheel_diameter=62.4, axle_track=115)

# ───────────────────────────────────────────
# 3) ジャイロ PID を有効化し、速度と距離を指定
# ───────────────────────────────────────────
robot.use_gyro(True)          # ジャイロで姿勢自動補正
hub.imu.reset_heading(0)      # ヘディングを 0°
robot.reset()                 # 走行距離を 0 mm

robot.settings(straight_speed=150)  # ≒30 %パワー（150 mm/s）
robot.straight(500)                 # 500 mm 前進
robot.stop(Stop.HOLD)               # 到達後に姿勢を保持


"""
ポイントのおさらい

front_side を USB ポートが向いている実方向に合わせる。

positive_direction を「正転＝前進」になるように左右それぞれ設定。

修正後は必ず hub.imu.reset_heading(0) → 軽く右に回して 数値が＋ になるか簡易テスト。

これで robot.straight(500) は確実に “前へ 50 cm 真っ直ぐ” になります。

Pybricks Code での「保存」完全ガイド

やりたいこと	操作
ブラウザ内に上書き保存	Ctrl + S または 画面左上の フロッピーアイコン（自動保存も有効）
PC にバックアップ	ファイルタブでプログラムにマウスを当て → ⬇︎ アイコン（Back up） をクリック → .py か .zip がダウンロードされる
修正後のプログラムをハブに書き込む	① Bluetooth 接続 → ② ▶（Run） か ↓（Download） を押す → ハブに上書き保存され、次回からはハブ中央ボタンだけで起動
名前を変える／複製する	ファイルタブでプログラムにカーソル → ✏️ Rename / 📄 Duplicate
全プログラムを一括バックアップ	ファイルタブ上部の Back up all programs

Pybricks Code のファイル管理ボタンは公式チュートリアルにもまとまっています。
Pybricks

💡 ヒント

ブラウザのキャッシュを消すとローカル保存分は消えるので、こまめに Back up しておくと安心です。

ハブ側には常に “最後に書き込んだ 1 本” だけが残ります。大会用に複数プログラムを持ちたい場合はメニュー方式（公式プロジェクト例あり）を使うと便利です。

これでコード修正 → 保存 → ハブ書き込みまで迷わず進められます。

https://chatgpt.com/c/68354691-4b74-8005-99d4-8456a6a34952?src=history_search

"""

