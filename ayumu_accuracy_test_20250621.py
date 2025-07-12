from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis, Direction, Stop
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait, multitask, run_task, StopWatch

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

# ───────────────────────────────────────────
# 実験設定
# ───────────────────────────────────────────

# テストパターンの定義
TEST_PATTERNS = [
    {"speed": 100, "distance": 200, "name": "低速・短距離"},
    {"speed": 100, "distance": 500, "name": "低速・中距離"},
    {"speed": 100, "distance": 1000, "name": "低速・長距離"},
    {"speed": 200, "distance": 200, "name": "中速・短距離"},
    {"speed": 200, "distance": 500, "name": "中速・中距離"},
    {"speed": 200, "distance": 1000, "name": "中速・長距離"},
    {"speed": 300, "distance": 200, "name": "高速・短距離"},
    {"speed": 300, "distance": 500, "name": "高速・中距離"},
    {"speed": 300, "distance": 1000, "name": "高速・長距離"},
    {"speed": 500, "distance": 200, "name": "最高速・短距離"},
    {"speed": 500, "distance": 500, "name": "最高速・中距離"},
    {"speed": 760, "distance": 200, "name": "限界速度・短距離"},
]

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
# 実験データを保存するためのリスト
# ───────────────────────────────────────────
experiment_data = []

# ログタスクの制御フラグ
logging_active = True

# ───────────────────────────────────────────
# 非同期タスクの定義
# ───────────────────────────────────────────

async def sensor_logger_task():
    """
    センサー値を定期的にターミナルに表示する非同期タスク。
    他のタスク（ロボットの移動）と並行して実行されます。
    """
    global logging_active
    print("--- センサーログタスク開始 ---")
    while logging_active:
        heading = hub.imu.heading()
        left_deg = left.angle()
        right_deg = right.angle()
        dist = robot.distance()
        print(f"LOG: dist={dist:4.0f} mm  heading={heading:4.0f}°  L={left_deg:5.0f}°  R={right_deg:5.0f}°")
        await wait(500)  # 500ミリ秒間隔でログ出力
    print("--- センサーログタスク終了 ---")

def reset_position():
    """位置とセンサーをリセット"""
    robot.stop()  # まずロボットを停止
    wait(100)     # 少し待機
    hub.imu.reset_heading(0)
    robot.reset()
    left.reset_angle(0)
    right.reset_angle(0)

async def measure_straight_performance(speed, target_distance, test_name):
    """
    直進性能を測定する関数
    
    Args:
        speed: 移動速度 (mm/s)
        target_distance: 目標移動距離 (mm)
        test_name: テストの名前
    
    Returns:
        dict: 測定結果
    """
    print(f"\n=== {test_name} テスト開始 ===")
    print(f"速度: {speed} mm/s, 目標距離: {target_distance} mm")
    
    # 測定開始前の初期化
    reset_position()
    await wait(1000)  # 1秒待機して安定化
    
    # 開始時のデータ記録
    stopwatch = StopWatch()
    start_heading = hub.imu.heading()
    start_left_angle = left.angle()
    start_right_angle = right.angle()
    
    print("移動開始...")
    
    # 時間計測開始
    stopwatch.reset()
    
    # ★重要修正★ 速度を指定して直進実行
    robot.settings(straight_speed=speed)  # 速度設定
    robot.straight(target_distance, then=Stop.BRAKE, wait=True)
    
    # 測定終了後のデータ記録
    elapsed_time = stopwatch.time() / 1000  # ミリ秒を秒に変換
    end_heading = hub.imu.heading()
    end_left_angle = left.angle()
    end_right_angle = right.angle()
    actual_distance = robot.distance()
    
    # 結果計算
    heading_error = end_heading - start_heading
    distance_error = actual_distance - target_distance
    average_speed = actual_distance / elapsed_time if elapsed_time > 0 else 0
    
    # 左右モーターの角度差（直進性の指標）
    left_rotation = end_left_angle - start_left_angle
    right_rotation = end_right_angle - start_right_angle
    motor_angle_diff = abs(left_rotation - right_rotation)
    
    # 結果を辞書で保存
    result = {
        "test_name": test_name,
        "target_speed": speed,
        "target_distance": target_distance,
        "actual_distance": actual_distance,
        "elapsed_time": elapsed_time,
        "average_speed": average_speed,
        "heading_error": heading_error,
        "distance_error": distance_error,
        "left_rotation": left_rotation,
        "right_rotation": right_rotation,
        "motor_angle_diff": motor_angle_diff
    }
    
    # 結果表示
    print(f"実際の移動距離: {actual_distance:.1f} mm")
    print(f"距離誤差: {distance_error:.1f} mm")
    print(f"所要時間: {elapsed_time:.2f} 秒")
    print(f"平均速度: {average_speed:.1f} mm/s")
    print(f"方向誤差: {heading_error:.1f}°")
    print(f"左モーター回転: {left_rotation:.1f}°")
    print(f"右モーター回転: {right_rotation:.1f}°")
    print(f"左右角度差: {motor_angle_diff:.1f}°")
    
    return result

async def main_robot_sequence_task():
    """メインの実験シーケンス"""
    global logging_active
    
    print("=== 直進性能測定実験開始 ===")
    
    # 各テストパターンを実行
    for i, pattern in enumerate(TEST_PATTERNS):
        print(f"\n【テスト {i+1}/{len(TEST_PATTERNS)}】")
        
        # ユーザーの準備確認
        print(f"次のテスト: {pattern['name']}")
        print("ロボットを開始位置に配置してください。")
        print("5秒後に自動でテストを開始します...")
        
        for countdown in range(5, 0, -1):
            print(f"開始まで {countdown} 秒...")
            await wait(1000)
        
        print("テスト開始します！")
        
        # 性能測定実行
        result = await measure_straight_performance(
            pattern["speed"], 
            pattern["distance"], 
            pattern["name"]
        )
        
        # 結果を実験データに追加
        experiment_data.append(result)
        
        # 次のテストまでの待機時間
        if i < len(TEST_PATTERNS) - 1:
            print("次のテストまで3秒待機...")
            await wait(3000)
    
    # ★重要修正★ 実験完了時にログタスクを停止
    logging_active = False
    
    # 全実験完了後の結果サマリー
    print("\n" + "="*50)
    print("=== 実験結果サマリー ===")
    print("="*50)
    
    for i, data in enumerate(experiment_data):
        print(f"\n【テスト{i+1}】{data['test_name']}")
        print(f"  距離精度: {data['distance_error']:+.1f} mm ({data['distance_error']/data['target_distance']*100:+.1f}%)")
        print(f"  方向精度: {data['heading_error']:+.1f}°")
        print(f"  速度精度: {data['average_speed']:.1f} mm/s (目標: {data['target_speed']} mm/s)")
        print(f"  直進性: 左右角度差 {data['motor_angle_diff']:.1f}°")
    
    # 最良・最悪の結果を表示
    if experiment_data:
        best_distance = min(experiment_data, key=lambda x: abs(x['distance_error']))
        best_heading = min(experiment_data, key=lambda x: abs(x['heading_error']))
        worst_distance = max(experiment_data, key=lambda x: abs(x['distance_error']))
        worst_heading = max(experiment_data, key=lambda x: abs(x['heading_error']))
        
        print(f"\n【最高精度】")
        print(f"  距離精度: {best_distance['test_name']} ({best_distance['distance_error']:+.1f} mm)")
        print(f"  方向精度: {best_heading['test_name']} ({best_heading['heading_error']:+.1f}°)")
        
        print(f"\n【要改善】")
        print(f"  距離精度: {worst_distance['test_name']} ({worst_distance['distance_error']:+.1f} mm)")
        print(f"  方向精度: {worst_heading['test_name']} ({worst_heading['heading_error']:+.1f}°)")
    
    robot.stop()

# ───────────────────────────────────────────
# プログラムの実行
# ───────────────────────────────────────────

print("直進性能測定実験プログラム")
print("このプログラムは12つの異なる条件で直進性能をテストします。")
print("各テストの前にロボットを開始位置に配置してください。")

try:
    run_task(multitask(
        sensor_logger_task(),         # センサー値を継続的にログに出力するタスク
        main_robot_sequence_task()    # ロボットの移動シーケンスを実行するタスク
    ))
except Exception as e:
    print(f"実験中にエラーが発生しました: {str(e)}")
    robot.stop()
    logging_active = False  # エラー時もログを停止

print("Finished! 実験が完了しました。結果を分析してロボットの性能改善に役立ててください。")