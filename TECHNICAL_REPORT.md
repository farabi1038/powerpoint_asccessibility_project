# PowerPoint Accessibility Enhancer: Technical Report

## Executive Summary
The PowerPoint Accessibility Enhancer is a Streamlit-based web application designed to improve the accessibility of PowerPoint presentations. It targets creators who want to make their content more accessible to individuals with disabilities, addressing key aspects of accessibility including image descriptions, text readability, color contrast, and overall WCAG compliance.

## Project Overview
### Motivation
Accessibility is a crucial aspect of content creation that is often overlooked. Many PowerPoint presentations lack proper accessibility features, making them difficult or impossible to use for people with disabilities. This project aims to provide an automated solution to enhance accessibility in existing presentations.

### Objectives
- Develop a tool that analyzes PowerPoint presentations for accessibility issues
- Implement AI-powered solutions to automatically enhance accessibility
- Provide comprehensive reports on accessibility compliance
- Make the tool user-friendly and accessible to non-technical users

## Technical Implementation

### Architecture
The application follows a modular architecture with the following components:
- **Frontend**: Streamlit web interface for user interaction
- **Processing Engine**: PowerPoint file parsing and modification
- **Analysis Module**: Evaluates presentations against accessibility standards
- **Enhancement Module**: Applies fixes to identified issues
- **AI Integration**: Connects with Ollama to provide AI-powered enhancements
- **Reporting**: Generates comprehensive accessibility reports

### Key Technologies
- **Streamlit**: Web application framework for the user interface
- **Python**: Primary programming language (v3.10+)
- **python-pptx**: Library for PowerPoint file manipulation
- **Ollama**: Local AI model server (v0.1.2)
- **LLaVA**: Large Language and Vision Assistant model for image understanding
- **PIL/Pillow**: Image processing for contrast analysis and format conversions
- **WCAG Contrast Ratio**: Library for accessibility contrast calculations
- **Docker**: Containerization for easy deployment
- **PyTorch**: Deep learning framework supporting the AI components

## Feature Implementation Details

### Accessibility Analysis
The application analyzes PowerPoint presentations against WCAG (Web Content Accessibility Guidelines) standards. This includes:
- Text size and readability evaluation (minimum 18pt recommended size)
- Color contrast analysis (minimum 4.5:1 for normal text, 3:1 for large text)
- Alt text presence verification
- Slide structure assessment
- Reading order validation

The scoring module provides numerical assessments of accessibility compliance, with weighted categories including text contrast, font size, alt text presence, and text complexity. The overall accessibility score helps users track improvements as they enhance their presentations.

### AI-powered Alt Text Generation
One of the key innovations is the automatic generation of descriptive alt text for images:
- Integration with LLaVA model via Ollama
- Image extraction from PowerPoint slides
- Context-aware description generation
- Fallback mechanisms when AI services are unavailable
- Support for varying detail levels (concise vs. detailed descriptions)
- Image preprocessing including format conversion and resizing

The implementation extracts images from presentations, processes them through the LLaVA model, and reintegrates the generated descriptions back into the PowerPoint file. The system handles image format conversions, including automatically converting RGBA images to RGB with white backgrounds for better compatibility with the AI model. The alt text generator includes retry mechanisms and error handling to ensure reliability.

### Font Size Optimization
The application detects text elements that may be difficult to read due to small font sizes:
- Analysis of text elements across all slides
- Identification of text below recommended size thresholds (18pt minimum)
- Automatic adjustment of font sizes to meet accessibility standards
- Preservation of relative size relationships between text elements

### Color Contrast Enhancement
Poor color contrast can make text difficult to read for users with visual impairments:
- Calculation of contrast ratios between text and background using WCAG standards
- Identification of contrast issues based on WCAG guidelines (4.5:1 ratio for normal text)
- Automatic adjustment of text or background colors to improve contrast
- Intelligent contrast fixing that chooses whether to darken text or lighten backgrounds
- Preservation of brand colors and design aesthetics where possible

The system uses an adaptive approach to contrast enhancement, analyzing text luminance to determine whether to adjust text or background colors for optimal readability while maintaining visual appeal.

### Text Simplification
Complex language can be a barrier to comprehension for many users:
- Analysis of text complexity using readability metrics
- Identification of overly complex sentences and terminology
- Suggestion of simplified alternatives
- Optional automatic implementation of simplifications

### Comprehensive Reports
The application generates detailed reports on accessibility issues:
- Slide-by-slide analysis
- Issue categorization and severity rating
- Before/after comparisons
- Exportable HTML format for accessibility documentation

## Implementation Challenges

### PowerPoint Format Complexity
The PowerPoint file format presents significant challenges:
- Complex object model with nested elements
- Variations between PowerPoint versions
- Limited documentation for some advanced features
- Special handling required for embedded objects and media

### AI Integration Challenges
Integrating AI capabilities presented several challenges:
- Balancing model quality with performance
- Managing dependencies on external services
- Handling unsupported image formats (WMF/EMF)
- Ensuring context-appropriate descriptions
- Cross-platform compatibility for Ollama integration
- Automated Ollama service management

The system includes sophisticated service management to detect if Ollama is running, start it if necessary, and check for the availability of the LLaVA model. This includes special handling for Windows environments and WSL (Windows Subsystem for Linux) detection.

### Performance Optimization
Processing large presentations required optimization:
- Parallelization of image processing
- Efficient memory management for large files
- Progress tracking and cancellation options
- Caching strategies for intermediate results
- Image resizing to maximum dimensions of 512px before AI processing
- Limiting token generation for faster processing

## Testing and Validation

### Accessibility Testing
The application was tested with:
- Screen reader compatibility testing
- Color contrast analyzers
- Automated accessibility checkers
- User testing with individuals with disabilities

### Performance Testing
Performance was validated with:
- Large presentation files (100+ slides)
- Presentations with numerous images
- Complex layouts and embedded content
- Various PowerPoint versions (2010 through 2021)

## Deployment and Distribution

### Deployment Options
The application can be deployed in several ways:
- Local installation (Windows, macOS, Linux)
- Docker containerization with multi-container setup
- Potential cloud-based SaaS deployment

The Docker implementation uses a multi-container approach with docker-compose, separating the Ollama service from the Streamlit application for better scalability and resource management.

### Dependencies Management
Dependencies are managed through:
- Requirements.txt for Python dependencies (including version pinning)
- Launcher scripts for environment setup (Windows and Unix variants)
- Docker containerization for consistent environments
- Special handling for platform-specific dependencies (e.g., python-magic-bin for Windows)

The launcher scripts provide a seamless experience across operating systems, automating the process of starting Ollama, pulling necessary models, and launching the Streamlit application.

## Cross-Platform Compatibility
The application is designed to work across multiple platforms:
- Windows-specific launcher (launcher.bat) with CMD command execution
- Unix/Linux/Mac launcher (launcher.sh) with bash scripting
- WSL (Windows Subsystem for Linux) detection and special networking setup
- Docker containerization for platform-agnostic deployment
- Platform-specific dependency handling in requirements.txt

## Future Enhancements

### Planned Improvements
Future work includes:
- Support for additional presentation formats (Google Slides, Keynote)
- Advanced layout optimization for screen readers
- Integration with additional AI models for enhanced capabilities
- Batch processing for multiple presentations
- API endpoints for integration with other systems
- Enhanced detection of slide structures and reading order
- Support for additional WCAG compliance criteria

## Conclusion
The PowerPoint Accessibility Enhancer provides a powerful, automated solution for improving presentation accessibility. By combining AI capabilities with accessibility expertise, it enables content creators to produce materials that are accessible to all users, including those with disabilities. The modular architecture allows for ongoing enhancements and adaptations to evolving accessibility standards.

The implementation balances ease of use with powerful features, making accessibility improvements accessible to non-technical users. The cross-platform compatibility ensures that the tool can be used across diverse environments, and the containerized deployment option provides a path to easy distribution and scalability. 