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

## M1 fixes and repo cleanup - 2026-10-26 to 2026-10-29

- **Student:** Turbileg Uurtsaikh (prompted the AI, reviewed its output and opened the PRs)
- **Tool / Assistant:** Claude Code (Anthropic, Claude Opus 5.5)
- **Scope / Assistance:**
  - **Menu split (PR #58):** moved menu routes, service and repository code out of the
    restaurant files into `menu_routes.py`, `menu_service.py` and `menu_repository.py`.
    Injected the service into `add_menu_item`. `RestaurantService` now passes plain
    dicts to the repository, fixing a Pylance type error.
  - **Pylint (PR #59):** added `.pylintrc`, pylint in `requirements.txt` and a CI lint job
    with `--fail-under` set to the scores at the time.
  - **Menu write fixes (PR #71, issues #61-#63):** rewrote menu update, add and delete in
    the repository and service, and mapped domain errors to 404 and validation errors to
    422 in the routes. Made new menu item ids unique across restaurants. Wrote 28
    regression tests first (`tests/test_menu_writes.py`) and updated the Mock-based tests
    in `tests/test_menu.py` to match.
  - **Docker data volume (PR #72):** mounted `./data` into the container and updated the README.
  - **Frontend add-item dialog (PR #73):** "+ Add item" button, dialog and form handling in
    `app/frontend/`, plus a frontend test.
  - **Planning and analysis:** drafted the M2 sprint plan, a status report of `main`
    (endpoints, data model, tests, 17 bugs probed with real HTTP requests on a copy of the
    data, and the M2 requirements checklist), the text of issues #60-#69, and code
    explanations on request.
- **Verification & Ownership:**
  - Claude ran pytest after each change: 54 tests before the fixes, 81 after PR #71,
    82 after PR #73. Bug symptoms were reproduced before fixing and re-checked afterwards
    with the same HTTP requests.
  - The student reviewed each change, tried the add-item dialog in the browser, and
    confirmed Docker writes reach `data/Restaurants.json`.
  - Each PR goes through review by a teammate who is not the author before merging.

- **Student** Isaac Meyer (prompted the AI and revied it's changes)
- **Tool / Assistant:** GitHub Copilot
- **Scope / Assistance:** 
  - Copilot altered the code in app.js to work with the new exception handler
  - Copilot sumarized some of the reasons why tests related to the frontend were failing (The problem was two-fold. 1: I had to update the test to reflect the changes we made to how we are using/catching exceptions and 2: there was an instance of EmptyMenuError that was incorrectly initialized)
  - Copilot read through main.py and reformatted the code to improve our pylint score. It did not alter the code's behaviour
- **Verification:** 
  - All tests relating to the frontend passed
  - I also went thropugh and reviewed the code, I then had copilot make a summary of what it did and why it works. This Summary matched with my understanding of what was written so it is good


## User Login Endpoint — 2026-11-12

- **Tool / Assistant:** Github Copilot
- **Scope / Assistance:** 
  - I had it reword error messages so that I would have an easier time fixing the bugs
  - I had it rework the user_login service because the order of the logic was causing errors
  - I also had it go through and reformat some of the code to improve the pylint score
- **Verification:** 
  - I carefully read through all of the code that the AI generated and rewrote most of it my self 
  - for any suggestions the AI gave me, I double checked with other online resources like geeksforgeeks.org
  - In addition, all the tests passed

## User Login Endpoint — 2026-11-15

- **Tool / Assistant:** Google's Gemini
- **Scope / Assistance:** 
  - the code for hashing passwords and extracting the user's JWT from the http header was based off of a gemini generated example. All of the code was modified to fit out project and not directly copied from gemini
- **Verification:** 
  - I read through the AIs explanation and double checked that it would work by going through the fastapi documentation
  - In addition, all the tests passed

## get customer Endpoint — 2026-11-16

- **Tool / Assistant:** Github Copilot
- **Scope / Assistance:** 
  - I had it go through and reformat some of the code to improve the pylint score
- **Verification:** 
  - I carefully read through all of the code that the AI modified and verified that the AI didn't generate any code, it mearly reformatted existing code to improve the lint score
  - In addition, all the tests passed

## Customer update: required address — 2026-11-19
- **Tool / Assistant:** Claude Code (Anthropic, Claude Opus 5.5)
- **Scope / Assistance:**
  - Explained how to make the address required in `CustomerUpdate`, and that FastAPI
    returns the 422 itself when the schema's validation fails, so the validator only raises `ValueError`.
  - Changed `address`, `city`, `province` and `postal_code` in `CustomerUpdate`
    (`app/schemas/user_schema.py`) from `Field(default=None)` to `Field(...)`, because
    a default value still let the fields be left out of a request.
  - Updated the `CustomerUpdate` tests in `tests/test_user_services.py` for the required address:
    - Added a `NEW_ADDRESS` fixture with all four address parts.
    - Added tests that reject a missing address part, an empty body, and a name/email
      change sent without the address.
    - Replaced the empty-body test with one that resends the current address with
      a new email and checks that only the email changed on disk.
- **Verification & Ownership:**
  - Claude did not run the tests: pytest stopped while loading `conftest.py` because PyJWT was
    not installed in the local `.venv`.
  - The student installed the requirements, ran the test suite and reviewed the changes.
---
## Bug Fixing 2026-11-18
- **Tool / Assistant:** Copilot
- **Scope / Assistance:**
- Changed test_orders.py and main.py to avoid 5 tests from failing

- **Verificaton**
- I read trough the changes it made to both files, ensuring no major reformating was done and that only lines necessary for bug fixign were altered.
- All tests passed.

## Writing Tests 2026-11-20
- **Tool / Assistant:** Copilot
- **Scope / Assistance:**
- Asked Copilot to write tests for the implementation of updating item quantity in a cart, deleting an item, and clearing the cart. Also tests for owners setting menu items to active/inactive, and how that status interacts with the checkout.

- **Verificaton**
- Asked copilot to explain what each of the tests do, how they work, and why it chose to implement them.
- Ensured tests made sense for the scope of our project.
- Verified all tests passed.
## M2 accounts, cart, orders, fixes and docs - 2026-11-16 to 2026-11-20

- **Student:** Turbileg Uurtsaikh (prompted the AI, reviewed its output and opened the PRs)
- **Tool / Assistant:** Claude Code (Anthropic, Claude Opus 5.5)
- **Scope / Assistance:**
  - **Login wiring (PR #119):** fixed `DomainError.status_code` typing and two dependency
    wiring bugs that made every login return 500. Added `tests/test_auth_wiring.py`, which
    runs login with only the repository overridden; both tests fail on the old code.
  - **Cart (PR #123, issues #95, #96):** cart schemas, `CartService` with the M2 rules
    (one restaurant per cart, unavailable item -> 409, same item merges quantity, nothing
    saved when a rule fails), the `CartRepositoryInterface`, and the cart routes. Wrote
    18 tests in `tests/test_cart.py` using an in-memory repository.
  - **Orders (PR #125, issues #99, #100):** view an order and my order history, with the
    item name and price stored at order time. Tests for 401/403/404, history, and the price
    staying the same after a menu change. Later simplified the order code and trimmed comments.
  - **Frontend (PR #126):** sign in, add to cart and view cart in `app/frontend/`, plus a
    page test and a sign in -> add to cart -> view cart test.
  - **Bug fixes (PR #134):** menu PUT/PATCH took an `int` restaurant id, so `r01` returned
    422 (#60); seeded owner and admin accounts and pointed restaurants at real owners;
    owners passed the admin check because `RestaurantOwner` subclasses `RestaurantAdmin`,
    so any owner could edit any restaurant (#89). Added `tests/test_roles.py`, which signs
    in with the seed accounts.
  - **OpenAPI (PR #135, issue #69):** typed `MenuItemUpdate` body and documented error
    responses. This PR was merged into the #134 branch after #134 had merged, so it did not
    reach `main`.
  - **Documentation:** updated `README.md` for Milestone 2 (features, demo accounts, endpoints,
    error codes, workflow, persistence) and this entry.
  - **Planning and analysis:** M2 progress reports (16-20 Nov) built from tests, lint and HTTP
    requests run on a copy of the data; drafts of the M2 decision receipt answers.
- **Verification & Ownership:**
  - Claude ran pytest and pylint after each change: 152 tests on main before PR #134, 171
    after it, 189 with PR #135. Bugs were reproduced over HTTP before fixing and re-checked
    afterwards with the same requests.
  - Tests were written before the fixes in PR #134 and PR #135 and failed on the old code.
  - The student reviewed each change, and each PR was reviewed by a teammate who is not the
    author before merging.
