# AI Lead Qualification Agent

Automate lead qualification and personalized follow-up email generation using LLMs.

This project receives inbound lead form submissions, scores and classifies leads using an AI-powered qualification workflow, generates a personalized follow-up email, and stores the results in PostgreSQL.

---

## Features

* AI-powered lead scoring
* Lead classification:

  * Qualified
  * Nurture
  * Disqualified
* Personalized follow-up email generation
* PostgreSQL persistence
* Redis-backed rate limiting
* Structured JSON logging
* Async FastAPI architecture
* Alembic database migrations
* Docker support

---

## Architecture

```text
Lead Form Submission
         │
         ▼
 FastAPI Endpoint
         │
         ▼
 Lead Qualification LLM
         │
         ├── Score Lead
         ├── Classify Lead
         └── Recommend Action
         │
         ▼
 Email Generation LLM
         │
         ▼
 PostgreSQL Storage
         │
         ▼
 API Response
```

---

## Tech Stack

### Backend

* FastAPI
* Python 3.13
* SQLAlchemy 2.0
* Alembic

### AI

* LangChain
* Groq
* Llama 3.3 70B

### Infrastructure

* PostgreSQL
* Redis
* Docker
* UV

---

## Project Structure

```text
app/
├── core/
│   ├── config.py
│   └── logger.py
│
├── db/
│   └── db.py
│
├── llm/
│   ├── client.py
│   └── prompts/
│       ├── qualify_v1.txt
│       └── email_v1.txt
│
├── models/
│   └── lead.py
│
├── main.py
│
alembic/
docker-compose.yml
Dockerfile
```

---

## Lead Qualification Flow

When a lead submits the form:

### Input

```json
{
  "name": "John Doe",
  "company": "Acme Inc",
  "email": "john@acme.com",
  "required_service": "AI Chatbot Development",
  "budget": 5000
}
```

### AI Qualification

The qualification agent evaluates:

* Budget quality
* Service fit
* Business credibility
* Sales priority

### Classification

| Score  | Classification |
| ------ | -------------- |
| 0-39   | Disqualified   |
| 40-69  | Nurture        |
| 70-100 | Qualified      |

### Recommended Actions

* Reject
* Send Automated Follow-up
* Book Discovery Call
* Immediate Founder Outreach

### Email Generation

A second LLM generates a personalized follow-up email tailored to:

* Company
* Requested service
* Lead score
* Qualification stage

---

## Environment Variables

Create a `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://postgres:pass@localhost:5432/leadqualifier

GROQ_API_KEY=your_groq_api_key

MISTRAL_API_KEY=

REDIS_URL=redis://localhost:6379

SECRET_KEY=change_me

DEBUG=false
```

---

## Local Development

### 1. Clone Repository

```bash
git clone <repo-url>
cd lead_qualification_agent
```

### 2. Install Dependencies

```bash
uv sync
```

### 3. Start Infrastructure

```bash
docker compose up -d
```

This starts:

* PostgreSQL
* Redis

### 4. Run Database Migrations

```bash
alembic upgrade head
```

### 5. Start API

```bash
uv run uvicorn app.main:app --reload
```

API will be available at:

```text
http://localhost:8000
```

---

## API Endpoints

### Health Check

```http
GET /health
```

Response:

```json
{
  "status": "healthy"
}
```

---

### Create Lead

```http
POST /leads
```

Content-Type:

```text
multipart/form-data
```

Fields:

| Field            | Type   |
| ---------------- | ------ |
| name             | string |
| email            | string |
| company          | string |
| required_service | string |
| budget           | string |

Example:

```bash
curl -X POST http://localhost:8000/leads \
  -F "name=John Doe" \
  -F "email=john@acme.com" \
  -F "company=Acme Inc" \
  -F "required_service=AI Chatbot Development" \
  -F "budget=5000"
```

Response:

```json
{
  "email": "Generated follow-up email..."
}
```

---

## Rate Limiting

The API uses Redis-backed rate limiting.

Current configuration:

```python
RateLimiter(
    times=5,
    seconds=60
)
```

Limits:

```text
5 requests / minute
```

per client.

---

## Database Schema

### leads

| Column         | Type     |
| -------------- | -------- |
| id             | Integer  |
| name           | String   |
| company_name   | String   |
| budget         | String   |
| problem        | Text     |
| score          | Integer  |
| classification | String   |
| email_draft    | Text     |
| status         | String   |
| created_at     | DateTime |
| updated_at     | DateTime |

---

## Future Improvements

* LangGraph multi-agent workflow
* CRM integrations (HubSpot, Salesforce)
* Human review queue
* Email sending automation
* Lead enrichment
* Admin dashboard
* Webhook support
* Authentication & RBAC
* Queue workers (Celery / Dramatiq)

---

## License

MIT
