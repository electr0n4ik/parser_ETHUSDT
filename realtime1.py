import websockets
import json
import pandas as pd
import asyncio
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


async def handle_trade(trade, trading_pair):
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

    # Добавить паузу в 10 секунд
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


async def main():
    eth_symbol = 'ethusdt'
    btc_symbol = 'btcusdt'
    eth_url = "wss://stream.binance.com:9443/ws"
    btc_url = "wss://stream.binance.com:9443/ws"

    await create_table()  # Создание таблицы

    async with websockets.connect(f"{eth_url}/{eth_symbol}@trade") as eth_ws, websockets.connect(
            f"{btc_url}/{btc_symbol}@trade") as btc_ws:
        while True:
            eth_response = await eth_ws.recv()
            btc_response = await btc_ws.recv()
            await handle_trade(eth_response, eth_symbol)
            await handle_trade(btc_response, btc_symbol)
            await delete_old_data()  # Удаление старых данных


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
