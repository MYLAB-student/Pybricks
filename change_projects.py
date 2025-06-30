from pybricks.hubs import PrimeHub
from pybricks.pupdevices import Motor, ColorSensor, UltrasonicSensor, ForceSensor
from pybricks.parameters import Button, Color, Direction, Port, Side, Stop, Icon, Axis
from pybricks.robotics import DriveBase
from pybricks.tools import wait, StopWatch

# Spike Prime本体のインスタンス形成
hub = PrimeHub()

# タッチセンサー（フォースセンサー）の設定
# ポートを必要に応じて変更してください（Port.A, Port.B, Port.C, Port.D, Port.E, Port.F）
touch_sensor = ForceSensor(Port.D)

# プロジェクトの識別名
projects = ["A", "B", "C"]

icon_map = {
    "A": Icon.HAPPY,
    "B": Icon.HEART,
    "C": Icon.SAD
}

# 各プロジェクトの関数定義
def A():
    print("=== Project A 実行中 ===")
    hub.display.icon(Icon.TRIANGLE_UP)
    wait(1000)
    print("Project A 完了\n")

def B():
    print("=== Project B 実行中 ===")
    hub.display.icon(Icon.TRIANGLE_LEFT)
    wait(1000)
    print("Project B 完了\n")

def C():
    print("=== Project C 実行中 ===")
    hub.display.icon(Icon.TRIANGLE_RIGHT)
    wait(1000)
    print("Project C 完了\n")

def show_current_selection(index):
    """現在の選択項目を表示"""
    if index < len(projects):
        project_name = projects[index]
        print(f"選択中: Project {project_name}")
        hub.display.icon(icon_map[project_name])
    else:
        print("選択中: プログラム終了")
        hub.display.icon(Icon.FALSE)

def projectExecute(index):
    if index == 0:
        A()
    elif index == 1:
        B()
    elif index == 2:
        C()

def wait_for_button_release():
    """ボタンが離されるまで待機"""
    while hub.buttons.pressed():
        wait(10)

def wait_for_touch_release():
    """タッチセンサーが離されるまで待機"""
    while touch_sensor.pressed():
        wait(10)

# メイン処理
def main():
    print("左右ボタンで選択、タッチセンサーで決定してください")
    print("操作方法:")
    print("- 左ボタン: 前の項目")
    print("- 右ボタン: 次の項目")
    print("- タッチセンサー(Port.A): 決定")
    print("- Bluetoothボタン: 緊急終了")
    
    current_index = 0  # 現在の選択インデックス (0=A, 1=B, 2=C, 3=終了)
    max_index = len(projects)  # 0-3 (A,B,C,終了)
    
    # 初期表示
    show_current_selection(current_index)
    
    while True:
        pressed_buttons = hub.buttons.pressed()
        
        # 左ボタンが押された場合（前の項目へ）
        if Button.LEFT in pressed_buttons:
            wait_for_button_release()  # ボタンが離されるまで待機
            current_index = (current_index - 1) % (max_index + 1)
            show_current_selection(current_index)
            wait(200)  # デバウンス
            
        # 右ボタンが押された場合（次の項目へ）
        elif Button.RIGHT in pressed_buttons:
            wait_for_button_release()  # ボタンが離されるまで待機
            current_index = (current_index + 1) % (max_index + 1)
            show_current_selection(current_index)
            wait(200)  # デバウンス
            
        # タッチセンサーが押された場合（決定）
        elif touch_sensor.pressed():
            wait_for_touch_release()  # タッチセンサーが離されるまで待機
            
            if current_index == max_index:  # 終了が選択された場合
                print("プログラムを終了します")
                hub.display.icon(Icon.HEART)
                wait(1000)
                break
            else:
                project_name = projects[current_index]
                print(f"\nProject {project_name} を実行します...")
                wait(100)
                
                # プロジェクト実行
                projectExecute(current_index)
                
                # 実行後の確認
                print(f"Project {project_name} が完了しました")
                print("左右ボタンで選択、タッチセンサーで決定してください")
                
                # 選択画面に戻る
                show_current_selection(current_index)
                wait(1000)
        
        # Bluetoothボタンが押された場合（緊急終了）
        elif Button.BLUETOOTH in pressed_buttons:
            wait_for_button_release()
            print("緊急終了します")
            hub.display.icon(Icon.FALSE)
            break
            
        wait(50)  # CPUへの負荷を軽減

# プログラム実行
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        hub.display.icon(Icon.FALSE)