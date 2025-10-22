#!/usr/bin/env python3
"""
Govee Light Test Script for Halloween Barrel Project

This script tests the Govee light functionality including:
- Light initialization and connection
- Color changes and effects
- On/off functionality
- Error handling and recovery
- Halloween sequence lighting effects

Usage:
    python light_test.py

Make sure your Govee light is connected to WiFi and the IP address is correct!
"""

import sys
import time
import logging
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from plugins.govee_plugin import GoveeLight

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

def test_light_initialization(logger, ip_address="192.168.1.212"):
    """Test light initialization and connection."""
    logger.info("=" * 50)
    logger.info("Testing Light Initialization")
    logger.info("=" * 50)
    
    try:
        logger.info(f"Initializing Govee light at IP: {ip_address}")
        light = GoveeLight(ip_address)
        logger.info("✅ Light object created successfully")
        return light
    except Exception as e:
        logger.error(f"❌ Light initialization failed: {e}")
        return None

def test_basic_light_control(logger, light):
    """Test basic light on/off functionality."""
    logger.info("=" * 50)
    logger.info("Testing Basic Light Control")
    logger.info("=" * 50)
    
    if not light:
        logger.error("❌ No light object available for testing")
        return False
    
    try:
        # Test turning light on
        logger.info("Turning light ON...")
        success = light.turn_on()
        if success:
            logger.info("✅ Light turned ON successfully")
        else:
            logger.error("❌ Failed to turn light ON")
            return False
        
        time.sleep(2)
        
        # Test turning light off
        logger.info("Turning light OFF...")
        success = light.turn_off()
        if success:
            logger.info("✅ Light turned OFF successfully")
        else:
            logger.error("❌ Failed to turn light OFF")
            return False
        
        time.sleep(1)
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic light control test failed: {e}")
        return False

def test_color_changes(logger, light):
    """Test color changing functionality."""
    logger.info("=" * 50)
    logger.info("Testing Color Changes")
    logger.info("=" * 50)
    
    if not light:
        logger.error("❌ No light object available for testing")
        return False
    
    colors = [
        ("Red", 255, 0, 0),
        ("Green", 0, 255, 0),
        ("Blue", 0, 0, 255),
        ("Yellow", 255, 255, 0),
        ("Purple", 255, 0, 255),
        ("Cyan", 0, 255, 255),
        ("White", 255, 255, 255),
        ("Orange", 255, 165, 0),
        ("Pink", 255, 192, 203),
        ("Lime", 191, 255, 0)
    ]
    
    try:
        logger.info("Testing various colors...")
        logger.info("⚠️  Watch your light for color changes!")
        
        for color_name, red, green, blue in colors:
            logger.info(f"Setting color to {color_name} (RGB: {red}, {green}, {blue})...")
            success = light.set_color(red, green, blue)
            if success:
                logger.info(f"✅ {color_name} color set successfully")
            else:
                logger.warning(f"⚠️ Failed to set {color_name} color")
            
            time.sleep(1.5)  # Wait to see the color change
        
        # Turn off at the end
        light.turn_off()
        logger.info("✅ Color testing completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Color change test failed: {e}")
        return False

def test_halloween_sequence_colors(logger, light):
    """Test the Halloween sequence color pattern."""
    logger.info("=" * 50)
    logger.info("Testing Halloween Sequence Colors")
    logger.info("=" * 50)
    
    if not light:
        logger.error("❌ No light object available for testing")
        return False
    
    try:
        logger.info("Running Halloween sequence color pattern...")
        logger.info("This simulates the actual Halloween barrel sequence!")
        
        # Phase 1: Yellow Warning
        logger.info("Phase 1: Yellow warning phase...")
        light.set_color(255, 255, 0)  # Yellow
        light.turn_on()
        time.sleep(3)
        
        # Phase 2: Green Preparation
        logger.info("Phase 2: Green preparation phase...")
        light.set_color(0, 255, 0)  # Green
        time.sleep(2)
        
        # Phase 3: Red Pump Activation
        logger.info("Phase 3: Red pump activation phase...")
        light.set_color(255, 0, 0)  # Red
        time.sleep(4)
        
        # Phase 4: Off
        logger.info("Phase 4: Completion phase...")
        light.turn_off()
        time.sleep(1)
        
        logger.info("✅ Halloween sequence color test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Halloween sequence test failed: {e}")
        return False

def test_flash_effects(logger, light):
    """Test flash effects."""
    logger.info("=" * 50)
    logger.info("Testing Flash Effects")
    logger.info("=" * 50)
    
    if not light:
        logger.error("❌ No light object available for testing")
        return False
    
    try:
        logger.info("Testing flash effects...")
        logger.info("⚠️  Watch your light for flashing!")
        
        # Set to red before flashing
        light.set_color(255, 0, 0)
        light.turn_on()
        time.sleep(1)
        
        # Test flash effect
        logger.info("Starting flash effect (10 flashes)...")
        success = light.flash(10, 0.3)  # 10 flashes, 0.3 second delay
        if success:
            logger.info("✅ Flash effect completed successfully")
        else:
            logger.warning("⚠️ Flash effect had some issues")
        
        # Turn off
        light.turn_off()
        return True
        
    except Exception as e:
        logger.error(f"❌ Flash effects test failed: {e}")
        return False

def test_error_handling(logger):
    """Test error handling with invalid IP addresses."""
    logger.info("=" * 50)
    logger.info("Testing Error Handling")
    logger.info("=" * 50)
    
    try:
        # Test with invalid IP
        logger.info("Testing with invalid IP address...")
        invalid_light = GoveeLight("192.168.1.999")
        
        # Try to turn on (should fail gracefully)
        success = invalid_light.turn_on()
        if not success:
            logger.info("✅ Invalid IP handled gracefully - light did not turn on")
        else:
            logger.warning("⚠️ Unexpected: Invalid IP seemed to work")
        
        # Test with unreachable IP
        logger.info("Testing with unreachable IP address...")
        unreachable_light = GoveeLight("192.168.1.200")
        
        success = unreachable_light.turn_on()
        if not success:
            logger.info("✅ Unreachable IP handled gracefully - light did not turn on")
        else:
            logger.warning("⚠️ Unexpected: Unreachable IP seemed to work")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error handling test failed: {e}")
        return False

def test_connection_stability(logger, light):
    """Test connection stability over time."""
    logger.info("=" * 50)
    logger.info("Testing Connection Stability")
    logger.info("=" * 50)
    
    if not light:
        logger.error("❌ No light object available for testing")
        return False
    
    try:
        logger.info("Testing connection stability for 30 seconds...")
        logger.info("This will send commands every 2 seconds...")
        
        start_time = time.time()
        command_count = 0
        success_count = 0
        
        while time.time() - start_time < 30:
            # Alternate between different colors
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
            color = colors[command_count % len(colors)]
            
            success = light.set_color(*color)
            command_count += 1
            
            if success:
                success_count += 1
                logger.info(f"Command {command_count}: Color set successfully")
            else:
                logger.warning(f"Command {command_count}: Color set failed")
            
            time.sleep(2)
        
        # Calculate success rate
        success_rate = (success_count / command_count * 100) if command_count > 0 else 0
        logger.info(f"Connection stability test complete: {success_count}/{command_count} commands successful ({success_rate:.1f}%)")
        
        # Turn off
        light.turn_off()
        
        return success_rate > 80  # Consider successful if >80% commands work
        
    except Exception as e:
        logger.error(f"❌ Connection stability test failed: {e}")
        return False

def run_interactive_test(logger, light):
    """Run an interactive test where user can control the light."""
    logger.info("=" * 50)
    logger.info("Interactive Light Control")
    logger.info("=" * 50)
    
    if not light:
        logger.error("❌ No light object available for testing")
        return False
    
    try:
        logger.info("Interactive light control started.")
        logger.info("Commands:")
        logger.info("  'on' - Turn light on")
        logger.info("  'off' - Turn light off")
        logger.info("  'red', 'green', 'blue', 'yellow', 'purple', 'white' - Set colors")
        logger.info("  'flash' - Flash 5 times")
        logger.info("  'test' - Run Halloween sequence")
        logger.info("  'q' - Quit interactive test")
        
        while True:
            try:
                command = input("\nEnter command: ").strip().lower()
                
                if command == 'q':
                    logger.info("Exiting interactive test...")
                    break
                elif command == 'on':
                    light.turn_on()
                    logger.info("Light turned ON")
                elif command == 'off':
                    light.turn_off()
                    logger.info("Light turned OFF")
                elif command == 'red':
                    light.set_color(255, 0, 0)
                    light.turn_on()
                    logger.info("Set to RED")
                elif command == 'green':
                    light.set_color(0, 255, 0)
                    light.turn_on()
                    logger.info("Set to GREEN")
                elif command == 'blue':
                    light.set_color(0, 0, 255)
                    light.turn_on()
                    logger.info("Set to BLUE")
                elif command == 'yellow':
                    light.set_color(255, 255, 0)
                    light.turn_on()
                    logger.info("Set to YELLOW")
                elif command == 'purple':
                    light.set_color(255, 0, 255)
                    light.turn_on()
                    logger.info("Set to PURPLE")
                elif command == 'white':
                    light.set_color(255, 255, 255)
                    light.turn_on()
                    logger.info("Set to WHITE")
                elif command == 'flash':
                    light.flash(5, 0.5)
                    logger.info("Flash effect completed")
                elif command == 'test':
                    logger.info("Running Halloween sequence...")
                    test_halloween_sequence_colors(logger, light)
                else:
                    logger.info("Invalid command. Try: on, off, red, green, blue, yellow, purple, white, flash, test, q")
                    
            except KeyboardInterrupt:
                logger.info("\nExiting interactive test...")
                break
            except Exception as e:
                logger.error(f"Error during interactive test: {e}")
        
        # Turn off light before exiting
        light.turn_off()
        return True
        
    except Exception as e:
        logger.error(f"❌ Interactive test failed: {e}")
        return False

def main():
    """Main test function."""
    logger = setup_logging()
    
    logger.info("🎃 Halloween Barrel Govee Light Test")
    logger.info("=" * 60)
    logger.info("This script will test the Govee light functionality.")
    logger.info("Make sure your Govee light is connected to WiFi!")
    logger.info("=" * 60)
    
    # Get IP address from user
    default_ip = "192.168.1.212"
    ip_input = input(f"Enter Govee light IP address (default: {default_ip}): ").strip()
    ip_address = ip_input if ip_input else default_ip
    
    logger.info(f"Using IP address: {ip_address}")
    
    # Test results
    test_results = []
    
    # Initialize light
    light = test_light_initialization(logger, ip_address)
    if not light:
        logger.error("❌ Cannot proceed without working light connection")
        return 1
    
    # Run all tests
    test_results.append(("Basic Control", test_basic_light_control(logger, light)))
    test_results.append(("Color Changes", test_color_changes(logger, light)))
    test_results.append(("Halloween Sequence", test_halloween_sequence_colors(logger, light)))
    test_results.append(("Flash Effects", test_flash_effects(logger, light)))
    test_results.append(("Error Handling", test_error_handling(logger)))
    test_results.append(("Connection Stability", test_connection_stability(logger, light)))
    
    # Ask user if they want to run interactive test
    logger.info("\n" + "=" * 60)
    response = input("Do you want to run interactive test? (y/n): ").strip().lower()
    
    if response == 'y':
        test_results.append(("Interactive Test", run_interactive_test(logger, light)))
    else:
        logger.info("Skipping interactive test as requested.")
    
    # Clean up
    try:
        light.turn_off()
        light.close()
        logger.info("Light connection closed")
    except Exception as e:
        logger.warning(f"Error closing light connection: {e}")
    
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
        logger.info("🎉 All tests passed! Govee light is working correctly.")
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
