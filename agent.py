import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_groq import ChatGroq
from langchain_community.agent_toolkits import create_sql_agent
from sqlalchemy import create_engine

# Load environment variables from .env file (like API keys)
# Node.js Equivalent: require('dotenv').config();
load_dotenv()

# We expect a GROQ_API_KEY in the environment. Let's make sure it's there.
if not os.getenv("GROQ_API_KEY"):
    print("WARNING: GROQ_API_KEY is missing from the environment. Please add it to your .env file.")

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
        # We use Groq's Llama 3 here as it's lightning fast and open source.
        # Node.js Equivalent: const llm = new ChatGroq({ model: "llama3-70b-8192", temperature: 0 });
        # temperature=0 ensures the model is deterministic and analytical, rather than creative.
        llm = ChatGroq(model="llama3-70b-8192", temperature=0)

        # 3. Create the SQL Agent
        # The agent acts as the 'brain'. It has tools to inspect table schemas, 
        # write SQL, run it, and interpret the result.
        # Node.js Equivalent: This is LangChain's pre-built agent executor for SQL.
        # We set return_intermediate_steps=True so we can show the generated SQL to the user.
        agent_executor = create_sql_agent(
            llm=llm,
            db=db,
            agent_type="tool-calling", # Modern approach using general tool-calling capabilities
            verbose=True, # Helpful for debugging, it prints the agent's thought process
            return_intermediate_steps=True
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
