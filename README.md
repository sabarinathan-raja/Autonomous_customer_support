# Autonomous Customer Support and Escalation System

An AI-powered multi-agent customer support application built using Python, Streamlit, Gemini API, and SQLite. The system analyzes customer queries, retrieves relevant support policies, checks order information, generates responses, validates compliance, and escalates complex cases for human review.

## 🚀 Project Overview

Traditional customer support systems often require manual intervention to understand customer issues, verify policies, and provide resolutions.

This project demonstrates an autonomous multi-agent workflow that coordinates specialized AI agents to handle customer support requests efficiently while maintaining policy compliance and human oversight.

## ✨ Key Features

- **Multi-Agent Architecture:** Multiple specialized agents collaborate to process customer requests.
- **Intake Agent:** Understands and classifies incoming customer queries.
- **Policy Agent:** Retrieves relevant support policies.
- **Order Agent:** Checks order information using a mock order API.
- **Resolution Agent:** Generates contextual customer responses using Google Gemini.
- **Compliance Agent:** Validates responses against support policies.
- **Escalation Agent:** Identifies cases that require human intervention.
- **Ticket Management:** Stores customer support interactions using SQLite.
- **Agent Execution Trace:** Records agent execution status and processing time.
- **Human Review Queue:** Displays cases requiring manual review.
- **Streamlit Dashboard:** Provides an interactive customer support interface.

## 🏗️ System Architecture

```text
             Customer Query
                    |
                    v
              Intake Agent
                    |
                    v
              Policy Agent
                    |
                    v
               Order Agent
                    |
                    v
             Resolution Agent
                    |
                    v
             Gemini API (LLM)
                    |
                    v
             Compliance Agent
                    |
                    v
             Escalation Agent
                    |
             +------+------+
             |             |
             v             v
        Auto Response   Human Review
             |             |
             +------+------+
                    |
                    v
              SQLite Database
                    |
                    v
             Streamlit Dashboard
```

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| LLM | Google Gemini API |
| Database | SQLite |
| Data Validation | Pydantic |
| Configuration | Python-dotenv |
| Containerization | Docker |
| Version Control | Git & GitHub |

## 📂 Project Structure

```text
Autonomous_customer_support/
│
├── app/
│   ├── agents/
│   │   ├── intake_agent.py
│   │   ├── policy_agent.py
│   │   ├── order_agent.py
│   │   ├── resolution_agent.py
│   │   ├── compliance_agent.py
│   │   └── escalation_agent.py
│   │
│   ├── tools/
│   │   ├── gemini_client.py
│   │   ├── mock_order_api.py
│   │   ├── policy_search.py
│   │   └── ticket_database.py
│   │
│   ├── workflow/
│   │   └── orchestrator.py
│   │
│   ├── main.py
│   ├── config.py
│   └── schemas.py
│
├── data/
│   └── mock_orders.json
│
├── knowledge_base/
│   └── support_policies.json
│
├── tests/
│   └── test_basic.py
│
├── Dockerfile
├── .dockerignore
├── .gitignore
├── requirements.txt
├── README.md
└── .env.example
```

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/autonomous-customer-support.git
cd autonomous-customer-support
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash
```

Replace the placeholder with your own Gemini API key. Never upload `.env` to GitHub.

### 5. Run the Application

```bash
python -m streamlit run app/main.py
```

Open the application at:

`http://localhost:8501`

## 🐳 Run with Docker

### Build Docker Image

```bash
docker build -t autonomous-customer-support .
```

### Run Docker Container

```bash
docker run -d --name customer-support-app -p 8501:8501 --env-file .env -v "${PWD}\data:/app/data" autonomous-customer-support
```

Open:

`http://localhost:8501`

## 🧪 Run Tests

```bash
pytest -v
```

## 🔄 Workflow

1. Customer submits a support request.
2. Intake Agent analyzes the request.
3. Policy Agent retrieves applicable support policies.
4. Order Agent verifies order information when an order ID is provided.
5. Resolution Agent generates a contextual response using Gemini.
6. Compliance Agent checks the response.
7. Escalation Agent determines whether human review is required.
8. Ticket details and execution information are stored in SQLite.
9. The Streamlit dashboard displays the result.

## 🔐 Human-in-the-Loop

The system does not automatically approve sensitive refund or cancellation requests. Cases requiring additional authorization or review can be escalated to a human support representative.

## 🎯 Use Cases

- Delayed delivery inquiries
- Order status verification
- Refund policy questions
- Cancellation requests
- Customer complaint handling
- Human escalation management

## 🔮 Future Enhancements

- Real e-commerce API integration
- Authentication and role-based access
- Advanced agent monitoring
- Production database integration
- Cloud deployment
- Advanced evaluation and analytics

## 👨‍💻 Author

**Sabarinathan A**

Electronics and Communication Engineering Graduate | Generative AI | Agentic AI | Python

## 📄 License

This project is developed for educational and portfolio demonstration purposes.