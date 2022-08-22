from homework import get_api_answer
from pprint import pprint
import time

current_timestamp = int(time.time())
result = get_api_answer(current_timestamp)
result2 = result.get('current_date', current_timestamp)
pprint(result2)
