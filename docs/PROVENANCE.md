# Project Provenance Log

This document records externally assisted content, AI tooling, and design assistance in accordance with the COSC 310 course policy.

---

## Milestone 0 — Foundational Gate

- **Date:** 2026-09-24
- **Tool / Assistant:** AI Assistant (Antigravity)
- **Scope / Assistance:**
  - Scaffolding the layered backend architecture:
    - FastAPI Route: `app/api/routes/health.py`
    - Service Layer: `app/services/health_service.py`
    - Repository Layer: `app/repositories/health_repository.py`
    - Pydantic Schema: `app/schemas/health.py`
    - Dependency Injection: `app/api/deps.py`
    - Configuration: `app/core/config.py` and `app/core/exceptions.py`
    - Entrypoint: `app/main.py`
  - Containerization setup:
    - `Dockerfile` using `python:3.12-slim` with non-root user and health checks
    - `.dockerignore`
    - `docker-compose.yml`
  - Automated testing setup:
    - `tests/conftest.py` with isolated fixtures
    - `tests/test_health.py` testing Route, Service, Repository, and 404 failure handling
  - Documentation:
    - Comprehensive `README.md` with setup, Docker, and testing instructions
    - Version tag update in `scrum/team-agreement.md` (Team Agreement V1)
- **Verification & Ownership:**
  - Team verified all 5 tests run and pass cleanly using `pytest`.
  - Team validated that the health endpoint returns HTTP 200 through the complete Route → Service → Repository flow.
  - Team verified Docker and local virtual environment execution.

- **Date:** 2026-09-25
- **Tool / Assistant:** Github Copilot
- **Scope / Assistance:**
  - Error locating
    - I told copilot to read through a long exception thrown out while running unit tests to tell me where the error was located
    - Copilot told me the file and then I coded in the fix which came down to a type mismatch between 2 functions written by separeate team members
- **Verification & Ownership:**
  - Copilot made no edits to the code, just pointed out the offending code block
  - Team verified all 11 tests run and pass cleanly using `pytest`.
