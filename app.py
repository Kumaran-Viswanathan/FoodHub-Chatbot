import streamlit as st
import requests
import os

# --- Streamlit Page Configuration ---
st.set_page_config(page_title="FoodHub Chatbot", page_icon=":robot:", layout="centered")

st.title("354 FoodHub Customer Support")
st.markdown("Hello! I am ChefByte, your AI assistant. How can I help you today?")

# Pointing to localhost within the same container
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What would you like to know about your order?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("ChefByte is thinking..."):
        try:
            response = requests.post(
                f"{BACKEND_URL}/chat",
                json={"question": prompt, "history": st.session_state.messages},
                timeout=60
            )
            response.raise_for_status()
            response_text = response.json().get("answer", "Sorry, I could not process that.")

        except Exception as e:
            response_text = f"Connection error: {e}"

        with st.chat_message("assistant"):
            st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})
