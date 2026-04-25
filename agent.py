import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from sqlalchemy import create_engine

# Load environment variables from .env file (like API keys)
# Node.js Equivalent: require('dotenv').config();
load_dotenv()

# Try to get the API key from environment variables or Streamlit secrets
api_key = os.getenv("API_KEY") or os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    try:
        import streamlit as st
        # Fallback to Streamlit Secrets
        api_key = st.secrets.get("OPENAI_API_KEY") or st.secrets.get("API_KEY") or st.secrets.get("XAI_API_KEY")
    except Exception:
        pass

if api_key:
    # Force set it in the environment so LangChain/OpenAI picks it up natively
    # This prevents the "Sync client is not available" bug.
    os.environ["OPENAI_API_KEY"] = str(api_key).strip()
else:
    print("WARNING: API Key is missing. Please add OPENAI_API_KEY to your .env file or Streamlit Secrets.")

# Define the connection string for SQLite
# Node.js Equivalent: This is the connection URL string.
db_uri = "sqlite:///ecommerce.db"

def ask_database(user_question):
    """
    Takes a natural language question, converts it to a SQL query using an LLM,
    executes the query against the SQLite database, and returns a plain English answer.
    """
    try:
        # 1. Connect to the Database
        # LangChain needs a SQLDatabase object, which wraps SQLAlchemy.
        db = SQLDatabase.from_uri(db_uri)

        # 2. Initialize the LLM (Large Language Model)
        # We are using an OpenAI-compatible client. If you are using xAI (Grok), 
        # make sure to set the BASE_URL to https://api.xai.com/v1 if needed.
        # Note: 'grok-4.20-reasoning' is a custom model name you provided.
        base_url = os.getenv("BASE_URL") # E.g., https://api.xai.com/v1
        
        # We let ChatOpenAI pull the API key directly from os.environ["OPENAI_API_KEY"]
        llm = ChatOpenAI(
            base_url=base_url if base_url else None,
            model="grok-4.20-reasoning", 
            temperature=0
        )

        # --- DIAGNOSTIC CHECK ---
        # We ping the API directly using 'requests' to see exactly what the proxy is returning.
        # This will bypass Langchain and catch any weird proxy behaviors.
        import requests
        debug_url = base_url if base_url else "https://api.openai.com/v1"
        debug_url = debug_url.rstrip("/") + "/chat/completions"
        debug_headers = {
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
            "Content-Type": "application/json"
        }
        debug_payload = {
            "model": "grok-4.20-reasoning",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        try:
            debug_resp = requests.post(debug_url, headers=debug_headers, json=debug_payload, timeout=10)
            debug_json = debug_resp.json()
            if debug_resp.status_code != 200 or not debug_json.get("choices"):
                return {
                    "answer": f"⚠️ **API Provider Issue Detected:**\nThe API provider returned an invalid response. This is NOT a code issue. See raw details below.",
                    "sql_query": f"HTTP Status: {debug_resp.status_code}\nRaw API Response:\n{debug_resp.text}"
                }
        except Exception as debug_e:
            return f"⚠️ **Network Request Failed:** Could not reach the API. Error: {str(debug_e)}"
        # --- END DIAGNOSTIC CHECK ---

        # 3. Create the SQL Agent
        # The agent acts as the 'brain'. It has tools to inspect table schemas, 
        # write SQL, run it, and interpret the result.
        # Node.js Equivalent: This is LangChain's pre-built agent executor for SQL.
        # We use a zero-shot-react agent because some third-party models or proxies
        # do not fully support native OpenAI tool-calling. This is universally compatible.
        agent_executor = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="zero-shot-react-description", # Generic text-based tool execution
            verbose=True, # Helpful for debugging, it prints the agent's thought process
            return_intermediate_steps=True,
            handle_parsing_errors=True # Crucial for non-standard models
        )

        # 4. Run the Agent
        # The invoke method sends the prompt to the LLM.
        # Node.js Equivalent: const result = await agentExecutor.invoke({ input: userQuestion });
        response = agent_executor.invoke({"input": user_question})
        
        # 5. Extract the Final Answer
        final_answer = response.get("output", "Sorry, I couldn't find an answer.")
        
        # 6. Extract the generated SQL query from the agent's intermediate steps
        sql_query = None
        for step in response.get("intermediate_steps", []):
            action, observation = step
            if action.tool == "sql_db_query":
                sql_query = action.tool_input
                # Sometimes the agent passes tool_input as a dict like: {'query': 'SELECT ...'}
                # sometimes it passes it as a plain string. We handle both.
                if isinstance(sql_query, dict):
                    sql_query = sql_query.get('query')
                break # Just get the first SQL query if there are multiple

        return {
            "answer": final_answer,
            "sql_query": sql_query
        }

    except Exception as e:
        # Graceful error handling
        # If the LLM writes a bad query or something else fails, we catch it here.
        # Node.js Equivalent: catch (error) { return `An error occurred: ${error.message}`; }
        print(f"Error during agent execution: {e}")
        return f"I encountered an error trying to answer that: {str(e)}"

# A quick way to test the agent locally without running Streamlit
if __name__ == "__main__":
    print("Testing the AI Agent locally...")
    test_question = "How many users signed up?"
    print(f"Question: {test_question}")
    result = ask_database(test_question)
    print(f"Result: {result}")
