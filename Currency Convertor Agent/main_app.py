import streamlit as st
from langchain_core.messages import HumanMessage
from main_graph import app  # your compiled LangGraph agent (currency version)

# --- Session Setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- UI Header ---
st.set_page_config(page_title="💱 Currency Converter", page_icon="💱")
st.title("💱 Currency Converter Assistant")
st.caption("Ask me: 'Convert 100 USD to PKR' or 'What is 1 EUR in GBP?'")

# --- User Input ---
user_query = st.chat_input("Enter your currency conversion query...")

if user_query:
    # Display user message
    st.chat_message("user").write(user_query)

    # Add to chat history
    user_msg = HumanMessage(content=user_query)
    st.session_state.chat_history.append(user_msg)

    # Input for LangGraph app
    inputs = {"messages": st.session_state.chat_history}

    # Response placeholder
    with st.chat_message("ai"):
        ai_placeholder = st.empty()
        final_response = ""

        try:
            for step in app.stream(inputs, stream_mode="values"):
                messages = step.get("messages", [])
                for msg in messages:
                    if hasattr(msg, "content") and isinstance(msg.content, str):
                        final_response = msg.content
                        ai_placeholder.markdown(final_response)
                        st.session_state.chat_history.append(msg)
        except Exception as e:
            ai_placeholder.markdown(f"❌ Error: {str(e)}")

# --- Display chat history after refresh ---
elif st.session_state.chat_history:
    for msg in st.session_state.chat_history:
        role = "user" if msg.type == "human" else "ai"
        if hasattr(msg, "content") and isinstance(msg.content, str):
            st.chat_message(role).write(msg.content)
