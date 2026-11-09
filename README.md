# Django REST Framework Project

REST API для образовательной платформы на Django REST Framework.

## Возможности проекта

- Регистрация и авторизация пользователей через JWT.
- Управление профилем пользователя.
- Создание и просмотр курсов.
- Создание и просмотр уроков.
- Подписка пользователей на курсы.
- Создание платежей через Stripe.
- Фоновые задачи с помощью Celery.
- Кэширование с помощью Redis.
- Документация API через Swagger и OpenAPI.
- PostgreSQL в качестве базы данных.
- Docker Compose для запуска проекта.

## Технологии

- Python 3.14
- Django
- Django REST Framework
- PostgreSQL
- Redis
- Celery
- Stripe
- Simple JWT
- drf-spectacular
- Docker
- Docker Compose
- Poetry

## Запуск проекта через Docker

### 1. Клонирование репозитория

```bash
git clone <URL-РЕПОЗИТОРИЯ>
cd django_drf_project
```

### 2. Настройка переменных окружения

Создайте файл `.env` на основе примера:

```bash
cp .env.example .env
```

Откройте `.env` и укажите свои значения:

- `SECRET_KEY` — секретный ключ Django.
- `DB_NAME` — имя базы данных.
- `DB_USER` — пользователь PostgreSQL.
- `DB_PASSWORD` — пароль PostgreSQL.
- `STRIPE_SECRET_KEY` — секретный ключ Stripe (для работы платежей).

Не публикуйте файл `.env` и не добавляйте его в Git.

### 3. Запуск контейнеров

```bash
docker compose up --build -d
```

Команда собирает Docker-образы и запускает контейнеры в фоновом режиме.

### 4. Проверка контейнеров

```bash
docker compose ps
```

### 5. Выполнение тестов

```bash
docker compose exec web python manage.py test
```

### 6. Остановка контейнеров

```bash
docker compose down
```

Для остановки с удалением томов и данных PostgreSQL используйте:

```bash
docker compose down -v
```

**Внимание:** команда `docker compose down -v` удаляет данные базы данных в Docker.

## Документация API

После запуска проекта документация доступна по адресам:

- Swagger UI: http://localhost:8000/api/docs/
- OpenAPI Schema: http://localhost:8000/api/schema/

## Основные API endpoints

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | `/api/users/register/` | Регистрация |
| GET | `/api/users/me/` | Получение профиля |
| PATCH | `/api/users/me/update/` | Обновление профиля |
| DELETE | `/api/users/me/delete/` | Удаление профиля |
| POST | `/api/token/` | Получение JWT-токенов |
| POST | `/api/token/refresh/` | Обновление access-токена |
| GET, POST | `/api/courses/` | Список и создание курсов |
| GET | `/api/courses/{id}/` | Получение курса |
| POST | `/api/courses/{course_id}/subscribe/` | Подписка на курс |
| GET, POST | `/api/lessons/` | Список и создание уроков |
| GET | `/api/lessons/{id}/` | Получение урока |
| GET | `/api/payments/` | Список платежей |
| POST | `/api/payments/create/` | Создание платежа |

## Структура проекта

```text
django_drf_project/
├── config/
├── materials/
├── users/
├── payments/
├── manage