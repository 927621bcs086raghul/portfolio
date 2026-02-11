# 🚀 Quick Start Guide - Robot AI Brain

Get your robot AI brain running in 3 minutes!

---

## Step 1️⃣: Install Dependencies (1 minute)

```bash
pip install -r requirements.txt
```

Wait for installation to complete...

---

## Step 2️⃣: Start the Backend Server (1 minute)

Open **PowerShell** or **Command Prompt** and run:

```bash
cd "c:\Users\sriha\OneDrive\Pictures\VR 47 2"
python backend.py
```

You should see:
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

✓ **Backend is now running!** Keep this terminal open.

---

## Step 3️⃣: Start the Streamlit Chatbot UI (1 minute)

Open **another PowerShell/Command Prompt** and run:

```bash
cd "c:\Users\sriha\OneDrive\Pictures\VR 47 2"
streamlit run app.py
```

You should see:
```
You can now view your Streamlit app in your browser.

  URL: http://localhost:8501
```

✓ **UI is now running!** Your browser should automatically open.

---

## Step 4️⃣: Test the System

### In the Streamlit Dashboard:

1. **Go to Sidebar** → Click **"🔗 Test API Connection"**
   - Should show: `✓ Connected to Robot AI Brain!`

2. **Go to "🎮 Manual Control" Tab**
   - Set: Front: 50cm, Left: 100cm, Right: 80cm
   - Click **"🚀 Get AI Decision"**
   - Should see: **Decision: FORWARD** ✓

3. **Go to "💬 Chat" Tab**
   - Click **"⬅️➡️ Left free aa?"**
   - Robot answers: *LEFT: free, RIGHT: free, Choose RIGHT*

✓ **All systems operational!**

---

## 📡 Your First Real Robot Test

Once you have your ESP32 configured:

### ESP32 will POST sensor data:
```
POST http://your-computer-ip:5000/api/robot/decide

{
    "front_dist": 42.3,
    "left_dist": 55.0,
    "right_dist": 48.2,
    "encoder_pulses": 1200,
    "stage": "A→B",
    "target_distance": 100
}
```

### Your robot receives back:
```json
{
    "decision": "FORWARD",
    "speed": 180,
    "motor_left_speed": 180,
    "motor_right_speed": 180,
    "explanation": "✓ ALL PATHS CLEAR! Moving FORWARD..."
}
```

### Robot controls motors and repeats every 100ms!

---

## 🎯 Common Tasks

### View Hardware Configuration
- **Sidebar** → **"📋 Load Hardware Config"**
- Shows all GPIO pins, thresholds, encoder specs

### Check Robot Status
- **Sidebar** → **"📊 Get Robot Status"**
- Real-time sensor readings and decision count

### Reset Everything
- **Sidebar** → **"🔄 Reset Robot Brain"**
- Clears all state for fresh start

### Ask Robot Questions (Tamil supported!)
- **Chat Tab** → Type or click preset questions
- Works with English & Tamil

---

## ⚙️ Quick Configuration

Edit [config.py](config.py) only if you have:
- Different GPIO pins
- Different wheel size
- Different sensor thresholds
- Different motor speeds

```python
# Example: Change safe distance threshold
SafetyConfig.SAFE_DISTANCE = 25  # Changed from 30cm

# Example: Change wheel diameter
EncoderConfig.WHEEL_DIAMETER_CM = 7.0  # Changed from 6.5cm
```

Then restart `backend.py` for changes to take effect.

---

## 🔗 Network Access

### Connect from Another Computer

1. Find your laptop's IP address:
   ```bash
   ipconfig
   # Look for "IPv4 Address" like 192.168.x.x
   ```

2. ESP32 connects to:
   ```
   http://192.168.x.x:5000/api/robot/decide
   ```

3. Access UI from another PC:
   ```
   http://192.168.x.x:8501
   ```

---

## 🐛 If Something Goes Wrong

### Backend won't start?
```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Can't connect to API?
```bash
# Verify server is running
curl http://localhost:5000/api/health
```

### Streamlit won't start?
```bash
# Reinstall Streamlit
pip uninstall streamlit
pip install streamlit==1.28.0
```

### Sensor decisions wrong?
- Check GPIO pins in [config.py](config.py)
- Adjust thresholds in `SafetyConfig`
- Test with manual sliders first

---

## 📚 What Each File Does

| File | Does | When to Edit |
|------|------|--------------|
| `app.py` | Web chatbot UI | Customize dashboard layout |
| `backend.py` | API server | Add new endpoints |
| `robot_brain.py` | AI decision logic | Change decision algorithm |
| `config.py` | Hardware settings | Different GPIO pins / thresholds |
| `requirements.txt` | Dependencies | Add new Python packages |

---

## ✨ You're All Set! 

- ✓ Backend running locally
- ✓ Streamlit UI working
- ✓ API ready for ESP32
- ✓ Real-time decisions ready

**Next:** 
1. Configure your ESP32 to send sensor data
2. Connect motors and sensors to GPIO pins
3. Upload a sketch that POSTs to `/api/robot/decide`
4. Watch your robot navigate autonomously!

---

**Questions?** Open README.md for detailed documentation.
