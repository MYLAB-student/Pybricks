from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis, Direction, Stop
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait, multitask, run_task

# ───────────────────────────────────────────
# 1) ハブの向きを宣言 ★USB の向きを合わせる★
# ───────────────────────────────────────────
hub = PrimeHub(top_side=Axis.Z,
               front_side=Axis.X)

# ───────────────────────────────────────────
# 2) モーターの極性を宣言 ★タイヤが"前"へ回る向きか確認★
# ───────────────────────────────────────────
left  = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
right = Motor(Port.B, positive_direction=Direction.CLOCKWISE)

# ロボットパラメータ（実測に合わせると直進精度↑）
robot = DriveBase(left, right, wheel_diameter=56, axle_track=115)

# 走行設定
STRAIGHT_DISTANCE_MM = 500
TURN_ANGLE_DEG = 30

# --- PIDゲイン変数の定義 ---
DISTANCE_KP = 1000
DISTANCE_KI = 50
DISTANCE_KD = 10

HEADING_KP = 2000
HEADING_KI = 50
HEADING_KD = 100

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
robot.use_gyro(True)
hub.imu.reset_heading(0)
robot.reset()



# ───────────────────────────────────────────
# 非同期タスクの定義
# ───────────────────────────────────────────

async def sensor_logger_task():
    """
    センサー値を定期的にターミナルに表示する非同期タスク。
    他のタスク（ロボットの移動）と並行して実行されます。
    """
    print("--- センサーログタスク開始 ---")
    while True: # プログラムが終了するまで継続的にログを出力
        heading = hub.imu.heading()
        left_deg = left.angle()
        right_deg = right.angle()
        dist = robot.distance()
        print(f"LOG: dist={dist:4.0f} mm  heading={heading:4.0f}°  L={left_deg:5.0f}°  R={right_deg:5.0f}°")
        await wait(100) # 100ミリ秒待機して、他のタスクに実行を譲る

async def main_robot_sequence_task():
    """
    ロボットの移動シーケンス（直進 → 停止 → 旋回）を制御する非同期タスク。
    robot.straight() や robot.turn() は同期的に動作するため、
    それぞれの処理が完了するまで await で待機します。
    """
    for i in range(10):


        if i%2==0:
            
            #await robot.straight(-STRAIGHT_DISTANCE_MM)  # 前進開始
            await robot.turn(-TURN_ANGLE_DEG)
            await wait(1000)
        else:
            
            await robot.turn(TURN_ANGLE_DEG)
            #await robot.straight(STRAIGHT_DISTANCE_MM)  # 前進開始
            await wait(1000)


    robot.stop()



# ───────────────────────────────────────────
# プログラムの実行
# ───────────────────────────────────────────

# run_task() を使うことで、main_robot_sequence_task が完了するまで
# プログラム全体が終了しないようにします。
# sensor_logger_task は main_robot_sequence_task と並行して動作します。
# run_task() が終わると、他のすべてのタスクも停止します。
run_task(multitask(
    sensor_logger_task(),         # センサー値を継続的にログに出力するタスク
    main_robot_sequence_task()    # ロボットの移動シーケンスを実行するタスク
))

print("Finished! (すべてのタスクが完了しました)") # この行はタスク完了後に実行される