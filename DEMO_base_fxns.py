##### API setup & Needed Functions #############################################
import asyncio
from    concurrent import futures
from    datetime import timedelta
from    datetime import datetime
import gc
import  hmac
import  hashlib
from    IPython.display import clear_output
import  json
import  DEMO_local_settings as local_settings
import logging
import  numpy as np
import math
import  os
import  pandas as pd
import  plotly.graph_objects as go
import  plotly.express as px
import psutil
from    pybit.unified_trading import HTTP
from pybit.unified_trading import WebSocket
import  requests
import resource
import sys
import  time
import tradeStats as tradeStats


api_key = local_settings.ake
api_secret = local_settings.ase
# base_url = 'https://api.bybit.com'
base_url = 'https://api-demo.bybit.com'
recv_window = '5000' # increase if alot of traffic
# Authentication
session = HTTP(testnet=False,
               demo=True,
               api_key=api_key,
               api_secret=api_secret)

# Parameters
def intialize_perp_params(perp_name,key_level,collat,leverage,take_profit_perc,stop_loss_perc=0.25):

    attemptLimit = 50
    lossLimit = 20 #dollars
    #--------------------------
    
    params = {
        'attempt_num':0,
        'condBelowSupport' : False,
        'collateral':{0:collat}, #{Anum 0: Intial collateral}
        'entries':{}, #{attempt_num:{datetime:entry_price}}
        'exits':{}, # attempt_num:exit_price
        'key_level' : key_level,    
        'leverage':leverage,
        'limit-chase-mode': False,
        'longedBool' : False ,      
        'losses':{0:0},  # attempt_num:loss
        'perp_name' : perp_name,
        'perp_info':{'qtyStepCoin':'',
                     'coin_precision_info':''}, 
        'profits':{0:0}, # attempt_num:profit
        'stop_loss_perc':stop_loss_perc,
        'stop_loss_price':{}, # attempt_num:stop_loss_price
        'take_profit_perc':take_profit_perc,
        'take_profit_price':{} # attempt_num:take_profit_price
        }
    return params
#--------------------------------------------------------------------------------------------------------------------------
def intialize_spot_params(spot_name,key_level,collat,take_profit_perc,stop_loss_perc=0.25):

    attemptLimit = 50
    lossLimit = 20 #dollars
    #--------------------------
    
    params = {
        'attempt_num':0,
        'condBelowSupport' : False,
        'collateral':{0:collat}, #{Anum 0: Intial collateral}
        'entries':{}, #{attempt_num:{datetime:entry_price}}
        'exits':{}, # attempt_num:exit_price
        'key_level' : key_level,
        'limit-chase-mode': False,
        'longedBool' : False,      
        'losses':{0:0},  # attempt_num:loss
        'spot_name' : spot_name, 
        'profits':{0:0}, # attempt_num:profit
        'stop_loss_perc':stop_loss_perc,
        'stop_loss_price':{}, # attempt_num:stop_loss_price
        'take_profit_perc':take_profit_perc,
        'take_profit_price':{}, # attempt_num:take_profit_price
        }  
    return params
#--------------------------------------------------------------------------------------------------------------------------
def tg_send_msg(msg):
    telegram_url = f"https://api.telegram.org/bot{tg_akey}/sendMessage?chat_id={tg_chat_id}&text='{msg}'"
    requests.get(telegram_url)

def tg_alert_msg(msg):

    for i in range(10):
        telegram_url = f"https://api.telegram.org/bot{tg_akey}/sendMessage?chat_id={tg_chat_id}&text='{msg}'"
        requests.get(telegram_url)
        time.sleep(30)
#--------------------------------------------------------------------------------------------------------------------------
def ring():
    os.system("afplay " + 'sample.wav')
#--------------------------------------------------------------------------------------------------------------------------
def memory_usage():

    # Get current process ID
    pid = os.getpid()

    # Get process info using psutil
    process = psutil.Process(pid)

    # Get memory usage in bytes and convert to MB
    memory_usage = process.memory_info().rss / (1024 * 1024)  # Resident Set Size (RSS)

    return memory_usage
#--------------------------------------------------------------------------------------------------------------------------
def timestamp_to_rtime(timestamp_ms):

    # Convert milliseconds to seconds
    timestamp_s = timestamp_ms / 1000

    # Convert to a datetime object
    dt_object = datetime.fromtimestamp(timestamp_s)

    # Format the datetime object to 'yyyy-mm-dd hh:mm:ss'
    formatted_time = dt_object.strftime('%Y-%m-%d %H:%M:%S')
    
    return formatted_time
#--------------------------------------------------------------------------------------------------------------------------

def ring():
    os.system("afplay " + 'sample.wav')

def get_kline(perp_name,rewind_days,freq=1):
    
    interval=freq
    category='linear'
    limit=200

    starting_ts = int((datetime.now() - timedelta(days=rewind_days)).timestamp()*1000)
    ending_ts = int(datetime.now().timestamp()*1000)
    last_ts = starting_ts

    tss_asc = []
    dts_asc = []
    opens_asc = []
    highs_asc = []
    lows_asc = []
    closes_asc = []
    # vol_asc = []
    # tos_asc = []

    while last_ts < ending_ts:

        tss = []
        dts = []
        opens = []
        highs = []
        lows = []
        closes = []
        # volumes = []
        # turnovers=[]

        msg = session.get_kline(category=category, 
                                symbol=perp_name, 
                                interval=interval,
                                start=last_ts,
                                limit=limit)

        for i in range(len(msg['result']['list'])): #200 values unless most recent
            ohlc = msg['result']['list'][i]
            
            if(len(tss_asc)>0 and ohlc[0] == tss_asc[-1][0]): #continous w/o repeat
                continue 

            tss.append(ohlc[0]) #str
            dts.append(datetime.strftime(datetime.fromtimestamp(int(ohlc[0])/1000),'%m/%d/%y %I:%M:%S %p'))
            opens.append(float(ohlc[1]))
            highs.append(float(ohlc[2]))
            lows.append(float(ohlc[3]))
            closes.append(float(ohlc[4]))
            # volumes.append(float(ohlc[5]))
            # turnovers.append(float(ohlc[6]))

        if len(tss)==0 or int(tss[0]) == last_ts: #we reached most recent ts, repeat, so break
            break

        last_ts = int(tss[0]) # update

        tss_asc.append(tss) #str
        dts_asc.append(dts)
        opens_asc.append(opens)
        highs_asc.append(highs)
        lows_asc.append(lows)
        closes_asc.append(closes)
        # vol_asc = []
        # tos_asc = []

    # Final total lists
    tss = []
    dts = []
    opens = []
    highs = []
    lows = []
    closes = []
    volumes = []
    turnovers = []
    for i,e in reversed(list(enumerate(tss_asc))):
        tss += tss_asc[i]
        dts += dts_asc[i]
        opens += opens_asc[i]
        highs+= highs_asc[i]
        lows+= lows_asc[i]
        closes+= closes_asc[i]
        # volumes+= vol_asc[i]
        # turnovers+= tos_asc[i]

    dff = {'symbol':[perp_name]*len(tss),
        'timestamp':tss, 'datetime':dts,
        'open':opens,'high':highs,'low':lows,'close':closes}#,'volume':volumes,'turnover':turnovers}
    
    df = pd.DataFrame(dff).loc[::-1].reset_index(drop=True)

    return df

def get_klines(pairs,rewind_days,freq):
    
    pdf = {}
    
    with futures.ThreadPoolExecutor() as pool:
        running = [pool.submit(get_kline,perp,rewind_days,freq) for perp in pairs]

        for future in futures.as_completed(running):
            pdf[future.result().symbol[0]]=future.result()
            
    return pdf

'''
new_ldf: new dict of dataframes consisting of current/older data {'BTCUSDT':Dataframe, 'ETHUSDT':Dataframe,...}
returns: combined_ldf which is a merge of old saved data and new data  
'''
def combineOldNewKlineDataOLD(new_ldfs,interval):
    perp_names = list(new_ldfs.keys())
    combined_ldfs = {}
    for symbol in perp_names:

        df = new_ldfs[symbol]
        kline_df_path = f'/Users/Research/kline_data/{symbol}_{interval}m.feather'
        
        if not os.path.exists(kline_df_path):
            df.to_feather(kline_df_path)
            combined_ldfs[symbol] = df
        else:
            existing_df = pd.read_feather(kline_df_path)
            merged_df = pd.concat([existing_df,df], axis=0,copy=False).drop_duplicates().reset_index(drop=True)
            merged_df = merged_df.sort_values(by='timestamp').reset_index(drop=True)
            merged_df.to_feather(kline_df_path) # same path as original
            combined_ldfs[symbol] = merged_df
    return combined_ldfs

'''
Load existing dataframes
'''
def loadExistingKlineData(perp_names,interval=1):
    ldf = {}
    for symbol in perp_names:

        kline_df_path = f'/Users/Research/kline_data/{symbol}_{interval}m.feather'
        
        if not os.path.exists(kline_df_path):
            print(f'{kline_df_path} does not exist.')
        else:
            existing_df = pd.read_feather(kline_df_path)
            ldf[symbol] = existing_df
    return ldf

def combineOldNewKlineData(pairs,rewind_days,interval):

    new_ldfs = get_klines(pairs=pairs,rewind_days=rewind_days,freq=interval)

    perp_names = list(new_ldfs.keys())
    combined_ldfs = {}
    for symbol in perp_names:

        df = new_ldfs[symbol]
        kline_df_path = f'/Users//Research/kline_data/{symbol}_{interval}m.feather'
        
        if not os.path.exists(kline_df_path):
            df.to_feather(kline_df_path)
            combined_ldfs[symbol] = df
        else:
            existing_df = pd.read_feather(kline_df_path)
            merged_df = pd.concat([existing_df,df], axis=0,copy=False).drop_duplicates().reset_index(drop=True)
            merged_df = merged_df.sort_values(by='timestamp').reset_index(drop=True)
            merged_df.to_feather(kline_df_path) # same path as original
            combined_ldfs[symbol] = merged_df
    return combined_ldfs
# 

# n-min returns 
def plot_nMin_returns(n,df):
    nMin = n # 12h=720m, 24h=1440m
    acceptable_nMin = 60%nMin==0 or nMin%60==0 #acceptable_time_scale
    perc_change_nMin = None
    perc_changes_nMin = {}
    prev_nMin_close = None
    curr_min_diff = None
    
    if not acceptable_nMin:
        return 'invalid n'

    for i in range(df.shape[0]):
        dt = df.loc[i,'datetime']
        close_price = df.loc[i,'close']
        if dt[12:17] == '00:00' and prev_nMin_close==None and nMin<240:
            prev_nMin_close = close_price
            curr_min_diff = 1
        elif dt[9:17] == '12:00:00' and prev_nMin_close==None: #For better looking results on HTF
            prev_nMin_close = close_price
            curr_min_diff = 1
        elif curr_min_diff != None and curr_min_diff!=0 and curr_min_diff%nMin==0:
            perc_change_nMin = np.round(100*(close_price - prev_nMin_close)/prev_nMin_close,3)
            perc_changes_nMin[dt] = perc_change_nMin
            prev_nMin_close = close_price
            curr_min_diff = 1
        elif curr_min_diff != None:
            curr_min_diff += 1

    fig3 = go.Figure().add_trace(go.Bar(
                x=list(perc_changes_nMin.keys()),
                y=list(perc_changes_nMin.values()), name = f'% Change',marker_color='orange'))
    fig3.update_layout(title={'text' : f"{nMin}m Returns from " + list(perc_changes_nMin.keys())[0] + ' to ' + list(perc_changes_nMin.keys())[-1],'y':0.92,'x':0.5,'xanchor': 'center','yanchor': 'top'},
                xaxis_title="Time",xaxis = {'rangeslider': {'visible': False}},yaxis_title='% Return',width=800,height=800,template = 'plotly_dark')
    fig3.show()    