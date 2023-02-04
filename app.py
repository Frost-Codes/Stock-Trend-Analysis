import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import streamlit as st
import yfinance as yf
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from main import trader
import statistics
import datetime
import fxcmpy
import socketio


start = datetime.datetime(2012, 1, 1)
end = datetime.datetime.today()
api_logs = './data/api_logs.log'
# access_token = '6a86b7d8cf1ad038e444db321ac95fe7279c607f'

with open(api_logs, 'a') as file:
    file.write(str(datetime.datetime.now()) + '\n\n')

# trader = fxcmpy.fxcmpy(access_token=access_token, log_level='error', log_file=api_logs)

st.set_page_config(page_title='Stocks', page_icon='💹')
st.header('ML Stock Trend Prediction')

symbol = st.selectbox('Select Symbol', ['XAU/USD', 'BTC/USD', 'EUR/USD', 'NZD/USD', 'US30', 'GBP/USD'])
data = trader.get_candles(symbol, period='H1', number=1000)
data['Close'] = (data['bidclose'] + data['askclose']) / 2

# data = yf.download(symbol, period='1mo', interval='1h', auto_adjust=True)

if len(data != 0):
    last = data.tail().iloc[-1]
    last['High'] = (last['bidhigh'] + last['askhigh']) / 2
    last['Low'] = (last['bidlow'] + last['asklow']) / 2
    second_last = data.tail().iloc[-2]
    second_last['High'] = (second_last['bidhigh'] + second_last['askhigh']) / 2
    second_last['Low'] = (second_last['bidlow'] + second_last['asklow']) / 2
    column1, column2, column3 = st.columns(3)
    column1.metric('HIGH', str(round(last['High'], 4)), str(round(last['High'] - second_last['High'], 4)))
    column2.metric('LOW', str(round(last['Low'], 4)), str(round(last['Low'] - second_last['Low'], 4)))
    column3.metric('CLOSE', str(round(last['Close'], 4)), str(round(last['Close'] - second_last['Close'], 4)))
    st.subheader(f'{symbol} 1 hour timeframe analysis')
    st.write(data.describe())

# doing some clean up
try:
    data = data.reset_index()
    data.drop(['date', 'bidopen', 'bidclose', 'bidhigh', 'bidlow', 'askopen', 'askclose',
               'askhigh', 'asklow', 'tickqty'], axis=1, inplace=True)
    # plotting close price
    st.subheader(f'{symbol} 1 hour timeframe close price')
    figure1 = plt.figure(figsize=(10, 6))
    plt.plot(data['Close'], label='Close')
    plt.legend()
    plt.xlabel('Day')
    plt.ylabel('Price')
    st.pyplot(figure1)

    # adding SMAs and direction
    data['SMA1'] = data['Close'].rolling(9).mean()
    data['SMA2'] = data['Close'].rolling(14).mean()
    data['direction'] = np.select([data['SMA1'] > data['SMA2'], data['SMA1'] < data['SMA2']], [1, -1])

    # Plotting with SMA
    st.subheader(f'{symbol} close price SMA 9 & SMA 14')
    figure2 = plt.figure(figsize=(10, 6))
    plt.plot(data['Close'], label='Close')
    plt.plot(data['SMA1'], label='SMA 9')
    plt.plot(data['SMA2'], label='SMA 14')
    plt.legend()
    plt.xlabel('Day')
    plt.ylabel('Price')
    st.pyplot(figure2)

    # splitting data
    data_training = pd.DataFrame(data['Close'][0:int(len(data) * 0.1)])
    data_testing = pd.DataFrame(data['Close'][int(len(data) * 0.1):])

    # analogy of last in training will be used in predicting first in testing
    last_training = data_training.tail(14)
    train_test = last_training.append(data_testing, ignore_index=True)

    # scaling the data
    scaler = MinMaxScaler(feature_range=(0, 1))
    final_testing = scaler.fit_transform(train_test)

    # split testing data into x_test and y_test
    x_test = []
    y_test = []
    for i in range(14, final_testing.shape[0]):
        x_test.append(final_testing[i - 14:i])
        y_test.append(final_testing[i, 0])

    # convert the list to narray
    x_test, y_test = np.array(x_test), np.array(y_test)

    # loading model
    model = load_model('./oneHourModel.h5')

    # making predictions
    y_predicted = model.predict(x_test)

    # finding scale factor
    scale_factor = 1 / scaler.scale_

    # scaling test data up
    y_predicted_scaled = y_predicted * scale_factor
    y_test_scaled = y_test * scale_factor

    # plotting original vs predictions
    st.subheader('Original vs Predictions')
    figure3 = plt.figure(figsize=(10, 6))
    plt.plot(y_test_scaled, label='Original')
    plt.plot(y_predicted_scaled, label='Predictions')
    plt.xlabel('Day')
    plt.ylabel('Price')
    plt.legend()
    st.pyplot(figure3)

    # trend summary
    st.subheader('Trend summary')
    if statistics.mode(data['direction'].iloc[-1:-7:-1] == 1):
        st.write(f'Currently in an uptrend (Buy {symbol})')
    elif statistics.mode(data['direction'].iloc[-1:-7:-1] == -1):
        st.write(f'Currently in a downtrend (Sell {symbol})')
    else:
        st.write(f'{symbol} is Consolidating')
except KeyError:
    st.write('Connect to the internet!!!')

st.markdown(
    """
    ---
    Created with ❤ by Ian
    """
)

