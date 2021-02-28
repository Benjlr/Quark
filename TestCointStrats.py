
from ib_insync.contract import CFD
from ib_insync.ib import IB
from ib_insync.order import LimitOrder, MarketOrder
from Trade import Trader


gert = Trader()
gert.PrimeKalman()
gert.StartTrading()
#ib = IB()
#ib.connect('127.0.0.1', 7497, clientId=1)   
#contractcba = CFD('CBA', currency= 'AUD')
#ib.qualifyContracts(contractcba)
#orderBuy = LimitOrder('SELL', 10,75.50 )
#tradeX = ib.placeOrder(contractcba, orderBuy)

IB.sleep(60*60*12)


