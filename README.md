# Hospital Management System

## Overview
This project is a production-oriented Hospital Management System developed using a microservices architecture. The system simulates a real-world healthcare backend, supporting core functionalities such as authentication, patient and doctor management, appointment scheduling, notifications, and invoice handling.

The system demonstrates key software engineering, distributed systems, and DevOps concepts, making it scalable, modular, and maintainable.

---

## Features

### Authentication & Authorization
- User registration and login
- Secure password hashing
- JWT-based authentication
- Role-based authorization (Doctor / Patient)

### Core Functionalities
- Doctors Management
  - Create, update, retrieve, delete doctors

- Patients Management
  - Create, update, retrieve, delete patients

- Appointments
  - Book, update, cancel appointments
  - Validate doctor availability

- Notifications
  - Notify users about appointment status (booked/cancelled)

- Invoices
  - Create and manage billing records
  - Read, update, and retrieve invoices

---

## Architecture

The system follows a microservices architecture, where each service is independently developed and deployed.
## Architecture Diagram

<img width="1536" height="1024" alt="architecture-diagram2" src="https://github.com/user-attachments/assets/df09a701-fdaf-40f4-9fcf-2e5ec92628c3" />


---

### Services
- Auth Service
- Patient Service
- Doctor Service
- Appointment Service
- Notification Service
- Invoice Service
- API Gateway

### Communication Design
- Synchronous Communication: REST APIs between services
- Asynchronous Communication: Design is compatible with message brokers (e.g., RabbitMQ or Kafka)

### API Gateway
- Acts as a single entry point
- Handles routing, authentication validation, and request forwarding

---

## Concepts Implemented

### 1. Clean Architecture
- Separation of concerns (controllers, services, models)
- Independent business logic per service

### 2. REST API Design
- Resource-based endpoints
- Proper HTTP methods (GET, POST, PUT, DELETE)
- Structured JSON responses

### 3. Containerization
- Services containerized using Docker
- Multi-service orchestration via Docker Compose

### 4. CI/CD Concept
- Pipeline design using GitHub Actions
- Automated build and deployment workflow (conceptual implementation)

### 5. Observability
- Centralized logging (ELK-ready design)
- Metrics collection using Prometheus
- Visualization via Grafana
- Distributed tracing using OpenTelemetry

### 6. Security Basics
- JWT authentication
- Password hashing
- Role-based access control
- Rate limiting (basic implementation)
- Secure environment configuration

---

## Distributed System Extension

The system was extended into a distributed architecture with:
- Multiple independent services
- Service-to-service communication via REST
- API Gateway pattern implementation
- Authentication and authorization across services

---

## Deployment

The system is designed to run in a cloud-like environment:
- Container orchestration using Docker Compose (Kubernetes-ready design)
- Environment-based configuration
- Scalable service deployment

---

## CI/CD & DevOps

- CI/CD pipeline design included
- Automated testing concept
- Continuous deployment simulation
- Infrastructure automation principles applied

---

## Monitoring & Reliability

- Centralized logging system
- Metrics monitoring dashboards
- Health check endpoints for services
- Fault tolerance strategies:
  - Service isolation
  - Graceful failure handling

---

## Advanced Security

- Secure authentication system
- Token-based authorization
- Rate limiting
- Secrets management (environment variables)

---

## Testing

- Unit testing for core services
- API endpoint testing
- Basic validation of service interactions

---

## User Interface

- Simple interface (CLI / basic frontend)
- Designed for demonstration purposes

---

## Technologies Used

- Language: Python
- Backend Framework: FastAPI
- Server: Uvicorn
- Containerization: Docker
- CI/CD: GitHub Actions
- Monitoring: Prometheus, Grafana
- Observability: OpenTelemetry

---

## Deliverables

- Architecture diagram
- API documentation
- Working microservices
- CI/CD pipeline configuration
- Deployment scripts
- Monitoring setup
- README (this document)

---


## Conclusion

This project demonstrates how a traditional hospital system can be transformed into a scalable, secure, and production-ready microservices platform. It integrates modern software development practices including distributed systems, DevOps, observability, and security, preparing it for real-world applications.

---

To run the system:

```bash
git clone https://github.com/AliGuzelel/hospital-management-system.git
cd hospital-management-system
docker-compose up --build
