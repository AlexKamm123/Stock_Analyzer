from computations import computations
from scraper import scraper

refURL = "https://www.marketwatch.com/investing/stock/pbi/financials/balance-sheet/quarter"
stock1 = scraper("abev")

quick_ratio = stock1.get_quick_ratio()
current_ratio = stock1.get_current_ratio()
debt_to_equity_ratio = stock1.get_debt_to_equity_ratio()
price_to_earnings_ratio = stock1.get_debt_to_equity_ratio()
roe = stock1.get_return_on_equity()

print(f"quick ratio: {quick_ratio}")
print(f"current ratio: {current_ratio}")
print(f"debt to equity ratio: {debt_to_equity_ratio}")
print(f"price to earnings ratio: {price_to_earnings_ratio}")
print(f"return on equity: {roe}%")