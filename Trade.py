
from helpers import MakeIntoDF, PrimeKalman, SaveIBDataToFile
from Cointegration import define_valid_series
from Trading.BuySell import BuySell
import numpy as np
from ib_insync.contract import CFD, Forex, Stock
from ib_insync.ib import IB
import kalman
from ib_insync import *

class Trader:
    myKal = kalman.Kalman()

    def __init__(self):        
        self.ib = IB()
        self.ib.connect('127.0.0.1', 7497, clientId=1)
        self.broker = BuySell(self.ib,CFD('EWA', 'SMART', 'USD'), CFD('EWC', 'SMART', 'USD'))     
        self.ewcBar = None
        self.ewaBar = None   
        print(self.ib.isConnected())
        

    def RetrieveHistoricalData(
        self,
        contract,
        endDate = '', 
        duration ='5 D',
        barsize ='1 min',
        showing = 'MIDPOINT',
        ontheReg = False):
        return self.ib.reqHistoricalData(
        contract,
        endDate,
        duration,
        barsize,
        showing,
        ontheReg,
        formatDate=1)


    def StartTrading(self):
        self.EWABars = self.ib.reqRealTimeBars(
        Stock('EWA', 'SMART', 'USD'), 5, 'MIDPOINT', False)
        self.EWABars.updateEvent += self.onBarUpdateEWA

        self.EWCBars = self.ib.reqRealTimeBars(
        Stock('EWC', 'SMART', 'USD'), 5, 'MIDPOINT', False)
        self.EWCBars.updateEvent += self.onBarUpdateEWC


    def onBarUpdateEWA(self, bars, hasNewBar):  
        print(f'EWA {bars[len(bars)-1].time}')
        if self.CheckTime(bars[len(bars)-1].time):
            self.ewaBar = bars[len(bars)-1]
            self.checkUpdate()


    def onBarUpdateEWC( self, bars, hasNewBar):
        print(f'EWC {bars[len(bars)-1].time}')
        if self.CheckTime(bars[len(bars)-1].time):
            self.ewcBar = bars[len(bars)-1]
            self.checkUpdate()          


    def checkUpdate(self):
        if self.ewcBar != None and self.ewaBar != None:
            self.myKal.update_prediction(self.ewaBar.close, self.ewcBar.close)
            self.myKal.showGraph()
            
            curr_iter =self.myKal.iter
            print(f'Time: {self.ewaBar.time}, X: {self.ewaBar.close}, Y: {self.ewcBar.close}, {curr_iter}, BETA:{self.myKal.beta[:, curr_iter]}')

            #checkExits first
            if (self.myKal.e[curr_iter] > 0 and self.broker.long):
                self.broker.ExitLong(self.ewaBar.close,self.ewcBar.close)     
                print('Exited Long!')          

            if (self.myKal.e[curr_iter] < 0 and self.broker.short):
                self.broker.ExitShort(self.ewaBar.close,self.ewcBar.close)
                print('Exited Short!')          

            if (self.myKal.e[curr_iter] < -np.sqrt(self.myKal.Q[curr_iter]) 
            and (not self.broker.long)):
                self.broker.LongEntry(self.myKal.beta[:,self.myKal.iter][0],self.ewaBar.close,self.ewcBar.close)
                print('Entered Long!')          

            if (self.myKal.e[curr_iter] > np.sqrt(self.myKal.Q[curr_iter]) 
            and (not self.broker.short)):
                self.broker.ShortEntry(self.myKal.beta[:,self.myKal.iter][0], self.ewaBar.close,self.ewcBar.close)
                print('Entered Short!')

            self.ewaBar = None
            self.ewcBar = None
        

    def CheckTime(self, datetime):
        if (datetime.second == 00):
                #if datetime.second == 00:
            return True
        return False
        #if datetime.second == 00 or datetime.second % 20 == 0:
        #            return True
        #return False


    def PrimeKalman(self):
        contractOne = Stock('EWA', exchange='SMART', currency='USD')
        contractTwo = Stock('EWC', exchange='SMART', currency='USD')
        self.ib.qualifyContracts(contractOne)
        self.ib.qualifyContracts(contractTwo)
        ewa = self.RetrieveHistoricalData(contractOne)
        ewc = self.RetrieveHistoricalData(contractTwo)
        df_x = MakeIntoDF(ewa)
        df_y = MakeIntoDF(ewc)
        PrimeKalman(self.myKal, define_valid_series(df_x,df_y))
        self.myKal.showGraph()

        

