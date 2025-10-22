# 🖥️ Smart Desk Monitor – Quick Start Guide

## ✅ Installation Complete!

You now have **two versions** of the Smart Desk Monitor:

### 1. **smart_desk_monitor_simple.py** ⭐ RECOMMENDED for Python 3.13
- ✅ Works with your current Python version (3.13.6)
- ✅ Already installed and ready to use!
- Uses OpenCV's built-in face and eye detection
- All core features included

### 2. **smart_desk_monitor.py** (Advanced - Requires Python 3.8-3.12)
- Full pose estimation with MediaPipe
- More accurate slouch detection
- Advanced posture tracking
- Requires Python 3.8-3.12 (not compatible with 3.13 yet)

## 🚀 How to Run

### Option 1: Run the Simplified Version (Recommended)
```bash
python smart_desk_monitor_simple.py
```

### Option 2: Run from PowerShell
```powershell
cd "d:\face meme"
python smart_desk_monitor_simple.py
```

## 🎮 Controls

Once running, use these keyboard shortcuts:

- **Q** - Quit the application
- **R** - Reset session statistics (start fresh)
- **S** - Save current session report
- **C** - Recalibrate (if detection becomes inaccurate)

## 📋 Features You'll Get

### ✅ Implemented Features:

1. **Face Detection & Distance Monitoring**
   - Alerts when too close to screen
   - Warns when too far away
   - Tracks optimal viewing distance

2. **Eye Tracking & Blink Detection**
   - Counts blinks automatically
   - Calculates blink rate per minute
   - Warns about low blink rate (eye strain risk)

3. **Attention Monitoring**
   - Detects when you look away
   - Tracks focused vs. distracted time
   - Alerts after prolonged inattention

4. **Real-time Statistics**
   - Live session timer
   - Focus percentage
   - Blink count and rate
   - Time away from screen

5. **Session Reports**
   - Detailed health analysis
   - Personalized recommendations
   - Saved automatically on exit

## 📊 Understanding the Display

### Status Indicators:
- **Green box** = Good position ✅
- **Orange box** = Too close ⚠️
- **Yellow box** = Too far or not centered ⚠️
- **Cyan box** = Face not centered properly

### Alert Messages:
- 🔴 **Red alerts** = Critical (too close)
- 🟡 **Yellow alerts** = Warning (attention needed)
- 🔵 **Blue alerts** = Health tip (blink rate)

## 💡 Tips for Best Results

### Setup:
1. **Lighting**: Ensure your face is well-lit (front lighting is best)
2. **Camera**: Position at eye level, about arm's length away
3. **Background**: Clear background improves detection
4. **Calibration**: Start in a comfortable, upright position

### During Use:
- Let it calibrate for 5-10 seconds when you first start
- Sit naturally - the system adapts to your comfortable position
- Respond to alerts promptly to build good habits
- Check session reports to track improvement

## 🏥 Health Recommendations

### The 20-20-20 Rule:
Every **20 minutes**, look at something **20 feet away** for **20 seconds**

### Optimal Blink Rate:
- Normal: 15-20 blinks per minute
- Low: < 10 blinks per minute (eye strain risk)
- Very low: < 5 blinks per minute (take a break!)

### Posture Tips:
- Keep screen at arm's length (about 50-70 cm)
- Screen top should be at or slightly below eye level
- Sit with back supported and feet flat on floor

## 🔧 Troubleshooting

### "No face detected"
- Improve lighting
- Move closer to camera
- Ensure camera is working (check privacy settings)
- Try pressing 'C' to recalibrate

### "False alerts"
- Press 'C' to recalibrate
- Adjust your seating position
- Ensure stable lighting conditions

### "Low FPS / Lag"
- Close other applications
- Reduce camera resolution (edit .py file)
- Check CPU usage

## 📈 Understanding Your Reports

Reports are saved as: `session_report_YYYY-MM-DD_HH-MM-SS.txt`

### Key Metrics:
- **Focus Rate** > 75% = Excellent
- **Focus Rate** 50-75% = Good
- **Focus Rate** < 50% = Needs improvement

- **Posture Score** > 80% = Excellent
- **Posture Score** 60-80% = Good
- **Posture Score** < 60% = Needs attention

## 🎯 Next Steps

### To Upgrade to Full Version (Optional):
1. Install Python 3.11 or 3.12 (alongside 3.13)
2. Create virtual environment with older Python
3. Install MediaPipe: `pip install mediapipe`
4. Run: `python smart_desk_monitor.py`

### Customize Settings:
Edit the Python file to adjust:
- Alert thresholds
- Alert sounds
- Display colors
- Cooldown timers

## 📞 Need Help?

Check the main README.md for:
- Detailed feature documentation
- Advanced customization options
- Contribution guidelines
- Future enhancement ideas

---

## 🎉 Ready to Start!

Just run:
```bash
python smart_desk_monitor_simple.py
```

**Stay healthy, stay focused! 💪👀**
