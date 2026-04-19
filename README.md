# 🐛 DebugGenius - AI Code Debugger

An intelligent Streamlit application that analyzes code error screenshots and provides AI-powered debugging assistance using Google Gemini API.

## ✨ Features

- 📤 **Image Upload**: Upload screenshots of code errors (PNG, JPG, JPEG)
- 🔍 **Two Debug Modes**:
  - **Hints Mode**: Get error explanation and tips without code changes
  - **Solution Mode**: Get error explanation + corrected code with full fix explanation
- 🎨 **Professional Dark Theme**: Modern, sleek UI optimized for code analysis
- ⚡ **Real-time Analysis**: Instant feedback using Google Gemini 2.0 Flash
- 🔒 **Secure API Key Management**: Environment variables via `.env` file
- 🌍 **Multi-language Support**: Auto-detects programming language from image

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Google Gemini API Key (get it from [Google AI Studio](https://aistudio.google.com/app/apikeys))

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/debuggenius.git
   cd debuggenius
   ```

2. **Create virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy .env.example to .env
   cp .env.example .env
   
   # Edit .env and add your Gemini API key
   # GEMINI_API_KEY=your_actual_api_key_here
   ```

5. **Run the app locally**
   ```bash
   streamlit run app.py
   ```

   The app will open at `http://localhost:8501`

## 💻 How to Use

1. **Upload Code Error Screenshot**
   - Click "Choose an image file" in the sidebar
   - Select a PNG, JPG, or JPEG image showing your code error
   - Preview appears automatically

2. **Select Debug Mode**
   - Choose "Hints (Explanation Only)" for error explanation + tips
   - Choose "Solution with Code" for complete fix with corrected code

3. **Click Debug Code**
   - Button triggers Gemini API analysis
   - Spinner shows while analyzing
   - Results display with formatted error analysis

4. **Review Results**
   - Error Type
   - Error Explanation
   - Root Cause Analysis
   - Quick Tips or Corrected Code (depending on mode selected)

## 🌐 Deploy to Streamlit Cloud

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit: DebugGenius - AI-powered code error analysis"
   git push origin main
   ```

2. **Deploy via Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Select `main` branch and `app.py` as the main file
   - Click "Deploy"

3. **Configure API Key**
   - In Streamlit Cloud app settings, go to "Secrets"
   - Add: `GEMINI_API_KEY = your_api_key_here`
   - The app will automatically use the secret

4. **Your app is live!**
   - Share the deployed URL with others

## 📁 Project Structure

```
ai-code-debugger/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .env                  # Local environment (not in repo)
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🛠️ Technical Details

### Dependencies
- **streamlit**: Web app framework
- **google-generativeai**: Gemini API client
- **python-dotenv**: Environment variable management
- **Pillow**: Image processing

### API Model
- **gemini-2.0-flash**: Fast vision model for error screenshot analysis

### UI/UX
- Dark theme with cyan (#00D9FF) and magenta (#FF006E) accent colors
- Responsive layout with sidebar controls
- Real-time image preview
- Loading spinners and success/error messages

## 🎯 Supported Programming Languages

The app auto-detects and supports:
- Python
- JavaScript/TypeScript
- Java
- C/C++
- C#
- Ruby
- PHP
- Go
- Rust
- Swift
- Kotlin
- And many more...

## ⚠️ Important Notes

- **API Key Security**: Never commit `.env` to GitHub. It's in `.gitignore`.
- **Image Quality**: Upload clear, readable screenshots for best results
- **Rate Limits**: Gemini API has rate limits. Check your quota at [Google AI Studio](https://aistudio.google.com/app/usage)
- **Supported Formats**: PNG, JPG, JPEG only

## 🐛 Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure `.env` file exists in the project root
- Add your Gemini API key to `.env`: `GEMINI_API_KEY=your_key_here`

### "Error analyzing image"
- Upload a clearer screenshot
- Ensure the image actually shows code
- Check your Gemini API rate limit

### App won't start locally
- Check Python version (3.8+ required)
- Verify virtual environment is activated
- Run `pip install -r requirements.txt` again

## 📄 License

This project is open source. Feel free to fork and contribute!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues first

---

**Made with ❤️ | DebugGenius - Your AI Debugging Partner**
