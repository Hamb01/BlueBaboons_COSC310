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

## Restaurant frontend - 2026-10-16

- **Tool / Assistant:** OpenAI Codex (Sites skill, local-only workflow).
- **Scope / Assistance:** Built the HTML/CSS/JavaScript interface at `/ui/`
  using existing REST endpoints for restaurant browsing, search/filter, details,
  menu viewing, and restaurant creation/editing. Added FastAPI static hosting,
  README instructions, and frontend asset/management API tests.
- **Verification:** JavaScript syntax check passed; 46 pytest tests passed.
  Interactive browser verification and team review remain outstanding.
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

## M2 contracts / scaffolding - 2026-10-23

- **Tool / Assistant:** Claude Code (Anthropic, Claude Opus 5.5)
- **Scope / Assistance:** Generated the M2 contracts PR scaffolding: Pydantic schemas
  (`user_schema.py`, `cart_schema.py`, `order_schema.py`, `error_schema.py`), domain error
  classes with HTTP status codes and the shared error handler in `app/main.py`,
  `get_current_user` / `require_roles` in `app/api/deps.py`, dependency providers,
  route definitions with OpenAPI metadata, the `JsonFileStore` persistence helper,
  repository and service method signatures (bodies intentionally left as
  `NotImplementedError` for each owner to implement), test fixtures in `tests/conftest.py`,
  `tests/test_m2_contracts.py`, and `docs/milestones/M2.md`.
- **Not AI-generated:** All business logic for customers, auth, cart, checkout, and orders
  is to be written by the owning team member.
- **Verification:** Full pytest suite passed (103 tests: 54 existing + 49 contract tests).
  Team review of the contract and ownership verification remain the team's responsibility.
