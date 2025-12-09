# Лабораторная работа 4: Kubernetes

## Описание задания

Развернуть собственный сервис event-app в Kubernetes (minikube) с использованием:
- Минимум 2 Deployment + 1 init-контейнер
- Кастомный образ для минимум одного Deployment
- Минимум один Deployment с init-контейнером и volume
- ConfigMap и/или Secret
- Service для минимум одного сервиса
- Liveness/Readiness probes
- Labels

## Файлы манифестов

```
lab4/manifests/
├── postgres-configmap.yml    # ConfigMap для PostgreSQL
├── postgres-secret.yml       # Secret для PostgreSQL (USER, PASSWORD)
├── postgres-pvc.yml          # PersistentVolumeClaim для данных БД
├── postgres-service.yml      # Service для PostgreSQL
├── postgres-deployment.yml   # Deployment PostgreSQL с volume
├── redis-service.yml         # Service для Redis
├── redis-deployment.yml      # Deployment Redis
├── app-configmap.yml         # ConfigMap для приложения
├── app-secret.yml            # Secret для приложения (DSN, ключи)
├── app-service.yml           # Service (NodePort) для приложения
└── app-deployment.yml        # Deployment с init-контейнером
```

---

## Ход работы

### Часть 1. Подготовка образа

```bash
# Сборка образа внутри minikube
eval $(minikube docker-env)
docker build -f Dockerfile.good -t event-app:latest .
```

### Часть 2. Применение манифестов

**Порядок применения манифестов:**

```bash
# Способ 1: Применить всё сразу
kubectl apply -f lab4/manifests/

# Способ 2: По порядку зависимостей
# 1. ConfigMaps и Secrets (независимые ресурсы)
kubectl apply -f lab4/manifests/postgres-configmap.yml
kubectl apply -f lab4/manifests/postgres-secret.yml
kubectl apply -f lab4/manifests/postgres-pvc.yml
kubectl apply -f lab4/manifests/app-configmap.yml
kubectl apply -f lab4/manifests/app-secret.yml

# 2. Services (создают DNS-записи)
kubectl apply -f lab4/manifests/postgres-service.yml
kubectl apply -f lab4/manifests/redis-service.yml
kubectl apply -f lab4/manifests/app-service.yml

# 3. Deployments (используют ConfigMaps, Secrets, Services)
kubectl apply -f lab4/manifests/postgres-deployment.yml
kubectl apply -f lab4/manifests/redis-deployment.yml
kubectl apply -f lab4/manifests/app-deployment.yml
```

### Часть 3. Проверка ресурсов

```bash
# Просмотр всех ресурсов
kubectl get all

# Просмотр подов
kubectl get pods

# Просмотр ConfigMaps
kubectl get configmaps

# Просмотр Secrets
kubectl get secrets

# Просмотр Services
kubectl get services

# Просмотр PVC
kubectl get pvc

# Детальная информация о поде
kubectl describe pod <pod-name>

# Логи пода
kubectl logs <pod-name>

# Логи init-контейнера
kubectl logs <pod-name> -c db-migrate
```

### Часть 4. Доступ к приложению

```bash
# Получить URL сервиса
minikube service event-app-service --url

# Проверка health endpoints
curl http://<url>/health/
curl http://<url>/health/ready

# Проверка API
curl http://<url>/api/v1/events
```

---

## Выполненные требования

| Требование | Статус | Где реализовано |
|------------|--------|-----------------|
| Минимум 2 Deployment | ✅ | postgres, redis, event-app |
| Init-контейнер | ✅ | app-deployment.yml (db-migrate) |
| Кастомный образ | ✅ | event-app:latest |
| Volume | ✅ | postgres-pvc.yml |
| ConfigMap | ✅ | postgres-configmap.yml, app-configmap.yml |
| Secret | ✅ | postgres-secret.yml, app-secret.yml |
| Service | ✅ | postgres-service, redis-service, event-app-service |
| Liveness probe | ✅ | Все 3 Deployment |
| Readiness probe | ✅ | Все 3 Deployment |
| Labels | ✅ | app, tier на всех ресурсах |

---

## Архитектура решения

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Kubernetes Cluster                             │
│                                                                         │
│  ┌─────────────────┐         ┌─────────────────────┐                   │
│  │ postgres-secret │         │    app-secret       │                   │
│  │  USER, PASSWORD │         │ DSN, SECRET_KEY,... │                   │
│  └────────┬────────┘         └──────────┬──────────┘                   │
│           │                             │                               │
│  ┌────────┴────────┐         ┌──────────┴──────────┐                   │
│  │postgres-configmap│        │  app-configmap      │                   │
│  │   POSTGRES_DB   │         │ HOST, PORT, ENV,... │                   │
│  └────────┬────────┘         └──────────┬──────────┘                   │
│           │                             │                               │
│  ┌────────┴────────┐         ┌──────────┴──────────┐  ┌─────────────┐  │
│  │    postgres     │         │     event-app       │  │    redis    │  │
│  │   Deployment    │◄────────│    Deployment       │──►  Deployment │  │
│  │   (1 replica)   │         │   (1 replica)       │  │  (1 replica)│  │
│  │   + PVC volume  │         │ + init: db-migrate  │  │             │  │
│  │   + probes      │         │ + probes            │  │  + probes   │  │
│  └────────┬────────┘         └──────────┬──────────┘  └──────┬──────┘  │
│           │                             │                     │         │
│  ┌────────┴────────┐         ┌──────────┴──────────┐  ┌──────┴──────┐  │
│  │ postgres-service│         │ event-app-service   │  │redis-service│  │
│  │  (ClusterIP)    │         │    (NodePort)       │  │ (ClusterIP) │  │
│  │    :5432        │         │     :8000           │  │   :6379     │  │
│  └─────────────────┘         └──────────┬──────────┘  └─────────────┘  │
│                                         │                               │
└─────────────────────────────────────────┼───────────────────────────────┘
                                          │
                                          ▼
                              minikube service event-app-service
```

---

## Ключевые особенности

### 1. Init-контейнер для миграций БД

```yaml
initContainers:
- name: db-migrate
  image: event-app:latest
  imagePullPolicy: Never
  command: ["uv", "run", "litestar", "database", "upgrade", "--no-prompt"]
  envFrom:
  - configMapRef:
      name: app-configmap
  - secretRef:
      name: app-secret
```

Init-контейнер запускается **до** основного контейнера и выполняет миграции базы данных. Это гарантирует, что БД готова к работе до старта приложения.

### 2. PersistentVolumeClaim для PostgreSQL

```yaml
volumes:
- name: postgres-storage
  persistentVolumeClaim:
    claimName: postgres-pvc
```

PVC обеспечивает сохранность данных PostgreSQL даже при перезапуске подов.

### 3. Liveness и Readiness probes

**PostgreSQL:**
```yaml
livenessProbe:
  exec:
    command: ["pg_isready", "-U", "event_user", "-d", "event_management"]
```

**Redis:**
```yaml
livenessProbe:
  exec:
    command: ["redis-cli", "ping"]
```

**Event-app (HTTP):**
```yaml
livenessProbe:
  httpGet:
    path: /health/
    port: 8000
readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
```

### 4. Labels для организации ресурсов

Все ресурсы имеют labels для удобной группировки:
- `app: postgres/redis/event-app` - идентификация приложения
- `tier: database/cache/backend` - уровень архитектуры

---

## Полезные команды

```bash
# Масштабирование
kubectl scale deployment event-app --replicas=3

# Перезапуск deployment
kubectl rollout restart deployment event-app

# Просмотр событий
kubectl get events --sort-by='.lastTimestamp'

# Выполнение команды в поде
kubectl exec -it <pod-name> -- bash

# Port-forward для отладки
kubectl port-forward service/event-app-service 8000:8000

# Удаление всех ресурсов lab4
kubectl delete -f lab4/manifests/
```
