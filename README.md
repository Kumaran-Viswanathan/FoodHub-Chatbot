---
title: FoodHub-ChefByte
emoji: 🍴
colorFrom: green
colorTo: blue
sdk: docker
app_file: app.py
pinned: false
---

# ChefByte: FoodHub Customer Support AI
ChefByte is a sophisticated, AI-powered chatbot designed to handle food order queries for the FoodHub platform. It combines SQL-based data retrieval with specialized language models to provide accurate, polite, and contextual support.



### Project Title
**FoodHub Customer Support Chatbot with SQL Agent and Guardrails**

### Description
This project implements an AI-powered chatbot for FoodHub, a food aggregator company, to automate customer support queries related to order details. The chatbot leverages a **Triple-LLM specialized architecture** using Groq's Llama 3.1 models for distinct roles: SQL query generation, reasoning, and response generation. It interacts with an SQL database (`customer_orders.db`) to fetch accurate order information and provides concise, polite, and customer-friendly responses. Additionally, the chatbot incorporates input and output guardrails to ensure safe interactions, prevent misuse, and escalate complex queries to human agents when necessary.

## 🚀 Project Architecture
The system utilizes a **Triple-LLM specialized architecture** using Llama 3.3 models via Groq:

### Key Features

- **Automated Order Tracking:** Direct integration with SQLite database via LangChain SQL Agent.
- **Advanced Memory:** Uses `ConversationSummaryBufferMemory` for efficient long-term context retention.
- **Safety First:** Built-in regex-based input guardrails to prevent malicious interactions and protect data.
- **FastAPI Backend:** High-performance async backend for agent orchestration.
- **Streamlit Frontend:** User-friendly web interface for customer interactions.

#### 1. Triple-LLM Architecture:
-   **SQL Agent LLM (Llama-3.3-70B-Versatile, temperature=0.0):** Generates precise SQL SELECT statements to query the `customer_orders.db` for order information.
-   **Reasoning LLM (Llama-3.3-70B-Versatile, temperature=0.0):** Acts as the 'brain' of the conversational agent, orchestrating tool selection (e.g., database lookup, human escalation) and managing conversational flow.
-   **Response & Summarization LLM (Llama-3.3-70B-Versatile, temperature=0.2):** Summarizes conversation history for long-term memory and formulates polite, customer-friendly responses.

#### 2. Agents & Tools:
-   **SQL Agent (db_agent):** Handles all database interactions, translating natural language queries into SQL and retrieving order details.
-   **Conversational Agent (notebook_conversational_agent):** The main agent combining the three LLMs with specialized tools to manage dialogue and process user requests.
-   **FoodHub_Order_Database:** An interface for the SQL agent to interact with the database.
-   **Human_Agent:** A tool for escalating complex, sensitive, or frustrated customer queries to human support.

#### 3. Memory Management:
-   **ConversationBufferMemory (Short-term):** Stores recent conversational turns for immediate context.
-   **ConversationSummaryBufferMemory (Long-term):** Summarizes older parts of the conversation (powered by `llm_response`) to maintain context over longer interactions without exceeding token limits.

#### 4. Guardrails:
-   **Input Guardrail (Regex-based):** Detects and blocks malicious, inappropriate, or harmful queries to prevent misuse.
-   **Output Guardrail:** Filters AI responses to prevent technical leakage (e.g., raw SQL, internal prompts) and ensures professional language.

### Deployment
The project is designed for seamless deployment to Hugging Face Spaces using Docker. It includes:
-   **FastAPI Backend (`backend.py`):** Provides a robust, async API endpoint (`/chat`) for processing user queries, integrating LLMs, tools, memory, and guardrails.
-   **Streamlit Frontend (`app.py`):** A user-friendly web interface that communicates with the FastAPI backend to display the chatbot.
-   **Configuration (`config.yaml`):** Externalizes LLM model names, temperatures, and database path for easy management.
-   **Dockerfile:** Packages the entire application (FastAPI, Streamlit, database, dependencies) into a portable container.
-   **GitHub Actions:** Configured for Continuous Integration/Continuous Deployment (CI/CD) to automate deployment to Hugging Face Spaces.

This setup ensures a modular, scalable, and secure AI chatbot capable of intelligently responding to customer queries while maintaining conversation context and adhering to safety protocols.

## 📦 Deployment Instructions

### 1. Repository Setup
- Ensure `app.py`, `backend.py`, `config.yaml`, and `customer_orders.db` are in the root directory.

### 2. Environment Secrets
Configure the following secrets in your Deployment Platform (GitHub/Hugging Face):
- `GROQ_API_KEY`: Your API key from Groq Console.
- `HF_TOKEN`: Hugging Face Write Token for deployment sync.

### 3. Docker Deployment
The project is pre-configured with a `Dockerfile` for easy deployment to Hugging Face Spaces:
```bash
# Build and Run (Local Test)
docker build -t chefbyte .
docker run -p 8501:8501 -p 8000:8000 -e GROQ_API_KEY=your_key chefbyte
```

## 📄 File Manifest
- `backend.py`: FastAPI application & LangChain Agent logic.
- `app.py`: Streamlit Chat Interface.
- `config.yaml`: LLM & Database configurations.
- `customer_orders.db`: SQLite database for order tracking.
- `Dockerfile`: Container configuration for production.
- `requirements.txt`: Python dependency list.
