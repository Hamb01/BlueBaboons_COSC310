# Project Provenance Log

This document records externally assisted content, AI tooling, and design assistance in accordance with the COSC 310 course policy.

## Menu browsing — 2026-10-16

- **Tool / Assistant:** OpenAI Codex
- **Scope / Assistance:** Corrected undefined string annotations blocking startup;
  implemented the MenuItem model, menu read endpoints, service lookup and
  repository reads; added seed menus, menu tests, and endpoint documentation.
  Separated stacked restaurant route decorators, aligned restaurant response
  mapping and existing tests with stored JSON, and repaired temporary-data fixtures.
- **Verification:** Codex ran the complete pytest suite: 22 tests passed, with
  one dependency deprecation warning. Team review and ownership verification
  remain the team's responsibility.

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


## Milestone 1 - first vertical slice
**Date:** 2026-10-16
- **Tool / Assistant:** Github Copilot
- **Scope / Assistance:**
  - created a number generator function
    - I had copilot generate the generate_menu_item_id function as while it is an easy operation, the syntax is easy to mess up on
  - created some unit tests for adding, updating and removing menu items
    - I had copilot generate some unit tests, I then reformatted all of them to better fit the coding style present in the other tests in test_menu.py (for continuities sake)
- **Verification & Ownership:**
  - code was reviewed by team members and all tests passed