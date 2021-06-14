# import http.client
# import json
#
# conn = http.client.HTTPSConnection("yahoo-finance-low-latency.p.rapidapi.com")
#
# headers = {
#     'x-rapidapi-key': "ad2a76ef08msh111b0faa42d8165p1c3321jsn7b86be045c34",
#     'x-rapidapi-host': "yahoo-finance-low-latency.p.rapidapi.com"
#     }
#
# conn.request("GET", "/v8/finance/spark?symbols=AAPL&range=max&interval=15m", headers=headers)
#
# res = conn.getresponse()
# data = res.read()
#
# stocks = data.decode("utf-8")
# dictionary = json.loads(stocks)
# appl = dictionary.get("AAPL")
# times = appl.get("timestamp")
# prices = appl.get("close")
#
# stock_history = []
# for i in range(len(prices)):
#     data = ["Time:", times[i], "Price:", prices[i]]
#     stock_history.append(data)
# print(stock_history)




# import models
# email_status = "passed"
# input = input()
# user = models.User.query.all()
# for user in user:
#     if input == user.email:
#         break
#         email_status = "failed"
# print(email_status)
