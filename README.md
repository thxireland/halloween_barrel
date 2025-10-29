# 🎃 Halloween Barrel Project

An automated Halloween barrel display that uses ultrasonic sensors to detect approaching trick-or-treaters and triggers a spooky sequence including skeleton movement, smoke effects, water spray, lighting, and music. The entire sequence is configurable via YAML without requiring code changes.

## 🌟 Features

- **Ultrasonic Sensor Detection** - Reliable object detection for triggering sequences
- **Automated Skeleton Movement** - Linear actuator controls skeleton leaning over barrel
- **Smoke Effects** - Atmospheric fog machine control
- **Water Spray** - Skeleton "getting sick" effect through mouth
- **Smart Lighting** - Govee light integration with color changes and flashing effects
- **Halloween Music** - MP3 audio playback synchronized with effects
- **YAML-Based Configuration** - Easy sequence customization without code changes
- **Comprehensive Logging** - Detailed operation tracking
- **Sequential Action System** - Fully configurable action sequences

## 🛠️ Hardware Requirements

### Required Components
- Raspberry Pi (any model with GPIO)
- 1x HC-SR04 Ultrasonic Sensor
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
| Motor | Forward | 6 | Skeleton leans forward over barrel |
| Motor | Reverse | 5 | Skeleton returns to resting position |
| Pump Relay | Control | 21 | Skeleton "getting sick" water effect |
| Smoke Relay | Control | 20 | Smoke machine relay control |
| Ultrasonic | Trigger | 8 | Sensor trigger pin |
| Ultrasonic | Echo | 7 | Sensor echo pin |

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

### 4. Music Files Setup
Place your MP3 files in the `music_files/` directory:
- `vomit_1_sec.mp3`
- `vomit_2_sec.mp3`
- `vomit_4_sec.mp3`

You can add additional files and reference them in your sequence configuration.

### 5. Configuration

Edit `configs.yaml` to match your setup:

#### Basic Configuration
```yaml
# Distance thresholds
distance_thresholds:
  warning: 100.0    # cm - object approaching warning
  trigger: 50.0     # cm - execute Halloween sequence

# Hardware pins (BCM numbering)
hardware:
  motor_pins:
    forward: 6
    reverse: 5
  pump_relay_pin: 21
  smoke_relay_pin: 20
  ultrasonic_pins:
    trigger: 8
    echo: 7
  govee_light:
    ip_address: "192.168.1.212"  # Your Govee light IP
```

#### Govee Light Setup
1. Connect your Govee light to WiFi
2. Find the device IP address in your router settings
3. Configure in `configs.yaml`:
```yaml
hardware:
  govee_light:
    ip_address: "192.168.1.212"  # Your light's IP
```

## ⚙️ Sequence Configuration

The project uses a powerful YAML-based sequence system that allows you to configure all actions without modifying code.

### Action Types

#### Motor Actions
Control the linear actuator/skeleton movement:
```yaml
- type: motor
  action: forward    # Options: forward, reverse, stop
  duration: 4        # Duration in seconds (for forward/reverse)
```

#### Relay Actions
Control the pump and smoke machine:
```yaml
- type: relay
  name: pump         # Options: pump, smoke
  action: on         # Options: on, off
```

#### Light Actions
Control Govee light colors and effects:
```yaml
- type: light
  action: set_color  # Options: set_color, flash
  colour:
    r: 255           # Red (0-255)
    g: 0             # Green (0-255)
    b: 0             # Blue (0-255)

- type: light
  action: flash
  amount: 15         # Number of flashes
```

#### Music Actions
Play audio files:
```yaml
- type: music
  file: vomit_4_sec.mp3  # File name from music_files/ directory
  action: play
```

#### Sleep/Delay
Add delays between actions:
```yaml
- type: sleep
  duration: 0.5      # Duration in seconds
```

### Setup Sequence

The `setup_sequence` runs once at startup to initialize and test hardware. Configure it in `configs.yaml`:

```yaml
setup_sequence:
  - type: light
    action: set_color
    colour:
      r: 100
      g: 100
      b: 0
  - type: motor
    action: forward
    duration: 4
  - type: motor
    action: reverse
    duration: 2.5
  # ... more setup actions
```

### Trigger Sequence

The `sequence` executes when an object is detected within the trigger distance. Configure it in `configs.yaml`:

```yaml
sequence:
  - type: motor
    action: forward
    duration: 4
  - type: relay
    name: smoke
    action: on
  - type: sleep
    duration: 0.5
  # ... more trigger actions
```

### Complete Sequence Example

Here's an example trigger sequence:
```yaml
sequence:
  - type: motor
    action: forward
    duration: 4
  - type: relay
    name: smoke
    action: on
  - type: sleep
    duration: 0.5
  - type: relay
    name: smoke
    action: off
  - type: relay
    name: pump
    action: on
  - type: music
    file: vomit_4_sec.mp3
    action: play
  - type: light
    action: set_color
    colour:
      r: 0
      g: 255
      b: 0
  - type: light
    action: flash
    amount: 15
  # ... continue with more actions
```

## 🚀 Usage

### Basic Operation
```bash
python main.py
```

The system will:
1. Load configuration from `configs.yaml`
2. Execute the `setup_sequence` to initialize hardware
3. Start monitoring for approaching objects
4. Execute `sequence` when triggered by detection
5. Log all operations to console and `halloween_barrel.log`

### Graceful Shutdown
- Press `Ctrl+C` to stop the system safely
- All components will be properly shut down
- Logs will be saved

## 📋 Configuration Reference

### Distance Thresholds
- `warning`: Distance (cm) for approach warning (object detected but not triggering)
- `trigger`: Distance (cm) to execute Halloween sequence

### Hardware Configuration
All GPIO pins can be reconfigured in the `hardware` section. Use BCM pin numbering:
- `motor_pins`: Forward and reverse pin numbers
- `pump_relay_pin`: GPIO pin for pump relay
- `smoke_relay_pin`: GPIO pin for smoke relay
- `ultrasonic_pins`: Trigger and echo pin numbers
- `govee_light.ip_address`: IP address of Govee WiFi light

### Sequence Actions Reference

| Action Type | Parameters | Description |
|-------------|------------|-------------|
| `motor` | `action: forward/reverse/stop`, `duration` (seconds) | Control skeleton movement |
| `relay` | `name: pump/smoke`, `action: on/off` | Control pump or smoke machine |
| `light` | `action: set_color`, `colour: {r, g, b}` | Set light color (0-255 RGB) |
| `light` | `action: flash`, `amount` (number) | Flash light specified number of times |
| `music` | `file` (filename), `action: play` | Play audio file from music_files/ |
| `sleep` | `duration` (seconds) | Delay between actions |

### Logging Configuration
- `level`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `file`: Log file path
- `console`: Enable console output

## 🔧 Troubleshooting

### Common Issues

#### "Configuration file not found"
- Ensure `configs.yaml` exists in the project directory
- Check file permissions

#### "Invalid YAML in config file"
- Validate YAML syntax using an online YAML validator
- Check for proper indentation (use spaces, not tabs)
- Ensure all sequence items have required `type` field

#### "Unknown action type"
- Check that action type is one of: `motor`, `relay`, `light`, `music`, `sleep`
- Verify action parameters match the expected format

#### "Unknown relay name"
- Relay name must be either `pump` or `smoke`
- Check spelling and case sensitivity

#### "Unknown music file"
- Ensure MP3 file exists in `music_files/` directory
- Verify filename matches exactly (including extension)

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
- **Testing**: Always test sequences in a safe environment before Halloween night
- **Power Management**: Ensure adequate power supplies for all components

## 📁 Project Structure

```
halloween_barrel/
├── main.py                 # Main application
├── configs.yaml           # Configuration file (sequences, hardware, etc.)
├── README.md              # This file
├── halloween_barrel.log   # Log file (created at runtime)
├── music_files/           # Audio files directory
│   ├── vomit_1_sec.mp3
│   ├── vomit_2_sec.mp3
│   └── vomit_4_sec.mp3
└── plugins/               # Hardware plugin modules
    ├── motor.py           # Motor control
    ├── ultrasonic.py      # Ultrasonic sensor control
    ├── relay.py           # Relay control
    ├── govee_plugin.py    # Govee light control
    └── music_player.py    # Audio playback
```

## 🎨 Customizing Your Sequence

### Tips for Creating Effective Sequences

1. **Start with Movement**: Begin with skeleton movement to catch attention
2. **Layer Effects**: Combine multiple effects (smoke + music + lights) for maximum impact
3. **Timing is Key**: Use `sleep` actions to coordinate timing between effects
4. **Build Suspense**: Gradually increase intensity (smoke → lights → music → pump)
5. **Reset State**: End sequences by returning to initial state (motor reverse, lights reset)

### Example: Creating a New Sequence

1. Open `configs.yaml`
2. Locate the `sequence:` section
3. Add actions in the order you want them executed:
```yaml
sequence:
  - type: motor
    action: forward
    duration: 3
  - type: light
    action: set_color
    colour:
      r: 255
      g: 0
      b: 0
  # ... add more actions
```

4. Save and restart the program

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
4. Validate your YAML syntax
5. Create an issue in the repository with detailed information

---

**Happy Halloween! 🎃👻**

*Remember to test your setup and sequences in a safe environment before Halloween night!*
