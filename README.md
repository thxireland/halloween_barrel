# 🎃 Halloween Barrel Project

An automated Halloween barrel display that uses ultrasonic sensors to detect approaching trick-or-treaters and triggers a spooky sequence including skeleton movement, smoke effects, water spray, lighting, and music.

## 🌟 Features

- **Dual Ultrasonic Sensors** - Reliable object detection with validation
- **Automated Skeleton Movement** - Linear actuator controls skeleton leaning over barrel
- **Smoke Effects** - Atmospheric fog machine control
- **Water Spray** - Skeleton "getting sick" effect through mouth
- **Smart Lighting** - Govee light integration (optional)
- **Halloween Music** - MP3 audio playback (optional)
- **Comprehensive Logging** - Detailed operation tracking
- **Safety Features** - Emergency stop, cooldown periods, health monitoring
- **YAML Configuration** - Easy customization without code changes

## 🛠️ Hardware Requirements

### Required Components
- Raspberry Pi (any model with GPIO)
- 2x HC-SR04 Ultrasonic Sensors
- Linear Actuator or DC Motor with Motor Control Board
- 2x Relay Modules (5V)
- Smoke Machine
- Water Pump
- Power supplies for all components

### Optional Components
- Govee Smart Light (WiFi)
- Audio system with MP3 playback capability

### GPIO Pin Connections

| Component | Pin Type | GPIO Pin | Description |
|-----------|----------|----------|-------------|
| Motor | Forward | 18 | Skeleton leans forward over barrel |
| Motor | Reverse | 19 | Skeleton returns to resting position |
| Pump Relay | Control | 21 | Skeleton "getting sick" water effect |
| Smoke Relay | Control | 20 | Smoke machine relay control |
| Ultrasonic 1 | Trigger | 24 | Sensor 1 trigger pin |
| Ultrasonic 1 | Echo | 23 | Sensor 1 echo pin |
| Ultrasonic 2 | Trigger | 7 | Sensor 2 trigger pin |
| Ultrasonic 2 | Echo | 8 | Sensor 2 echo pin |

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd halloween_barrel
```

### 2. Install Dependencies
```bash
pip install RPi.GPIO pygame pyyaml
```

### 3. Hardware Setup
1. Connect all components according to the GPIO pin table above
2. Ensure proper power supplies for all components
3. Test each component individually before running the full system

### 4. Configuration
Edit `configs.yaml` to match your setup:

```yaml
# Example configuration
distance_thresholds:
  warning: 100.0    # cm - object approaching
  trigger: 50.0     # cm - execute sequence
  minimum_valid: 2.0
  maximum_valid: 400.0

timing:
  motor_forward_duration: 2.5
  motor_reverse_duration: 2.5
  smoke_delay: 0.5
  smoke_duration: 1.0
  pump_duration: 6.0
  cooldown_duration: 10.0

hardware:
  motor_pins:
    forward: 18
    reverse: 19
  pump_relay_pin: 21
  smoke_relay_pin: 20
  # ... more settings
```

### 5. Optional Components Setup

#### Govee Light
1. Connect your Govee light to WiFi
2. Find the device IP address in your router settings
3. Enable and configure in `configs.yaml`:
```yaml
optional_components:
  govee_light:
    enabled: true
    ip_address: "192.168.1.100"  # Your light's IP
    port: 4003
```

#### Music Player
1. Place your Halloween audio file in the project directory
2. Configure in `configs.yaml`:
```yaml
optional_components:
  music_player:
    enabled: true
    audio_file: "/path/to/halloween_sound.mp3"
    volume: 0.7
```

## 🚀 Usage

### Basic Operation
```bash
python main.py
```

The system will:
1. Load configuration from `configs.yaml`
2. Initialize and test all hardware components
3. Start monitoring for approaching objects
4. Execute Halloween sequence when triggered
5. Log all operations to console and `halloween_barrel.log`

### Graceful Shutdown
- Press `Ctrl+C` to stop the system safely
- All components will be properly shut down
- Logs will be saved

## ⚙️ Configuration Reference

### Distance Thresholds
- `warning`: Distance (cm) for approach warning
- `trigger`: Distance (cm) to execute Halloween sequence
- `minimum_valid`: Minimum reliable sensor reading
- `maximum_valid`: Maximum reliable sensor reading

### Timing Settings
- `motor_forward_duration`: How long skeleton leans forward over barrel (seconds)
- `motor_reverse_duration`: How long skeleton returns to resting position (seconds)
- `smoke_delay`: Delay before smoke activation (seconds)
- `smoke_duration`: How long smoke runs (seconds)
- `pump_duration`: How long water pump runs (seconds)
- `cooldown_duration`: Minimum time between sequences (seconds)
- `reading_interval`: Time between distance readings (seconds)

### Validation Settings
- `consecutive_readings`: Number of readings for consistency check
- `reading_tolerance`: Tolerance for reading consistency (cm)
- `max_failed_readings`: Max failures before system error

### Hardware Configuration
All GPIO pins can be reconfigured in the `hardware` section. Use BCM pin numbering.

### Logging Configuration
- `level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `file`: Log file path
- `console`: Enable console output

### Safety Settings
- `emergency_stop_enabled`: Enable emergency stop functionality
- `max_sequence_duration`: Maximum time for a sequence (seconds)
- `auto_cleanup_on_error`: Auto cleanup on errors

## 🔧 Troubleshooting

### Common Issues

#### "Configuration file not found"
- Ensure `configs.yaml` exists in the project directory
- Check file permissions

#### "Invalid YAML in config file"
- Validate YAML syntax using an online YAML validator
- Check for proper indentation (use spaces, not tabs)

#### "Hardware initialization failed"
- Verify all GPIO connections
- Check power supplies
- Ensure components are properly connected

#### "Ultrasonic sensor failed test"
- Check sensor connections (trigger and echo pins)
- Verify sensor power supply (5V)
- Clean sensor faces
- Check for obstructions

#### "Motor not responding"
- Verify motor control board connections
- Check motor power supply
- Test motor control board independently

#### "Relay not activating"
- Check relay power supply
- Verify relay control signal
- Test relay with multimeter

### Debug Mode
Enable debug logging by setting in `configs.yaml`:
```yaml
logging:
  level: "DEBUG"
```

### Log Files
Check `halloween_barrel.log` for detailed operation logs and error messages.

## 🔒 Safety Considerations

- **Electrical Safety**: Ensure all connections are secure and properly insulated
- **Water Safety**: Use appropriate water pump and ensure electrical connections are protected from moisture
- **Mechanical Safety**: Ensure skeleton movement area is clear and secure
- **Emergency Stop**: System includes automatic emergency stop functionality
- **Cooldown Periods**: Built-in delays prevent rapid-fire triggering

## 📁 Project Structure

```
halloween_barrel/
├── main.py                 # Main application
├── configs.yaml           # Configuration file
├── README.md              # This file
├── halloween_barrel.log   # Log file (created at runtime)
└── plugins/               # Hardware plugin modules
    ├── motor.py           # Motor control
    ├── ultrasonic.py      # Ultrasonic sensor control
    ├── relay.py           # Relay control
    ├── govee_plugin.py    # Govee light control
    └── music_player.py    # Audio playback
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Please ensure you follow all local regulations and safety guidelines when building and operating this Halloween display.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the log files for error messages
3. Verify your hardware connections and configuration
4. Create an issue in the repository with detailed information

---

**Happy Halloween! 🎃👻**

*Remember to test your setup in a safe environment before Halloween night!*
