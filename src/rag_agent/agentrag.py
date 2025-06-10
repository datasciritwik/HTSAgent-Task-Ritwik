import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.utils.config import Config
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI

from src.utils.raghelper import _chroma_db

chat_model = ChatGoogleGenerativeAI(google_api_key=Config.gemini_api_key, 
                                   model=Config.gemini_model,)
db_connection = _chroma_db()
retriever = db_connection.as_retriever(search_kwargs={"k": 5})
chat_template = ChatPromptTemplate.from_messages([
    # System Message Prompt Template
    SystemMessage(content="""You are TariffBot — an intelligent assistant trained on U.S. International Trade Commission data. You exist to help importers, analysts, and trade professionals quickly understand tariff rules, duty rates, and policy agreements. You always provide clear, compliant, and factual answers grounded in official HTS documentation.
                  
    - When given an HTS code and product information, you explain all applicable duties and cost components.
    - When asked about trade agreements (e.g., NAFTA, Israel FTA), you reference the relevant General Notes with citations.
    - If a query is ambiguous or unsupported, you politely defer or recommend reviewing the relevant HTS section manually.
    - You do not speculate or make policy interpretations — you clarify with precision and data."""),
    # Human Message Prompt Template
    HumanMessagePromptTemplate.from_template("""Answer the question based on the given context.
    Context: {context}
    Question: {question}
    Answer: """)
])
output_parser = StrOutputParser()

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | chat_template
    | chat_model
    | output_parser
)

def rag_agent(question: str):
    """Run the RAG agent with the given question."""
    # Run the rag_chain with the question
    response = rag_chain.invoke(question)
    return response