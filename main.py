from scraper import scraper
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import numpy as np


tickers = [] #stores user inputs
num_stocks = input("how many stock tickers do you want to enter? (max of 5)\n")
while (not str.isdigit(num_stocks)):
        num_stocks = input("Please enter an integer (1 - 5)\n")

num_stocks = int(num_stocks)

# getting valid user inputs and storing in list
i = 1
while i <= num_stocks:
    if i <= 5:
        stock = input("ticker #" + str(i) + ": ")
        validity = scraper.is_valid(stock)
        if validity[0] == 1:
            print(f"{stock} is not a valid ticker")
            i-=1
        elif validity[0] == 2:
            print(f"{stock} is on ({validity[1]}), not on the NYSE or NASDAQ")
            i-=1
        elif validity[0] == 3:
            print(f"{stock} has insufficient data avilable")
            i-=1
        else:
            tickers.append(stock)
    i+=1

    


WIDTH = 0.4/len(tickers) + 0.1 # width value of bars
count = 0 # used to format bar graph
ratios = ["Quick", "Current", "Debt to Equity", "Price to Earnings", "Return on Equity(%)"]
plt.figure(figsize=(12, 6), dpi=100, num = 1)
plt.axes().set_facecolor("#f0f0f0")
xpos = np.arange(len(ratios))
plt.xticks(xpos + (len(tickers)/10) - 0.1, ratios, fontsize = 10, fontfamily = "serif")

# calculating data and plotting it
for ticker in tickers:
    scrape = scraper(ticker)

    qr = scrape.get_quick_ratio()
    cr = scrape.get_current_ratio()
    dte = scrape.get_debt_to_equity_ratio()
    pte = scrape.get_price_to_earnings_ratio()
    roe = scrape.get_return_on_equity()

    #print(f"qr = {qr}, cr = {cr}, dte = {dte}, pte = {pte}, roe = {roe}")

    values = [qr, cr, dte, pte, roe]
    values = [np.nan if val == "NA" else val for val in values]
    bar = plt.bar(xpos + WIDTH * count, values, WIDTH, label = ticker, edgecolor = "black")
    plt.bar_label(bar, fontsize = 8, padding = 3)

    count +=1
axis_font = {'family': "serif", "color": "darkred", "size": 12}
title_font = {"family": "serif", "color": "black", "size": 18}


plt.title("Stock Evaluation Ratios", fontdict = title_font)
plt.xlabel("Ratios", fontdict = axis_font)
plt.ylabel("Values", fontdict = axis_font)
plt.legend(prop = {"size": 10, "family": "serif"}, facecolor = "#f0f0f0", loc = "upper left")

plt.show()
