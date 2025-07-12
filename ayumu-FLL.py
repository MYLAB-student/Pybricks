from pybricks.hubs import PrimeHub 
from pybricks.parameters import Port, Direction
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait

hub = PrimeHub()

left_motor = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
right_motor = Motor(Port.B, positive_direction=Direction.CLOCKWISE)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=115)




print("500mm 前に進みます．．．")
robot.straight(500)
wait(1000) # 1秒待機

print("500mm 後ろに進みます．．．")
robot.straight(-500)
wait(1000) # 1秒待機

print("右に90度曲がります．．．")
robot.turn(-360)
wait(1000) # 1秒待機

print("左に90度曲がります")
robot.turn(-90)
wait(1000) # 1秒待機

print("ロボットを停止します。")
robot.stop()

print("すべての動きが完了しました")


