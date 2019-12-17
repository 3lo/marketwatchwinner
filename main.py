import time
import statistics
import math
from requests_html import HTMLSession
from prettytable import PrettyTable
session = HTMLSession()
print("MarketWatch PythonBot v1")

# Gathering Intel (Pulling Stock Information & Stats)
current = time.strftime('%H:%M:%S')  # print(time.tzname) // need to set timezone for non-EST timezones
open_time = '09:30:00'  # NYSE Opening Time is 9:30 am ET
closing_time = '16:00:00'  # NYSE Closing Time is 4:00 pm ET
print(current, " ", open_time)


def weekend():
    day = str(time.strftime("%A"))
    if "Sat" in day or "Sun" in day:
        return bool(False)
    else:
        return bool(True)


if open_time <= current <= closing_time and weekend():
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
        self.price_list = []
        self.info = self.symbol, self.price, self.pe_ratio, self.pb_ratio, self.de_ratio, self.free_cash_flow,\
                    self.peg_ratio, self.return_on_equity, self.current_ratio


screener_URL = "https://finance.yahoo.com/screener/predefined/undervalued_growth_stocks?offset=0&count=100"
screen = session.get(url=screener_URL)
screening = screen.html.find('td')

stock_symbols = []  # empty array for stock symbols

# scrapes all of the stock symbols
j = 0
for i in range(0, 100):
    stock_symbols.append(screening[j].text)  # putting stock symbols into array
    j = j + 10
# print(stock_symbols)  # displays all the stock symbols

finance_URL = 'https://finance.yahoo.com/quote/'
x = 1
y = 4
stockList = []
for i in range(0, 100):
    priceList = []
    stats = session.get(url=finance_URL + stock_symbols[i] + "/key-statistics?p=" + stock_symbols[i])
    financial = stats.html.find('td')
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
    if "N/A" not in stock.info and float(stock.price) > 2:
        history = session.get(url=finance_URL + stock_symbols[i] + "/history?p=" + stock_symbols[i])
        price_history = history.html.find('td')
        # get the closing prices of the last 10 days
        for z in range(0, 10):
            try:
                priceList.append(float(price_history[y].text))
            except ValueError:
                priceList.append(float(price_history[y+1].text))
            y = y + 7
            if y >= 74:
                y = 4
        stock.price_list = priceList
        stockList.append(stock)

table = PrettyTable()
table.field_names = ["Symbol", "Price", "PE Ratio", "PB Ratio", "DE Ratio", "Free Cash Flow", "PEG Ratio",
                     "Return on Equity", "Current Ratio", "LCL", "Sale Price", "UCL"]

for stock in stockList:
    meanx = statistics.mean(stock.price_list)
    standard_deviation = statistics.stdev(stock.price_list)
    o = standard_deviation / math.sqrt(10)

    UCL = round(meanx + (2.262 * o), 2)
    LCL = round(meanx - (2.262 * o), 2)

    percentList = []
    for money in range(int(LCL), int(UCL) + 2):
        percentage = 1.0 - ((money - meanx) / standard_deviation)
        percentage = round(percentage * 100, 2)
        if percentage < 100:  # can't have +100%
            percentList.append(str(percentage) + " " + str(money))
            maxPercent = max(percentList)
    swap = maxPercent.split(" ")

    probability = swap[1] + " (" + swap[0] + "%)"
    table.add_row([stock.symbol, stock.price, stock.pe_ratio, stock.pb_ratio, stock.de_ratio, stock.free_cash_flow,
                  stock.peg_ratio, stock.return_on_equity, stock.current_ratio, LCL, probability, UCL])

print(table)
print("exit")
