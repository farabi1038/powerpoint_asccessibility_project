"""
Accessibility Chat Assistant using Llama via Ollama.

This module provides a chat interface for users to ask accessibility-related questions.
"""

import streamlit as st
from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate

# Define the system prompt for the assistant
ASSISTANT_PROMPT_TEMPLATE = """
You are an accessibility expert assistant specializing in PowerPoint presentations.
Your role is to help users understand and implement accessibility best practices.
You provide clear, concise answers about:
- Alt text for images
- Font size and readability
- Color contrast requirements
- Text complexity and simplification
- WCAG compliance guidelines
- Screen reader compatibility

Always be helpful, practical, and focus on actionable advice.

User: {question}
Assistant: """

def initialize_chat():
    """Initialize the chat assistant"""
    # Initialize chat history in session state if it doesn't exist
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hello! I'm your accessibility assistant. How can I help you improve your presentation's accessibility?"}
        ]

def create_chat_interface():
    """Create and display the chat interface"""
    st.markdown("<h3 style='color: #2E7D32;'>Accessibility Assistant</h3>", unsafe_allow_html=True)
    
    # Initialize chat
    initialize_chat()
    
    # Create the chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Check if Ollama is available
    ollama_available = check_ollama_availability()
    
    # User input
    if user_input := st.chat_input("Ask about accessibility...", disabled=not ollama_available):
        # Add user message to history
        st.session_state.chat_messages.append({"role": "user", "content": user_input})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        
        if ollama_available:
            # Generate response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    response = generate_response(user_input)
                    st.markdown(response)
            
            # Add assistant response to history
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
        else:
            # Add error message if Ollama is not available
            error_msg = "Sorry, I can't respond right now. The AI service is not available. Please check the Ollama service status in the sidebar."
            with st.chat_message("assistant"):
                st.error(error_msg)
            st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})

def generate_response(question):
    """Generate a response using the Llama model via Ollama"""
    try:
        # Create template and prompt
        template = ASSISTANT_PROMPT_TEMPLATE
        prompt = ChatPromptTemplate.from_template(template)
        
        # Use llama3.2 if available, fall back to llava
        try:
            model = OllamaLLM(model="llama3.2", temperature=0.7)
        except:
            model = OllamaLLM(model="llava", temperature=0.7)
        
        # Create chain and invoke
        chain = prompt | model
        response = chain.invoke({"question": question})
        
        return response
    except Exception as e:
        return f"I encountered an error: {str(e)}. Please check if Ollama is running properly."

def check_ollama_availability():
    """Check if Ollama is available"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/health", timeout=1)
        return response.status_code == 200
    except:
        return False 