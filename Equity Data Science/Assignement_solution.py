'''
@Date    : xx-xx-2020
@author  : Shivam Pundir
@contact : writetoshivampundir@gmail.com
'''

# imports
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
import os


def histogram_for_metric(data:'pandas.core.frame.DataFrame',metric:str,value:float,timeframe:int,bins:int='auto'):
    '''
    The function returs the histogram plot of the future return for stocks with
    a given metric criterion .
    
    Parameters
    ----------
    data       : 'pandas.core.frame.DataFrame'
                Pandas data frame object with columns including required components
                needed for metric evaluation along with date, price and ticker_exchange.

    metric     : str
                A string with metric evaluation criteria.
                This could be a single metric like pB or a definition for metric evaluation 
                like price/epsNtm.

    value     : float
                Minimum threshold value of metric to consider equity for future return. 
    
    timeframe : int
                Timeframe is the length of time in months over which to calculate the price change
                into the future. float type is casted into int.
                
    bins      : int
                It is the number of bins to have in histogram plot and bin_df dataframe.
                By default the bins is set to 'auto'.
                         
    Returns
    -------
    fig        : matplotlib.figure.Figure
                 matplotlib figure object with histogram plot of forward returns
                 with bins count set to bins. Fig has x,y labels and title .
                 
    bin_df     : pandas.core.frame.DataFrame
                 pandas dataframe with histogram frequency and binned return as separate
                 columns.Rightmost edge is returned for binned return. 
    
    '''

    data['date'] = pd.to_datetime(data['date'],format='%m/%d/%Y')
    
    # handling if metric is ratio or not
    _metric = metric.split('/') if '/' in metric else metric 

    # metric evaluation . div is faster then pandas.eval for this size
    data['metric'] = data[_metric[0]]/data[_metric[-1]] if isinstance(_metric,list) else data[_metric] 

    # massage data frame into wide format. multi level columns with price and metric 
    # at different level for each equity id
    data = data.pivot(index='date',values=['price','metric'],columns='ticker_exchange')
    data = data.sort_index(ascending=True)

    # future price return is assigned to each date when metric value is evaluated
    data['price'] = data['price'].pct_change(int(timeframe)).shift(-int(timeframe))

    # flattened numpy operations are fast and easy to handle
    price_return  = data['price'].values.flatten()
    metric_arr  = data['metric'].values.flatten()

    # filtered price return for metric > value
    price_return = price_return[metric_arr>value] # might raise a warning if metric_arr has nan # can be safely ignored
    price_return = price_return[~np.isnan(price_return)] 

    # matplot plot fot the price returns
    plt.rcParams.update({'font.size': 12})
    
    fig = plt.figure(figsize=(8,6))
    freq, bins, _ = plt.hist(x=price_return, bins=bins,color='#0504aa', 
                                alpha=0.7, rwidth=0.85) 
    plt.grid(True,axis='y',alpha=.5,color='k',linestyle='--')
    plt.xlabel("Return %") ; plt.ylabel("Frequency")
    plt.title("{} months forward return for {}  > {}".format(timeframe,metric,value))
    
    # return binned dataframe 
    bin_df = pd.DataFrame({"Frequency":freq,"Binned_Return":bins[1:]})
#     bin_df = bin_df[bin_df['Frequency']!=0] # could be useful for specific purposes
    
    return fig , bin_df


if __name__ == '__main__':
    data = pd.read_csv('interviewAssignment.csv')
    # fig,df =  histogram_for_metric(data,'price/epsNtm',30,6)
    metrics = ['price/epsNtm', 'entrVal/ebitdaNtm', 'entrVal/salesNtm','roe','pB']
    for  metric in metrics:
        fig, bin_df = histogram_for_metric(data,metric,30,12,50)
        plt.show() 
        plt.savefig('{}.png'.format(metric.replace("/","_")))
