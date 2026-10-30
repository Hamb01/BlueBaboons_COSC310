# Blue Baboons Food Delivery Application

COSC 310 Milestone 1: restaurant discovery and menu browsing, built with
FastAPI, Pydantic, JSON persistence, pytest, and an HTML/CSS/JavaScript frontend.

[GitHub repository](https://github.com/Hamb01/BlueBaboons_COSC310)

## Features

- List restaurants and view restaurant details.
- Search restaurant names, cuisines, and locations; filter by cuisine, location,
  and open status through the search/filter feature.
- Browse menus and retrieve individual menu items.
- Create restaurants and update restaurant information.
- Use the frontend at `/ui/` to browse and manage restaurants through REST calls.

The frontend and search/filter features are included in the merged application.
If `/ui/` returns 404 or `/restaurants` ignores filters, update your checkout
and restart or rebuild the application.
Authentication, shopping carts, orders, and delivery are outside M1 scope.

## Quick start: Docker

Install Docker with Compose, then run:

```powershell
git clone https://github.com/Hamb01/BlueBaboons_COSC310.git
cd BlueBaboons_COSC310
git switch main
git pull origin main
docker compose up --build
```

Open **[http://localhost:8000/ui/](http://localhost:8000/ui/)**.
API documentation is at **[http://localhost:8000/docs](http://localhost:8000/docs)**.
The root `/` returns a JSON API overview.

Stop the container with `docker compose stop`. Resume with `docker compose start`.
Use `docker compose down` to remove the stack. Use `docker compose up --build`
after code changes to build the updated application.

### Container-name conflict

Compose uses the fixed container name `bluebaboons-api`. Stop the Compose stack
from the checkout that created it before starting another checkout/worktree.
For example, from the frontend worktree on the existing Windows setup:

```powershell
docker compose -f C:\Users\tubul\BlueBaboons_COSC310\docker-compose.yml down
docker compose up --build
```

The current Compose configuration has no persistent data volume. JSON changes
survive restarting the same container, but removing/recreating that container
loses its writable data. Preserve required data before doing so, or configure a
data volume for long-term Docker persistence.

## Local development

Python 3.12 is recommended and is used by the Docker image. No Node installation
or frontend build step is required to run the application.

### Windows PowerShell

From the project checkout:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

### macOS / Linux

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m uvicorn app.main:app --reload --port 8000
```

Open **http://localhost:8000/ui/**. Keep the terminal running; press **Ctrl+C**
to stop. If port 8000 is occupied, use `--port 8001` and open the matching URL.

### Existing frontend worktree

If Git says `feature/restaurant-frontend` is already checked out in another
worktree, change to that directory instead of checking it out again:

```powershell
cd C:\Users\tubul\BlueBaboons_COSC310\.worktrees\restaurant-frontend
C:\Users\tubul\BlueBaboons_COSC310\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

## Frontend walkthrough

1. Open `/ui/` to fetch restaurants from the API.
2. Enter search text or filters and select **Search**. **Clear** resets filters.
3. Select a restaurant to view its details and menu.
4. Select **View item** to fetch an individual menu item.
5. Select **Add restaurant** to create a restaurant.
6. Select **Edit restaurant** in its details to update its information.

The interface displays loading, empty, unavailable-item, and error states.
Saving refreshes the list and opens the saved restaurant. Restaurant data is
fetched from the REST API rather than hard-coded in frontend files.
The current frontend management forms cover restaurant creation and editing.

## REST API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API overview |
| GET | `/health` | Service and persistence-directory status |
| GET | `/restaurants` | List, search, and filter restaurants |
| GET | `/restaurants/{restaurant_id}` | Restaurant details |
| POST | `/restaurants` | Create restaurant (201) |
| PUT | `/restaurants/{restaurant_id}` | Update restaurant information |
| GET | `/restaurants/{restaurant_id}/menu` | Restaurant menu |
| GET | `/restaurants/{restaurant_id}/menu/{item_id}` | Individual menu item |
| POST | `/restaurant/{restaurant_id}/menu` | Registered menu-create route |
| PUT / PATCH | `/restaurant/{restaurant_id}/menu/{item_id}` | Registered menu-update routes |
| DELETE | `/restaurants/{restaurant_id}/menu/{menu_item}` | Registered menu-delete route |
| GET | `/ui/` | Restaurant frontend |
| GET | `/docs` | Interactive Swagger documentation |
| GET | `/redoc` | ReDoc documentation |
| GET | `/openapi.json` | Generated API contract |

Menu-write routes currently use different naming from menu reads. In the locally
verified backend, update IDs are typed as integers despite string seed IDs,
creation bypasses dependency injection, and the delete route's path parameter
name differs from its function argument. Verify these routes before relying on
menu management; repository/service tests alone do not verify these HTTP writes.

Unknown restaurant/item reads return 404. A restaurant without menu items returns
an empty menu. Menu item responses use `availability`, not `available`.

### Search/filter parameters

| Parameter | Behavior |
|---|---|
| `search` | Substring of restaurant name, cuisine, or location |
| `cuisine` | Exact cuisine match |
| `location` | Substring of restaurant location |
| `is_open` | Boolean `true` or `false` |

Text matching ignores case and surrounding whitespace. Empty text filters are
ignored. Supplied filters combine with AND. No matches returns HTTP 200 with
`[]`; invalid boolean values return 422.

```text
GET /restaurants?search=taco
GET /restaurants?cuisine=Japanese&location=Rutland&is_open=true
GET /restaurants/r01
GET /restaurants/r01/menu
GET /restaurants/r01/menu/m01
```

### Create/update restaurant body

```json
{
  "name": "Campus Cafe",
  "location": "Kelowna",
  "isOpen": true,
  "cuisine": "Cafe",
  "opening_hours": "08:00-17:00"
}
```

The server assigns restaurant IDs. The update model also accepts partial fields.

## Architecture and persistence

```text
Frontend -> REST route -> Service -> Repository -> JSON
```

Routes handle HTTP input/output and dependency injection. Services coordinate
operations, return Pydantic models, and apply search/filter rules. Repositories
read/write `data/Restaurants.json`. Restaurant records are keyed by stable IDs;
menus are nested under each restaurant's `menu` field.

Local writes survive application restarts. `DATA_DIR` overrides the storage
directory, for example `$env:DATA_DIR = "C:\path\to\data"` in PowerShell.
Each checkout/worktree uses its own data directory unless configured otherwise.

```text
app/main.py                      FastAPI setup and /ui static hosting
app/api/routes/                  Health and restaurant endpoints
app/api/deps.py                  Dependency injection
app/services/                    Application logic
app/repositories/                JSON persistence
app/schemas/                     Pydantic contracts
app/core/                        Settings and domain exceptions
app/frontend/                    HTML/CSS/JavaScript frontend assets
data/Restaurants.json            Restaurant and menu data
tests/                           Tests and isolated fixtures
.github/workflows/run_tests.yaml  Automated pytest workflow
docs/PROVENANCE.md                Assistance/provenance record
scrum/                           Team agreement and meeting notes
```

## Tests and CI

Use the checkout's virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

On macOS/Linux: `.venv/bin/python -m pytest -q`.
Tests use temporary data and dependency overrides. GitHub Actions installs
requirements and runs pytest on pushes and pull requests.

Lint with pylint (configured in `.pylintrc`) before opening a pull request:

```bash
.venv/bin/python -m pylint app
.venv/bin/python -m pylint tests --disable=redefined-outer-name,missing-function-docstring
```

CI runs the same commands with a `--fail-under` score, so a pull request cannot
lower the lint score. Raise the thresholds in `.github/workflows/run_tests.yaml`
as files are cleaned up; the team goal is 10/10.

For Windows temporary-folder permission errors, use a fresh repository-local
base directory whose parent already exists:

```powershell
New-Item -ItemType Directory -Force .test-tmp
.\.venv\Scripts\python.exe -m pytest -q --basetemp=.test-tmp/run-1
```

Choose a new directory name on subsequent runs. Pytest manages the base directory.
For optional JavaScript syntax checking: `node --check app/frontend/app.js`.
Before the live demo, manually verify browsing, filters, details, menus,
restaurant creation/editing, error states, and persistence after restarting.

## Milestone records

- Assistance and provenance: `docs/PROVENANCE.md`.
- Team agreement and meeting notes: `scrum/`.
- Submit the reviewed version using the immutable tag `m1-vertical-slice`.
- The Canvas PDF must include repository, project-board and tag/release URLs,
  the full tagged commit SHA, and agreed contribution percentages totaling 100%.
