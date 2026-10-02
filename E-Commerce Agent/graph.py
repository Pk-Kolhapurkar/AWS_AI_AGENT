# graph.py
import os
import json
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from typing_extensions import TypedDict
from typing import Annotated

from tools import recommend_products as _recommend, place_order as _place, get_order as _get

load_dotenv()

# ---------- Tools exposed to the LLM ----------
@tool
def recommend_products(prompt: str) -> str:
    """Suggest products for a shopper based on what they ask for."""
    return json.dumps(_recommend(prompt))

@tool
def place_order(product_id: str, quantity: int) -> str:
    """Place an order for a product with given quantity."""
    return json.dumps(_place(product_id, quantity))

@tool
def get_order(order_id: str) -> str:
    """Look up the status of an existing order by its order id."""
    return json.dumps(_get(order_id))

TOOLS = [recommend_products, place_order, get_order]

# ---------- LLM ----------
llm = ChatGroq(
    model="openai/gpt-oss-120b",   # ✅ active, best for tool use
    temperature=0.2,
)

llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_PROMPT = SystemMessage(content=(
    "You are AnyCart's shopping assistant. "
    "Help users find products, place orders, and track orders. "
    "Always use the tools when the user asks about products, orders, or order status. "
    "When you place an order, always show the order_id clearly."
))

# ---------- State ----------
class State(TypedDict):
    messages: Annotated[list, add_messages]

# ---------- Nodes ----------
def orchestrator(state: State):
    messages = [SYSTEM_PROMPT] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(TOOLS)

def should_continue(state: State):
    last = state["messages"][-1]
    if getattr(last, "tool_calls", None):
        return "tools"
    return END

# ---------- Graph ----------
builder = StateGraph(State)
builder.add_node("orchestrator", orchestrator)
builder.add_node("tools", tool_node)

builder.add_edge(START, "orchestrator")
builder.add_conditional_edges("orchestrator", should_continue, {"tools": "tools", END: END})
builder.add_edge("tools", "orchestrator")

memory = MemorySaver()
graph = builder.compile(checkpointer=memory)

# ---------- Convenience wrapper for Streamlit ----------
def run_agent(user_message: str, thread_id: str = "default") -> str:
    """Run the graph and return the final assistant text."""
    config = {"configurable": {"thread_id": thread_id}}
    result = graph.invoke(
        {"messages": [{"role": "user", "content": user_message}]},
        config=config,
    )
    last = result["messages"][-1]
    return last.content if hasattr(last, "content") else str(last)

# ---------- Local test ----------
if __name__ == "__main__":
    print(run_agent("Can you recommend me some shoes?", thread_id="test1"))
    print(run_agent("Order running shoes product id 101 quantity 2", thread_id="test1"))