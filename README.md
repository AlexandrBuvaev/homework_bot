**Homework bot**

Телеграмм бот для проверки статуса домашнего задания. Основной функционал бота состоит в отправке запроса к API Яндекс.Практикум, для проверки статуса домашнего задания.

**Установка и запуск проекта.**

- Скопируйте репозиторий на локальное устройство:
```bash
git clone git@github.com:AlexandrBuvaev/homework_bot.git
```

- Создайте в корневой директории проекта файл .env с переменными окружения:
``` bash
PRACTICUM_TOKEN = 'your practicum token'
TELEGRAM_TOKEN = 'your telegram token'
TELEGRAM_CHAT_ID = 'your telegram chat_id'
```
- Создайте папку с виртуальным окружением и активируйте его:
```bash
python3 -m venv venv
source venv/bin/activate
```
- Установите все необходимые зависимости и запустите проект:
```bash
pip install -r requirements.txt
python3 homework.py
```
