# Django Order Management

A small-scale, production-grade backend showcasing modern practices: JWT auth, order APIs, background processing with Celery, PostgreSQL, Redis, error handling, logging, and rate limiting.

## Tech Stack
- Python 3.10
- Django REST Framework (DRF)
- SimpleJWT (access token defaults to 15 minutes, refresh 7 days)
- Celery + Redis (broker + results)
- PostgreSQL
- Docker + Docker Compose

## Features
- Authentication
  - POST /users/register — create account (bcrypt password hashing)
  - POST /users/login — returns access and refresh JWTs
  - POST /users/token/refresh — returns new access token from refresh
- Orders
  - GET /orders — list logged-in user's orders (paginated)
  - POST /orders — create a new order (product_name, quantity, amount)
  - PATCH /orders/:id/cancel — cancel an order by its uid
- Background jobs
  - Every 2–3 minutes, Celery Beat picks all pending orders, marks them processing → completed
  - Logs show which orders were processed
- Error handling & logging
  - 400, 401, 404, 409, 500 where appropriate, with structured JSON errors
  - Application and task logs via Python logging
- Rate limiting
  - Per-user, per-endpoint limiting via Redis (429 response when exceeded)

## One-Click Container Setup
Prerequisites: Docker and Docker Compose installed.

1) Copy environment template

```
cp .env.example .env
```

2) Start all services
```
docker compose up -d
```
This launches:
- postgres (port 5432)
- redis (port 6379)
- backend (Django at :8000)
- celery worker
- celery beat (scheduler)

3) Apply database migrations
```
docker compose exec backend python manage.py migrate
```

5) Access the API
- Base URL: http://localhost:8000/
- See endpoints below and your Postman collection.

## Local Development Without Docker
1) Python environment
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
2) Ensure Postgres and Redis are running locally, then set .env with matching values (e.g., DB_HOST=localhost, REDIS_URL=redis://localhost:6379/0).
3) Migrate and run
```
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```
4) Start Celery worker and beat (in separate terminals)
```
celery -A config worker --loglevel=info
celery -A config beat --loglevel=info
```

## API Endpoints
Authorization: Bearer <access_token> on protected endpoints.

- POST /users/register
  - Body: { "name": string, "email": string, "password": string }
  - 201: { id, message }
  - 409: validation errors

- POST /users/login
  - Body: { "email": string, "password": string }
  - 200: { message, access, refresh }
  - 409: invalid credentials; 500 on unexpected errors

- POST /users/token/refresh
  - Body: { "refresh": string }
  - 200: { access, message }
  - 401: invalid or expired refresh token

- GET /orders
  - Headers: Authorization: Bearer <access>
  - 200: paginated list of user's orders
  - Response items: { uid, product_name, quantity, amount, status }

- POST /orders
  - Headers: Authorization: Bearer <access>
  - Body: { "product_name": string, "quantity": integer, "amount": decimal }
  - 201: { order_id, message }

- PATCH /orders/:id/cancel
  - Headers: Authorization: Bearer <access>
  - Path param: id = order uid
  - 200: { order_id, message }
  - 404: when the order uid is not found

## Background Processing
- Celery Beat runs the scheduled task orders.tasks.process_pending_orders at intervals defined by CELERY_BEAT_SCHEDULER_SECONDS (default 120 seconds).
- Task behavior:
  1) Find all orders with status = pending
  2) Log and mark them processing
  3) Simulate work for ~10s
  4) Mark them completed and log IDs

## Rate Limiting
- Applied to authenticated users per endpoint via Redis.
- Environment controls:
  - RATE_LIMIT_MAX_REQUEST (default 100)
  - RATE_LIMIT_WINDOW_SECONDS (default 600)
- Exceeding the limit returns HTTP 429 with a retry message.

## Database Schema
- users.CustomUser
  - id, uid, name, email (unique), password_hash, created_at, updated_at, deleted_at
  - AUTH_USER_MODEL = users.CustomUser (USERNAME_FIELD = email)
- orders.Order
  - id, uid (unique), user_id (FK → users.CustomUser), product_name, quantity, amount, status, created_at, updated_at, deleted_at
  - Status values: pending, processing, completed, cancelled

Migrations are included under app migrations directories and apply automatically via manage.py migrate.

## Error Handling
- 400 Bad Request: missing/invalid fields
- 401 Unauthorized: invalid/expired JWT or missing token
- 404 Not Found: order not found on cancel
- 409 Conflict: validation errors (e.g., user already exists, bad login)
- 500 Internal Server Error: unexpected server errors

## Logging
- App logs capture registration/login/order operations and unexpected errors.
- Celery worker logs show when pending orders are processed and completed.
- View logs via:
```
docker compose logs -f backend
docker compose logs -f celery
docker compose logs -f celery-beat
```

## Postman Collection
Click on the hyper link for the postman collection.
##### [Postman Collection URL](https://lively-astronaut-595012.postman.co/workspace/My-Workspace~98a11104-d5f2-4192-8b59-162375a3d554/collection/28455756-3909e007-147b-4009-8a15-f3225aef3997?action=share&creator=28455756).
Import it and set the base URL variable (http://localhost:8000). Use the login call to obtain the access token and set it as a collection variable for Authorization.





## Running Tests
```
python manage.py test --settings=test_settings
```
(Or inside the container: `docker compose exec backend python manage.py test`)
