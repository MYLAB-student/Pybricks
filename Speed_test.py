from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis, Direction, Stop
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait, multitask, run_task

def setup_hub():
    """ハブの向きを設定"""
    return PrimeHub(top_side=Axis.Z, front_side=Axis.X)

def setup_motors():
    """モーターの設定と初期化"""
    left = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
    right = Motor(Port.B, positive_direction=Direction.CLOCKWISE)
    lift = Motor(Port.A, positive_direction=Direction.CLOCKWISE)
    return left, right, lift

def setup_robot_parameters(left, right):
    """ロボットのパラメータ設定"""
    straight_rate = 40                              # 直進速度の最大値に対する割合
    straight_spd = 500 * (straight_rate / 100)      # 割合に沿って速度を決定
    turn_rate = 30                                  # 旋回速度の最大値に対する割合
    turn_spd = 500 * (turn_rate / 100)              # 割合に沿って速度を決定

    # ロボットパラメータ（実測に合わせると直進精度↑）
    robot = DriveBase(
                    left, 
                    right, 
                    wheel_diameter=56, 
                    axle_track=115   
    )

    robot.settings(
        straight_speed=straight_spd,        # 直進速度      デフォルト:200mm/s      最大速度の40%
        # straight_acceleration             # 直進加速度    デフォルト:400mm/s^2    
        turn_rate=turn_spd,                # 旋回速度      デフォルト:200deg/s     最大速度の40%
        # turn_acceleration=360             # 旋回加速度    デフォルト:400deg/s^2
    )
    
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

def initialize_sensors(hub, robot, lift):
    """センサーとジャイロの初期化"""
    # ───────────────────────────────────────────
    # ジャイロ PID を有効化し、計測を初期化
    # ───────────────────────────────────────────
    robot.use_gyro(True)
    hub.imu.reset_heading(0)
    robot.reset()
    lift.reset_angle(0)

def get_mission_parameters():
    """ミッション用パラメータの取得"""
    return {
        'FIRST_STRAIGHT_DISTANCE_MM': 260,
        'TURN_ANGLE_DEG': -45,
        'TO_TOWER_DISTANCE_MM': 710,
        'LIFT_ARM_TURN_ANGLE': 500,
        'LIFT_ARM_TURN_SPEED': 180
    }

async def sensor_logger_task(hub, left, right, robot):
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
        await wait(200) # 100ミリ秒待機して、他のタスクに実行を譲る

async def main_robot_sequence_task(robot, lift, params):
    """メインのロボット動作シーケンス"""
    print("Start Go Forward")
    await robot.straight(params['FIRST_STRAIGHT_DISTANCE_MM'])
    print("Stop")
    
    await wait(1000)
    
    print("Start Turn To Mission Tower")
    await robot.turn(params['TURN_ANGLE_DEG'])
    print("Stop")
    
    await wait(1000)
    
    print("Start Go To Mission Tower")
    await robot.straight(params['TO_TOWER_DISTANCE_MM'])
    print("Stop")

    await wait(1000)
    
    print("Start Lifting Tower")
    await lift.run_target(params['LIFT_ARM_TURN_SPEED'], params['LIFT_ARM_TURN_ANGLE'])

    await wait(1000)

    print("Return")
    await lift.run_target(params['LIFT_ARM_TURN_SPEED'], 0)
    print("Mission Complete")

    robot.stop()

async def turn_test(robot, hub):
    """旋回テスト機能"""
    set_angle = 30
    for i in range(1, (180/set_angle)+1, 1): 
        angle = set_angle * i
        print(f"setting_angles = {angle:4.0f}°")
        await robot.turn(angle)
        await wait(1000)

        robot.stop()

        robot.use_gyro(False)
        hub.imu.reset_heading(0)
        robot.use_gyro(True)
    
    print("Test_Complete")

async def turn_accuracy_test(robot, hub):
    """旋回精度測定テスト"""
    print("=== 旋回精度測定テスト開始 ===")
    
    # テストする角度のリスト
    test_angles = [30, 45, 60, 90, 120, 135, 150, 180]
    
    # 精度データを保存するリスト
    accuracy_data = []
    
    for target_angle in test_angles:
        print(f"\n--- {target_angle}度旋回テスト ---")
        
        # 旋回前の角度を記録
        start_heading = hub.imu.heading()
        print(f"開始角度: {start_heading:.1f}°")
        
        # 旋回実行
        print(f"目標角度: {target_angle}° で旋回開始")
        await robot.turn(target_angle)
        
        # 旋回後の角度を記録
        await wait(500)  # 安定化のため少し待機
        end_heading = hub.imu.heading()
        print(f"終了角度: {end_heading:.1f}°")
        
        # 実際の旋回角度を計算
        actual_angle = end_heading - start_heading
        
        # 精度を計算
        error = abs(target_angle - actual_angle)
        accuracy_percent = max(0, 100 - (error / target_angle * 100))
        
        print(f"実際の旋回角度: {actual_angle:.1f}°")
        print(f"誤差: {error:.1f}°")
        print(f"精度: {accuracy_percent:.1f}%")
        
        # データを保存
        accuracy_data.append({
            'target': target_angle,
            'actual': actual_angle,
            'error': error,
            'accuracy': accuracy_percent
        })
        
        # 次のテストのためリセット
        await wait(1000)
        robot.stop()
        robot.use_gyro(False)
        hub.imu.reset_heading(0)
        robot.use_gyro(True)
        await wait(500)
    
    # 結果サマリーを表示
    print("\n=== 旋回精度測定結果サマリー ===")
    print("角度\t目標\t実際\t誤差\t精度")
    print("-" * 40)
    
    total_error = 0
    total_accuracy = 0
    
    for data in accuracy_data:
        print(f"{data['target']:3.0f}°\t{data['target']:3.0f}°\t{data['actual']:5.1f}°\t{data['error']:4.1f}°\t{data['accuracy']:5.1f}%")
        total_error += data['error']
        total_accuracy += data['accuracy']
    
    avg_error = total_error / len(accuracy_data)
    avg_accuracy = total_accuracy / len(accuracy_data)
    
    print("-" * 40)
    print(f"平均誤差: {avg_error:.1f}°")
    print(f"平均精度: {avg_accuracy:.1f}%")
    
    # 精度評価
    if avg_accuracy >= 95:
        print("評価: 優秀 (95%以上)")
    elif avg_accuracy >= 90:
        print("評価: 良好 (90-95%)")
    elif avg_accuracy >= 80:
        print("評価: 普通 (80-90%)")
    else:
        print("評価: 要改善 (80%未満)")
    
    print("=== 旋回精度測定テスト完了 ===")

async def continuous_accuracy_monitor(robot, hub):
    """連続精度モニタリング"""
    print("=== 連続精度モニタリング開始 ===")
    print("任意の角度で旋回テストを行います")
    print("終了するには 'q' を入力してください")
    
    while True:
        try:
            # ユーザー入力（実際のロボットでは固定値を使用）
            target_angle = 45  # テスト用固定値
            
            print(f"\n--- {target_angle}度旋回テスト ---")
            
            # 旋回前の角度
            start_heading = hub.imu.heading()
            print(f"開始角度: {start_heading:.1f}°")
            
            # 旋回実行
            await robot.turn(target_angle)
            await wait(500)
            
            # 旋回後の角度
            end_heading = hub.imu.heading()
            actual_angle = end_heading - start_heading
            
            # 精度計算
            error = abs(target_angle - actual_angle)
            accuracy = max(0, 100 - (error / target_angle * 100))
            
            print(f"目標: {target_angle}° → 実際: {actual_angle:.1f}°")
            print(f"誤差: {error:.1f}° (精度: {accuracy:.1f}%)")
            
            # リセット
            await wait(1000)
            robot.stop()
            robot.use_gyro(False)
            hub.imu.reset_heading(0)
            robot.use_gyro(True)
            await wait(500)
            
            # 実際のロボットでは無限ループを避けるため、テスト回数を制限
            break
            
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            break
    
    print("=== 連続精度モニタリング終了 ===")

def run_mission():
    """メインミッションの実行"""
    # 初期化
    hub = setup_hub()
    left, right, lift = setup_motors()
    robot = setup_robot_parameters(left, right)
    setup_pid_control(robot)
    initialize_sensors(hub, robot, lift)
    
    # パラメータ取得
    params = get_mission_parameters()
    
    # タスク実行
    run_task(multitask(
        sensor_logger_task(hub, left, right, robot),         # センサー値を継続的にログに出力するタスク
        # main_robot_sequence_task(robot, lift, params)      # ロボットの移動シーケンスを実行するタスク
        # turn_test(robot, hub)                              # 基本的な旋回テスト
        turn_accuracy_test(robot, hub)                       # 旋回精度測定テスト
        # continuous_accuracy_monitor(robot, hub)            # 連続精度モニタリング
    ))

    print("Finished! (すべてのタスクが完了しました)") # この行はタスク完了後に実行される

# プログラムの実行
if __name__ == "__main__":
    run_mission()