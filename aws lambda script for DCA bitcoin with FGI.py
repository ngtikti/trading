import json
import gemini
import requests

public_key = ""  
private_key = ""
symbol = "BTCSGD"
tick_size = 8
#update symbol based on what crypto/fiat pair you want to buy. Default is BTCUSD, change to BTCEUR for Euros or ETHUSD for Ethereum (for example) - see all possibilities down in symbols and minimums link
#update tick size based on what crypto-pair you are buying. BTC is 8. Check out the API link below to see what you need for your pair
#https://docs.gemini.com/rest-api/#symbols-and-minimums

def _buyBitcoin(buy_size,pub_key, priv_key):
    # Set up a buy for 0.999 times the current price add more decimals for a higher price and faster fill, if the price is too close to spot your order won't post. 
    # Lower factor makes the order cheaper but fills quickly (0.5 would set an order for half the price and so your order could take months/years/never to fill)
    trader = gemini.PrivateClient(pub_key, priv_key)
    factor = 0.999
    price = str(round(float(trader.get_ticker(symbol)['ask'])*factor,2))

    #set amount to the most precise rounding (tick_size) and multiply by 0.999 for fee inclusion - if you make an order for $20.00 there should be $19.98 coin bought and $0.02 (0.10% fee)
    amount = round((buy_size*.999)/float(price),tick_size)
		
    #execute maker buy with the appropriate symbol, amount, and calculated price
    buy = trader.new_order(symbol, str(amount), price, "buy", ["maker-or-cancel"])
    print(f'Maker Buy: {buy}')

###########################################################################################################################################################################
#defining new function to remove spaces from text in site
def remove(string):
    return "".join(string.split())

#defining function to get crypto FGI index    
def getFGI():
    x = requests.get('https://alternative.me/crypto/fear-and-greed-index/')
    sitetext = remove(x.text)
    y=sitetext.split(">")
    indexofnow=y.index("Now</div")
    z=y[indexofnow+6].split("<")
    
    try: 
        FGInow=int(z[0])
    except:
        FGInow=-1
    
    return FGInow


#buying BTCSGD incorporating FGI data
def lambda_handler(event, context):
    #get FGI for the day
    d=getFGI()
    
    #conditions to buy BTCSGD weekly (eg. Neutral = 50SGD, Greed = 25SGD, Fear = 75SGD, Extreme Fear = 100SGD)
    if d>75:
        print("Extreme Greed. Won't buy")
    
    elif (d>55 and d<=75):
        print("Greed. Buy just a little")
        _buyBitcoin(50, public_key, private_key)
    
    elif (d>45 and d<=55):
        print("Neutral. Buy")
        _buyBitcoin(100, public_key, private_key)
    
    elif (d>25 and d<=45):
        print("Fear. Buy a little more")
        _buyBitcoin(200, public_key, private_key)
    
    elif(d<=25 and d>=0):
        print("Extreme Fear. Buy more!")
        _buyBitcoin(400, public_key, private_key)
    
    elif (d==-1):
        print("Something went wrong with extracting FGI data")
    
    else:
        print("Something went wrong with extracting FGI data")
        
    
    return {
        'statusCode': 200,
        'body': json.dumps('End of script')
    }