# Hospital Management System (Microservices)

## Services
- API Gateway (`8000`)
- Auth Service (`8001`)
- Patient Service (`8002`)
- Doctor Service (`8003`)
- Appointment Service (`8004`)
- Notification Service (`8005`)
- RabbitMQ (`5672`, UI: `15672`)
- Prometheus (`9090`)
- Grafana (`3000`)

## Architecture
All services use clean architecture style modules:
- `routes/` -> `services/` -> `models/` -> `database/`
- `schemas/` for DTO validation
- `config/` for environment and logging

## Features
- JWT auth with roles (`admin`, `doctor`, `patient`)
- API gateway routing + token guard + rate limiting
- Patient and Doctor management
- Appointment booking/canceling with cross-service validation
- RabbitMQ async events consumed by notification service
- `/health` + `/metrics` for each service
- Prometheus and Grafana included

## Run
```bash
docker compose up --build
```

## CI/CD
GitHub Actions workflow in `.github/workflows/ci.yml`:
- installs service dependencies
- runs tests for every service
- builds Docker images
