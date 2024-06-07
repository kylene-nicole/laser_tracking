from gpiozero import Servo, OutputDevice
import gpiozero.pins.pigpio import PiGPIOFactory
import math
import time

factory = PiGPIOFactory()

laser = OutputDevice(17, pin_factory=factory)
pan_servo = Servo(18, pin_factory=factory)
tilt_servo = Servo(23, pin_factory=factory)

def set_servo_angle(servo, angle):
    servo.value = convert_pwm(angle)

def convert_pwm(angle):
    return math.sin(math.radians(angle)) / 2 + 0.5

def set_servo_default():
    set_servo_angle(pan_servo, 50)
    set_servo_angle(tilt_servo, 10)

def main():
    set_servo_default()    

    laser.on()
    
    for i in [25, 90]:
        set_servo_angle(pan_servo, i)
        time.sleep(1)

    for y in [-5, 25]:
        set_servo_angle(tilt_servo, y)
        time.sleep(1)

    set_servo_default()

    laser.off()

if __name__ == '__main__':
    main()