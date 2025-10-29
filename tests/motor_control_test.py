#!/usr/bin/env python3
"""
Motor Control Test Script for Halloween Barrel Project

This script tests the motor control functionality including:
- Motor initialization
- Forward movement
- Reverse movement
- Stop functionality
- Error handling
- GPIO cleanup

Usage:
    python motor_control_test.py

Make sure to run this on a Raspberry Pi with the motor properly connected!
"""

import sys
import time
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from plugins.motor import Motor

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

def test_motor_initialization(logger):
    """Test motor initialization with different pin configurations."""
    logger.info("=" * 50)
    logger.info("Testing Motor Initialization")
    logger.info("=" * 50)
    
    # Test valid pin configuration
    try:
        logger.info("Testing valid pin configuration (18, 19)...")
        motor = Motor(18, 19)
        if motor.is_initialized():
            logger.info("✅ Motor initialization successful")
            motor.cleanup()
            return True
        else:
            logger.error("❌ Motor initialization failed - not initialized")
            return False
    except Exception as e:
        logger.error(f"❌ Motor initialization failed: {e}")
        return False

def test_motor_forward_movement(logger):
    """Test motor forward movement."""
    logger.info("=" * 50)
    logger.info("Testing Motor Forward Movement")
    logger.info("=" * 50)
    
    try:
        motor = Motor(18, 19)
        if not motor.is_initialized():
            logger.error("❌ Motor not initialized, skipping forward test")
            return False
        
        logger.info("Moving motor forward for 2 seconds...")
        logger.info("⚠️  WARNING: Make sure motor is properly connected and safe to move!")
        
        # Countdown before movement
        for i in range(3, 0, -1):
            logger.info(f"Starting in {i}...")
            time.sleep(1)
        
        success = motor.move_forward(2.0)
        if success:
            logger.info("✅ Motor forward movement completed successfully")
        else:
            logger.error("❌ Motor forward movement failed")
        
        motor.cleanup()
        return success
        
    except Exception as e:
        logger.error(f"❌ Motor forward test failed: {e}")
        return False

def test_motor_reverse_movement(logger):
    """Test motor reverse movement."""
    logger.info("=" * 50)
    logger.info("Testing Motor Reverse Movement")
    logger.info("=" * 50)
    
    try:
        motor = Motor(18, 19)
        if not motor.is_initialized():
            logger.error("❌ Motor not initialized, skipping reverse test")
            return False
        
        logger.info("Moving motor reverse for 2 seconds...")
        logger.info("⚠️  WARNING: Make sure motor is properly connected and safe to move!")
        
        # Countdown before movement
        for i in range(3, 0, -1):
            logger.info(f"Starting in {i}...")
            time.sleep(1)
        
        success = motor.move_reverse(2.0)
        if success:
            logger.info("✅ Motor reverse movement completed successfully")
        else:
            logger.error("❌ Motor reverse movement failed")
        
        motor.cleanup()
        return success
        
    except Exception as e:
        logger.error(f"❌ Motor reverse test failed: {e}")
        return False

def test_motor_stop_functionality(logger):
    """Test motor stop functionality."""
    logger.info("=" * 50)
    logger.info("Testing Motor Stop Functionality")
    logger.info("=" * 50)
    
    try:
        motor = Motor(18, 19)
        if not motor.is_initialized():
            logger.error("❌ Motor not initialized, skipping stop test")
            return False
        
        logger.info("Testing motor stop functionality...")
        
        # Test stop when motor is not moving
        success = motor.stop()
        if success:
            logger.info("✅ Motor stop (idle) successful")
        else:
            logger.error("❌ Motor stop (idle) failed")
        
        motor.cleanup()
        return success
        
    except Exception as e:
        logger.error(f"❌ Motor stop test failed: {e}")
        return False

def test_motor_error_handling(logger):
    """Test motor error handling with invalid inputs."""
    logger.info("=" * 50)
    logger.info("Testing Motor Error Handling")
    logger.info("=" * 50)
    
    # Test invalid pin numbers
    try:
        logger.info("Testing invalid pin numbers...")
        motor = Motor(99, 100)  # Invalid pins
        logger.error("❌ Should have raised ValueError for invalid pins")
        return False
    except ValueError as e:
        logger.info(f"✅ Correctly caught ValueError: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False
    
    # Test same pin for forward and reverse
    try:
        logger.info("Testing same pin for forward and reverse...")
        motor = Motor(18, 18)  # Same pin
        logger.error("❌ Should have raised ValueError for same pins")
        return False
    except ValueError as e:
        logger.info(f"✅ Correctly caught ValueError: {e}")
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False
    
    # Test invalid duration
    try:
        motor = Motor(5, 6)
        logger.info("Testing invalid duration (negative)...")
        motor.move_forward(-1.0)
        logger.error("❌ Should have raised ValueError for negative duration")
        motor.cleanup()
        return False
    except ValueError as e:
        logger.info(f"✅ Correctly caught ValueError: {e}")
        motor.cleanup()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        motor.cleanup()
        return False
    
    try:
        motor = Motor(5, 6)
        logger.info("Testing invalid duration (too long)...")
        motor.move_forward(100.0)  # Too long
        logger.error("❌ Should have raised ValueError for too long duration")
        motor.cleanup()
        return False
    except ValueError as e:
        logger.info(f"✅ Correctly caught ValueError: {e}")
        motor.cleanup()
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        motor.cleanup()
        return False
    
    return True

def test_motor_cleanup(logger):
    """Test motor cleanup functionality."""
    logger.info("=" * 50)
    logger.info("Testing Motor Cleanup")
    logger.info("=" * 50)
    
    try:
        motor = Motor(5, 6)
        if not motor.is_initialized():
            logger.error("❌ Motor not initialized, skipping cleanup test")
            return False
        
        logger.info("Testing motor cleanup...")
        motor.cleanup()
        
        if not motor.is_initialized():
            logger.info("✅ Motor cleanup successful - motor no longer initialized")
        else:
            logger.error("❌ Motor cleanup failed - motor still initialized")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Motor cleanup test failed: {e}")
        return False

def test_motor_context_manager(logger):
    """Test motor context manager functionality."""
    logger.info("=" * 50)
    logger.info("Testing Motor Context Manager")
    logger.info("=" * 50)
    
    try:
        logger.info("Testing motor context manager...")
        
        with Motor(5, 6) as motor:
            if motor.is_initialized():
                logger.info("✅ Motor initialized in context manager")
                
                # Test a quick movement
                logger.info("Testing quick movement in context manager...")
                success = motor.move_forward(0.5)
                if success:
                    logger.info("✅ Movement successful in context manager")
                else:
                    logger.error("❌ Movement failed in context manager")
                    return False
            else:
                logger.error("❌ Motor not initialized in context manager")
                return False
        
        logger.info("✅ Motor context manager cleanup completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Motor context manager test failed: {e}")
        return False

def run_interactive_test(logger):
    """Run an interactive test where user can control the motor."""
    logger.info("=" * 50)
    logger.info("Interactive Motor Control Test")
    logger.info("=" * 50)
    
    try:
        motor = Motor(5, 6)
        if not motor.is_initialized():
            logger.error("❌ Motor not initialized, skipping interactive test")
            return False
        
        logger.info("Interactive test started. You can control the motor manually.")
        logger.info("Commands:")
        logger.info("  'f' - Move forward for 2 seconds")
        logger.info("  'r' - Move reverse for 2 seconds")
        logger.info("  's' - Stop motor")
        logger.info("  'q' - Quit interactive test")
        logger.info("⚠️  WARNING: Make sure motor is properly connected and safe to move!")
        
        while True:
            try:
                command = input("\nEnter command (f/r/s/q): ").strip().lower()
                
                if command == 'q':
                    logger.info("Exiting interactive test...")
                    break
                elif command == 'f':
                    logger.info("Moving forward...")
                    motor.move_forward(2.0)
                elif command == 'r':
                    logger.info("Moving reverse...")
                    motor.move_reverse(2.0)
                elif command == 's':
                    logger.info("Stopping motor...")
                    motor.stop()
                else:
                    logger.info("Invalid command. Use f/r/s/q")
                    
            except KeyboardInterrupt:
                logger.info("\nExiting interactive test...")
                break
            except Exception as e:
                logger.error(f"Error during interactive test: {e}")
        
        motor.cleanup()
        return True
        
    except Exception as e:
        logger.error(f"❌ Interactive test failed: {e}")
        return False

def main():
    """Main test function."""
    logger = setup_logging()
    
    logger.info("🎃 Halloween Barrel Motor Control Test")
    logger.info("=" * 60)
    logger.info("This script will test the motor control functionality.")
    logger.info("Make sure the motor is properly connected to GPIO pins 5 and 6!")
    logger.info("=" * 60)
    
    # Test results
    test_results = []
    
    # Run all tests
    test_results.append(("Initialization", test_motor_initialization(logger)))
    test_results.append(("Error Handling", test_motor_error_handling(logger)))
    test_results.append(("Stop Functionality", test_motor_stop_functionality(logger)))
    test_results.append(("Context Manager", test_motor_context_manager(logger)))
    test_results.append(("Cleanup", test_motor_cleanup(logger)))
    
    # Ask user if they want to run movement tests
    logger.info("\n" + "=" * 60)
    response = input("Do you want to run movement tests? (y/n): ").strip().lower()
    
    if response == 'y':
        test_results.append(("Forward Movement", test_motor_forward_movement(logger)))
        test_results.append(("Reverse Movement", test_motor_reverse_movement(logger)))
        
        # Ask user if they want to run interactive test
        response = input("Do you want to run interactive test? (y/n): ").strip().lower()
        if response == 'y':
            test_results.append(("Interactive Test", run_interactive_test(logger)))
    else:
        logger.info("Skipping movement tests as requested.")
    
    # Print test results summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name:20} - {status}")
        if result:
            passed += 1
    
    logger.info("=" * 60)
    logger.info(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! Motor control is working correctly.")
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
