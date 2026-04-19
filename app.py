import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import base64
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure page
st.set_page_config(
    page_title="DebugGenius - AI Code Debugger",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    :root {
        --primary-color: #00D9FF;
        --secondary-color: #FF006E;
        --background-color: #0F0E17;
        --surface-color: #16213E;
        --text-color: #FFFFFF;
    }
    
    .stApp {
        background-color: #0F0E17;
    }
    
    .main-title {
        color: #00D9FF;
        text-shadow: 0 0 10px rgba(0, 217, 255, 0.5);
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .subtitle {
        color: #B0B0B0;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    
    .section-header {
        color: #00D9FF;
        font-size: 1.3em;
        font-weight: bold;
        margin-top: 20px;
        margin-bottom: 10px;
        border-bottom: 2px solid #FF006E;
        padding-bottom: 10px;
    }
    
    .debug-button {
        background: linear-gradient(135deg, #00D9FF 0%, #FF006E 100%);
        color: white;
        font-weight: bold;
        padding: 12px 30px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        transition: transform 0.2s;
    }
    
    .debug-button:hover {
        transform: scale(1.05);
    }
    
    .error-box {
        background-color: rgba(255, 0, 110, 0.1);
        border-left: 4px solid #FF006E;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .success-box {
        background-color: rgba(0, 217, 255, 0.1);
        border-left: 4px solid #00D9FF;
        padding: 12px;
        border-radius: 4px;
        margin: 10px 0;
    }
    
    .code-block {
        background-color: #16213E;
        border: 1px solid #FF006E;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        color: #00D9FF;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
    }
    
    .tips-section {
        background-color: #16213E;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #00D9FF;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Gemini API
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("❌ GEMINI_API_KEY not found in .env file. Please configure it before proceeding.")
    st.stop()

genai.configure(api_key=api_key)

# Page Title
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown('<div class="main-title">🐛 DebugGenius - AI Code Debugger</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">AI-Powered Code Error Analysis | Upload screenshots, get instant solutions</div>', unsafe_allow_html=True)

# Sidebar Configuration
st.sidebar.markdown("### 📤 Upload Your Code Error")
uploaded_file = st.sidebar.file_uploader(
    "Choose an image file (PNG, JPG, JPEG)",
    type=["png", "jpg", "jpeg"],
    help="Upload a screenshot of your code error"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🔍 Debug Mode")
debug_mode = st.sidebar.radio(
    "Select how you want the debugging assistance:",
    ["Hints (Explanation Only)", "Solution with Code"],
    help="Hints: Shows error explanation | Solution: Includes corrected code"
)

st.sidebar.markdown("---")

# Display uploaded image preview
if uploaded_file is not None:
    st.sidebar.markdown("### 👀 Image Preview")
    image = Image.open(uploaded_file)
    st.sidebar.image(image, use_column_width=True)

# Main Debug Button
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    debug_button = st.button(
        "🚀 Debug Code",
        use_container_width=True,
        key="debug_button"
    )

# Validation and API Call
if debug_button:
    # Validate inputs
    if uploaded_file is None:
        st.error("❌ Please upload an image file first!")
        st.stop()
    
    if debug_mode is None:
        st.error("❌ Please select a debug mode (Hints or Solution with Code)!")
        st.stop()
    
    # Prepare image for API
    image_data = uploaded_file.getvalue()
    base64_image = base64.standard_b64encode(image_data).decode("utf-8")
    
    # Determine file type
    file_extension = uploaded_file.name.split(".")[-1].lower()
    mime_types = {
        "png": "image/png",
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg"
    }
    mime_type = mime_types.get(file_extension, "image/jpeg")
    
    # Create appropriate prompt based on selected mode
    if "Hints" in debug_mode:
        prompt = """Analyze this code error screenshot and provide:
1. **Error Type**: What kind of error is this? (e.g., SyntaxError, TypeError, ValueError, NullPointerException, etc.)
2. **Error Explanation**: What does this error mean in simple terms?
3. **Root Cause**: Why is this error occurring? What went wrong in the code?
4. **Quick Tips**: 2-3 key hints on how to fix this error.

Format your response clearly with these sections. Do NOT provide corrected code."""
    else:
        prompt = """Analyze this code error screenshot and provide:
1. **Error Type**: What kind of error is this? (e.g., SyntaxError, TypeError, ValueError, NullPointerException, etc.)
2. **Error Explanation**: What does this error mean in simple terms?
3. **Root Cause**: Why is this error occurring? What went wrong in the code?
4. **Corrected Code**: Provide the corrected version of the problematic code section.
5. **Explanation of Fix**: Explain what changed and why it fixes the error.

Format your response clearly with these sections. Provide code in markdown code blocks with appropriate language syntax highlighting."""
    
    # Make API call with spinner
    with st.spinner("🔍 Analyzing your code error... This may take a few seconds."):
        try:
            # Use Gemini 2.0 Flash model for vision analysis
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            # Send request with image and text - using correct API format
            response = model.generate_content([
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": base64_image,
                    }
                },
                prompt
            ])
            
            # Display response
            st.markdown("---")
            st.markdown('<div class="section-header">✅ Analysis Results</div>', unsafe_allow_html=True)
            
            # Format response with markdown
            st.markdown(response.text)
            
            # Success indicator
            st.markdown('<div class="success-box">✨ Debugging analysis complete! Review the suggestions above.</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error analyzing image: {str(e)}")
            st.info("💡 Tip: Make sure the image clearly shows the code error and is not too blurry.")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #B0B0B0; font-size: 0.9em; margin-top: 30px;">
    <p>🚀 Powered by Shayan Abrar | 💻 Built with Streamlit</p>
    <p>For best results, upload clear screenshots of code errors</p>
</div>
""", unsafe_allow_html=True)
