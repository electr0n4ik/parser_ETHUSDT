import asyncio
import json
import time

import asyncpg
import pandas as pd
import websockets


async def create_table():
    conn = await asyncpg.connect(
        user='postgres',
        password='12345',
        database='postgres',
        port='5432'
    )

    # Создание таблицы, если она не существует
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id serial PRIMARY KEY,
            symbol TEXT,
            price NUMERIC,
            timestamp TIMESTAMP
        )
    ''')

    await conn.close()


async def handle_trade(trade):
    data = json.loads(trade)
    print(f"Торговая пара: {data['s']}, Цена: {data['p']} {data['s']}")
    symbol = data['s']
    price = data['p']

    conn = await asyncpg.connect(
        user='postgres',
        password='12345',
        database='postgres',
        port='5432'
    )

    # Вставка данных в таблицу
    await conn.execute('''
        INSERT INTO trades (symbol, price, timestamp) VALUES ($1, $2, NOW())
    ''', symbol, price)

    await conn.close()

    # пауза в 10 секунд
    await asyncio.sleep(10)


async def delete_old_data():
    conn = await asyncpg.connect(
        user='postgres',
        password='12345',
        database='postgres',
        port='5432'
    )

    # Удаление данных старше 1 часа
    await conn.execute('''
        DELETE FROM trades WHERE timestamp < NOW() - interval '1 hour'
    ''')

    await conn.close()


async def calculate_correlation():
    conn = await asyncpg.connect(
        user='postgres',
        password='12345',
        database='postgres',
        port='5432'
    )

    try:
        # SQL-запрос для извлечения данных из базы данных
        query = 'SELECT timestamp, price FROM trades ORDER BY timestamp'
        result = await conn.fetch(query)

        # DataFrame из полученных данных
        data = pd.DataFrame(result, columns=['X', 'Y'])

        # Рассчет корреляции
        if not data.empty:
            correlation = data['X'].corr(data['Y'])

            if not pd.isnull(correlation):
                print(f"Корреляция между X и Y: {correlation}")
            else:
                print("Недостаточно данных для расчета корреляции.")
        else:
            print("Недостаточно данных для расчета корреляции.")
    except asyncpg.PostgresError as e:
        print(f"Error executing query: {e}")
    finally:
        await conn.close()


async def price_change_alert(data, price_change_threshold=0.01, time_frame=60):
    price_history = []

    while True:
        current_price = data["p"]
        timestamp = int(time.time())
        price_history.append((current_price, timestamp))

        # Оставляем только данные, которые находятся в заданном временном диапазоне
        while price_history and timestamp - price_history[0][1] > time_frame * 60:
            price_history.pop(0)

        # Рассчитываем изменение цены
        if len(price_history) >= 2:
            previous_price = price_history[0][0]
            percent_change = (current_price - previous_price) / previous_price

            if abs(percent_change) >= price_change_threshold:
                if percent_change > 0:
                    movement = "Цена растет"
                else:
                    movement = "Цена падает"

                print(f"Изменение цены на {abs(percent_change) * 100:.2f}% за последние {time_frame} минут. {movement}")

        await asyncio.sleep(10)  # Проверяем каждые 10 секунд


async def main():
    symbol = 'ethusdt'
    url = "wss://stream.binance.com:9443/ws"

    await create_table()  # Создание таблицы

    async with websockets.connect(f"{url}/{symbol}@trade") as ws:
        while True:
            response = await ws.recv()
            await handle_trade(response)
            await delete_old_data()  # Удаление старых данных
            await calculate_correlation()


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
