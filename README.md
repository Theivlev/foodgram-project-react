# "Продуктовый помощник" (Foodgram)

## 1. [Описание](#1)
## 2. [Установка Docker (на платформе Ubuntu)](#2)
## 3. [База данных и переменные окружения](#3)
## 4. [Команды для запуска](#4)
## 5. [Техническая информация](#5)
## 6. [Об авторе](#7)

## 1. Описание

Проект "Продуктовый помошник" (Foodgram) предоставляетследующие возможности:
  - регистрироваться
  - просматривать рецепты других пользователей
  - создавать свои рецепты и управлять ими (корректировать\удалять)
  - добавлять рецепты других пользователей в  "Корзину" и "Избранное"
  - осуществлять подписку на других пользователей
  - скачать "Корзину" покупок

## 2. Установка Docker (на платформе Ubuntu)

Проект поставляется в четырех контейнерах Docker (backend, nginx, db, frontend).  
Для запуска необходимо установить Docker и Docker Compose.  
Подробнее об установке на других можно узнать на [официальном сайте](https://docs.docker.com/engine/install/).

## 3. База данных и переменные окружения

Проект использует базу данных PostgreSQL.  
Для подключения и выполненя запросов к базе данных необходимо создать и заполнить файл ".env" с переменными окружения в папке "./infra/".

Шаблон для заполнения файла ".env":
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

## 4. Команды для запуска

Cоздать и активировать виртуальное окружение:
python -m venv venv
Linux: source venv/bin/activate
Windows: source venv/Scripts/activate

Установить зависимости из файла requirements.txt:

python3 -m pip install --upgrade pip

pip install -r requirements.txt
# Выполнить миграции:

*WIN: python manage.py migrate*

*MAC: python3 manage.py migrate*

# Запустить проект:

*WIN: python manage.py runserver*

*MAC: python3 manage.py runserver*

## Документация:
*Полная документация и примеры запросов доступны по эндпоинту*

http://127.0.0.1:8000/redoc/

## 5. Техническая информация

Стек технологий: Python, Docker, PostgreSQL, nginx, Django Rest,   gunicorn, 

Веб-сервер: nginx (контейнер nginx)  
Frontend фреймворк: React (контейнер frontend)  
Backend фреймворк: Django (контейнер backend)  
API фреймворк: Django REST (контейнер backend)  
База данных: PostgreSQL (контейнер db)

## 7. Об авторе

Ивлев Алексей Константинович 
Python-разработчик (Backend)   
E-mail: theivlev@yandex.ru  


[![foodgram_workflow](https://github.com/Theivlev/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)