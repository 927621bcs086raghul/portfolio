# ============================================================================
# ROBOT AI CHATBOT - Streamlit Web Interface
# ============================================================================
# Beautiful chat interface for real-time robot control and interaction
# Like ChatGPT + Gemini but for robot navigation
# ============================================================================

import streamlit as st
import requests
import json
from datetime import datetime
import time

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Robot AI Brain 🤖",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .sensor-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        font-size: 1.1rem;
    }
    
    .decision-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 10px 0;
        font-size: 1.1rem;
    }
    
    .status-box {
        padding: 1rem;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #667eea;
    }
    
    .success { background-color: #d4edda; border-left-color: #28a745; }
    .warning { background-color: #fff3cd; border-left-color: #ffc107; }
    .error { background-color: #f8d7da; border-left-color: #dc3545; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SESSION STATE
# ============================================================================

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'api_url' not in st.session_state:
    st.session_state.api_url = "http://localhost:5000"

if 'last_sensor_data' not in st.session_state:
    st.session_state.last_sensor_data = None

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.title("⚙️ Configuration")
    
    # API Server Configuration
    st.subheader("API Server Settings")
    api_host = st.text_input("API Host", value="localhost")
    api_port = st.number_input("API Port", value=5000, min_value=1, max_value=65535)
    st.session_state.api_url = f"http://{api_host}:{api_port}"
    
    # Test Connection
    if st.button("🔗 Test API Connection"):
        try:
            response = requests.get(f"{st.session_state.api_url}/api/health", timeout=3)
            if response.status_code == 200:
                st.success("✓ Connected to Robot AI Brain!")
            else:
                st.error(f"✗ Server responded with status {response.status_code}")
        except:
            st.error("✗ Cannot connect to API server. Is backend running?")
    
    st.divider()
    
    # Robot Configuration
    st.subheader("Robot Configuration")
    if st.button("📋 Load Hardware Config"):
        try:
            response = requests.get(f"{st.session_state.api_url}/api/robot/config", timeout=5)
            if response.status_code == 200:
                config = response.json()['pin_config']
                st.json(config)
            else:
                st.error("Failed to load config")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.divider()
    
    # Robot Status
    st.subheader("Robot Status")
    if st.button("📊 Get Robot Status"):
        try:
            response = requests.get(f"{st.session_state.api_url}/api/robot/status", timeout=5)
            if response.status_code == 200:
                status = response.json()['data']
                st.json(status)
            else:
                st.error("Failed to get status")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    if st.button("🔄 Reset Robot Brain"):
        try:
            response = requests.post(f"{st.session_state.api_url}/api/robot/reset", timeout=5)
            if response.status_code == 200:
                st.success("Robot brain reset!")
                st.session_state.chat_history = []
            else:
                st.error("Failed to reset")
        except Exception as e:
            st.error(f"Error: {str(e)}")
    
    st.divider()
    
    # Chat History
    st.subheader("Chat History")
    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

# ============================================================================
# MAIN CONTENT AREA
# ============================================================================

# Header
st.title("🤖 Robot AI Brain")
st.markdown("*Real-time autonomous robot control & navigation AI*")

# Create tabs for different sections
tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 Sensor Dashboard", "🎮 Manual Control"])

# ============================================================================
# TAB 1: CHAT INTERFACE
# ============================================================================

with tab1:
    st.subheader("Conversational AI - Ask Robot Questions")
    
    # Display chat history
    if st.session_state.chat_history:
        st.markdown("### Chat History")
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.chat_message("user").markdown(f"**You:** {msg['content']}")
            else:
                st.chat_message("assistant").markdown(f"**Robot:** {msg['content']}")
    
    st.divider()
    
    # Quick preset questions
    st.markdown("### Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🚧 Obstacle irukku na?"):
            question = "Are there any obstacles? What do you see?"
            st.session_state.selected_question = question
    
    with col2:
        if st.button("⬅️➡️ Left free aa?"):
            question = "Left free aa? Right free aa? (Tamil: Is left path free? Is right path free?)"
            st.session_state.selected_question = question
    
    with col3:
        if st.button("📏 Distance correct aa?"):
            question = "A→B ku pona distance correct ah? (Tamil: Is the distance traveled from A to B correct?)"
            st.session_state.selected_question = question
    
    st.divider()
    
    # Chat input
    st.markdown("### Ask Me Anything")
    col_input, col_send = st.columns([5, 1])
    
    with col_input:
        user_question = st.text_input(
            "Type your question...",
            placeholder="E.g., 'What's happening with the front sensor?' or 'Explain the last decision'",
            key="user_input"
        )
    
    with col_send:
        send_btn = st.button("📤 Send", use_container_width=True, type="primary")
    
    # Process user question
    if send_btn and user_question:
        # Add to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # Send to API
        try:
            response = requests.post(
                f"{st.session_state.api_url}/api/chat/ask",
                json={"question": user_question},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                robot_answer = result.get('response', 'No response')
                
                # Add to history
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": robot_answer
                })
                
                st.rerun()
            else:
                st.error("API error: " + str(response.status_code))
        except Exception as e:
            st.error(f"Connection error: {str(e)}")

# ============================================================================
# TAB 2: SENSOR DASHBOARD
# ============================================================================

with tab2:
    st.subheader("Real-Time Sensor Data & Status")
    
    col1, col2, col3 = st.columns(3)
    
    # Refresh button
    if st.button("🔄 Refresh Sensor Data"):
        try:
            response = requests.get(f"{st.session_state.api_url}/api/robot/status", timeout=5)
            if response.status_code == 200:
                st.session_state.last_sensor_data = response.json()['data']
        except:
            st.error("Failed to fetch sensor data")
    
    if st.session_state.last_sensor_data:
        data = st.session_state.last_sensor_data
        
        # Display sensor readings
        st.markdown("### 📡 Ultrasonic Sensors (cm)")
        col_front, col_left, col_right = st.columns(3)
        
        with col_front:
            front = data.get('front_dist', 0)
            st.metric("🔴 Front", f"{front:.1f} cm", 
                     delta=f"Smooth: {data.get('smoothed_front', 0):.1f}")
        
        with col_left:
            left = data.get('left_dist', 0)
            st.metric("🟡 Left", f"{left:.1f} cm",
                     delta=f"Smooth: {data.get('smoothed_left', 0):.1f}")
        
        with col_right:
            right = data.get('right_dist', 0)
            st.metric("🟢 Right", f"{right:.1f} cm",
                     delta=f"Smooth: {data.get('smoothed_right', 0):.1f}")
        
        st.divider()
        
        # Display encoder data
        st.markdown("### 📏 Encoder Wheel Data")
        col_enc1, col_enc2 = st.columns(2)
        
        with col_enc1:
            st.metric("Distance Traveled", 
                     f"{data.get('encoder_distance', 0):.1f} cm")
        
        with col_enc2:
            st.metric("Current Stage", 
                     data.get('current_stage', 'IDLE'))
        
        st.divider()
        
        # Display decision info
        st.markdown("### 🎯 Last Decision")
        col_d1, col_d2, col_d3 = st.columns(3)
        
        with col_d1:
            st.metric("Decision", data.get('last_decision', 'NONE'))
        
        with col_d2:
            st.metric("Total Decisions", data.get('total_decisions', 0))
        
        with col_d3:
            st.metric("Timestamp", 
                     data.get('timestamp', 'N/A')[-8:] if data.get('timestamp') else 'N/A')
        
        st.divider()
        
        # Full data
        st.markdown("### 📋 Full Status Data")
        st.json(data)
    else:
        st.info("Click 'Refresh Sensor Data' to load the latest readings")

# ============================================================================
# TAB 3: MANUAL SENSOR INPUT
# ============================================================================

with tab3:
    st.subheader("🎮 Manual Sensor Input & Decision Testing")
    st.info("Send custom sensor values to test the AI decision engine")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        front_dist = st.slider("Front Distance (cm)", 0, 200, 50)
    
    with col2:
        left_dist = st.slider("Left Distance (cm)", 0, 200, 100)
    
    with col3:
        right_dist = st.slider("Right Distance (cm)", 0, 200, 80)
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        encoder_pulses = st.number_input("Encoder Pulses", 0, 10000, 500)
    
    with col5:
        target_distance = st.number_input("Target Distance (cm)", 0, 500, 100)
    
    with col6:
        stage = st.selectbox("Navigation Stage", ["A→B", "B→C", "IDLE"])
    
    st.divider()
    
    if st.button("🚀 Get AI Decision", type="primary", use_container_width=True):
        try:
            response = requests.post(
                f"{st.session_state.api_url}/api/robot/decide",
                json={
                    "front_dist": float(front_dist),
                    "left_dist": float(left_dist),
                    "right_dist": float(right_dist),
                    "encoder_pulses": int(encoder_pulses),
                    "stage": stage,
                    "target_distance": float(target_distance)
                },
                timeout=5
            )
            
            if response.status_code == 200:
                decision = response.json()
                
                st.success("✓ Decision Received!")
                st.divider()
                
                # Display decision
                col_dec1, col_dec2, col_dec3 = st.columns(3)
                with col_dec1:
                    st.metric("🎯 Decision", decision['decision'])
                with col_dec2:
                    st.metric("⚡ Speed", decision['speed'])
                with col_dec3:
                    st.metric("🔄 Decision #", decision['decision_number'])
                
                st.divider()
                
                # Motor commands
                st.markdown("### 🏎️ Motor Commands")
                col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                
                with col_m1:
                    st.info(f"Left Motor Speed\n{decision['motor_left_speed']}")
                with col_m2:
                    st.info(f"Left Direction\n{decision['motor_left_direction']}")
                with col_m3:
                    st.info(f"Right Motor Speed\n{decision['motor_right_speed']}")
                with col_m4:
                    st.info(f"Right Direction\n{decision['motor_right_direction']}")
                
                st.divider()
                
                # Explanation
                st.markdown("### 💭 AI Reasoning")
                st.markdown(f"**{decision['explanation']}**")
                
                # Full JSON
                with st.expander("📋 Full Response JSON"):
                    st.json(decision)
            else:
                st.error(f"API Error: {response.status_code}")
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
---
**🤖 Robot AI Brain** | Real-time Autonomous Navigation Engine  
Built with Streamlit + Flask | ESP32 + Ultrasonic + Encoder Wheel  
© 2026 | Status: Ready for Operation
""")