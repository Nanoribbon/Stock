"""
@author: Dr. Martin Hell
"""

import glob
import json
import time
import sys
import os
import re
import math
import numpy as np
import pandas as pd
import yfinance as yf
import ftplib
import datetime

import pyqtgraph as pg
import pyqtgraph.opengl as gl
import pyqtgraph.exporters
from plotly.offline import plot as plo
#import plotly.plotly as py
import plotly.graph_objs as go
import plotly.express as px
import matplotlib.pyplot as plt
from plotly.graph_objs import Scatter, Layout
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import dates, pyplot
from PyQt5 import QtGui,QtCore
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore, uic, QtWidgets, QtWebEngineWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication,QSlider, QWidget, QPushButton, QAction, QLineEdit, QMessageBox, QMenu, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QPixmap, QScreen
from PyQt5.QtWidgets import QFileDialog
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph import PlotWidget, plot
from time import time
from datetime import date
from pathlib import Path
from yahoo_fin.stock_info import get_data
from yahoo_fin import stock_info as si
from pathlib import Path
from StockerGui import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setWindowIcon(QtGui.QIcon('hellicon.png'))
        self.setWindowTitle('Stocker')
  
        uic.loadUi('StockerGui.ui', self)
        
        self.pushButton_1.clicked.connect(self.symbollister)
        self.pushButton_2.clicked.connect(self.pennystocks)
        self.pushButton_3.clicked.connect(self.analysis)
        #self.pushButton_4.clicked.connect(self.test)
        self.pushButton_4.clicked.connect(self.plotter)

    

        self.fig1 = Figure()                                   
        self.canvas1 = FigureCanvas(self.fig1)        
        self.verticalLayout.replaceWidget(self.widget, self.canvas1)

        past_days=int(self.lineEdit_3.text())
        self.today=datetime.date.today() 
        self.past = self.today + datetime.timedelta(-past_days)
        print(self.past)
        print(self.today)
        self.now = self.today + datetime.timedelta(+1)
        self.timeline=np.arange(-past_days,0)

    def barcounter(self,bar,symbols, counter):
        pb = getattr(self,bar)
        pb.setMaximum(len(symbols))
        pb.setValue(counter)

    def get_symbol_df(self, ticka):
      
        ticka.reset_index(drop=True)
        ticka["index"] = pd.to_datetime(ticka["index"])
        return ticka

    def symbollister(self):
        url = "ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqlisted.txt"
        df=pd.read_csv(url, sep="|")
        export={'Symbols':[]}
        for i in df['Symbol']:
            export['Symbols'].append(i)
        json.dump( export, open("Tickers.json", 'w' ) ) 
        self.label_1.setText("done")

    def pennystocks(self):
        pennystocks=[]
        with open('Tickers.json') as f:
            symbols = json.load(f)
        counter=1
        for x in symbols:    
            self.barcounter('progressBar_1',symbols, counter)
            ticka = yf.Ticker(x)
            hist = ticka.history(start_date=str(self.past), end_date=str(self.today))
            print(str(x) +" -->> "+str(np.mean(hist["Close"])))
            if np.mean(hist["Close"])<float(self.lineEdit.text()):
                pennystocks.append(x)   
            else:
                pass
            counter+=1
        json.dump( pennystocks, open("pennystocks.json", 'w' ) ) 
        self.label_2.setText("done")

    def analysis(self):
        self.hotlist={}
        self.ticklist=[]
        self.timelist=[]
        
        with open('pennystocks.json') as f:
            symbols = json.load(f)  
            counter=1
        for x in symbols:         
            ticka = yf.Ticker(x)       
            hist = ticka.history(period="5d")
            #hist = yf.download(str(ticka), start="2017-02-01", end="2017-02-04")
            #hist = ticka.history(start_date=str(self.past), end_date=str(self.today))
            print(hist)
            hist.reset_index(inplace=True)
            cl_val=hist['Close'] 
            t  = pd.to_datetime(hist['Date'],format = '%Y-%m-%d')
            self.timelist=t
            live_data = si.get_live_price(x)
            
            if np.mean(hist["Close"])*1.5<live_data:
                self.textBrowser.append(str(x))                 
                self.hotlist[str(x)]= [cl_val]
                self.ticklist.append(x)
            
            self.barcounter('progressBar_2',symbols, counter)
            QCoreApplication.processEvents()
            counter+=1
        Tot=len(self.ticklist)
        self.Cols=3
        self.Rows=Tot//self.Cols
        if Tot%self.Cols!=0:
            self.Rows+=1
        self.label_4.setText('done')
     
    def recorder(self):
        for key in self.hotlist:
            live_data = si.get_live_price(key)
            self.hotlist[key].append(live_data)
    
   
    
    def plotter(self):

        
        k=1
        for tick in self.ticklist:
            print(self.timelist)
            print(self.hotlist[str(tick)])
            ax = self.fig1.add_subplot(self.Rows,self.Cols,k)
            ax.plot(self.timeline,self.hotlist[str(tick)][0]) 
            k+=1
            self.fig1.tight_layout()                                      
            self.canvas1.draw() 
       
       
#%%     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def main():
    #app = QtGui.QApplication(sys.argv)
    

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
if __name__ == '__main__':         
    main()