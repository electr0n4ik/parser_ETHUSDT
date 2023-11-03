import asyncio
import websockets
import json
import asyncpg


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


async def main():
    symbol = 'ethusdt'
    url = "wss://stream.binance.com:9443/ws"

    await create_table()  # Создание таблицы

    async with websockets.connect(f"{url}/{symbol}@trade") as ws:
        while True:
            response = await ws.recv()
            await handle_trade(response)
            await delete_old_data()  # Удаление старых данных


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
