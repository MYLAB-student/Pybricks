# FLLロボット制御プログラム
# このプログラムはLEGO SPIKE Primeハブを使用してロボットを制御します

# 必要なライブラリをインポート
from pybricks.hubs import PrimeHub  # SPIKE Primeハブの制御用
from pybricks.parameters import Port, Direction  # ポート番号と回転方向の定義
from pybricks.pupdevices import Motor  # モーター制御用
from pybricks.robotics import DriveBase  # ロボットの移動制御用
from pybricks.tools import wait  # 待機時間制御用

def setup_robot():
    """
    ロボットの初期設定を行う関数
    ハブ、モーター、DriveBaseの初期化を実行
    """
    # ハードウェアの初期化
    hub = PrimeHub()  # SPIKE Primeハブの初期化
    
    # 左右のモーターを設定
    left_motor = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)  # 左側のモーター（反時計回りを正方向に設定）
    right_motor = Motor(Port.B, positive_direction=Direction.CLOCKWISE)  # 右側のモーター（時計回りを正方向に設定）
    
    # DriveBaseオブジェクトを作成（タイヤ直径: 56mm、軸間距離: 115mm）
    robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=115)
    
    return robot

# ===== メイン処理 =====
# ロボットの初期設定を実行
robot = setup_robot()

# ===== ロボットの動作シーケンス =====

# 1. 前方への移動
print("500mm 前に進みます．．．")
robot.straight(500)  # 500mm前方に直進
wait(1000)  # 1秒間待機（動作完了を確認）

# 2. 後方への移動
print("500mm 後ろに進みます．．．")
robot.straight(-500)  # -500mm（後方）に直進
wait(1000)  # 1秒間待機

# 3. 右旋回（360度回転）
print("右に90度曲がります．．．")
robot.turn(-360)  # -360度（右旋回）で1回転
wait(1000)  # 1秒間待機

# 4. 左旋回（90度回転）
print("左に90度曲がります")
robot.turn(-90)  # -90度（左旋回）
wait(1000)  # 1秒間待機

# 5. ロボットの停止
print("ロボットを停止します。")
robot.stop()  # モーターを停止

# プログラム完了の通知
print("すべての動きが完了しました")


