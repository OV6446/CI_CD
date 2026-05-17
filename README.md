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

2. Запустите тесты:
   ```
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
