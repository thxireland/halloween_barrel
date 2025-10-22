import logging
import time
import sys
import yaml
import os
from plugins.motor import Motor
from plugins.ultrasonic import UltrasonicSensor
from plugins.relay import Relay
from plugins.govee_plugin import GoveeLight
from plugins.music_player import MP3Player

light = GoveeLight("192.168.1.212")

light.set_color(255,0,0)