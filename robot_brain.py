# ============================================================================
# ROBOT BRAIN - Real-Time AI Decision Engine
# ============================================================================
# Processes sensor data and makes navigation decisions like a control engineer
# ============================================================================

from config import SafetyConfig, MotorConfig, NavigationConfig, EncoderConfig, AIConfig
from datetime import datetime
from collections import deque

class RobotBrain:
    """
    AI Brain for autonomous robot navigation.
    - Analyzes ultrasonic and encoder data
    - Makes safe navigation decisions (forward, turn, stop)
    - Explains reasoning for each decision
    """
    
    def __init__(self):
        # Sensor smoothing buffers (moving average)
        self.front_distance_buffer = deque(maxlen=AIConfig.SENSOR_AVERAGE_WINDOW)
        self.left_distance_buffer = deque(maxlen=AIConfig.SENSOR_AVERAGE_WINDOW)
        self.right_distance_buffer = deque(maxlen=AIConfig.SENSOR_AVERAGE_WINDOW)
        
        # Navigation tracking
        self.current_stage = NavigationConfig.STAGE_IDLE
        self.stage_distance_traveled = 0
        self.obstacle_history = []  # Remember obstacles for optimization
        
        # Decision tracking
        self.last_decision = "IDLE"
        self.decision_count = 0
        self.decision_reasons = []
        
    def add_sensor_reading(self, front_cm, left_cm, right_cm):
        """Add raw sensor readings to smoothing buffers"""
        self.front_distance_buffer.append(max(0, front_cm))
        self.left_distance_buffer.append(max(0, left_cm))
        self.right_distance_buffer.append(max(0, right_cm))
    
    def get_smoothed_distances(self):
        """Return averaged sensor readings for stable decision-making"""
        front_avg = sum(self.front_distance_buffer) / len(self.front_distance_buffer) if self.front_distance_buffer else 0
        left_avg = sum(self.left_distance_buffer) / len(self.left_distance_buffer) if self.left_distance_buffer else 0
        right_avg = sum(self.right_distance_buffer) / len(self.right_distance_buffer) if self.right_distance_buffer else 0
        
        return {
            "front": round(front_avg, 1),
            "left": round(left_avg, 1),
            "right": round(right_avg, 1)
        }
    
    def check_obstacle(self, distance_cm, threshold=None):
        """
        Analyze if obstacle exists based on distance threshold.
        Returns: "BLOCKED", "CAUTION", or "CLEAR"
        """
        if threshold is None:
            threshold = SafetyConfig.SAFE_DISTANCE
        
        if distance_cm <= SafetyConfig.CRITICAL_DISTANCE:
            return "BLOCKED"
        elif distance_cm <= threshold:
            return "CAUTION"
        else:
            return "CLEAR"
    
    def decide_navigation(self, front_dist, left_dist, right_dist, encoder_distance, target_distance=None):
        """
        AI DECISION ENGINE - Core logic for real-time navigation.
        
        Inputs:
          - front_dist: Ultrasonic distance ahead (cm)
          - left_dist: Ultrasonic distance left (cm)
          - right_dist: Ultrasonic distance right (cm)
          - encoder_distance: Total distance traveled (cm)
          - target_distance: Target distance for current stage (optional)
        
        Outputs:
          - decision: "FORWARD", "TURN_LEFT", "TURN_RIGHT", "STOP"
          - speed: Motor PWM (0-255)
          - explanation: Reason in plain English
        """
        
        self.decision_count += 1
        
        # ===== STAGE 1: CHECK FRONT OBSTACLE =====
        front_status = self.check_obstacle(front_dist, SafetyConfig.FRONT_CHECK_THRESHOLD)
        
        if front_status == "BLOCKED":
            # DECISION: STOP & EVALUATE
            decision = "STOP"
            speed = 0
            explanation = f"🚫 OBSTACLE AHEAD! Front distance: {front_dist:.1f}cm < {SafetyConfig.CRITICAL_DISTANCE}cm (critical). EMERGENCY STOP."
            self.last_decision = decision
            return self._format_decision(decision, speed, explanation)
        
        # ===== STAGE 2: CHECK NAVIGATION PROGRESS =====
        if target_distance is not None:
            if encoder_distance >= target_distance:
                decision = "STOP"
                speed = 0
                explanation = f"✓ DESTINATION REACHED! Traveled {encoder_distance:.1f}cm / Target {target_distance}cm. Navigation complete."
                self.last_decision = decision
                return self._format_decision(decision, speed, explanation)
        
        # ===== STAGE 3: COMPARE LEFT vs RIGHT PATHS =====
        left_status = self.check_obstacle(left_dist)
        right_status = self.check_obstacle(right_dist)
        
        # Determine best available path
        left_available = left_dist >= SafetyConfig.SAFE_DISTANCE
        right_available = right_dist >= SafetyConfig.SAFE_DISTANCE
        front_available = front_dist >= SafetyConfig.SAFE_DISTANCE
        
        # ===== STAGE 4: MAKE STEERING DECISION =====
        
        # Case 1: All paths clear - Go straight
        if front_available and left_available and right_available:
            decision = "FORWARD"
            speed = MotorConfig.SPEED_NORMAL
            explanation = (
                f"✓ ALL PATHS CLEAR! Front: {front_dist:.1f}cm, Left: {left_dist:.1f}cm, Right: {right_dist:.1f}cm. "
                f"Moving FORWARD at {speed} PWM."
            )
        
        # Case 2: Front blocked, both sides available - Choose wider path
        elif not front_available and left_available and right_available:
            if left_dist >= right_dist:
                decision = "TURN_LEFT"
                speed = MotorConfig.SPEED_NORMAL
                explanation = (
                    f"⬅️ TURN LEFT! Front blocked ({front_dist:.1f}cm), but left path wider: "
                    f"Left {left_dist:.1f}cm vs Right {right_dist:.1f}cm."
                )
            else:
                decision = "TURN_RIGHT"
                speed = MotorConfig.SPEED_NORMAL
                explanation = (
                    f"➡️ TURN RIGHT! Front blocked ({front_dist:.1f}cm), but right path wider: "
                    f"Right {right_dist:.1f}cm vs Left {left_dist:.1f}cm."
                )
        
        # Case 3: Front + one side blocked - Turn to available side
        elif not front_available:
            if left_available and not right_available:
                decision = "TURN_LEFT"
                speed = MotorConfig.SPEED_SLOW
                explanation = (
                    f"⬅️ FORCED LEFT TURN! Front ({front_dist:.1f}cm) & right ({right_dist:.1f}cm) blocked. "
                    f"Only left path available: {left_dist:.1f}cm."
                )
            elif right_available and not left_available:
                decision = "TURN_RIGHT"
                speed = MotorConfig.SPEED_SLOW
                explanation = (
                    f"➡️ FORCED RIGHT TURN! Front ({front_dist:.1f}cm) & left ({left_dist:.1f}cm) blocked. "
                    f"Only right path available: {right_dist:.1f}cm."
                )
            else:
                # All paths blocked
                decision = "STOP"
                speed = 0
                explanation = (
                    f"⚠️ TRAPPED! All paths blocked - Front: {front_dist:.1f}cm, "
                    f"Left: {left_dist:.1f}cm, Right: {right_dist:.1f}cm. "
                    f"STOPPING to re-evaluate."
                )
        
        # Case 4: Front clear but caution zone - Slow down and move carefully
        elif front_status == "CAUTION":
            decision = "FORWARD"
            speed = MotorConfig.SPEED_SLOW
            explanation = (
                f"🟡 CAUTION ZONE! Front distance {front_dist:.1f}cm is in warning range "
                f"({SafetyConfig.CRITICAL_DISTANCE}-{SafetyConfig.SAFE_DISTANCE}cm). "
                f"Moving FORWARD SLOWLY at {speed} PWM."
            )
        
        else:
            # Default: move forward at normal speed
            decision = "FORWARD"
            speed = MotorConfig.SPEED_NORMAL
            explanation = f"✓ MOVING FORWARD. Front: {front_dist:.1f}cm clear. Speed: {speed} PWM."
        
        self.last_decision = decision
        return self._format_decision(decision, speed, explanation)
    
    def _format_decision(self, decision, speed, explanation):
        """Format decision in standardized output"""
        motor_map = {
            "FORWARD": {"left_speed": speed, "right_speed": speed, "left_dir": "FWD", "right_dir": "FWD"},
            "TURN_LEFT": {"left_speed": speed // 2, "right_speed": speed, "left_dir": "FWD", "right_dir": "FWD"},
            "TURN_RIGHT": {"left_speed": speed, "right_speed": speed // 2, "left_dir": "FWD", "right_dir": "FWD"},
            "STOP": {"left_speed": 0, "right_speed": 0, "left_dir": "STOP", "right_dir": "STOP"},
        }
        
        motor_cmd = motor_map.get(decision, motor_map["STOP"])
        
        return {
            "decision": decision,
            "speed": speed,
            "motor_left_speed": motor_cmd["left_speed"],
            "motor_right_speed": motor_cmd["right_speed"],
            "motor_left_direction": motor_cmd["left_dir"],
            "motor_right_direction": motor_cmd["right_dir"],
            "explanation": explanation,
            "decision_number": self.decision_count,
            "timestamp": datetime.now().isoformat()
        }
    
    def update_stage(self, encoder_distance, stage_target):
        """Track navigation between stages A→B→C"""
        if encoder_distance >= stage_target:
            if self.current_stage == NavigationConfig.STAGE_IDLE:
                self.current_stage = NavigationConfig.STAGE_A_TO_B
            elif self.current_stage == NavigationConfig.STAGE_A_TO_B:
                self.current_stage = NavigationConfig.STAGE_B_TO_C
            elif self.current_stage == NavigationConfig.STAGE_B_TO_C:
                self.current_stage = NavigationConfig.STAGE_ARRIVED_C
            
            self.stage_distance_traveled = 0
        else:
            self.stage_distance_traveled = encoder_distance
        
        return self.current_stage
    
    def get_status_report(self):
        """Generate full diagnostic report"""
        return {
            "last_decision": self.last_decision,
            "total_decisions": self.decision_count,
            "current_stage": self.current_stage,
            "stage_distance": self.stage_distance_traveled,
            "obstacles_encountered": len(self.obstacle_history)
        }


# ============================================================================
# EXPERT ROBOTICIST RESPONSE GENERATOR
# ============================================================================

class ExpertResponder:
    """
    Generates responses like a roboticist + control engineer.
    Answers questions about sensor data, decisions, hardware config, etc.
    """
    
    def __init__(self, brain):
        self.brain = brain
    
    def explain_decision(self, decision_data):
        """Convert raw decision into expert explanation"""
        return decision_data.get("explanation", "No explanation available")
    
    def answer_sensor_question(self, front, left, right):
        """Answer: 'Obstacle irukku na enna pannuva?' (Tamil: Is there an obstacle, what to do?)"""
        responses = []
        
        if front <= SafetyConfig.CRITICAL_DISTANCE:
            responses.append(f"🚫 FRONT: BLOCKED ({front:.1f}cm) - DANGER!")
        elif front <= SafetyConfig.SAFE_DISTANCE:
            responses.append(f"🟡 FRONT: CAUTION ({front:.1f}cm) - Slow down")
        else:
            responses.append(f"✓ FRONT: CLEAR ({front:.1f}cm) - Safe to proceed")
        
        if left <= SafetyConfig.CRITICAL_DISTANCE:
            responses.append(f"🚫 LEFT: BLOCKED ({left:.1f}cm)")
        elif left <= SafetyConfig.SAFE_DISTANCE:
            responses.append(f"🟡 LEFT: CAUTION ({left:.1f}cm)")
        else:
            responses.append(f"✓ LEFT: CLEAR ({left:.1f}cm)")
        
        if right <= SafetyConfig.CRITICAL_DISTANCE:
            responses.append(f"🚫 RIGHT: BLOCKED ({right:.1f}cm)")
        elif right <= SafetyConfig.SAFE_DISTANCE:
            responses.append(f"🟡 RIGHT: CAUTION ({right:.1f}cm)")
        else:
            responses.append(f"✓ RIGHT: CLEAR ({right:.1f}cm)")
        
        return "\n".join(responses)
    
    def answer_path_question(self, left, right):
        """Answer: 'Left free aa? Right free aa?' (Tamil: Is left free? Is right free?)"""
        left_free = left >= SafetyConfig.SAFE_DISTANCE
        right_free = right >= SafetyConfig.SAFE_DISTANCE
        
        response = f"LEFT: {'✓ FREE ({:.1f}cm)'.format(left) if left_free else '✗ BLOCKED ({:.1f}cm)'.format(left)}\n"
        response += f"RIGHT: {'✓ FREE ({:.1f}cm)'.format(right) if right_free else '✗ BLOCKED ({:.1f}cm)'.format(right)}\n"
        
        if left_free and right_free:
            better = "LEFT" if left > right else "RIGHT"
            response += f"\n→ BOTH FREE! Choose {better} (wider by {abs(left-right):.1f}cm)"
        elif left_free:
            response += f"\n→ Turn LEFT only option"
        elif right_free:
            response += f"\n→ Turn RIGHT only option"
        else:
            response += f"\n→ Both sides BLOCKED - STOP and re-evaluate"
        
        return response
    
    def hardware_info(self, query):
        """Answer hardware configuration questions"""
        from config import PinConfig, SafetyConfig, EncoderConfig, CommConfig
        
        query_lower = query.lower()
        
        if "pin" in query_lower or "gpio" in query_lower:
            return f"""
**GPIO PIN MAPPING (ESP32):**
- Motor A: PWM=GPIO{PinConfig.MOTOR_A_PWM}, IN1=GPIO{PinConfig.MOTOR_A_IN1}, IN2=GPIO{PinConfig.MOTOR_A_IN2}
- Motor B: PWM=GPIO{PinConfig.MOTOR_B_PWM}, IN1=GPIO{PinConfig.MOTOR_B_IN1}, IN2=GPIO{PinConfig.MOTOR_B_IN2}
- Ultrasonic Front: TRIG=GPIO{PinConfig.ULTRA_FRONT_TRIG}, ECHO=GPIO{PinConfig.ULTRA_FRONT_ECHO}
- Ultrasonic Left: TRIG=GPIO{PinConfig.ULTRA_LEFT_TRIG}, ECHO=GPIO{PinConfig.ULTRA_LEFT_ECHO}
- Ultrasonic Right: TRIG=GPIO{PinConfig.ULTRA_RIGHT_TRIG}, ECHO=GPIO{PinConfig.ULTRA_RIGHT_ECHO}
- Encoder: GPIO{PinConfig.ENCODER_PIN}
"""
        elif "threshold" in query_lower or "distance" in query_lower:
            return f"""
**SAFETY THRESHOLDS:**
- Safe Distance: {SafetyConfig.SAFE_DISTANCE}cm (maintain this minimum)
- Critical Distance: {SafetyConfig.CRITICAL_DISTANCE}cm (emergency stop)
- Follow Distance: {SafetyConfig.FOLLOW_DISTANCE}cm (optimal cruising)
"""
        elif "encoder" in query_lower or "wheel" in query_lower:
            return f"""
**ENCODER WHEEL SPECIFICATIONS:**
- Wheel Diameter: {EncoderConfig.WHEEL_DIAMETER_CM}cm
- Slots: {EncoderConfig.ENCODER_SLOTS}
- Circumference: {EncoderConfig.WHEEL_CIRCUMFERENCE:.2f}cm
- Distance per pulse: {EncoderConfig.DISTANCE_PER_PULSE:.3f}cm
"""
        elif "api" in query_lower or "server" in query_lower:
            return f"""
**API SERVER CONFIGURATION:**
- Host: {CommConfig.API_HOST}
- Port: {CommConfig.API_PORT}
- Baudrate (Serial): {CommConfig.ESP32_BAUDRATE}
"""
        else:
            return "Ask about: pins, thresholds, encoder wheel, or API server configuration."

