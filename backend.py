# ============================================================================
# ROBOT AI BACKEND - Flask REST API Server
# ============================================================================
# Receives sensor data from ESP32 via HTTP POST
# Returns real-time navigation decisions as JSON
# ============================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
from robot_brain import RobotBrain, ExpertResponder
from config import CommConfig, SafetyConfig, NavigationConfig
from datetime import datetime
import traceback

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable cross-origin requests for Streamlit

# Initialize Robot Brain
brain = RobotBrain()
responder = ExpertResponder(brain)

# Store last sensor readings
last_sensor_data = {
    "front_dist": 0,
    "left_dist": 0,
    "right_dist": 0,
    "encoder_distance": 0,
    "timestamp": None
}

# ============================================================================
# MAIN API ENDPOINT - Receive sensor data and get navigation decision
# ============================================================================

@app.route('/api/robot/decide', methods=['POST'])
def robot_decide():
    """
    Endpoint for ESP32 to send sensor data and receive navigation decision.
    
    Request JSON:
    {
        "front_dist": 45.2,      # Ultrasonic front (cm)
        "left_dist": 60.0,       # Ultrasonic left (cm)
        "right_dist": 35.5,      # Ultrasonic right (cm)
        "encoder_pulses": 1240,  # Encoder pulse count
        "stage": "A→B",          # Current navigation stage
        "target_distance": 100   # Target distance for stage (optional)
    }
    
    Response JSON:
    {
        "decision": "FORWARD",
        "speed": 180,
        "motor_left_speed": 180,
        "motor_right_speed": 180,
        "motor_left_direction": "FWD",
        "motor_right_direction": "FWD",
        "explanation": "Movement reasoning...",
        "timestamp": "2026-02-11T...",
        "status": "success"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['front_dist', 'left_dist', 'right_dist']
        if not all(field in data for field in required_fields):
            return jsonify({
                "status": "error",
                "message": f"Missing required fields: {required_fields}"
            }), 400
        
        # Extract sensor data
        front_dist = float(data.get('front_dist', 0))
        left_dist = float(data.get('left_dist', 0))
        right_dist = float(data.get('right_dist', 0))
        encoder_pulses = int(data.get('encoder_pulses', 0))
        target_distance = float(data.get('target_distance', NavigationConfig.STAGE_A_TARGET_DISTANCE))
        
        # Calculate encoder distance in cm
        from config import EncoderConfig
        encoder_distance = encoder_pulses * EncoderConfig.DISTANCE_PER_PULSE
        
        # Add readings to smoothing buffer
        brain.add_sensor_reading(front_dist, left_dist, right_dist)
        
        # Get smoothed distances
        smoothed = brain.get_smoothed_distances()
        
        # Get AI decision
        decision = brain.decide_navigation(
            front_dist=smoothed['front'],
            left_dist=smoothed['left'],
            right_dist=smoothed['right'],
            encoder_distance=encoder_distance,
            target_distance=target_distance
        )
        
        # Update stage tracking
        current_stage = brain.update_stage(encoder_distance, target_distance)
        
        # Store last reading
        last_sensor_data.update({
            "front_dist": front_dist,
            "left_dist": left_dist,
            "right_dist": right_dist,
            "encoder_distance": encoder_distance,
            "timestamp": datetime.now().isoformat(),
            "smoothed_front": smoothed['front'],
            "smoothed_left": smoothed['left'],
            "smoothed_right": smoothed['right']
        })
        
        # Add stage info to response
        decision['current_stage'] = current_stage
        decision['encoder_distance'] = encoder_distance
        decision['status'] = 'success'
        
        return jsonify(decision), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500


# ============================================================================
# AUXILIARY ENDPOINTS - Get status and information
# ============================================================================

@app.route('/api/robot/status', methods=['GET'])
def robot_status():
    """Get current robot status and state information"""
    return jsonify({
        "status": "success",
        "data": {
            **last_sensor_data,
            **brain.get_status_report(),
            "safe_distance_threshold": SafetyConfig.SAFE_DISTANCE,
            "critical_distance_threshold": SafetyConfig.CRITICAL_DISTANCE
        }
    }), 200


@app.route('/api/robot/reset', methods=['POST'])
def robot_reset():
    """Reset robot brain and state"""
    global brain
    brain = RobotBrain()
    last_sensor_data.clear()
    return jsonify({
        "status": "success",
        "message": "Robot brain reset. Ready for new navigation."
    }), 200


@app.route('/api/robot/config', methods=['GET'])
def robot_config():
    """Get hardware configuration (pin mapping, thresholds, etc.)"""
    from config import PinConfig, SafetyConfig, EncoderConfig, CommConfig
    
    return jsonify({
        "status": "success",
        "pin_config": {
            "motor_a": {
                "pwm": PinConfig.MOTOR_A_PWM,
                "in1": PinConfig.MOTOR_A_IN1,
                "in2": PinConfig.MOTOR_A_IN2
            },
            "motor_b": {
                "pwm": PinConfig.MOTOR_B_PWM,
                "in1": PinConfig.MOTOR_B_IN1,
                "in2": PinConfig.MOTOR_B_IN2
            },
            "ultrasonic": {
                "front": {"trig": PinConfig.ULTRA_FRONT_TRIG, "echo": PinConfig.ULTRA_FRONT_ECHO},
                "left": {"trig": PinConfig.ULTRA_LEFT_TRIG, "echo": PinConfig.ULTRA_LEFT_ECHO},
                "right": {"trig": PinConfig.ULTRA_RIGHT_TRIG, "echo": PinConfig.ULTRA_RIGHT_ECHO}
            },
            "encoder": PinConfig.ENCODER_PIN
        },
        "safety_thresholds": {
            "safe_distance_cm": SafetyConfig.SAFE_DISTANCE,
            "critical_distance_cm": SafetyConfig.CRITICAL_DISTANCE,
            "follow_distance_cm": SafetyConfig.FOLLOW_DISTANCE
        },
        "encoder_info": {
            "wheel_diameter_cm": EncoderConfig.WHEEL_DIAMETER_CM,
            "slots": EncoderConfig.ENCODER_SLOTS,
            "circumference_cm": round(EncoderConfig.WHEEL_CIRCUMFERENCE, 2),
            "distance_per_pulse_cm": round(EncoderConfig.DISTANCE_PER_PULSE, 3)
        }
    }), 200


# ============================================================================
# CHAT ENDPOINTS - For Streamlit chatbot integration
# ============================================================================

@app.route('/api/chat/ask', methods=['POST'])
def chat_ask():
    """
    Chatbot endpoint for asking questions about robot status, decisions, etc.
    
    Request JSON:
    {
        "question": "Left free aa? Right free aa?",
        "context": "sensor_data"  # Optional context
    }
    """
    try:
        data = request.get_json()
        question = data.get('question', '')
        
        if not question:
            return jsonify({"status": "error", "message": "Question required"}), 400
        
        question_lower = question.lower()
        
        # Route to appropriate responder
        if "left" in question_lower and "right" in question_lower:
            # Answer: "Left free aa? Right free aa?"
            response = responder.answer_path_question(
                last_sensor_data.get('left_dist', 0),
                last_sensor_data.get('right_dist', 0)
            )
        elif "obstacle" in question_lower:
            # Answer: "Obstacle irukku na enna pannuva?"
            response = responder.answer_sensor_question(
                last_sensor_data.get('front_dist', 0),
                last_sensor_data.get('left_dist', 0),
                last_sensor_data.get('right_dist', 0)
            )
        elif "pin" in question_lower or "gpio" in question_lower or "config" in question_lower:
            # Hardware config question
            response = responder.hardware_info(question)
        else:
            response = f"Question: {question}\n\nCurrent Robot State:\n{json.dumps(last_sensor_data, indent=2)}"
        
        return jsonify({
            "status": "success",
            "question": question,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# ============================================================================
# HEALTH CHECK & WELCOME ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Robot AI Brain",
        "timestamp": datetime.now().isoformat()
    }), 200


@app.route('/', methods=['GET'])
def welcome():
    """Welcome page with API documentation"""
    return jsonify({
        "status": "online",
        "service": "Robot AI Brain - Real-Time Navigation Engine",
        "version": "1.0",
        "endpoints": {
            "POST /api/robot/decide": "Send sensor data, get navigation decision",
            "GET /api/robot/status": "Get current robot state",
            "GET /api/robot/config": "Get hardware configuration",
            "POST /api/robot/reset": "Reset robot brain",
            "POST /api/chat/ask": "Ask questions about robot state",
            "GET /api/health": "Health check"
        },
        "documentation": "http://localhost:5000/api/docs (if available)",
        "timestamp": datetime.now().isoformat()
    }), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(400)
def bad_request(e):
    return jsonify({"status": "error", "message": "Bad request"}), 400

@app.errorhandler(404)
def not_found(e):
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"status": "error", "message": "Internal server error"}), 500


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("ROBOT AI BRAIN - FLASK SERVER")
    print("="*70)
    print(f"Starting API server on {CommConfig.API_HOST}:{CommConfig.API_PORT}")
    print("\nAvailable endpoints:")
    print(f"  POST   /api/robot/decide      - Get navigation decision")
    print(f"  GET    /api/robot/status      - Get robot status")
    print(f"  GET    /api/robot/config      - Get hardware config")
    print(f"  POST   /api/robot/reset       - Reset robot state")
    print(f"  POST   /api/chat/ask          - Ask robot questions")
    print(f"  GET    /api/health            - Health check")
    print("\n" + "="*70 + "\n")
    
    app.run(
        host=CommConfig.API_HOST,
        port=CommConfig.API_PORT,
        debug=CommConfig.API_DEBUG,
        use_reloader=False  # Disable reloader to prevent duplicate threads
    )
