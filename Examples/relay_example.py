import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)

# Relay GPIO pins
RELAY_PINS = [12, 16, 20, 21]

# Set up each relay pin as an output
for pin in RELAY_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Ensure relays are off initially

def toggle_relays():
    try:
        while True:
            # Loop through each relay and toggle it on/off
            for pin in RELAY_PINS:
                print(f"Turning relay on for pin {pin}")
                GPIO.output(pin, GPIO.HIGH)  # Turn the relay on
                time.sleep(1)  # Keep it on for 1 second
                
                print(f"Turning relay off for pin {pin}")
                GPIO.output(pin, GPIO.LOW)  # Turn the relay off
                time.sleep(1)  # Keep it off for 1 second

    except KeyboardInterrupt:
        print("Relay control stopped by user.")
        GPIO.cleanup()  # Clean up the GPIO pins on exit

# Run the relay control function
toggle_relays()
