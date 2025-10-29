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

# Initialize hardware
light = GoveeLight(govee_light_config['ip_address'])
motor = Motor(motor_pins['forward'], motor_pins['reverse'])
pump_relay = Relay(pump_relay_pin)
smoke_relay = Relay(smoke_relay_pin)
ultrasonic = UltrasonicSensor(ultrasonic_pins['trigger'], ultrasonic_pins['echo'])

# Initialize music players
music_files = {
    'vomit_1_sec.mp3': MP3Player(f"{current_dir}/music_files/vomit_1_sec.mp3"),
    'vomit_2_sec.mp3': MP3Player(f"{current_dir}/music_files/vomit_2_sec.mp3"),
    'vomit_4_sec.mp3': MP3Player(f"{current_dir}/music_files/vomit_4_sec.mp3")
}

# Relay mapping
relays = {
    'pump': pump_relay,
    'smoke': smoke_relay
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("HalloweenBarrel")

def execute_sequence(sequence_config):
    """
    Execute a sequence of actions from YAML configuration.
    
    Args:
        sequence_config: List of action dictionaries from YAML config
    """
    for action in sequence_config:
        action_type = action.get('type')
        
        try:
            if action_type == 'motor':
                motor_action = action.get('action')
                if motor_action == 'forward':
                    duration = action.get('duration', 2.0)
                    logger.info(f"Moving forward for {duration} seconds")
                    motor.move_forward(duration)
                elif motor_action == 'reverse':
                    duration = action.get('duration', 2.0)
                    logger.info(f"Moving reverse for {duration} seconds")
                    motor.move_reverse(duration)
                elif motor_action == 'stop':
                    logger.info("Stopping motor")
                    motor.stop()
            elif action_type == 'relay':
                relay_name = action.get('name')
                relay_action = action.get('action')
                relay = relays.get(relay_name)
                if not relay:
                    logger.error(f"Unknown relay name: {relay_name}")
                    continue
                if relay_action == 'on':
                    logger.info(f"Turning {relay_name} relay ON")
                    relay.on()
                elif relay_action == 'off':
                    logger.info(f"Turning {relay_name} relay OFF")
                    relay.off()
            elif action_type == 'light':
                light_action = action.get('action')
                if light_action == 'set_color':
                    r = action.get('colour', {}).get('r', 0)
                    g = action.get('colour', {}).get('g', 0)
                    b = action.get('colour', {}).get('b', 0)
                    logger.info(f"Setting light color to RGB({r}, {g}, {b})")
                    light.set_color(r, g, b)
                elif light_action == 'flash':
                    amount = action.get('amount', 10)
                    logger.info(f"Flashing light {amount} times")
                    light.flash(amount)
                    
            elif action_type == 'music':
                file_name = action.get('file')
                music_action = action.get('action')
                
                if music_action == 'play':
                    player = music_files.get(file_name)
                    if not player:
                        logger.error(f"Unknown music file: {file_name}")
                        continue
                    logger.info(f"Playing music: {file_name}")
                    player.play()
                    
            elif action_type == 'sleep':
                duration = action.get('duration', 1.0)
                logger.debug(f"Sleeping for {duration} seconds")
                time.sleep(duration)
                
            else:
                logger.warning(f"Unknown action type: {action_type}")
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            continue

def setup_hardware():
    """Setup hardware using sequence from YAML configuration."""
    setup_sequence_config = config_file.get('setup_sequence', [])
    logger.info("Running hardware setup sequence")
    execute_sequence(setup_sequence_config)

def main():
    """Main entry point."""
    setup_hardware()
    
    # Load sequence from config
    sequence_config = config_file.get('sequence', [])
    
    while True:
        distance = ultrasonic.read_distance()
        if not distance:
            continue
        if distance < warning_distance:
            logger.info(f"Distance: {distance} cm")
            logger.info("Warning: Object is approaching")
        if distance < trigger_distance:
            logger.info(f"Distance: {distance} cm")
            logger.info("Trigger: Object is close")
            execute_sequence(sequence_config)

if __name__ == "__main__":
    sys.exit(main())

