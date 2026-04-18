# Hospital Management System (Microservices)

Production-style Hospital Management System built with **FastAPI** microservices, **JWT** auth, **RabbitMQ** events, **Docker Compose**, **Prometheus**, and **Grafana**.

## Architecture

```text
Clients
   |
   v
API Gateway :8000  (JWT checks + rate limiting + HTTP proxying)
   |-----------------------------|------------------------------|
   v                             v                              v
Auth :8001                   Patient :8002                 Doctor :8003
   |                             \                            /
   |                              v                          v
   |                         Appointment :8004  ------> RabbitMQ
   |                                        (appointment_created)
   v                                              |
JWT issued here                                  v
                                           Notification :8005
```

### Service responsibilities

- **api-gateway**: Single public entrypoint. Validates JWT (signature + role gates), applies basic rate limiting, forwards requests with `httpx`, and maps downstream failures to **503/504** when appropriate.
- **auth-service**: Register/login, password hashing (`bcrypt`), JWT minting (`HS256`). Roles: `admin`, `doctor`, `patient`.
- **patient-service**: Patient CRUD + list. Exposes **internal** patient lookup for other services using `X-Service-Token`.
- **doctor-service**: Doctor CRUD + list + availability JSON. Exposes **internal** doctor lookup for other services using `X-Service-Token`.
- **appointment-service**: Creates/cancels/lists appointments. Validates patient/doctor via internal HTTP calls, checks doctor availability windows, prevents overlapping scheduled appointments, publishes `appointment.created` to RabbitMQ.
- **notification-service**: Consumes `appointment.created` and logs a structured notification message.

### Inter-service communication

- **Synchronous**: `httpx` between services. Inside Docker, URLs **must** be service names (for example `http://patient-service:8002`), never `localhost`.
- **Asynchronous**: RabbitMQ **topic** exchange `hospital.events` with routing key `appointment.created`.

### Observability

Every Python service exposes:

- `GET /health`
- `GET /metrics` (Prometheus)

Prometheus scrapes all services using `prometheus.yml`. Grafana is provisioned with a Prometheus datasource.

## Ports

| Service              | Port  |
|----------------------|-------|
| API Gateway          | 8000  |
| Auth                 | 8001  |
| Patient              | 8002  |
| Doctor               | 8003  |
| Appointment          | 8004  |
| Notification         | 8005  |
| RabbitMQ AMQP        | 5672  |
| RabbitMQ Management  | 15672 |
| Prometheus           | 9090  |
| Grafana              | 3000  |

## Run with Docker Compose

From this directory:

```bash
cp .env.example .env
docker compose up --build
```

Defaults:

- Grafana: `http://localhost:3000` (admin / admin)
- RabbitMQ UI: `http://localhost:15672` (guest / guest)
- Prometheus: `http://localhost:9090`
- API docs (per service): `http://localhost:8000/docs` (gateway), `http://localhost:8001/docs`, etc.

## Example API flow (valid JSON)

The examples below use multi-line `curl` with `^` line continuation (**Windows `cmd.exe`**).

On **PowerShell**, prefer single-line requests (or PowerShell’s backtick `` ` `` continuation), for example:

```powershell
Invoke-RestMethod -Method Post -Uri "http://localhost:8000/auth/login" `
  -ContentType "application/json" `
  -Body '{"username":"admin1","password":"password123"}'
```

### 1) Create users

Register an admin:

```bash
curl -sS -X POST "http://localhost:8000/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin1\",\"password\":\"password123\",\"role\":\"admin\"}"
```

Register a patient user:

```bash
curl -sS -X POST "http://localhost:8000/auth/register" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"patient1\",\"password\":\"password123\",\"role\":\"patient\"}"
```

Login:

```bash
curl -sS -X POST "http://localhost:8000/auth/login" ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"admin1\",\"password\":\"password123\"}"
```

Copy `access_token` from the response as `TOKEN`.

### 2) Create patient + doctor records

Create a patient (admin only). Link the patient record to the patient user id from `/auth/login` response (`user_id`):

```bash
curl -sS -X POST "http://localhost:8000/patients" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Alice Example\",\"email\":\"alice@example.com\",\"phone\":\"+15550001\",\"user_id\":2}"
```

Create a doctor:

```bash
curl -sS -X POST "http://localhost:8000/doctors" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"Dr. Smith\",\"email\":\"smith@example.com\",\"phone\":\"+15550002\",\"user_id\":3}"
```

Set availability (Monday 09:00-18:00). Use the doctor id returned by the API (`DOCTOR_ID`):

```bash
curl -sS -X PUT "http://localhost:8000/doctors/DOCTOR_ID/availability" ^
  -H "Authorization: Bearer %TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"slots\":[{\"weekday\":0,\"start\":\"09:00\",\"end\":\"18:00\"}]}"
```

Note: `weekday` uses Python’s convention (`0=Monday` … `6=Sunday`).

### 3) Book an appointment

Use a patient user token for booking (or admin):

```bash
curl -sS -X POST "http://localhost:8000/appointments" ^
  -H "Authorization: Bearer %PATIENT_TOKEN%" ^
  -H "Content-Type: application/json" ^
  -d "{\"patient_id\":1,\"doctor_id\":1,\"start_time\":\"2026-04-20T10:00:00Z\",\"end_time\":\"2026-04-20T10:30:00Z\"}"
```

On success, **appointment-service** publishes an `appointment.created` event and **notification-service** logs it.

## Tests

Each service uses the package name `app`, so tests must run **from inside each service folder** (or CI does `cd <service> && pytest`).

From `hospital-system/`:

```bash
cd auth-service && pytest -q && cd ..
cd patient-service && pytest -q && cd ..
```

There is also a small repo-layout smoke test:

```bash
pytest -q tests
```

## CI/CD

GitHub Actions workflow lives at:

- `../.github/workflows/ci.yml`

It runs service tests with the correct working directories and runs `docker compose config` + `docker compose build` under `hospital-system/`.

## Security notes

- Change `JWT_SECRET` and `INTERNAL_SERVICE_TOKEN` for any shared environment.
- Internal routes require `X-Service-Token` matching `INTERNAL_SERVICE_TOKEN`.
- The API Gateway enforces coarse role checks; each service still enforces authorization on its own routes.
