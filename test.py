from email import message
from homework import get_api_answer, check_response, parse_status, send_message
from pprint import pprint
import time

current_timestamp = int(time.time())
response = get_api_answer(current_timestamp)
homeworks = check_response(response)

result = {}
for homework in homeworks:
    homework_name = homework['homework_name']
    result[homework_name] = homework['status']
    message = parse_status(homework)
    if message != result[homework_name]:
        send_message(bot, message)
        result[homework_name] = message
    else:
        print('нет обновлений!')