# Blue Baboons Food Delivery Application

COSC 310 Milestone 2: an integrated food delivery system. Customers sign in,
build a cart from one restaurant's menu, check out, and view their orders;
restaurant owners and admins manage restaurants and menus. Built on the
Milestone 1 restaurant discovery slice with FastAPI, Pydantic, JSON persistence,
pytest, and an HTML/CSS/JavaScript frontend.

[GitHub repository](https://github.com/Hamb01/BlueBaboons_COSC310)

## Features

- List restaurants and view restaurant details.
- Search restaurant names, cuisines, and locations; filter by cuisine, location,
  and open status through the search/filter feature.
- Browse menus and retrieve individual menu items.
- Create restaurants and update restaurant information.
- Sign in with a JSON Web Token; view and update your account; deactivate your
  account, or deactivate a customer as an administrator.
- Roles: only a restaurant's owner or an admin can create or edit restaurants
  and menus; owners can mark menu items unavailable or inactive.
- Shopping cart: add items from one restaurant, change quantities, remove items,
  and clear the cart. Totals are calculated by the backend.
- Checkout: turn the cart into an order using current menu prices; view an order
  and your order history.
- Use the frontend at `/ui/` to browse restaurants, sign in, and manage a cart.

Delivery tracking, payment, and order cancellation are outside M2 scope.
If `/ui/` returns 404 or a route is missing, update your checkout and restart or
rebuild the application.

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

### Demo accounts

| Role | Username | Password | Notes |
|---|---|---|---|
| Customer | `UserName1` | `HardPassword1234` | Customer `c01` |
| Owner | `owner1` | `owner1pass` | Owns restaurant `r01` |
| Owner | `owner2` | `owner2pass` | Owns restaurant `r02` |
| Admin | `admin1` | `admin1pass` | Can edit every restaurant |

Sign in with `POST /auth/login` (or **Sign in** on `/ui/`) and send the returned
token as `Authorization: Bearer <token>`. In `/docs`, select **Authorize**.
These passwords are for local demos only.

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

Compose mounts the checkout's `data/` folder into the container, so changes made
through the app are written to `data/*.json` on your machine and survive
`docker compose down` and rebuilds. Don't commit data changes made while testing;
undo them with `git checkout data/`. Code is still built into the image, so run
`docker compose up --build` after changing code or switching branches.

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
7. Select **Sign in** and use a demo customer account.
8. Select **Add to cart** on a menu item, then open the cart to view items and
   the backend-calculated total.

The interface displays loading, empty, unavailable-item, and error states.
Saving refreshes the list and opens the saved restaurant. Restaurant data is
fetched from the REST API rather than hard-coded in frontend files.
Checkout and order history are available through the API
(`/docs`); the frontend covers browsing, restaurant management, sign-in, and the cart.

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
| POST | `/restaurants/{restaurant_id}/menu` | Add menu item (owner/admin) |
| PUT / PATCH | `/restaurants/{restaurant_id}/menu/{item_id}` | Update menu item, availability, or `is_active` (owner/admin) |
| DELETE | `/restaurants/{restaurant_id}/menu/{menu_item_id}` | Delete menu item (owner/admin, 204) |
| POST | `/auth/login` | Sign in; returns a JWT |
| GET / PATCH | `/customers/me` | View or update my account |
| POST | `/customers/me/deactivate` | Deactivate my account |
| POST | `/customers/{customer_id}/deactivate` | Admin deactivates a customer |
| GET | `/customers/{customer_id}` | Customer details |
| GET / DELETE | `/cart` | View my active cart / clear it |
| POST | `/cart/items` | Add an item to my cart |
| PATCH / DELETE | `/cart/items/{menu_item_id}` | Change quantity / remove an item |
| POST | `/checkout` | Check out my cart into an order (201) |
| GET | `/customers/me/orders` | My order history |
| GET | `/orders/{order_id}` | One of my orders |
| GET | `/ui/` | Frontend |
| GET | `/docs` | Interactive Swagger documentation |
| GET | `/redoc` | ReDoc documentation |
| GET | `/openapi.json` | Generated API contract |

Unknown restaurant/item reads return 404. A restaurant without menu items returns
an empty menu. Menu item responses use `availability`, not `available`; inactive
items (`is_active: false`) are hidden from menus.

Errors use one JSON shape (`status_code`, `message`, `details`):

| Status | Meaning |
|---|---|
| 401 | Missing or invalid token |
| 403 | Deactivated account, or not allowed (e.g. owner editing another owner's restaurant) |
| 404 | Restaurant, menu item, cart item, or order not found |
| 409 | Business rule broken: items from a second restaurant, unavailable item, empty or missing cart at checkout |
| 422 | Invalid body or parameters, e.g. quantity below 1 or negative price |

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

### Customer-to-order workflow

```text
POST /auth/login            {"username": "UserName1", "password": "HardPassword1234"}
POST /cart/items            {"restaurant_id": "r01", "menu_item_id": "m01", "quantity": 2}
PATCH /cart/items/m01       {"quantity": 3}
POST /checkout              -> 201 order with price snapshot; cart is closed
GET /customers/me/orders    -> the new order
```

Checkout rechecks every item against the current menu: an unavailable or inactive
item returns 409 and leaves the cart unchanged, and a changed price is used in
the order. The order stores each item's name and price at checkout, so later menu
changes do not alter it. The order is saved before the cart is closed.

## Architecture and persistence

```text
Frontend -> REST route -> Service -> Repository -> JSON
```

Routes handle HTTP input/output, authentication, and dependency injection.
Services own the business rules (roles, one restaurant per cart, availability,
checkout) and return Pydantic models. Each repository owns one JSON file and only
loads and saves records:

| Repository | File | Records |
|---|---|---|
| `UserRepository` | `data/Users.json` | Customers (`c01`), owners (`o01`), admins (`a01`) |
| `RestaurantRepository` / `MenuRepository` | `data/Restaurants.json` | Restaurants (`r01`) with nested menus (`m01`) |
| `CartRepository` | `data/Carts.json` | Carts (`k01`) referencing customer, restaurant, and menu item IDs |
| `OrderRepository` | `data/Orders.json` | Orders (`o01`) with name and price snapshots |

Records reference each other by stable string IDs. Writes go through
`JsonStore`, which writes a temporary file and replaces the original, so a crash
cannot leave a half-written file. Checkout writes `Orders.json` and then
`Carts.json`; the two files are not updated in one transaction.

Local writes survive application restarts. `DATA_DIR` overrides the storage
directory, for example `$env:DATA_DIR = "C:\path\to\data"` in PowerShell.
Each checkout/worktree uses its own data directory unless configured otherwise.

```text
app/main.py                      FastAPI setup and /ui static hosting
app/api/routes/                  Health, restaurant, menu, auth, customer, cart, order endpoints
app/api/deps.py                  Dependency injection
app/services/                    Application logic
app/repositories/                JSON persistence
app/schemas/                     Pydantic contracts
app/core/                        Settings and domain exceptions
app/frontend/                    HTML/CSS/JavaScript frontend assets
data/*.json                      Users, restaurants and menus, carts, orders
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
restaurant creation/editing, sign-in, cart, checkout, order history, a
deactivated customer, error states, and persistence after restarting.

## Milestone records

- Assistance and provenance: `docs/PROVENANCE.md`.
- Team agreement and meeting notes: `scrum/`.
- Milestone 1 was submitted with the tag `m1-vertical-slice`.
- Milestone 2 is submitted with the immutable tag `m2-integrated-system`.
- The Canvas PDF must include repository, project-board and tag/release URLs,
  the full tagged commit SHA, and agreed contribution percentages totaling 100%.
