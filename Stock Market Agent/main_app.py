import streamlit as st
from langchain_core.messages import HumanMessage
from main_graph import app  # your compiled LangGraph agent

# --- Session Setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- UI Header ---
st.set_page_config(page_title="📈 Stock Assistant", page_icon="💹")
st.title("💹 Stock Market Assistant")
st.caption("Ask me: 'What's the stock price of Google?'")

# --- User Input ---
user_query = st.chat_input("Ask about a stock...")

if user_query:
    # Show user message
    st.chat_message("user").write(user_query)

    # Append user message
    user_msg = HumanMessage(content=user_query)
    st.session_state.chat_history.append(user_msg)

    # Prepare input to LangGraph
    inputs = {"messages": st.session_state.chat_history}

    # Placeholder for AI response
    with st.chat_message("ai"):
        ai_placeholder = st.empty()
        final_response = ""

        try:
            for step in app.stream(inputs,stream_mode="values"):
                messages = step.get("messages", [])
                for msg in messages:
                    if hasattr(msg, "content") and isinstance(msg.content, str):
                        final_response = msg.content  # update final content
                        ai_placeholder.markdown(final_response)  # stream to UI
                        st.session_state.chat_history.append(msg)
        except Exception as e:
            ai_placeholder.markdown(f"❌ Error: {str(e)}")

# --- Show previous chat on refresh ---
elif st.session_state.chat_history:
    for msg in st.session_state.chat_history:
        role = "user" if msg.type == "human" else "ai"
        if hasattr(msg, "content") and isinstance(msg.content, str):
            st.chat_message(role).write(msg.content)
