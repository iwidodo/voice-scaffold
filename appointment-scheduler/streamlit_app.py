"""
Streamlit UI for the Appointment Scheduling Chatbot.
Run with: streamlit run streamlit_app.py
"""
import streamlit as st
import requests
from datetime import datetime
import json

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Healthcare Appointment Scheduler",
    page_icon="🏥",
    layout="centered"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None


def send_message(user_message: str) -> dict:
    """Send a message to the conversation API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/conversation/",
            json={
                "message": user_message,
                "conversation_id": st.session_state.conversation_id
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {
            "error": "Cannot connect to the backend server. Make sure it's running on http://localhost:8000"
        }
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.RequestException as e:
        return {"error": f"API Error: {str(e)}"}


def check_health() -> bool:
    """Check if the backend is healthy."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


# UI Layout
st.title("🏥 Healthcare Appointment Scheduler")
st.markdown("Chat with our AI assistant to schedule an appointment with a healthcare provider.")

# Check backend health
if not check_health():
    st.error("⚠️ Backend server is not running. Please start it with `./run_local.sh`")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("ℹ️ About")
    st.markdown("""
    This chatbot helps you:
    - Find the right healthcare provider
    - Check their availability
    - Schedule appointments
    
    **How to use:**
    1. Describe your health issue
    2. The assistant will suggest a provider
    3. Choose a convenient time slot
    4. Confirm your appointment
    """)
    
    st.divider()
    
    # Conversation info
    if st.session_state.conversation_id:
        st.caption(f"Conversation ID: {st.session_state.conversation_id[:8]}...")
    
    # Reset button
    if st.button("🔄 Start New Conversation"):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.rerun()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display suggested actions if available
        if message["role"] == "assistant" and "suggested_actions" in message:
            if message["suggested_actions"]:
                st.caption("💡 Suggestions:")
                for action in message["suggested_actions"]:
                    st.caption(f"  • {action}")

# Chat input
if prompt := st.chat_input("Describe your health issue or ask a question..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_data = send_message(prompt)
            
            if "error" in response_data:
                error_message = f"❌ Error: {response_data['error']}"
                st.error(error_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
            else:
                # Update conversation ID
                if response_data.get("conversation_id"):
                    st.session_state.conversation_id = response_data["conversation_id"]
                
                # Display assistant response
                assistant_message = response_data.get("response", "I'm sorry, I couldn't process that.")
                st.markdown(assistant_message)
                
                # Store message with metadata
                message_data = {
                    "role": "assistant",
                    "content": assistant_message,
                    "suggested_actions": response_data.get("suggested_actions", []),
                    "state": response_data.get("state")
                }
                st.session_state.messages.append(message_data)
                
                # Display suggested actions
                if response_data.get("suggested_actions"):
                    st.caption("💡 Suggestions:")
                    for action in response_data["suggested_actions"]:
                        st.caption(f"  • {action}")

# Footer
st.divider()
st.caption("Powered by OpenAI GPT-4 and FastAPI")
