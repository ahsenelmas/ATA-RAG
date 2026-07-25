# ATA RAG University Assistant

ATA RAG is a multilingual university information assistant built for Akademia Techniczno-Artystyczna. The system retrieves relevant content from official ATA University sources and generates source-grounded answers about programmes, admissions, tuition fees, scholarships and university services.

## Project Overview

The project combines:

- Web scraping of official ATA University pages
- Document chunking and embedding generation
- Semantic search over indexed university content
- Retrieval-Augmented Generation
- FastAPI backend services
- Next.js frontend
- Live dashboard statistics
- User feedback collection
- Automated RAG evaluation

## Main Features

### University Chat Assistant

The assistant can:

- Answer questions about ATA University
- Respond in English and Polish
- Detect unsupported or out-of-scope questions
- Return grounded or not-grounded status
- Display the sources used for each answer
- Show source relevance scores
- Preserve the conversation session
- Handle backend connection errors
- Retry failed requests
- Clear the conversation with New Chat

### Feedback System

Users can rate assistant responses as:

- Helpful
- Not helpful

Feedback is stored in the backend and displayed on the dashboard.

### Live Dashboard

The dashboard displays live backend data, including:

- Total documents
- Total chunks
- Embedded chunks
- Total chat messages
- Grounded message count
- Grounded answer rate
- Average response latency
- Total feedback
- Helpful feedback
- Not helpful feedback
- Positive feedback rate
- Recent questions
- Latest feedback
- Scraper and crawl statistics

## Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Alembic
- Pydantic
- Sentence Transformers
- Hugging Face
- LangChain
- Uvicorn

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS

### Infrastructure

- Docker
- Docker Compose
- GitHub
- Coolify
- PostgreSQL-compatible cloud database

## Project Structure

```text
ATA-RAG
├── backend
│   ├── alembic
│   ├── app
│   │   ├── api
│   │   ├── core
│   │   ├── db
│   │   ├── models
│   │   ├── schemas
│   │   └── services
│   ├── scripts
│   ├── tests
│   ├── .env
│   ├── alembic.ini
│   └── requirements.txt
├── evaluation
├── frontend
│   ├── app
│   │   ├── chat
│   │   ├── dashboard
│   │   └── page.tsx
│   ├── lib
│   ├── public
│   ├── .env.local
│   └── package.json
├── .env.example
├── docker-compose.yml
└── README.md
```

## Environment Configuration

Create the backend environment file:

```text
backend/.env
```

Required values include:

```env
APP_NAME=ATA RAG
APP_ENV=development
DEBUG=true

DATABASE_URL=your_database_connection

BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000

LLM_BASE_URL=your_llm_base_url
LLM_API_KEY=your_llm_api_key
LLM_MODEL=your_llm_model

LANGCHAIN_TRACING_V2=false
LANGCHAIN_TRACING=false
LANGSMITH_TRACING=false
```

Never commit API keys, database passwords or private connection strings.

Create the frontend environment file:

```text
frontend/.env.local
```

Add:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

## Backend Setup

Open a terminal in the backend directory:

```powershell
cd backend
```

Create a virtual environment:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```powershell
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

Run the backend:

```powershell
py -m uvicorn app.main:app --reload
```

The backend will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

Open a new terminal:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Run the frontend:

```powershell
npm run dev
```

The frontend will be available at:

```text
http://localhost:3000
```

## Main Frontend Pages

### Home

```text
http://localhost:3000
```

Includes:

- Project introduction
- Feature overview
- Suggested university questions
- Chat preview
- Navigation to the assistant and dashboard

### Chat

```text
http://localhost:3000/chat
```

Includes:

- Real backend API connection
- Suggested questions
- Grounded and not-grounded status
- Source cards
- Relevance scores
- Helpful and not-helpful buttons
- Retry handling
- New Chat functionality
- Mobile responsive layout

### Dashboard

```text
http://localhost:3000/dashboard
```

Includes:

- Live database statistics
- Grounded answer rate
- Average latency
- Feedback statistics
- Recent questions
- Latest feedback
- Crawl status
- Manual refresh button

## Main API Endpoints

### Chat

```http
POST /api/chat
```

Example request:

```json
{
  "question": "What are the admission requirements?",
  "language": "en",
  "retrieval_limit": 5,
  "session_id": null
}
```

### Feedback

```http
POST /api/feedback
```

Example request:

```json
{
  "message_id": "assistant-message-uuid",
  "rating": "helpful",
  "comment": null
}
```

Accepted ratings:

```text
helpful
not_helpful
```

### Dashboard

```http
GET /api/dashboard/statistics
GET /api/dashboard/recent-chats
GET /api/dashboard/feedback
GET /api/dashboard/crawls
```

### Health

```http
GET /api/health
GET /api/health/database
```

## Functional Tests Completed

The following scenarios were manually tested:

- English university question
- Polish university question
- Automatic language detection
- Unsupported weather question
- Grounded answer display
- Not-grounded answer display
- Source link opening
- New Chat reset
- Backend connection failure
- Retry after backend restart
- Helpful feedback submission
- Dashboard feedback refresh
- Mobile home page
- Mobile chat page
- Mobile dashboard page

## Known Limitations

- The scraper history may display `No crawl recorded` if no crawl run has been stored in the database.
- Hugging Face may display an unauthenticated request warning when no `HF_TOKEN` is configured.
- LangSmith tracing should remain disabled unless a valid LangSmith API key is provided.
- Answer quality depends on the retrieved ATA content.
- Important university information should still be verified using the displayed official source links.

## Team Responsibilities

### Ahsen

- Backend architecture
- FastAPI API development
- RAG pipeline
- Embedding and retrieval services
- Database integration
- Evaluation system
- Backend deployment configuration

### Selma

- Frontend architecture
- Next.js interface
- Home page design
- Chat interface
- Backend chat integration
- Source display
- Feedback interface
- Dashboard integration
- Responsive mobile testing
- Frontend functional testing

## Development Branch

Frontend work was developed on:

```text
selma/frontend-ui
```

## Security Notes

Do not commit:

```text
backend/.env
frontend/.env.local
API keys
Database passwords
Private connection strings
```

Confirm that environment files are included in `.gitignore` before pushing changes.

## Status

Current project status:

- Backend running locally
- Frontend running locally
- Chat connected to the backend
- Dashboard connected to live backend data
- Feedback system working
- Mobile responsive tests completed
- Functional tests completed
- Ready for final review, commit, push and deployment