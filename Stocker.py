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
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import dates, pyplot
from PyQt5.QtCore import QCoreApplication
from PyQt5 import QtCore, uic, QtWidgets
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
        self.pushButton_4.clicked.connect(self.plotter)


        self.today=datetime.date.today() 
        self.past = self.today + datetime.timedelta(-15)
        self.now = self.today + datetime.timedelta(+1)

    def barcounter(self,bar,symbols, counter):
        pb = getattr(self,bar)
        if len(symbols)<=100:
            modulo=int(100/len(symbols))
            pb.setValue(counter*modulo)
        else:
            modulo=int(len(symbols)/100)
            if counter%modulo==0:
                pb.setValue(counter)
       
    def quote(self):
        mm=si.get_quote_table("aapl")
        live_data = si.get_live_price("aapl")
        print(mm)
        print(live_data)

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

        for x in symbols:    
            ticka = yf.Ticker(x)
            hist = ticka.history(start_date=str(self.past), end_date=str(self.today))
            print(str(x) +" -->> "+str(np.mean(hist["Close"])))
            if np.mean(hist["Close"])<float(self.lineEdit.text()):
                pennystocks.append(x)   
            else:
                pass
        json.dump( pennystocks, open("pennystocks.json", 'w' ) ) 
        self.label_2.setText("done")

    def analysis(self):
        self.hotlist={}
        self.ticklist=[]
        with open('pennystocks.json') as f:
            symbols = json.load(f)
         
            counter=1
        for x in symbols:         
            ticka = yf.Ticker(x)
            hist = ticka.history(start_date=str(self.past), end_date=str(self.today))
            live_data = si.get_live_price(x)
            
            if np.mean(hist["Close"])*1.5<live_data:
                self.textBrowser.append(str(x))                 
                self.hotlist['x']= hist['Close']  
                self.ticklist.append(x)
            
            self.barcounter('progressBar_2',symbols, counter)
            QCoreApplication.processEvents()
            counter+=1
        self.label_4.setText('done')

    def recorder(self):
        for key in self.hotlist:
            live_data = si.get_live_price(key)
            self.hotlist[key].append(live_data)

    def plotter(self,index):
        ticker=self.ticklist[0]
        data=self.hotlist[ticker]
        self.widget.plot(data['Date'],data['Close'],pen=pg.mkPen('b', width=2)) 
 
 
#%%     %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setAttribute(QtCore.Qt.AA_Use96Dpi)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())
if __name__ == '__main__':         
    main()