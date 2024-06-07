#!/bin/bash
sudo pigpiod
sudo systemctl start mosquitto
/usr/bin/python /path/to/your/my_script.py
