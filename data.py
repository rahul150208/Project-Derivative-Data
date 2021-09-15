from xlrd import open_workbook
import xlrd
import pymysql
import sqlalchemy
from datetime import datetime
import pandas as pd
import openpyxl
import math 
from nsepy.derivatives import get_expiry_date
import threading




def getoptiondata():
    path = "D:\\project_option\\Book1.xlsm"
    
    pd_xl_file = pd. ExcelFile(path)
    df = pd_xl_file. parse("Sheet2")
    df = pd.DataFrame.from_dict(df)
    def strick_price(current_price):
        x=((math.ceil(current_price/100))*100)
        current_price=x-400
        #print(current_price)
        return [current_price+50*i for i in range(17)]
       
    def current_exy():
        for date in expiry:
             if (date > (datetime.now().date())):
                    return(datetime.strftime(date,'%d-%b-%Y'))

    expiry = list((get_expiry_date(year=datetime.now().year, month=datetime.now().month)))
    expiry=sorted(expiry)
    
    strike_price=strick_price(df['Column1.PE.underlyingValue'][1])
    new_df=df[df['Column1.strikePrice'].isin(strike_price) & df['Column1.expiryDate'].isin([current_exy()])]

    print('data of::',datetime.now())

    engine = sqlalchemy.create_engine("mysql+pymysql://root:Rahulydv#150208@127.0.0.1:3306/marketdata")
    new_df.to_sql(name='oc_table',con =engine,index= False,if_exists = 'append')
  

def startTimer():
    #interval =120 #seconds
    #getoptiondata()
    timer = threading.Timer(300, startTimer)
    timer.start()
    getoptiondata()


if __name__== '__main__':
    startTimer()
    