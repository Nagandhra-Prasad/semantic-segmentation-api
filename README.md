# semantic-segmentation-api

FastAPI service for semantic segmentation.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

- API docs: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/api/v1/health

## Project layout

```
app/
├── main.py              # FastAPI app entry
├── api/v1/              # Versioned routes
│   ├── router.py
│   └── routes/
├── core/                # Config, shared settings
├── schemas/             # Pydantic models (request/response)
└── services/            # Business logic (e.g. model inference)
```