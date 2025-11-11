#!/usr/bin/env python3
"""
Streamlit App for Area Monitoring System - Simple Demo Version
Works without OpenCV dependencies for cloud deployment
"""

import streamlit as st
import numpy as np
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io

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
    .demo-mode {
        background: linear-gradient(135deg, #ffa500 0%, #ff6347 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
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
if 'demo_active' not in st.session_state:
    st.session_state.demo_active = False
if 'detection_count' not in st.session_state:
    st.session_state.detection_count = 0
if 'alert_active' not in st.session_state:
    st.session_state.alert_active = False
if 'screenshots_taken' not in st.session_state:
    st.session_state.screenshots_taken = 0
if 'session_start' not in st.session_state:
    st.session_state.session_start = datetime.now()
if 'demo_frame_count' not in st.session_state:
    st.session_state.demo_frame_count = 0

def create_demo_frame():
    """Create a demo frame showing simulated detection"""
    # Create a simple demo image
    img = Image.new('RGB', (640, 480), color=(30, 30, 50))
    draw = ImageDraw.Draw(img)
    
    # Add background pattern
    for i in range(0, 640, 40):
        for j in range(0, 480, 40):
            if (i + j) % 80 == 0:
                draw.rectangle([i, j, i+20, j+20], fill=(40, 40, 60))
    
    # Add title
    draw.text((200, 50), "AREA MONITORING SYSTEM", fill=(150, 150, 200))
    draw.text((250, 80), "DEMO MODE", fill=(100, 200, 100))
    
    # Simulate detection box if demo is "active"
    if st.session_state.demo_active and st.session_state.demo_frame_count % 60 < 30:
        # Draw detection box
        x, y, w, h = 250, 180, 120, 200
        draw.rectangle([x, y, x+w, y+h], outline=(0, 255, 0), width=3)
        draw.text((x, y-20), "Person Detected", fill=(0, 255, 0))
        
        # Update detection count occasionally
        if st.session_state.demo_frame_count % 60 == 0:
            st.session_state.detection_count += 1
            st.session_state.alert_active = True
    else:
        st.session_state.alert_active = False
    
    # Add info overlay
    draw.text((10, 450), f"Frame: {st.session_state.demo_frame_count}", fill=(200, 200, 200))
    draw.text((10, 430), "Simulated Detection Algorithm", fill=(150, 150, 150))
    
    st.session_state.demo_frame_count += 1
    
    return np.array(img)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎥 Area Monitoring System</h1>
        <p>Advanced Person Detection with Computer Vision</p>
        <small>Demo Version - Showcasing Interface & Detection Algorithms</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Demo mode notice
    st.markdown("""
    <div class="demo-mode">
        <h3>🎨 Demo Mode Active</h3>
        <p>This is a demonstration version showcasing the interface and detection algorithms.<br>
        For full camera functionality, run locally with: <code>streamlit run streamlit_app.py</code></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar controls
    st.sidebar.title("🔧 Control Panel")
    
    # Demo controls
    st.sidebar.subheader("🎮 Demo Controls")
    
    demo_button_text = "⏹️ Stop Demo" if st.session_state.demo_active else "🎥 Start Demo"
    if st.sidebar.button(demo_button_text, key="demo_toggle"):
        st.session_state.demo_active = not st.session_state.demo_active
        if st.session_state.demo_active:
            st.session_state.session_start = datetime.now()
            st.session_state.detection_count = 0
            st.session_state.screenshots_taken = 0
            st.session_state.demo_frame_count = 0
            st.sidebar.success("🟢 Demo Started!")
        else:
            st.sidebar.info("🔴 Demo Stopped!")
            st.session_state.alert_active = False
    
    # Detection settings (for demonstration)
    st.sidebar.subheader("⚙️ Detection Settings")
    motion_threshold = st.sidebar.slider("Motion Sensitivity", 10, 50, 25, 5)
    skin_threshold = st.sidebar.slider("Skin Detection Sensitivity", 5, 20, 8, 1)
    confidence_threshold = st.sidebar.slider("Confidence Threshold", 0.1, 1.0, 0.5, 0.1)
    
    # Features
    st.sidebar.subheader("🎛️ Features")
    auto_screenshot = st.sidebar.checkbox("📸 Auto Screenshot", value=True)
    show_detection_info = st.sidebar.checkbox("📊 Show Detection Info", value=True)
    show_fps = st.sidebar.checkbox("⚡ Show FPS", value=True)
    
    # Main content area
    col1, col2 = st.columns([2.5, 1])
    
    with col1:
        st.subheader("📺 Demo Camera Feed")
        
        # Camera feed container
        camera_placeholder = st.empty()
        
        if st.session_state.demo_active:
            # Show demo frame
            demo_frame = create_demo_frame()
            
            st.markdown('<div class="camera-frame">', unsafe_allow_html=True)
            camera_placeholder.image(demo_frame, channels="RGB", use_column_width=True)
            
            # Auto-refresh for animation
            time.sleep(0.1)
            st.rerun()
        else:
            # Show offline placeholder
            placeholder_img = np.zeros((480, 640, 3), dtype=np.uint8)
            placeholder_img.fill(40)  # Dark gray background
            
            # Create PIL image for text
            pil_img = Image.fromarray(placeholder_img)
            draw = ImageDraw.Draw(pil_img)
            
            # Add text
            draw.text((120, 200), 'AREA MONITORING SYSTEM', fill=(150, 150, 150))
            draw.text((240, 250), 'Demo Offline', fill=(100, 100, 100))
            draw.text((180, 300), 'Click "Start Demo" to begin', fill=(120, 120, 120))
            
            placeholder_array = np.array(pil_img)
            
            st.markdown('<div class="camera-frame">', unsafe_allow_html=True)
            camera_placeholder.image(placeholder_array, channels="RGB", use_column_width=True)
    
    with col2:
        st.subheader("📊 System Dashboard")
        
        # Status indicators
        if st.session_state.demo_active:
            st.markdown('<p class="status-online">🟢 Demo: Active & Running</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-offline">🔴 Demo: Offline</p>', unsafe_allow_html=True)
        
        # Alert status
        if st.session_state.alert_active:
            st.markdown("""
            <div class="alert-box">
                🚨 PERSON DETECTED! 🚨<br>
                <small>Simulated Detection Active</small>
            </div>
            """, unsafe_allow_html=True)
        
        # Real-time metrics
        st.subheader("📈 Live Statistics")
        
        # Calculate session time
        uptime = datetime.now() - st.session_state.session_start
        uptime_str = str(uptime).split('.')[0]  # Remove microseconds
        
        # Metrics in a nice layout
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.metric("🔍 Detections", st.session_state.detection_count)
            st.metric("📸 Screenshots", st.session_state.screenshots_taken)
        
        with col_b:
            st.metric("⏱️ Uptime", uptime_str)
            current_fps = "30" if st.session_state.demo_active else "0"
            st.metric("⚡ FPS", current_fps)
        
        # Manual controls
        st.subheader("🎮 Manual Controls")
        
        if st.button("📸 Take Screenshot Now"):
            st.session_state.screenshots_taken += 1
            st.success("📸 Demo screenshot captured!")
        
        if st.button("🔄 Reset Statistics"):
            st.session_state.detection_count = 0
            st.session_state.screenshots_taken = 0
            st.session_state.session_start = datetime.now()
            st.success("📊 Statistics reset!")
        
        # System information
        st.subheader("ℹ️ System Info")
        st.info(f"""
        **🎨 Mode**: Demo Simulation  
        **🤖 Algorithm**: Motion + Skin Analysis (Simulated)  
        **⚡ Performance**: 30 FPS (Simulated)  
        **🎯 Accuracy**: Multi-stage Validation  
        **📊 Status**: {'🟢 Demo Active' if st.session_state.demo_active else '🔴 Demo Standby'}  
        **🔧 Environment**: Streamlit Cloud Compatible
        """)
        
        # Technical details
        with st.expander("🔬 Technical Details"):
            st.write("""
            **Detection Pipeline (Actual Implementation):**
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
            
            **Demo Features:**
            - Simulated person detection
            - Real-time interface updates
            - Interactive controls
            - Professional UI showcase
            """)
        
        # Deployment info
        with st.expander("🚀 Deployment Options"):
            st.write("""
            **Local Deployment (Full Features):**
            ```bash
            pip install opencv-python streamlit
            streamlit run streamlit_app.py
            ```
            
            **Cloud Deployment:**
            - ✅ Streamlit Cloud (Demo Mode)
            - ✅ Heroku (API Mode)
            - ✅ Railway (Possible Full Mode)
            - ⚠️ Render (OpenCV Issues)
            
            **Repository:**
            https://github.com/ShridharPT/AreaMonitoringSystem
            """)

if __name__ == "__main__":
    main()
