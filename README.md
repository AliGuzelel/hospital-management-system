Task Management Microservice


Done By: Ali Yakup Guzelel, Harir Duraid, Hanan Abazah

Project Overview
The Task Management Microservice allows users to create, read, update, and delete tasks. Each task contains basic information such as title, description, status, priority, and due date. The main goal of this project is not only to build a functional service, but also to apply professional software development practices such as clean architecture, containerization, observability, CI/CD concepts, and security basics.

Objectives:
-	Design a microservice using Clean Architecture
-	Build a REST API for task management
-	Prepare the service for containerized deployment
-	Demonstrate the idea of CI/CD
-	Include logging and monitoring concepts
-	Apply basic security practices

Features
-	Create and delete tasks
-	View all tasks
-	View a single task by ID
-	Update task details
-	Change task status
-	Input validation
-	Structured error handling
-	Logging support
-	Docker support
-	CI/CD workflow concept
 
Clean Architecture
This project follows the principles of Clean Architecture by separating responsibilities into clear layers. This makes the code easier to maintain, test, and extend.
Example structure:
-	Domain Layer
Contains the core business entities and rules.
-	Application Layer
Contains use cases and business logic.
-	Infrastructure Layer
Handles database access and technical implementation details.
-	Presentation Layer
Exposes REST API endpoints and handles requests and responses.

REST API Design
The microservice exposes RESTful endpoints for task management.
Example Endpoints:
-	POST /tasks → Create a task
-	GET /tasks → Get all tasks
-	GET /tasks/{id} → Get task by ID
-	PUT /tasks/{id} → Update task
-	DELETE /tasks/{id} → Delete task
-	PATCH /tasks/{id}/status → Update task status

Containerization
The project is prepared for containerized execution using Docker. Containerization ensures that the microservice runs consistently across different environments.
Benefits
-	Easy setup and deployment
-	Consistent runtime environment
-	Better portability
-	Simplified dependency management
 
System Architecture:
-	API Gateway (port 8000) – single entry point for the client
-	Auth Service (port 8001) – login + token validation
-	Task Service (port 8002) – task CRUD + emits task events
-	Task Worker Service (port 8004) – consumes task events and triggers notifications
-	Notification Service (port 8003) – receives task notifications

CI/CD Concept
This project demonstrates the concept of Continuous Integration and Continuous Deployment (CI/CD) using GitHub Actions.
The CI/CD pipeline can be used to:
-	Automatically build the project
-	Run tests on every push
-	Check code quality
-	Prepare deployment steps

Observability
Observability is important for understanding the health and behavior of a microservice.
This project includes or plans to include:
-	Application logging
-	Error logging
-	Request tracking
-	Health check endpoint
-	Basic monitoring support

Security Basics
Basic security practices are considered in this project, including:
-	Input validation
-	Secure API request handling
-	Error message control
-	Protection against invalid or malicious data
-	Authentication concept (if implemented)
-	Authorization concept (if implemented)
 
Implemented Services
1. API Gateway (Port 8000)
Clients communicate only with the gateway, which forwards requests to the appropriate service.
Endpoints:
-	POST /auth/login
-	GET /auth/validate
-	GET /tasks
-	POST /tasks
-	PUT /tasks/{task_id}
-	DELETE /tasks/{task_id}

2. Auth Service (Port 8001)
Endpoints:
-	POST /login
-	GET /validate
Features:
-	User login
-	Token generation
-	Token validation

3. Task Service (Port 8002)
Endpoints:
-	POST /tasks
-	GET /tasks
-	PUT /tasks/{task_id}
-	DELETE /tasks/{task_id}
4. Task Worker Service (Port 8004):
The worker continuously pulls events from the Task Service and triggers notifications.
Responsibilities:
-	Poll `task_service` for the next event (`/internal/events/next`)
-	Send notification requests to Notification Service (`/notify`)

5. Notification Service (Port 8003)
Endpoints:
-	POST /notify 
Communication Flow:

1.	The client sends requests to the API Gateway.
2.	The API Gateway forwards authentication requests to the Auth Service.
3.	The API Gateway forwards task requests to the Task Service.
4.	When tasks change, the Task Service emits a task event (in-memory queue inside Task Service).
5.	The Task Worker Service pulls the next event from the Task Service and sends a notification to the Notification Service.
6.	The Notification Service processes the notification.



Client
   |
   v
API Gateway
   |
   +-------------------+
   |                   |
   v                   v
AuthService          TaskAPI
                         |
                         +----------------------+
                         |                      |
                         v                      v
                      TaskDB                TaskQueue
                         |
                         v
                TaskWorkerService
                         |
                         v
                NotificationService
                         |
                         v
                Email / Log / Console
