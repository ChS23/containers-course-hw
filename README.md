# Лабораторная работа 1: Dockerfile

Репозиторий содержит два Dockerfile для контейнеризации веб-приложения на Python (Litestar framework):
- `Dockerfile.bad` - с плохими практиками (но рабочий)
- `Dockerfile.good` - с исправленными практиками

## Приложение

Веб-приложение на базе Litestar framework для управления событиями и продажей билетов.

## Структура репозитория

```
.
├── Dockerfile.bad      # Плохой Dockerfile
├── Dockerfile.good     # Хороший Dockerfile
├── .dockerignore       # Исключения для Docker build
├── app/                # Исходный код приложения
├── pyproject.toml      # Зависимости проекта
└── uv.lock            # Lock-файл зависимостей
```

## Плохие практики в Dockerfile.bad

### 1. Использование тега `latest`

**Плохо:**
```dockerfile
FROM python:latest
```

**Почему плохо:**
- Непредсказуемость: `latest` может измениться в любой момент
- Нарушается воспроизводимость сборок
- Разные разработчики могут получить разные версии
- Проблемы при откате к предыдущей версии

**Как исправлено:**
```dockerfile
FROM python:3.12-slim-bookworm
```
- Конкретная версия Python (3.12)
- Конкретная версия Debian (bookworm)
- Slim-образ для уменьшения размера

---

### 2. Множественные RUN команды

**Плохо:**
```dockerfile
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get install -y vim
RUN apt-get install -y nano
RUN apt-get install -y git
RUN apt-get install -y build-essential
```

**Почему плохо:**
- Каждая RUN команда создает новый слой в образе
- Увеличивается итоговый размер образа
- Замедляется сборка
- Усложняется кэширование

**Как исправлено:**
```dockerfile
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*
```
- Одна RUN команда = один слой
- Очистка кэша APT в той же команде
- Установка только необходимых пакетов

---

### 3. Установка ненужных пакетов

**Плохо:**
```dockerfile
RUN apt-get install -y vim
RUN apt-get install -y nano
RUN apt-get install -y git
RUN apt-get install -y build-essential
```

**Почему плохо:**
- Увеличение размера образа
- Увеличение поверхности атаки (больше пакетов = больше уязвимостей)
- Нарушение принципа минимальности
- vim/nano не нужны в production контейнере

**Как исправлено:**
```dockerfile
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*
```
- Установлен только curl (нужен для HEALTHCHECK)
- git и build-essential не нужны (UV скачивает готовые wheels)

---

### 4. Отсутствие очистки кэша APT

**Плохо:**
```dockerfile
RUN apt-get update
RUN apt-get install -y curl
# кэш не очищается
```

**Почему плохо:**
- Кэш APT остается в образе
- Увеличение размера образа на десятки/сотни MB
- Лишние данные в production образе

**Как исправлено:**
```dockerfile
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*
```
- Очистка в той же RUN команде
- Кэш не попадает в финальный слой

---

### 5. Неправильный порядок COPY (плохое кэширование)

**Плохо:**
```dockerfile
WORKDIR /app
COPY . .
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN uv sync
```

**Почему плохо:**
- При изменении ЛЮБОГО файла кода инвалидируется кэш
- Зависимости переустанавливаются даже если не изменились
- Медленная пересборка при разработке

**Как исправлено:**
```dockerfile
# Сначала копируем только файлы зависимостей
COPY pyproject.toml uv.lock* ./

# Устанавливаем зависимости (кэшируется)
RUN uv sync --no-dev --frozen

# Потом копируем код
COPY . .
```
- Зависимости кэшируются отдельно
- Пересборка быстрее при изменении кода

---

### 6. Использование chmod 777 (критическая уязвимость)

**Плохо:**
```dockerfile
RUN chmod 777 /app/app/scripts/entry
RUN chmod 777 /app
```

**Почему плохо:**
- Полные права для всех пользователей (read, write, execute)
- Критическая уязвимость безопасности
- Любой процесс может изменить файлы
- Нарушение принципа наименьших привилегий

**Как исправлено:**
```dockerfile
RUN chmod +x /app/app/scripts/entry
```
- Только права на выполнение
- Владелец и группа остаются с минимальными правами

---

### 7. Установка dev-зависимостей в production

**Плохо:**
```dockerfile
RUN uv sync
```

**Почему плохо:**
- Устанавливаются dev-зависимости (pytest, linters, etc.)
- Увеличение размера образа
- Лишние пакеты в production
- Потенциальные уязвимости

**Как исправлено:**
```dockerfile
RUN uv sync --no-dev --frozen
```
- `--no-dev`: только production зависимости
- `--frozen`: использовать lock-файл без изменений

---

### 8. Отсутствие EXPOSE

**Плохо:**
```dockerfile
# EXPOSE отсутствует
```

**Почему плохо:**
- Неясно какой порт использует приложение
- Плохая документация
- Проблемы с автоматическим обнаружением портов

**Как исправлено:**
```dockerfile
EXPOSE 8000
```
- Явное указание используемого порта
- Самодокументирование

---

## Сравнение размеров образов

```bash
# Плохой образ
docker build -f Dockerfile.bad -t app:bad .
# REPOSITORY   TAG       SIZE
# app          bad       ~1.2GB

# Хороший образ
docker build -f Dockerfile.good -t app:good .
# REPOSITORY   TAG       SIZE
# app          good      ~450MB
```

Разница: **~750MB** (в 2.5+ раза меньше)

---

# Лабораторная работа 2: Docker Compose

## Описание композ-файла

Docker Compose проект состоит из 4 сервисов:
- **app-init** - одноразовый init-контейнер для инициализации БД
- **app** - основное приложение (Litestar API)
- **postgres** - база данных PostgreSQL
- **redis** - кэш Redis

### Архитектура

```
┌─────────────┐
│  app-init   │ (один раз)
│  (init DB)  │
└──────┬──────┘
       │ depends_on
       ▼
┌─────────────┐     ┌──────────────┐
│  postgres   │────▶│     app      │
│  (database) │     │ (Litestar)   │
└─────────────┘     └──────┬───────┘
                           │
┌─────────────┐            │
│    redis    │◀───────────┘
│   (cache)   │
└─────────────┘
```

## Разбор docker-compose.yml

### Сервис: app-init (Init Container)

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
  command: ["bash", "-c", "python -m app.db.init_db && echo 'Database initialized successfully'"]
  restart: "no"
```

**Назначение:** Одноразовая инициализация базы данных (создание таблиц, схемы).

**Ключевые особенности:**
- ✅ **build** - автоматическая сборка из Dockerfile.good
- ✅ **image: event-app:latest** - присвоение имени образу
- ✅ **container_name** - жесткое именование контейнера
- ✅ **depends_on** - ждет готовности postgres (condition: service_healthy)
- ✅ **command** - кастомная команда для инициализации БД
- ✅ **restart: "no"** - не перезапускается (одноразовый)
- ✅ **networks** - подключен к event-network

---

### Сервис: app (Main Application)

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

**Ключевые особенности:**
- ✅ **build + image** - сборка из Dockerfile и именование
- ✅ **container_name** - жесткое имя
- ✅ **ports** - проброс порта 8000 наружу
- ✅ **volumes** - монтирование volume для логов
- ✅ **depends_on** - зависит от postgres, redis, app-init
  - Ждет `service_healthy` для БД и кэша
  - Ждет `service_completed_successfully` для init
- ✅ **healthcheck** - проверка здоровья приложения
- ✅ **entrypoint** - кастомная точка входа
- ✅ **env_file** - все переменные из .env
- ✅ **networks** - подключен к event-network

---

### Сервис: postgres (Database)

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

**Назначение:** База данных PostgreSQL для хранения данных.

**Ключевые особенности:**
- ✅ **image** - готовый образ postgres:16-alpine
- ✅ **container_name** - жесткое именование
- ✅ **environment** - env-переменные из .env файла
- ✅ **ports** - проброс порта 5432
- ✅ **volumes** - персистентное хранилище данных
- ✅ **healthcheck** - проверка готовности БД через pg_isready
- ✅ **logging** - ротация логов (max 10MB, 3 файла)
- ✅ **networks** - подключен к event-network

---

### Сервис: redis (Cache)

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
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

**Назначение:** Redis для кэширования данных и сессий.

**Ключевые особенности:**
- ✅ **image** - готовый образ redis:7-alpine
- ✅ **container_name** - жесткое именование
- ✅ **ports** - проброс порта 6379
- ✅ **volumes** - персистентное хранилище для AOF
- ✅ **command** - кастомная команда с AOF persistence и паролем
- ✅ **healthcheck** - проверка через redis-cli ping
- ✅ **networks** - подключен к event-network

---

### Networks

```yaml
networks:
  event-network:
    driver: bridge
    name: event-network
```

**Назначение:** Изолированная сеть для всех сервисов.

**Особенности:**
- ✅ **Явное указание network** - все сервисы в одной сети
- Сервисы обращаются друг к другу по именам (postgres, redis, app)
- Изоляция от других Docker сетей

---

### Volumes

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

**Назначение:** Персистентное хранилище данных.

**Особенности:**
- **postgres-data** - данные БД сохраняются между перезапусками
- **redis-data** - AOF файлы Redis
- **app-logs** - логи приложения
- ✅ **Явное именование volumes**

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
# Отредактируйте .env и установите безопасные пароли
```

---

## Запуск проекта

### 1. Первый запуск

```bash
# Создайте .env файл
cp .env.example .env
nano .env  # Измените пароли

# Запустите все сервисы
docker-compose up -d

# Проверьте статус
docker-compose ps
```

### 2. Просмотр логов

```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f app
docker-compose logs -f postgres

# Init контейнер
docker-compose logs app-init
```

### 3. Проверка health status

```bash
# Все сервисы
docker-compose ps

# Конкретный сервис
docker inspect event-app --format='{{.State.Health.Status}}'
docker inspect event-postgres --format='{{.State.Health.Status}}'
```

### 4. Остановка и очистка

```bash
# Остановить все
docker-compose down

# Остановить + удалить volumes
docker-compose down -v

# Пересобрать образы
docker-compose build --no-cache
docker-compose up -d
```

---

## Ответы на вопросы

### Вопрос 1: Можно ли ограничивать ресурсы (память, CPU) для сервисов в docker-compose.yml?

**Ответ: Да, можно.**

Docker Compose поддерживает ограничение ресурсов через ключи `deploy.resources` (Docker Swarm mode) или напрямую через `mem_limit`, `cpus` (Docker Compose v2).

**Пример для Docker Compose v3+:**

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

**Пример для Docker Compose v2 (legacy):**

```yaml
services:
  app:
    image: event-app:latest
    mem_limit: 1g          # Максимум 1GB RAM
    cpus: 2.0              # Максимум 2 CPU cores
    mem_reservation: 512m  # Гарантированно 512MB
```

**Важные нюансы:**

1. **deploy.resources работает только в Docker Swarm mode**
   - Для локальной разработки нужно использовать `docker-compose --compatibility up`
   
2. **Для production рекомендуется Kubernetes** для более гибкого управления ресурсами

3. **Ограничение I/O операций:**
```yaml
services:
  postgres:
    image: postgres:16-alpine
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
    # Ограничение дисковых операций
    blkio_config:
      weight: 500
      device_read_bps:
        - path: /dev/sda
          rate: '50mb'
```

---

### Вопрос 2: Как запустить только определенный сервис из docker-compose.yml?

**Ответ: Используйте команду `docker-compose up` с указанием имени сервиса.**

**1. Запустить один сервис без зависимостей:**

```bash
docker-compose up postgres --no-deps
```

- `--no-deps` - не запускать зависимые сервисы

**2. Запустить один сервис С зависимостями:**

```bash
docker-compose up app
```

Автоматически запустятся:
- `postgres` (зависимость app)
- `redis` (зависимость app)
- `app-init` (зависимость app)
- `app` (основной сервис)

**3. Запустить несколько конкретных сервисов:**

```bash
docker-compose up postgres redis
```

**4. Запустить сервис в фоне:**

```bash
docker-compose up -d app
```

**5. Остановить конкретный сервис:**

```bash
docker-compose stop app
```

**6. Перезапустить конкретный сервис:**

```bash
docker-compose restart app
```

**7. Выполнить команду в работающем сервисе:**

```bash
docker-compose exec app bash
docker-compose exec postgres psql -U event_user -d event_management
```

**8. Одноразовое выполнение команды:**

```bash
docker-compose run --rm app python -m app.db.init_db
```

- `--rm` - удалить контейнер после выполнения

**Полезные комбинации:**

```bash
# Только БД и Redis (без приложения)
docker-compose up -d postgres redis

# Только init контейнер
docker-compose up app-init

# Пересобрать и запустить только app
docker-compose up -d --build app

# Просмотр логов конкретного сервиса
docker-compose logs -f app
```

---

## Диаграмма зависимостей

```
Порядок запуска:
1. postgres, redis (параллельно)
   ↓ (ждем service_healthy)
2. app-init
   ↓ (ждем service_completed_successfully)
3. app
```

**Dependency Graph:**
```
┌──────────┐
│ postgres │ (service_healthy)
└────┬─────┘
     │
     ├──────────────┐
     │              │
     ▼              ▼
┌──────────┐   ┌──────────┐
│   redis  │   │ app-init │
│(healthy) │   │(complete)│
└────┬─────┘   └────┬─────┘
     │              │
     └──────┬───────┘
            ▼
       ┌────────┐
       │  app   │
       └────────┘
```

---

## Проверка соответствия требованиям

| Требование | Статус | Где реализовано |
|-----------|--------|-----------------|
| Минимум 1 init + 2 app сервиса | ✅ | app-init + app + postgres + redis |
| Автоматическая сборка из Dockerfile | ✅ | `build: {context: ., dockerfile: Dockerfile.good}` |
| Присвоение имени образу | ✅ | `image: event-app:latest` |
| Жесткое именование контейнеров | ✅ | `container_name: event-app` и т.д. |
| Минимум один с depends_on | ✅ | app зависит от postgres, redis, app-init |
| Минимум один с volume | ✅ | postgres, redis, app имеют volumes |
| Минимум один с портом | ✅ | app (8000), postgres (5432), redis (6379) |
| Минимум один с command/entrypoint | ✅ | app (entrypoint), app-init (command), redis (command) |
| Healthcheck | ✅ | app, postgres, redis |
| Env-ы в .env файле | ✅ | `env_file: .env` |
| Явно указана network | ✅ | `event-network` для всех сервисов |

---

## Troubleshooting

### Проблема: app не стартует

```bash
# Проверьте логи
docker-compose logs app

# Проверьте, что БД готова
docker-compose logs postgres

# Перезапустите init
docker-compose up app-init
```

### Проблема: порты заняты

```bash
# Найдите процесс на порту
sudo lsof -i :8000
sudo lsof -i :5432

# Убейте процесс или измените порт в docker-compose.yml
```

### Проблема: volumes не очищаются

```bash
# Удалите все volumes
docker-compose down -v

# Или вручную
docker volume rm event-postgres-data event-redis-data event-app-logs
```

---

## Заключение

Docker Compose позволяет:
- Описать всю инфраструктуру в одном файле
- Запускать многоконтейнерные приложения одной командой
- Управлять зависимостями между сервисами
- Легко масштабировать и переносить окружение

Готовый проект можно развернуть на любой машине с Docker за минуту!
