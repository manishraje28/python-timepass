"""
Smart Desk Monitor - Simplified Version
Real-time monitoring using OpenCV's built-in features
Compatible with Python 3.13+
"""

import cv2
import numpy as np
import time
import winsound
from datetime import datetime
from collections import deque
import threading

class SimplifiedDeskMonitor:
    def __init__(self):
        # Load pre-trained models
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Monitoring parameters
        self.baseline_face_size = None
        self.distance_threshold_near = 1.3  # Face size ratio (too close)
        self.distance_threshold_far = 0.7   # Face size ratio (too far)
        self.away_time_threshold = 5  # Seconds looking away before alert
        
        # Tracking variables
        self.looking_away_start = None
        self.blink_counter = 0
        self.blink_times = deque(maxlen=100)
        self.last_blink_time = time.time()
        self.eye_closed_frames = 0
        
        # Session statistics
        self.session_start = time.time()
        self.total_away_time = 0
        self.total_focused_time = 0
        self.total_too_close_time = 0
        self.total_good_posture_time = 0
        self.last_check = time.time()
        
        # Alert cooldowns
        self.last_distance_alert = 0
        self.last_attention_alert = 0
        self.alert_cooldown = 5  # Seconds between alerts
        
        # State tracking
        self.is_looking_away = False
        self.calibrated = False
        
    def play_alert_sound(self):
        """Play alert sound in separate thread"""
        def play():
            try:
                winsound.Beep(1000, 300)  # 1000 Hz for 300ms
            except:
                pass
        
        thread = threading.Thread(target=play)
        thread.daemon = True
        thread.start()
    
    def detect_face_and_eyes(self, frame):
        """Detect face and eyes using Haar Cascades"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            return None, None, None
        
        # Get the largest face (closest to camera)
        face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = face
        
        # Detect eyes in face region
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 5)
        
        return face, eyes, roi_gray
    
    def analyze_position(self, face, frame_shape):
        """Analyze face position and distance"""
        if face is None:
            return {
                'face_detected': False,
                'too_close': False,
                'too_far': False,
                'centered': False,
                'face_size': 0
            }
        
        x, y, w, h = face
        frame_h, frame_w = frame_shape[:2]
        
        # Calculate face size (for distance estimation)
        face_size = w * h
        
        # Calibration
        if not self.calibrated and face_size > 5000:
            self.baseline_face_size = face_size
            self.calibrated = True
        
        # Check distance
        too_close = False
        too_far = False
        if self.baseline_face_size:
            size_ratio = face_size / self.baseline_face_size
            too_close = size_ratio > self.distance_threshold_near
            too_far = size_ratio < self.distance_threshold_far
        
        # Check if centered
        face_center_x = x + w // 2
        centered = (frame_w * 0.3 < face_center_x < frame_w * 0.7)
        
        return {
            'face_detected': True,
            'too_close': too_close,
            'too_far': too_far,
            'centered': centered,
            'face_size': face_size,
            'face_rect': face
        }
    
    def analyze_eyes(self, eyes, face):
        """Analyze eye state for blinks and attention"""
        if face is None:
            return {
                'eyes_detected': 0,
                'looking_at_screen': False,
                'blink_detected': False
            }
        
        num_eyes = len(eyes)
        
        # Blink detection (eyes disappear)
        current_time = time.time()
        blink_detected = False
        
        if num_eyes < 2:
            self.eye_closed_frames += 1
        else:
            if self.eye_closed_frames >= 2 and self.eye_closed_frames <= 8:
                # Valid blink (2-8 frames)
                if current_time - self.last_blink_time > 0.2:
                    self.blink_counter += 1
                    self.blink_times.append(current_time)
                    self.last_blink_time = current_time
                    blink_detected = True
            self.eye_closed_frames = 0
        
        # Calculate blink rate (blinks per minute)
        recent_blinks = [t for t in self.blink_times if current_time - t < 60]
        blink_rate = len(recent_blinks)
        
        # Looking at screen if eyes are detected
        looking_at_screen = num_eyes >= 1
        
        return {
            'eyes_detected': num_eyes,
            'looking_at_screen': looking_at_screen,
            'blink_detected': blink_detected,
            'blink_rate': blink_rate
        }
    
    def draw_alerts(self, frame, position_info, eye_info):
        """Draw alerts and information on frame"""
        h, w = frame.shape[:2]
        current_time = time.time()
        
        alerts = []
        
        # Position alerts
        if position_info and position_info['too_close']:
            alerts.append(("⚠️ TOO CLOSE! Move back from screen", (0, 165, 255)))
            if current_time - self.last_distance_alert > self.alert_cooldown:
                self.play_alert_sound()
                self.last_distance_alert = current_time
        
        if position_info and position_info['too_far']:
            alerts.append(("⚠️ Too far from screen", (0, 255, 255)))
        
        # Attention alerts
        if eye_info and position_info:
            if not eye_info['looking_at_screen'] or not position_info['face_detected']:
                if self.looking_away_start is None:
                    self.looking_away_start = current_time
                elif current_time - self.looking_away_start > self.away_time_threshold:
                    alerts.append(("👀 FOCUS! Look at your work", (0, 255, 255)))
                    if current_time - self.last_attention_alert > self.alert_cooldown:
                        self.play_alert_sound()
                        self.last_attention_alert = current_time
            else:
                self.looking_away_start = None
        
        # Blink rate warning
        if eye_info and eye_info.get('blink_rate', 0) < 10 and eye_info.get('blink_rate', 0) > 0:
            alerts.append(("😔 Low blink rate - Blink more often!", (0, 140, 255)))
        
        # Draw alerts
        y_offset = 30
        for alert, color in alerts:
            cv2.rectangle(frame, (10, y_offset - 25), (w - 10, y_offset + 5), (0, 0, 0), -1)
            cv2.putText(frame, alert, (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 40
        
        return frame
    
    def draw_visualizations(self, frame, face, eyes, position_info):
        """Draw face and eye detection boxes"""
        if face is not None:
            x, y, w, h = face
            
            # Face box color based on distance
            color = (0, 255, 0)  # Green = good
            if position_info['too_close']:
                color = (0, 165, 255)  # Orange = too close
            elif position_info['too_far']:
                color = (0, 255, 255)  # Yellow = too far
            elif not position_info['centered']:
                color = (255, 255, 0)  # Cyan = not centered
            
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            
            # Draw eyes
            if eyes is not None:
                for (ex, ey, ew, eh) in eyes:
                    cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0, 255, 0), 2)
        
        return frame
    
    def draw_stats_panel(self, frame, eye_info):
        """Draw statistics panel"""
        h, w = frame.shape[:2]
        session_duration = time.time() - self.session_start
        
        # Create semi-transparent panel
        panel_height = 200
        overlay = frame.copy()
        cv2.rectangle(overlay, (w - 350, 10), (w - 10, panel_height), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        # Calculate focus percentage
        focus_percentage = 0
        if session_duration > 0:
            focus_percentage = (self.total_focused_time / session_duration * 100)
        
        # Stats text
        stats = [
            f"📊 SESSION STATS",
            f"Time: {int(session_duration // 60)}m {int(session_duration % 60)}s",
            f"",
            f"👁️  Blinks: {self.blink_counter}",
            f"Rate: {eye_info.get('blink_rate', 0)}/min",
            f"",
            f"🎯 Focused: {int(self.total_focused_time // 60)}m",
            f"😴 Away: {int(self.total_away_time // 60)}m",
            f"Focus: {focus_percentage:.1f}%"
        ]
        
        y_pos = 35
        for stat in stats:
            cv2.putText(frame, stat, (w - 340, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 22
        
        return frame
    
    def update_statistics(self, position_info, eye_info):
        """Update session statistics"""
        if not position_info or not eye_info:
            return
            
        current_time = time.time()
        time_delta = current_time - self.last_check
        
        face_detected = position_info.get('face_detected', False)
        looking = eye_info.get('looking_at_screen', False)
        
        if face_detected and looking:
            self.total_focused_time += time_delta
            if not position_info.get('too_close', False):
                self.total_good_posture_time += time_delta
            else:
                self.total_too_close_time += time_delta
        else:
            self.total_away_time += time_delta
        
        self.is_looking_away = not (face_detected and looking)
        self.last_check = current_time
    
    def save_session_report(self):
        """Save session report to file"""
        session_duration = time.time() - self.session_start
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        focus_rate = (self.total_focused_time / session_duration * 100) if session_duration > 0 else 0
        posture_score = (self.total_good_posture_time / session_duration * 100) if session_duration > 0 else 0
        avg_blink_rate = (self.blink_counter / (session_duration / 60)) if session_duration > 60 else 0
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║     SMART DESK MONITOR - SESSION REPORT                 ║
╚══════════════════════════════════════════════════════════╝

📅 Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

⏱️  SESSION DURATION
   Total Time: {int(session_duration // 3600)}h {int((session_duration % 3600) // 60)}m {int(session_duration % 60)}s

👁️  ATTENTION & FOCUS
   Focused Time: {int(self.total_focused_time // 60)}m {int(self.total_focused_time % 60)}s
   Looking Away: {int(self.total_away_time // 60)}m {int(self.total_away_time % 60)}s
   Focus Rate: {focus_rate:.1f}%
   
👀 BLINK STATISTICS
   Total Blinks: {self.blink_counter}
   Avg Blink Rate: {avg_blink_rate:.1f} blinks/min
   Recommended: 15-20 blinks/min
   Status: {"✅ Good" if 12 <= avg_blink_rate <= 25 else "⚠️ Needs attention"}

🪑 POSTURE ANALYSIS
   Good Distance: {int(self.total_good_posture_time // 60)}m
   Too Close: {int(self.total_too_close_time // 60)}m
   Posture Score: {posture_score:.1f}%

💡 RECOMMENDATIONS
"""
        
        # Add recommendations
        if self.total_too_close_time / session_duration > 0.3:
            report += "   ⚠️  Sitting too close frequently. Adjust your desk setup.\n"
        
        if avg_blink_rate < 12:
            report += "   ⚠️  Low blink rate. Follow the 20-20-20 rule: Every 20 min,\n"
            report += "       look at something 20 feet away for 20 seconds.\n"
        
        if self.total_away_time / session_duration > 0.4:
            report += "   ⚠️  Frequently distracted. Consider focus techniques like Pomodoro.\n"
        
        if focus_rate > 75:
            report += "   ✅ Excellent focus maintained! Great job!\n"
        
        if posture_score > 80:
            report += "   ✅ Good distance from screen maintained!\n"
        
        if 12 <= avg_blink_rate <= 25:
            report += "   ✅ Healthy blink rate - your eyes are well hydrated!\n"
        
        report += "\n" + "="*60 + "\n"
        
        # Save to file
        filename = f"session_report_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Session report saved to: {filename}")
        print(report)
    
    def run(self):
        """Main monitoring loop"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("🚀 Smart Desk Monitor Started!")
        print("📹 Calibrating... Please sit at a comfortable distance and look at camera")
        print("\n💡 Controls:")
        print("   Q - Quit")
        print("   R - Reset statistics")
        print("   S - Save session report")
        print("   C - Recalibrate\n")
        
        fps_time = time.time()
        fps_counter = 0
        fps = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame for mirror effect
            frame = cv2.flip(frame, 1)
            
            # Detect face and eyes
            face, eyes, roi_gray = self.detect_face_and_eyes(frame)
            
            # Analyze position and attention
            position_info = self.analyze_position(face, frame.shape)
            eye_info = self.analyze_eyes(eyes, face)
            
            # Update statistics
            self.update_statistics(position_info, eye_info)
            
            # Draw visualizations
            if face is not None:
                frame = self.draw_visualizations(frame, face, eyes, position_info)
            
            # Draw alerts and stats
            frame = self.draw_alerts(frame, position_info, eye_info)
            frame = self.draw_stats_panel(frame, eye_info)
            
            # Show calibration status
            if not self.calibrated:
                cv2.putText(frame, "🎯 Calibrating... Sit comfortably and look at camera", 
                           (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (0, 255, 255), 2)
            
            # Calculate and display FPS
            fps_counter += 1
            if time.time() - fps_time > 1:
                fps = fps_counter
                fps_counter = 0
                fps_time = time.time()
            
            cv2.putText(frame, f"FPS: {fps}", (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            # Display frame
            cv2.imshow('Smart Desk Monitor - Posture & Focus Tracker', frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                self.reset_statistics()
                print("📊 Statistics reset!")
            elif key == ord('s'):
                self.save_session_report()
            elif key == ord('c'):
                self.calibrated = False
                self.baseline_face_size = None
                print("🔄 Recalibrating...")
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        
        # Final report
        print("\n🏁 Session ended!")
        self.save_session_report()
    
    def reset_statistics(self):
        """Reset all statistics"""
        self.session_start = time.time()
        self.total_away_time = 0
        self.total_focused_time = 0
        self.total_too_close_time = 0
        self.total_good_posture_time = 0
        self.blink_counter = 0
        self.blink_times.clear()


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║    SMART DESK MONITOR - POSTURE & FOCUS TRACKER          ║
    ║              Simplified Edition (Python 3.13)             ║
    ╚═══════════════════════════════════════════════════════════╝
    
    This version uses OpenCV's built-in face and eye detection.
    For advanced pose estimation, please use Python 3.8-3.12 with MediaPipe.
    """)
    
    monitor = SimplifiedDeskMonitor()
    monitor.run()
