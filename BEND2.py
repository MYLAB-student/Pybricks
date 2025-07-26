# 曲がる角度30度で出力を変えて精度を試すプログラム（Gemini-2.5-pro）
# このプログラムは、ロボットが30度曲がる際の精度を、様々なモーター出力で検証します
# 各出力設定で複数回実験を行い、平均誤差を算出して最適な出力設定を特定します

from setup import initialize_robot  # ロボット初期化関数をインポート
from pybricks.tools import wait     # 待機時間制御用

# ===== 実験パラメータの設定 =====
# モーター出力リスト（10%〜100%）
# 低出力から高出力まで段階的にテストして、精度への影響を調査
power_list = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

# 試す角度は60度のみ
# 60度は一般的な曲がり角で、精度が重要
angle = 60

# 各条件での実験回数
# 統計的な信頼性を確保するため、複数回実験
repeat_num = 3

# ===== ロボットの初期化 =====
# 最初に一度だけ初期化
# ハブ、モーター、DriveBase、センサーを設定
hub, left, right, robot = initialize_robot(
    straight_speed_percent=40,  # 直進速度（40%に設定）
    turn_speed_percent=30,     # 旋回速度（30%に設定）
    motor_power_percent=100    # 仮の値（後でdcで上書き）
)

# ===== 実験結果を格納するリスト =====
all_results = []  # 全ての結果を記録するリスト

# ===== 各出力設定での実験ループ =====
for power in power_list:
    print(f"\n==============================")
    print(f"モーター出力: {power}% で実験開始")
    print(f"==============================")
    
    # 出力を設定
    # robot.settings()で旋回速度を設定（left.dc()とright.dc()の代わり）
    # power/100で0.0〜1.0の範囲に正規化し、旋回速度として設定
    # 最大旋回速度500deg/sに対する割合として設定
    turn_rate = 500 * (power / 100)  # deg/s単位
    robot.settings(turn_rate=turn_rate)
    
    # この出力設定での誤差を記録するリスト
    errors = []      # 符号付き誤差（正負の値）
    abs_errors = []  # 絶対誤差（常に正の値）
    
    # ===== 各実験回数のループ =====
    for trial in range(1, repeat_num + 1):
        print(f"\n--- [出力{power}% 角度{angle}度] 実験{trial}/{repeat_num} ---")
        
        # ロボットを指定角度だけ回転させる
        robot.turn(angle)
        
        # 回転完了を待つ（1秒）
        wait(1000)
        
        # 現在の向きを取得（IMUセンサーから）
        current_heading = hub.imu.heading()
        
        # 誤差を計算
        # 正の値：目標より多く回転、負の値：目標より少なく回転
        error = current_heading - angle
        errors.append(error)
        abs_errors.append(abs(error))
        
        # 結果を表示
        sign = "+" if error >= 0 else "-"
        print(f"→ 実際の向き: {current_heading:.1f}度")
        print(f"→ 誤差: {sign}{abs(error):.1f}度")
        print("-------------------------------")
        
        # ロボットを停止
        robot.stop()
        wait(200)  # 停止を確実にするため少し待機
        
        # センサーをリセット（次の実験のため）
        hub.imu.reset_heading(0)
        wait(500)  # リセット完了を待つ
    
    # ===== この出力設定での統計計算 =====
    # 平均誤差計算（符号付き）
    mean_error = sum(errors) / repeat_num
    # 平均絶対誤差計算（精度の指標）
    mean_abs_error = sum(abs_errors) / repeat_num
    
    # 結果をリストに追加
    all_results.append((power, mean_error, mean_abs_error, repeat_num))

# ===== 結果の表示 =====
# 罫線付き表形式で結果を出力
print(f"\n=== 60度曲げ精度テスト結果（Gemini-2.5-pro） ===")
print("+------------+----------------+-------------------+------------+")
print("| 出力[%]    | 平均誤差[度]   | 平均絶対誤差[度]   | 実験回数   |")
print("+------------+----------------+-------------------+------------+")

# 各出力設定の結果を表形式で表示
for power, mean_error, mean_abs_error, repeat_num in all_results:
    # 符号を決定（正の誤差は+、負の誤差は-）
    sign = "+" if mean_error >= 0 else "-"
    # 表形式で出力（右寄せで整列）
    print(f"| {power:>10} |   {sign}{abs(mean_error):>8.2f}   |      {mean_abs_error:>8.2f}      | {repeat_num:>6}    |")

print("+------------+----------------+-------------------+------------+")

# ===== 結果の解釈 =====
# 平均絶対誤差が最も小さい出力設定が、最も精度が高い
# 平均誤差の符号で、系統的な過回転（+）か不足回転（-）かを判断可能
