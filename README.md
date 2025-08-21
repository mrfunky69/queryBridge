# QueryBridge  

A **GenAI-powered unified query platform** that enables users to ask questions in plain English and get answers across multiple databases — without writing SQL or worrying about where the data lives.  

---

## 📖 Project Overview  

Business data often lives in **different systems** (ERP, cloud warehouses, spreadsheets), making insights slow and error-prone.  

**QueryBridge** solves this by:  

- Dynamically routing natural language queries to the correct data source  
- Auto-generating SQL and fetching results  
- Performing lightweight post-processing  
- Returning both structured data and **smart visualizations**  

👉 For this prototype, we integrated **SAP HANA**, **Google BigQuery**, and **Excel/CSV files** as the demo databases.  
⚠️ To run the project locally, you’ll need to connect to at least one of these demo data sources.  

---

## 🛠️ Tech Stack  

- **Python** – core backend logic  
- **DuckDB** – local query engine for Excel/CSV  
- **Google BigQuery Python SDK** – access to BigQuery  
- **SAP HANA DBAPI** – integration with enterprise HANA DB  
- **Pandas** – in-memory data processing  
- **Matplotlib / Plotly** – visualization  
- **LangGraph** – orchestration of LLM reasoning steps  
- **Streamlit** – user interface  

---

## ✨ Key Features  

- ✅ Single query interface across multiple databases  
- ✅ No SQL knowledge required  
- ✅ Dynamic routing + auto SQL generation  
- ✅ Post-query insights & suggested charts  
- ✅ Lightweight, portable, and extensible (Snowflake, APIs, etc.)  

---

## 🚀 Running the Project  

1. **Clone this repo**  
   ```bash
   git clone https://github.com/<your-username>/querybridge.git
   cd querybridge

2. **Create a virtual environment, install dependencies, and connect to a demo DB**
   ```bash
  Copy
  Edit
  python -m venv env
  source env/bin/activate   # On Windows: env\Scripts\activate
  pip install -r requirements.txt
  # ⚠️ Update the config to connect to a demo database 
# (SAP HANA, BigQuery, or Excel file)

3. **Run the Streamlit app**

```bash
Copy
Edit
streamlit run app.py
