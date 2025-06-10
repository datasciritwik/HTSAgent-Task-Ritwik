from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from google import genai
from google.genai import types
from src.utils.config import Config
# from config import Config
import re

client = genai.Client(api_key=Config.gemini_api_key)
system_instruction = """Always response in the SQL query. keep the query in the code block format. Do not add any additional text.

Here is the schema of the table hts_data:
HTS Number: TEXT
Description: TEXT
General Rate of Duty Parsed (%): FLOAT
Special Rate of Duty Parsed (%): FLOAT
Column 2 Rate of Duty Parsed (%): FLOAT
CIF Value: FLOAT
Product Cost: FLOAT
Freight: FLOAT
Insurance: FLOAT
Column 2 Rate of Duty Duty Amount: FLOAT
General Rate of Duty Duty Amount: FLOAT
Special Rate of Duty Duty Amount: FLOAT
Indent: TEXT
Unit of Quantity: TEXT
Is Special Free: BOOLEAN
Special Countries: TEXT
"""

def _chroma_db():
    path = "notebooks/chroma_db_"
    embedding_model = GoogleGenerativeAIEmbeddings(google_api_key=Config.gemini_api_key, model=Config.gemini_embed_model)
    db_connection = Chroma(persist_directory=path, embedding_function=embedding_model)
    return db_connection

def _connect_duckdb():
    """Connect to the DuckDB database."""
    path="data/processed/hts_data.duckdb"
    import duckdb
    db_connection = duckdb.connect(database=path, read_only=True)
    return db_connection

def query_cleaner(query: str) -> str:
    """Clean the generated SQL query."""
    # Remove ```sql and ``` from the query
    cleaned_query = re.sub(r"```sql\s*|```", "", query, flags=re.IGNORECASE)
    
    # Remove extra whitespace and newlines
    cleaned_query = cleaned_query.strip()
    
    # Ensure the query ends with a semicolon if it doesn't already
    if not cleaned_query.endswith(';'):
        cleaned_query += ';'
    
    return cleaned_query

def generate_query(prompt: str) -> str:
    """Generate a SQL query based on the provided prompt."""
    try:
        response = client.models.generate_content(
            model=Config.gemini_model,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
            ),
            contents=prompt
        )
        
        if not response or not response.text:
            raise ValueError("No response received from the model.")
        
        # Clean the query
        cleaned_query = query_cleaner(response.text)
        
        print(f"Generated SQL Query: {cleaned_query}")
        return cleaned_query
        
    except Exception as e:
        print(f"Error generating SQL query: {str(e)}")
        raise e


# if __name__ == "__main__":
#     # Example usage
#     prompt = "Given HTS code 0101.30.00.00, a product cost of $10,000, 500 kg weight, and 5 units — what are all applicable duties?"
#     query = generate_query(prompt)
#     query = query_cleaner(query)
#     print(f"Generated SQL Query: {query}")
    
#     # Connect to DuckDB and execute the generated query
#     db_connection = _connect_duckdb()
#     try:
#         result = db_connection.execute(query).df().to_dict(orient="records")
#         print(f"Query Result: {result}")
#     except Exception as e:
#         print(f"An error occurred while executing the query: {e}")