from plugins.motor import Motor
from plugins.ultrasonic import UltrasonicSensor
from plugins.relay import Relay
from time import sleep

motor = Motor(18, 19)
pump_reply = Relay(21)
smoke_relay = Relay(20)
ultrasonic_sensor_1 = UltrasonicSensor(24, 23)
ultrasonic_sensor_2 = UltrasonicSensor(7, 8)

def get_shortest_distance():
    distance_1 = ultrasonic_sensor_1.get_distance()
    distance_2 = ultrasonic_sensor_2.get_distance()
    return min(distance_1, distance_2)

def main():
    while True:
        distance = get_shortest_distance()
        print(f"Distance: {distance} cm")
        if distance < 100:
            pass
        if distance < 50:
            motor.move_forward(2.5)
            sleep(.5)
            smoke_relay.on()
            sleep(1)
            pump_reply.on()
            sleep(1)
            smoke_relay.off()
            sleep(6)
            pump_reply.off()
            sleep(1)
            motor.move_reverse(2.5)
            sleep(2)

