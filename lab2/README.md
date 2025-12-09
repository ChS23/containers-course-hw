# Лабораторная работа 2: Docker Compose

## Описание задания

Создать docker-compose.yml из минимум трёх сервисов на основе Dockerfile из ЛР1.

## Файлы

- [`compose.yml`](../compose.yml) — Docker Compose конфигурация
- [`.env.example`](../.env.example) — пример файла переменных окружения
- [`Dockerfile.good`](../Dockerfile.good) — Dockerfile для сборки приложения

---

## Архитектура проекта

```
┌─────────────────────────────────────────────────────────────┐
│                      event-network                          │
│                                                             │
│  ┌─────────────┐                                            │
│  │  app-init   │ (одноразовый)                              │
│  │  init DB    │                                            │
│  └──────┬──────┘                                            │
│         │ depends_on (service_healthy)                      │
│         ▼                                                   │
│  ┌─────────────┐     ┌──────────────┐     ┌─────────────┐  │
│  │  postgres   │────▶│     app      │◀────│    redis    │  │
│  │  :5432      │     │    :8000     │     │    :6379    │  │
│  └─────────────┘     └──────────────┘     └─────────────┘  │
│         │                   │                    │          │
│         ▼                   ▼                    ▼          │
│  [postgres-data]      [app-logs]          [redis-data]     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Порядок запуска:**
1. `postgres` и `redis` запускаются параллельно
2. После `service_healthy` запускается `app-init`
3. После `service_completed_successfully` запускается `app`

---

## Описание сервисов

### 1. app-init (Init Container)

```yaml
app-init:
  build:
    context: .
    dockerfile: Dockerfile.good
  image: event-app:latest
  container_name: event-app-init
  env_file: .env
  depends_on:
    postgres:
      condition: service_healthy
  networks:
    - event-network
  entrypoint: ["uv", "run", "litestar", "database", "upgrade", "--no-prompt"]
  restart: "no"
```

**Назначение:** Одноразовый запуск миграций БД через Litestar CLI (Alembic под капотом).

| Ключ | Значение | Описание |
|------|----------|----------|
| `build` | `Dockerfile.good` | Сборка из хорошего Dockerfile |
| `image` | `event-app:latest` | Имя собранного образа |
| `container_name` | `event-app-init` | Жёсткое имя контейнера |
| `depends_on` | `postgres: service_healthy` | Ждёт готовности БД |
| `entrypoint` | `litestar database upgrade --no-prompt` | Миграции БД (Alembic) |
| `restart` | `"no"` | Не перезапускается (одноразовый) |

---

### 2. app (Main Application)

```yaml
app:
  build:
    context: .
    dockerfile: Dockerfile.good
  image: event-app:latest
  container_name: event-app
  env_file: .env
  ports:
    - "8000:8000"
  volumes:
    - app-logs:/app/logs
  depends_on:
    postgres:
      condition: service_healthy
    redis:
      condition: service_healthy
    app-init:
      condition: service_completed_successfully
  networks:
    - event-network
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 40s
  restart: unless-stopped
  entrypoint: ["bash", "/app/app/scripts/entry"]
```

**Назначение:** Основное веб-приложение на Litestar.

| Ключ | Значение | Описание |
|------|----------|----------|
| `ports` | `8000:8000` | Проброс порта наружу |
| `volumes` | `app-logs:/app/logs` | Volume для логов |
| `depends_on` | postgres, redis, app-init | Зависимости с условиями |
| `healthcheck` | `curl /health` | Проверка здоровья |
| `entrypoint` | `bash /app/app/scripts/entry` | Точка входа |

---

### 3. postgres (Database)

```yaml
postgres:
  image: postgres:16-alpine
  container_name: event-postgres
  env_file: .env
  environment:
    - POSTGRES_DB=${POSTGRES_DB}
    - POSTGRES_USER=${POSTGRES_USER}
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
  ports:
    - "5432:5432"
  volumes:
    - postgres-data:/var/lib/postgresql/data
  networks:
    - event-network
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
    interval: 10s
    timeout: 5s
    retries: 5
    start_period: 30s
  restart: unless-stopped
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

**Назначение:** База данных PostgreSQL.

| Ключ | Значение | Описание |
|------|----------|----------|
| `image` | `postgres:16-alpine` | Официальный образ PostgreSQL |
| `environment` | из `.env` | Конфигурация БД |
| `volumes` | `postgres-data` | Персистентное хранилище |
| `healthcheck` | `pg_isready` | Проверка готовности БД |
| `logging` | max 10MB x 3 files | Ротация логов |

---

### 4. redis (Cache)

```yaml
redis:
  image: redis:7-alpine
  container_name: event-redis
  ports:
    - "6379:6379"
  volumes:
    - redis-data:/data
  networks:
    - event-network
  command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
  healthcheck:
    test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 30s
  restart: unless-stopped
```

**Назначение:** Redis для кэширования.

| Ключ | Значение | Описание |
|------|----------|----------|
| `command` | `redis-server --appendonly yes` | AOF persistence + пароль |
| `volumes` | `redis-data:/data` | Персистентность данных |
| `healthcheck` | `redis-cli ping` | Проверка доступности |

---

## Networks

```yaml
networks:
  event-network:
    driver: bridge
    name: event-network
```

- Все сервисы в одной изолированной сети
- Сервисы обращаются друг к другу по именам (`postgres`, `redis`, `app`)
- Bridge driver — стандартный для single-host

---

## Volumes

```yaml
volumes:
  postgres-data:
    driver: local
    name: event-postgres-data
  redis-data:
    driver: local
    name: event-redis-data
  app-logs:
    driver: local
    name: event-app-logs
```

| Volume | Назначение |
|--------|------------|
| `postgres-data` | Данные БД (таблицы, индексы) |
| `redis-data` | AOF файлы Redis |
| `app-logs` | Логи приложения |

---

## Переменные окружения (.env)

```bash
# PostgreSQL
POSTGRES_DB=event_management
POSTGRES_USER=event_user
POSTGRES_PASSWORD=secure_password_123
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_PASSWORD=redis_password_123
REDIS_HOST=redis
REDIS_PORT=6379

# Application
APP_ENV=production
APP_PORT=8000
DEBUG=false
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO
```

**Важно:** Скопируйте `.env.example` в `.env` и измените пароли!

```bash
cp .env.example .env
```

---

## Запуск проекта

### Первый запуск

```bash
# Создать .env
cp .env.example .env

# Запустить все сервисы
docker compose up -d

# Проверить статус
docker compose ps
```

### Просмотр логов

```bash
# Все сервисы
docker compose logs -f

# Конкретный сервис
docker compose logs -f app
docker compose logs -f postgres
```

### Остановка

```bash
# Остановить
docker compose down

# Остановить + удалить volumes
docker compose down -v
```

---

## Ответы на вопросы

### Вопрос 1: Можно ли ограничивать ресурсы (память, CPU) для сервисов в docker-compose.yml?

**Ответ: Да, можно.**

#### Способ 1: deploy.resources (Docker Compose v3+)

```yaml
services:
  app:
    image: event-app:latest
    deploy:
      resources:
        limits:
          cpus: '2.0'        # Максимум 2 CPU cores
          memory: 1024M      # Максимум 1GB RAM
        reservations:
          cpus: '0.5'        # Гарантированно 0.5 CPU
          memory: 512M       # Гарантированно 512MB RAM
```

**Важно:** `deploy.resources` полноценно работает только в Docker Swarm mode. Для обычного Docker Compose нужно запускать с флагом:

```bash
docker compose --compatibility up -d
```

#### Способ 2: Прямые ключи (Docker Compose v2)

```yaml
services:
  app:
    image: event-app:latest
    mem_limit: 1g
    cpus: 2.0
    mem_reservation: 512m
```

#### Ограничение I/O

```yaml
services:
  postgres:
    image: postgres:16-alpine
    blkio_config:
      weight: 500
      device_read_bps:
        - path: /dev/sda
          rate: '50mb'
```

---

### Вопрос 2: Как запустить только определенный сервис из docker-compose.yml?

**Ответ: Указать имя сервиса в команде `docker compose up`.**

#### Запуск одного сервиса БЕЗ зависимостей

```bash
docker compose up postgres --no-deps
```

- `--no-deps` — не запускать сервисы, от которых зависит postgres

#### Запуск одного сервиса С зависимостями

```bash
docker compose up app
```

Автоматически запустятся: `postgres` → `redis` → `app-init` → `app`

#### Запуск нескольких сервисов

```bash
docker compose up postgres redis
```

#### Запуск в фоне

```bash
docker compose up -d app
```

#### Остановка конкретного сервиса

```bash
docker compose stop app
```

#### Перезапуск конкретного сервиса

```bash
docker compose restart app
```

#### Выполнение команды в работающем контейнере

```bash
docker compose exec app bash
docker compose exec postgres psql -U event_user -d event_management
```

#### Одноразовый запуск команды

```bash
docker compose run --rm app python -m app.db.init_db
```

- `--rm` — удалить контейнер после выполнения

---

## Чек-лист соответствия требованиям

| Требование | Статус | Где реализовано |
|------------|--------|-----------------|
| Минимум 1 init + 2 app сервиса | ✅ | app-init + app + postgres + redis |
| Автоматическая сборка из Dockerfile | ✅ | `build: { dockerfile: Dockerfile.good }` |
| Присвоение имени образу | ✅ | `image: event-app:latest` |
| Жёсткое именование контейнеров | ✅ | `container_name: event-app` и т.д. |
| Минимум один с depends_on | ✅ | app, app-init зависят от postgres/redis |
| Минимум один с volume | ✅ | postgres, redis, app имеют volumes |
| Минимум один с портом | ✅ | app (8000), postgres (5432), redis (6379) |
| Минимум один с command/entrypoint | ✅ | app (entrypoint), app-init (command), redis (command) |
| Healthcheck | ✅ | app, postgres, redis |
| Env-ы в .env файле | ✅ | `env_file: .env` |
| Явно указана network | ✅ | `event-network` для всех сервисов |
