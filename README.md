# AI Lead Qualification Agent

When a lead comes in from a form, this agent scores and qualifies them using an LLM, then writes a personalized follow-up email. The result is fed to n8n which handles automated email sending and lead nurturing.

---

## Architecture

```
Tally Form → n8n Webhook → POST /leads → [background: LLM scores + writes email]
                                 ↓
n8n polls → GET /leads/{id} → status: scored → n8n sends email via Gmail
```

---

## Tech Stack

- **FastAPI** — async REST API
- **LangChain + Groq (Llama 3.3 70B)** — lead scoring and email generation
- **PostgreSQL** — lead persistence
- **Redis** — rate limiting
- **n8n** — webhook orchestration, email sending
- **Docker** — local infrastructure
- **LangSmith** — LLM call tracing

---

## Setup

```bash
git clone https://github.com/deepak-aibuilds/lead_qualification_agent
cd lead_qualification_agent

cp .env.example .env
# fill in: GROQ_API_KEY, DATABASE_URL, REDIS_URL, LANGCHAIN_API_KEY

uv sync
docker compose up -d
alembic upgrade head

uv run uvicorn app.main:app --reload
# Optional: run the demo UI
uv pip install streamlit
streamlit run demo.py
```

---

## API

### POST /leads
Accepts a lead, saves to DB, runs qualification in background.

```bash
curl -X POST http://localhost:8000/leads \
  -F "name=John Doe" \
  -F "email=john@acme.com" \
  -F "company=Acme Inc" \
  -F "required_service=AI Chatbot" \
  -F "budget=5000"
```

Response:
```json
{ "id": 1, "status": "pending" }
```

### GET /leads/{id}
Poll for qualification result.

Response:
```json
{
  "id": 1,
  "status": "scored",
  "lead_score": 75,
  "lead_qualification": "qualified",
  "email_subject": "Following up on your AI Chatbot inquiry",
  "email_body": "Hi John..."
}
```

---

## Tests

```bash
pytest tests/test_leads.py -v
```

---

## License

MIT