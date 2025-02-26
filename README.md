# PowerPoint Accessibility Enhancer

A Streamlit application that improves accessibility of PowerPoint presentations by adding alt text, fixing font sizes, and more.

## Features

- **Accessibility Analysis**: Evaluates presentations against WCAG standards
- **AI-powered Alt Text Generation**: Uses LLaVA via Ollama to create descriptive alt text for images
- **Font Size Optimization**: Adjusts text to ensure readability
- **Accessibility Report**: Provides a downloadable HTML report

## Installation

1. Clone this repository
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Install Ollama for AI-powered alt text generation:
   - Download from [ollama.ai/download](https://ollama.ai/download)
   - Pull the LLaVA model:
     ```
     ollama pull llava
     ```

## Usage

1. Run the Streamlit app:
   ```
   streamlit run app.py
   ```
2. Start Ollama with the LLaVA model:
   ```
   ollama run llava
   ```
3. Upload your PowerPoint presentation
4. Analyze accessibility
5. Click "Enhance Presentation" to improve accessibility
6. Download the enhanced presentation

## LLaVA Integration

This application uses the LLaVA (Large Language and Vision Assistant) model via Ollama to generate descriptive alt text for images. LLaVA combines vision capabilities with language understanding to create contextually relevant image descriptions for screen readers.

If Ollama is not available, the application will fall back to using basic placeholder text.

## Requirements

- Python 3.8+
- Streamlit
- python-pptx
- Pillow
- Ollama (for AI-powered alt text)

## Known Limitations

- WMF (Windows Metafile) images in PowerPoint presentations can't be processed for AI-based alt text generation. These images will be assigned a generic alt text.
- EMF (Enhanced Metafile) images may have similar limitations.

## Development

The project is organized into modules:
- `ppt_processor.py`: Handles PowerPoint file operations
- `alt_text_generator.py`: Generates alt text for images
- `accessibility_checker.py`: Checks and fixes font/contrast issues
- `text_simplifier.py`: Simplifies complex text
- `scoring.py`: Implements accessibility scoring

## System Dependencies

For better handling of Windows Metafile (WMF) and Enhanced Metafile (EMF) images, install:

**For Ubuntu/Debian:**
```bash
sudo apt-get install librsvg2-bin python3-magic
```

**For macOS:**
```bash
brew install librsvg
pip install python-magic
```

**For Windows:**
Install Python Magic and its dependencies:
```bash
pip install python-magic-bin
```

# For GPU support
To install PyTorch with CUDA support:

```bash
# First, uninstall any existing PyTorch installation
pip uninstall torch torchvision torchaudio -y

# Then, install PyTorch with CUDA support using the official command
# This will detect your CUDA version and install the appropriate package
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

# For CUDA 12.x:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 11.7:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu117
 
