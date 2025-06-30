from pybricks.hubs import PrimeHub
from pybricks.parameters import Port, Axis, Direction, Stop
from pybricks.pupdevices import Motor
from pybricks.robotics import DriveBase
from pybricks.tools import wait, multitask, run_task

hub = PrimeHub(top_side=Axis.Z,
               front_side=Axis.X)

left  = Motor(Port.F, positive_direction=Direction.COUNTERCLOCKWISE)
right = Motor(Port.B, positive_direction=Direction.CLOCKWISE)

lift = Motor(Port.A,positive_direction=Direction.CLOCKWISE)

robot = DriveBase(left, right, wheel_diameter=56, axle_track=115)


FIRST_STRAIGHT_DISTANCE_MM = 260
TURN_ANGLE_REG = -45
TO_TOWER_DISTANCE_MM = 670
LIFT_ARM_TURN_ANGLE = 500
LIFT_ARM_TURN_SPEED = 180


DISTANCE_KP = 1000
DISTANCE_KI = 50
DISTANCE_KD = 10

HEADING_KP = 2000
HEADING_KI = 50
HEADING_KD = 100


robot.distance_control.pid(
    kp=DISTANCE_KP,
    ki=HEADING_KI,
    kd=HEADING_KD
)


robot.use_gyro(True)
hub.imu.reset_heading(0)
robot.reset()
lift.reset_angle(0)



async def sensor_logger_task():

    while True:
        heading = hub.imu.heading()
        left_deg = left.angle()
        right_deg = right.angle()
        dist = robot.distance()
        print(f"LOG:dist={dist:4.0f} mm headimg={heading:4.0f}゜ L={left_deg:5.0f}゜ R={right_deg:5.0f}°")
        await wait(1000)
async def main_robot_sequence_task():
    print("start GO forward")
    await robot.straight(FIRST_STRAIGHT_DISTANCE_MM)
    print("Stop")

    await wait(1000)

    print("Start GO To Mission tower")
    await robot.straight(100)
    print("Stop")
#曲がるところ
    await wait(1000)
    await robot.turn(-48)
    print("Start Lefting tower")
    await robot.straight(640)
    await lift.run_target(LIFT_ARM_TURN_SPEED,LIFT_ARM_TURN_ANGLE)

    await wait(1000)
    
    print("Return")
    await lift.run_target(LIFT_ARM_TURN_SPEED,LIFT_ARM_TURN_ANGLE)
    print("Mission Complete")

    robot.stop()


run_task(multitask(
    sensor_logger_task(),
    main_robot_sequence_task()
))

    