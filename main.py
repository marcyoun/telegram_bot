import pandas as pd
import telebot 
from pycoingecko import CoinGeckoAPI
from datetime import date
import os 

# API_KEY = os.environ.get("BOT_KEY")
API_KEY = '5122613375:AAGQY-MU6gvRgApKzMGnMJ1JZ6Vanylzrwg'
cg = CoinGeckoAPI()

bot = telebot.TeleBot(API_KEY)

commands = ['start', 'price', 'marketcap', 'returns', 'books']
# Intro
intro = "Type any of the below commands to get started\n\n"
price_def = f"/{commands[1]}: get the current price of Bitcoin in cuck bucks\n"
marketcap_def = f"/{commands[2]}: get the current market cap of Bitcoin in cuck bucks\n"
returns_def = f"/{commands[3]}: get historical returns in percentage\n\n"
books_def = f"/{commands[4]}: get recommended Bitcoin, economics, and other books\n"
metrics = [price_def, marketcap_def, returns_def]
resources = [books_def]

# Resources
books_dict = {
    'Grokking Bitcoin': 'https://rb.gy/gymfxz',
    'Inventing Bitcoin: The Technology Behind the First Truly Scarce and Decentralized Money Explained': 'https://rb.gy/vqtj64',
    'The Blocksize War: The Battle for Control Over Bitcoin’s Protocol Rules':'https://rb.gy/4svnhd', 
    'The Bitcoin Standard: The Decentralized Alternative to Central Banking': 'https://rb.gy/lsfdny',
    'The Sovereign Individual: Mastering the Transition to the Information Age': 'https://rb.gy/1ciqvd',
    'Economics in One Lesson': 'https://rb.gy/btp2qh',
    'What Has Government Done to Our Money?': 'https://rb.gy/a7objr',
    'The Road to Serfdom': 'https://rb.gy/vvexny',
    'When Money Dies: The Nightmare of Deficit Spending, Devaluation, and Hyperinflation in Weimar, Germany': 'https://rb.gy/hngvxq',
    'The Law': 'https://rb.gy/hfsbcp'

}


@bot.message_handler(commands=['start'])
def start(message):
    metrics_output = "Metrics\n"
    resources_output = "Resources\n"

    for t in metrics:
        metrics_output += t
    for t in resources:
        resources_output += t

    response = intro
    sections = [metrics_output, resources_output]

    for t in sections:
        response += t

    print(response)
        
    bot.send_message(message.chat.id, response)
    
@bot.message_handler(commands=['price'])
def price(message):
    price = cg.get_price('bitcoin', 'usd')
    current_price = price['bitcoin']['usd']
    sats_per_dollar = round(100000000 / price['bitcoin']['usd'])
    sats_millionaire = round(1000000 / sats_per_dollar)
    
    response = f'1 BTC = {current_price} USD \n\n 1 USD = {sats_per_dollar} sats \n\n {sats_millionaire} USD to become a sats millionaire'
    
    print(response)

    bot.send_message(message.chat.id, response)
    
    
@bot.message_handler(commands=['marketcap'])
def marketCap(message):
    today = date.today()
    today= today.strftime('%d-%m-%Y')
    data = cg.get_coin_history_by_id('bitcoin', date=today)
    market_cap = data['market_data']['market_cap']['usd']
    market_cap = str(round((market_cap / 1000000000),1)) + "B"
    response = f'{market_cap} cuck bucks'

    print(response)
        
    bot.send_message(message.chat.id, response)
    
@bot.message_handler(commands=['returns'])
def returns(message):
    today = date.today()
    today= today.strftime('%d-%m-%Y')
    df = cg.get_coin_market_chart_by_id('bitcoin','usd','max')
    prices = df['prices']
    prices = pd.DataFrame(prices)
    prices.iloc[:,0] =  pd.to_datetime(prices.iloc[:,0],unit='ms')
    prices.columns = ['date','price']
    prices.index = prices['date']
    prices.drop('date', axis = 1 , inplace=True)
    rets = prices.pct_change().dropna()
    compounded_rets = (rets['price'] + 1)
    n = 365
    one_day_ret = compounded_rets.iloc[-1:].prod() - 1
    one_week_ret = compounded_rets.iloc[-7:].prod() - 1
    one_month_ret = compounded_rets.iloc[-30:].prod() - 1
    three_month_ret = compounded_rets.iloc[-90:].prod() - 1
    one_year_ret = compounded_rets.iloc[-n:].prod() - 1
    three_year_ret = compounded_rets.iloc[-n*3:].prod() - 1
    five_year_ret = compounded_rets.iloc[-n*5:].prod() - 1

    rets = [one_day_ret, one_week_ret, one_month_ret, one_year_ret, three_year_ret, five_year_ret]
    labels = ['1d','1w','1m','1y', '3y', '5y']

    for i in range(len(rets)):
        if rets[i] < 0:
            rets[i] = str(round(rets[i]*100,1)) + "%\n"
        else:
            rets[i] = " " + str(round(rets[i]*100,1)) + "%\n"

    response = [f'{labels[i]} -->  {rets[i]}' for i in range(len(rets))]


    return_string = ""

    for s in response:
        return_string += s

    print(return_string)
    
    bot.send_message(message.chat.id, return_string)
    
@bot.message_handler(commands=['books'])
def books(message):
    response = ""
    for key, value in books_dict.items():
        response += f'{key}: {value}\n\n'

    print(response)
    
    bot.send_message(message.chat.id, response)


bot.polling()


