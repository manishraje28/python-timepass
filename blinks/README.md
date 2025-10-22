# 🖥️ Smart Desk Monitor – Posture & Focus Tracker

A real-time computer vision application that monitors your posture, attention, and focus while working or studying. Get instant feedback to improve productivity and reduce health problems!

## ✨ Features

### 1. 🪑 Posture Detection
- **Slouch Detection**: Uses pose estimation to detect when you're slouching or leaning too far forward
- **Distance Monitoring**: Alerts when you're too close or too far from the screen
- **Real-time Feedback**: Visual and audio alerts to correct your posture
- **Posture Tracking**: Records how long you maintain good posture vs. slouching

### 2. 👁️ Attention & Eye Tracking
- **Gaze Detection**: Monitors if you're looking at the screen or away
- **Blink Rate Analysis**: Tracks your blink rate to prevent eye strain
- **Focus Alerts**: Notifies you when you've been looking away for too long
- **Eye Strain Prevention**: Warns when blink rate is too low (risk of dry eyes)

### 3. 📊 Focus Monitoring
- **Session Tracking**: Measures total focused time vs. distracted time
- **Real-time Statistics**: Live dashboard showing session metrics
- **Daily Reports**: Detailed session reports with recommendations
- **Focus Score**: Calculate your focus percentage for each session

### 4. 🎯 Smart Alerts
- **Customizable Thresholds**: Adjust sensitivity for posture and attention
- **Alert Cooldown**: Prevents alert spam with configurable cooldown periods
- **Visual & Audio Feedback**: On-screen warnings and sound alerts
- **Non-intrusive**: Alerts appear only when needed

## 🚀 Installation

1. **Clone or download this project**

2. **Install required packages:**
```bash
pip install -r requirements.txt
```

### Required Dependencies:
- `opencv-python` - Computer vision and webcam handling
- `mediapipe` - Pose estimation and face mesh detection
- `numpy` - Numerical computations

## 📖 Usage

### Basic Usage

Run the main application:
```bash
python smart_desk_monitor.py
```

### Controls

- **Q**: Quit the application
- **R**: Reset session statistics
- **S**: Save current session report

### First-time Setup

1. **Calibration**: When you first start, sit in a good posture and face the camera
2. The system will calibrate based on your initial position
3. Maintain this reference posture for best results

### Tips for Best Results

- **Lighting**: Ensure good, even lighting on your face
- **Camera Position**: Place camera at eye level, about arm's length away
- **Background**: Use a clear background for better detection
- **Clothing**: Avoid clothing that matches your background

## 📊 Understanding the Interface

### Stats Panel (Top Right)
- **Session**: Total session duration
- **Blinks**: Number of blinks detected
- **Focused**: Time spent looking at screen
- **Away**: Time spent looking away
- **Slouching**: Time spent in poor posture
- **Status**: Current posture/focus status

### Alert Messages
- 🔴 **Red**: Critical posture issues (slouching)
- 🟡 **Orange**: Distance warnings (too close/far)
- 🟡 **Yellow**: Attention alerts (looking away)
- 🔵 **Blue**: Eye strain warning (low blink rate)

## 📄 Session Reports

After each session, a detailed report is generated containing:

- **Session Duration**: Total time monitored
- **Attention Metrics**: Focus time, distraction time, focus percentage
- **Blink Statistics**: Total blinks and average blink rate
- **Posture Analysis**: Good posture time vs. slouching time
- **Personalized Recommendations**: Based on your session data

Reports are saved as `session_report_YYYY-MM-DD_HH-MM-SS.txt`

## ⚙️ Customization

You can adjust the monitoring parameters in the `SmartDeskMonitor` class:

```python
# Posture thresholds
self.slouch_threshold = 0.15  # Increase for less sensitive slouch detection
self.distance_threshold_near = 150  # Adjust "too close" distance
self.distance_threshold_far = 400  # Adjust "too far" distance

# Attention thresholds
self.away_time_threshold = 5  # Seconds before "looking away" alert
self.blink_threshold = 0.2  # Eye aspect ratio for blink detection

# Alert settings
self.alert_cooldown = 5  # Seconds between repeated alerts
```

## 🏥 Health Benefits

### Posture Improvement
- Reduces neck and back pain
- Prevents long-term spinal issues
- Improves breathing and circulation

### Eye Health
- Reduces eye strain and fatigue
- Prevents dry eye syndrome
- Reminds you to follow the **20-20-20 rule**
  (Every 20 minutes, look at something 20 feet away for 20 seconds)

### Productivity
- Tracks focus and attention
- Identifies distraction patterns
- Helps maintain work-life balance

## 🔬 Technical Details

### Technologies Used
- **MediaPipe Pose**: 33-point body pose estimation
- **MediaPipe Face Mesh**: 468 facial landmarks for eye tracking
- **OpenCV**: Video capture and image processing
- **Eye Aspect Ratio (EAR)**: Blink detection algorithm

### Performance
- Runs at ~30 FPS on modern hardware
- Low CPU usage (<20% on average)
- Works with standard webcams (720p recommended)

## 🐛 Troubleshooting

### Camera Not Detected
```python
# Try changing camera index in smart_desk_monitor.py
cap = cv2.VideoCapture(1)  # Change 0 to 1, 2, etc.
```

### Poor Detection Accuracy
- Improve lighting conditions
- Ensure full upper body is visible
- Move to a clearer background
- Adjust camera angle

### False Alerts
- Recalibrate by restarting the app in good posture
- Adjust threshold values (see Customization section)
- Reset statistics with 'R' key

## 🎯 Future Enhancements (Optional)

### Emotion Detection
Add emotion/stress detection using FER or DeepFace:
```bash
pip install deepface
```

### Break Reminders
- Pomodoro timer integration
- Stretch exercise suggestions
- Eye exercise prompts

### Cloud Sync
- Upload session reports to cloud
- Track progress over time
- Compare daily/weekly stats

### Multi-user Support
- Profile management
- Personalized thresholds
- Individual progress tracking

## 📝 Notes

- This application is for **personal wellness** and **productivity improvement**
- Not a replacement for professional ergonomic assessment
- Always consult healthcare professionals for persistent pain or issues
- Camera feed is processed **locally only** - no data is sent anywhere

## 🤝 Contributing

Feel free to enhance this project with:
- Emotion detection integration
- Machine learning-based posture scoring
- Mobile app companion
- Custom alert sounds/themes
- Multi-language support

## 📜 License

This project is open source and available for personal and educational use.

## 🙏 Acknowledgments

- MediaPipe by Google for pose and face detection
- OpenCV community for computer vision tools
- Inspired by the need for healthier work habits in the digital age

---

**Stay healthy, stay focused! 💪👀**
