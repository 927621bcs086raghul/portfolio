# 🤖 Robot AI Brain - Real-Time Autonomous Navigation Engine

A complete AI control system for autonomous robots using ESP32, ultrasonic sensors, encoder wheels, and motor drivers. Features real-time decision-making, obstacle avoidance, and conversational AI interface.

---

## 📋 Project Structure

```
VR 47 2/
├── app.py              # Streamlit chatbot web interface
├── backend.py          # Flask REST API server
├── robot_brain.py      # Core AI navigation logic
├── config.py           # Hardware pins & parameters
├── requirements.txt    # Python dependencies
└── README.md           # This file
```

---

## 🛠️ Hardware Setup

### Components Required
- **Microcontroller**: ESP32
- **Motor Driver**: L298N or L293D
- **Motors**: 2x DC Motors (left & right wheels)
- **Ultrasonic Sensors**: 3x HC-SR04 sensors (front, left, right)
- **Encoder Wheel**: Slotted wheel with encoder (20 slots)
- **Power**: 5V/12V supply for motors, 5V for ESP32

### GPIO Pin Configuration (ESP32)

| Component | Pin | Function |
|-----------|-----|----------|
| Motor A PWM | GPIO25 | Left motor speed |
| Motor A IN1 | GPIO27 | Left motor direction |
| Motor A IN2 | GPIO26 | Left motor direction |
| Motor B PWM | GPIO12 | Right motor speed |
| Motor B IN1 | GPIO14 | Right motor direction |
| Motor B IN2 | GPIO13 | Right motor direction |
| Ultrasonic Front TRIG | GPIO5 | Front sensor trigger |
| Ultrasonic Front ECHO | GPIO18 | Front sensor echo |
| Ultrasonic Left TRIG | GPIO19 | Left sensor trigger |
| Ultrasonic Left ECHO | GPIO21 | Left sensor echo |
| Ultrasonic Right TRIG | GPIO23 | Right sensor trigger |
| Ultrasonic Right ECHO | GPIO22 | Right sensor echo |
| Encoder | GPIO4 | Interrupt pin |

Configure these in [config.py](config.py) under `PinConfig` class.

---

## 🚀 Installation & Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Hardware (ESP32 Code)

Write ESP32 firmware to:
1. Read ultrasonic sensor data
2. Count encoder pulses
3. Send data to Flask API via POST request to `http://robot-ip:5000/api/robot/decide`
4. Receive navigation decision and control motors

**Example ESP32 POST Request** (pseudocode):
```cpp
// Read sensors
float frontDist = getUltrasonic(TRIG_FRONT, ECHO_FRONT);
float leftDist = getUltrasonic(TRIG_LEFT, ECHO_LEFT);
float rightDist = getUltrasonic(TRIG_RIGHT, ECHO_RIGHT);
int pulses = pulseCount;

// Send to Flask API
HTTPClient http;
http.begin("http://robot-ip:5000/api/robot/decide");
http.addHeader("Content-Type", "application/json");

String payload = "{\"front_dist\":" + String(frontDist) + 
                 ",\"left_dist\":" + String(leftDist) +
                 ",\"right_dist\":" + String(rightDist) +
                 ",\"encoder_pulses\":" + String(pulses) + "}";

int code = http.POST(payload);
String response = http.getString();  // Get decision

// Parse JSON and control motors
```

---

## 💻 Running the System

### Option 1: Start Backend First, Then Frontend

**Terminal 1** - Start Flask API Server:
```bash
python backend.py
```
Output:
```
================================================================================
ROBOT AI BRAIN - FLASK SERVER
================================================================================
Starting API server on 0.0.0.0:5000

Available endpoints:
  POST   /api/robot/decide      - Get navigation decision
  GET    /api/robot/status      - Get robot status
  GET    /api/robot/config      - Get hardware config
  POST   /api/robot/reset       - Reset robot state
  POST   /api/chat/ask          - Ask robot questions
  GET    /api/health            - Health check
================================================================================
```

**Terminal 2** - Start Streamlit Chatbot UI:
```bash
streamlit run app.py
```
Output:
```
You can now view your Streamlit app in your browser.

  URL: http://localhost:8501
```

### Access the UI
- **Chatbot Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:5000

---

## 📡 API Endpoints

### 1. Send Sensor Data & Get Decision
**Endpoint**: `POST /api/robot/decide`

**Request:**
```json
{
    "front_dist": 45.2,
    "left_dist": 60.0,
    "right_dist": 35.5,
    "encoder_pulses": 1240,
    "stage": "A→B",
    "target_distance": 100
}
```

**Response:**
```json
{
    "decision": "FORWARD",
    "speed": 180,
    "motor_left_speed": 180,
    "motor_right_speed": 180,
    "motor_left_direction": "FWD",
    "motor_right_direction": "FWD",
    "explanation": "✓ ALL PATHS CLEAR! Front: 45.2cm, Left: 60.0cm, Right: 35.5cm. Moving FORWARD at 180 PWM.",
    "current_stage": "A→B",
    "encoder_distance": 45.0,
    "decision_number": 1,
    "timestamp": "2026-02-11T12:34:56.789",
    "status": "success"
}
```

### 2. Get Robot Status
**Endpoint**: `GET /api/robot/status`

Returns current sensor readings, decision history, and stage tracking.

### 3. Get Hardware Configuration
**Endpoint**: `GET /api/robot/config`

Returns GPIO pin mapping, safety thresholds, encoder specifications.

### 4. Chat with Robot
**Endpoint**: `POST /api/chat/ask`

```json
{
    "question": "Left free aa? Right free aa?"
}
```

### 5. Reset Robot Brain
**Endpoint**: `POST /api/robot/reset`

Clears all state and decision history.

---

## 🤖 AI Decision Logic

The robot makes intelligent navigation decisions based on:

### Decision Tree
```
1. Check Front obstacle
   ├─ BLOCKED (≤ 15cm) → STOP (emergency)
   ├─ CAUTION (15-30cm) → FORWARD SLOW
   └─ CLEAR (> 30cm) → Continue to step 2

2. Check Destination Reached
   └─ If encoded distance ≥ target → STOP (arrived)

3. Compare Left vs Right Paths
   ├─ Both CLEAR → Go STRAIGHT
   ├─ Front blocked, Left/Right clear → TURN to wider path
   ├─ Only LEFT clear → TURN LEFT
   ├─ Only RIGHT clear → TURN RIGHT
   └─ All BLOCKED → STOP (reevaluate)
```

### Safety Thresholds (configurable)
- **Safe Distance**: 30cm (maintain minimum)
- **Critical Distance**: 15cm (emergency stop)
- **Follow Distance**: 25cm (optimal cruising)

---

## 💬 Conversational AI Features

The chatbot responds to natural language queries like:

### Supported Questions
1. **"Obstacle irukku na?"** (Tamil: Are there obstacles?)
   → Lists status of front, left, right sensors

2. **"Left free aa? Right free aa?"** (Tamil: Is left path free? Is right path free?)
   → Compares left vs right distances, recommends best path

3. **"A→B ku pona distance correct ah?"** (Tamil: Is A→B distance correct?)
   → Verifies encoder distance against target

4. **Hardware questions**: "Show me GPIO pins", "What's the encoder specification?"
   → Returns hardware configuration

5. **Custom questions**: Any question about robot state
   → Returns real-time sensor data interpretation

---

## 📊 Streamlit Dashboard Features

### Tab 1: 💬 Chat
- Conversational AI interface
- Quick preset questions (Tamil support)
- Full chat history
- Real-time responses

### Tab 2: 📊 Sensor Dashboard
- Real-time ultrasonic readings with smoothed values
- Encoder wheel distance tracking
- Navigation stage indicator
- Decision history
- Full status JSON display

### Tab 3: 🎮 Manual Control
- Manual sensor input sliders
- Test AI decision engine
- Motor command output
- Detailed reasoning explanation
- Full JSON response viewer

---

## ⚙️ Configuration Guide

Edit [config.py](config.py) to customize:

### 1. Distance Thresholds
```python
class SafetyConfig:
    SAFE_DISTANCE = 30      # Minimum safe distance (cm)
    CRITICAL_DISTANCE = 15  # Emergency stop distance (cm)
```

### 2. Motor Speeds
```python
class MotorConfig:
    SPEED_FULL = 255    # Full speed (0-255 PWM)
    SPEED_NORMAL = 180  # Normal speed
    SPEED_SLOW = 100    # Slow for caution
```

### 3. Encoder Wheel
```python
class EncoderConfig:
    WHEEL_DIAMETER_CM = 6.5   # Physical diameter
    ENCODER_SLOTS = 20         # Slots in encoder wheel
```

### 4. Navigation Targets
```python
class NavigationConfig:
    STAGE_A_TARGET_DISTANCE = 100  # To reach B
    STAGE_B_TARGET_DISTANCE = 50   # To reach C
```

---

## 🐛 Troubleshooting

### API Server Won't Start
```bash
# Check if port 5000 is already in use
netstat -ano | findstr :5000

# Kill process using port 5000
taskkill /PID <PID> /F

# Or use different port in config.py
```

### Streamlit Connection Error
```bash
# Verify Flask server is running
curl http://localhost:5000/api/health

# Check network connectivity
ping localhost
```

### Incorrect Sensor Readings
1. Check GPIO pin connections in hardware
2. Verify pin numbers in [config.py](config.py)
3. Test sensors independently with serial monitor

### Motor Not Moving
1. Verify motor driver power supply (check GND connection)
2. Test motor with direct power (+5V/+12V)
3. Check GPIO pin output with multimeter
4. Verify PWM frequency in config

### Encoder Distance Incorrect
1. Measure actual wheel circumference: π × diameter
2. Count actual encoder slots (rotate wheel and count pulses)
3. Adjust `WHEEL_DIAMETER_CM` and `ENCODER_SLOTS` in config

---

## 📚 Files Overview

| File | Purpose |
|------|---------|
| [config.py](config.py) | Hardware pins, thresholds, parameters |
| [robot_brain.py](robot_brain.py) | AI navigation logic, decision engine |
| [backend.py](backend.py) | Flask API server for sensor data |
| [app.py](app.py) | Streamlit chatbot web interface |
| [requirements.txt](requirements.txt) | Python dependencies |

---

## 🔄 Data Flow

```
ESP32 Robot (Sensor Data)
        ↓
        ├─→ POST /api/robot/decide
        ↓
    Flask Backend (Decision Engine)
        ↓
        ├─→ Parse Sensor Data
        ├─→ Run AI Brain Logic
        ├─→ Generate Decision & Explanation
        ↓
        └─→ JSON Response (Motor Commands)
        ↓
ESP32 Robot (Execute Motors)

Streamlit UI ←─→ Flask API (Chat, Status, Config)
```

---

## 📝 Example Workflow

### Navigation Scenario
```
1. Robot starts at Point A
2. User sets target: "Navigate to Point B (100cm away)"
3. Every 100ms, ESP32 sends:
   - Front distance: 45cm, Left: 60cm, Right: 52cm
   - Encoder pulses: 523 (45cm traveled)
   
4. Flask decides: "FORWARD at 180 PWM"
   (All paths clear, moving toward target)
   
5. Streamlit shows:
   - Real-time sensor values
   - Decision: FORWARD
   - Distance progress: 45cm / 100cm
   - Explanation: "✓ ALL PATHS CLEAR!"
   
6. When encoder reaches 100cm → Auto-STOP at Point B
```

---

## 🎯 Future Enhancements

- [ ] Add PID controller for precision movement
- [ ] Implement path memory (avoid previously hit obstacles)
- [ ] Add camera vision integration
- [ ] Support for circular path navigation
- [ ] Data logging to CSV for analysis
- [ ] Multi-robot coordination
- [ ] GPS support for outdoor navigation

---

## 📄 License

Open source for robotics education. Use freely for learning and development.

---

## 👨‍💻 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Verify hardware connections and GPIO pins
3. Run `python config.py` to print all configuration
4. Test API endpoints individually with curl/Postman

---

**Ready to navigate! 🚀** Start the backend and Streamlit servers to begin controlling your robot in real-time.
