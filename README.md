# Simple web messenger
**SimpleWebProject** is a web application consisting of multiple microservices, developed using FastAPI, PostgreSQL, and Docker. The project includes services for user authentication and chat between users.

## Description

**SimpleWebProject** is a web application consisting of multiple microservices, developed using FastAPI, PostgreSQL, and Docker. The project utilizes Event-Driven Microservice Architecture to facilitate communication between services. The components of the project include:

- **auth-service**: Handles user registration, authentication, and management.
- **chat-service**: Manages real-time communication between users using WebSocket.
- **Nginx**: Acts as a reverse proxy to route requests to the appropriate microservices.
- **RabbitMQ**: A message broker used for event-driven communication between services.

The event-driven approach allows for efficient, decoupled communication between services, making the system more scalable and resilient.

## Installation

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) must be installed on your machine.

### Cloning the Repository

git clone https://github.com/Crusazer/SimpleWebMessenger
cd SimpleWebProject

### Setting Up the Environment

1. **Configure Environment Variables**

   Create a `.env` file in the root of the project and add the necessary environment variables. Example:

2. **Start Docker Compose**
``` bash
make build make up
```

## Makefile Commands

- **Start Microservices**

  `make up`

- **Stop Microservices**

  `make down`

- **Build Docker Images**

  `make build`

- **View Logs**

  `make logs`

- **Apply Migrations for auth-service**

  `make migrate-auth`

- **Apply Migrations for chat-service**

  `make migrate-chat`

- **Run Tests**

  `make test`

- **Remove Containers and Data**

  `make clean`

