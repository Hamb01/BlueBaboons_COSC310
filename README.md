# Blue Baboons — Food Delivery Application Backend

A modular, testable, and reliable food-delivery application backend built with **FastAPI**, **Pydantic**, and **pytest**, utilizing layered architecture (**Route → Service → Repository → Persistence**) and containerized with **Docker**.

---

## Team Information
- **Team Name:** Blue Baboons

---

## Prerequisites & Requirements
- **Python Version:** Python 3.10+ (Tested on Python 3.12 / 3.14)
- **Package Manager:** `pip`
- **Optional / Recommended:** Docker & Docker Compose

---

## Repository Structure

```text
.
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── health.py          # HTTP Route: /health endpoint
│   │   ├── __init__.py
│   │   └── deps.py                # Dependency injection wiring (Route -> Service -> Repo)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Dynamic configuration & paths
│   │   └── exceptions.py          # Domain & persistence exceptions
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── health_repository.py   # Repository layer: storage / persistence access
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── health.py              # Pydantic data schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── health_service.py      # Service layer: business logic & orchestration
│   ├── __init__.py
│   └── main.py                    # FastAPI application entrypoint & middleware
├── data/                          # Data directory for JSON/CSV persistence
├── docs/                          # Project documentation & provenance tracking
├── scrum/
│   └── team-agreement.md          # Team Agreement V1
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Test fixtures & isolated persistence
│   └── test_health.py             # Route, Service, and Repository test suite
├── .dockerignore                  # Docker build exclusions
├── .gitignore                     # Git ignore rules
├── Dockerfile                     # Production-ready container image definition
├── docker-compose.yml             # Container orchestration config
├── requirements.txt               # Project dependencies
└── README.md                      # Setup and execution guide
```

---

## Architecture Flow

The backend follows strict separation of concerns:

```
[HTTP Request]
       ↓
[FastAPI Route]  (app/api/routes/health.py)
       ↓
[Service Layer]  (app/services/health_service.py)
       ↓
[Repository Layer] (app/repositories/health_repository.py)
       ↓
[Persistence]    (data/)
```

---

## Local Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd BlueBaboons_COSC310
```

### 2. Create and Activate a Virtual Environment

**macOS / Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Starting the Application

### Option A: Running Directly with Uvicorn (Local)
Ensure your virtual environment is active, then run:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will start at `http://127.0.0.1:8000`.

---

### Option B: Running with Docker

#### Using Docker Compose (Recommended)
```bash
docker compose up --build
```
To stop:
```bash
docker compose down
```

#### Using Docker CLI Directly
1. Build the Docker image:
   ```bash
   docker build -t bluebaboons-api .
   ```
2. Run the container:
   ```bash
   docker run -d -p 8000:8000 --name bluebaboons-container bluebaboons-api
   ```
3. To stop:
   ```bash
   docker stop bluebaboons-container && docker rm bluebaboons-container
   ```

---

## API Endpoints & Interactive Documentation

| Endpoint | Method | Description |
|---|---|---|
| `/` | `GET` | API root overview with documentation links |
| `/health` | `GET` | Health check verifying Route → Service → Repository → Persistence |
| `/docs` | `GET` | Interactive Swagger UI (OpenAPI) |
| `/redoc` | `GET` | ReDoc API documentation |

- **OpenAPI Documentation:** [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- **Health Check:** [`http://127.0.0.1:8000/health`](http://127.0.0.1:8000/health)
- **Representative Data Directory:** Located in [`data/`](data/)

---

## Running Automated Tests

The automated test suite uses `pytest` and runs against isolated temporary directories, guaranteeing zero mutations to persistent data:

```bash
pytest
```

For verbose output:
```bash
pytest -v
```
