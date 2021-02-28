import numpy as np
from numpy.core.defchararray import array
from numpy.core.fromnumeric import shape
import pandas as pd
import matplotlib.pyplot as plt
from pandas.core import series
import statsmodels.formula.api as sm
import statsmodels.tsa.stattools as ts
import statsmodels.tsa.vector_ar.vecm as vm



class Kalman:
    x = np.ndarray(shape=[0,2])
    y = []
    yhat = np.array([],float)
    Q = np.array([],float)
    e = np.array([],float)
    iter = 0

    def __init__(self):        
        self.R = np.zeros((2,2))
        self.delta=0.0001
        self.beta=np.ndarray(shape=[2,0])
        self.Vw=self.delta/(1-self.delta)*np.eye(2)
        self.Ve=0.001
        


    def update_prediction(self, x_close, y_close):   
        self.x = np.append(self.x, [[x_close,1]], axis=0) 
        self.y = np.append(self.y, y_close)
        self.iter = len(self.y)-1
        
        if(self.iter< 1):
            self.beta = np.append(self.beta, [[0], [0]] , axis=1) 

        if(self.iter > 0):
            #self.beta = np.append(self.beta, [[self.beta[0,iter-1]], [self.beta[1,iter-1]]] , axis=1) 
            self.R=self.P+self.Vw

        self.yhat = np.append(self.yhat, np.dot(self.x[self.iter, :], self.beta[:, self.iter]))
        self.Q= np.append(self.Q, np.dot(np.dot(self.x[self.iter, :], self.R), self.x[self.iter, :].T)+self.Ve)
        self.e= np.append(self.e, self.y[self.iter]-self.yhat[self.iter]) 
        K=np.dot(self.R, self.x[self.iter, :].T)/self.Q[self.iter] 
        self.beta = np.append(self.beta, [[(self.beta[0, self.iter]+np.dot(K, self.e[self.iter])[0])], 
        [(self.beta[1, self.iter]+np.dot(K, self.e[self.iter])[1])]] , axis=1) 
        self.P=self.R-np.dot(np.outer(K, self.x[self.iter, :]), self.R) # Thanks to Matthias for chaning np.dot -> np.outer!
        #self.showGraph()

    def showGraph(self):
        if self.iter > 30:
            plt.plot(self.e[30:])
            plt.plot(np.sqrt(self.Q[30:]))
            plt.plot(-np.sqrt(self.Q[30:]))
            plt.pause(0.01)
