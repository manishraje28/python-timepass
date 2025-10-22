"""
Smart Desk Monitor - Posture & Focus Tracker
Real-time monitoring system for posture, attention, and focus while working
"""

import cv2
import mediapipe as mp
import numpy as np
import time
import winsound
from datetime import datetime, timedelta
from collections import deque
import threading

class SmartDeskMonitor:
    def __init__(self):
        # Initialize MediaPipe components
        self.mp_pose = mp.solutions.pose
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Initialize pose and face mesh
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Monitoring parameters
        self.slouch_threshold = 0.15  # Angle threshold for slouching
        self.distance_threshold_near = 150  # Too close to screen
        self.distance_threshold_far = 400  # Too far from screen
        self.away_time_threshold = 5  # Seconds looking away before alert
        self.blink_threshold = 0.2  # Eye aspect ratio threshold
        
        # Tracking variables
        self.looking_away_start = None
        self.blink_counter = 0
        self.blink_times = deque(maxlen=100)
        self.last_blink_time = time.time()
        
        # Session statistics
        self.session_start = time.time()
        self.total_slouch_time = 0
        self.total_away_time = 0
        self.total_focused_time = 0
        self.last_posture_check = time.time()
        self.is_slouching = False
        self.is_looking_away = False
        
        # Alert cooldowns
        self.last_posture_alert = 0
        self.last_distance_alert = 0
        self.last_attention_alert = 0
        self.alert_cooldown = 5  # Seconds between alerts
        
        # Reference measurements (calibrated on first good frame)
        self.reference_shoulder_distance = None
        self.calibrated = False
        
    def calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def calculate_distance(self, point1, point2):
        """Calculate Euclidean distance between two points"""
        return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    
    def eye_aspect_ratio(self, eye_landmarks):
        """Calculate eye aspect ratio to detect blinks"""
        # Vertical distances
        v1 = self.calculate_distance(eye_landmarks[1], eye_landmarks[5])
        v2 = self.calculate_distance(eye_landmarks[2], eye_landmarks[4])
        
        # Horizontal distance
        h = self.calculate_distance(eye_landmarks[0], eye_landmarks[3])
        
        # Eye aspect ratio
        ear = (v1 + v2) / (2.0 * h)
        return ear
    
    def check_posture(self, pose_landmarks, frame_shape):
        """Analyze posture and detect slouching"""
        h, w = frame_shape[:2]
        
        # Get key landmarks
        left_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_ear = pose_landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_EAR]
        right_ear = pose_landmarks.landmark[self.mp_pose.PoseLandmark.RIGHT_EAR]
        nose = pose_landmarks.landmark[self.mp_pose.PoseLandmark.NOSE]
        
        # Convert to pixel coordinates
        left_shoulder_coords = [left_shoulder.x * w, left_shoulder.y * h]
        right_shoulder_coords = [right_shoulder.x * w, right_shoulder.y * h]
        left_ear_coords = [left_ear.x * w, left_ear.y * h]
        right_ear_coords = [right_ear.x * w, right_ear.y * h]
        nose_coords = [nose.x * w, nose.y * h]
        
        # Calculate shoulder midpoint
        shoulder_midpoint = [
            (left_shoulder_coords[0] + right_shoulder_coords[0]) / 2,
            (left_shoulder_coords[1] + right_shoulder_coords[1]) / 2
        ]
        
        # Calculate ear midpoint
        ear_midpoint = [
            (left_ear_coords[0] + right_ear_coords[0]) / 2,
            (left_ear_coords[1] + right_ear_coords[1]) / 2
        ]
        
        # Check slouching (head forward of shoulders)
        head_shoulder_offset = (ear_midpoint[0] - shoulder_midpoint[0]) / w
        
        # Calculate shoulder width for distance estimation
        shoulder_distance = self.calculate_distance(left_shoulder_coords, right_shoulder_coords)
        
        # Calibration
        if not self.calibrated and shoulder_distance > 50:
            self.reference_shoulder_distance = shoulder_distance
            self.calibrated = True
        
        # Estimate distance from camera (inverse of shoulder width)
        distance_ratio = 1.0
        if self.reference_shoulder_distance:
            distance_ratio = self.reference_shoulder_distance / shoulder_distance if shoulder_distance > 0 else 1.0
        
        is_slouching = head_shoulder_offset > self.slouch_threshold
        is_too_close = shoulder_distance > self.distance_threshold_near if self.reference_shoulder_distance else False
        is_too_far = shoulder_distance < self.distance_threshold_far if self.reference_shoulder_distance else False
        
        return {
            'slouching': is_slouching,
            'too_close': is_too_close,
            'too_far': is_too_far,
            'head_shoulder_offset': head_shoulder_offset,
            'shoulder_distance': shoulder_distance,
            'nose_coords': nose_coords,
            'shoulder_midpoint': shoulder_midpoint
        }
    
    def check_attention(self, face_landmarks, frame_shape):
        """Check if user is looking at screen and track blinks"""
        h, w = frame_shape[:2]
        
        # Get eye landmarks (MediaPipe Face Mesh indices)
        # Left eye: 33, 160, 158, 133, 153, 144
        # Right eye: 362, 385, 387, 263, 373, 380
        
        left_eye_indices = [33, 160, 158, 133, 153, 144]
        right_eye_indices = [362, 385, 387, 263, 373, 380]
        
        left_eye = [(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h) 
                    for i in left_eye_indices]
        right_eye = [(face_landmarks.landmark[i].x * w, face_landmarks.landmark[i].y * h) 
                     for i in right_eye_indices]
        
        # Calculate eye aspect ratios
        left_ear = self.eye_aspect_ratio(left_eye)
        right_ear = self.eye_aspect_ratio(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Detect blink
        if avg_ear < self.blink_threshold:
            current_time = time.time()
            if current_time - self.last_blink_time > 0.3:  # Minimum time between blinks
                self.blink_counter += 1
                self.blink_times.append(current_time)
                self.last_blink_time = current_time
        
        # Calculate blink rate (blinks per minute)
        current_time = time.time()
        recent_blinks = [t for t in self.blink_times if current_time - t < 60]
        blink_rate = len(recent_blinks)
        
        # Get head pose (using nose and eyes)
        nose = face_landmarks.landmark[1]
        nose_coords = (nose.x * w, nose.y * h)
        
        # Simple attention check: face is centered and eyes are open
        face_center_x = nose.x
        is_centered = 0.3 < face_center_x < 0.7
        eyes_open = avg_ear > self.blink_threshold
        
        is_looking_at_screen = is_centered and eyes_open
        
        return {
            'looking_at_screen': is_looking_at_screen,
            'blink_rate': blink_rate,
            'total_blinks': self.blink_counter,
            'eye_aspect_ratio': avg_ear,
            'is_centered': is_centered
        }
    
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
    
    def draw_alerts(self, frame, posture_info, attention_info):
        """Draw alerts and information on frame"""
        h, w = frame.shape[:2]
        current_time = time.time()
        
        # Alert messages
        alerts = []
        
        # Posture alerts
        if posture_info['slouching']:
            alerts.append(("⚠️ SLOUCHING DETECTED! Sit up straight", (0, 0, 255)))
            if current_time - self.last_posture_alert > self.alert_cooldown:
                self.play_alert_sound()
                self.last_posture_alert = current_time
        
        if posture_info['too_close']:
            alerts.append(("⚠️ Too close to screen! Move back", (0, 165, 255)))
            if current_time - self.last_distance_alert > self.alert_cooldown:
                self.last_distance_alert = current_time
        
        # Attention alerts
        if not attention_info['looking_at_screen']:
            if self.looking_away_start is None:
                self.looking_away_start = current_time
            elif current_time - self.looking_away_start > self.away_time_threshold:
                alerts.append(("👀 Focus on your work!", (0, 255, 255)))
                if current_time - self.last_attention_alert > self.alert_cooldown:
                    self.play_alert_sound()
                    self.last_attention_alert = current_time
        else:
            self.looking_away_start = None
        
        # Draw alerts
        y_offset = 30
        for alert, color in alerts:
            cv2.rectangle(frame, (10, y_offset - 25), (w - 10, y_offset + 5), (0, 0, 0), -1)
            cv2.putText(frame, alert, (20, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 40
        
        # Blink rate warning
        if attention_info['blink_rate'] < 10:  # Less than 10 blinks per minute
            cv2.putText(frame, "😔 Low blink rate - Risk of eye strain!", 
                       (20, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 140, 255), 2)
            y_offset += 30
        
        return frame
    
    def draw_stats_panel(self, frame):
        """Draw statistics panel"""
        h, w = frame.shape[:2]
        session_duration = time.time() - self.session_start
        
        # Create semi-transparent panel
        panel_height = 180
        overlay = frame.copy()
        cv2.rectangle(overlay, (w - 350, 10), (w - 10, panel_height), (0, 0, 0), -1)
        frame = cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)
        
        # Stats text
        stats = [
            f"Session: {int(session_duration // 60)}m {int(session_duration % 60)}s",
            f"Blinks: {self.blink_counter}",
            f"Focused: {int(self.total_focused_time // 60)}m",
            f"Away: {int(self.total_away_time // 60)}m",
            f"Slouching: {int(self.total_slouch_time // 60)}m",
            f"Status: {'✓ Good' if not self.is_slouching and not self.is_looking_away else '⚠ Alert'}"
        ]
        
        y_pos = 35
        for stat in stats:
            cv2.putText(frame, stat, (w - 340, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            y_pos += 25
        
        return frame
    
    def update_statistics(self, posture_info, attention_info):
        """Update session statistics"""
        current_time = time.time()
        time_delta = current_time - self.last_posture_check
        
        self.is_slouching = posture_info['slouching']
        self.is_looking_away = not attention_info['looking_at_screen']
        
        if self.is_slouching:
            self.total_slouch_time += time_delta
        
        if self.is_looking_away:
            self.total_away_time += time_delta
        else:
            self.total_focused_time += time_delta
        
        self.last_posture_check = current_time
    
    def run(self):
        """Main monitoring loop"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        print("🚀 Smart Desk Monitor Started!")
        print("📹 Calibrating... Please sit in a good posture and look at the camera")
        print("Press 'q' to quit, 'r' to reset statistics, 's' to save session report")
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Flip frame for mirror effect
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process pose
            pose_results = self.pose.process(rgb_frame)
            face_results = self.face_mesh.process(rgb_frame)
            
            posture_info = None
            attention_info = None
            
            # Analyze posture
            if pose_results.pose_landmarks:
                posture_info = self.check_posture(pose_results.pose_landmarks, frame.shape)
                
                # Draw pose landmarks
                self.mp_drawing.draw_landmarks(
                    frame, 
                    pose_results.pose_landmarks,
                    self.mp_pose.POSE_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
                )
            
            # Analyze attention
            if face_results.multi_face_landmarks:
                attention_info = self.check_attention(face_results.multi_face_landmarks[0], frame.shape)
            
            # Update statistics and draw alerts
            if posture_info and attention_info:
                self.update_statistics(posture_info, attention_info)
                frame = self.draw_alerts(frame, posture_info, attention_info)
            
            # Draw stats panel
            frame = self.draw_stats_panel(frame)
            
            # Show calibration status
            if not self.calibrated:
                cv2.putText(frame, "Calibrating... Please face the camera", 
                           (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 
                           0.7, (0, 255, 255), 2)
            
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
        
        # Cleanup
        cap.release()
        cv2.destroyAllWindows()
        self.pose.close()
        self.face_mesh.close()
        
        # Final report
        self.save_session_report()
    
    def reset_statistics(self):
        """Reset all statistics"""
        self.session_start = time.time()
        self.total_slouch_time = 0
        self.total_away_time = 0
        self.total_focused_time = 0
        self.blink_counter = 0
        self.blink_times.clear()
    
    def save_session_report(self):
        """Save session report to file"""
        session_duration = time.time() - self.session_start
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        report = f"""
╔══════════════════════════════════════════════════════════╗
║        SMART DESK MONITOR - SESSION REPORT              ║
╚══════════════════════════════════════════════════════════╝

📅 Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

⏱️  SESSION DURATION
   Total Time: {int(session_duration // 3600)}h {int((session_duration % 3600) // 60)}m {int(session_duration % 60)}s

👁️  ATTENTION & FOCUS
   Focused Time: {int(self.total_focused_time // 60)}m {int(self.total_focused_time % 60)}s
   Looking Away: {int(self.total_away_time // 60)}m {int(self.total_away_time % 60)}s
   Focus Rate: {(self.total_focused_time / session_duration * 100):.1f}%
   
👀 BLINK STATISTICS
   Total Blinks: {self.blink_counter}
   Avg Blink Rate: {(self.blink_counter / (session_duration / 60)):.1f} blinks/min
   Recommended: 15-20 blinks/min

🪑 POSTURE ANALYSIS
   Good Posture: {int((session_duration - self.total_slouch_time) // 60)}m
   Slouching Time: {int(self.total_slouch_time // 60)}m {int(self.total_slouch_time % 60)}s
   Posture Score: {((session_duration - self.total_slouch_time) / session_duration * 100):.1f}%

💡 RECOMMENDATIONS
"""
        
        # Add recommendations
        if self.total_slouch_time / session_duration > 0.3:
            report += "   ⚠️  You slouched frequently. Consider ergonomic chair adjustments.\n"
        
        if self.blink_counter / (session_duration / 60) < 12:
            report += "   ⚠️  Low blink rate detected. Take breaks and use the 20-20-20 rule.\n"
        
        if self.total_away_time / session_duration > 0.4:
            report += "   ⚠️  Frequently distracted. Try time-blocking or focus techniques.\n"
        
        if self.total_focused_time / session_duration > 0.8:
            report += "   ✅ Excellent focus! Keep up the good work.\n"
        
        if ((session_duration - self.total_slouch_time) / session_duration) > 0.8:
            report += "   ✅ Great posture maintained throughout the session!\n"
        
        report += "\n" + "="*60 + "\n"
        
        # Save to file
        filename = f"session_report_{timestamp}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n📄 Session report saved to: {filename}")
        print(report)


if __name__ == "__main__":
    monitor = SmartDeskMonitor()
    monitor.run()
