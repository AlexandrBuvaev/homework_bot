import json
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import EndPointError, JSONError

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s, %(levelname)s, %(message)s')
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)


def send_message(bot, message):
    """Функция отправки сообщения."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError:
        logger.error('Произошла ошибка при отправке сообщения.')


def get_api_answer(current_timestamp):
    """Функция делает запрос к API сервису Практикум.домашка."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            raise requests.HTTPError('Произошла ошибка HTTP.')
        else:
            response = response.json()
            return response
    except requests.exceptions.RequestException:
        raise EndPointError('Введен некорректныей URL.')
    except json.JSONDecodeError:
        raise JSONError('Ответ получен не в виде json.')


def check_response(response):
    """Функция проверяет корректность API запроса."""
    if not isinstance(response, dict):
        raise TypeError('Ожидаемое значение "response" словарь.')
    key = 'homeworks'
    if key not in response:
        raise KeyError(f'Отсутствует ключ {key} в "response".')
    if not isinstance(response[key], list):
        raise TypeError(f'Ожидаемое значение "response" {key} список.')
    return response[key]


def parse_status(homework):
    """Функция проверяет статус API запроса."""
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
    except KeyError as e:
        raise KeyError(f'В словаре домашней работы отсутствует ключ {e}.')

    if homework_status not in HOMEWORK_STATUSES:
        raise ValueError(f'Незадокументированный статус домашней'
                         f'работы:{homework_status}')
    verdict = HOMEWORK_STATUSES[homework_status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Функция проверяет наличие переменных окружения."""
    return all([TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        error_message = 'Отсутствуют обязательные переменные окружения!'
        logger.critical(error_message)
        sys.exit(error_message)
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())

    last_result = {}
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            if not homeworks:
                logger.debug('Нет обновлений.')
            for homework in homeworks:
                homework_name = homework['homework_name']
                last_result[homework_name] = homework['status']
                message = parse_status(homework)
                if message != last_result[homework_name]:
                    logger.debug('Нет обновлений в статусе работ.')
                else:
                    send_message(bot, message)
            current_timestamp = response.get('current_date', current_timestamp)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.error(message)
            send_message(bot, message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('Работа остановлена.')
