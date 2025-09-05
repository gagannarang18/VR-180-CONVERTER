# 🥽 VR 180 Immersive Experience Converter

Transform any 2D video into an immersive VR 180 stereoscopic experience using AI-powered depth estimation.

## ✨ Key Features

- **🤖 AI-Powered Depth Estimation** - Custom algorithm using gradient and brightness analysis
- **👁️ Stereoscopic Generation** - Creates proper left/right eye views with parallax effects
- **📊 Real-Time Progress Tracking** - Live updates during video processing
- **🎬 VR-Ready Output** - Standard VR 180 side-by-side format
- **☁️ Cloud Deployment** - Accessible via Streamlit Cloud
- **💰 100% Free Resources** - No paid APIs or services required

## 🚀 Live Demo

**Try it now:** [https://vr-180-converter-humanity-founders.streamlit.app/](https://vr-180-converter-humanity-founders.streamlit.app/)

## 📱 How to Use

1. Upload your 2D video (MP4, AVI, MOV, MKV)
2. Watch the real-time conversion process with progress tracking
3. Download your VR 180 stereoscopic video
4. View in VR headsets using "180° Side-by-Side" mode in players like Oculus Browser, SkyBox, or BigScreen

## 🛠️ Technology Stack

- **Frontend:** Streamlit - Clean, intuitive user interface
- **Backend:** Python with OpenCV for video processing
- **Computer Vision:** Custom depth estimation algorithm combining gradient detection and brightness analysis
- **Video Processing:** MoviePy and OpenCV for efficient frame manipulation
- **Deployment:** Streamlit Cloud for free hosting
- **AI Approach:** Mathematical depth mapping without expensive APIs

## 🏗️ Local Installation & Setup

git clone https://github.com/yourusername/vr-180-converter.git
cd vr-180-converter/vr180_streamlit
pip install -r requirements.txt
streamlit run app.py