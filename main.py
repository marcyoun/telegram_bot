import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import pandas as pd
from pycoingecko import CoinGeckoAPI
from datetime import date
import os

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)


logger = logging.getLogger(__name__)
TOKEN = os.environ.get("API_KEY")

cg = CoinGeckoAPI()

# Initialize variables
commands = ['start', 'price', 'marketcap', 'returns', 'books', 'podcasts', 'wallets', 'mempool', 'treasury']
    # Intro
intro = "Type any of the below commands to get started\n\n"
price_def = f"/{commands[1]}: get the current price of Bitcoin in cuck bucks\n"
marketcap_def = f"/{commands[2]}: get the current market cap of Bitcoin in cuck bucks\n"
returns_def = f"/{commands[3]}: get historical compounded returns in percentage\n"
books_def = f"/{commands[4]}: get recommended Bitcoin, economics, privacy, and liberty books\n"
podcasts_def = f"/{commands[5]}: get recommended Bitcoin, economics, privacy, and liberty podcasts\n"
wallets_def = f"/{commands[6]}: list of recommneded Bitcoin hardware and software wallets\n"
mempool_def = f"/{commands[7]}: recommended websites to check Bitcoin's mempool\n\n"
treasury_def = f"/{commands[8]}: top 10 companies that hold Bitcoin in treasury\n\n"
metrics = [price_def, marketcap_def, returns_def, treasury_def]
resources = [books_def, podcasts_def, mempool_def]


    # Resources
books_dict = {
    'Inventing Bitcoin: The Technology Behind the First Truly Scarce and Decentralized Money Explained': 'https://rb.gy/vqtj64',
    'Grokking Bitcoin': 'https://rb.gy/gymfxz',
    'The Blocksize War: The Battle for Control Over Bitcoin’s Protocol Rules':'https://rb.gy/4svnhd', 
    'The Bitcoin Standard: The Decentralized Alternative to Central Banking': 'https://rb.gy/lsfdny',
    'The Sovereign Individual: Mastering the Transition to the Information Age': 'https://rb.gy/1ciqvd',
    'Economics in One Lesson': 'https://rb.gy/btp2qh',
    'What Has Government Done to Our Money?': 'https://rb.gy/a7objr',
    'The Road to Serfdom': 'https://rb.gy/vvexny',
    'When Money Dies: The Nightmare of Deficit Spending, Devaluation, and Hyperinflation in Weimar, Germany': 'https://rb.gy/hngvxq',
    'The Law': 'https://rb.gy/hfsbcp'
}

podcasts_dict = {
    'Tales from the Crypt': 'https://talesfromthecrypt.libsyn.com/',
    'Citadel Dispatch': 'https://citadeldispatch.com/',
    'Stephan Livera Podcast': 'https://stephanlivera.com/',
    'What is Money?' : 'https://whatismoneypodcast.com/episodes/dear-eric-weinstein-D4QstV19',
    'Wake Up Podcast': 'https://anchor.fm/wakeuppod',
    'Opt Out': 'https://optoutpod.com/'
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

mempoool_dict = {
    'Best overall\n Mempool .space': 'https://mempool.space/'
}

def start(update, context):
    """Send a message when the command /start is issued."""
    metrics_output = "Metrics\n"
    resources_output = "Resources\n"
    wallets_output = "Wallets\n"

    for t in metrics:
        metrics_output += t
    for t in resources:
        resources_output += t

    response = intro
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
    """Return Bitcoin's compounded returns for multiple timeframes"""
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

    string_list = [f'{labels[i]} -->  {rets[i]}' for i in range(len(rets))]


    response = ""

    for s in string_list:
        response += s

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
    """Return recommended websites to check mempool"""
    """Ret"""
    response = ""
    mempool_text = "Mempool refers to the transactions pending to be mined. The higher the number of transactions in mempool both in terms of count and size, the higher the Bitcoin network fees because senders bid for limited block space. On average, one block contains 2k transactions (depending on transaction size) and is mined every 10 minutes\n\n"
    response+= mempool_text

    for key, value in mempoool_dict.items():
        response+= f'{key}: {value}\n\n'

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

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()

