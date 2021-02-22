from datetime import datetime, timedelta
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas

import threading
import time

class IBapi(EWrapper, EClient):	
	def __init__(self):
		EClient.__init__(self, self)
		self.connect('127.0.0.1', 7497, 123)
		api_thread = threading.Thread(target=self.run_loop, daemon=True)
		api_thread.start()
		self.data = [] 
		time.sleep(1)

	def run_loop(self):
		self.run()

	def historicalData(self, reqId, bar):
		#print(f'Time: {bar.date} {bar.open} {bar.high} {bar.low} {bar.close} {bar.volume}')
		self.data.append([bar.date, bar.open, bar.high, bar.low, bar.close])


	def createStockContract(self, window_size, end_date, bar_size, ticker, security='STK', exch='SMART', msr ='MIDPOINT' ):
		self.data = []
		eurusd_contract = Contract()
		eurusd_contract.symbol = ticker
		eurusd_contract.secType = security
		eurusd_contract.exchange = exch
		eurusd_contract.currency = 'USD'
		#'2021-02-16 16:05:00'
		self.reqHistoricalData(1, eurusd_contract, end_date, window_size, bar_size, msr, 0, 1, False, [])
		time.sleep(10)
		self.write_prices(ticker)
	
	def write_prices(self, filename):
		df = pandas.DataFrame(self.data, columns=['Time', 'Open', 'High', 'Low', 'Close'])
		df['Time'] = pandas.to_datetime(df['Time']).dt.strftime("%d/%m/%Y %H:%M:%S")
		df = df.set_index('Time')
		df.to_csv(f'C:\\Temp\\{filename}.csv', header=None)  

	