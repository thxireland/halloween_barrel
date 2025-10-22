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


current_dir = os.path.dirname(os.path.abspath(__file__))
vomit_1 = MP3Player(f"{current_dir}/music_files/vomit_1_sec.mp3")
vomit_2 = MP3Player(f"{current_dir}/music_files/vomit_2_sec.mp3")
vomit_4 = MP3Player(f"{current_dir}/music_files/vomit_4_sec.mp3")

lights = GoveeLight("192.168.1.212")

config_file = yaml.safe_load(open(f"{current_dir}/configs.yaml"))
hardware_config = config_file['hardware']
motor_pins = hardware_config['motor_pins']
pump_relay_pin = hardware_config['pump_relay_pin']
smoke_relay_pin = hardware_config['smoke_relay_pin']
ultrasonic_pins = hardware_config['ultrasonic_pins']
govee_light_config = hardware_config['govee_light']

distances = config_file['distance_thresholds']
warning_distance = distances['warning']
trigger_distance = distances['trigger']

light = GoveeLight(govee_light_config['ip_address'])
motor = Motor(motor_pins['forward'], motor_pins['reverse'])
pump_relay = Relay(pump_relay_pin)
smoke_relay = Relay(smoke_relay_pin)
ultrasonic = UltrasonicSensor(ultrasonic_pins['trigger'], ultrasonic_pins['echo'])

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HalloweenBarrel")

def setup_hardware():
    light.set_color(100, 100, 0)
    motor.move_forward(4)
    motor.move_reverse(2.5)
    pump_relay.on()
    smoke_relay.on()
    time.sleep(1)
    pump_relay.off()
    smoke_relay.off()
    motor.stop()

def main():
    """Main entry point."""
    setup_hardware()
    while True:
        distance = ultrasonic.read_distance()
        if not distance:
            continue
        time.sleep(1)
        if distance < warning_distance:
            logger.info(f"Distance: {distance} cm")
            logger.info("Warning: Object is approaching")
        if distance < trigger_distance:
            logger.info(f"Distance: {distance} cm")
            logger.info("Trigger: Object is close")
            motor.move_formward(4)
            logger.info("Moving forward")
            pump_relay.on()
            logger.info("Pump relay on")
            light.set_color(0, 255, 0)
            light.flash(15)
            logger.info("Setting light to green")
            time.sleep(.5)
            vomit_1.play()
            logger.info("Playing vomit 1")
            smoke_relay.on()
            time.sleep(1)
            smoke_relay.off()
            logger.info("Smoke relay off")
            vomit_2.play()
            time.sleep(2)
            light.set_color(255, 0, 0)
            logger.info("Setting light to red")
            vomit_4.play()
            logger.info("Playing vomit 4")
            motor.stop()
            time.sleep(4)
            pump_relay.off()
            logger.info("Pump relay off")
            time.sleep(.5)
            motor.move_reverse(2.5)
            logger.info("Moving reverse")
            time.sleep(1)
            light.set_color(100, 100, 0)
            logger.info("Setting light to yellow")
            time.sleep(5)

if __name__ == "__main__":
    sys.exit(main())

