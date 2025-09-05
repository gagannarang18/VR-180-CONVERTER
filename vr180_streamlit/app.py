import streamlit as st
import cv2
import numpy as np
import os
import tempfile
from moviepy.editor import VideoFileClip
from utils.video_processor import SimpleVRProcessor
import time

# Page configuration
st.set_page_config(
    page_title="VR 180 Converter",
    page_icon="🥽",
    layout="centered"
)

# Custom CSS for clean design
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🥽 VR 180 Converter</h1>
        <p>Transform your 2D videos into immersive VR 180 experiences</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False
    if 'output_file' not in st.session_state:
        st.session_state.output_file = None
    
    # Main interface
    if not st.session_state.processing_complete:
        upload_interface()
    else:
        result_interface()

def upload_interface():
    """Clean upload interface"""
    
    st.markdown("## 📁 Upload Your 2D Video")
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a video file",
        type=['mp4', 'avi', 'mov', 'mkv'],
        help="Supported formats: MP4, AVI, MOV, MKV"
    )
    
    if uploaded_file is not None:
        # Show file info
        col1, col2 = st.columns(2)
        
        with col1:
            st.info(f"""
            **File Details:**
            - Name: {uploaded_file.name}
            - Size: {uploaded_file.size / (1024*1024):.1f} MB
            """)
        
        with col2:
            if st.button("🔍 Quick Analysis"):
                analyze_video(uploaded_file)
        
        # Convert button
        st.markdown("---")
        if st.button("🚀 Convert to VR 180", type="primary", use_container_width=True):
            process_video(uploaded_file)

def analyze_video(uploaded_file):
    """Quick video analysis"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name
    
    try:
        cap = cv2.VideoCapture(tmp_file_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        st.success(f"""
        **Video Analysis:**
        - Duration: {duration:.1f} seconds
        - Resolution: {width} x {height}
        - Frame Rate: {fps:.1f} FPS
        - Total Frames: {frame_count:,}
        """)
    except Exception as e:
        st.error(f"Analysis failed: {str(e)}")
    finally:
        os.unlink(tmp_file_path)

def process_video(uploaded_file):
    """Process video with live progress"""
    
    st.markdown("## 🔄 Converting to VR 180...")
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    step_indicators = st.empty()
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(uploaded_file.read())
            input_path = tmp_file.name
        
        # Initialize processor
        processor = SimpleVRProcessor()
        
        # Progress callback
        def update_progress(progress, message, step):
            progress_bar.progress(progress / 100)
            status_text.text(f"{message} ({progress}%)")
            
            # Visual step indicators
            steps = ["📁 Loading", "🧠 Depth Analysis", "👁️ Stereo Creation", "🎬 VR Optimization"]
            step_status = ""
            for i, step_name in enumerate(steps):
                if i < step:
                    step_status += f"✅ {step_name}\n"
                elif i == step:
                    step_status += f"🔄 {step_name}\n"
                else:
                    step_status += f"⏸️ {step_name}\n"
            
            step_indicators.text(step_status)
        
        # 🔥 MAIN CONVERSION CALL
        output_path = processor.convert_to_vr180(
            input_path, 
            progress_callback=update_progress
        )
        
        # Success!
        progress_bar.progress(1.0)
        status_text.success("✅ VR 180 conversion completed!")
        
        # Store results
        st.session_state.processing_complete = True
        st.session_state.output_file = output_path
        
        # Cleanup input file
        os.unlink(input_path)
        
        # Show results
        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ Conversion failed: {str(e)}")
        if 'input_path' in locals():
            os.unlink(input_path)

def result_interface():
    """Results and download"""
    
    st.markdown("## ✅ Conversion Complete!")
    
    st.markdown("""
    <div class="success-box">
        <h4>🎉 Your VR 180 video is ready!</h4>
        <p>Download and enjoy in your VR headset!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Download options
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.output_file and os.path.exists(st.session_state.output_file):
            with open(st.session_state.output_file, 'rb') as file:
                st.download_button(
                    label="📥 Download VR Video",
                    data=file.read(),
                    file_name=f"vr180_converted_{int(time.time())}.mp4",
                    mime="video/mp4",
                    type="primary",
                    use_container_width=True
                )
    
    with col2:
        if st.button("🔄 Convert Another", use_container_width=True):
            # Reset everything
            st.session_state.processing_complete = False
            st.session_state.output_file = None
            st.rerun()
    
    # Instructions
    st.markdown("### 📱 How to View in VR:")
    st.info("""
    1. **Download** the VR video
    2. **Transfer** to your VR headset
    3. **Open** VR video player (Oculus Browser, SkyBox)
    4. **Select** "180° Side-by-Side" format
    5. **Enjoy** your immersive experience! 🎬
    """)

if __name__ == "__main__":
    main()
