import streamlit as st
from agent import ask_database

# --- Streamlit Frontend Configuration ---
# Streamlit is like React but strictly for Python data apps. It's declarative.
# Node.js Equivalent: Imagine a combination of Next.js frontend and Express backend in one file.

st.set_page_config(
    page_title="Enterprise Text-to-SQL Agent",
    page_icon="🤖",
    layout="centered"
)

# --- Custom Styling for a Clean, Modern UI ---
# Inject custom CSS to make it look premium
# Node.js Equivalent: Injecting <style> tags or using styled-components
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #f4f7f6;
    }
    /* Title styling */
    h1 {
        color: #2c3e50;
        text-align: center;
        font-family: 'Helvetica Neue', sans-serif;
    }
    /* Answer box styling */
    .answer-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-top: 20px;
        font-size: 1.1em;
        color: #34495e;
        border-left: 5px solid #3498db;
    }
    /* Adjust text inputs somewhat */
    .stTextInput>div>div>input {
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# --- Application Header ---
st.title("🤖 Enterprise Text-to-SQL Agent")
st.markdown("<p style='text-align: center; color: #7f8c8d; font-size: 1.2em;'>Ask questions about your e-commerce data in plain English.</p>", unsafe_allow_html=True)

st.divider()

# --- User Input ---
# Node.js Equivalent: const [query, setQuery] = useState("");
user_query = st.text_input("What would you like to know?", placeholder="e.g., Show me the top 5 most expensive products.")

# --- Action ---
# If the user has typed a query and pressed enter (or a button)
# Node.js Equivalent: if (query) { handleFormSubmit(); }
if user_query:
    # Display a loading spinner while the agent 'thinks'
    # Node.js Equivalent: { isLoading && <Spinner /> }
    with st.spinner("Analyzing database schema, writing SQL, and interpreting results..."):
        
        # Call our AI Brain (agent.py)
        result = ask_database(user_query)
        
        # Display the result
        if isinstance(result, dict):
            # We use a custom HTML div to make the answer look nice (styled above)
            st.markdown(f'<div class="answer-box"><strong>Answer:</strong><br>{result["answer"]}</div>', unsafe_allow_html=True)
            
            # Bonus: Show the actual SQL query to the recruiter
            if result.get("sql_query"):
                st.markdown("<br>### 🔍 Under the Hood: Generated SQL", unsafe_allow_html=True)
                st.code(result["sql_query"], language="sql")
        else:
            # Handle error string case (if an exception was caught in agent.py)
            st.error(result)

# --- Footer / Context ---
st.markdown("<br><br>", unsafe_allow_html=True)
with st.expander("ℹ️ How it works under the hood"):
    st.write("""
        1. **User Input:** You ask a question in natural language (e.g., "How many orders were placed?").
        2. **LangChain SQL Agent:** An LLM reads the database schema (`Users`, `Products`, `Orders`) and writes a valid SQL query.
        3. **Execution:** The SQL query runs against the local SQLite database.
        4. **Synthesis:** The LLM translates the raw SQL results back into a friendly English sentence.
    """)
