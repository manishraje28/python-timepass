"""
Test script to verify OpenCV installation and camera access
"""

import cv2
import sys

def test_camera():
    print("🔍 Testing camera access...")
    
    # Try to open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ ERROR: Could not access camera!")
        print("   Please check:")
        print("   - Camera is connected")
        print("   - No other app is using the camera")
        print("   - Camera permissions are granted")
        return False
    
    print("✅ Camera accessed successfully!")
    
    # Read a test frame
    ret, frame = cap.read()
    if not ret:
        print("❌ ERROR: Could not read frame from camera!")
        cap.release()
        return False
    
    print(f"✅ Frame captured: {frame.shape[1]}x{frame.shape[0]}")
    
    # Test face detection
    print("🔍 Testing face detection...")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    if face_cascade.empty():
        print("❌ ERROR: Could not load face detection model!")
        cap.release()
        return False
    
    print("✅ Face detection model loaded!")
    
    # Try to detect face
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    
    if len(faces) > 0:
        print(f"✅ Face detected! ({len(faces)} face(s) found)")
    else:
        print("⚠️  No face detected in first frame (this is OK - just face the camera)")
    
    cap.release()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED! Ready to run the monitor!")
    print("="*60)
    return True

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║          SMART DESK MONITOR - SYSTEM TEST                ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    try:
        if test_camera():
            print("\n💡 To start monitoring, run:")
            print("   python smart_desk_monitor_simple.py")
            print("\n   Or double-click: run_monitor.bat")
        else:
            print("\n❌ Tests failed. Please fix the issues above.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nPlease ensure OpenCV is installed:")
        print("   pip install opencv-python")
        sys.exit(1)
