# ============================================================================
# ROBOT AI BRAIN - Hardware Configuration & Control Parameters
# ============================================================================
# ESP32 Robot with Ultrasonic Sensors, Encoder Wheel, Motor Driver (L298N)
# ============================================================================

# ======================== ESP32 GPIO PIN MAPPING ==========================
class PinConfig:
    # Motor A (Left Motor)
    MOTOR_A_IN1 = 27  # GPIO27 - Motor A Direction Pin 1
    MOTOR_A_IN2 = 26  # GPIO26 - Motor A Direction Pin 2
    MOTOR_A_PWM = 25  # GPIO25 - Motor A Speed (PWM)
    
    # Motor B (Right Motor)
    MOTOR_B_IN1 = 14  # GPIO14 - Motor B Direction Pin 1
    MOTOR_B_IN2 = 13  # GPIO13 - Motor B Direction Pin 2
    MOTOR_B_PWM = 12  # GPIO12 - Motor B Speed (PWM)
    
    # Ultrasonic Sensor - Front
    ULTRA_FRONT_TRIG = 5   # GPIO5  - Front Trigger
    ULTRA_FRONT_ECHO = 18  # GPIO18 - Front Echo
    
    # Ultrasonic Sensor - Left
    ULTRA_LEFT_TRIG = 19   # GPIO19 - Left Trigger
    ULTRA_LEFT_ECHO = 21   # GPIO21 - Left Echo
    
    # Ultrasonic Sensor - Right
    ULTRA_RIGHT_TRIG = 23  # GPIO23 - Right Trigger
    ULTRA_RIGHT_ECHO = 22  # GPIO22 - Right Echo
    
    # Encoder Wheel (Interrupt Pin)
    ENCODER_PIN = 4  # GPIO4 - Encoder interrupt
    
    # PWM Parameters
    PWM_FREQUENCY = 5000  # 5 kHz for motor control
    PWM_RESOLUTION = 8    # 8-bit (0-255)

# =================== DISTANCE & SAFETY PARAMETERS =========================
class SafetyConfig:
    # Safe Distance Thresholds (in cm)
    SAFE_DISTANCE = 30  # Minimum safe distance to obstacle
    CRITICAL_DISTANCE = 15  # Emergency stop distance
    FOLLOW_DISTANCE = 25  # Optimal distance to maintain
    
    # Decision Thresholds
    FRONT_CHECK_THRESHOLD = 40  # Check front before moving forward
    TURN_DECISION_THRESHOLD = 50  # Distance difference to decide turn direction
    
    # Ultrasonic Parameters
    SOUND_SPEED = 0.034  # cm/microsecond (Speed of sound in air)
    SENSOR_CALIBRATION_OFFSET = 0  # Offset in cm (adjust if sensors read high/low)

# =================== MOTOR CONTROL PARAMETERS =============================
class MotorConfig:
    # Motor Speed Control (0-255 PWM values)
    SPEED_FULL = 255    # Full forward speed
    SPEED_NORMAL = 180  # Normal forward speed
    SPEED_SLOW = 100    # Slow forward (for fine movements)
    SPEED_STOP = 0      # Stop
    
    # Motor Direction Mapping
    # Both motors moving forward
    DIRECTION_FORWARD = {"A": "forward", "B": "forward"}
    # Turn right (left motor faster)
    DIRECTION_RIGHT = {"A": "forward", "B": "forward"}
    # Turn left (right motor faster)
    DIRECTION_LEFT = {"A": "forward", "B": "forward"}
    # Stop
    DIRECTION_STOP = {"A": "stop", "B": "stop"}

# =================== ENCODER WHEEL PARAMETERS ==============================
class EncoderConfig:
    # Wheel Specifications
    WHEEL_DIAMETER_CM = 6.5  # Physical wheel diameter in cm
    ENCODER_SLOTS = 20  # Number of slots in encoder wheel
    
    # Distance Calculation
    WHEEL_CIRCUMFERENCE = WHEEL_DIAMETER_CM * 3.14159  # πd
    DISTANCE_PER_PULSE = WHEEL_CIRCUMFERENCE / ENCODER_SLOTS
    
    # For debugging: Print pulse data
    DEBUG_ENCODER = True

# =================== NAVIGATION PARAMETERS ==================================
class NavigationConfig:
    # Stage-based Navigation (A → B → C)
    STAGE_A_TARGET_DISTANCE = 100  # Distance to reach B (in cm)
    STAGE_B_TARGET_DISTANCE = 50   # Distance to reach C (in cm)
    STAGE_C_TARGET_DISTANCE = 0    # Final destination
    
    # Distance Tolerance (cm) - acceptable error margin
    DISTANCE_TOLERANCE = 5
    
    # Navigation Stages
    STAGE_IDLE = "IDLE"
    STAGE_A_TO_B = "A→B"
    STAGE_B_TO_C = "B→C"
    STAGE_ARRIVED_C = "ARRIVED_C"

# =================== AI DECISION LOGIC PARAMETERS ===========================
class AIConfig:
    # Decision delay (ms) - time between sensor reads
    DECISION_INTERVAL_MS = 100
    
    # Moving average window for sensor smoothing
    SENSOR_AVERAGE_WINDOW = 5
    
    # Enable/Disable Features
    ENABLE_OBSTACLE_AVOIDANCE = True
    ENABLE_ENCODER_TRACKING = True
    ENABLE_MEMORY_SYSTEM = True  # Remember past obstacles
    
    # Response explanations
    VERBOSE_MODE = True  # If True, AI explains WHY decisions are made

# =================== COMMUNICATION PARAMETERS ================================
class CommConfig:
    # Flask API Server
    API_HOST = "0.0.0.0"  # Listen on all network interfaces
    API_PORT = 5000
    API_DEBUG = True
    
    # ESP32 Connection
    ESP32_BAUDRATE = 115200
    SERIAL_TIMEOUT = 2  # seconds
    
    # Data update interval
    DATA_UPDATE_INTERVAL = 0.1  # seconds (100ms)

# =================== ROBOT STATE INITIALIZATION =============================
class RobotState:
    """Current real-time state of the robot"""
    def __init__(self):
        # Ultrasonic readings (cm)
        self.distance_front = 0
        self.distance_left = 0
        self.distance_right = 0
        
        # Encoder data
        self.pulse_count = 0
        self.distance_traveled = 0
        
        # Navigation state
        self.current_stage = NavigationConfig.STAGE_IDLE
        self.stage_distance_traveled = 0
        
        # Motor state
        self.motor_speed_left = 0
        self.motor_speed_right = 0
        self.motor_direction = "stop"
        
        # Decision history
        self.last_decision = "idle"
        self.obstacle_memory = []  # Remember obstacles encountered
        
        # Timestamps
        self.last_update_time = 0
        self.decision_count = 0

# ========================= HELPER FUNCTIONS =================================
def print_config():
    """Print all configuration parameters for debugging"""
    print("=" * 70)
    print("ROBOT AI BRAIN - CONFIGURATION SUMMARY")
    print("=" * 70)
    print("\n[GPIO PIN MAPPING]")
    print(f"  Motor A PWM: GPIO{PinConfig.MOTOR_A_PWM}, Direction: GPIO{PinConfig.MOTOR_A_IN1}/{PinConfig.MOTOR_A_IN2}")
    print(f"  Motor B PWM: GPIO{PinConfig.MOTOR_B_PWM}, Direction: GPIO{PinConfig.MOTOR_B_IN1}/{PinConfig.MOTOR_B_IN2}")
    print(f"  Ultrasonic: Front(GPIO{PinConfig.ULTRA_FRONT_TRIG}/{PinConfig.ULTRA_FRONT_ECHO}), "
          f"Left(GPIO{PinConfig.ULTRA_LEFT_TRIG}/{PinConfig.ULTRA_LEFT_ECHO}), "
          f"Right(GPIO{PinConfig.ULTRA_RIGHT_TRIG}/{PinConfig.ULTRA_RIGHT_ECHO})")
    print(f"  Encoder: GPIO{PinConfig.ENCODER_PIN}")
    
    print("\n[SAFETY THRESHOLDS]")
    print(f"  Safe Distance: {SafetyConfig.SAFE_DISTANCE}cm")
    print(f"  Critical Distance: {SafetyConfig.CRITICAL_DISTANCE}cm")
    print(f"  Wheel Circumference: {EncoderConfig.WHEEL_CIRCUMFERENCE:.2f}cm ({EncoderConfig.ENCODER_SLOTS} slots)")
    
    print("\n[NAVIGATION TARGETS]")
    print(f"  A→B Distance: {NavigationConfig.STAGE_A_TARGET_DISTANCE}cm")
    print(f"  B→C Distance: {NavigationConfig.STAGE_B_TARGET_DISTANCE}cm")
    
    print("\n[API SERVER]")
    print(f"  Flask running on {CommConfig.API_HOST}:{CommConfig.API_PORT}")
    print("=" * 70)
