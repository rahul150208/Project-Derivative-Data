from flask import Flask,render_template
import pymysql
import sqlalchemy as db
import pandas as pd
import numpy as np

import threading
import openpyxl
from xlrd import open_workbook
import xlrd
import math

import plotly.graph_objects as go
from plotly.subplots import make_subplots




engine= db.create_engine('mysql+pymysql://root:Rahulydv#150208@127.0.0.1:3306/marketdata')
app = Flask(__name__)



    
@app.route('/')
def hello_world():
    table_oi = pd.read_sql_table("oc_table",con=engine)

    grouped_oi=table_oi.groupby('Time').agg({'Column1.CE.openInterest':'sum',
                                             'Column1.CE.changeinOpenInterest':'sum',
                                             'Column1.CE.impliedVolatility':'mean',
                                             'Column1.PE.openInterest':'sum',
                                             'Column1.PE.changeinOpenInterest':'sum',
                                             'Column1.PE.impliedVolatility':'mean'}).reset_index()

    grouped_oi['oi_diff']=grouped_oi['Column1.PE.openInterest']-grouped_oi['Column1.CE.openInterest']

    grouped_ce=table_oi.groupby('Time').agg({'Column1.CE.openInterest':'sum',
                                             'Column1.CE.changeinOpenInterest':'sum',
                                             'Column1.CE.impliedVolatility':'mean'}).reset_index()

    grouped_pe=table_oi.groupby('Time').agg({'Column1.PE.openInterest':'sum',
                                             'Column1.PE.changeinOpenInterest':'sum',
                                             'Column1.PE.impliedVolatility':'mean'}).reset_index()

    ist=grouped_pe['Column1.PE.openInterest']-grouped_ce['Column1.CE.openInterest']


    atmprice=math.ceil(table_oi['Column1.CE.underlyingValue'].iloc[1]/100)*100
    atmprice

    
    group_PE_itm=table_oi[table_oi['Column1.PE.openInterest']>atmprice].groupby('Time',as_index=False).agg({'Column1.PE.openInterest':'sum'})
    group_PE_otm=table_oi[table_oi['Column1.PE.openInterest']<atmprice].groupby('Time',as_index=False).agg({'Column1.PE.openInterest':'sum'})


    group_CE_itm=table_oi[table_oi['Column1.CE.openInterest']>atmprice].groupby('Time',as_index=False).agg({'Column1.CE.openInterest':'sum'})
    group_CE_otm=table_oi[table_oi['Column1.CE.openInterest']<atmprice].groupby('Time',as_index=False).agg({'Column1.CE.openInterest':'sum'})

    groupstk=table_oi.groupby('Column1.strikePrice')

    



    fig = make_subplots(rows=4, cols=2,shared_xaxes=False,  specs=[[{"secondary_y": True}, {"secondary_y": True}],
                            [{"secondary_y": True}, {"secondary_y": True}],
                            [{"secondary_y": True}, {"secondary_y": True}],
                            [{"secondary_y": True}, {"secondary_y": True}]],subplot_titles=("cum_openInterest","cum_changeinOpenInterest","OI-DIFFERENCE [PE-CE]","avg_iv","PEstk_oi","CEstk_oi",
                                  "ITM_OTM_PE","ITM_OTM_CE"))

    # Top left
    fig.add_trace(
        go.Scatter(x=grouped_oi['Time'], y=grouped_oi['Column1.PE.openInterest'], name="PE_OI"),
        row=1, col=1, secondary_y=False)

    fig.add_trace(
        go.Scatter(x=grouped_oi['Time'], y=grouped_oi['Column1.CE.openInterest'], name="CE_OI"),
        row=1, col=1, secondary_y=True
    )

    fig.add_trace(
        go.Scatter(x=grouped_oi['Time'], y=grouped_oi['Column1.PE.changeinOpenInterest'], name="PE_OI"),
        row=1, col=2, secondary_y=False)

    fig.add_trace(
        go.Scatter(x=grouped_oi['Time'], y=grouped_oi['Column1.CE.changeinOpenInterest'], name="CE_OI"),
        row=1, col=2, secondary_y=True
    )

    # Top right
    fig.add_trace(
        go.Scatter(x=grouped_oi['Time'], y=grouped_oi['oi_diff'], name="OI-DIFFERENCE [PE-CE]"),
        row=2, col=1, secondary_y=False
    )

    # Bottom left
    fig.add_trace(
        go.Scatter(x=grouped_oi['Time'], y=grouped_oi['Column1.CE.impliedVolatility'], name="AVG_CE_IV"),
        row=2, col=2, secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=grouped_oi['Time'], y=grouped_oi['Column1.PE.impliedVolatility'], name="AVG_PE_IV"),
        row=2, col=2, secondary_y=True
    )

    # Bottom right
    fig.add_trace(
        go.Scatter(x=groupstk.get_group(atmprice)['Time'], y=groupstk.get_group(atmprice)['Column1.PE.openInterest'], name='ATM_OI'),
        row=3, col=1, secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=groupstk.get_group(atmprice)['Time'], y=groupstk.get_group(atmprice)['Column1.PE.lastPrice'], name="PE_ATM_LTP"),
        row=3, col=1, secondary_y=True
    )

        

    fig.add_trace(
        go.Scatter(x=groupstk.get_group(atmprice)['Time'], y=groupstk.get_group(atmprice)['Column1.CE.openInterest'], name='ATM_{}_OI'.format(atmprice)),
        row=3, col=2, secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=groupstk.get_group(atmprice)['Time'], y=groupstk.get_group(atmprice)['Column1.CE.lastPrice'], name="CE_ATM_LTP"),
        row=3, col=2, secondary_y=True
    )

        
    fig.add_trace(
        go.Scatter(x=group_PE_itm['Time'], y=group_PE_itm['Column1.PE.openInterest'], name='PE_ITM'),
        row=4, col=1, secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=group_PE_otm['Time'], y=group_PE_otm['Column1.PE.openInterest'], name="PE_OTM"),
        row=4, col=1, secondary_y=True
    )


    fig.add_trace(
        go.Scatter(x=group_CE_itm['Time'], y=group_CE_itm['Column1.CE.openInterest'], name='CE_ITM'),
        row=4, col=2, secondary_y=False
    )

    fig.add_trace(
        go.Scatter(x=group_CE_otm['Time'], y=group_CE_otm['Column1.CE.openInterest'], name="CE_OTM"),
        row=4, col=2, secondary_y=True
    )
    
    fig.update_traces(hovertemplate=None)
    fig.update_layout(height=1500, width=1500,hovermode='x')




        
    fig.write_html('templates/home.html')
    return render_template('home.html')




if __name__ == '__main__':
    app.run(debug=True)