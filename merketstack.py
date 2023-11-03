import json
import requests
import psycopg2
from datetime import datetime, timedelta


db_params = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '12345',
}

current_time = datetime.now()
one_hour_ago = current_time - timedelta(hours=1)


access_key = 'b9420d6b6fd3cea37e4bc7787faae31e'
symbol = 'ETH'

api_url = f'http://api.marketstack.com/v1/intraday?access_key={access_key}&symbols={symbol}&interval=1min'

conn = psycopg2.connect(**db_params)
cursor = conn.cursor()


response = requests.get(api_url)
data = response.json()

print(json.dumps(data, indent=4))

with open('data.json', 'w') as f:
    json.dump(data, f, indent=4)
#
# for item in data['data']:
#     print(json.dumps(item, indent=4))
#     date = item['date'].split('T')[0]  # Получаем только дату без времени
#     date_time = datetime.strptime(date, "%Y-%m-%d")
#     open_price = item['open']
#     close_price = item['close']
#     high_price = item['high']
#     low_price = item['low']
#     volume = item['volume']
#
#     cursor.execute(
#         "INSERT INTO stock_prices (date, open, close, high, low, volume) VALUES (%s, %s, %s, %s, %s, %s)",
#         (date, open_price, close_price, high_price, low_price, volume)
#     )
#
# # Сохраните изменения в базе данных
# conn.commit()
# cursor.close()
# conn.close()
#
print(1)
