import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage
from llm_gemini import Load_Gemini_Model
# Or use: from langchain_openai import ChatOpenAI

# --- Load LLM (Gemini or OpenAI) ---
llm = Load_Gemini_Model()

# --- Session State for Chat ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Streamlit Page Setup ---
st.set_page_config(page_title="🧠 ChatGPT-style Bot", page_icon="💬")
st.title("💬 Simple ChatBot")

# --- Display Full Chat History (Always)
for msg in st.session_state.chat_history:
    role = "user" if isinstance(msg, HumanMessage) else "ai"
    with st.chat_message(role):
        st.markdown(msg.content)

# --- User Input ---
user_input = st.chat_input("Ask me anything...")

if user_input:
    # Show user message immediately
    st.chat_message("user").markdown(user_input)
    user_msg = HumanMessage(content=user_input)
    st.session_state.chat_history.append(user_msg)

    # Get response from LLM
    response = llm.invoke(st.session_state.chat_history)

    # Show assistant message
    with st.chat_message("ai"):
        st.markdown(response.content)
    st.session_state.chat_history.append(response)
