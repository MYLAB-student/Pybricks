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
robot.settings(
    straight_speed=STRAIGHT_SPEED,
    straight_acceleration=100,  # 加速度を下げる（デフォルトより穏やか）
    turn_rate=50,              # 旋回レートを下げる（デフォルトより穏やか）
    turn_acceleration=50       # 旋回加速度を下げる（デフォルトより穏やか）
)

# ───────────────────────────────────────────
# 走行を開始し、途中でセンサー値を取得して表示
# ───────────────────────────────────────────
robot.drive(STRAIGHT_SPEED, 0)  # 前進開始

while abs(robot.distance()) < DISTANCE_MM:
    # 各種センサー値を取得
    heading = hub.imu.heading()      # ヘディング角 [°]
    left_deg = left.angle()          # 左モーター角度 [°]
    right_deg = right.angle()        # 右モーター角度 [°]
    dist = robot.distance()          # 走行距離 [mm]

    # Pybricks Code のターミナルへ出力
    print(f"dist={dist:4.0f} mm  heading={heading:4.0f}°  L={left_deg:5.0f}°  R={right_deg:5.0f}°")

    wait(100)  # 100 ms 間隔で更新

# 到達後に穏やかに停止
robot.stop(Stop.BRAKE)  # HOLDからBRAKEに変更

print("Finished!")