# load required package
from xml.etree import ElementTree as ET 
import urllib.request as rq
import pandas as pd
import numpy as np
from pandas.io.json import json_normalize as jnorm
import lxml.etree as et
import json, requests
# import pandasdmx as pdsx
# get data availability

# get available indicators

indi = rq.urlopen('http://wits.worldbank.org/API/V1/wits/datasource/tradestats-trade/indicator/ALL?format=JSON')

test = et.parse(indi)
indi_list = et.tostring(test, pretty_print = True)


def wits_trade(rpt = 'usa', ptn = 'chn', pcd = 'Total', idt = 'MPRT-TRD-VL', yr_def = 'all'): 
    #get the data
    # perform a country-partner-productcode-indicator with all years.
    # ideally to loop for country list and productcode.

    dashjoin = "/"
    preurl = "http://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade"
    rpurl = "reporter"
    yrurl = "year"
    pturl = "partner"
    pcurl = "product"
    idurl = "indicator"
    tail = "?format=JSON"

    # add this since there is no dash
    posturl = idt + tail

    full_url = dashjoin.join( (preurl, rpt ,rpurl , yrurl, yr_def, pturl , ptn, pcurl, pcd, idurl, posturl) )

    # response_totalimport = requests.get("http://wits.worldbank.org/API/V1/SDMX/V21/datasource/tradestats-trade/reporter/usa/year/all/partner/chn/product/Total/indicator/MPRT-TRD-VL?format=JSON")
    response_totalimport = requests.get(full_url)
    json_totalimport = response_totalimport.json()
    #jnorm(json_totalimport)
    
    # retrieve the values of indicator for all the years
    sv_obs = json_totalimport['dataSets'][0]['series']['0:0:0:0:0']['observations']

    # shape it into a pandas dataframe
    sl_obs = pd.DataFrame.from_dict(sv_obs,  orient = 'index') 
    obs_value = sl_obs[0]
    obs_value = obs_value.values
    sl_obs.rename(columns = {sl_obs.columns[0] : 'value'}, inplace = True)


    # retrieve all the available years
    sv_year = json_totalimport['structure']['dimensions']['observation'][0]['values']
    sl_year = pd.DataFrame.from_dict(sv_year, orient = 'columns')
    sl_year.rename(columns = {sl_year.columns[1] : 'year'}, inplace = True)

    # ------------------------------------------- #
    # report the params of this request
    #freq =  annual
    sv_freq = json_totalimport['structure']['dimensions']['series'][0]['values'][0]['id']

    # Anchored the reporter, report its iso 3 code
    sv_reporter = json_totalimport['structure']['dimensions']['series'][1]['values'][0]['id']

    # Anchored the partner country, report its iso 3 code
    sv_partner = json_totalimport['structure']['dimensions']['series'][2]['values'][0]['id']

    # Anchored the product code, report its code which can be found in Trade: http://wits.worldbank.org/API/V1/wits/datasource/tradestats-trade/product/all
    sv_prod = json_totalimport['structure']['dimensions']['series'][3]['values'][0]['id']

    # Anchored the indicator, which can be found in Trade: http://wits.worldbank.org/API/V1/wits/datasource/tradestats-trade/indicator/ALL
    sv_indi = json_totalimport['structure']['dimensions']['series'][4]['values'][0]['id']

    # combine all the results
    # obtain a good shape dataframe as container
    df_combined = pd.DataFrame(pd.np.empty((sl_year.shape[0] , 7)), columns = {'year', 'value', 'freq', 'report', 'partner', 'prod', 'indi'})

    df_combined['year'] = sl_year['year']
    df_combined['value'] = obs_value
    df_combined['report'] = sv_reporter
    df_combined['partner'] = sv_partner
    df_combined['prod'] = sv_prod
    df_combined['indi'] = sv_indi
    df_combined['freq'] = sv_freq

    return(df_combined)



test = wits_trade()