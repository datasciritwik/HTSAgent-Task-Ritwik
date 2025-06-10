
# HTS AI Agent – Ritwik Singh

🚀 **Submission for HTS AI Agent Task (Personaliz.ai)**  
📧 Contact: [officialritwik098@gmail.com](mailto:officialritwik098@gmail.com)  
👤 Author: Ritwik Singh  
📽️ Demo Video: [Watch Demo](http://youtube.com/watch?v=gg9iyODIn-E&feature=youtu.be)
---

## 📚 Overview

The **HTS AI Agent** is a dual-function intelligent assistant designed to:

1. 🧠 **Answer trade policy and agreement-related queries** using RAG (Retrieval-Augmented Generation) on HTS General Notes documentation.
2. 💸 **Compute duties and landed cost** based on HTS code and CIF (Cost + Insurance + Freight) details using DuckDB and HTS tariff CSVs.

The agent leverages:
- **ChromaDB** + **GoogleGenerativeAIEmbeddings** for RAG
- **DuckDB** for HTS data storage and duty computation
- **LangChain MultiTool Agent** for smart routing between tools
- **Streamlit** for the frontend UI

---

## ⚙️ Architecture

```mermaid
graph TD
User["🧑 User (NL Query via Streamlit)"]
Preprocessor["🔍 Query Router"]
RAGAgent["📚 RAG Agent (Chroma + Gemini)"]
SQLAgent["🧾 SQL Agent (DuckDB + Duty Calculator)"]
ResponseFormatter["🖼 Markdown Output"]
CSVExporter["⬇️ Downloadable CSV (landed_cost_duties.csv)"]

User --> Preprocessor
Preprocessor --> RAGAgent
Preprocessor --> SQLAgent
RAGAgent --> ResponseFormatter
SQLAgent --> ResponseFormatter
ResponseFormatter --> CSVExporter
````

---

## 🛠 Features

### 🔹 RAG Agent (LangChain)

* Loads and chunks *General Notes Full Documentation* (PDF)
* Embeds using `GoogleGenerativeAIEmbeddings`
* Stores vectors in **ChromaDB**
* Performs semantic search for trade-related questions

### 🔹 HTS Tariff Calculator Agent

* Loads **Section I CSV** into DuckDB
* Accepts HTS code + product cost, weight, quantity
* Parses duty strings (% / ¢ per kg / \$ per unit)
* Computes all applicable duty amounts and total landed cost
* Returns breakdown in Markdown and CSV format

### 🔹 Unified Agent (LangChain MultiTool)

* Dynamically chooses between RAG and SQL tools
* Supports **multi-tool queries in one prompt**
* Markdown-rich answers with data tables
* Exportable CSV of calculated duties

---

## 🧪 Sample Queries Demonstrated

### ✅ RAG Examples

* What is the United States-Israel Free Trade Agreement?
* Can a product that exceeds its tariff-rate quota still qualify for duty-free entry under GSP or any FTA?
* How is classification determined for an imported item that will be used as a part in manufacturing but isn’t itself a finished part?

### ✅ Tariff Examples

* HTS Code: `0101.30.00.00`, Cost: `$10,000`, Weight: `500kg`, Units: `5`
* What’s the HTS code for donkeys?
* What are the applicable duty rates for female cattle?

---

## 🏗️ Tech Stack

| Component       | Technology                             |
| --------------- | -------------------------------------- |
| Embeddings      | GoogleGenerativeAIEmbeddings           |
| Vector DB       | ChromaDB                               |
| DB Engine       | DuckDB                                 |
| RAG             | LangChain ConversationalRetrievalChain |
| Frontend        | Streamlit                              |
| Package Manager | `uv`                                   |
| Language        | Python 3.11                            |


---

## 💡 How to Run

1. **Install Dependencies (via `uv`):**

   ```bash
   uv pip install -r requirements.txt
   ```

2. **Run the Streamlit App:**

   ```bash
    streamlit run .\src\frontend\app.py
   ```

3. **Interact:**

   * Enter a trade policy question or HTS-based duty calculation request.
   * View the Markdown output and download CSV (if applicable).

---

## 📦 Deliverables

* ✅ GitHub Repository (Codebase)
* ✅ Demo Video (RAG + SQL Agent in action)
* ✅ [This README](#)
* ✅ Resume of Ritwik Singh

---

## 🙌 Acknowledgements

Thanks to **Personaliz.ai** for this unique opportunity to blend AI, data extraction, and international trade policy into one intelligent assistant.

---
