from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis, Direction, Stop
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait, multitask, run_task
from setup import initialize_robot

async def sensor_logger_task(hub, left, right, robot):
    """センサー値を定期的にターミナルに表示する非同期タスク"""
    print("--- センサーログタスク開始 ---")
    while True:
        heading = hub.imu.heading()
        left_deg = left.angle()
        right_deg = right.angle()
        dist = robot.distance()
        print(f"LOG: dist={dist:4.0f} mm  heading={heading:4.0f}°  L={left_deg:5.0f}°  R={right_deg:5.0f}°")
        await wait(200)

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

async def single_angle_test(robot, hub, target_angle):
    """単一角度での旋回精度テスト"""
    print(f"\n=== {target_angle}度旋回精度テスト ===")
    
    # 旋回前の角度を記録
    start_heading = hub.imu.heading()
    print(f"開始角度: {start_heading:.1f}°")
    
    # 旋回実行
    print(f"目標角度: {target_angle}° で旋回開始")
    await robot.turn(target_angle)
    
    # 旋回後の角度を記録
    await wait(500)
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
    
    # 精度評価
    if accuracy_percent >= 95:
        print("評価: 優秀")
    elif accuracy_percent >= 90:
        print("評価: 良好")
    elif accuracy_percent >= 80:
        print("評価: 普通")
    else:
        print("評価: 要改善")
    
    return {
        'target': target_angle,
        'actual': actual_angle,
        'error': error,
        'accuracy': accuracy_percent
    }

async def repeat_accuracy_test(robot, hub, target_angle, repeat_count=5):
    """同じ角度での繰り返し精度テスト"""
    print(f"\n=== {target_angle}度旋回 繰り返し精度テスト ({repeat_count}回) ===")
    
    results = []
    
    for i in range(repeat_count):
        print(f"\n--- {i+1}回目 ---")
        
        # リセット
        robot.use_gyro(False)
        hub.imu.reset_heading(0)
        robot.use_gyro(True)
        await wait(500)
        
        # テスト実行
        result = await single_angle_test(robot, hub, target_angle)
        results.append(result)
        
        # 次のテストのため待機
        await wait(1000)
        robot.stop()
    
    # 統計結果を表示
    print(f"\n=== {target_angle}度旋回 統計結果 ===")
    errors = [r['error'] for r in results]
    accuracies = [r['accuracy'] for r in results]
    
    avg_error = sum(errors) / len(errors)
    avg_accuracy = sum(accuracies) / len(accuracies)
    max_error = max(errors)
    min_error = min(errors)
    
    print(f"平均誤差: {avg_error:.1f}°")
    print(f"最大誤差: {max_error:.1f}°")
    print(f"最小誤差: {min_error:.1f}°")
    print(f"平均精度: {avg_accuracy:.1f}%")
    print(f"精度のばらつき: {max_error - min_error:.1f}°")

async def speed_comparison_test(robot, hub, target_angle=90):
    """異なる速度での精度比較テスト"""
    print(f"\n=== 速度比較テスト ({target_angle}度旋回) ===")
    
    # テストする速度設定（15%ずつ）
    speed_settings = [
        (15, 10),   # 直進15%, 旋回10%
        (30, 25),   # 直進30%, 旋回25%
        (45, 40),   # 直進45%, 旋回40%
        (60, 55),   # 直進60%, 旋回55%
        (75, 70),   # 直進75%, 旋回70%
        (90, 85),   # 直進90%, 旋回85%
    ]
    
    speed_results = []
    
    for straight_speed, turn_speed in speed_settings:
        print(f"\n--- 速度設定: 直進{straight_speed}%, 旋回{turn_speed}% ---")
        
        # ロボットの速度設定を更新
        straight_spd = 500 * (straight_speed / 100)
        turn_spd = 500 * (turn_speed / 100)
        
        # 速度設定を適用
        robot.settings(straight_speed=straight_spd, turn_rate=turn_spd)
        
        print(f"実際の速度: 直進{straight_spd:.0f}mm/s, 旋回{turn_spd:.0f}deg/s")
        
        # リセット
        robot.use_gyro(False)
        hub.imu.reset_heading(0)
        robot.use_gyro(True)
        await wait(500)
        
        # テスト実行
        result = await single_angle_test(robot, hub, target_angle)
        
        # 速度情報を追加
        result['straight_speed_percent'] = straight_speed
        result['turn_speed_percent'] = turn_speed
        result['straight_speed_mmps'] = straight_spd
        result['turn_speed_degps'] = turn_spd
        
        speed_results.append(result)
        
        # 次のテストのため待機
        await wait(1000)
        robot.stop()
    
    # 速度比較結果を表示
    print(f"\n=== 速度比較テスト結果サマリー ===")
    print("直進速度\t旋回速度\t目標角度\t実際角度\t誤差\t精度")
    print("-" * 70)
    
    for result in speed_results:
        straight_info = f"{result['straight_speed_percent']:3.0f}% ({result['straight_speed_mmps']:3.0f}mm/s)"
        turn_info = f"{result['turn_speed_percent']:3.0f}% ({result['turn_speed_degps']:3.0f}deg/s)"
        target_info = f"{result['target']:3.0f}°"
        actual_info = f"{result['actual']:5.1f}°"
        error_info = f"{result['error']:4.1f}°"
        accuracy_info = f"{result['accuracy']:5.1f}%"
        
        print(f"{straight_info}\t{turn_info}\t{target_info}\t{actual_info}\t{error_info}\t{accuracy_info}")
    
    # 最良の精度を特定
    best_result = min(speed_results, key=lambda x: x['error'])
    print(f"\n最良の精度: 直進{best_result['straight_speed_percent']}%, 旋回{best_result['turn_speed_percent']}%")
    print(f"誤差: {best_result['error']:.1f}°, 精度: {best_result['accuracy']:.1f}%")
    
    return speed_results

async def comprehensive_test(robot, hub, target_angle=90):
    """速度とモーター出力の組み合わせによる包括的テスト"""
    print(f"\n=== 包括的テスト ({target_angle}度旋回) ===")
    
    # テストする速度設定
    speed_settings = [
        (15, 10),   # 直進15%, 旋回10%
        (30, 25),   # 直進30%, 旋回25%
        (45, 40),   # 直進45%, 旋回40%
        (60, 55),   # 直進60%, 旋回55%
        (75, 70),   # 直進75%, 旋回70%
        (90, 85),   # 直進90%, 旋回85%
    ]
    
    # テストするモーター出力設定
    motor_power_settings = [50, 75, 100, 125, 150]
    
    comprehensive_results = []
    
    for straight_speed, turn_speed in speed_settings:
        for motor_power in motor_power_settings:
            print(f"\n--- 速度: 直進{straight_speed}%/旋回{turn_speed}%, モーター出力: {motor_power}% ---")
            
            # ロボットの速度設定を更新
            straight_spd = 500 * (straight_speed / 100)
            turn_spd = 500 * (turn_speed / 100)
            
            # 速度設定を適用
            robot.settings(straight_speed=straight_spd, turn_rate=turn_spd)
            
            # モーター出力設定を適用
            left_motor = robot.left_motor
            right_motor = robot.right_motor
            left_motor.control.limits(power=motor_power)
            right_motor.control.limits(power=motor_power)
            
            print(f"実際の設定: 直進{straight_spd:.0f}mm/s, 旋回{turn_spd:.0f}deg/s, モーター出力{motor_power}%")
            
            # リセット
            robot.use_gyro(False)
            hub.imu.reset_heading(0)
            robot.use_gyro(True)
            await wait(500)
            
            # テスト実行
            result = await single_angle_test(robot, hub, target_angle)
            
            # 設定情報を追加
            result['straight_speed_percent'] = straight_speed
            result['turn_speed_percent'] = turn_speed
            result['motor_power_percent'] = motor_power
            result['straight_speed_mmps'] = straight_spd
            result['turn_speed_degps'] = turn_spd
            
            comprehensive_results.append(result)
            
            # 次のテストのため待機
            await wait(1000)
            robot.stop()
    
    # 包括的テスト結果を表示
    print(f"\n=== 包括的テスト結果サマリー ===")
    print("直進速度\t旋回速度\tモーター出力\t目標角度\t実際角度\t誤差\t精度")
    print("-" * 90)
    
    for result in comprehensive_results:
        straight_info = f"{result['straight_speed_percent']:3.0f}%"
        turn_info = f"{result['turn_speed_percent']:3.0f}%"
        power_info = f"{result['motor_power_percent']:3.0f}%"
        target_info = f"{result['target']:3.0f}°"
        actual_info = f"{result['actual']:5.1f}°"
        error_info = f"{result['error']:4.1f}°"
        accuracy_info = f"{result['accuracy']:5.1f}%"
        
        print(f"{straight_info}\t\t{turn_info}\t\t{power_info}\t\t{target_info}\t{actual_info}\t{error_info}\t{accuracy_info}")
    
    # 最良の精度を特定
    best_result = min(comprehensive_results, key=lambda x: x['error'])
    print(f"\n最良の精度設定:")
    print(f"直進速度: {best_result['straight_speed_percent']}%, 旋回速度: {best_result['turn_speed_percent']}%")
    print(f"モーター出力: {best_result['motor_power_percent']}%")
    print(f"誤差: {best_result['error']:.1f}°, 精度: {best_result['accuracy']:.1f}%")
    
    return comprehensive_results

def run_experiment(straight_speed_percent=40, turn_speed_percent=30, motor_power_percent=100):
    """実験の実行"""
    print("=== 旋回精度実験開始 ===")
    
    # 初期化
    hub, left, right, robot = initialize_robot(straight_speed_percent, turn_speed_percent, motor_power_percent)
    
    # 実験実行
    run_task(multitask(
        sensor_logger_task(hub, left, right, robot),  # センサー値ログ
        turn_accuracy_test(robot, hub)                # 旋回精度測定テスト
    ))

    print("=== 実験完了 ===")

def run_single_test(straight_speed_percent=40, turn_speed_percent=30, motor_power_percent=100, target_angle=90):
    """単一角度テストの実行"""
    print("=== 単一角度旋回テスト開始 ===")
    
    # 初期化
    hub, left, right, robot = initialize_robot(straight_speed_percent, turn_speed_percent, motor_power_percent)
    
    # テスト実行
    run_task(single_angle_test(robot, hub, target_angle))

def run_repeat_test(straight_speed_percent=40, turn_speed_percent=30, motor_power_percent=100, target_angle=90, repeat_count=5):
    """繰り返しテストの実行"""
    print("=== 繰り返し精度テスト開始 ===")
    
    # 初期化
    hub, left, right, robot = initialize_robot(straight_speed_percent, turn_speed_percent, motor_power_percent)
    
    # テスト実行
    run_task(repeat_accuracy_test(robot, hub, target_angle, repeat_count))

def run_speed_comparison_test(target_angle=90, motor_power_percent=100):
    """速度比較テストの実行"""
    print("=== 速度比較テスト開始 ===")
    
    # 初期化
    hub, left, right, robot = initialize_robot(40, 30, motor_power_percent)  # 初期設定（後で変更される）
    
    # テスト実行（センサーログなしで単独実行）
    run_task(speed_comparison_test(robot, hub, target_angle))

def run_comprehensive_test(target_angle=90):
    """包括的テストの実行"""
    print("=== 包括的テスト開始 ===")
    
    # 初期化
    hub, left, right, robot = initialize_robot(40, 30, 100)  # 初期設定（後で変更される）
    
    # テスト実行
    run_task(comprehensive_test(robot, hub, target_angle))

# プログラムの実行
if __name__ == "__main__":
    print("=== 旋回精度テストメニュー ===")
    print("1. 全角度精度測定テスト")
    print("2. 単一角度テスト")
    print("3. 繰り返し精度テスト")
    print("4. 速度比較テスト")
    print("5. 包括的テスト（速度とモーター出力の全組み合わせ）")
    print("6. 全パターンテスト（モーター出力別 + 包括的テスト）")
    print("0. 終了")
    print("=" * 40)
    
    while True:
        try:
            choice = input("実行したいテストの番号を入力してください (0-6): ")
            
            if choice == "0":
                print("プログラムを終了します。")
                break
            elif choice == "1":
                print("\n=== 全角度精度測定テスト開始 ===")
                motor_power = int(input("モーター出力を入力してください (50-150): "))
                run_experiment(straight_speed_percent=40, turn_speed_percent=30, motor_power_percent=motor_power)
            elif choice == "2":
                print("\n=== 単一角度テスト開始 ===")
                motor_power = int(input("モーター出力を入力してください (50-150): "))
                target_angle = int(input("目標角度を入力してください (度): "))
                run_single_test(straight_speed_percent=40, turn_speed_percent=30, motor_power_percent=motor_power, target_angle=target_angle)
            elif choice == "3":
                print("\n=== 繰り返し精度テスト開始 ===")
                motor_power = int(input("モーター出力を入力してください (50-150): "))
                target_angle = int(input("目標角度を入力してください (度): "))
                repeat_count = int(input("繰り返し回数を入力してください: "))
                run_repeat_test(straight_speed_percent=40, turn_speed_percent=30, motor_power_percent=motor_power, target_angle=target_angle, repeat_count=repeat_count)
            elif choice == "4":
                print("\n=== 速度比較テスト開始 ===")
                motor_power = int(input("モーター出力を入力してください (50-150): "))
                target_angle = int(input("目標角度を入力してください (度): "))
                run_speed_comparison_test(target_angle=target_angle, motor_power_percent=motor_power)
            elif choice == "5":
                print("\n=== 包括的テスト開始 ===")
                target_angle = int(input("目標角度を入力してください (度): "))
                run_comprehensive_test(target_angle=target_angle)
            elif choice == "6":
                print("\n=== 全パターンテスト開始 ===")
                print("モーター出力パターン: 50%, 75%, 100%, 125%, 150%")
                print("=" * 40)
                
                # テストするモーター出力設定
                motor_power_settings = [50, 75, 100, 125, 150]
                
                for motor_power in motor_power_settings:
                    print(f"\n" + "="*60)
                    print(f"モーター出力 {motor_power}% でのテスト開始")
                    print("="*60)
                    
                    # 1. 全角度精度測定テスト
                    print(f"\n--- モーター出力 {motor_power}%: 全角度精度測定テスト ---")
                    run_experiment(straight_speed_percent=40, turn_speed_percent=30, motor_power_percent=motor_power)
                    
                    # 2. 単一角度テスト
                    print(f"\n--- モーター出力 {motor_power}%: 単一角度テスト ---")
                    run_single_test(straight_speed_percent=40, turn_speed_percent=30, motor_power_percent=motor_power, target_angle=90)
                    
                    # 3. 繰り返し精度テスト
                    print(f"\n--- モーター出力 {motor_power}%: 繰り返し精度テスト ---")
                    run_repeat_test(straight_speed_percent=40, turn_speed_percent=30, motor_power_percent=motor_power, target_angle=90, repeat_count=5)
                    
                    # 4. 速度比較テスト
                    print(f"\n--- モーター出力 {motor_power}%: 速度比較テスト ---")
                    run_speed_comparison_test(target_angle=90, motor_power_percent=motor_power)
                    
                    print(f"\nモーター出力 {motor_power}% のテスト完了")
                    print("次のモーター出力設定に進みます...")
                    wait(2000)  # 次のテストの前に少し待機
                
                # 5. 包括的テスト（速度とモーター出力の全組み合わせ）
                print(f"\n" + "="*60)
                print("包括的テスト開始（速度とモーター出力の全組み合わせ）")
                print("="*60)
                run_comprehensive_test(target_angle=90)
                
                print("\n" + "="*60)
                print("全モーター出力パターンのテスト完了！")
                print("="*60)
            else:
                print("無効な選択です。0-6の数字を入力してください。")
            
            print("\n" + "="*40)
            print("メニューに戻ります...")
            print("="*40)
            
        except ValueError:
            print("数値を入力してください。")
        except KeyboardInterrupt:
            print("\nプログラムを終了します。")
            break 