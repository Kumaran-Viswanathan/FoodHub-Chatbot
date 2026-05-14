from fastapi import FastAPI, Request
from pydantic import BaseModel
import os
import re
import sqlite3
import yaml

from langchain.agents import create_sql_agent, initialize_agent, AgentType
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_groq import ChatGroq
from langchain.memory import ConversationSummaryBufferMemory
from langchain.agents import Tool

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    question: str
    history: list

class ChatResponse(BaseModel):
    answer: str

# --- App Initialization ---
app = FastAPI(title="FoodHub Order Status Tracking")

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

groq_api_key = os.environ.get("GROQ_API_KEY")

# Initialize specialized LLMs
llm_sql = ChatGroq(model=config["llm_models"]["llm_sql"]["model_name"], temperature=0, groq_api_key=groq_api_key)
llm_reason = ChatGroq(model=config["llm_models"]["llm_reason"]["model_name"], temperature=0, groq_api_key=groq_api_key)
llm_response = ChatGroq(model=config["llm_models"]["llm_response"]["model_name"], temperature=0.2, groq_api_key=groq_api_key)

# DB Connection
db = SQLDatabase.from_uri(f"sqlite:///{config['database']['path']}")

# 1. SQL Agent Tool
toolkit = SQLDatabaseToolkit(db=db, llm=llm_sql)
db_agent = create_sql_agent(
    llm=llm_sql,
    toolkit=toolkit,
    verbose=True,
    handle_parsing_errors=True,
    system_message=SystemMessage("You are FoodHub SQL Expert. Only use SELECT statements. Always provide Order ID or Customer ID.")
)

sql_query_tool = Tool(
    name="FoodHub_Order_Database",
    func=db_agent.invoke,
    description="Useful for order status, items, preparation status or delivery info. Input: natural language query."
)

# 2. Escalation Tool
def handle_escalation(query: str) -> str:
    return "I will escalate your request to a human agent. Please provide your Order ID or Customer ID for a smoother handoff."
escalation_tool = Tool(name="Human_Agent", func=handle_escalation, description="Use when user is frustrated or for complex complaints.")

# --- Guardrails ---
def apply_input_guardrail(query):
    blocked_pattern = r'hacker|unauthorized|access\\s+all|steal|private|confidential|delete|harm|data\\s+security|vulnerability|breach|hacking'
    if re.search(blocked_pattern, query, re.IGNORECASE):
        return "I cannot assist with inappropriate or unauthorized requests. All interactions require proper verification."
    return None

def apply_output_guardrail(response_text):
    technical_leakage = ["SELECT *", "FROM orders", "SystemMessage", "HumanMessage", "SQLDatabase"]
    for keyword in technical_leakage:
        if keyword in response_text:
            return "I encountered a technical issue while formatting the response. Please try again or contact support."
    return response_text

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    # Apply Input Guardrail
    input_violation = apply_input_guardrail(request.question)
    if input_violation:
        return ChatResponse(answer=input_violation)

    # Setup Memory
    memory = ConversationSummaryBufferMemory(
        llm=llm_response,
        max_token_limit=2000,
        memory_key="chat_history",
        return_messages=True
    )
    for msg in request.history:
        if msg['role'] == 'user': memory.chat_memory.add_user_message(msg['content'])
        elif msg['role'] == 'assistant': memory.chat_memory.add_ai_message(msg['content'])

    # Main Agent Orchestration (ChefByte)
    agent = initialize_agent(
        tools=[sql_query_tool, escalation_tool],
        llm=llm_reason,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
        agent_kwargs={"system_message": SystemMessage("You are ChefByte, the friendly AI assistant for FoodHub. Always introduce yourself as ChefByte if asked.")}
    )

    try:
        agent_response = agent.invoke({"input": request.question})
        # Apply Output Guardrail
        final_answer = apply_output_guardrail(agent_response["output"])
        return ChatResponse(answer=final_answer)
    except Exception as e:
        return ChatResponse(answer=f"Processing error: {str(e)}")
