## Запуск проекта

### Требования

- [Docker](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/)

### Настройка

1. Клонируйте репозиторий:

   ```bash
   git clone https://github.com/kooflixy/korum.git
   cd korum
   ```

2. Создайте файл `.env` на основе примера:

   ```bash
   cp .env.example .env
   ```

3. При необходимости измените переменные окружения в `.env`.

4. Сгенерируйте RSA-ключи для JWT:

   ```bash
   python scripts/generate_keys.py
   ```

### Запуск

Соберите и запустите контейнеры:

```bash
docker compose up -d --build
```

При запуске контейнера backend автоматически выполняются миграции Alembic, после чего запускается FastAPI-приложение.

### Доступные сервисы

| Сервис | Адрес |
|---|---|
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| MinIO Console | http://localhost:9001 |

### Полезные команды

```bash
# Запустить проект
docker compose up -d

# Пересобрать образы и запустить проект
docker compose up -d --build

# Посмотреть логи всех сервисов
docker compose logs -f

# Посмотреть логи backend
docker compose logs -f backend

# Остановить контейнеры
docker compose down

# Остановить контейнеры и удалить данные PostgreSQL и MinIO
docker compose down -v
```

> **Важно:** команда `docker compose down -v` удаляет Docker volumes, содержащие данные PostgreSQL и MinIO. Используйте её только при необходимости сбросить данные.