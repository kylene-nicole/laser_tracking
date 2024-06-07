from gpiozero import Servo, OutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory
import logging
import json
import paho.mqtt.client as mqtt
import math
import time
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])

factory = PiGPIOFactory()

laser = OutputDevice(17, pin_factory=factory)
pan_servo = Servo(18, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
tilt_servo = Servo(23, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)

mqtt_broker = ""
mqtt_topic = "laser/system"
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker")
        client.subscribe(mqtt_topic)
    else:
        logging.error(f"Failed to connect with result code {rc}")

def on_message(client, userdata, msg):
    logging.info(f"Received message: {msg.payload}")
    try:
        data = json.loads(msg.payload.decode('utf-8'))
        set_servo_angle(pan_servo, data['pan'])
        set_servo_angle(tilt_servo, data['tilt'])
        set_laser(data['laser'])
    except (json.JSONDecodeError, KeyError) as e:
        logging.error(f"Error processing message: {e}")

def set_laser(state):
    if state == "on":
        laser.on()
        logging.info("Laser is on")
    elif state == "off":
        laser.off()
        logging.info("Laser is off")
    else:
        logging.error("Invalid laser state")

def set_servo_angle(servo, angle):
    servo.value = convert_pwm(angle)
    logging.info(f"Set {servo} angle to {angle}°")

def convert_pwm(angle):
    return math.sin(math.radians(angle))

def set_servo_default():
    set_servo_angle(pan_servo, 50)
    set_servo_angle(tilt_servo, 10)

def main():
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(mqtt_broker, 1883, 60)
        client.loop_forever()
    except Exception as e:
        logging.error(f"Failed to connect to MQTT broker: {e}")
        sys.exit(1)

    set_servo_default()    

    # laser.on()
    
    # i = 25
    # while i <= 90:
    #     set_servo_angle(pan_servo, i)
    #     time.sleep(1)
    #     i += 5

    # set_servo_default()    

    # y = -5
    # while y <= 25:
    #     set_servo_angle(tilt_servo, y)
    #     time.sleep(1)
    #     y += 5

    # set_servo_default()

    laser.off()

if __name__ == '__main__':
    main()