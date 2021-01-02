import requests
from datetime import date, timedelta
from twilio.rest import Client
import os

STOCK_NAME = "FB"
COMPANY_NAME = "FACEBOOK"

STOCK_API_URL = "https://www.alphavantage.co/query"
NEWS_API_URL = "https://newsapi.org/v2/everything"

stock_param = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK_NAME,
    'apikey': os.environ['API_KEY']
}

response = requests.get(STOCK_API_URL, stock_param)
#print(response.json())

yesterday_date = (date.today()-timedelta(days=1)).isoformat()
dayBefore_yesterday_date = (date.today()-timedelta(days=2)).isoformat()

yes_data = response.json()['Time Series (Daily)']['2020-12-24']
yes_close = yes_data['4. close']
print(yes_close)
dayBefore_data = response.json()['Time Series (Daily)']['2020-12-23']
dayBefore_close = dayBefore_data['4. close']
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
for i in range(0, 2):
    mess = "\n\n"+stock_stat+"\n\nClosing Price: "+str(round(float(yes_close), 2))+"\n\nHeadline: "+titles[i]+"\n\nDescription: "+description[i]
    message = client.messages.create(
             body=mess,
             from_='+12562861254',
             to='+639226083968'
        )