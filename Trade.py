
import numpy as np
import ib_insync
from ib_insync.contract import Forex
from ib_insync.ib import IB
import kalman
from ib_insync import *



class Trader:
    myKal = kalman.Kalman() 
    #contractEWA = CFD('EWA', 'SMART', 'USD')
    #contractEWC = CFD('EWC', 'SMART', 'USD')
    contractEWA = Forex('CADUSD')
    contractEWC = Forex('AUDUSD')

    ewaBar = None
    ewcBar = None
    

    def __init__(self):
        
        self.ib = IB()
        self.ib.connect('127.0.0.1', 7497, clientId=1)
        print(self.ib.isConnected())
        print(self.ib.pnl())
        
        self.EWABars = self.ib.reqRealTimeBars(
        self.contractEWA, 5, 'MIDPOINT', False)
        self.EWABars.updateEvent += self.onBarUpdateEWA
        print(self.EWABars)

        self.EWCBars = self.ib.reqRealTimeBars(
        self.contractEWC, 5, 'MIDPOINT', False)
        self.EWCBars.updateEvent += self.onBarUpdateEWC
        print(self.EWCBars)



    def onBarUpdateEWA(self, bars, hasNewBar):   
        if self.CheckTime(bars.date.dt):
            self.ewaBar = bars[len(bars)-1]
            self.checkUpdate()


    def onBarUpdateEWC( self, bars, hasNewBar):
        if self.CheckTime(bars.date.dt):
            self.ewcBar = bars[len(bars)-1]
            self.checkUpdate()


    def checkUpdate(self):
        if self.ewcBar != None and self.ewaBar != None:
            self.myKal.update_prediction(self.ewaBar.close, self.ewcBar.close)
            #checkExits first
            if self.myKal.e > 0 & self.long:
                #ext

            if self.myKal.e < 0 & self.short:
                #ext

            if self.myKal.e < -np.sqrt(self.myKal.Q) & ~self.long:
                self.LongEntry()

            if self.myKal.e > np.sqrt(self.myKal.Q) & ~self.short:
                self.ShortEntry()

            print(f'{self.ewaBar.close}, {self.ewcBar.close}')
            print(self.myKal.beta[:, self.myKal.iter])
            self.ewaBar = None
            self.ewcBar = None
        

    def CheckTime(datetime):
        if (datetime.minute == 00 |
            datetime.minute == 15 | 
            datetime.minute == 30 |
            datetime.minute == 45):
                if datetime.second == 00:
                    return True
        return False

    leverage = 100
    long =False
    short = False
    tradeX = Trade()
    tradeY = Trade()

    def LongEntry(self):
        XXShares = self.leverage 
        YYShares = self.leverage * self.myKal.beta[:, self.myKal.iter][0]
        self.ib.qualifyContracts(self.contractEWA)
        self.ib.qualifyContracts(self.contractEWC)
        orderBuy = MarketOrder('BUY', XXShares, self.ewaBar.close)
        orderSell = MarketOrder('SELL', YYShares, self.ewcBar.close)
        self.tradeX = self.ib.placeOrder(self.contractEWA, orderSell)
        self.tradeY = self.ib.placeOrder(self.contractEWC, orderBuy)
        self.long = True

    def ShortEntry(self):
        XXShares = self.leverage 
        YYShares = self.leverage * self.myKal.beta[:, self.myKal.iter][0]
        self.ib.qualifyContracts(self.contractEWA)
        self.ib.qualifyContracts(self.contractEWC)
        orderSell = MarketOrder('SELL', XXShares, self.ewaBar.close)
        orderBuy = MarketOrder('BUY', YYShares, self.ewcBar.close)
        self.tradeX = self.ib.placeOrder(self.contractEWA, orderSell)
        self.tradeY = self.ib.placeOrder(self.contractEWC, orderBuy)
        self.short = True


    def ExitLong(self):
        orderBuy = MarketOrder('BUY', XXShares, self.ewaBar.close)
        orderSell = MarketOrder('BUY', XXShares, self.ewaBar.close)


    def ExitShort(self):


gert = Trader()
IB.sleep(1000)