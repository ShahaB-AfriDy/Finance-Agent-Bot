from langgraph.graph import StateGraph, add_messages,END
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage,SystemMessage, ToolMessage
from langchain.tools import tool

from pydantic import BaseModel,Field
from typing import Annotated,Sequence

import os
from dotenv import load_dotenv

load_dotenv()


###################################################################
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)
###################################################################
Document_Content = ""
###################################################################

### create schema of graph
class AgentState(BaseModel):
    messages: Annotated[Sequence[BaseMessage],add_messages,
                    Field(...,description="The Chat history is required")]

###################################################################
############################ make tools
@tool
def Save_File(file_name:str) -> str:
    """Save the current document to a text file and finish the process.
    Args:
        filename: Name for the text file.
    """
    global Document_Content

    if not file_name.endswith(".txt"):
        file_name = F"{file_name}.txt"

    try:
        with open(file_name,"w") as file:
            file.write(Document_Content)
        print(F"Document has been successfully saved to: {file_name}")
        return F"Document has been successfully saved to: {file_name}"
    except Exception as e:
        return F"Error during save document {e}"
###################################################################
def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end the conversation."""

    messages = state.messages
    
    if not messages:
        return "continue"
    
    # This looks for the most recent tool message....
    for message in reversed(messages):
        # ... and checks if this is a ToolMessage resulting from save
        if (isinstance(message, ToolMessage) and 
            "saved" in message.content.lower() and
            "document" in message.content.lower()):
            return "end" # goes to the end edge which leads to the endpoint
        
    return "continue"
###################################################################
## make list of tools and also bind the llm
custom_tools = [Save_File]
llm_with_tools = llm.bind_tools(tools=custom_tools)
###################################################################

def agent_node(state: AgentState) -> AgentState:
    system_prompt = SystemMessage(content=f"""
    You are Drafter, a helpful writing assistant. You are going to help the user save the documents.
    
    - If the user wants to save and finish, you need to use the 'save' tool.
    - Make sure to always show the current document state after modifications.
    
    The current document content is:{Document_Content}
    """)
    
    if not state.messages:
        intial_input = "I'm ready to help you update a document. What would you like to create?"
        ai_message = AIMessage(content=intial_input)

    else:
        user_input = input("\nWhat would you like to do with the document? ")
        print(f"\n👤 USER: {user_input}")
        user_message = HumanMessage(content=user_input)

    all_messages = [system_prompt] + [ai_message] + list(state.messages) + [user_message]

    response = llm_with_tools.invoke(all_messages)

    print(f"\n🤖 AI: {response.content}")
    if hasattr(response, "tool_calls") and response.tool_calls:
        print(f"🔧 USING TOOLS: {[tc['name'] for tc in response.tool_calls]}")

    return {"messages": list(state.messages) + [user_message, response]}

###################################################################
## make graph

graph = StateGraph(AgentState)

graph.add_node(node="agent",action=agent_node)
graph.add_node(node="tools",action=ToolNode(tools=custom_tools))


graph.set_entry_point(key="agent")
graph.add_edge("agent", "tools")

graph.add_conditional_edges(
    source="tools",
    path=should_continue,
    path_map={
        "continue": "agent",
        "end": END,
    },
)

app = graph.compile()
###################################################################
def Run_Document_Agent():
    print("\n","DRAFTER".center(100,"="))
    user_input = ""
    while True:
        for step in app.stream({"messages": [HumanMessage(content=user_input)]},stream_mode='values'):
            step['messages'][-1].pretty_print()
        print("\n","USER".center(80,"="))
        user_input = input("You: ")
        if user_input in  ['quit','exit','q']:
            print("Goodbye".center(100,"="))
            break           
    print("\n","DRAFTER FINISHED".center(100,"="))
######################################################################

if __name__ == "__main__":
    Run_Document_Agent()