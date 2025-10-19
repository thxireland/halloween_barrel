# 🔌 Halloween Barrel Wiring Diagram

## Raspberry Pi 5 Halloween Barrel Project - Complete Wiring Guide

This diagram shows the complete wiring setup for the Halloween barrel project using a Raspberry Pi 5, including the linear actuator skeleton, water pump, smoke machine, black light, and ultrasonic sensors.

## 📋 Components Overview

- **Raspberry Pi 5** - Main controller
- **Linear Actuator** - Moves skeleton to lean over barrel
- **Water Pump** - Pumps water through skeleton's mouth
- **Smoke Machine** - Creates atmospheric fog effects
- **Black Light** - UV lighting effect (mains powered)
- **2x Ultrasonic Sensors** - Distance detection
- **2x Relay Modules** - Control pump and smoke machine
- **Motor Control Board** - Controls linear actuator

---

## 🔌 Raspberry Pi 5 GPIO Pinout

```
                    Raspberry Pi 5 GPIO Layout
    ┌─────────────────────────────────────────────────────────────┐
    │  3V3  │ 5V   │ GPIO2 │ 5V   │ GPIO3 │ GND  │ GPIO4 │ 14 │
    │   GND  │ GPIO14│ GND  │ GPIO15│ GPIO18│ GND  │ GPIO23│ 24 │
    │ GPIO10│ GPIO9 │ GPIO11│ GND  │ GPIO25│ GPIO8 │ GND  │ GPIO7│
    │   GND  │ GPIO5 │ GPIO6 │ GPIO12│ GND  │ GPIO13│ GPIO19│ GND │
    │ GPIO16│ GPIO26│ GPIO20│ GND  │ GPIO21│ GPIO27│ GPIO22│ 3V3 │
    └─────────────────────────────────────────────────────────────┘
```

---

## 🔗 Complete Wiring Diagram

### Power Connections
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   5V Power      │    │   12V Power     │    │   Mains Power   │
│   Supply        │    │   Supply        │    │   (120V/240V)   │
│   (for Pi)      │    │   (for Actuator)│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
    ┌─────────┐              ┌─────────┐              ┌─────────┐
    │  Pi 5V  │              │  Motor  │              │  Black  │
    │  Pin 2  │              │  Control│              │  Light  │
    │  Pin 4  │              │  Board  │              │         │
    └─────────┘              └─────────┘              └─────────┘
```

### Raspberry Pi 5 GPIO Connections

```
                    Raspberry Pi 5
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │  GPIO18 ────────────► Motor Control Board (Forward)        │
    │  GPIO19 ────────────► Motor Control Board (Reverse)        │
    │  GPIO20 ────────────► Smoke Relay Control Pin              │
    │  GPIO21 ────────────► Pump Relay Control Pin               │
    │  GPIO23 ────────────► Ultrasonic 1 Echo Pin                │
    │  GPIO24 ────────────► Ultrasonic 1 Trigger Pin             │
    │  GPIO7  ────────────► Ultrasonic 2 Trigger Pin             │
    │  GPIO8  ────────────► Ultrasonic 2 Echo Pin                │
    │  GND    ────────────► All Component Grounds                 │
    │  5V     ────────────► Relay Module VCC (if 5V relays)      │
    │  3.3V   ────────────► Ultrasonic Sensors VCC               │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
```

---

## 🎭 Component Details

### 1. Linear Actuator & Skeleton
```
Motor Control Board
┌─────────────────────┐
│  VCC    GND   IN1   │
│   │      │     │    │
│   ▼      ▼     ▼    │
│  12V    GND  GPIO18 │ ← Forward Control
│                     │
│  VCC    GND   IN2   │
│   │      │     │    │
│   ▼      ▼     ▼    │
│  12V    GND  GPIO19 │ ← Reverse Control
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Linear Actuator   │
│                     │
│  Connected to       │
│  Skeleton Frame     │
└─────────────────────┘
```

### 2. Water Pump System
```
Pump Relay Module
┌─────────────────────┐
│  VCC  GND  IN   COM │
│   │    │    │    │  │
│   ▼    ▼    ▼    ▼  │
│  5V   GND GPIO21 NO │ ← Pump Control
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│    Water Pump       │
│                     │
│  Connected to       │
│  Skeleton's Mouth   │
│  (Spit Effect)      │
└─────────────────────┘
```

### 3. Smoke Machine System
```
Smoke Relay Module
┌─────────────────────┐
│  VCC  GND  IN   COM │
│   │    │    │    │  │
│   ▼    ▼    ▼    ▼  │
│  5V   GND GPIO20 NO │ ← Smoke Control
└─────────────────────┘
         │
         ▼
┌─────────────────────┐
│   Smoke Machine     │
│                     │
│  Connected to       │
│  External Switch    │
│  (Relay bypasses    │
│   manual switch)    │
└─────────────────────┘
```

### 4. Ultrasonic Sensors
```
Ultrasonic Sensor 1
┌─────────────────────┐
│  VCC  Trig Echo GND │
│   │     │     │    │
│   ▼     ▼     ▼    │
│  3.3V GPIO24 GPIO23│
└─────────────────────┘

Ultrasonic Sensor 2
┌─────────────────────┐
│  VCC  Trig Echo GND │
│   │     │     │    │
│   ▼     ▼     ▼    │
│  3.3V GPIO7  GPIO8 │
└─────────────────────┘
```

### 5. Black Light (Mains Powered)
```
Black Light Connection
┌─────────────────────┐
│   Mains Power       │
│   (120V/240V AC)    │
│                     │
│  Connected directly │
│  to wall outlet     │
│  (No Pi control)    │
└─────────────────────┘
```

---

## 🔌 Detailed Connection Table

| Component | Raspberry Pi Pin | Function | Notes |
|-----------|------------------|----------|-------|
| **Motor Control** | | | |
| Motor Forward | GPIO18 | Forward control | Controls actuator direction |
| Motor Reverse | GPIO19 | Reverse control | Controls actuator direction |
| Motor VCC | External 12V | Power supply | Use appropriate 12V supply |
| Motor GND | GND | Ground | Common ground |
| **Pump Relay** | | | |
| Pump Control | GPIO21 | Relay trigger | Controls water pump |
| Pump VCC | 5V | Relay power | If using 5V relay module |
| Pump GND | GND | Ground | Common ground |
| **Smoke Relay** | | | |
| Smoke Control | GPIO20 | Relay trigger | Controls smoke machine |
| Smoke VCC | 5V | Relay power | If using 5V relay module |
| Smoke GND | GND | Ground | Common ground |
| **Ultrasonic 1** | | | |
| Trigger | GPIO24 | Trigger signal | 10μs pulse to trigger |
| Echo | GPIO23 | Echo response | Measures echo duration |
| VCC | 3.3V | Sensor power | 5V compatible sensor |
| GND | GND | Ground | Common ground |
| **Ultrasonic 2** | | | |
| Trigger | GPIO7 | Trigger signal | 10μs pulse to trigger |
| Echo | GPIO8 | Echo response | Measures echo duration |
| VCC | 3.3V | Sensor power | 5V compatible sensor |
| GND | GND | Ground | Common ground |

---

## ⚡ Power Requirements

### Power Supplies Needed:
1. **5V Supply** - For Raspberry Pi 5 (3A recommended)
2. **12V Supply** - For linear actuator (check actuator specs)
3. **5V Supply** - For relay modules (if using 5V relays)
4. **Mains Power** - For black light, smoke machine, water pump

### Current Draw Estimates:
- Raspberry Pi 5: ~3A @ 5V
- Linear Actuator: Depends on model (check specs)
- Relay Modules: ~50-100mA @ 5V each
- Ultrasonic Sensors: ~15mA @ 3.3V each

---

## 🛡️ Safety Considerations

### Electrical Safety:
- Use appropriate fuses and circuit breakers
- Ensure all connections are properly insulated
- Use waterproof connections for outdoor components
- Follow local electrical codes for mains connections

### Mechanical Safety:
- Secure all mounting points
- Ensure linear actuator has proper end stops
- Test skeleton movement range before operation
- Use appropriate mounting hardware

### Water Safety:
- Use waterproof pump connections
- Ensure water lines are secure
- Consider water damage protection
- Use food-safe tubing for water lines

---

## 🔧 Assembly Notes

### Linear Actuator Installation:
1. Mount actuator to secure base
2. Connect skeleton frame to actuator arm
3. Ensure smooth movement range
4. Test full extension/retraction

### Water System Setup:
1. Connect pump to water reservoir
2. Run tubing to skeleton's mouth
3. Test water flow and pressure
4. Secure all connections

### Smoke Machine Setup:
1. Position smoke machine for optimal effect
2. Connect relay to external switch terminals
3. Test smoke output and timing
4. Ensure proper ventilation

### Sensor Placement:
1. Mount sensors at appropriate height
2. Angle sensors for optimal detection
3. Ensure clear line of sight
4. Test detection range and accuracy

---

## 🎃 Halloween Effect Sequence

When triggered, the system will:

1. **Detection** - Ultrasonic sensors detect approaching person
2. **Lighting** - Black light provides UV atmosphere
3. **Movement** - Linear actuator moves skeleton forward
4. **Smoke** - Smoke machine creates fog effect
5. **Water** - Pump sprays water through skeleton's mouth
6. **Return** - Skeleton returns to resting position
7. **Cooldown** - System waits before next activation

---

## 🔍 Troubleshooting

### Common Issues:
- **Actuator not moving**: Check 12V power and control signals
- **Pump not working**: Verify relay connections and water supply
- **Smoke not activating**: Check relay and smoke machine power
- **Sensors not detecting**: Verify wiring and sensor positioning
- **Pi not responding**: Check 5V power supply and connections

### Testing Procedures:
1. Test each component individually
2. Verify all power supplies are working
3. Check GPIO signals with multimeter
4. Test relay switching with LED indicators
5. Verify sensor readings in software

---

*Remember to test your setup in a safe environment before Halloween night! 🎃*
