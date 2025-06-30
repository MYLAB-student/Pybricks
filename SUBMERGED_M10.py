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

lift = Motor(Port.A, positive_direction=Direction.CLOCKWISE)

# ロボットパラメータ（実測に合わせると直進精度↑）
robot = DriveBase(left, right, wheel_diameter=56, axle_track=115)

# 走行設定
FIRST_STRAIGHT_DISTANCE_MM = 260
TURN_ANGLE_DEG = -45
TO_TOWER_DISTANCE_MM = 670
LIFT_ARM_TURN_ANGLE = 500
LIFT_ARM_TURN_SPEED = 180

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
lift.reset_angle(0)



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
        await wait(1000) # 100ミリ秒待機して、他のタスクに実行を譲る

async def main_robot_sequence_task():
    print("Start Go Forward")
    await robot.straight(FIRST_STRAIGHT_DISTANCE_MM)
    print("Stop")
    
    await wait(1000)
    
    print("Start Turn To Mission Tower")
    await robot.turn(TURN_ANGLE_DEG)
    print("Stop")
    
    await wait(1000)
    
    print("Start Go To Mission Tower")
    await robot.straight(TO_TOWER_DISTANCE_MM)
    print("Stop")

    await wait(1000)
    
    print("Start Lifting Tower")
    await lift.run_target(LIFT_ARM_TURN_SPEED, LIFT_ARM_TURN_ANGLE)

    await wait(1000)

    print("Return")
    await lift.run_target(LIFT_ARM_TURN_SPEED, 0)
    print("Mission Complete")

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