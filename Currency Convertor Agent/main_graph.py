from langchain_core.messages import BaseMessage,HumanMessage,SystemMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.graph.message import add_messages
from typing import Annotated, Sequence
from pydantic import BaseModel


from llm_gemini import Load_Gemini_Model
from Tool_api import get_conversion_factor,currency_convert


## loading environment variables in .env file
from dotenv import load_dotenv
load_dotenv()


llm = Load_Gemini_Model()

custom_tools = [get_conversion_factor,currency_convert]

llm_with_tools = llm.bind_tools(custom_tools)

## build schema of graph
class AgentState(BaseModel):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# build agent node
def agent_node(state: AgentState) -> AgentState:
    system_message = SystemMessage(content=
        "You are my AI assistant, please answer my query to the best of your ability.")
    response = llm_with_tools.invoke([system_message]+state.messages)
    return {"messages": [response]}

## building graph

graph = StateGraph(AgentState)

graph.add_node(node="agent",action=agent_node)
graph.add_node(node="tools",action=ToolNode(tools=custom_tools))

graph.set_entry_point(key="agent")

graph.add_conditional_edges(source="agent",path=tools_condition)

graph.add_edge(start_key="tools",end_key="agent")
graph.set_finish_point(key="agent")

app = graph.compile()


inputs = {
    "messages": 
    [HumanMessage(
        content="""convert 5 USD dollar to pakistani rupees
        And Tell me a joke""")]
}

if __name__ == "__main__":
    ## print the only last message of the llm
    result = app.invoke(inputs)
    agent_message = " ".join(result["messages"][-1].content.split("\n"))
    print(agent_message)

    # for message in app.stream(input=inputs,stream_mode="values"):
    #     last_message = message['messages'][-1]
    #     last_message.pretty_print()
