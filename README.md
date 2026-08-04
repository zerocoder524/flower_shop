\# Flower Shop



Учебный веб-проект интернет-магазина цветов с оформлением заказов

и отправкой уведомлений сотруднику магазина через Telegram.



\## Возможности проекта



\- регистрация пользователей;

\- вход и выход из аккаунта;

\- просмотр каталога цветов;

\- просмотр карточки товара;

\- загрузка изображений товаров;

\- оформление заказа на доставку;

\- проверка доступности товара;

\- приём заказов только в рабочее время;

\- отправка информации о новом заказе через Telegram Bot API;

\- управление товарами и заказами через Django Admin;

\- автоматические тесты регистрации, каталога и заказов.



\## Используемые технологии



\- Python 3.12.4;

\- Django 5.2;

\- SQLite;

\- HTML и CSS;

\- Telegram Bot API;

\- Requests;

\- Pillow;

\- python-dotenv.



\## Структура проекта



```text

flower\_shop/

├── catalog/          # Каталог товаров

├── config/           # Настройки Django

├── orders/           # Оформление заказов

├── telegram\_bot/     # Интеграция с Telegram

├── users/            # Регистрация и авторизация

├── templates/        # HTML-шаблоны

├── static/           # Статические файлы

├── media/            # Изображения товаров

├── manage.py

├── requirements.txt

├── .env.example

└── README.md

```



\## Установка на Windows 11



Клонируйте репозиторий:



```cmd

git clone https://github.com/USERNAME/flower\_shop.git

cd flower\_shop

```



Создайте виртуальное окружение:



```cmd

py -3.12 -m venv .venv

```



Активируйте его:



```cmd

.venv\\Scripts\\activate.bat

```



Установите зависимости:



```cmd

python -m pip install -r requirements.txt

```



Создайте локальный файл настроек:



```cmd

copy .env.example .env

```



Примените миграции:



```cmd

python manage.py migrate

```



Создайте администратора:



```cmd

python manage.py createsuperuser

```



Проверьте проект:



```cmd

python manage.py check

```



Запустите сервер:



```cmd

python manage.py runserver

```



Сайт будет доступен по адресу:



```text

http://127.0.0.1:8000/

```



Административная панель:



```text

http://127.0.0.1:8000/admin/

```



\## Настройка Telegram



Создайте Telegram-бота через BotFather и заполните в `.env`:



```env

TELEGRAM\_BOT\_TOKEN=токен\_бота

TELEGRAM\_CHAT\_ID=идентификатор\_чата

TELEGRAM\_NOTIFICATIONS\_ENABLED=True

TELEGRAM\_API\_TIMEOUT=10

```



Получатель уведомлений должен предварительно открыть чат с ботом

и отправить команду:



```text

/start

```



Для запуска проекта без Telegram используйте:



```env

TELEGRAM\_NOTIFICATIONS\_ENABLED=False

```



\## Рабочее время магазина



Рабочее время задаётся в `.env`:



```env

SHOP\_OPEN\_TIME=09:00

SHOP\_CLOSE\_TIME=20:00

```



\## Тестирование



Запуск всех тестов:



```cmd

python manage.py test -v 2

```



На момент подготовки проекта реализовано 11 автоматических тестов.



\## Лицензия



Проект распространяется по лицензии MIT.

