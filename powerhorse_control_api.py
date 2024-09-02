from fastapi import FastAPI
from powerhorse_arm_motor_control import Motor, LinkedMotors, Arrow
from powerhorse_track_motor_control import MotorControl
from PCA9685 import PCA9685
import time

Dir = [
    'forward',
    'backward',
]

pwm = PCA9685(0x40, debug=False)
pwm.setPWMFreq(50)

class MotorDriver():
    def __init__(self):
        self.PWMA = 0
        self.AIN1 = 1
        self.AIN2 = 2
        self.PWMB = 5
        self.BIN1 = 3
        self.BIN2 = 4

    def MotorRun(self, motor, index, speed):
        if speed > 100:
            return
        if(motor == 0):
            pwm.setDutycycle(self.PWMA, speed)
            if(index == Dir[0]):
                print ("1")
                pwm.setLevel(self.AIN1, 0)
                pwm.setLevel(self.AIN2, 1)
            else:
                print ("2")
                pwm.setLevel(self.AIN1, 1)
                pwm.setLevel(self.AIN2, 0)
        else:
            pwm.setDutycycle(self.PWMB, speed)
            if(index == Dir[0]):
                print ("3")
                pwm.setLevel(self.BIN1, 0)
                pwm.setLevel(self.BIN2, 1)
            else:
                print ("4")
                pwm.setLevel(self.BIN1, 1)
                pwm.setLevel(self.BIN2, 0)

    def MotorStop(self, motor):
        if (motor == 0):
            pwm.setDutycycle(self.PWMA, 0)
        else:
            pwm.setDutycycle(self.PWMB, 0)



class PowerHorse:
    def __init__(self):
        self.arm_motor_shoulder = Motor("MOTOR1",1)
        self.arm_motor_elbow = Motor("MOTOR2",1)
        self.arm_motor_wrist = Motor("MOTOR3",1)
        self.arm_motor_gripper = Motor("MOTOR4",1)
        self.arm_motors = {
            "shoulder": self.arm_motor_shoulder,
            "elbow": self.arm_motor_elbow,
            "wrist": self.arm_motor_wrist,
            "gripper": self.arm_motor_gripper
        }

        self.arm_all = LinkedMotors(self.arm_motor_shoulder, self.arm_motor_elbow, self.arm_motor_wrist, self.arm_motor_gripper)

        self.track_motors = MotorDriver()

        self.arm_arrow_shoulder = Arrow(1)
        self.arm_arrow_elbow = Arrow(2)
        self.arm_arrow_wrist = Arrow(3)
        self.arm_arrow_gripper = Arrow(4)
        self.arm_arrows = {
            "shoulder": self.arm_arrow_shoulder,
            "elbow": self.arm_arrow_elbow,
            "wrist": self.arm_arrow_wrist,
            "gripper": self.arm_arrow_gripper
        }

        self.light = False
        self.arm = {"shoulder": 0, "elbow": 0, "wrist": 0, "gripper": 0}
        self.camera_angle = 0
        self.tracks = {"throttle": 0, "differential": 0}

    def set_light(self, state: bool):
        self.light = state

    def set_tracks(self, throttle: float, differential: float):
        self.tracks["throttle"] = throttle
        self.tracks["differential"] = differential
        
        # Ensure throttle and differential are within the range of -100 to 100
        throttle = max(min(throttle, 100), -100)
        differential = max(min(differential, 100), -100)

        # Determine direction index based on the sign of the throttle
        direction_index = "forward" if throttle >= 0 else "backward"

        # Calculate motor speeds based on throttle and differential values
        abs_throttle = abs(throttle)
        if differential == 0:
            motor_left_speed = abs_throttle
            motor_right_speed = abs_throttle
        elif 0 < differential <= 50:
            motor_left_speed = abs_throttle * (1 - differential / 50)
            motor_right_speed = abs_throttle
        elif differential > 50:
            motor_left_speed = abs_throttle * ((differential - 50) / 50)
            motor_right_speed = abs_throttle
        elif -50 <= differential < 0:
            motor_left_speed = abs_throttle
            motor_right_speed = abs_throttle * (1 + differential / 50)
        else:  # differential < -50
            motor_left_speed = abs_throttle
            motor_right_speed = abs_throttle * ((-differential - 50) / 50)

        # Ensure motor speeds are within the range of 0 to 100
        motor_left_speed = max(min(motor_left_speed, 100), 0)
        motor_right_speed = max(min(motor_right_speed, 100), 0)

        self.track_motors.MotorRun(0, direction_index, motor_left_speed)
        self.track_motors.MotorRun(1, direction_index, motor_right_speed)

        return self.tracks

    
    def set_arm(self, joint: str, power: float):
        self.arm[joint] = power
        self.arm_arrows[joint].on()
        if power > 0:
            self.arm_motors[joint].forward(power)
        elif power < 0:
            self.arm_motors[joint].backward(power)
        else:
            self.arm_motors[joint].stop()

    def stop_arm(self, joint: str):
        self.arm[joint] = 0
        self.arm_arrows[joint].off()
        self.arm_motors[joint].set_power(0)


    def set_camera(self, angle: int):
        self.camera_angle = angle

app = FastAPI()
powerhorse = PowerHorse()

@app.get("/")
async def root():
    return {"message": "Powerhorse Control API"}

@app.get("/powerhorse/tracks")
async def get_tracks():
    return powerhorse.tracks

@app.put("/powerhorse/tracks/{throttle}/{differential}")
async def set_tracks(throttle: float, differential: float):
    powerhorse.set_tracks(throttle, differential)
    return {"throttle": throttle, "differential": differential}

@app.put("/powerhorse/tracks/throttle/{throttle}")
async def set_tracks_throttle(throttle: float):
    powerhorse.set_tracks(throttle, powerhorse.tracks["differential"])
    return {"throttle": throttle, "differential": powerhorse.tracks["differential"]}

@app.put("/powerhorse/tracks/differential/{differential}")
async def set_tracks_differential(differential: float):
    powerhorse.set_tracks(powerhorse.tracks["throttle"], differential)
    return {"throttle": powerhorse.tracks["throttle"], "differential": differential}

@app.put("/powerhorse/tracks/stop")
async def stop_tracks():
    powerhorse.set_tracks(0, 0)
    return {"throttle": 0, "differential": 0}

@app.get("/powerhorse/arm")
async def get_arm():
    return {"joints": powerhorse.arm}

@app.get("/powerhorse/arm/{joint}")
async def get_arm_joint(joint: str):
    return {"joint": joint, "power": powerhorse.arm[joint]}

@app.put("/powerhorse/arm/{joint}/{power}")
async def set_arm_joint(joint: str, power: float):
    powerhorse.set_arm(joint, power)
    return {"joint": joint, "power": power}

@app.put("/powerhorse/arm/stop")
async def stop_arm():
    powerhorse.set_arm("shoulder", 0)
    powerhorse.set_arm("elbow", 0)
    powerhorse.set_arm("wrist", 0)
    powerhorse.set_arm("gripper", 0)
    return {"joints": powerhorse.arm}

@app.put("/powerhorse/arm/stop/{joint}")
async def stop_arm_joint(joint: str):
    powerhorse.set_arm(joint, 0)
    return {"joint": joint, "power": 0}

@app.get("/powerhorse/light")
async def get_light():
    return {"light": powerhorse.light}

@app.put("/powerhorse/light/on")
async def turn_light_on():
    powerhorse.set_light(True)
    return {"light": powerhorse.light}

@app.put("/powerhorse/light/off")
async def turn_light_off():
    powerhorse.set_light(False)
    return {"light": powerhorse.light}

@app.put("/powerhorse/light/toggle")
async def toggle_light():
    if powerhorse.light:
        powerhorse.set_light(False)
    else:
        powerhorse.set_light(True)
    return {"light": powerhorse.light}

@app.get("/powerhorse/camera")
async def get_camera():
    return {"camera": powerhorse.camera_angle}

@app.put("/powerhorse/camera/rotate/{angle}")
async def rotate_camera(angle: int):
    powerhorse.set_camera(angle)
    return {"camera": powerhorse.camera_angle}

@app.put("/powerhorse/camera/stop")
async def stop_camera():
    powerhorse.set_camera(0)
    return {"camera": powerhorse.camera_angle}

@app.put("/powerhorse/camera/home")
async def home_camera():
    powerhorse.set_camera(0)
    return {"camera": powerhorse.camera_angle}

@app.put("/powerhorse/stop")
async def emergency_stop():
    powerhorse.set_tracks(0, 0)
    powerhorse.set_arm("shoulder", 0)
    powerhorse.set_arm("elbow", 0)
    powerhorse.set_arm("wrist", 0)
    powerhorse.set_arm("gripper", 0)
    powerhorse.set_light(False)
    powerhorse.set_camera(0)
    return {"stop": True}
