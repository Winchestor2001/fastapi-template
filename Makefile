# Docker settings
DOCKER_COMPOSE = docker compose
DOCKER_COMPOSE_RUN = $(DOCKER_COMPOSE) run --rm
DOCKER_COMPOSE_EXEC = $(DOCKER_COMPOSE) exec

# Container names
EXPRESSO_CONTAINER = project_name
CELERY_CONTAINER = celery_tasks
POSTGRES_CONTAINER = postgres
REDIS_CONTAINER = redis

# Build Docker containers
.PHONY: build
build:
	$(DOCKER_COMPOSE) build

# Up Docker containers
.PHONY: up
up:
	$(DOCKER_COMPOSE) up -d

# Run Docker containers
.PHONY: run
run:
	$(DOCKER_COMPOSE) up --build -d

# Stop the Docker containers
.PHONY: down
down:
	$(DOCKER_COMPOSE) down

# Restart containers
.PHONY: restart
restart:
	$(DOCKER_COMPOSE) restart

# Remove volumes and clean up
.PHONY: clean
clean:
	$(DOCKER_COMPOSE) down -v --rmi local --remove-orphans

# Alembic: Create a new migration
.PHONY: migration
migration:
	$(DOCKER_COMPOSE_EXEC) $(EXPRESSO_CONTAINER) alembic revision --autogenerate --message "$(message)"

# Alembic: Apply migrations
.PHONY: migrate
migrate:
	$(DOCKER_COMPOSE_EXEC) $(EXPRESSO_CONTAINER) alembic upgrade head

# Start the Celery worker
.PHONY: celery-worker
celery-worker:
	$(DOCKER_COMPOSE) up -d $(CELERY_CONTAINER)

# Stop Celery worker
.PHONY: stop-celery
stop-celery:
	$(DOCKER_COMPOSE) stop $(CELERY_CONTAINER)

# Execute a bash shell inside the Expresso container
.PHONY: shell
shell:
	$(DOCKER_COMPOSE_EXEC) $(EXPRESSO_CONTAINER) /bin/bash

# View logs for all services
.PHONY: logs
logs:
	$(DOCKER_COMPOSE) logs -f

.PHONY: logs-celery
logs-celery:
	$(DOCKER_COMPOSE) logs -f $(CELERY_CONTAINER)

.PHONY: logs-postgres
logs-postgres:
	$(DOCKER_COMPOSE) logs -f $(POSTGRES_CONTAINER)

# Sleep command
.PHONY: pause
pause:
	sleep 5

# First run: Build, up, apply migrations
.PHONY: first-run
first-run: build up pause migration pause migrate pause