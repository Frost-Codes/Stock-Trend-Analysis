import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import streamlit as st
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import statistics
import datetime
from plotly import express as px
import streamlit_authenticator as stauth
from database import get_users
from database import sign_up
from main import trader


api_logs = './data/api_logs.log'

with open(api_logs, 'a') as file:
    file.write(str(datetime.datetime.now()) + '\n\n')


st.set_page_config(page_title='Stocks', page_icon='💹', initial_sidebar_state='collapsed')

try:

    users = get_users()
    emails = []
    passwords = []
    user_names = []

    for user in users:
        emails.append(user['key'])
        user_names.append(user['username'])
        passwords.append(user['password'])

    credentials = {'usernames': {}}
    for index in range(len(emails)):
        credentials['usernames'][user_names[index]] = {'name': emails[index], 'password': passwords[index]}

    authenticator = stauth.Authenticate(credentials, cookie_name='MLStosks', key='abcdef', cookie_expiry_days=5)
    email, authentication_status, user_name = authenticator.login('Login', 'main')
    info, info1 = st.columns(2)

    # sign up page
    if not authentication_status:
        sign_up()

    if user_name:
        if user_name in user_names:
            if authentication_status:

                # let user see app

                st.header('ML Stock Trend Prediction')

                symbol = st.selectbox('Select Symbol', ['XAU/USD', 'BTC/USD', 'EUR/USD', 'NZD/USD', 'US30', 'GBP/USD'])

                # logout
                authenticator.logout('Log out', 'sidebar')
                st.sidebar.subheader(f'Welcome {user_name}')
                # date functionality
                start_date = st.sidebar.date_input('Start Date',
                                                   value=datetime.datetime.today() - datetime.timedelta(days=12),
                                                   max_value=datetime.datetime.today() - datetime.timedelta(days=1))
                end_date = st.sidebar.date_input('End Date', value=datetime.datetime.today(),
                                                 min_value=start_date + datetime.timedelta(days=1),
                                                 max_value=datetime.datetime.today())
                period = st.sidebar.selectbox('Time Frame', ['H1', 'm30', 'H4'])

                data = trader.get_candles(symbol, period='H1', number=750)
                data['Close'] = (data['bidclose'] + data['askclose']) / 2

                data2 = trader.get_candles(symbol, period=period, start=str(start_date), end=str(end_date))
                data2['Close'] = (data2['bidclose'] + data2['askclose']) / 2

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
                    column3.metric('CLOSE', str(round(last['Close'], 4)),
                                   str(round(last['Close'] - second_last['Close'], 4)))
                    st.subheader(f'{symbol} 1 hour timeframe analysis')
                    st.write(data.describe())

                try:
                    # plotting close price
                    st.subheader(f'{symbol} {period} timeframe close price')
                    figure1 = px.line(data2, x=data2.index, y=data2['Close'])
                    figure1.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
                    st.plotly_chart(figure1)

                    # adding SMAs and direction
                    data['SMA1'] = data['Close'].rolling(9).mean()
                    data['SMA2'] = data['Close'].rolling(14).mean()
                    data['direction'] = np.select([data['SMA1'] > data['SMA2'], data['SMA1'] < data['SMA2']], [1, -1])

                    data2['SMA1'] = data2['Close'].rolling(9).mean()
                    data2['SMA2'] = data2['Close'].rolling(14).mean()

                    # Plotting with SMA
                    st.subheader(f'{symbol} {period} close price with SMA 9 & SMA 14')

                    figure2 = px.line(data2, x=data2.index, y=[data2['Close'], data2['SMA1'], data2['SMA2']])
                    figure2.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                                          yaxis_title='Price')
                    st.plotly_chart(figure2)

                    # doing some clean up
                    data = data.reset_index()
                    data.drop(['date', 'bidopen', 'bidclose', 'bidhigh', 'bidlow', 'askopen', 'askclose',
                               'askhigh', 'asklow', 'tickqty'], axis=1, inplace=True)

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
                    predictions = pd.DataFrame()
                    predictions['Predictions'] = y_predicted_scaled.reshape(len(y_predicted_scaled))
                    predictions['Original'] = y_test_scaled.reshape(len(y_test_scaled))
                    predictions.index.name = 'Days'

                    # plotting original vs predictions
                    st.subheader('Original vs Predictions')
                    figure3 = px.line(predictions, x=predictions.index,
                                      y=[predictions['Original'], predictions['Predictions']], width=750, height=450)
                    figure3.update_layout(xaxis=dict(showgrid=False), yaxis=dict(showgrid=False),
                                          xaxis_title='Days', yaxis_title='Price')
                    st.plotly_chart(figure3)

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

            elif not authentication_status:
                with info:
                    st.error('Incorrect Password')
            elif authentication_status is None:
                with info:
                    st.warning('Please Enter your Username and password')

        else:
            with info:
                st.warning('Username does not exist, Please Sign up ')

except:
    st.success('Refresh page')

