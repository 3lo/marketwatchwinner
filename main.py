import time
from requests_html import HTMLSession
session = HTMLSession()
print("MarketWatch PythonBot v1")

# MarketWatch Authentication
username = "[ENTER USERNAME]"
password = "[ENTER PASSWORD]"

login_URL = "https://sso.accounts.dowjones.com/usernamepassword/login"
# https://sso.accounts.dowjones.com/public/api/users/validate_userpassword - public api to validate username/password
data = {
    "username": username,
    "password": password,
    "connection": "DJldap",
    "client_id": "5hssEAdMy0mJTICnJNvC9TXEw3Va7jfO",
    "tenant": "sso"
}

r = session.post(url=login_URL, data=data)
print(r)

'''
game_URL = "[ENTER GAME URL]"
g = session.get(url=game_URL)
print(g.html.text)

# Game INFORMATION
[GET] [ENTER GAME URL]/tradeorder?chartingSymbol=STOCK/US/XNYS/{stock}
[POST] [ENTER GAME URL]/trade/submitorder
JSON data
Fuid	STOCK-XNAS-MU
Shares	1
Term	Cancelled
Type	Buy
'''

# Gathering Intel (Pulling Stock Information & Stats)
current = time.strftime('%H:%M:%S')  # print(time.tzname) // need to set timezone for non-EST timezones
open_time = '09:30:00'  # NYSE Opening Time is 9:30 am ET
closing_time = '16:00:00'  # NYSE Closing Time is 4:00 pm ET
print(current, " ", open_time)
if open_time <= current <= closing_time:
    print("trading time")
else:
    print("can't trade")


class Stock:
    def __init__(self, s, p, pe, pb, de, fcf, peg, roe, cr):
        self.symbol = s
        self.price = p
        self.pe_ratio = pe  # lower is better
        self.pb_ratio = pb  # <1 means undervalued
        self.de_ratio = de  # lower is better
        self.free_cash_flow = fcf  # the higher the better
        self.peg_ratio = peg  # <= 1 means undervalued or perfect correlation
        self.return_on_equity = roe  # higher the better (15% or higher)
        self.current_ratio = cr
        info = s, p, pe, pb, de, fcf, peg, roe, cr
        if "N/A" in info:
            del info
        elif float(p) < 2:
            del info
        else:
            print(info)  # can use info[0] + info[1] to print stock name & price


screener_URL = "https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks?offset=0&count=100"
screen = session.get(url=screener_URL)
screening = screen.html.find('td')

stock_symbols = []  # empty array for stock symbols

# scrapes all of the stock symbols
j = 0
for i in range(0, 100):
    stock_symbols.append(screening[j].text)  # putting stock symbols into array
    j = j + 10
print(stock_symbols)  # displays all the stock symbols

finance_URL = 'https://finance.yahoo.com/quote/'
x = 1
for i in range(0, 100):
    statistics = session.get(url=finance_URL + stock_symbols[i] + "/key-statistics?p=" + stock_symbols[i])
    financial = statistics.html.find('td')
    stats = statistics.html.find('span')
    symbol = stock_symbols[i]
    price = screening[x + 1].text
    pe_ratio = financial[5].text
    pb_ratio = financial[13].text
    de_ratio = financial[53].text
    free_cash_flow = financial[61].text
    peg_ratio = financial[9].text
    return_on_equity = financial[29].text
    current_ratio = financial[55].text
    x = x + 10
    stock = Stock(symbol, price, pe_ratio, pb_ratio, de_ratio, free_cash_flow, peg_ratio,
                  return_on_equity, current_ratio)

print("exit")

# z-test formulas to determine the sell price of stocks
# maybe use google docs or excel to monitor the data for each stock