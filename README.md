# PowerPoint Accessibility Enhancer

A Streamlit web application that enhances PowerPoint presentations for better accessibility, helping creators make their content accessible to everyone, including people with disabilities.

## 🌟 Features
- **Accessibility Analysis**: Evaluates presentations against WCAG standards
- **AI-powered Alt Text Generation**: Uses LLaVA via Ollama to create descriptive alt text for images
- **Font Size Optimization**: Adjusts text to ensure readability
- **Color Contrast Enhancement**: Improves text visibility for low vision users
- **Text Simplification**: Makes complex text more accessible
- **Comprehensive Reports**: Provides a downloadable HTML accessibility report

## 📥 Installation
1. Clone this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install Ollama for AI-powered alt text generation:
   - Download from [ollama.ai/download](https://ollama.ai/download)
   - Pull the LLaVA model:
     ```bash
     ollama pull llava
     ```

## 🚀 Usage
### Using the Launchers
#### Windows
#### Linux/Mac

### Manual Startup
1. Start Ollama with the LLaVA model:
   ```bash
   ollama run llava
   ```
2. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```
3. Open your browser and go to: [http://localhost:8501](http://localhost:8501)
4. Upload your PowerPoint presentation
5. Analyze accessibility
6. Click "Enhance Presentation" to improve accessibility
7. Download the enhanced presentation

## 🖥️ LLaVA Integration
This application uses the LLaVA (Large Language and Vision Assistant) model via Ollama to generate descriptive alt text for images. LLaVA combines vision capabilities with language understanding to create contextually relevant image descriptions for screen readers.

If Ollama is not available, the application will fall back to using basic placeholder text.

## 🗂️ Project Structure
```
powerpoint_accessibility_project/
├── app.py                  # Main application entry point
├── README.md               # Project documentation
├── requirements.txt        # Dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose config
├── launcher.bat            # Windows launcher
├── launcher.sh             # Linux/Mac launcher
├── src/                    # Source code directory
│   ├── accessibility_checker.py  # Checking and fixing accessibility
│   ├── analysis.py               # Accessibility analysis
│   ├── enhancement.py            # Enhancement processing
│   ├── ppt_processor.py          # PowerPoint processing logic
│   ├── state.py                  # State management
│   ├── ui.py                     # UI components and layouts
│   ├── alt_text_generator.py      # Image alt text generator
│   ├── chat_assistant.py          # Accessibility assistant
│   ├── scoring.py                 # Scoring algorithms
│   ├── text_simplifier.py         # Text simplification
│   ├── utils.py                   # Helpers and utilities
│   └── images/                    # Image assets
```

## 🔧 Troubleshooting
### Ollama Connection Issues
- Make sure Ollama is running (`ollama serve` command)
- Check that the LLaVA model is downloaded (`ollama list`)
- Verify port **11434** is not blocked by a firewall

### PowerPoint Processing Errors
- Ensure your PowerPoint file is not password-protected
- Try saving your presentation with a different name
- Check for unsupported content (embedded videos, complex animations)

## ⚠️ Known Limitations
- **WMF/EMF Images**: Windows Metafile (WMF) and Enhanced Metafile (EMF) images cannot be processed by the AI for alt text generation. These will receive generic descriptions.
- **Complex Layouts**: Very complex slide layouts may not be perfectly analyzed.
- **Font Embedding**: Some custom fonts may not be properly detected.

## 🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.