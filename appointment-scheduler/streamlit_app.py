"""
Streamlit UI for the Appointment Scheduling Chatbot.
Run with: streamlit run streamlit_app.py
"""
import streamlit as st
import requests
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    logger.info("[streamlit_app.py.root] Initialized new message history")
    
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
    logger.info("[streamlit_app.py.root] Initialized conversation_id as None")


def send_message(user_message: str) -> dict:
    """Send a message to the conversation API."""
    logger.info(f"[streamlit_app.py.send_message] Sending message: '{user_message[:50]}...' to API")
    
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
        logger.info(f"[streamlit_app.py.send_message] Received successful response from API")
        return response.json()
    except requests.exceptions.ConnectionError:
        logger.error("[streamlit_app.py.send_message] Connection error - backend server not reachable")
        return {
            "error": "Cannot connect to the backend server. Make sure it's running on http://localhost:8000"
        }
    except requests.exceptions.Timeout:
        logger.error("[streamlit_app.py.send_message] Request timeout")
        return {"error": "Request timed out. Please try again."}
    except requests.exceptions.RequestException as e:
        logger.error(f"[streamlit_app.py.send_message] API request error: {e}")
        return {"error": f"API Error: {str(e)}"}


def check_health() -> bool:
    """Check if the backend is healthy."""
    logger.debug("[streamlit_app.py.check_health] Checking backend health")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        is_healthy = response.status_code == 200
        logger.info(f"[streamlit_app.py.check_health] Backend health check: {'healthy' if is_healthy else 'unhealthy'}")
        return is_healthy
    except Exception as e:
        logger.error(f"[streamlit_app.py.check_health] Health check failed: {e}")
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
        logger.info("[streamlit_app.py.root] User initiated new conversation")
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
    logger.info(f"[streamlit_app.py.root] User input received: '{prompt[:50]}...'")
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            logger.debug("[streamlit_app.py.root] Sending message to backend")
            response_data = send_message(prompt)
            logger.debug(f"[streamlit_app.py.root] Response data: {response_data}")
            
            if "error" in response_data:
                error_message = f"❌ Error: {response_data['error']}"
                logger.error(f"[streamlit_app.py.root] Error in response: {response_data['error']}")
                st.error(error_message)
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })
            else:
                # Update conversation ID
                if response_data.get("conversation_id"):
                    st.session_state.conversation_id = response_data["conversation_id"]
                    logger.debug(f"[streamlit_app.py.root] Updated conversation_id: {st.session_state.conversation_id}")
                
                # Display assistant response
                assistant_message = response_data.get("response", "")
                
                # Handle empty response
                if not assistant_message or assistant_message.strip() == "":
                    logger.warning("[streamlit_app.py.root] Received empty response from backend")
                    assistant_message = "I'm processing your request. Please give me a moment..."
                
                logger.info(f"[streamlit_app.py.root] Displaying assistant response (length: {len(assistant_message)})")
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
