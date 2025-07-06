import streamlit as st
import requests

st.title("🤖 PlanPal - Your Calendar Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Get user input
prompt = st.chat_input("Ask me to book/reschedule/delete an event...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            res = requests.post("http://localhost:8000/agent", json={"message": prompt})
            reply = res.json().get("response", "Something went wrong.")
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
