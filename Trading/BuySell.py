
from ib_insync import contract
from ib_insync.contract import Contract
from ib_insync.ib import IB
from ib_insync.order import LimitOrder, MarketOrder, Trade
from ib_insync import *


class BuySell:
    leverage = 100    
    
    def __init__(self,  ib , contractX, contractY):        
        self.ibConnection = ib
        self.tradeContractX = contractX
        self.tradeContractY = contractY
        self.long = False
        self.short = False
        self.Qualify()
        
    def LongEntry(self, ratio, xclose, yclose):
        self.sharesX = self.leverage 
        self.sharesY = round(self.leverage * ratio)

        orderBuy = LimitOrder('BUY', self.sharesX, xclose+5)
        orderSell = LimitOrder('SELL', self.sharesY, yclose-5)
        self.tradeX = self.ibConnection.placeOrder(self.tradeContractX, orderBuy)
        self.tradeY = self.ibConnection.placeOrder(self.tradeContractY, orderSell)
        self.long = True

    def ShortEntry(self,ratio, xclose, yclose):
        self.sharesX = self.leverage 
        self.sharesY = round(self.leverage * ratio)
        orderSell = LimitOrder('SELL', self.sharesX, xclose-5)
        orderBuy = LimitOrder('BUY', self.sharesY, yclose+5)
        self.tradeX = self.ibConnection.placeOrder(self.tradeContractX, orderSell)
        self.tradeY = self.ibConnection.placeOrder(self.tradeContractY, orderBuy)
        self.short = True


    def ExitLong(self,xclose, yclose):
        orderBuy = LimitOrder('SELL', self.sharesX, xclose-5)
        orderSell = LimitOrder('BUY', self.sharesY, yclose+5)
        self.tradeX = self.ibConnection.placeOrder(self.tradeContractX, orderBuy)
        self.tradeY = self.ibConnection.placeOrder(self.tradeContractY, orderSell)
        self.long = False
        


    def ExitShort(self,xclose, yclose):
        orderSell = LimitOrder('BUY', self.sharesX, xclose+5)
        orderBuy = LimitOrder('SELL', self.sharesY, yclose-5)
        self.tradeX = self.ibConnection.placeOrder(self.tradeContractX, orderSell)
        self.tradeY = self.ibConnection.placeOrder(self.tradeContractY, orderBuy)
        self.short = False

    def Qualify(self):
        self.ibConnection.qualifyContracts(self.tradeContractX)
        self.ibConnection.qualifyContracts(self.tradeContractY)