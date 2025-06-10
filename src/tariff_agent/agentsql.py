import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.utils.raghelper import _connect_duckdb
import json

def sql_agent(query: str):
    """Run the SQL agent with the given query and return results as a list of dicts."""
    try:
        # Connect to the DuckDB database
        db_connection = _connect_duckdb()
        
        # Clean the query (remove any extra whitespace/newlines)
        query = query.strip()
        
        # Execute the query and fetch results
        result_df = db_connection.execute(query).df()
        
        # Convert to list of dictionaries
        result = result_df.to_dict(orient="records")
        
        # print(f"SQL Query executed successfully: {query}")
        # print(f"Number of rows returned: {len(result)}")
        
        # Close the connection
        db_connection.close()
        
        return result  # returns a list of dicts
    except Exception as e:
        error_msg = f"An error occurred while executing the query: {str(e)}"
        # print(error_msg)
        return {"error": error_msg}