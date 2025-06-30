from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis, Direction, Stop
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# ───────────────────────────────────────────
# 1) ハブの向きを宣言 ★USB の向きを合わせる★
# ───────────────────────────────────────────
hub = PrimeHub(top_side=Axis.Z,
               front_side=Axis.X)      # ←必要なら「-Axis.X」に

# ───────────────────────────────────────────
# 2) モーターの極性を宣言 ★タイヤが"前"へ回る向きか確認★
# ───────────────────────────────────────────
left  = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
right = Motor(Port.B, positive_direction=Direction.CLOCKWISE)

# ロボットパラメータ（実測に合わせると直進精度↑）
robot = DriveBase(left, right, wheel_diameter=56, axle_track=115)

# --- PIDゲイン変数の定義 ---
# 前進距離制御 (distance_control) のゲイン
# Kp: 比例ゲイン, Ki: 積分ゲイン, Kd: 微分ゲイン
# 初期値はロボットや環境によって調整が必要です。
# デフォルト値から少しずつ変更して試すことを推奨します。
DISTANCE_KP = 1000 # 例: Pゲインを少し高めに設定
DISTANCE_KI = 50   # 例: わずかな定常偏差を解消するためにKiを設定
DISTANCE_KD = 10   # 例: オーバーシュート抑制と安定化のためにKdを設定

# 旋回方向制御 (heading_control) のゲイン
# ロボットがまっすぐ進まず蛇行する場合に特に重要です。
HEADING_KP = 2000 # 例: 旋回時のPゲイン
HEADING_KI = 50   # 例: 旋回時のIゲイン
HEADING_KD = 100  # 例: 旋回時のDゲイン (過度な修正を抑制)

# --- PIDゲインの設定 ---
robot.distance_control.pid(
    kp=DISTANCE_KP,
    ki=DISTANCE_KI,
    kd=DISTANCE_KD
)

robot.heading_control.pid(
    kp=HEADING_KP,
    ki=HEADING_KI,
    kd=HEADING_KD
)

# ───────────────────────────────────────────
# 3) ジャイロ PID を有効化し、計測を初期化
# ───────────────────────────────────────────
robot.use_gyro(True)          # ジャイロで姿勢自動補正
hub.imu.reset_heading(0)      # ヘディングを 0°
robot.reset()                 # 走行距離を 0 mm

# 走行設定
DISTANCE_MM = 500             # 走行距離
STRAIGHT_SPEED = 150          # ≒30 %パワー（150 mm/s）

# PID設定を穏やかに調整
# robot.settings(
#     straight_speed=STRAIGHT_SPEED,
#     straight_acceleration=100,  # 加速度を下げる（デフォルトより穏やか）
#     turn_rate=50,              # 旋回レートを下げる（デフォルトより穏やか）
#     turn_acceleration=50       # 旋回加速度を下げる（デフォルトより穏やか）
# )

# ───────────────────────────────────────────
# 走行を開始し、途中でセンサー値を取得して表示
# ───────────────────────────────────────────
for i in range(10):
    heading = hub.imu.heading()     
    left_deg = left.angle()         
    right_deg = right.angle()       
    dist = robot.distance()         
    print(f"{str(i)}:dist={dist:4.0f} mm  heading={heading:4.0f}°  L={left_deg:5.0f}°  R={right_deg:5.0f}°")

    if i%2==0:
        robot.straight(-STRAIGHT_SPEED)  # 前進開始
        robot.turn(-90)
        wait(10)
    else:
        robot.turn(90)
        robot.straight(STRAIGHT_SPEED)  # 前進開始
        wait(10)
        


# 到達後に穏やかに停止
#robot.stop(Stop.BRAKE)  # HOLDからBRAKEに変更

print("Finished!")