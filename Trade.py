
import ib_insync
from ib_insync.contract import Forex
from ib_insync.ib import IB
import kalman
from ib_insync import *



class Trader:
    myKal = kalman.Kalman() 
    #contractEWA = CFD('EWA', 'SMART', 'USD')
    #contractEWC = CFD('EWC', 'SMART', 'USD')
    contractEWA = Forex('USDCAD')
    contractEWC = Forex('AUDCAD')

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
        '''        if (bars.date.dt.minute == 00 or
            bars.date.dt.minute == 15 or 
            bars.date.dt.minute == 30 or
            bars.date.dt.minute == 45) and bars.date.dt.second == 00:'''
        self.ewaBar = bars[len(bars)-1]
        print(bars[len(bars)-1].time)
        print(bars[len(bars)-1].close)
        self.checkUpdate()


    def onBarUpdateEWC( self, bars, hasNewBar):
        '''       if (bars.date.dt.minute == 00 or
            bars.date.dt.minute == 15 or 
            bars.date.dt.minute == 30 or
            bars.date.dt.minute == 45) and bars.date.dt.second == 00:'''
        self.ewcBar = bars[len(bars)-1]
        self.checkUpdate()

    def checkUpdate(self):
        if self.ewcBar != None and self.ewaBar != None:
            self.myKal.update_prediction(self.ewaBar.close,self.ewcBar.close )
            self.ewaBar = None
            self.ewcBar = None
            print(self.myKal.beta[:, self.myKal.iter])
            


gert = Trader()
IB.sleep(1000)