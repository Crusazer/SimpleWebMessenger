# Variables
DOCKER_COMPOSE = docker compose -f docker/docker-compose.yaml

# Commands
up:
	$(DOCKER_COMPOSE) up
down:
	$(DOCKER_COMPOSE) down
build:
	$(DOCKER_COMPOSE) build
logs:
	$(DOCKER_COMPOSE) logs -f
# Migration commands
migrate-auth:
	docker-compose exec auth-service alembic upgrade head
migrate-chat:
	docker-compose exec chat-service alembic upgrade head

# Commands for test
test:
	pytest

# Commands for delete data
clean:
	$(DOCKER_COMPOSE) down --volumes --remove-orphans