from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis, Direction, Stop
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase

def setup_hub():
    """ハブの向きを設定"""
    return PrimeHub(top_side=Axis.Z, front_side=Axis.X)

def setup_motors():
    """モーターの設定と初期化"""
    left = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
    right = Motor(Port.B, positive_direction=Direction.CLOCKWISE)
    return left, right

def setup_robot_parameters(left, right, straight_speed_percent=40, turn_speed_percent=30, motor_power_percent=100):
    """ロボットのパラメータ設定"""
    # 速度設定（パーセンテージで指定）
    straight_rate = straight_speed_percent          # 直進速度の最大値に対する割合
    straight_spd = 500 * (straight_rate / 100)      # 割合に沿って速度を決定
    turn_rate = turn_speed_percent                  # 旋回速度の最大値に対する割合
    turn_spd = 500 * (turn_rate / 100)              # 割合に沿って速度を決定

    print(f"速度設定: 直進={straight_speed_percent}% ({straight_spd:.0f}mm/s), 旋回={turn_speed_percent}% ({turn_spd:.0f}deg/s)")
    print(f"モーターパワー設定: {motor_power_percent}%")

    # ロボットパラメータ（実測に合わせると直進精度↑）
    robot = DriveBase(
                    left, 
                    right, 
                    wheel_diameter=56, 
                    axle_track=115   
    )

    robot.settings(
        straight_speed=straight_spd,        # 直進速度
        turn_rate=turn_spd,                # 旋回速度
    )
    
    # モーターパワーの設定
    motor_power = motor_power_percent / 100.0
    left.dc(motor_power)
    right.dc(motor_power)
    
    return robot

def setup_pid_control(robot):
    """PID制御の設定"""
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

def initialize_sensors(hub, robot):
    """センサーとジャイロの初期化"""
    robot.use_gyro(True)
    hub.imu.reset_heading(0)
    robot.reset()

def initialize_robot(straight_speed_percent=40, turn_speed_percent=30, motor_power_percent=100):
    """ロボットの完全な初期化"""
    print("=== ロボット初期化開始 ===")
    
    # ハブの設定
    hub = setup_hub()
    print("✓ ハブ設定完了")
    
    # モーターの設定
    left, right = setup_motors()
    print("✓ モーター設定完了")
    
    # ロボットパラメータの設定
    robot = setup_robot_parameters(left, right, straight_speed_percent, turn_speed_percent, motor_power_percent)
    print("✓ ロボットパラメータ設定完了")
    
    # PID制御の設定
    setup_pid_control(robot)
    print("✓ PID制御設定完了")
    
    # センサーの初期化
    initialize_sensors(hub, robot)
    print("✓ センサー初期化完了")
    
    print("=== ロボット初期化完了 ===")
    
    return hub, left, right, robot 