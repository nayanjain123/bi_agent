# Conversational Business Intelligence Agent

This is a PoC for AI-powered conversational business intelligence assistant that converts natural language into SQL queries, executes them on structured datasets, and generates insights with visualizations.

Built using **LangChain**, **LangGraph**, **Streamlit**, **SQLite**, and **Gemini APIs**.

---

## Features

- Natural Language → SQL Query Generation
- Conversational Analytics Workflow
- Multi-Domain Query Routing
- Read-Only SQL Validation Layer
- Interactive Dashboard with Streamlit
- Automated Insight Summarization
- Automated Chart Selection
- In-Memory SQLite Analytics Engine
- Gemini API Integration
- LangGraph-Based Agent Pipeline

---

## Architecture

```text
User Query
   ↓
Question Rewriter
   ↓
Domain Router
   ↓
SQL Generator
   ↓
SQL Safety Validator
   ↓
SQLite Execution Engine
   ↓
Insight Summarizer
   ↓
Visualization Generator
```

---

## Supported Domains

### Sales Analytics

- Revenue Analysis
- Product Performance Tracking
- Inventory Monitoring
- Channel-wise Sales Trends
- Regional Business Insights

### Support Analytics

- Ticket Resolution Analysis
- Priority Distribution
- Customer Issue Tracking
- SLA Monitoring
- Support Workload Insights

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core Backend |
| LangChain | LLM Orchestration |
| LangGraph | Agent Workflow Pipeline |
| Streamlit | Interactive Dashboard |
| SQLite | Analytics Database |
| Plotly | Data Visualization |
| Gemini API | LLM Inference |
| Pandas | Data Processing |

---

## Project Structure

```text
ai-analytics-copilot/
│
├── data/
│   ├── customers.csv
│   ├── orders.csv
│   ├── products.csv
│   └── support_tickets.csv
│
├── agent.py
├── app.py
├── config.py
├── dataset.py
├── sql_safety.py
├── visualization.py
├── main.py
│
├── .env
├── requirements.txt
└── README.md
```

---

## Sample Queries

### Sales

- What is revenue by region?
- Which products generated the most revenue?
- Show monthly revenue trends by sales channel.
- Which products are below reorder threshold?

### Support

- How many open tickets exist by priority?
- What is the average resolution time by category?
- Which customer segments generate the most urgent tickets?
- Show support ticket distribution by status.

---

## Screenshots

### Dashboard

_Add dashboard screenshot here_

```markdown
![Dashboard](assets/dashboard.png)
```

### SQL Generation

_Add SQL generation screenshot here_

```markdown
![SQL Generation](assets/sql_generation.png)
```

### Visualizations

_Add charts screenshot here_

```markdown
![Visualizations](assets/charts.png)
```

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone https://github.com/your-username/ai-analytics-copilot.git
cd ai-analytics-copilot
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

Activate the environment:

#### Windows

```bash
.\.venv\Scripts\Activate.ps1
```

#### Linux / Mac

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file:

```env
GOOGLE_API_KEY=your_gemini_api_key
MODEL_NAME=gemini-1.5-flash
```

### 5. Run Application

```bash
streamlit run app.py
```

---

## Example Workflow

1. User enters a business question
2. Agent rewrites the query into standalone form
3. Query is routed to the appropriate business domain
4. LLM generates SQL Queries
5. SQL validator enforces read-only constraints
6. SQLite executes the query
7. AI summarizes analytical insights
8. Dashboard renders tabular and graphical output

---

## Key Highlights

- Modular AI-agent architecture
- Modular workflow orchestration
- Secure SQL validation pipeline
- Lightweight local analytics engine
- Real-time conversational BI experience

---

## Future Enhancements

- PostgreSQL / MySQL connectors
- Authentication & RBAC
- Vector search integration
- Multi-agent collaboration
- Real-time streaming analytics
- Cloud deployment support
- Dashboard export functionality

---

## Author

**Nayan Jain**