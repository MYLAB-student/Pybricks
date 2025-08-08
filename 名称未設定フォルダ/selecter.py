from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis, Direction, Button, Color
from pybricks.pupdevices import Motor, ForceSensor
from pybricks.robotics import DriveBase
from pybricks.tools import wait, multitask, run_task
from setup import initialize_robot
import run

# ロボットの初期化
hub, left, right, robot = initialize_robot()

# プログラムリスト
programs = [
   
    {"name": "straight_with_power", "module": run, "description": "straight_with_power関数", "function": "straight_with_power", "params": [robot,100, 50]},
     {"name": "straight_with_power", "module": run, "description": "straight_with_power関数", "function": "straight_with_power", "params": [robot,100, 10]},
     {"name": "回転", "module": run, "description": "回転", "function": "turn_with_power", "params": [robot,hub,100, 10]},
    # 他のプログラムをここに追加
]

program_id = 0
max_programs = len(programs) - 1

# フォースセンサーの初期化
button = ForceSensor(Port.C)

print("=== プログラムセレクター ===")
print("LEFT/RIGHT: プログラム選択")
print("フォースセンサー: プログラム実行")

def reset_robot():
    """ロボットのリソースをリセット"""
    try:
        robot.stop()
        robot.reset()
        hub.imu.reset_heading(0)
        print("ロボットリソースをリセットしました")
    except Exception as e:
        print(f"リセットエラー: {e}")

while True:
    # 現在のプログラムIDを表示
    current_program = programs[program_id]
    hub.display.number(program_id)
    
    # プログラム名をターミナルに表示
    print(f"選択中: {program_id} - {current_program['name']} ({current_program['description']})")
    
    # ボタン入力の処理
    pressed_buttons = hub.buttons.pressed()
    
    if Button.RIGHT in pressed_buttons:
        program_id = (program_id + 1) % (max_programs + 1)
        hub.light.on(Color.GREEN)
        wait(100)
        hub.light.off()
        print(f"→ プログラム {program_id} に変更")
        
    elif Button.LEFT in pressed_buttons:
        program_id = (program_id - 1) if program_id > 0 else max_programs
        hub.light.on(Color.BLUE)
        wait(100)
        hub.light.off()
        print(f"← プログラム {program_id} に変更")
    
    # フォースセンサーでプログラム実行
    if button.force() >= 0.5:
        hub.light.on(Color.RED)
        print(f"=== プログラム {program_id} を実行中 ===")
        
        try:
            # 実行前にリソースをリセット
            reset_robot()
            wait(50)  # リセット後に少し待機
            
            # 選択されたプログラムを実行
            function_name = current_program['function']
            function = getattr(current_program['module'], function_name)
            
            # パラメータがある場合は渡す
            if 'params' in current_program:
                function(*current_program['params'])
            else:
                function()
                
            print(f"=== プログラム {program_id} 実行完了 ===")
            
        except Exception as e:
            print(f"エラー: {e}")
            hub.light.on(Color.RED)
            wait(500)
            hub.light.off()
        finally:
            # 実行後にリソースをリセット
            try:
                reset_robot()
                wait(50)  # リセット後に少し待機
            except Exception as e:
                print(f"リセットエラー: {e}")
        
        hub.light.off()
        print("セレクターに戻りました")
    
    wait(50)  # ボタン連打防止のため少し待つ
