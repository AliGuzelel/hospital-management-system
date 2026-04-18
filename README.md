# Hospital Management System (Microservice)

This project is a microservices-based Hospital Management System developed using FastAPI, Docker, and PostgreSQL. The goal of this system is to simulate a real-world backend architecture for managing hospital operations such as user authentication, patient records, doctor information, appointment scheduling, and notifications.

The system is designed with scalability, modularity, and maintainability in mind. Each service is independent and can be developed, deployed, and updated without affecting other parts of the system.

## Features

- JWT-based authentication and authorization
- Role-based access control (Admin, Doctor, Patient)
- Patient profile and record management
- Doctor profile and availability management
- Appointment booking, updating, and cancellation
- Notification service for alerts and system messages
- API Gateway for centralized routing and request handling
- Dockerized architecture for easy deployment
- Monitoring support using Prometheus and Grafana

## System Architecture

The application follows a microservices architecture where each service handles a specific responsibility. All client requests go through the API Gateway, which manages routing, authentication validation, and request forwarding.

Services included in the system:

- API Gateway: Acts as the single entry point. Handles routing, authentication checks, and request/response handling.
- Auth Service: Manages user registration, login, password hashing, and JWT token generation.
- Patient Service: Handles patient-related data such as profiles and records.
- Doctor Service: Manages doctor information including specialization and availability.
- Appointment Service: Responsible for scheduling, updating, and canceling appointments.
- Notification Service: Sends system notifications and can be extended for email/SMS integration.
- Hospital Service: Manages general hospital-related configurations and information.

Each service is implemented as an independent FastAPI application and communicates with others using REST APIs.

## Tech Stack

Backend: Python 3.11, FastAPI  
Database: PostgreSQL  
Containerization: Docker, Docker Compose  
API Communication: REST  
Monitoring: Prometheus, Grafana  
Configuration: Environment variables (.env), Pydantic settings  

## Project Structure

hospital-management-system/
│
├── api-gateway/
├── auth-service/
├── patient-service/
├── doctor-service/
├── appointment-service/
├── notification-service/
├── hospital-system/
│
├── docker-compose.yml
├── README.md
└── .env

Each service contains its own routes, models, schemas, and business logic, following a clean and organized structure.

## Getting Started

Prerequisites:

- Docker and Docker Compose installed
- Git
- Python 3.11 (optional for local development)

To run the system:

```bash
git clone https://github.com/AliGuzelel/hospital-management-system.git
cd hospital-management-system
docker-compose up --build<img width="1376" height="768" alt="hospital-system-request-flow" src="https://github.com/user-attachments/assets/51123deb-1c93-419d-aa0e-72e37c35aa97" />
<img width="1376" height="768" alt="hospital-system-architecture" src="https://github.com/user-attachments/assets/913d214c-95ae-46ee-aaca-6d9c3320bbfe" />
