# semantic-segmentation-api

FastAPI backend for **Deep Vision Based Semantic Segmentation for Self-Driving Cars** — aligned with the architecture: Angular client → FastAPI (file handler, JWT, JSON) → Celery AI pipeline (SegFormer) → MongoDB.

## Modules (API)

| Module | Endpoints |
|--------|-----------|
| 1 – Auth | `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET/PATCH /api/v1/users/me`, `PATCH /api/v1/users/{id}/role` (admin) |
| Admin | `GET /api/v1/admin/users`, `PATCH /api/v1/admin/users/{id}/active`, `GET /api/v1/admin/uploads` (admin only) |
| 2 – Upload | `POST /api/v1/uploads` (road image, dashcam video, traffic scene, **dataset .zip**) |
| 3 – AI engine | `POST /api/v1/processing/uploads/{id}/run` (Celery) |
| 4 – Segmentation | `GET /api/v1/segmentation/legend`, `GET /api/v1/segmentation/dashboard/{job_id}` |
| 5 – Dashboard data | Same as segmentation + file URLs under `/api/v1/files/results/...` |
| 6 – Analytics | `GET /api/v1/analytics/summary`, `GET /api/v1/analytics/jobs/{job_id}` |
| 7 – Reports | `POST /api/v1/reports/jobs/{job_id}`, download PDF/Excel |
| 8 – History | `GET /api/v1/history/uploads`, `jobs`, `reports`, `activity` |

Dataset helper: `GET /api/v1/dataset/cityscapes/samples`

## Stack

- **FastAPI** – REST API / controllers (`app/api/v1/routes/`)
- **MongoDB** + Beanie – users, uploads, jobs, reports, activity
- **Celery** + **Redis** – async SegFormer inference
- **SegFormer** (`nvidia/segformer-b0-finetuned-cityscapes-1024-1024`) – free Hugging Face weights
- **OpenCV** – video frame extraction
- **ReportLab / openpyxl** – PDF & Excel reports

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Start infrastructure (local Mac). If **another project already uses Mongo on 27017** (e.g. `brew services start mongodb-community`), run **this** API’s Mongo on **27018** only:

```bash
chmod +x scripts/start-mongodb.sh scripts/stop-mongodb.sh
./scripts/start-mongodb.sh          # mongodb://localhost:27018 (uses brew’s mongod, separate data/)
brew services start redis
```

Keep `MONGODB_URI=mongodb://localhost:27018` in `.env`. Do **not** point this app at 27017 unless that instance is only for this project.

MongoDB Compass for **this** project: `mongodb://localhost:27018` → database `semantic_segmentation`.

Optional Docker instead: `docker compose up -d redis` (Compose Mongo also maps to host `27018`).

Run API:

```bash
uvicorn app.main:app --reload
```

Run Celery worker (separate terminal):

```bash
./scripts/run_celery_worker.sh
# or: celery -A app.core.celery_app worker --loglevel=info --pool=solo
```

## Frontend (Angular)

```bash
cd ../semantic-segmentation-web
npm start
```

UI at http://localhost:4200 (proxies `/api` → FastAPI). Lite purple theme: login hero, upload, viewer, analytics, reports, history.

Or everything via Docker:

```bash
docker compose up --build
```

## Flow (matches system diagram)

1. User registers / logs in (JWT).
2. Upload image or dashcam video → validated and stored under `storage/uploads/`.
3. `POST .../processing/uploads/{id}/run` enqueues Celery task.
4. Worker: preprocess → SegFormer inference → colour mask & overlay → save under `storage/results/{job_id}/`.
5. MongoDB stores job metrics, class counts, paths.
6. Dashboard/history/analytics endpoints serve JSON for Angular.
7. Generate PDF/Excel report from completed job.

## Cityscapes

See [data/cityscapes/README.md](data/cityscapes/README.md). Point `CITYSCAPES_DATA_ROOT` in `.env` at your dataset root.

## Login (OAuth2 form)

Use `username` = email and `password` in `/api/v1/auth/login` (Swagger **Authorize** uses the same).

### Default admin (dev)

On startup the API ensures an admin user from `.env` (`ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_FULL_NAME`). Defaults:

- Email: `admin@segvision.dev`
- Password: ` `

Admins see **Admin** in the Angular sidebar: list all users (activate/deactivate), all uploads, and open any segmentation viewer. Deactivated users cannot log in or use existing tokens.

## Project layout

```
app/
  api/v1/routes/     # Controllers (REST)
  core/              # Config, JWT, DB, Celery
  db/models/         # MongoDB documents
  ml/                # Preprocess, SegFormer, post-process, colours
  schemas/           # Pydantic DTOs
  services/          # Business logic
  workers/           # Celery tasks
storage/             # uploads, results, reports
```
