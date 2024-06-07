import paho.mqtt.client as mqtt
import json
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo, OutputDevice
import time
import math
import logging
import sys

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])

# GPIO setup
factory = PiGPIOFactory()
pan_pin = 18
tilt_pin = 23
laser_pin = 17

pan_servo = Servo(pan_pin, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
tilt_servo = Servo(tilt_pin, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000, pin_factory=factory)
laser = OutputDevice(laser_pin)

# MQTT setup
mqtt_broker = ""
mqtt_topic = "laser_turret/angles"
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
        set_angles(data['pan'], data['tilt'])
    except (json.JSONDecodeError, KeyError) as e:
        logging.error(f"Error processing message: {e}")

def angle_to_pwm_convert(angle):
    return (angle / 180.0) * 2000 + 500

def set_angles(pan_angle, tilt_angle):
    pan_pulse = angle_to_pwm_convert(pan_angle)
    tilt_pulse = angle_to_pwm_convert(tilt_angle)
    pan_servo.value = (pan_pulse - 1500) / 1000.0
    tilt_servo.value = (tilt_pulse - 1500) / 1000.0
    logging.info(f"Set pan angle to {pan_angle}° ({pan_pulse} PWM) and tilt angle to {tilt_angle}° ({tilt_pulse} PWM)")

def setup_default_angles():
    set_angles(0, 90)

def main():
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(mqtt_broker, 1883, 60)
        client.loop_forever()
    except Exception as e:
        logging.error(f"Failed to connect to MQTT broker: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_default_angles()
    main()
