import streamlit as st
from PIL import Image
import requests
import json
import base64
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import cufflinks as cf
import datetime

##------------------------------------------Streamlit Page division------------------------------------------------------##
st.set_page_config(layout="wide",page_title=' Crypto and Stocks', page_icon='📈',initial_sidebar_state='collapsed')
col1 = st.sidebar
nav=col1.radio("Navigation",["Cryptocurrency","Stocks","Currency Converter"])

if nav=="Cryptocurrency":
    ##--------------------------------------------Cypto-Heading--------------------------------------------------------##
    col2, col3 = st.columns((3,1))
    col1.header('Input Options')
    col2.title("Cryptocurrency Web Application")
    col2.markdown("""This app displays information about Top 100 Cryptocurrencies from **CoinMarketCap** !""")
    expander_bar = col2.expander("About")
    expander_bar.markdown("""
    * Built in `Python` using `streamlit`, `requests`, `json`, `base64`, `pandas` and `matplotlib`
    * The data source used is [CoinMarketCap](https://pro.coinmarketcap.com/) API
    * App built by **Sanchai Ahilan J K**
    """)
    image = Image.open('crypto.jpg')
    col3.image(image)
    col3.text("\n")
    col3.text("\n")
    col3.text("\n")
    col3.text("\n")
    col2.text("\n")
    col2.text("\n")

    ##----------------------------------------------Cypto-Col1---------------------------------------------------------##
    #SideBar - Select Price
    cpu = col1.selectbox('Select currency for price', ('USD', 'INR', 'EUR'))

    ##-------------------------------------------API-to-DataFrame------------------------------------------------------##
    #Requesting data from API
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
    parameters = {
    'start':'1',
    'limit':'100',
    'convert':cpu,
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': 'YOUR API KEY',
    }
    response = requests.get(url, params=parameters, headers=headers)
    jsondata = json.loads(response.text)

    #Storing JSON in a Dataframe
    CoinDF = pd.json_normalize(jsondata['data'])
    CoinDF = CoinDF[['name','symbol','max_supply','circulating_supply','quote.'+cpu+'.price','quote.'+cpu+'.percent_change_1h','quote.'+cpu+'.percent_change_24h','quote.'+cpu+'.percent_change_7d']]

    ##----------------------------------------------Cypto-Col1---------------------------------------------------------##
    #SideBar - Select Crypto
    sorted_coin = sorted( CoinDF['symbol'] )
    selected_coin = col1.multiselect('Cryptocurrency', sorted_coin, ['BTC','ETH','BNB','SHIB','DOGE'])
    df_selected_coin = CoinDF[ (CoinDF['symbol'].isin(selected_coin)) ]

    #Sidebar - Number of coins to display
    num_coin = col1.slider('Display Top N Coins', 1, 100, 100)
    df_coins = df_selected_coin[:num_coin]

    #Sidebar - Percent change timeframe
    percent_timeframe = col1.selectbox('Percent change time frame',['A Week','A Day', 'An Hour'])
    percent_dict = {"A Week":'quote.'+cpu+'.percent_change_7d',"A Day":'quote.'+cpu+'.percent_change_24h',"An Hour":'quote.'+cpu+'.percent_change_1h'}
    selected_percent_timeframe = percent_dict[percent_timeframe]

    #Sidebar - Sorting values
    sort_values = col1.selectbox('Sort values?', ['Yes', 'No'])

    ##----------------------------------------------Cypto-Col2---------------------------------------------------------##
    #Display Price
    col2.subheader('Price Data of Selected Cryptocurrency')
    col2.dataframe(df_coins[['name','symbol','quote.'+cpu+'.price','max_supply','circulating_supply']])

    #Download CSV
    def filedownload1(df):
        csv = df_coins[['name','symbol','quote.'+cpu+'.price','max_supply','circulating_supply']].to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="crypto price.csv">Download CSV File</a>'
        return href
    col2.markdown(filedownload1(df_selected_coin), unsafe_allow_html=True)

    #Display Change
    col2.subheader('Table of % Price Change')
    col2.dataframe(df_coins[['symbol','quote.'+cpu+'.percent_change_1h','quote.'+cpu+'.percent_change_24h','quote.'+cpu+'.percent_change_7d']])

    #Download CSV
    def filedownload2(df):
        csv = df_coins[['symbol','quote.'+cpu+'.percent_change_1h','quote.'+cpu+'.percent_change_24h','quote.'+cpu+'.percent_change_7d']].to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="crypto change.csv">Download CSV File</a>'
        return href
    col2.markdown(filedownload2(df_selected_coin), unsafe_allow_html=True)

    ##----------------------------------------------Cypto-Col3---------------------------------------------------------##
    # Preparing data for Bar plot of % Price change
    df_change = df_coins[['symbol','quote.'+cpu+'.percent_change_1h','quote.'+cpu+'.percent_change_24h','quote.'+cpu+'.percent_change_7d']]
    df_change = df_change.set_index('symbol')
    df_change['positive_percent_change_1h'] = df_change['quote.'+cpu+'.percent_change_1h'] > 0
    df_change['positive_percent_change_24h'] = df_change['quote.'+cpu+'.percent_change_24h'] > 0
    df_change['positive_percent_change_7d'] = df_change['quote.'+cpu+'.percent_change_7d'] > 0

    #Plotting the Change Graph
    col3.subheader('Bar plot of % Price Change')
    if percent_timeframe == 'A Week':
        df_change = df_change.sort_values(by=['quote.'+cpu+'.percent_change_7d'])
        col3.write('7 Days Period')
        plt.figure(figsize=(5,6))
        plt.subplots_adjust(top = 1, bottom = 0)
        df_change['quote.'+cpu+'.percent_change_7d'].plot(kind='barh', color=df_change.positive_percent_change_7d.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
    elif percent_timeframe == 'A Day':
        df_change = df_change.sort_values(by=['quote.'+cpu+'.percent_change_24h'])
        col3.write('24 Hour Period')
        plt.figure(figsize=(5,6))
        plt.subplots_adjust(top = 1, bottom = 0)
        df_change['quote.'+cpu+'.percent_change_24h'].plot(kind='barh', color=df_change.positive_percent_change_24h.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
    else:
        df_change = df_change.sort_values(by=['quote.'+cpu+'.percent_change_1h'])
        col3.write('60 Minutes Period')
        plt.figure(figsize=(5,6))
        plt.subplots_adjust(top = 1, bottom = 0)
        df_change['quote.'+cpu+'.percent_change_1h'].plot(kind='barh', color=df_change.positive_percent_change_1h.map({True: 'g', False: 'r'}))
        col3.pyplot(plt)
##------------------------------------------------------------------------------------------------------------------------##

elif nav=="Currency Converter":
    ##--------------------------------------------Currency-Heading--------------------------------------------------------##
    col1.header('Input Options')
    col2,col3=st.columns((10000,1))
    image = Image.open('currency.jpg')
    col2.image(image,width=700)
    col2.title("Currency Converter Web Application")
    col2.markdown("""This app displays latest value of International currencies from **ExchangeRatesAPI** !""")
    expander_bar = col2.expander("About")
    expander_bar.markdown("""
    * Built in `Python` using `streamlit`
    * The data source used is [Free Currency Converter](https://free.currencyconverterapi.com) API
    * App built by **Sanchai Ahilan J K**
    """)

    ##----------------------------------------------Currency-Col1---------------------------------------------------------##
    currency_list = ['AUD', 'BGN', 'BRL', 'CAD', 'CHF', 'CNY', 'CZK', 'DKK', 'GBP', 'HKD', 'HRK', 'HUF', 'IDR', 'ILS', 'INR', 'ISK', 'JPY', 'KRW', 'MXN', 'MYR', 'NOK', 'NZD', 'PHP', 'PLN', 'RON', 'RUB', 'SEK', 'SGD', 'THB', 'TRY', 'USD', 'ZAR']
    base = col1.selectbox('Base Currency', currency_list)
    target = col1.selectbox('Target currency', currency_list)
    amount=col1.number_input('Amount',min_value=0)

    url = 'https://free.currconv.com/api/v7/convert?q='+base+'_'+target+'&compact=ultra&apiKey=YOUR API KEY'
    response = requests.get(url)
    data = response.json()
    x=amount*data[base+'_'+target]

    ##----------------------------------------------Currency-Col2---------------------------------------------------------##
    col2.subheader(str(amount)+" "+base+" is equal to "+str(x)+" "+target)

else:
    ##--------------------------------------------Stocks-Heading--------------------------------------------------------##
    col1.header('Input Options')
    col2,col3=st.columns((1000,1))
    col2.title("Stocks Web Application")
    col2.markdown("""This app displays Stock Price Data of top Organizations from **yfinance** !""")
    expander_bar = col2.expander("About")
    expander_bar.markdown("""
    * The Data Source is [Yfinance](https://finance.yahoo.com)
    * Built in `Python` using `streamlit`, `yfinance`, `cufflinks`, `pandas` and `datetime`
    * App built by **Sanchai Ahilan J K**
    """)

    # Sidebar
    start_date = col1.date_input("Start date", datetime.date(2019, 1, 1))
    end_date = col1.date_input("End date", datetime.date(2021, 1, 31))

    # Retrieving tickers data
    ticker_list = pd.read_csv('https://raw.githubusercontent.com/dataprofessor/s-and-p-500-companies/master/data/constituents_symbols.txt')
    tickerSymbol = col1.selectbox('Stock ticker', ticker_list) # Select ticker symbol
    tickerData = yf.Ticker(tickerSymbol) # Get ticker data
    tickerDf = tickerData.history(period='1d', start=start_date, end=end_date) #get the historical prices for this ticker

    # Ticker information
    string_logo = '<img src=%s>' % tickerData.info['logo_url']
    col2.markdown(string_logo, unsafe_allow_html=True)

    string_name = tickerData.info['longName']
    col2.header('**%s**' % string_name)

    string_summary = tickerData.info['longBusinessSummary']
    col2.info(string_summary)

    # Ticker data
    col2.header('**Ticker data**')
    col2.write(tickerDf)

    # Bollinger bands
    col2.header('**Bollinger Bands**')
    qf=cf.QuantFig(tickerDf,title='First Quant Figure',legend='top',name='GS')
    qf.add_bollinger_bands()
    fig = qf.iplot(asFigure=True)
    st.plotly_chart(fig)