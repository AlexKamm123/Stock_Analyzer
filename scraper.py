from bs4 import BeautifulSoup
import requests

class scraper:
    """
    class to scrape data off of balance sheets, income statments, and necessary websites to
    then calculate 5 common ratios used to evaluate a stock
    """


    def __init__(self, ticker):
        """
        Creates a new scraper object
        and initializes fields
        """
        self.ticker = ticker

        self.income_url = "https://www.marketwatch.com/investing/stock/" + str(ticker) + "/financials/income/quarter"
        self.income_result = requests.get(self.income_url)
        self.income_doc = BeautifulSoup(self.income_result.text, "html.parser")

        self.url = "https://marketwatch.com/investing/stock/" + str(ticker) + "/financials/balance-sheet/quarter"
        self.result = requests.get(self.url)
        self.doc = BeautifulSoup(self.result.text, "html.parser")

        # setting data
        self.quarterly_assets = self.get_quarterly_assets()
        self.quarterly_liabilities = self.get_quarterly_liabilities()
        self.eps = self.get_eps()
        self.curr_price = self.get_curr_price()
        self.quarter_net_income = self.get_quarter_net_income()
        self.previous_equity = self.get_previous_equity()

    @staticmethod
    def is_valid(ticker):
        """
        Ensures that the link with the given ticker symbol
        is valid, meaning this ticker exists and has data available.
        returns tuple (0) if ticker is valid
        returns tuple (1) if ticker doesn't exist
        returns tuple (2, <name of exchange>) if ticker is not on NASDAQ or NYSE
        returns tuple (3) if ticker has no data available
        """
        try:

            main_url = "https://marketwatch.com/investing/stock/" + str(ticker) + "/financials/balance-sheet/quarter"
            main_result = requests.get(main_url)
            main_doc = BeautifulSoup(main_result.text, "html.parser")
            exchange = main_doc.find(class_ = "company__market").text

            if exchange != "U.S.: Nasdaq" and exchange !="U.S.: NYSE":
                return (2, exchange)# if ticker is on wrong exchange
        except:
            return (1,) # if ticker doesn't exist
        
        try:
            scrapeTest = scraper(ticker)
        except:
            return (3,) # if the data doesn't exist
        

        return (0,) # if everything passes

            


    def get_quarterly_assets(self) -> dict:
        """
        gets all of the asset data of the balance sheet
        for the most recent quearter
        """
        tbody1 = self.doc.find("tbody", class_="table__body row-hover")
        rows1 = tbody1.find_all("span")
        rows_names1 = tbody1.find_all(class_="overflow__cell fixed--column")
        count = 0
        assets_data = []
        assets_names = []

        #for data
        for val in rows1:
            if count == 4:
                count = -1
                assets_data.append(self.num_format(val.string))
            count+=1

        #for names
        for val in rows_names1:
            for data in val.contents:
                if(data.string != "\n" and data.string not in assets_names):
                    assets_names.append(self.num_format(data.getText()))

        assets = dict(zip(assets_names, assets_data))
        return assets

    def get_quarterly_liabilities(self) -> dict:
        """
        gets the most recent months data on the balance
        sheet for the Liabilites section
        """

        tbody2 = self.doc.find_all("tbody")[4]
        rows2 = tbody2.find_all("span")
        rows_names2 = tbody2.find_all(class_="overflow__cell fixed--column")
        count = 0
        liabilities_data = []
        liabilities_names = []

        #for data
        for val in rows2:
            if count == 4:
                count = -1
                liabilities_data.append(self.num_format(val.string))
            count+=1

        #for names
        for val in rows_names2:
            for data in val.contents:
                if(data.string != "\n" and data.string not in liabilities_names):
                    liabilities_names.append(self.num_format(data.getText()))

        liabilities = dict(zip(liabilities_names, liabilities_data))
        return liabilities

    def get_eps(self) -> float:
        """
        gets the TTM eps of the company
        """
        try:
            row = self.income_doc.find(text = "EPS (Diluted)").parent.parent.parent
            data = row.find_all("td")
            eps = 0
            for cell in data[2:len(data) - 1]:
                if cell.text[0] == "(":
                    negative = cell.text[1:len(cell.text)-1]
                    negative = float(negative)
                    negative *= -1
                    eps += negative
                else:
                    eps += float(cell.text)
            return eps
        except:
            return 0

    def get_curr_price(self) -> float:
        """
        gets the current trading price of company
        """

        section = self.doc.find(class_ = "intraday__data")
        value = section.find(class_ = "value")
        try:
            value = float(value.string)
            return value
        except:
            return 0

    def get_quarter_net_income(self) -> float:
        """
        gets the most recent quarters net income
        off of the companies income statment
        """
        row = self.income_doc.find(text = "Net Income").parent.parent.parent
        data = row.find_all("td")[5].text
        if data[0] == "(":
            negative = data[1:len(data)-1]
            negative = self.num_format(negative)
            data = negative * -1
        else:
            data = self.num_format(data)
        return data

    def get_previous_equity(self) -> float:
        """
        gets the total stockholder equity of the 
        second most recent quarter to be used in the 
        calculation for the ROE%
        """
        row = self.doc.find(text = "Total Equity").parent.parent.parent
        data = row.find_all("td")[4].text
        data = self.num_format(data)
        return data
        
    def num_format(self, num):
        """
        data from balance sheet is in format
        5.6M to represent 5_000_000. This method
        converts strings to correct format
        """
        
        if num[-1] == "T":
            num = num[0: len(num) - 1]
            num = float(num)
            num *= 1_000_000_000_000
        elif num[-1] == "B":
            num = num[0: len(num) - 1]
            num = float(num)
            num *= 1_000_000_000
        elif num[-1] == "M":
            num = num[0: len(num) - 1]
            num = float(num)
            num *= 1_000_000
        elif num[-1] == "K":
            num = num[0: len(num) - 1]
            num = float(num)
            num *= 1_000
        elif num == "-":
            num = 0
        return num

    def get_quick_ratio(self) -> float:
        """
        calculates the quick ratio for the most 
        recent quarter of the stock
        and returns NA if its 0 or there was an error
        with the data (some companies dont have data for every section)
        """
        try:
            numerator = (self.quarterly_assets["Total Current Assets"] - self.quarterly_assets["Inventories"])
            denominator =  self.quarterly_liabilities["Total Current Liabilities"]
            qr = numerator / denominator
            if qr == 0:
                return "NA"
            return round(qr, 2)
        except:
            return "NA"
    
    def get_current_ratio(self) -> float:
        """
        calculates the current ratio for the most 
        recent quarter of the stock
        and returns NA if its 0 or there was an error
        with the data (some companies dont have data for every section)
        """
        try:
            cr = self.quarterly_assets["Total Current Assets"] / self.quarterly_liabilities["Total Current Liabilities"]
            if cr == 0:
                return "NA"
            return round(cr, 2)
        except:
            return "NA"

    def get_debt_to_equity_ratio(self) -> float:
        """
        calculates the debt to equity ratio for the most
        recent quarter of the stock
        and returns NA if its 0 or there was an error
        with the data (some companies dont have data for every section)
        """
        try:
            numerator = self.quarterly_liabilities["ST Debt & Current Portion LT Debt"] + self.quarterly_liabilities["Long-Term Debt"]
            denominator = self.quarterly_liabilities["Total Shareholders' Equity"]
            dte = numerator / denominator
            if dte == 0:
                return "NA"
            return round(dte, 2)
        except:
            return "NA"

    def get_price_to_earnings_ratio(self) -> float:
        """
        calculates the price to earnings ratio for the most
        recent quarter of the stock
        and returns NA if its 0 or there was an error
        with the data (some companies dont have data for every section)
        """
        if self.eps == 0:
            return "NA"
        pte = self.curr_price / self.eps
        return round(pte, 2)

    def get_return_on_equity(self) -> float:
        """
        calculates the return on equity ratio for the most
        recent quarter of the the stock
        and returns NA if its 0 or there was an error
        with the data (some companies dont have data for every section)
        """
        try:
            numerator = ( self.quarter_net_income * 4 ) 
            denominator = ( (self.quarterly_liabilities["Total Equity"] + self.previous_equity) / 2 )
            roe = (numerator / denominator) * 100
            if roe == 0:
                return "NA"
            return round(roe, 2)
        except:
            return "NA"