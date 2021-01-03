import requests
from datetime import date, timedelta
from twilio.rest import Client
import os
import pymongo

STOCK_API_URL = "https://www.alphavantage.co/query"
NEWS_API_URL = "https://newsapi.org/v2/everything"

myClient = pymongo.MongoClient(os.environ['MONGO_CLIENT'])

# create database
myDb = myClient['stocksDB']

# create collection
myCollection = myDb['subscriptions']

data = myCollection.find()

for x in data:
    print(x['symbol'])
    STOCK_NAME = x['symbol']
    COMPANY_NAME = x['company']

    stock_param = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': STOCK_NAME,
        'apikey': os.environ['API_KEY']
    }

    response = requests.get(STOCK_API_URL, stock_param)
    #print(response.json())

    yesterday_date = (date.today()-timedelta(days=1)).isoformat()
    dayBefore_yesterday_date = (date.today()-timedelta(days=2)).isoformat()

    yes_data = response.json()['Time Series (Daily)']['2020-12-31']
    yes_close = yes_data['4. close']
    yes_open = yes_data['1. open']
    yes_high = yes_data['2. high']
    yes_low = yes_data['3. low']
    print(yes_close)
    dayBefore_data = response.json()['Time Series (Daily)']['2020-12-30']
    dayBefore_close = dayBefore_data['4. close']
    dayBefore_open = dayBefore_data['1. open']
    dayBefore_high = dayBefore_data['2. high']
    dayBefore_low = dayBefore_data['3. low']
    print(dayBefore_close)
    difference = (float(yes_close) - float(dayBefore_close))
    print(difference)

    diff_percent = difference/float(yes_close) * 100
    print(diff_percent)
    if diff_percent < 0:
        sym = 'down'
    else:
        sym = 'up'

    new_param = {
        'qInTitle': COMPANY_NAME,
        'apiKey': os.environ['NEWS_API_KEY']
    }
    news = requests.get(NEWS_API_URL, new_param)
    articles = news.json()['articles']
    titles = []
    description = []

    for i,each_article in enumerate(articles):
        if i > 2:
            break
        titles.append(each_article['title'])
        description.append(each_article['description'])

    print(titles)

    client = Client(os.environ['ACCOUNT_SID'], os.environ['ACCOUNT_AUTH'])
    stock_stat = COMPANY_NAME+": "+sym+" "+str(round(diff_percent, 2))+"%"
    for i in range(0, 1):
        mess = "\n\n"+stock_stat+"\n\nLast Opening Price: "+str(round(float(yes_open), 2))+"\nLast Highest Price: "+str(round(float(yes_high), 2))+"\nLast Lowest Price: "+str(round(float(yes_low), 2))+"\nLast Closing Price: "+str(round(float(yes_close), 2))+"\n\nHeadline: "+titles[i]+"\n\nDescription: "+description[i]
        message = client.messages.create(
                 body=mess,
                 from_='+12562861254',
                 to=x['mobileNo']
            )
