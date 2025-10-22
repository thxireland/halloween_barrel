import logging
import time
import signal
import sys
import yaml
import os
from pathlib import Path
from typing import Optional, Dict, Any
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

def load_config(config_path: str = "configs.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dict containing the configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
        ValueError: If config file has invalid structure
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in config file: {e}")
    
    # Validate required sections
    required_sections = ['distance_thresholds', 'timing', 'validation', 'hardware']
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate distance thresholds
    distance_thresholds = config['distance_thresholds']
    required_distance_keys = ['warning', 'trigger', 'minimum_valid', 'maximum_valid']
    for key in required_distance_keys:
        if key not in distance_thresholds:
            raise ValueError(f"Missing required distance threshold: {key}")
    
    # Validate timing
    timing = config['timing']
    required_timing_keys = ['motor_forward_duration', 'motor_reverse_duration', 
                           'smoke_delay', 'smoke_duration', 'pump_duration', 
                           'cooldown_duration', 'reading_interval']
    for key in required_timing_keys:
        if key not in timing:
            raise ValueError(f"Missing required timing setting: {key}")
    
    # Validate hardware pins
    hardware = config['hardware']
    if 'motor_pins' not in hardware or 'forward' not in hardware['motor_pins'] or 'reverse' not in hardware['motor_pins']:
        raise ValueError("Invalid motor pin configuration")
    
    # Set default values for optional sections
    if 'logging' not in config:
        config['logging'] = {'level': 'INFO', 'file': 'halloween_barrel.log', 'console': True}
    
    if 'safety' not in config:
        config['safety'] = {'emergency_stop_enabled': True, 'max_sequence_duration': 30.0, 'auto_cleanup_on_error': True}
    
    if 'optional_components' not in config:
        config['optional_components'] = {
            'govee_light': {'enabled': False, 'ip_address': '192.168.1.100', 'port': 4003},
            'music_player': {'enabled': False, 'audio_file': '/path/to/halloween_sound.mp3', 'volume': 0.7}
        }
    
    
    return config

class HalloweenBarrelController:
    """
    Main controller class for the Halloween barrel project.
    
    This class manages all hardware components and provides comprehensive
    validation, error handling, and safety features.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Halloween barrel controller.
        
        Args:
            config: Configuration dictionary containing all settings
        """
        self.config = config
        self.logger = self._setup_logging()
        self.is_running = False
        self.last_trigger_time = 0
        self.failed_readings_count = 0
        
        # Hardware components
        self.motor: Optional[Motor] = None
        self.pump_relay: Optional[Relay] = None
        self.smoke_relay: Optional[Relay] = None
        self.ultrasonic_1: Optional[UltrasonicSensor] = None
        self.ultrasonic_2: Optional[UltrasonicSensor] = None
        self.govee_light: Optional[GoveeLight] = None
        self.music_player: Optional[MP3Player] = None
        
        # Distance reading cache
        self.distance_history = []
        
        # Sensor health tracking
        self.sensor1_working = True
        self.sensor2_working = True
        
        self.logger.info("Halloween Barrel Controller initializing...")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging configuration from YAML config."""
        log_config = self.config.get('logging', {})
        
        # Set logging level
        level_str = log_config.get('level', 'INFO').upper()
        level = getattr(logging, level_str, logging.INFO)
        
        # Create handlers
        handlers = []
        
        # Console handler
        if log_config.get('console', True):
            handlers.append(logging.StreamHandler(sys.stdout))
        
        # File handler
        log_file = log_config.get('file', 'halloween_barrel.log')
        handlers.append(logging.FileHandler(log_file))
        
        # Configure logging
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
        
        return logging.getLogger(__name__)
    
    def initialize_hardware(self) -> bool:
        """
        Initialize all hardware components with comprehensive validation.
        
        Returns:
            bool: True if all components initialized successfully, False otherwise
        """
        self.logger.info("Initializing hardware components...")
        
        try:
            # Initialize motor
            self.logger.info("Initializing motor...")
            motor_pins = self.config['hardware']['motor_pins']
            self.motor = Motor(motor_pins['forward'], motor_pins['reverse'])
            if not self.motor.is_initialized():
                raise RuntimeError("Motor initialization failed")
            self.motor.move_forward(4)
            self.motor.move_reverse(2.5)
            
            # Initialize relays
            self.logger.info("Initializing relays...")
            self.pump_relay = Relay(self.config['hardware']['pump_relay_pin'])
            self.smoke_relay = Relay(self.config['hardware']['smoke_relay_pin'])
            
            if not self.pump_relay.is_initialized() or not self.smoke_relay.is_initialized():
                raise RuntimeError("Relay initialization failed")
            
            # Initialize ultrasonic sensors with fallback logic
            self.logger.info("Initializing ultrasonic sensors...")
            us1_pins = self.config['hardware']['ultrasonic_1_pins']
            us2_pins = self.config['hardware']['ultrasonic_2_pins']
            
            # Try to initialize sensor 1
            try:
                self.ultrasonic_1 = UltrasonicSensor(us1_pins['trigger'], us1_pins['echo'])
                if self.ultrasonic_1.is_initialized():
                    self.sensor1_working = True
                    self.logger.info("✅ Ultrasonic sensor 1 initialized successfully")
                else:
                    self.sensor1_working = False
                    self.logger.warning("⚠️ Ultrasonic sensor 1 initialization failed")
            except Exception as e:
                self.sensor1_working = False
                self.logger.warning(f"⚠️ Ultrasonic sensor 1 initialization error: {e}")
            
            # Try to initialize sensor 2
            try:
                self.ultrasonic_2 = UltrasonicSensor(us2_pins['trigger'], us2_pins['echo'])
                if self.ultrasonic_2.is_initialized():
                    self.sensor2_working = True
                    self.logger.info("✅ Ultrasonic sensor 2 initialized successfully")
                else:
                    self.sensor2_working = False
                    self.logger.warning("⚠️ Ultrasonic sensor 2 initialization failed")
            except Exception as e:
                self.sensor2_working = False
                self.logger.warning(f"⚠️ Ultrasonic sensor 2 initialization error: {e}")
            
            # Check if at least one sensor is working
            if not (self.sensor1_working or self.sensor2_working):
                raise RuntimeError("Both ultrasonic sensors failed to initialize - at least one sensor is required")
            
            # Test ultrasonic sensors (non-blocking)
            self._test_ultrasonic_sensors()
            
            # Final check - ensure at least one sensor is still working after testing
            if not (self.sensor1_working or self.sensor2_working):
                raise RuntimeError("Both ultrasonic sensors failed testing - at least one working sensor is required")
            
            # Log final sensor status
            if self.sensor1_working and self.sensor2_working:
                self.logger.info("🎉 Both ultrasonic sensors initialized and tested successfully")
            elif self.sensor1_working:
                self.logger.info("🎉 System running with sensor 1 only (sensor 2 failed)")
            elif self.sensor2_working:
                self.logger.info("🎉 System running with sensor 2 only (sensor 1 failed)")
            
            # Initialize Govee light (optional)
            govee_config = self.config.get('optional_components', {}).get('govee_light', {})
            if govee_config.get('enabled', False):
                try:
                    self.logger.info("Initializing Govee light...")
                    self.govee_light = GoveeLight(govee_config['ip_address'], govee_config.get('port', 4003))
                    self.logger.info("Govee light initialized successfully")
                except Exception as e:
                    self.logger.warning(f"Govee light initialization failed (optional): {e}")
                    self.govee_light = None
            else:
                self.logger.info("Govee light disabled in configuration")
                self.govee_light = None
            
            # Initialize music player (optional)
            music_config = self.config.get('optional_components', {}).get('music_player', {})
            if music_config.get('enabled', False):
                try:
                    audio_file = music_config.get('audio_file', '')
                    if audio_file and audio_file != '/path/to/halloween_sound.mp3':
                        self.logger.info("Initializing music player...")
                        self.music_player = MP3Player(audio_file, music_config.get('volume', 0.7))
                        self.logger.info("Music player initialized successfully")
                    else:
                        self.logger.info("Music player disabled (no valid audio file configured)")
                        self.music_player = None
                except Exception as e:
                    self.logger.warning(f"Music player initialization failed (optional): {e}")
                    self.music_player = None
            else:
                self.logger.info("Music player disabled in configuration")
                self.music_player = None
            
            self.logger.info("All hardware components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Hardware initialization failed: {e}")
            self.cleanup()
            return False
    
    def _test_ultrasonic_sensors(self) -> None:
        """
        Test ultrasonic sensors with multiple readings to validate they're working.
        
        This method is non-blocking and will not raise errors. It only updates
        the sensor working status based on test results.
        """
        self.logger.info("Testing ultrasonic sensors...")
        
        test_readings = 5
        valid_readings_1 = 0
        valid_readings_2 = 0
        
        # Test sensor 1 if it's marked as working
        if self.sensor1_working and self.ultrasonic_1:
            for i in range(test_readings):
                try:
                    distance_1 = self.ultrasonic_1.read_distance()
                    if distance_1 is not None:
                        valid_readings_1 += 1
                        self.logger.info(f"Ultrasonic 1 reading {i+1}: {distance_1:.1f} cm")
                    else:
                        self.logger.debug(f"Ultrasonic 1 reading {i+1}: No reading")
                    time.sleep(0.1)
                except Exception as e:
                    self.logger.warning(f"Sensor 1 test reading {i+1} error: {e}")
        
        # Test sensor 2 if it's marked as working
        if self.sensor2_working and self.ultrasonic_2:
            for i in range(test_readings):
                try:
                    distance_2 = self.ultrasonic_2.read_distance()
                    if distance_2 is not None:
                        valid_readings_2 += 1
                        self.logger.info(f"Ultrasonic 2 reading {i+1}: {distance_2:.1f} cm")
                    else:
                        self.logger.debug(f"Ultrasonic 2 reading {i+1}: No reading")
                    time.sleep(0.1)
                except Exception as e:
                    self.logger.warning(f"Sensor 2 test reading {i+1} error: {e}")
        
        # Require at least 60% valid readings for a sensor to be considered working
        min_valid_readings = int(test_readings * 0.6)
        
        # Update sensor 1 status based on test results
        if self.sensor1_working:
            if valid_readings_1 < min_valid_readings:
                self.sensor1_working = False
                self.logger.warning(f"⚠️ Ultrasonic sensor 1 failed test: only {valid_readings_1}/{test_readings} valid readings")
            else:
                self.logger.info(f"✅ Ultrasonic sensor 1 test passed: {valid_readings_1}/{test_readings} valid readings")
        
        # Update sensor 2 status based on test results
        if self.sensor2_working:
            if valid_readings_2 < min_valid_readings:
                self.sensor2_working = False
                self.logger.warning(f"⚠️ Ultrasonic sensor 2 failed test: only {valid_readings_2}/{test_readings} valid readings")
            else:
                self.logger.info(f"✅ Ultrasonic sensor 2 test passed: {valid_readings_2}/{test_readings} valid readings")
        
        # Final status check
        if self.sensor1_working and self.sensor2_working:
            self.logger.info("✅ Both ultrasonic sensors are working properly")
        elif self.sensor1_working:
            self.logger.info("✅ Only sensor 1 is working (sensor 2 failed)")
        elif self.sensor2_working:
            self.logger.info("✅ Only sensor 2 is working (sensor 1 failed)")
        else:
            self.logger.error("❌ Both sensors failed testing - system will not function properly")
    
    def get_validated_distance(self) -> Optional[float]:
        """
        Get a validated distance reading using multiple sensors with fallback logic.
        
        If both sensors are working, uses the shortest reading.
        If only one sensor is working, uses that sensor.
        If neither sensor is working, returns None.
        
        Returns:
            Optional[float]: Validated distance in cm, or None if no valid readings
        """
        try:
            valid_distances = []
            
            # Try sensor 1 if it's marked as working
            if self.sensor1_working and self.ultrasonic_1:
                try:
                    distance_1 = self.ultrasonic_1.read_distance()
                    if distance_1 is not None and self._validate_distance_reading(distance_1):
                        valid_distances.append(distance_1)
                        self.logger.debug(f"Valid distance from sensor 1: {distance_1:.1f} cm")
                    else:
                        self.logger.debug("Sensor 1: No valid reading")
                except Exception as e:
                    self.logger.warning(f"Sensor 1 error: {e}")
                    self.sensor1_working = False
            
            # Try sensor 2 if it's marked as working
            if self.sensor2_working and self.ultrasonic_2:
                try:
                    distance_2 = self.ultrasonic_2.read_distance()
                    if distance_2 is not None and self._validate_distance_reading(distance_2):
                        valid_distances.append(distance_2)
                        self.logger.debug(f"Valid distance from sensor 2: {distance_2:.1f} cm")
                    else:
                        self.logger.debug("Sensor 2: No valid reading")
                except Exception as e:
                    self.logger.warning(f"Sensor 2 error: {e}")
                    self.sensor2_working = False
            
            # Check if we have any valid readings
            if not valid_distances:
                self.logger.warning("No valid distance readings from either sensor")
                self.failed_readings_count += 1
                
                # If both sensors are marked as not working, try to reinitialize them
                if not self.sensor1_working and not self.sensor2_working:
                    self.logger.info("Both sensors marked as not working, attempting reinitialization...")
                    self._attempt_sensor_recovery()
                
                return None
            
            # Reset failed readings counter on successful reading
            self.failed_readings_count = 0
            
            # Use the shortest valid distance (closest object)
            shortest_distance = min(valid_distances)
            
            # Log which sensors are being used
            if len(valid_distances) == 2:
                self.logger.debug(f"Using both sensors, shortest distance: {shortest_distance:.1f} cm")
            else:
                working_sensor = "sensor 1" if self.sensor1_working else "sensor 2"
                self.logger.debug(f"Using only {working_sensor}, distance: {shortest_distance:.1f} cm")
            
            # Add to history for consistency checking
            self.distance_history.append(shortest_distance)
            if len(self.distance_history) > self.config['validation']['consecutive_readings']:
                self.distance_history.pop(0)
            
            # Check for consistency if we have enough readings
            if len(self.distance_history) >= self.config['validation']['consecutive_readings']:
                if not self._validate_reading_consistency():
                    self.logger.warning("Distance readings are inconsistent, discarding")
                    return None
            
            return shortest_distance
            
        except Exception as e:
            self.logger.error(f"Error getting validated distance: {e}")
            self.failed_readings_count += 1
            return None
    
    def _attempt_sensor_recovery(self) -> None:
        """
        Attempt to recover failed sensors by reinitializing them.
        """
        self.logger.info("Attempting sensor recovery...")
        
        # Try to recover sensor 1
        if not self.sensor1_working and self.ultrasonic_1:
            try:
                # Test if sensor 1 can provide a reading
                distance = self.ultrasonic_1.read_distance()
                if distance is not None and self._validate_distance_reading(distance):
                    self.sensor1_working = True
                    self.logger.info("✅ Sensor 1 recovered")
                else:
                    self.logger.warning("Sensor 1 still not working")
            except Exception as e:
                self.logger.warning(f"Sensor 1 recovery failed: {e}")
        
        # Try to recover sensor 2
        if not self.sensor2_working and self.ultrasonic_2:
            try:
                # Test if sensor 2 can provide a reading
                distance = self.ultrasonic_2.read_distance()
                if distance is not None and self._validate_distance_reading(distance):
                    self.sensor2_working = True
                    self.logger.info("✅ Sensor 2 recovered")
                else:
                    self.logger.warning("Sensor 2 still not working")
            except Exception as e:
                self.logger.warning(f"Sensor 2 recovery failed: {e}")
        
        # Log final status
        if self.sensor1_working or self.sensor2_working:
            self.logger.info(f"Sensor recovery complete: Sensor 1: {self.sensor1_working}, Sensor 2: {self.sensor2_working}")
        else:
            self.logger.error("Sensor recovery failed: No sensors working")
    
    def _validate_distance_reading(self, distance: float) -> bool:
        """
        Validate a single distance reading.
        
        Args:
            distance: Distance reading to validate
            
        Returns:
            bool: True if reading is valid, False otherwise
        """
        min_dist = self.config['distance_thresholds']['minimum_valid']
        max_dist = self.config['distance_thresholds']['maximum_valid']
        
        if distance < min_dist or distance > max_dist:
            self.logger.debug(f"Distance reading {distance:.1f} cm outside valid range ({min_dist}-{max_dist} cm)")
            return False
        
        return True
    
    def _validate_reading_consistency(self) -> bool:
        """
        Validate that recent readings are consistent (not jumping around).
        
        Returns:
            bool: True if readings are consistent, False otherwise
        """
        if len(self.distance_history) < self.config['validation']['consecutive_readings']:
            return True
        
        tolerance = self.config['validation']['reading_tolerance']
        
        # Check if all readings are within tolerance of each other
        min_distance = min(self.distance_history)
        max_distance = max(self.distance_history)
        
        if max_distance - min_distance > tolerance:
            self.logger.debug(f"Readings inconsistent: range {min_distance:.1f}-{max_distance:.1f} cm (tolerance: {tolerance} cm)")
            return False
        
        return True
    
    def check_distance_thresholds(self, distance: float) -> Dict[str, bool]:
        """
        Check distance against configured thresholds.
        
        Args:
            distance: Distance reading to check
            
        Returns:
            Dict[str, bool]: Dictionary with threshold check results
        """
        thresholds = self.config['distance_thresholds']
        
        return {
            'warning': distance < thresholds['warning'],
            'trigger': distance < thresholds['trigger'],
            'valid': self._validate_distance_reading(distance)
        }
    
    def execute_halloween_sequence(self) -> bool:
        """
        Execute the complete Halloween barrel sequence with colored lighting and synchronized sound effects.
        
        Sequence phases:
        1. YELLOW - Warning phase with skeleton movement
        2. GREEN - Preparation phase with smoke
        3. RED - Pump activation phase with water spray
        4. OFF - Return to normal
        
        Returns:
            bool: True if sequence completed successfully, False otherwise
        """
        self.logger.info("Starting Halloween barrel sequence...")
        
        try:
            # Check cooldown period
            current_time = time.time()
            time_since_last_trigger = current_time - self.last_trigger_time
            
            if time_since_last_trigger < self.config['timing']['cooldown_duration']:
                remaining_cooldown = self.config['timing']['cooldown_duration'] - time_since_last_trigger
                self.logger.info(f"Sequence in cooldown, {remaining_cooldown:.1f} seconds remaining")
                return False
            
            # PHASE 1: YELLOW WARNING PHASE
            self.logger.info("Phase 1: Yellow warning phase - Skeleton movement")
            self._set_light_color(255, 255, 0)  # Yellow
            self._play_sound_effect('warning')  # Play 1-second vomiting sound
            
            # Move skeleton forward during yellow phase
            self.logger.info("Moving skeleton forward...")
            if not self.motor.move_forward(self.config['timing']['motor_forward_duration']):
                raise RuntimeError("Motor forward movement failed")
            
            time.sleep(2.0)  # Wait for yellow phase
            
            # PHASE 2: GREEN PREPARATION PHASE
            self.logger.info("Phase 2: Green preparation phase - Smoke activation")
            self._set_light_color(0, 255, 0)  # Green
            
            # Wait before smoke
            time.sleep(self.config['timing']['smoke_delay'])
            
            # Activate smoke during green phase
            self.logger.info("Activating smoke...")
            if not self.smoke_relay.on():
                raise RuntimeError("Failed to activate smoke relay")
            
            time.sleep(1.5)  # Wait for green phase
            
            # PHASE 3: RED PUMP ACTIVATION PHASE
            self.logger.info("Phase 3: Red pump activation phase - Water spray")
            self._set_light_color(255, 0, 0)  # Red
            
            # Activate pump (water spray) during red phase
            self.logger.info("Activating pump...")
            if not self.pump_relay.on():
                raise RuntimeError("Failed to activate pump relay")
            
            time.sleep(0.5)
            self._play_sound_effect('pump')  # Play 1-second vomiting sound synchronized with pump activation

            # Deactivate smoke during red phase
            self.logger.info("Deactivating smoke...")
            if not self.smoke_relay.off():
                raise RuntimeError("Failed to deactivate smoke relay")
            
            # Keep pump running for configured duration
            time.sleep(4)
            self._play_sound_effect('preparation')  # Play 4-second vomiting sound synchronized with pump
            time.sleep(2)
            
            # Deactivate pump
            self.logger.info("Deactivating pump...")
            if not self.pump_relay.off():
                raise RuntimeError("Failed to deactivate pump relay")
            
            # PHASE 4: COMPLETION PHASE
            self.logger.info("Phase 4: Completion phase - Skeleton return")
            
            # Wait before reverse movement
            time.sleep(1.0)
            
            # Move skeleton back
            self.logger.info("Moving skeleton back...")
            if not self.motor.move_reverse(self.config['timing']['motor_reverse_duration']):
                raise RuntimeError("Motor reverse movement failed")
            
            # Turn off light
            self._set_light_color(0, 0, 0)  # Off
            self.logger.info("Lighting deactivated")
            
            # Update last trigger time
            self.last_trigger_time = current_time
            
            self.logger.info("Halloween barrel sequence completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Halloween sequence failed: {e}")
            self._emergency_stop()
            return False
    
    def _set_light_color(self, red: int, green: int, blue: int) -> None:
        """
        Set the Govee light color with error handling.
        
        Args:
            red: Red component (0-255)
            green: Green component (0-255)
            blue: Blue component (0-255)
        """
        if lights:
            try:
                self.lights.set_color(red, green, blue)
                if red == 0 and green == 0 and blue == 0:
                    self.lights.turn_off()
                else:
                    self.lights.turn_on()
                self.logger.debug(f"Light set to RGB({red}, {green}, {blue})")
            except Exception as e:
                self.logger.error(f"Failed to set light color: {e}")
    
    def _play_sound_effect(self, sound_type: str) -> None:
        """
        Play a vomiting sound effect based on the type.
        
        Args:
            sound_type: Type of sound to play ('warning', 'preparation', 'pump')
        """
        try:
            if sound_type == 'warning':
                vomit_1.play()
                self.logger.debug("Playing warning vomiting sound (1 sec)")
            elif sound_type == 'preparation':
                vomit_2.play()
                self.logger.debug("Playing preparation vomiting sound (2 sec)")
            elif sound_type == 'pump':
                vomit_4.play()
                self.logger.debug("Playing pump vomiting sound (4 sec)")
            else:
                self.logger.warning(f"Unknown sound type: {sound_type}")
        except Exception as e:
            self.logger.error(f"Failed to play vomiting sound {sound_type}: {e}")
    
    def _emergency_stop(self) -> None:
        """Emergency stop all active components."""
        self.logger.warning("Emergency stop activated!")
        
        try:
            if self.motor:
                self.motor.stop()
            
            if self.pump_relay:
                self.pump_relay.off()
            
            if self.smoke_relay:
                self.smoke_relay.off()
            
            if self.govee_light:
                self.govee_light.turn_off()
            
            if self.music_player:
                self.music_player.stop()
            
            # Stop all vomiting sounds
            try:
                vomit_1.stop()
                vomit_2.stop()
                vomit_4.stop()
                self.logger.debug("Stopped all vomiting sounds")
            except Exception as e:
                self.logger.error(f"Error stopping vomiting sounds: {e}")
                
        except Exception as e:
            self.logger.error(f"Error during emergency stop: {e}")
    
    def check_system_health(self) -> bool:
        """
        Check the overall health of the system.
        
        Returns:
            bool: True if system is healthy, False otherwise
        """
        if self.failed_readings_count >= self.config['validation']['max_failed_readings']:
            self.logger.error(f"Too many consecutive failed readings: {self.failed_readings_count}")
            return False
        
        # Check if all critical components are initialized
        critical_components = [self.motor, self.pump_relay, self.smoke_relay]
        
        for component in critical_components:
            if component is None or not component.is_initialized():
                self.logger.error(f"Critical component not initialized: {component}")
                return False
        
        # Check ultrasonic sensors - at least one must be working
        if not (self.sensor1_working or self.sensor2_working):
            self.logger.error("No ultrasonic sensors working - both sensors failed")
            return False
        
        # Log sensor status
        if self.sensor1_working and self.sensor2_working:
            self.logger.debug("Both ultrasonic sensors working")
        elif self.sensor1_working:
            self.logger.info("Using only sensor 1 (sensor 2 failed)")
        elif self.sensor2_working:
            self.logger.info("Using only sensor 2 (sensor 1 failed)")
        
        return True
    
    def run(self) -> None:
        """Main control loop."""
        self.logger.info("Starting Halloween barrel control loop...")
        self.is_running = True
        
        try:
            while self.is_running:
                # Check system health
                if not self.check_system_health():
                    self.logger.error("System health check failed, stopping...")
                    break
                
                # Get validated distance reading
                distance = self.get_validated_distance()
                
                if distance is not None:
                    self.logger.info(f"Distance: {distance:.1f} cm")
                    
                    # Check thresholds
                    thresholds = self.check_distance_thresholds(distance)
                    
                    if thresholds['warning'] and not thresholds['trigger']:
                        self.logger.debug("Warning threshold reached - object approaching")
                    
                    elif thresholds['trigger']:
                        self.logger.info("Trigger threshold reached - executing Halloween sequence")
                        self.execute_halloween_sequence()
                    
                else:
                    self.logger.warning("No valid distance reading available")
                
                # Wait before next reading
                time.sleep(self.config['timing']['reading_interval'])
                
        except KeyboardInterrupt:
            self.logger.info("Control loop interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error in control loop: {e}")
        finally:
            self.is_running = False
            self.cleanup()
    
    def stop(self) -> None:
        """Stop the control loop."""
        self.logger.info("Stopping Halloween barrel controller...")
        self.is_running = False
    
    def cleanup(self) -> None:
        """Clean up all hardware components."""
        self.logger.info("Cleaning up hardware components...")
        
        try:
            if self.motor:
                self.motor.cleanup()
            
            if self.pump_relay:
                self.pump_relay.cleanup()
            
            if self.smoke_relay:
                self.smoke_relay.cleanup()
            
            if self.ultrasonic_1:
                self.ultrasonic_1.cleanup()
            
            if self.ultrasonic_2:
                self.ultrasonic_2.cleanup()
            
            if self.govee_light:
                self.govee_light.close()
            
            if self.music_player:
                self.music_player.cleanup()
            
            # Clean up vomiting sound players
            try:
                vomit_1.cleanup()
                vomit_2.cleanup()
                vomit_4.cleanup()
                self.logger.debug("Cleaned up vomiting sound players")
            except Exception as e:
                self.logger.error(f"Error cleaning up vomiting sounds: {e}")
                
            self.logger.info("Hardware cleanup completed")
            
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print("\nShutdown signal received...")
    if 'controller' in globals():
        controller.stop()
    sys.exit(0)

def main():
    """Main entry point."""
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Load configuration from YAML file
        print("Loading configuration...")
        config = load_config()
        print("Configuration loaded successfully")
        
        # Create and initialize controller
        global controller
        controller = HalloweenBarrelController(config)
        
        if controller.initialize_hardware():
            controller.run()
        else:
            print("Hardware initialization failed. Exiting.")
            return 1
            
    except FileNotFoundError as e:
        print(f"Configuration error: {e}")
        print("Please ensure configs.yaml exists and is properly configured.")
        return 1
    except yaml.YAMLError as e:
        print(f"Configuration error: Invalid YAML in configs.yaml: {e}")
        return 1
    except ValueError as e:
        print(f"Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"Fatal error: {e}")
        return 1
    finally:
        if 'controller' in globals():
            controller.cleanup()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

