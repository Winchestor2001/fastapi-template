
# 🚀 FastAPI Project Template

A modular FastAPI project template ready for production deployment, CI/CD integration, Celery tasks, and third-party service integrations.

---

## 📁 Project Structure

```bash
app/
├── __init__.py
├── main.py                # Entry point
├── core/                  # Shared business logic, enums, utils
├── users/                 # Users module (auth, user management)
├── websocket/             # WebSocket API module
├── database/              # DB connection, models, repositories
├── integrations/          # External service integrations (S3, Firebase, etc.)
├── api/                   # Global dependencies, middleware, routes
├── celery_tasks/          # Celery background tasks
├── loggers/               # Logging configuration
tests/
├── unit/                  # Unit tests
├── integration/           # Integration tests
migrations/                # Alembic migrations
scripts/                   # CLI helper scripts
```

---

## 🛠 Technologies Used

- **FastAPI** — main backend framework
- **SQLAlchemy** + Alembic — database ORM and migrations
- **Pydantic** — data validation and serialization
- **PostgreSQL** (default)
- **Redis** — caching and Celery backend
- **Celery** — background tasks and async processing
- **Docker** + Docker Compose — containerization and orchestration
- **Nginx** — reverse proxy server
- **pytest + coverage** — testing and code coverage
- **pre-commit** — automatic checks before commits
- **GitHub Actions / CI (optional)** — continuous integration and automation

---

## ⚙️ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-org/fastapi-template.git
cd fastapi-template
```

### 2. Copy and configure the `.env` file

```bash
cp .env.example .env
```

### 3. Build and run the containers

```bash
docker-compose up --build
```

### 4. Run database migrations

```bash
docker-compose exec backend alembic upgrade head
```

---

## 🧪 Testing

### Run all tests with coverage

```bash
pytest --cov=app --cov-config=.coveragerc
```

### Generate HTML coverage report

```bash
coverage html
open coverage_html_report/index.html  # macOS / use your system’s equivalent
```

---

## 📦 Makefile

A `Makefile` is provided to simplify common operations:

```bash
make build         # docker-compose build
make up            # docker-compose up
make down          # docker-compose down
make migrate       # alembic upgrade head
make test          # run tests
make lint          # run linters
```

---

## 🧱 Architecture

This project uses a **domain-based modular structure**:

- Each business domain is located in its own folder (e.g. `users`, `websocket`, etc.)
- Inside each domain: models, schemas, services, repositories, routers
- Shared and infrastructure modules are placed in `core/`, `integrations/`, `database/`, `api/`

> This modular structure allows for easier scaling and separation of concerns.

---

## 🔌 Integrations

The `integrations/` folder contains connections to external services:

- `firebase/` — Firebase SDK integration
- `aws/` — Amazon S3 support
- `redis/` — Redis client
- `payments/`, `sms/` — external service providers

---

## 🚀 Deployment

This project is production-ready and containerized:

- Use a separate `.env.production` file for production environments
- Nginx is preconfigured as a reverse proxy to FastAPI
- Celery can be launched via a separate worker container

---

## 💡 TODO (customizable per project)

- [ ] Configure CI/CD (GitHub Actions, GitLab CI, etc.)
- [ ] Add OpenAPI authentication
- [ ] Integrate monitoring tools (Sentry, Prometheus)
- [ ] Implement role-based access control (RBAC)
- [ ] Enable Swagger token-based authorization
- [ ] Add basic tests (healthcheck, authentication, user flows)

---

## 🧙 Tips for Using the Template

- Copy the `users/` module to scaffold new domains (e.g. `orders/`)
- Use `core/` only for truly shared business logic
- Keep all external service clients in `integrations/`
- Don’t forget to enable `pre-commit` and format your code

---

## 📎 License

MIT. Free to use, fork, extend and build awesome projects.
