import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import pandas as pd
from pycoingecko import CoinGeckoAPI
from datetime import date
import os
import requests
import json
import tweepy


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


logger = logging.getLogger(__name__)
TOKEN = os.environ.get("API_KEY")

# Twitter Authentication
consumer_key = os.environ.get("consumer_key")
consumer_secret = os.environ.get("consumer_secret")
access_token = os.environ.get("access_token")
access_token_secret = os.environ.get("access_token_secret")


cg = CoinGeckoAPI()

# Initialize variables
commands = ['start', 'price', 'marketcap', 'returns', 'books', 'podcasts', 'wallets', 'mempool', 'treasury', 'maxdrawdown', 'news']
    # Intro
intro = "Type any of the below commands to get started\n\n"
price_def = f"/{commands[1]}: get the current price of Bitcoin in cuck bucks\n"
marketcap_def = f"/{commands[2]}: get the current market cap of Bitcoin in cuck bucks\n"
returns_def = f"/{commands[3]}: get compounded returns for different timeframes\n"
books_def = f"/{commands[4]}: get recommended Bitcoin, economics, privacy, and liberty books\n"
podcasts_def = f"/{commands[5]}: get recommended Bitcoin, economics, privacy, and liberty podcasts\n\n"
wallets_def = f"/{commands[6]}: list of recommneded Bitcoin hardware and software wallets\n"
mempool_def = f"/{commands[7]}: check recommended Bitcoin network fees  \n\n"
treasury_def = f"/{commands[8]}: top 10 companies that hold Bitcoin in treasury\n"
drawdown_def = f"/{commands[9]}: get max drawdown for different timeframes\n"
news_def = f"/{commands[10]}: Twitter Bitcoin and Macro news\n\n"
metrics = [price_def, marketcap_def, returns_def, drawdown_def, treasury_def, mempool_def]
resources = [books_def, podcasts_def]



    # Resources
books_dict = {
    'Inventing Bitcoin: The Technology Behind the First Truly Scarce and Decentralized Money Explained by Yan Pritzker': 'https://rb.gy/vqtj64',
    'Grokking Bitcoin by Kalle Rosenbaum': 'https://rb.gy/gymfxz',
    'The Blocksize War: The Battle for Control Over Bitcoin’s Protocol Rules by Jonathan Bier':'https://rb.gy/4svnhd', 
    'The Bitcoin Standard: The Decentralized Alternative to Central Banking by Saifedean Ammous': 'https://rb.gy/lsfdny',
    'The Sovereign Individual: Mastering the Transition to the Information Age by James Dale Davidson and  William Rees-Mogg': 'https://rb.gy/1ciqvd',
    'Economics in One Lesson by Henry Hazlitt': 'https://rb.gy/btp2qh',
    'What Has Government Done to Our Money by Murray N. Rothbard': 'https://rb.gy/a7objr',
    'The Road to Serfdom by Friedrich Hayek': 'https://rb.gy/vvexny',
    'When Money Dies: The Nightmare of Deficit Spending, Devaluation, and Hyperinflation in Weimar, Germany by Adam Fergusson': 'https://rb.gy/hngvxq',
    'The Law by Frédéric Bastiat': 'https://rb.gy/hfsbcp'
}

podcasts_dict = {
    'Best for newbies - Start from here\n Btcoin Audible' : 'https://bitcoinaudible.com/',
    'Best for contrarian views as well as weekly Bitcoin updates\n Tales from the Crypt' : 'https://talesfromthecrypt.libsyn.com/',
    'Best for actionable advice on Bitcoin tools and privacy (A bit technical and not recommended for new comers)\n Citadel Dispatch' : 'https://citadeldispatch.com/',
    'Best overall for Bitcoin and Austrian Economics\n Stephan Livera Podcast' : 'https://stephanlivera.com/',
    'Best for philosophy and understanding money\n What is Money?' : 'https://whatismoneypodcast.com/episodes/dear-eric-weinstein-D4QstV19',
    'Best for unplugging yourself from the matrix - Good dives into freedom, psychology, and philosophy\n Wake Up Podcast' : 'https://anchor.fm/wakeuppod',
    'Best for those who want to learn more about privacy in a digital world\n Opt Out': 'https://optoutpod.com/'
}

software_wallets_dict = {
    'Best Android and privacy wallet\n Samourai wallet': 'https://samouraiwallet.com/',
    'Best Desktop wallet overall\n Sparrow wallet': 'https://www.sparrowwallet.com/',
    'Best IOS wallet\n Blue wallet': 'https://bluewallet.io/',
    'Best Mobile Lightning wallet\n Muun wallet': 'https://muun.com/'
}

hardware_wallets_dict = {
    'Best overall\n Coldcard': 'https://coldcard.com/',
    'Best for DIY\n SeedSigner': 'https://seedsigner.com/',

}

def start(update, context):
    """Send a message when the command /start is issued."""
    news_output = "UPDATE: New news section available now!\n"
    news_output += news_def
    metrics_output = "Metrics\n"
    resources_output = "Resources\n"
    wallets_output = "Wallets\n"

    for t in metrics:
        metrics_output += t
    for t in resources:
        resources_output += t

    response = intro
    response += news_output
    sections = [metrics_output, resources_output]

    for t in sections:
        response += t

    # Add wallets 
    response += wallets_output
    response += wallets_def

    update.message.reply_text(response)

def price(update, message):
    """Return the price of Bitcoin, in usd, sats per usd, and how many usd needed to become a sats millionaire"""
    price = cg.get_price('bitcoin', 'usd')
    current_price = price['bitcoin']['usd']
    sats_per_dollar = round(100000000 / price['bitcoin']['usd'])
    sats_millionaire = round(1000000 / sats_per_dollar)
    
    response = f'1 BTC = {current_price} USD \n\n 1 USD = {sats_per_dollar} sats \n\n {sats_millionaire} USD to become a sats millionaire'

    update.message.reply_text(response)

def marketCap(update, message):
    """Return the market price of Bitcoin in usd"""
    today = date.today()
    today= today.strftime('%d-%m-%Y')
    data = cg.get_coin_history_by_id('bitcoin', date=today)
    market_cap = data['market_data']['market_cap']['usd']
    market_cap = str(round((market_cap / 1000000000),1)) + "B"
    response = f'{market_cap} cuck bucks'
        
    update.message.reply_text(response)

def returns(update, message):
    """Return Bitcoin's returns for multiple timeframes"""
    df = cg.get_coin_market_chart_by_id('bitcoin','usd','max')
    prices = df['prices']
    prices = pd.DataFrame(prices)
    prices.iloc[:,0] =  pd.to_datetime(prices.iloc[:,0],unit='ms')
    prices.columns = ['date','price']
    prices.index = prices['date']
    prices.drop('date', axis = 1 , inplace=True)
    n = 365
    last_price = prices.iloc[-1]
    one_day_ret = last_price / prices.iloc[-2] - 1
    one_week_ret = last_price / prices.iloc[-7] - 1
    one_month_ret = last_price / prices.iloc[-30] - 1
    three_month_ret = last_price / prices.iloc[-90] - 1
    one_year_ret = last_price / prices.iloc[-n] - 1
    three_year_ret = last_price / prices.iloc[-n*3] - 1
    five_year_ret = last_price / prices.iloc[-n*5] - 1

    rets = [one_day_ret, one_week_ret, one_month_ret, three_month_ret , one_year_ret, three_year_ret, five_year_ret]
    labels = ['1d','1w','1m','3m','1y', '3y', '5y']

    for i in range(len(rets)):
        rets[i] = " " + str(round(rets[i][0]*100,1)) + "%\n"

    string_list = [f'{labels[i]} -->  {rets[i]}' for i in range(len(rets))]

    response = "Returns refer to the change in cuck buck price of Bitcoin. Bitcoin's returns measured in bitcoin are 0. Remember that one bitcoin is one bitcoin\n\n"

    for s in string_list:
        response += s + '\n'

    update.message.reply_text(response)  

def books(update, message):
    """Return recommended books to read"""
    response = ""
    for key, value in books_dict.items():
        response += f'{key}: {value}\n\n'
    
    update.message.reply_text(response)

def podcasts(update, message):
    """Return recommeded podcasts to listen to"""
    response = ""
    for key, value in podcasts_dict.items():
        response += f'{key}: {value}\n\n'
    
    update.message.reply_text(response)

def wallets(update, message):
    """Return recommended software and hardware wallets to use"""
    response = "" 
    sw_text = "----Software Wallets----\n\n"
    hw_text = "\n----Hardware Wallets----\n\n"

    response += sw_text

    for key,value in software_wallets_dict.items():
        response += f'{key}: {value}\n\n'

    response += hw_text

    for key, value in hardware_wallets_dict.items():
        response += f'{key}: {value}\n\n'

    update.message.reply_text(response)

def mempool(update, message):
    """Return recommended mempool fees"""
    response = "Mempool refers to the transactions pending to be mined. The higher the number of transactions in mempool both in terms of count and size, the higher the Bitcoin network fees because senders bid for limited block space. On average, one block contains 2k transactions (depending on transaction size) and is mined every 10 minutes\n\n"
    recommended_link = "https://mempool.space/"
    fees_link = "https://mempool.space/api/v1/fees/recommended"

    mempool_fees = requests.get(fees_link).content
    mempool_fees = json.loads(mempool_fees.decode('utf-8'))
    mempool_fees = pd.DataFrame(mempool_fees.items())
    mempool_fees.iloc[:, 1] = 10*"-" + mempool_fees.iloc[:,1].astype('str') + " sat/vB"
    mempool_fees.iloc[:,0] = 10*"-" + mempool_fees.iloc[:,0]
    mempool_fees_string = mempool_fees.to_string(index=False, header=False)

    response += 'Current recommended fees\n'
    response += mempool_fees_string
    response += f'\n\n Learn more: {recommended_link}'

    update.message.reply_text(response)

def treasury(update, context):
    """Return top 10 companies that hold Bitcoin in treausry"""
    df = cg.get_companies_public_treasury_by_coin_id('bitcoin')
    df = pd.DataFrame(df['companies'])
    # Clean up numeric column formatting
    df['total_entry_value_usd'] = round(df['total_entry_value_usd'] / 1000000).astype('int').astype('string') + 'M'
    df['total_current_value_usd'] = round(df['total_current_value_usd'] / 1000000).astype('int').astype('string') + 'M'
    df['percentage_of_total_supply'] = round(df['percentage_of_total_supply'],4).astype('string') + '%'

    response = ""

    for i in range(10):
        treasury = df.iloc[i,:]
        response += treasury.to_string() + '\n\n'

    update.message.reply_text(response)

def max_drawdown(update, context):
    """Return max drawdon of Bitcoin across multiple timeframes"""
    df = cg.get_coin_market_chart_by_id('bitcoin','usd','max')
    prices = df['prices']
    prices = pd.DataFrame(prices)
    prices.iloc[:,0] =  pd.to_datetime(prices.iloc[:,0],unit='ms')
    prices.columns = ['date','price']
    prices.index = prices['date']
    prices.drop('date', axis = 1 , inplace=True)

    def get_max_drawdown(prices):
        dd = prices / prices.cummax() - 1
        return (dd.idxmin(), dd.min())

    n = 365
    one_week_prices = prices.iloc[-7:]
    one_month_prices = prices.iloc[-30:]
    three_month_prices = prices.iloc[-90:]
    one_year_prices = prices.iloc[-n:]
    three_year_prices = prices.iloc[-n*3:]
    five_year_prices = prices.iloc[-n*5:]

    prices = [one_week_prices, one_month_prices, three_month_prices, one_year_prices, three_year_prices, five_year_prices]
    labels = ['1w','1m','3m', '1y', '3y', '5y']

    dds = [get_max_drawdown(prices[i]) for i in range(len(prices))]
    response = "Max drawdown represents peak-trough decline for a given period. For example, given the same period of past 1 month, if max price was 60K and min price was 40K, then max drawdown would be -33%\n\n"

    for i in range(len(dds)):
        date_, dd_ = dds[i]
        dd_ = str(round(dd_[0]*100,2)) + "%"
        response += f'{labels[i]} --> {dd_} \n\n'

    update.message.reply_text(response)

# Add timeline tweets 
callback_uri = 'oob' 
auth = tweepy.OAuthHandler(consumer_key, consumer_secret, access_token, access_token_secret, callback_uri)
api = tweepy.API(auth)
authors = ['zerohedge','BitcoinMagazine', 'Fxhedgers', 'WallStreetSilv', 'LynAldenContact']

def extract_timeline_as_df(timeline_list, authors):
    columns = set()
    allowed_types = [str, int]
    tweets_data = []
    for status in timeline_list:
        status_dict = dict(vars(status))
        keys = status_dict.keys()
        single_tweet_data = {"created_at": status_dict['_json']['created_at'], "user": status.user.screen_name, "author": status.author.screen_name}

        for k in keys:
            try:
                v_type = type(status_dict[k])
            except:
                v_type = None
            if v_type != None:
                if v_type in allowed_types:
                    single_tweet_data[k] = status_dict[k]
                    columns.add(k)
        tweets_data.append(single_tweet_data)
    header_cols = list(columns)
    header_cols.append('created_at')
    header_cols.append('user')
    header_cols.append('author')
    
    df = pd.DataFrame(tweets_data, columns = header_cols)
    df = df[df.user.isin(authors)][['user','text', 'created_at']]
    return df


def twitter_news(update, context):
    my_timeline = api.home_timeline()
    twitter_timeline = extract_timeline_as_df(my_timeline, authors)
    n = twitter_timeline.shape[0]
    for i in range(n):
        cols = list(twitter_timeline.columns)
        response = ""
        for col in range(len(cols)):
            response += twitter_timeline.iloc[i,col] + "\n\n"
        response += "-------------\n"

    update.message.reply_text(response)


def echo(update, context):
    """Echo the user message."""
    #update.message.reply_text(update.message.text)
    response = "Send /start to check the list of valid commands"

    update.message.reply_text(response)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler(commands[0], start))
    dp.add_handler(CommandHandler(commands[1], price))
    dp.add_handler(CommandHandler(commands[2], marketCap))
    dp.add_handler(CommandHandler(commands[3], returns))
    dp.add_handler(CommandHandler(commands[4], books))
    dp.add_handler(CommandHandler(commands[5], podcasts))
    dp.add_handler(CommandHandler(commands[6], wallets))
    dp.add_handler(CommandHandler(commands[7], mempool))
    dp.add_handler(CommandHandler(commands[8], treasury))
    dp.add_handler(CommandHandler(commands[9], max_drawdown))
    dp.add_handler(CommandHandler(commands[10], twitter_news))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    # Heroku 
    main()


