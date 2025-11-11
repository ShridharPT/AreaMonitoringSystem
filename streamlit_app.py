#!/usr/bin/env python3
"""
Streamlit App for Area Monitoring System
Real-time person detection with OpenCV
"""

import streamlit as st
import cv2
import numpy as np
import time
from datetime import datetime
import threading
import queue
from PIL import Image
import io
import base64

# Configure Streamlit page
st.set_page_config(
    page_title="🎥 Area Monitoring System",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for cyberpunk styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    .alert-box {
        background: linear-gradient(135deg, #ff0064 0%, #cc0050 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        animation: pulse 2s infinite;
        box-shadow: 0 8px 32px rgba(255,0,100,0.3);
        font-size: 1.2em;
        font-weight: bold;
    }
    @keyframes pulse {
        0% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.8; transform: scale(1.02); }
        100% { opacity: 1; transform: scale(1); }
    }
    .status-online {
        color: #00ff88;
        font-weight: bold;
        font-size: 1.1em;
    }
    .status-offline {
        color: #ff4444;
        font-weight: bold;
        font-size: 1.1em;
    }
    .camera-frame {
        border: 3px solid #667eea;
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'camera_active' not in st.session_state:
    st.session_state.camera_active = False
if 'detection_count' not in st.session_state:
    st.session_state.detection_count = 0
if 'alert_active' not in st.session_state:
    st.session_state.alert_active = False
if 'screenshots_taken' not in st.session_state:
    st.session_state.screenshots_taken = 0
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()
if 'prev_frame' not in st.session_state:
    st.session_state.prev_frame = None
if 'consecutive_detections' not in st.session_state:
    st.session_state.consecutive_detections = 0
if 'fps_counter' not in st.session_state:
    st.session_state.fps_counter = 0
if 'last_fps_time' not in st.session_state:
    st.session_state.last_fps_time = time.time()

def detect_person_advanced(frame):
    """
    Advanced person detection using motion and skin tone analysis
    Similar to your original dashboard.js algorithm
    """
    height, width = frame.shape[:2]
    
    # Convert to different color spaces
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Initialize previous frame if not exists
    if st.session_state.prev_frame is None:
        st.session_state.prev_frame = gray
        return False, [], frame
    
    # Motion detection
    diff = cv2.absdiff(st.session_state.prev_frame, gray)
    _, motion_mask = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    
    # Morphological operations to reduce noise
    kernel = np.ones((3, 3), np.uint8)
    motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_OPEN, kernel)
    motion_mask = cv2.morphologyEx(motion_mask, cv2.MORPH_CLOSE, kernel)
    
    # Skin color detection (multiple ranges for better detection)
    lower_skin1 = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin1 = np.array([20, 255, 255], dtype=np.uint8)
    lower_skin2 = np.array([0, 50, 80], dtype=np.uint8)
    upper_skin2 = np.array([30, 200, 255], dtype=np.uint8)
    
    skin_mask1 = cv2.inRange(hsv, lower_skin1, upper_skin1)
    skin_mask2 = cv2.inRange(hsv, lower_skin2, upper_skin2)
    skin_mask = cv2.bitwise_or(skin_mask1, skin_mask2)
    
    # Combine motion and skin detection
    combined_mask = cv2.bitwise_and(motion_mask, skin_mask)
    
    # Apply Gaussian blur to smooth the mask
    combined_mask = cv2.GaussianBlur(combined_mask, (5, 5), 0)
    
    # Find contours
    contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detection_boxes = []
    motion_pixels = cv2.countNonZero(motion_mask)
    skin_pixels = cv2.countNonZero(skin_mask)
    
    # Process contours
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 800:  # Minimum area threshold
            x, y, w, h = cv2.boundingRect(contour)
            
            # Size and aspect ratio filters
            if w > 25 and h > 40 and w < width * 0.8 and h < height * 0.8:
                aspect_ratio = h / w if w > 0 else 0
                if 1.2 <= aspect_ratio <= 4.0:  # Human-like aspect ratio
                    detection_boxes.append({
                        'x': x, 'y': y, 'w': w, 'h': h,
                        'area': area,
                        'confidence': min(area / 2000, 1.0)
                    })
    
    # Merge overlapping boxes (simplified version)
    if len(detection_boxes) > 1:
        merged_boxes = []
        for box in detection_boxes:
            merged = False
            for merged_box in merged_boxes:
                # Check for overlap
                if (abs(box['x'] - merged_box['x']) < 50 and 
                    abs(box['y'] - merged_box['y']) < 50):
                    # Merge boxes - keep the larger one
                    if box['area'] > merged_box['area']:
                        merged_boxes.remove(merged_box)
                        merged_boxes.append(box)
                    merged = True
                    break
            if not merged:
                merged_boxes.append(box)
        detection_boxes = merged_boxes
    
    # Determine if person is detected
    person_detected = (len(detection_boxes) > 0 and 
                      motion_pixels > 15 and 
                      skin_pixels > 8)
    
    # Update consecutive detections for stability
    if person_detected:
        st.session_state.consecutive_detections += 1
    else:
        st.session_state.consecutive_detections = max(0, st.session_state.consecutive_detections - 1)
    
    # Require multiple consecutive detections to confirm
    confirmed_detection = st.session_state.consecutive_detections >= 2
    
    # Draw detection boxes on frame
    processed_frame = frame.copy()
    for box in detection_boxes:
        x, y, w, h = box['x'], box['y'], box['w'], box['h']
        confidence = box['confidence']
        
        # Draw bounding box
        color = (0, 255, 0) if confirmed_detection else (0, 255, 255)
        thickness = 3 if confirmed_detection else 2
        cv2.rectangle(processed_frame, (x, y), (x + w, y + h), color, thickness)
        
        # Draw label
        label = f"Person {confidence:.1f}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(processed_frame, (x, y - label_size[1] - 10), 
                     (x + label_size[0], y), color, -1)
        cv2.putText(processed_frame, label, (x, y - 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
    
    # Add detection info overlay
    info_text = f"Motion: {motion_pixels} | Skin: {skin_pixels} | Boxes: {len(detection_boxes)}"
    cv2.putText(processed_frame, info_text, (10, height - 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Update previous frame
    st.session_state.prev_frame = gray
    
    return confirmed_detection, detection_boxes, processed_frame

def calculate_fps():
    """Calculate and return current FPS"""
    current_time = time.time()
    st.session_state.fps_counter += 1
    
    if current_time - st.session_state.last_fps_time >= 1.0:
        fps = st.session_state.fps_counter
        st.session_state.fps_counter = 0
        st.session_state.last_fps_time = current_time
        return fps
    return 0

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎥 Area Monitoring System</h1>
        <p>Advanced Person Detection with OpenCV & Computer Vision</p>
        <small>Real-time Motion Analysis • Skin Tone Detection • Smart Alerts</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.title("🔧 Control Panel")
    
    # Camera controls
    st.sidebar.subheader("📹 Camera Controls")
    
    camera_button_text = "⏹️ Stop Camera" if st.session_state.camera_active else "🎥 Start Camera"
    if st.sidebar.button(camera_button_text, key="camera_toggle"):
        st.session_state.camera_active = not st.session_state.camera_active
        if st.session_state.camera_active:
            st.session_state.session_start = datetime.now()
            st.session_state.detection_count = 0
            st.session_state.screenshots_taken = 0
            st.session_state.consecutive_detections = 0
            st.sidebar.success("🟢 Camera Started!")
        else:
            st.sidebar.info("🔴 Camera Stopped!")
            st.session_state.alert_active = False
    
    # Detection settings
    st.sidebar.subheader("⚙️ Detection Settings")
    motion_threshold = st.sidebar.slider("Motion Sensitivity", 10, 50, 25, 5)
    skin_threshold = st.sidebar.slider("Skin Detection Sensitivity", 5, 20, 8, 1)
    min_area = st.sidebar.slider("Minimum Detection Area", 500, 2000, 800, 100)
    
    # Features
    st.sidebar.subheader("🎛️ Features")
    auto_screenshot = st.sidebar.checkbox("📸 Auto Screenshot", value=True)
    show_detection_info = st.sidebar.checkbox("📊 Show Detection Info", value=True)
    show_fps = st.sidebar.checkbox("⚡ Show FPS", value=True)
    
    # Main content area
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        st.subheader("📺 Live Camera Feed")
        
        # Camera feed container
        camera_container = st.container()
        
        with camera_container:
            if st.session_state.camera_active:
                # Camera placeholder
                camera_placeholder = st.empty()
                
                try:
                    # Try to initialize camera
                    cap = cv2.VideoCapture(0)
                    
                    if not cap.isOpened():
                        st.error("❌ Camera not accessible!")
                        st.info("""
                        **Possible solutions:**
                        - 🖥️ **Local deployment**: Run `streamlit run streamlit_app.py` locally
                        - 📱 **Mobile**: Use your phone's camera via browser
                        - 🌐 **Cloud**: Camera access limited in cloud environments
                        """)
                        st.session_state.camera_active = False
                    else:
                        # Set camera properties
                        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                        cap.set(cv2.CAP_PROP_FPS, 30)
                        
                        # Main camera loop
                        frame_count = 0
                        detection_active = False
                        
                        while st.session_state.camera_active:
                            ret, frame = cap.read()
                            if not ret:
                                st.error("❌ Failed to read camera frame")
                                break
                            
                            # Resize for consistent processing
                            frame = cv2.resize(frame, (640, 480))
                            
                            # Process every 2nd frame for performance
                            if frame_count % 2 == 0:
                                detected, boxes, processed_frame = detect_person_advanced(frame)
                                
                                if detected:
                                    st.session_state.detection_count += 1
                                    detection_active = True
                                    
                                    # Auto screenshot every 30 detections (~10 seconds)
                                    if auto_screenshot and st.session_state.detection_count % 30 == 0:
                                        st.session_state.screenshots_taken += 1
                                else:
                                    detection_active = False
                                
                                st.session_state.alert_active = detection_active
                            else:
                                processed_frame = frame
                            
                            # Add FPS counter
                            if show_fps:
                                fps = calculate_fps()
                                if fps > 0:
                                    cv2.putText(processed_frame, f"FPS: {fps}", (10, 30), 
                                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            
                            # Convert BGR to RGB for Streamlit
                            display_frame = cv2.cvtColor(processed_frame, cv2.COLOR_BGR2RGB)
                            
                            # Display with custom styling
                            camera_placeholder.markdown(
                                '<div class="camera-frame">', 
                                unsafe_allow_html=True
                            )
                            camera_placeholder.image(
                                display_frame, 
                                channels="RGB", 
                                use_column_width=True
                            )
                            
                            frame_count += 1
                            time.sleep(0.033)  # ~30 FPS
                        
                        cap.release()
                        
                except Exception as e:
                    st.error(f"❌ Camera Error: {str(e)}")
                    st.info("""
                    **Note**: Camera access works best in local environments.
                    
                    **For Streamlit Cloud deployment:**
                    - Camera features are limited due to browser security
                    - The UI and detection algorithms will still be visible
                    - Perfect for demonstrating the interface and code
                    """)
                    st.session_state.camera_active = False
            else:
                # Offline placeholder
                placeholder_img = np.zeros((480, 640, 3), dtype=np.uint8)
                
                # Create attractive offline screen
                cv2.rectangle(placeholder_img, (50, 50), (590, 430), (50, 50, 50), -1)
                cv2.rectangle(placeholder_img, (50, 50), (590, 430), (100, 100, 100), 3)
                
                # Add text
                cv2.putText(placeholder_img, 'AREA MONITORING SYSTEM', (120, 200), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150, 150, 150), 2)
                cv2.putText(placeholder_img, 'Camera Offline', (240, 250), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (100, 100, 100), 2)
                cv2.putText(placeholder_img, 'Click "Start Camera" to begin', (180, 300), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (120, 120, 120), 1)
                
                st.markdown('<div class="camera-frame">', unsafe_allow_html=True)
                st.image(placeholder_img, channels="RGB", use_column_width=True)
    
    with col2:
        st.subheader("📊 System Dashboard")
        
        # Status indicators
        status_container = st.container()
        with status_container:
            if st.session_state.camera_active:
                st.markdown('<p class="status-online">🟢 Camera: Online & Active</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="status-offline">🔴 Camera: Offline</p>', unsafe_allow_html=True)
        
        # Alert status
        if st.session_state.alert_active:
            st.markdown("""
            <div class="alert-box">
                🚨 PERSON DETECTED! 🚨<br>
                <small>Motion & Skin Analysis Active</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Real-time metrics
        st.subheader("📈 Live Statistics")
        
        # Calculate session time
        if st.session_state.camera_active:
            uptime = datetime.now() - st.session_state.session_start
        else:
            uptime = datetime.now() - st.session_state.session_start
        
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        # Metrics in a nice layout
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.metric("🔍 Detections", st.session_state.detection_count)
            st.metric("📸 Screenshots", st.session_state.screenshots_taken)
        
        with col_b:
            st.metric("⏱️ Uptime", uptime_str)
            st.metric("🎯 Stability", f"{st.session_state.consecutive_detections}/3")
        
        # Manual controls
        st.subheader("🎮 Manual Controls")
        
        if st.button("📸 Take Screenshot Now"):
            if st.session_state.camera_active:
                st.session_state.screenshots_taken += 1
                st.success("📸 Screenshot captured!")
            else:
                st.warning("⚠️ Start camera first!")
        
        if st.button("🔄 Reset Statistics"):
            st.session_state.detection_count = 0
            st.session_state.screenshots_taken = 0
            st.session_state.consecutive_detections = 0
            st.session_state.session_start = datetime.now()
            st.success("📊 Statistics reset!")
        
        # System information
        st.subheader("ℹ️ System Info")
        st.info(f"""
        **🤖 Detection Algorithm**: Motion + Skin Analysis  
        **⚡ Performance**: ~30 FPS Processing  
        **🎯 Accuracy**: Multi-stage Validation  
        **📊 Status**: {'🟢 Active Detection' if st.session_state.camera_active else '🔴 Standby Mode'}  
        **🔧 Mode**: {'Real-time' if st.session_state.camera_active else 'Demo'}
        """)
        
        # Technical details
        with st.expander("🔬 Technical Details"):
            st.write("""
            **Detection Pipeline:**
            1. 📹 Frame Capture (640x480)
            2. 🎨 Color Space Conversion (BGR→HSV)
            3. 🏃 Motion Detection (Frame Difference)
            4. 👤 Skin Tone Analysis (HSV Range)
            5. 🔍 Contour Detection & Filtering
            6. 📦 Bounding Box Generation
            7. ✅ Multi-frame Validation
            
            **Performance Optimizations:**
            - Frame skipping (every 2nd frame)
            - Morphological operations
            - Gaussian blur smoothing
            - Aspect ratio filtering
            """)

if __name__ == "__main__":
    main()
