# KineticKPI

KineticKPI turns operational datasets into KPIs, anomaly signals, explanations, and reports. NovaCommerce is the demonstration company; the ingestion API is designed to accept data from other companies using the same documented dataset shapes.

## Day 1: setup and data ingestion

The first slice provides a FastAPI backend, PostgreSQL import metadata, and validated CSV/XLSX uploads for orders, employees, deliveries, and productivity.

### Run locally

1. Copy `.env.example` to `.env` and activate the project virtual environment.
2. Install dependencies with `python -m pip install -r requirements.txt`.
3. Start PostgreSQL with `docker compose up -d db`.
4. From the `backend` directory, run `..\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload` (or use `python -m uvicorn app.main:app --reload` in an activated environment).
5. Open `http://localhost:8000/docs` to use the API.

### Upload contract

`POST /api/v1/imports` accepts multipart form fields `dataset_type` and `file`. Dataset types are `orders`, `employees`, `deliveries`, and `productivity`. Column names are matched case-insensitively after trimming whitespace; each type requires the following columns:

| Dataset type | Required columns |
| --- | --- |
| orders | `order_id`, `order_date`, `region`, `amount`, `status` |
| employees | `employee_id`, `department`, `region` |
| deliveries | `delivery_id`, `order_id`, `promised_date`, `delivered_date`, `region` |
| productivity | `employee_id`, `date`, `tasks_completed`, `hours_worked` |

Date and numeric fields are validated, blank required values are reported with spreadsheet row numbers, and invalid uploads are rejected with HTTP 422. Valid source files are retained in `data/uploads`; `/api/v1/imports` lists their metadata. The upload size limit is configured by `MAX_UPLOAD_SIZE_MB`.

`GET /health` provides a basic service check. PostgreSQL import records are created at application startup for this initial local-development milestone.
