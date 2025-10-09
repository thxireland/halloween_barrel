import RPi.GPIO as GPIO
import time

# Set up GPIO
GPIO.setmode(GPIO.BCM)
TRIG = 24
ECHO = 23

# Set up Trigger and Echo pins
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def measure_distance():
    # Send a pulse to trigger the sensor
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.5)
    GPIO.output(TRIG, GPIO.HIGH)
    time.sleep(0.00001)  # 10 microseconds
    GPIO.output(TRIG, GPIO.LOW)
    
    # Wait for Echo to go HIGH
    while GPIO.input(ECHO) == GPIO.LOW:
        pulse_start = time.time()
    
    # Wait for Echo to go LOW
    while GPIO.input(ECHO) == GPIO.HIGH:
        pulse_end = time.time()
    
    # Calculate the time difference between the start and end of the pulse
    pulse_duration = pulse_end - pulse_start
    
    # Speed of sound is roughly 34300 cm/s, so calculate the distance
    distance = pulse_duration * 34300 / 2  # Distance in centimeters
    
    return distance

try:
    while True:
        distance = measure_distance()
        print(f"Distance: {distance:.2f} cm")
        time.sleep(1)

except KeyboardInterrupt:
    print("Measurement stopped by user.")
    GPIO.cleanup()  # Clean up the GPIO pins on exit
