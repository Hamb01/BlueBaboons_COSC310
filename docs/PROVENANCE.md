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


## Restaurant search and filtering - 2026-10-16

- **Tool / Assistant:** OpenAI Codex
- **Scope / Assistance:** Implemented `GET /restaurants` with optional text
  search across restaurant name, cuisine, and location; exact cuisine filtering;
  partial location filtering; and open-status filtering. Text matching ignores
  case and surrounding whitespace, and supplied filters combine with AND.
  The route delegates to the service, which reads through the existing repository
  and returns Pydantic restaurant response models.
- **Tests / Readability:** Added 18 individually named search/filter tests using
  isolated shared fixtures and direct assertions. Expanded the service logic
  into explicit checks and named variables at the student's request.
- **Integration Assistance:** Resolved the service conflict with `main`, preserving
  both search/filter logic and existing restaurant methods. Removed the duplicate
  `GET /restaurants` route so listing and filtering use one endpoint.
- **Verification:** After conflict resolution, the complete pytest suite passed:
  44 tests, including the 18 search/filter tests. Existing dependency deprecation
  and pytest cache permission warnings remained. Team review and ownership
  verification remain the team's responsibility.

- **Test simplification:** At the student's request, Codex condensed the
  search/filter tests from 18 functions to 8, grouping related checks and removing
  redundant assertions. Core listing, search, filters, validation, and read-only
  checks remain. The complete suite passed: 34 tests.
