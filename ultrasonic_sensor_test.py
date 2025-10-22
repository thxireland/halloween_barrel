#!/usr/bin/env python3
"""
Ultrasonic Sensor Test Script for Halloween Barrel Project

This script tests the ultrasonic sensor functionality including:
- Dual sensor initialization and testing
- Fallback logic to use single sensor if one fails
- Distance measurement validation
- Sensor health monitoring
- Error handling and recovery

Usage:
    python ultrasonic_sensor_test.py

Make sure to run this on a Raspberry Pi with the sensors properly connected!
"""

import sys
import time
import logging
from pathlib import Path
from typing import Optional, Tuple, List

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from plugins.ultrasonic import UltrasonicSensor

def setup_logging():
    """Set up logging for the test."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

class UltrasonicSensorManager:
    """
    Manages dual ultrasonic sensors with fallback logic.
    
    This class handles two ultrasonic sensors and provides fallback
    functionality to use only one sensor if the other fails.
    """
    
    def __init__(self, sensor1_pins: Tuple[int, int], sensor2_pins: Tuple[int, int]):
        """
        Initialize the ultrasonic sensor manager.
        
        Args:
            sensor1_pins: (trigger, echo) pins for sensor 1
            sensor2_pins: (trigger, echo) pins for sensor 2
        """
        self.logger = logging.getLogger(__name__)
        self.sensor1: Optional[UltrasonicSensor] = None
        self.sensor2: Optional[UltrasonicSensor] = None
        self.sensor1_working = False
        self.sensor2_working = False
        self.sensor1_pins = sensor1_pins
        self.sensor2_pins = sensor2_pins
        
    def initialize_sensors(self) -> bool:
        """
        Initialize both ultrasonic sensors.
        
        Returns:
            bool: True if at least one sensor initialized successfully
        """
        self.logger.info("Initializing ultrasonic sensors...")
        
        # Initialize sensor 1
        try:
            self.logger.info(f"Initializing sensor 1 on pins {self.sensor1_pins}...")
            self.sensor1 = UltrasonicSensor(self.sensor1_pins[0], self.sensor1_pins[1])
            if self.sensor1.is_initialized():
                self.sensor1_working = True
                self.logger.info("✅ Sensor 1 initialized successfully")
            else:
                self.logger.error("❌ Sensor 1 initialization failed")
        except Exception as e:
            self.logger.error(f"❌ Sensor 1 initialization error: {e}")
            self.sensor1_working = False
        
        # Initialize sensor 2
        try:
            self.logger.info(f"Initializing sensor 2 on pins {self.sensor2_pins}...")
            self.sensor2 = UltrasonicSensor(self.sensor2_pins[0], self.sensor2_pins[1])
            if self.sensor2.is_initialized():
                self.sensor2_working = True
                self.logger.info("✅ Sensor 2 initialized successfully")
            else:
                self.logger.error("❌ Sensor 2 initialization failed")
        except Exception as e:
            self.logger.error(f"❌ Sensor 2 initialization error: {e}")
            self.sensor2_working = False
        
        # Check if at least one sensor is working
        if self.sensor1_working or self.sensor2_working:
            self.logger.info(f"✅ At least one sensor working: Sensor 1: {self.sensor1_working}, Sensor 2: {self.sensor2_working}")
            return True
        else:
            self.logger.error("❌ No sensors working - both initialization failed")
            return False
    
    def test_sensor_readings(self, sensor_num: int, sensor: UltrasonicSensor, test_name: str) -> bool:
        """
        Test a single sensor with multiple readings.
        
        Args:
            sensor_num: Sensor number (1 or 2)
            sensor: Sensor instance to test
            test_name: Name for logging
            
        Returns:
            bool: True if sensor is working properly
        """
        self.logger.info(f"Testing {test_name}...")
        
        test_readings = 5
        valid_readings = 0
        readings = []
        
        for i in range(test_readings):
            try:
                distance = sensor.read_distance()
                if distance is not None:
                    valid_readings += 1
                    readings.append(distance)
                    self.logger.info(f"Sensor {sensor_num} reading {i+1}: {distance:.1f} cm")
                else:
                    self.logger.warning(f"Sensor {sensor_num} reading {i+1}: No reading")
                
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Sensor {sensor_num} reading {i+1} error: {e}")
        
        # Require at least 60% valid readings
        min_valid_readings = int(test_readings * 0.6)
        
        if valid_readings >= min_valid_readings:
            avg_distance = sum(readings) / len(readings) if readings else 0
            self.logger.info(f"✅ {test_name} passed: {valid_readings}/{test_readings} valid readings, avg: {avg_distance:.1f} cm")
            return True
        else:
            self.logger.error(f"❌ {test_name} failed: only {valid_readings}/{test_readings} valid readings")
            return False
    
    def test_both_sensors(self) -> Tuple[bool, bool]:
        """
        Test both sensors and return their status.
        
        Returns:
            Tuple[bool, bool]: (sensor1_working, sensor2_working)
        """
        self.logger.info("=" * 50)
        self.logger.info("Testing Both Ultrasonic Sensors")
        self.logger.info("=" * 50)
        
        sensor1_working = False
        sensor2_working = False
        
        # Test sensor 1
        if self.sensor1 and self.sensor1_working:
            sensor1_working = self.test_sensor_readings(1, self.sensor1, "Sensor 1")
        else:
            self.logger.warning("Sensor 1 not available for testing")
        
        # Test sensor 2
        if self.sensor2 and self.sensor2_working:
            sensor2_working = self.test_sensor_readings(2, self.sensor2, "Sensor 2")
        else:
            self.logger.warning("Sensor 2 not available for testing")
        
        # Update working status
        self.sensor1_working = sensor1_working
        self.sensor2_working = sensor2_working
        
        return sensor1_working, sensor2_working
    
    def get_distance_reading(self) -> Optional[float]:
        """
        Get distance reading with fallback logic.
        
        Returns:
            Optional[float]: Distance reading in cm, or None if no sensors working
        """
        valid_readings = []
        
        # Try sensor 1
        if self.sensor1 and self.sensor1_working:
            try:
                distance = self.sensor1.read_distance()
                if distance is not None:
                    valid_readings.append(distance)
                    self.logger.debug(f"Sensor 1 reading: {distance:.1f} cm")
            except Exception as e:
                self.logger.error(f"Sensor 1 reading error: {e}")
                self.sensor1_working = False
        
        # Try sensor 2
        if self.sensor2 and self.sensor2_working:
            try:
                distance = self.sensor2.read_distance()
                if distance is not None:
                    valid_readings.append(distance)
                    self.logger.debug(f"Sensor 2 reading: {distance:.1f} cm")
            except Exception as e:
                self.logger.error(f"Sensor 2 reading error: {e}")
                self.sensor2_working = False
        
        if not valid_readings:
            self.logger.warning("No valid readings from either sensor")
            return None
        
        # Use the shortest valid reading (closest object)
        shortest_distance = min(valid_readings)
        
        if len(valid_readings) == 2:
            self.logger.debug(f"Using shortest of both readings: {shortest_distance:.1f} cm")
        else:
            self.logger.debug(f"Using single sensor reading: {shortest_distance:.1f} cm")
        
        return shortest_distance
    
    def get_sensor_status(self) -> dict:
        """
        Get the current status of both sensors.
        
        Returns:
            dict: Status information about both sensors
        """
        return {
            'sensor1_working': self.sensor1_working,
            'sensor2_working': self.sensor2_working,
            'sensor1_initialized': self.sensor1 is not None and self.sensor1.is_initialized(),
            'sensor2_initialized': self.sensor2 is not None and self.sensor2.is_initialized(),
            'at_least_one_working': self.sensor1_working or self.sensor2_working
        }
    
    def cleanup(self):
        """Clean up both sensors."""
        self.logger.info("Cleaning up ultrasonic sensors...")
        
        if self.sensor1:
            try:
                self.sensor1.cleanup()
                self.logger.debug("Sensor 1 cleaned up")
            except Exception as e:
                self.logger.error(f"Error cleaning up sensor 1: {e}")
        
        if self.sensor2:
            try:
                self.sensor2.cleanup()
                self.logger.debug("Sensor 2 cleaned up")
            except Exception as e:
                self.logger.error(f"Error cleaning up sensor 2: {e}")

def test_sensor_initialization(logger):
    """Test sensor initialization."""
    logger.info("=" * 50)
    logger.info("Testing Sensor Initialization")
    logger.info("=" * 50)
    
    try:
        # Test with the pins from your config
        sensor_manager = UltrasonicSensorManager((24, 23), (7, 8))
        
        success = sensor_manager.initialize_sensors()
        if success:
            logger.info("✅ Sensor initialization successful")
        else:
            logger.error("❌ Sensor initialization failed")
        
        sensor_manager.cleanup()
        return success
        
    except Exception as e:
        logger.error(f"❌ Sensor initialization test failed: {e}")
        return False

def test_sensor_readings(logger):
    """Test sensor readings and fallback logic."""
    logger.info("=" * 50)
    logger.info("Testing Sensor Readings and Fallback Logic")
    logger.info("=" * 50)
    
    try:
        sensor_manager = UltrasonicSensorManager((24, 23), (7, 8))
        
        if not sensor_manager.initialize_sensors():
            logger.error("❌ Sensor initialization failed, skipping reading test")
            return False
        
        # Test both sensors
        sensor1_working, sensor2_working = sensor_manager.test_both_sensors()
        
        logger.info(f"Sensor status: Sensor 1: {sensor1_working}, Sensor 2: {sensor2_working}")
        
        if not (sensor1_working or sensor2_working):
            logger.error("❌ No sensors working, cannot test readings")
            sensor_manager.cleanup()
            return False
        
        # Test distance readings
        logger.info("Testing distance readings...")
        logger.info("⚠️  WARNING: Make sure sensors have clear line of sight!")
        
        for i in range(10):
            distance = sensor_manager.get_distance_reading()
            if distance is not None:
                logger.info(f"Reading {i+1}: {distance:.1f} cm")
            else:
                logger.warning(f"Reading {i+1}: No valid reading")
            time.sleep(0.5)
        
        # Test sensor status
        status = sensor_manager.get_sensor_status()
        logger.info(f"Sensor status: {status}")
        
        sensor_manager.cleanup()
        return True
        
    except Exception as e:
        logger.error(f"❌ Sensor reading test failed: {e}")
        return False

def test_single_sensor_fallback(logger):
    """Test fallback to single sensor when one fails."""
    logger.info("=" * 50)
    logger.info("Testing Single Sensor Fallback")
    logger.info("=" * 50)
    
    try:
        sensor_manager = UltrasonicSensorManager((24, 23), (7, 8))
        
        if not sensor_manager.initialize_sensors():
            logger.error("❌ Sensor initialization failed, skipping fallback test")
            return False
        
        # Test both sensors first
        sensor1_working, sensor2_working = sensor_manager.test_both_sensors()
        
        if not (sensor1_working or sensor2_working):
            logger.error("❌ No sensors working, cannot test fallback")
            sensor_manager.cleanup()
            return False
        
        # Test readings with available sensors
        logger.info("Testing readings with available sensors...")
        
        for i in range(5):
            distance = sensor_manager.get_distance_reading()
            if distance is not None:
                logger.info(f"Fallback reading {i+1}: {distance:.1f} cm")
            else:
                logger.warning(f"Fallback reading {i+1}: No valid reading")
            time.sleep(0.5)
        
        # Test status reporting
        status = sensor_manager.get_sensor_status()
        logger.info(f"Final sensor status: {status}")
        
        if status['at_least_one_working']:
            logger.info("✅ Fallback logic working - at least one sensor operational")
        else:
            logger.error("❌ Fallback logic failed - no sensors working")
        
        sensor_manager.cleanup()
        return status['at_least_one_working']
        
    except Exception as e:
        logger.error(f"❌ Single sensor fallback test failed: {e}")
        return False

def test_continuous_monitoring(logger):
    """Test continuous monitoring with fallback logic."""
    logger.info("=" * 50)
    logger.info("Testing Continuous Monitoring")
    logger.info("=" * 50)
    
    try:
        sensor_manager = UltrasonicSensorManager((24, 23), (7, 8))
        
        if not sensor_manager.initialize_sensors():
            logger.error("❌ Sensor initialization failed, skipping monitoring test")
            return False
        
        logger.info("Starting continuous monitoring for 30 seconds...")
        logger.info("Move objects in front of sensors to test detection!")
        logger.info("Press Ctrl+C to stop early")
        
        start_time = time.time()
        reading_count = 0
        valid_readings = 0
        
        try:
            while time.time() - start_time < 30:
                distance = sensor_manager.get_distance_reading()
                reading_count += 1
                
                if distance is not None:
                    valid_readings += 1
                    logger.info(f"Reading {reading_count}: {distance:.1f} cm")
                else:
                    logger.warning(f"Reading {reading_count}: No valid reading")
                
                time.sleep(1.0)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        
        # Calculate success rate
        success_rate = (valid_readings / reading_count * 100) if reading_count > 0 else 0
        logger.info(f"Monitoring complete: {valid_readings}/{reading_count} valid readings ({success_rate:.1f}%)")
        
        sensor_manager.cleanup()
        return success_rate > 50  # Consider successful if >50% valid readings
        
    except Exception as e:
        logger.error(f"❌ Continuous monitoring test failed: {e}")
        return False

def run_interactive_test(logger):
    """Run an interactive test where user can monitor sensors."""
    logger.info("=" * 50)
    logger.info("Interactive Sensor Monitoring")
    logger.info("=" * 50)
    
    try:
        sensor_manager = UltrasonicSensorManager((24, 23), (7, 8))
        
        if not sensor_manager.initialize_sensors():
            logger.error("❌ Sensor initialization failed, skipping interactive test")
            return False
        
        logger.info("Interactive monitoring started.")
        logger.info("Commands:")
        logger.info("  'r' - Get single reading")
        logger.info("  's' - Show sensor status")
        logger.info("  'c' - Continuous monitoring (10 readings)")
        logger.info("  'q' - Quit interactive test")
        logger.info("⚠️  WARNING: Make sure sensors have clear line of sight!")
        
        while True:
            try:
                command = input("\nEnter command (r/s/c/q): ").strip().lower()
                
                if command == 'q':
                    logger.info("Exiting interactive test...")
                    break
                elif command == 'r':
                    distance = sensor_manager.get_distance_reading()
                    if distance is not None:
                        logger.info(f"Distance reading: {distance:.1f} cm")
                    else:
                        logger.warning("No valid reading available")
                elif command == 's':
                    status = sensor_manager.get_sensor_status()
                    logger.info(f"Sensor status: {status}")
                elif command == 'c':
                    logger.info("Continuous monitoring (10 readings)...")
                    for i in range(10):
                        distance = sensor_manager.get_distance_reading()
                        if distance is not None:
                            logger.info(f"Reading {i+1}: {distance:.1f} cm")
                        else:
                            logger.warning(f"Reading {i+1}: No valid reading")
                        time.sleep(0.5)
                else:
                    logger.info("Invalid command. Use r/s/c/q")
                    
            except KeyboardInterrupt:
                logger.info("\nExiting interactive test...")
                break
            except Exception as e:
                logger.error(f"Error during interactive test: {e}")
        
        sensor_manager.cleanup()
        return True
        
    except Exception as e:
        logger.error(f"❌ Interactive test failed: {e}")
        return False

def main():
    """Main test function."""
    logger = setup_logging()
    
    logger.info("🎃 Halloween Barrel Ultrasonic Sensor Test")
    logger.info("=" * 60)
    logger.info("This script will test the ultrasonic sensor functionality.")
    logger.info("Make sure the sensors are properly connected to GPIO pins!")
    logger.info("Sensor 1: Trigger=24, Echo=23")
    logger.info("Sensor 2: Trigger=7, Echo=8")
    logger.info("=" * 60)
    
    # Test results
    test_results = []
    
    # Run all tests
    test_results.append(("Initialization", test_sensor_initialization(logger)))
    test_results.append(("Readings & Fallback", test_sensor_readings(logger)))
    test_results.append(("Single Sensor Fallback", test_single_sensor_fallback(logger)))
    test_results.append(("Continuous Monitoring", test_continuous_monitoring(logger)))
    
    # Ask user if they want to run interactive test
    logger.info("\n" + "=" * 60)
    response = input("Do you want to run interactive test? (y/n): ").strip().lower()
    
    if response == 'y':
        test_results.append(("Interactive Test", run_interactive_test(logger)))
    else:
        logger.info("Skipping interactive test as requested.")
    
    # Print test results summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name:25} - {status}")
        if result:
            passed += 1
    
    logger.info("=" * 60)
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! Ultrasonic sensors are working correctly.")
        return 0
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
