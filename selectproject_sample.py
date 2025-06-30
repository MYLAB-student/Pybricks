# -*- coding: utf-8 -*-
from pybricks.hubs import PrimeHub
from pybricks.parameters import Button
from pybricks.tools import wait

# Spike Prime本体のインスタンス形成
# 必要なら引数を与える
hub = PrimeHub()

# プロジェクトの識別名
projects = ["A", "B", "C"]
# プロジェクト選択インデックス
index = 0

# 画面の更新
def screenUpdate(index):
    hub.display.clear()
    hub.display.text("SELECT:")
    wait(500)  # 表示切り替えのため少し待つ
    hub.display.text(projects[index])

# 各プロジェクトの関数定義
def A():
    hub.display.clear()
    hub.display.text("Running A")
    wait(1000)  # デモ用に1秒待機

def B():
    hub.display.clear()
    hub.display.text("Running B")
    wait(1000)

def C():
    hub.display.clear()
    hub.display.text("Running C")
    wait(1000)

# プロジェクト実行
def projectExecute(index):
    if projects[index] == "A":
        A()
    elif projects[index] == "B":
        B()
    elif projects[index] == "C":
        C()
    #もし追加する場合
    # elif projects[index] == "D":
    #    D()
    #...

# 初期画面表示
screenUpdate(index)

# メインループ
while True:
    #　ボタン入力を検出
    buttons = hub.buttons.pressed()

    if Button.LEFT in buttons:
        index = (index - 1) % len(projects)
        screenUpdate(index)
        wait(300)

    elif Button.RIGHT in buttons:
        index = (index + 1) % len(projects)
        screenUpdate(index)
        wait(300)

    elif Button.CENTER in buttons:
        projectExecute(index)
        screenUpdate(index)  # 終了後に選択画面に戻す
        wait(300)

    wait(50)
