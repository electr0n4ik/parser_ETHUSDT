import asyncio
import json
import time

import pandas as pd
import websockets
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True)
    symbol = Column(String)
    price = Column(Numeric)
    timestamp = Column(DateTime)


async def create_table():
    engine = create_engine('postgresql://postgres:12345@localhost:5432/postgres')
    Base.metadata.create_all(engine)


async def handle_trade(trade):
    data = json.loads(trade)
    print(f"Торговая пара: {data['s']}, Цена: {data['p']} {data['s']}")
    symbol = data['s']
    price = data['p']

    engine = create_engine('postgresql://postgres:12345@localhost:5432/postgres')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Вставка данных в таблицу
    trade_entry = Trade(symbol=symbol, price=price, timestamp=time.strftime('%Y-%m-%d %H:%M:%S'))
    session.add(trade_entry)
    session.commit()
    session.close()

    # пауза в 10 секунд
    await asyncio.sleep(10)


async def delete_old_data():
    engine = create_engine('postgresql://postgres:12345@localhost:5432/postgres')
    Session = sessionmaker(bind=engine)
    session = Session()

    # Удаление данных старше 1 часа
    session.query(Trade).filter(
        Trade.timestamp < time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() - 3600))).delete()
    session.commit()
    session.close()


async def calculate_correlation():
    engine = create_engine('postgresql://postgres:12345@localhost:5432/postgres')
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # SQL-запрос для извлечения данных из базы данных
        result = session.query(Trade.timestamp, Trade.price).order_by(Trade.timestamp).all()

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
    except Exception as e:
        print(f"Error executing query: {e}")
    finally:
        session.close()


async def price_change_alert(data, price_change_threshold=0.01, time_frame=60):
    engine = create_engine('postgresql://postgres:12345@localhost:5432/postgres')
    Session = sessionmaker(bind=engine)
    session = Session()

    price_history = []

    while True:
        current_price = data["p"]
        timestamp = time.time()

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

    session.close()


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
