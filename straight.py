from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis, Direction
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# --- 初期設定関数 ---
def setup_hub():
    return PrimeHub(top_side=Axis.Z, front_side=Axis.X)

def setup_motors():
    left = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
    right = Motor(Port.B, positive_direction=Direction.CLOCKWISE)
    return left, right

def setup_robot_parameters(left, right, straight_speed_percent=40, motor_power_percent=100):
    straight_spd = 500 * (straight_speed_percent / 100)
    robot = DriveBase(
        left,
        right,
        wheel_diameter=56,
        axle_track=115
    )
    robot.settings(
        straight_speed=straight_spd,
        turn_rate=100
    )
    motor_power = motor_power_percent / 100.0
    left.dc(motor_power)
    right.dc(motor_power)
    return robot

def initialize_robot(straight_speed_percent=40, motor_power_percent=100):
    hub = setup_hub()
    left, right = setup_motors()
    robot = setup_robot_parameters(left, right, straight_speed_percent, motor_power_percent)
    robot.use_gyro(True)
    hub.imu.reset_heading(0)
    robot.reset()
    return hub, left, right, robot

# --- 実験条件 ---
power_list = [40, 50, 60, 70, 80, 90, 100]
distance_list = [d for d in range(20, 201, 20)]  # 20, 40, ..., 200
repeat_num = 3

hub, left, right, robot = initialize_robot()

all_results = []

for power in power_list:
    left.dc(power / 100)
    right.dc(power / 100)
    distance_results = []
    for distance in distance_list:
        errors = []
        abs_errors = []
        for trial in range(1, repeat_num + 1):
            print(f"\n--- [出力{power}% 距離{distance}mm] 実験{trial}/{repeat_num} ---")
            robot.reset()
            robot.straight(distance)
            wait(1000)
            actual_distance = robot.distance()
            error = actual_distance - distance
            errors.append(error)
            abs_errors.append(abs(error))
            sign = "+" if error >= 0 else "-"
            print(f"→ 実際の距離: {actual_distance:.1f}mm")
            print(f"→ 誤差: {sign}{abs(error):.1f}mm")
            print("→ {0}mm後退して元の位置に戻ります...".format(distance))
            robot.straight(-distance)
            wait(500)
            print("-------------------------------")
            robot.stop()
            wait(200)
        mean_error = sum(errors) / repeat_num
        mean_abs_error = sum(abs_errors) / repeat_num
        distance_results.append((distance, mean_error, mean_abs_error, repeat_num))
    all_results.append((power, distance_results))

# 結果を罫線付き表形式で出力
for power, distance_results in all_results:
    print(f"\n=== モーター出力: {power}% の結果 ===")
    print("+------------+----------------+-------------------+------------+")
    print("| 指定距離[mm] | 平均誤差[mm]   | 平均絶対誤差[mm]   | 実験回数   |")
    print("+------------+----------------+-------------------+------------+")
    for distance, mean_error, mean_abs_error, repeat_num in distance_results:
        sign = "+" if mean_error >= 0 else "-"
        print(f"| {distance:>10} |   {sign}{abs(mean_error):>8.2f}   |      {mean_abs_error:>8.2f}      | {repeat_num:>6}    |")
    print("+------------+----------------+-------------------+------------+")
