# Музыкальная библиотека

Веб-приложение для создания и управления музыкальными плейлистами с интеграцией Deezer API.

## Функциональность

- Регистрация и авторизация пользователей
- Создание и управление плейлистами
- Поиск музыки через Deezer API
- Добавление песен в плейлисты
- Просмотр истории поиска
- Радио с случайными треками
- Управление пользователями (для администраторов)

## Технологии

- Python 3.13
- Django 4.2+
- SQLite
- Deezer API

## Запуск через Docker

1. Соберите и запустите контейнер:
```bash
docker compose up --build
```

2. Откройте в браузере: http://localhost:8000

3. Запуск тестов API:
```bash
python test_api.py
```

## Установка (локально)

1. Клонируйте репозиторий:
```bash
git clone [url-репозитория]
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
```

3. Активируйте виртуальное окружение:
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Примените миграции:
```bash
python manage.py migrate
```

6. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```

7. Запустите сервер:
```bash
python manage.py runserver
```

## Тестирование с помощью Selenium

Для запуска автоматических тестов регистрации и логина:

1. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```
   Убедитесь, что установлен Chrome и chromedriver

2. Установите dev-зависимости и запустите тесты:
   ```
   pip install -r requirements-dev.txt
   python manage.py test main.tests.UserAuthSeleniumTests
   ```

Тесты автоматически проверяют все основные сценарии регистрации и входа пользователя.

## Структура проекта

- `main/` - основное приложение
  - `models.py` - модели данных
  - `views.py` - представления
  - `forms.py` - формы
  - `urls.py` - маршруты
  - `templates/` - HTML шаблоны
  - `tests.py` - Selenium-тесты
- `myproject/` - настройки проекта

## Основные модели

- `User` - пользователи системы
- `Artist` - исполнители
- `Song` - песни
- `Playlist` - плейлисты пользователей
- `PlaylistSong` - связи между плейлистами и песнями
- `SearchHistory` - история поиска

## API Endpoints

- `/` - главная страница
- `/register/` - регистрация
- `/search/` - поиск музыки
- `/create-playlist/` - создание плейлиста
- `/my-playlist/<id>/` - просмотр плейлиста
- `/manage-playlists/` - управление плейлистами
- `/radio/` - радио с случайными треками

## CI/CD и проверки безопасности

При push в `main` запускается [Security CI/CD](.github/workflows/security-ci.yml):

1. Функциональные тесты  
2. Bandit (SAST), pip-audit (SCA), Gitleaks  
3. Django `check --deploy`  
4. Trivy (Docker), OWASP ZAP (DAST)  
5. **CI gate** — явная проверка, что все jobs успешны  
6. **CD:** deploy на сервер **только после** CI gate (новый push отменяет предыдущий run)  

### Переменные окружения

```bash
cp .env.example .env
```

Сгенерировать `DJANGO_SECRET_KEY`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

На сервере в `.env`: `DJANGO_DEBUG=false`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`.

### GitHub Secrets для автодеплоя

**Settings → Secrets → Actions:** `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY`, опционально `SSH_PORT`.

### Как специально «сломать» проверки (для демо)

| Инструмент | Что изменить |
|------------|--------------|
| **Bandit** | Убрать `timeout` в `requests.get` (`get_random_track`) |
| **pip-audit** | `urllib3==1.26.2` в `requirements.txt` |
| **Gitleaks** | Fake API key в коде |
| **Django check** | `DJANGO_DEBUG=true` в `env:` workflow |
| **Trivy** | Старый `Dockerfile` без `apt-get upgrade` |
| **Deploy** | Удалить `SSH_HOST` из Secrets |
| **DAST (ZAP)** | `fail_action: false` в workflow или убрать `zap/rules.tsv` |

### DAST (OWASP ZAP)

- Сканируются публичные URL из `scripts/dast_urls.txt` (спайдер ZAP от главной).
- Запуск через **Gunicorn** (как на сервере), не `runserver`.
- `fail_action: true`, порог отчёта `-l WARN` (в ZAP нет уровня MEDIUM); ожидаемые предупреждения HTTP в CI — в `zap/rules.tsv`.
- Отчёты: артефакт `zap-report` в Actions.
