import ccxt
import matplotlib.pyplot as plt
import datetime
import time

import numpy as np
import pandas as pd

actual_eth_prices = [100, 105, 110, 115, 120]  # Фактические цены ETHUSDT
predicted_eth_prices = [101, 104, 112, 117, 119]  # Предсказанные цены ETHUSDT

actual_btc_prices = [5000, 5200, 5400, 5500, 5600]  # Фактические цены BTCUSDT
predicted_btc_prices = [4900, 5180, 5450, 5530, 5575]  # Предсказанные цены BTCUSDT


residuals_eth = [actual - predicted for actual, predicted in zip(actual_eth_prices, predicted_eth_prices)]
residuals_btc = [actual - predicted for actual, predicted in zip(actual_btc_prices, predicted_btc_prices)]


# Создайте DataFrame с остатками
data = {
    'residuals_eth': residuals_eth,
    'residuals_btc': residuals_btc
}
df = pd.DataFrame(data)

# Рассчитайте корреляцию между остатками ETHUSDT и BTCUSDT
correlation = df['residuals_eth'].corr(df['residuals_btc'])

print(f"Корреляция между остатками ETHUSDT и BTCUSDT: {correlation}")

# Создайте объект биржи (в данном случае Binance)
exchange = ccxt.binance()

# Выберите символ фьючерса ETHUSDT
symbol = 'ETH/USDT'

# Создайте списки для хранения времени и цен
times = []
prices = []

last_ticker = 0


# Создайте функцию для получения данных о цене и обновления графика в реальном времени
def update_price_chart():
    try:
        # Получите данные о цене
        ticker = exchange.fetch_ticker(symbol)
        price = float(ticker['last'])
        last_ticker = price

        # Запишите текущее время
        current_time = datetime.datetime.now()

        # Очистите текущее окно графика
        plt.close()

        # Добавьте время и цену в списки
        times.append(current_time)
        prices.append(price)

        # Ограничьте количество точек на графике (например, последние 3600 точек)
        if len(times) > 3600:
            times.pop(0)
            prices.pop(0)

        # Очистите текущий график
        plt.clf()

        # Постройте график
        plt.plot(times, prices, label=symbol)
        plt.title(f'Real-time Price Chart for {symbol}')
        plt.xlabel('Time')
        plt.ylabel('Price')
        plt.legend()
        plt.xticks(rotation=45)

        # Отобразите график
        plt.pause(1)
        if (price < last_ticker) and (last_ticker < price):
            print(price)

    except Exception as e:
        print(f"An error occurred: {e}")


# Запустите бесконечный цикл для обновления графика в реальном времени
while True:
    update_price_chart()
    time.sleep(10)  # Обновление каждые 10 секунд
