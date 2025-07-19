from setup import initialize_robot
from pybricks.tools import wait

# モーター出力リスト（15%ずつ）
power_list = [40, 55, 70, 85, 100]
# 調べる角度リスト
angles = [30, 60, 90, 120, 180]
# 各条件での実験回数
repeat_num = 3

# 最初に一度だけ初期化
hub, left, right, robot = initialize_robot(
    straight_speed_percent=40,  # 直進速度
    turn_speed_percent=30,     # 旋回速度
    motor_power_percent=100    # 仮の値（後でdcで上書き）
)

all_results = []  # 全ての結果を記録

for power in power_list:
    print(f"\n==============================")
    print(f"モーター出力: {power}% で実験開始")
    print(f"==============================")
    # 出力を設定
    left.dc(power / 100)
    right.dc(power / 100)
    angle_results = []
    for angle in angles:
        errors = []
        abs_errors = []
        for trial in range(1, repeat_num + 1):
            print(f"\n--- [出力{power}% 角度{angle}度] 実験{trial}/{repeat_num} ---")
            robot.turn(angle)
            wait(1000)
            current_heading = hub.imu.heading()
            error = current_heading - angle
            errors.append(error)
            abs_errors.append(abs(error))
            sign = "+" if error >= 0 else "-"
            print(f"→ 実際の向き: {current_heading:.1f}度")
            print(f"→ 誤差: {sign}{abs(error):.1f}度")
            print("-------------------------------")
            robot.stop()
            wait(200)
            hub.imu.reset_heading(0)
            wait(500)
        # 平均誤差計算
        mean_error = sum(errors) / repeat_num
        mean_abs_error = sum(abs_errors) / repeat_num
        angle_results.append((angle, mean_error, mean_abs_error, repeat_num))
    all_results.append((power, angle_results))

# 結果を罫線付き表形式で出力
for power, angle_results in all_results:
    print(f"\n=== モーター出力: {power}% の結果 ===")
    print("+------------+----------------+-------------------+------------+")
    print("| 指定角度[度] | 平均誤差[度]   | 平均絶対誤差[度]   | 実験回数   |")
    print("+------------+----------------+-------------------+------------+")
    for angle, mean_error, mean_abs_error, repeat_num in angle_results:
        sign = "+" if mean_error >= 0 else "-"
        print(f"| {angle:>10} |   {sign}{abs(mean_error):>8.2f}   |      {mean_abs_error:>8.2f}      | {repeat_num:>6}    |")
    print("+------------+----------------+-------------------+------------+")
