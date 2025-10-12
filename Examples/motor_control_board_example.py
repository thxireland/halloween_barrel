import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)

# Motor control board GPIO pins
FORWARD_PIN = 5  # GPIO pin for forward movement
REVERSE_PIN = 6  # GPIO pin for reverse movement

# Set up motor control pins as outputs
GPIO.setup(FORWARD_PIN, GPIO.OUT)
GPIO.setup(REVERSE_PIN, GPIO.OUT)

# Ensure motor is stopped initially
GPIO.output(FORWARD_PIN, GPIO.LOW)
GPIO.output(REVERSE_PIN, GPIO.LOW)

def move_forward(duration=2.0):
    """Move actuator forward for specified duration."""
    print(f"Moving forward for {duration} seconds...")
    GPIO.output(REVERSE_PIN, GPIO.LOW)  # Ensure reverse is off
    GPIO.output(FORWARD_PIN, GPIO.HIGH)  # Turn on forward
    time.sleep(duration)
    GPIO.output(FORWARD_PIN, GPIO.LOW)  # Stop motor
    print("Forward movement complete")

def move_reverse(duration=2.0):
    """Move actuator reverse for specified duration."""
    print(f"Moving reverse for {duration} seconds...")
    GPIO.output(FORWARD_PIN, GPIO.LOW)  # Ensure forward is off
    GPIO.output(REVERSE_PIN, GPIO.HIGH)  # Turn on reverse
    time.sleep(duration)
    GPIO.output(REVERSE_PIN, GPIO.LOW)  # Stop motor
    print("Reverse movement complete")

def stop_motor():
    """Stop the motor immediately."""
    print("Stopping motor...")
    GPIO.output(FORWARD_PIN, GPIO.LOW)
    GPIO.output(REVERSE_PIN, GPIO.LOW)

def halloween_barrel_sequence():
    """Execute a spooky barrel opening sequence."""
    print("Starting Halloween barrel sequence...")
    
    # 1. Quick peek to build anticipation
    print("Peek...")
    move_forward(1.0)  # Quick forward movement
    time.sleep(1.5)
    
    # 2. Close back down
    print("Closing...")
    move_reverse(1.0)  # Quick reverse movement
    time.sleep(2.0)
    
    # 3. Dramatic full open
    print("BOO! Full open!")
    move_forward(2.0)  # Longer forward movement
    time.sleep(3.0)
    
    # 4. Close for next cycle
    print("Closing for next victim...")
    move_reverse(2.0)  # Longer reverse movement
    time.sleep(2.0)
    
    print("Barrel sequence complete!")

def simple_test():
    """Simple forward/reverse test."""
    try:
        print("=== Linear Actuator Simple Test ===")
        print("Press Ctrl+C to stop")
        
        while True:
            print("\nChoose action:")
            print("1. Move forward (2 seconds)")
            print("2. Move reverse (2 seconds)")
            print("3. Halloween barrel sequence")
            print("4. Stop motor")
            print("5. Exit")
            
            choice = input("Enter choice (1-5): ").strip()
            
            if choice == "1":
                move_forward(2.0)
            elif choice == "2":
                move_reverse(2.0)
            elif choice == "3":
                halloween_barrel_sequence()
            elif choice == "4":
                stop_motor()
            elif choice == "5":
                break
            else:
                print("Invalid choice, please try again")
                
    except KeyboardInterrupt:
        print("\nTest stopped by user.")
    finally:
        stop_motor()
        GPIO.cleanup()  # Clean up the GPIO pins on exit

# Run the simple test
halloween_barrel_sequence()