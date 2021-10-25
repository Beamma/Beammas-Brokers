import yfinance as yf
#
msft = yf.Ticker("TSLA")
# print(msft)
# get stock info
# print(msft.info)

# get historical market data
history = msft.history(period="7d")
# print(history)

print(max(history['High']))
print(msft.info['shortName'])

# stock_history = []
# for index in history.index:
#     date_price = [index, history.loc[index]['Close']]
#     stock_history.append(date_price)
# print(stock_history)

# show actions (dividends, splits)
# msft.actions
#
# # show dividends
# msft.dividends
#
# # show splits
# msft.splits
#
# # show financials
# msft.financials
# msft.quarterly_financials
#
# # show major holders
# msft.major_holders
#
# # show institutional holders
# msft.institutional_holders
#
# # show balance sheet
# msft.balance_sheet
# msft.quarterly_balance_sheet
#
# # show cashflow
# msft.cashflow
# msft.quarterly_cashflow
#
# # show earnings
# msft.earnings
# msft.quarterly_earnings
#
# # show sustainability
# msft.sustainability
#
# # show analysts recommendations
# msft.recommendations
#
# # show next event (earnings, etc)
# msft.calendar
#
# # show ISIN code - *experimental*
# # ISIN = International Securities Identification Number
# msft.isin
#
# # show options expirations
# msft.options
#
# # get option chain for specific expiration
# opt = msft.option_chain('YYYY-MM-DD')
# data available via: opt.calls, opt.puts
