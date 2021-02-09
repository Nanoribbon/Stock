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
       # self.pushButton_4.clicked.connect(self.plotter)

        self.pushButton.clicked.connect(self.test)

        self.fig1 = Figure()                                   
        self.canvas1 = FigureCanvas(self.fig1)        
        self.verticalLayout.replaceWidget(self.widget_1, self.canvas1)

        self.fig2 = Figure()                                   
        self.canvas2 = FigureCanvas(self.fig2)        
        self.verticalLayout.replaceWidget(self.widget_2, self.canvas2)

       
        self.today=datetime.date.today() 
        self.past = self.today + datetime.timedelta(-30)
        self.now = self.today + datetime.timedelta(-3)
       

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
        self.textBrowser.clear()
        self.hotlist={}
        self.ticklist=[]
       
        gain=float(self.lineEdit_2.text())
      #  with open('pennystocks.json') as f:
        with open('pennystock_test.json') as f:          
            symbols = json.load(f)  
            counter=1
        for x in symbols:         
            ticka = yf.Ticker(str(x))       
            ref = ticka.history(start=str(self.past), end=str(self.now), index_as_date = True)
            #ref = ticka.history(period="5d", index_as_date = True)
         
            ref.reset_index(inplace=True)   
            op_val=ref['Open']      
            cl_val=ref['Close']           
           
            
            live_data = si.get_live_price(x)
          
            if np.mean(op_val)*gain<=live_data:
                self.textBrowser.append(str(x))                 
                self.hotlist[str(x)]= [op_val]
                self.ticklist.append(x)
            
            self.barcounter('progressBar_2',symbols, counter)
            QCoreApplication.processEvents()
            counter+=1
        self.Tot=len(self.ticklist)
        self.Cols=1
       # self.Rows=self.Tot//self.Cols
        
       # if self.Tot%self.Cols!=0:
       #     self.Rows+=1
        self.label_4.setText('done')
        self.label_4.setStyleSheet("""QLineEdit { background-color: green; color: white }""")
        self.past_plotter()
        self.present_plotter()
     
    def recorder(self):
        for key in self.hotlist:
            live_data = si.get_live_price(key)
            self.hotlist[key].append(live_data)
    
    def test(self):
        ticka = yf.Ticker("AACQW") 
        hist = ticka.history(period="1d", interval="5m", index_as_date = True)
        hist.reset_index(inplace=True)
        print(hist['Datetime'][0])
        t=hist['Datetime'][0]
        t= t.strftime("%H:%M:%S")
        #s= datetime.datetime.strptime(t, "%Y-%m-%d")
        print(t)
      #  ticka = yf.Ticker("AACQW")      
      #  hist =get_data("AACQW", start_date="10/04/2019", end_date="12/04/2019", index_as_date = True)
      #  hist.reset_index(inplace=True)
       # get_data(ticker, start_date = None, end_date = None, index_as_date = True, interval = “1d”)
        #hist = yf.download(str(ticka), start="2020-02-01", end="2020-02-04")
       # hist = ticka.history(period="1d", index_as_date = True)
       # hist = ticka.history(period="1d", index_as_date = False)
            #hist = yf.download(str(ticka), start="2017-02-01", end="2017-02-04")
            #hist = ticka.history(start_date=str(self.past), end_date=str(self.today)) 
       # print(hist)
    
    def past_plotter(self):
        self.fig1.clear()
        k=1
        for tick in self.ticklist:
            ticka = yf.Ticker(str(tick))         
            ref = ticka.history(period="1mo", index_as_date = True)
            op_val=ref['Open']      
            cl_val=ref['Close']
            x=np.arange(-len(op_val),0,1)
            ax = self.fig1.add_subplot(self.Tot,self.Cols,k)
            ax.tick_params(axis='x',  which='both',   bottom=False,  labelbottom=False)           
            ax.plot(x,op_val, label='open',c='b') 
            ax.plot(x,cl_val, label='close',c='b' )
            if k==self.Tot:
                ax.tick_params(axis='x',  which='both',   bottom=False,  labelbottom=True)
                ax.legend(loc='upper left', shadow=True)
            ax.fill_between(x, op_val, cl_val, where=cl_val >= op_val, facecolor='green', interpolate=True)
            ax.fill_between(x, op_val, cl_val, where=cl_val <= op_val, facecolor='red', interpolate=True)
            ax.set_title( str(tick), loc='center')
            ax.set_xticks(np.arange(-len(op_val),0,2))
          #  ax.xaxis.set_major_locator(len(op_val))#(plt.MaxNLocator(len(op_val)/2))
            k+=1
            self.fig1.tight_layout()                                      
        self.canvas1.draw() 
       
    def present_plotter(self):
        self.fig2.clear()
        k=1
        for tick in self.ticklist:
            ticka = yf.Ticker(str(tick)) 
            hist = ticka.history(period="1d", interval="5m", index_as_date = True)
            print(hist)
            hist.reset_index(inplace=True)
            hist['Datetime']= [s.strftime("%H:%M:%S") for s in hist['Datetime']]
            ax2 = self.fig2.add_subplot(self.Tot,self.Cols,k)
            ax2.tick_params(axis='x',  which='both',   bottom=False,  labelbottom=False)
            if k==self.Tot:
                ax2.tick_params(axis='x',  which='both',   bottom=False,  labelbottom=True)
         
            ax2.plot(hist['Datetime'],hist['Close'])
          
                
            #ax2.plot(hist['Datetime'],hist['Close']) 
            ax2.set_title(str(tick),  loc='center')
            ax2.tick_params(labelrotation=90)
            ax2.xaxis.set_major_locator(plt.MaxNLocator(5))
            k+=1
            self.fig2.tight_layout()                                      
        self.canvas2.draw() 

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