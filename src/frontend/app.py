import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from langchain.tools import BaseTool
import os, json
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.config import Config
from langchain.agents import initialize_agent, AgentType
from src.rag_agent.agentrag import rag_agent
from src.tariff_agent.agentsql import sql_agent
from src.utils.raghelper import generate_query
import streamlit as st

st.set_page_config(page_title="RAG Agent", page_icon=":robot_face:", layout="wide")
expander = st.sidebar.toggle("Enable expander mode", key="expander_mode", help="Enable this to show the thinking process in an expander.")

# Session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

if "expander_mode" not in st.session_state:
    st.session_state.expander_mode = False
    
if "initial_expander" not in st.session_state:
    st.session_state.initial_expander = True

if "last_sql_result" not in st.session_state:
    st.session_state.last_sql_result = None

class RagAgent(BaseTool):
    name: str = "Document_Search_Agent"
    description: str = """Use this tool ONLY for:
    - General questions about tariffs, trade, or HTS codes that need document-based answers
    - Questions asking for explanations, definitions, or background information
    - Questions about trade policies, procedures, or regulations
    - When you need to search through documents for conceptual information
    
    DO NOT use for:
    - Specific calculations or numerical queries
    - Questions asking for data from specific HTS codes
    - Questions requiring database lookups or structured data retrieval"""

    def _run(self, text: str):
        if isinstance(text, dict):
            text = text.get('output', str(text))
        
        result = rag_agent(text)
        return str(result)

    async def _arun(self, text: str):
        return self._run(text)

class SQLAgent(BaseTool):
    name: str = "Database_Query_Agent"
    description: str = """Use this tool ONLY for:
    - Questions asking for specific data about HTS codes (like rates, duties, descriptions)
    - Calculations involving tariff rates, duty amounts, or costs
    - Questions asking "what is the rate for HTS code X"
    - Questions asking about specific countries, duty amounts, or CIF values
    - Questions requiring numerical data retrieval from the database
    - Questions asking to "calculate", "find rate", "get duty amount", etc.
    
    Keywords that indicate this tool should be used:
    - HTS code followed by numbers (e.g., "HTS 0101.30.00.00")
    - "calculate duty", "duty rate", "tariff rate"
    - "CIF value", "product cost", "freight", "insurance"
    - "special rate", "general rate", "column 2 rate"
    - Specific numerical queries about trade data"""

    def _run(self, text: str):
        try:
            if isinstance(text, dict):
                text = text.get('output', str(text))
            
            # Generate the SQL query from the text
            query = generate_query(text)
            
            # Execute the query using sql_agent
            result = sql_agent(query)
            
            # Check if there's an error in the result
            if isinstance(result, dict) and "error" in result:
                return f"SQL execution failed: {result['error']}"
            
            # Store result in session state for DataFrame display
            if isinstance(result, list) and len(result) > 0:
                st.session_state.last_sql_result = result
                formatted_result = f"Database Query Results: Found {len(result)} record(s)\n"
                for i, row in enumerate(result, 1):
                    formatted_result += f"\nRecord {i}:\n"
                    for key, value in row.items():
                        formatted_result += f"  • {key}: {value}\n"
                return formatted_result
            elif isinstance(result, list) and len(result) == 0:
                st.session_state.last_sql_result = []
                return "Query executed successfully but returned no results."
            else:
                return str(result)
                
        except Exception as e:
            return f"Error in Database Query Agent: {str(e)}"

    async def _arun(self, text: str):
        return self._run(text)

# Enhanced LLM with better system prompt
os.environ["GOOGLE_API_KEY"] = Config.gemini_api_key
llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=0,
    max_tokens=512,
)

tools = [RagAgent(), SQLAgent()]

# Create agent with custom system message
system_message = """You are an intelligent assistant that helps with tariff and trade-related questions.

TOOL SELECTION RULES:
1. Use "Database_Query_Agent" for:
   - Questions with specific HTS codes (e.g., "What's the rate for HTS 0101.30.00.00?")
   - Numerical calculations or data retrieval
   - Questions asking for rates, duties, or specific values
   - Questions with keywords: "calculate", "rate", "duty", "HTS code", "CIF value"

2. Use "Document_Search_Agent" for:
   - General explanations or definitions
   - Questions about trade policies or procedures
   - Background information requests
   - Conceptual questions about tariffs

IMPORTANT: Always choose the most appropriate tool based on whether the user needs:
- Specific data/calculations → Database_Query_Agent
- General information/explanations → Document_Search_Agent

Be precise in your tool selection."""

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,  # Set to True for debugging
    return_intermediate_steps=True,
    agent_kwargs={
        "prefix": system_message
    }
)

# Show chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if isinstance(msg["content"], dict) and "output" in msg["content"]:
            with st.expander("Tool used", expanded=st.session_state.expander_mode):
                if "intermediate_steps" in msg["content"] and msg["content"]["intermediate_steps"]:
                    for step, obs in msg["content"]["intermediate_steps"]:
                        st.markdown(f"**Thought/Action:** {getattr(step, 'log', step)}\n\n**Observation:** {obs}")
            st.markdown(msg["content"]["output"])
            
            # Show DataFrame if this was a SQL query result
            if "sql_result" in msg["content"] and msg["content"]["sql_result"]:
                import pandas as pd
                if len(msg["content"]["sql_result"]) > 0:
                    df = pd.DataFrame(msg["content"]["sql_result"])
                    st.subheader("📊 Data Table View")
                    st.dataframe(df, use_container_width=True)
                    
                    # Add download button for the data
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name="query_results.csv",
                        mime="text/csv"
                    )
        else:
            st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Type your message here..."):
    # Add user input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent response
    with st.chat_message("assistant"):
        with st.spinner("Processing...", show_time=True):
            try:
                response = agent(prompt)
                with st.expander("Tool used", expanded=st.session_state.initial_expander):
                    if response.get('intermediate_steps'):
                        for step, obs in response["intermediate_steps"]:
                            st.markdown(f"**Thought/Action:** {getattr(step, 'log', step)}\n\n**Observation:** {obs}")
                        st.session_state.initial_expander = False
                    else:
                        st.write("No intermediate steps.")
                
                st.markdown(response['output'])
                
                # Check if we have SQL results to display
                if hasattr(st.session_state, 'last_sql_result') and st.session_state.last_sql_result:
                    import pandas as pd
                    if len(st.session_state.last_sql_result) > 0:
                        df = pd.DataFrame(st.session_state.last_sql_result)
                        st.subheader("📊 Data Table View")
                        st.dataframe(df, use_container_width=True)
                        
                        # Add download button for the data
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Download CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv",
                            key=f"download_{len(st.session_state.messages)}"
                        )
                        
                        # Store SQL result in the response for chat history
                        response['sql_result'] = st.session_state.last_sql_result
                        # Clear the session state
                        st.session_state.last_sql_result = None
                
                st.session_state.messages.append({"role": "assistant", "content": response})
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.session_state.messages.append({"role": "assistant", "content": f"Error: {str(e)}"})