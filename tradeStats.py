
from    datetime import datetime
import  hmac
import  hashlib
# import tooling.local_settings as local_settings
import logging
import numpy as np
import  requests



def perp_pnl(entry,exit,leverage,side,collateral):
 
    if side == 'Long':
        ls = 1          
    elif side == 'Short':
        ls = -1

    position = np.round(collateral*leverage,3)
    # rollover = 0.0063/100
    # usdting = 0.0015/100
    # liq_price_distance = entry * ( collateral*0.9 - rollover*collateral - usdting*collateral )/collateral/leverage
    # liq_price = np.round(entry - ls*liq_price_distance,3)

    pnl_frac  = np.round(ls*leverage*(exit - entry)/entry,5)
    pnl_val = np.round(collateral*pnl_frac,4)
    pnl_perc = np.round(np.abs(pnl_frac*100),3)

    # print('trade stats:')
    return pnl_val,pnl_perc