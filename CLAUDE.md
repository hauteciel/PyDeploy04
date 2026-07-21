# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

Two independent apps in one repo, not sharing a package manager or root config:

- `backend/` — FastAPI + SQLAlchemy 2.0 + MySQL (via PyMySQL) file-upload API
- `frontend/` — React 19 + Vite app; the file-upload feature lives in `src/191_FileUpload/` as a self-contained module (lesson-numbered folder convention — expect more `NNN_Feature/` folders to appear over time)

There is no test suite in either project (no test files, no test script in `package.json`) — don't assume one exists.

## Commands

### Backend (run from `backend/`)
```
python -m venv venv && venv\Scripts\activate   # or use one of the repo's activate_*.bat scripts
pip install -r requirements.txt
copy .env.example .env    # then fill in real DB credentials
python main.py             # runs uvicorn with reload, binds 127.0.0.1:8000 in dev
```
Requires a running MySQL server matching `DB_*` in `.env` — `database.Base.metadata.create_all()` runs at import time in `main.py` and will fail to connect otherwise.

### Frontend (run from `frontend/`)
```
npm install
npm run dev        # Vite dev server, default port 5173
npm run build       # production build -> dist/
npm run lint        # ESLint (flat config, eslint.config.js)
npm run preview     # serve the production build locally
```

## Architecture

### Backend request flow
`main.py` (app init, CORS, uvicorn entrypoint) → `controllers.py` (`APIRouter(prefix="/api/files")`: upload/list/download/view endpoints) → `models.py` (single `UploadedFile` ORM model / table `uploaded_files`) → `schemas.py` (Pydantic response model) → `database.py` (engine/session, `get_db()` dependency).

### Environment-driven config (`backend/.env`, template in `backend/.env.example`)
All of the following are read via `python-dotenv` and change behavior between dev and prod without code changes:
- `ENVIRONMENT` (`development`|`production`) — toggles SQL echo logging (`database.py`) and uvicorn `host`/`reload` (`main.py`: `127.0.0.1`+reload in dev, `0.0.0.0` no-reload in prod, expecting Nginx in front)
- `ALLOWED_ORIGINS` — comma-separated CORS origins, parsed in `main.py`
- `DB_USER`/`DB_PASSWORD`/`DB_HOST`/`DB_PORT`/`DB_NAME` — build `DATABASE_URL` in `database.py` (local MySQL in dev, RDS endpoint in prod)
- `STORAGE_BACKEND` (`local`|`s3`), `AWS_REGION`, `AWS_S3_BUCKET` — see storage abstraction below

### Storage abstraction (`storage.py`)
`controllers.py` never touches the filesystem or S3 directly — it calls `storage.save_file()`, `storage.file_exists()`, `storage.get_local_path()`, `storage.get_presigned_url()`. Behavior switches on `STORAGE_BACKEND`:
- `local` (dev default): files live under `{repo root}/upload/`; download/view endpoints return `FileResponse`
- `s3` (prod): files go to `AWS_S3_BUCKET` via `boto3`; download/view endpoints return a `RedirectResponse` to a presigned URL instead of streaming through the server

`MAX_FILE_SIZE` (2MB) is enforced in `controllers.py` before either backend is touched. Uploaded filenames are UUID-renamed to avoid collisions; `original_name` is preserved in the DB for download.

### Frontend API wiring
`src/191_FileUpload/api.js` creates the shared axios instance with `baseURL: import.meta.env.VITE_API_BASE_URL`, sourced from `frontend/.env.development` / `frontend/.env.production` (Vite's mode-based env file convention — `.env.production` must be updated with the real deployed API domain before building for prod). Download and image-view links in `App191.jsx` are built by string-concatenating `api.defaults.baseURL` directly (`${api.defaults.baseURL}/download/${id}`) rather than via axios calls, since the browser needs to navigate straight to the file.

Note: `src/App.jsx` is still the default Vite scaffold — it does not mount `App191`, so the file-upload feature isn't currently wired into the app entrypoint.

### Deployment
`배포전략.md` (Korean) documents the recommended AWS architecture: React static build on S3+CloudFront, FastAPI on EC2 (Nginx reverse-proxying Gunicorn/Uvicorn workers), MySQL on RDS, uploaded files in S3 — matching the `STORAGE_BACKEND=s3` path above. It also covers separate dev/prod resource sizing and a step-by-step provisioning order (network/security groups → RDS → S3 → EC2 backend → S3+CloudFront frontend → CI/CD).
