from enum import Enum

from sklearn.preprocessing import StandardScaler, MinMaxScaler

#from predict_example import kaggle_stock_market_Tech
import Utils_Yfinance
import Utils_buy_sell_points
import Utils_col_sele
import Utils_plotter
import talib_technical_crash_points
import talib_technical_funtions
import talib_technical_PY_TI
import talib_technical_pandas_TA
import talib_technical_pandas_TU
import yfinance as yf
import pandas as pd
import numpy as np


from LogRoot.Logging import Logger
from talib_technical_class_object import TechData
from yhoo_external_raw_factors import DICT_EXTERNAL_FACTORS


class Option_Historical(Enum):
    YEARS_3 = 1
    MONTH_3 = 2
    DAY_20 = 3

list_stocks = ["RIVN", "VWDRY", "TWLO",          "GOOG","ASML","SNOW","ADBE","LYFT","UBER","ZI", "BXP","ANET","MITK","QCOM","PYPL","JBLU","IAG.L",]
list_stocks = ["GE","SPOT","F","SAN.MC","TMUS","MBG.DE","INTC","TRIG.L","GOOG","ASML","SNOW","ADBE","LYFT","UBER","ZI", "BXP","ANET","MITK","QCOM","PYPL","JBLU","IAG.L",
                "UBSG.ZU","NDA.DE","TWTR","ITX.MC","PFE","FER.MC","AA","ABBN.ZU","RUN","IBE.MC","ESP35","BAYN.DE","GTLB","IBM","NESN.ZU","MDB","NVDA","CSCO","AMD","ADSK","AMZN",
                "RR.L","BABA","MBT","AAPL","NFLX","BA","VWS.CO","FFIV","GOOG","MSFT","AIR.PA","ABNB","BTC","TSLA","FB","REP.MC","BBVA.MC","OB"]

# BEGIN_DATE = '2019-01-01'
# END_DATE = '2025-01-01'
STOCKID = "UBER"

Y_TARGET = 'buy_sell_point'


def get_historial_data_3y(stockID, prepos=True):
    yho_stk = yf.Ticker(stockID)
    hist = yho_stk.history(period="3y", prepost=prepos)

    df_his = pd.DataFrame(hist)
    df_his.reset_index(inplace=True)
    df_his = df_his.drop(columns=['Dividends', 'Stock Splits'],errors='ignore')

    return df_his

def get_historial_data_3_month(stockID, prepos=True, interva="15m"):
    yho_stk = yf.Ticker(stockID)
    hist = yho_stk.history(period="60d",prepost=prepos, interval=interva)

    df_his = pd.DataFrame(hist)
    df_his.reset_index(inplace=True)
    df_his = df_his.drop(columns=['Dividends', 'Stock Splits'],errors='ignore')

    df_his = df_his.rename(columns={'Datetime': 'Date'})
    df_his['Date'] = df_his['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')

    # for c in ['Open', 'High', 'Low', 'Close', 'Volume']:
    #     df_his[c] = df_his[c].round(3)
    #     #df_his = df_his.rename(columns={c: c+"_m"})

    return df_his

def get_historial_data_20_days(stockID, prepos=True, interva="15m"):
    yho_stk = yf.Ticker(stockID)
    #en 15 min , 1d es 25 filas
    hist = yho_stk.history(period="20d",prepost=prepos, interval=interva)

    df_his = pd.DataFrame(hist)
    df_his.reset_index(inplace=True)
    df_his = df_his.drop(columns=['Dividends', 'Stock Splits'],errors='ignore')

    df_his = df_his.rename(columns={'Datetime': 'Date'})
    df_his['Date'] = df_his['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    return df_his



def get_stock_history_Tech_download(stockId, opion, get_technical_data = False, prepost=True, interval="30m",
                                    add_stock_id_colum = False, costum_columns = None):

    df_his = __select_dowload_time_config(interval, opion, prepost, stockId)

    if add_stock_id_colum:
        df_his.insert(loc=1, column='ticker', value=stockId)

    if df_his is None:
        Logger.logr.debug("d_price/" + stockId + "_stock_history_"+str(opion.name)+".csv  is NONE stock: " + stockId)
    else:
        if get_technical_data:
            df_his = get_technical_data_and_NQ(costum_columns, df_his, interval, opion)

        df_his['Date'] = df_his['Date'].astype(str)
        df_his.reset_index(drop=True, inplace=True)
        if costum_columns is None:
            df_his.to_csv("d_price/" + stockId + "_stock_history_"+str(opion.name)+".csv", sep="\t", index=None)
            Logger.logr.info("d_price/" + stockId + "_stock_history_"+str(opion.name)+".csv  stock: " + stockId + " Shape: " + str(df_his.shape))

    return df_his


def get_technical_data_and_NQ(costum_columns, df_his, interval, opion):

    df_his = TechData(df_his, costum_columns).get_ALL_tech_data()

    # NASDAQ external factor
    if costum_columns is None or any("NQ_" in co for co in costum_columns):
        exter_id_NQ = "NQ=F"
        df_his = get_external_factor(df_his, exter_id_NQ, interval, opion, remove_str_in_colum="=F",
                                     startswith_str_in_colum='NQ_')
    if costum_columns is not None:
        start_columns = ['Date', 'buy_sell_point', 'Open', 'High', 'Low', 'Close', 'Volume', 'per_Close',
                         'per_Volume', 'has_preMarket', 'per_preMarket']
        df_his = df_his[start_columns + costum_columns]
        df_his = df_his.loc[:, ~df_his.columns.duplicated()].copy()
    return df_his


def get_external_factor(df_his, exter_id_NQ, interval, opion, remove_str_in_colum = "=F",startswith_str_in_colum = 'NQ_'):
    df_ext = __select_dowload_time_config(interval, opion, prepost=False, stockId=exter_id_NQ)

    df_ext = Utils_Yfinance.add_variation_percentage(df_ext, prefix=exter_id_NQ + "_")
    df_ext.ta.sma(length=20, prefix=exter_id_NQ, cumulative=True, append=True)
    df_ext.ta.sma(length=100, prefix=exter_id_NQ, cumulative=True, append=True)
    df_ext = df_ext.rename(columns={'Volume': exter_id_NQ + "_"'Volume', 'Close': exter_id_NQ + "_"'Close'})

    names_col = [col for col in df_ext.columns if col.startswith(exter_id_NQ + "_")]
    df_ext = df_ext[['Date'] + names_col]
    for ncol in names_col:
        df_ext = df_ext.rename(columns={ncol: ncol.replace(remove_str_in_colum, "")})

    df_his = pd.merge(df_his, df_ext, how='left')

    cols_NQ = [col for col in df_his.columns if col.startswith(startswith_str_in_colum)]
    df_his[cols_NQ] = df_his[cols_NQ].fillna(method='ffill')
    df_his[cols_NQ] = df_his[cols_NQ].fillna(method='bfill')
    return df_his


def __select_dowload_time_config(interval, opion, prepost, stockId):
    df_his = None
    if opion.value == Option_Historical.YEARS_3.value:
        df_his = get_historial_data_3y(stockId, prepos=prepost)
    elif opion.value == Option_Historical.MONTH_3.value:
        df_his = get_historial_data_3_month(stockId, prepos=prepost, interva=interval)
    elif opion.value == Option_Historical.DAY_20.value:
        df_his = get_historial_data_20_days(stockId, prepos=prepost, interva=interval)
    return df_his


def get_stock_history_Tech_Local(df_his):
    df_his.reset_index(drop=True, inplace=True)
    df_his = TechData(df_his).get_ALL_tech_data()
    df_his['Date'] = df_his['Date'].astype(str)
    df_his.reset_index(drop=True, inplace=True)

    Logger.logr.debug("get_stock_history_Tech_Local  Shape: " + str(df_his.shape))

    return df_his




def get_favs_SCALA_csv_stocks_history_Download_list(list_companys, csv_name, opion ):

     # ["ma_T3_50", "ma_TEMA_50", "ma_DEMA_100", "ma_T3_100", "ma_TEMA_100"]

    df_all = pd.DataFrame()
    df_all_generate_history = pd.DataFrame()

    for l in list_companys:
        df_all_generate_history ,df_l = get_favs_SCALA_csv_stocks_history_Download_One(df_all_generate_history, l, opion)
        df_all = pd.concat([df_all,df_l ])

    #
    df_all_generate_history = df_all_generate_history.sort_values(by=['Date', 'ticker'], ascending=True)
    max_recent_date = pd.to_datetime(df_all_generate_history['Date'].max() ).strftime("%Y%m%d")
    min_recent_date = pd.to_datetime(df_all_generate_history['Date'].min() ).strftime("%Y%m%d")
    df_all_generate_history.to_csv("d_price/wRAW_" + csv_name + "_history_" + max_recent_date + "__" + min_recent_date + ".csv", sep='\t', index=None)


    df_all = df_all.sort_values(by=['Date', 'ticker'], ascending=True)
    df_all.insert(1, 'ticker', df_all.pop('ticker'))
    df_all.to_csv("d_price/" + csv_name + "_SCALA_stock_history_" + str(opion.name) + "_sep.csv", sep='\t', index=None)
    print("get_favs_SCALA_csv_stocks_history_Download d_price/" + csv_name + "_SCALA_stock_history_" + str(opion.name) + ".csv  Shape: " + str(df_l.shape))
    return df_all


def get_favs_SCALA_csv_stocks_history_Download_One(df_all_generate_history, l, opion, generate_csv_a_stock = True, costum_columns = None):
    sc = MinMaxScaler(feature_range=(-100, 100))


    df_l = get_stock_history_Tech_download(l, opion, get_technical_data=True,
                                           prepost=True, interval="15m", add_stock_id_colum=False, costum_columns = costum_columns)

    if costum_columns is None:
        df_l_generate_history = df_l[Utils_col_sele.RAW_PURE_COLUMNS]
        df_l_generate_history.insert(loc=1, column='ticker', value=l)
        df_all_generate_history = pd.concat([df_all_generate_history, df_l_generate_history])


    df_l['buy_sell_point'].replace([101, -101], [100, -100], inplace=True)
    df_l = df_l.drop(columns=Utils_col_sele.COLUMNS_DELETE_NO_ENOGH_DATA, errors='ignore')  # luego hay que borrar los nan y daña mucho el dato
    for c in [col for col in df_l.columns if col.startswith('cdl_')]:  # a pesar de que no se haya dado ningun patron de vela el Scaler tiene que respetar el mas menos
        df_l.at[0, c] = -100
        df_l.at[1, c] = 100

    aux_date_save = df_l['Date']  # despues se añade , hay que pasar el sc.fit_transform
    df_l['Date'] = 0
    array_stock = sc.fit_transform(df_l)
    df_l = pd.DataFrame(array_stock, columns=df_l.columns)
    df_l.insert(loc=1, column='ticker', value=l)
    df_l['Date'] = aux_date_save  # to correct join

    if costum_columns is None:
        if generate_csv_a_stock:
            print("get_favs_SCALA_csv_stocks_history_Download d_price/" + l + "_SCALA_stock_history_" + str(
                opion.name) + ".csv  Shape: " + str(df_l.shape))
            df_l.to_csv("d_price/" + l + "_SCALA_stock_history_" + str(opion.name) + ".csv", sep='\t', index=None)
    return df_all_generate_history, df_l


def get_favs_SCALA_csv_tocks_history_Local(df_his_stock, csv_name, opion):
    from sklearn.preprocessing import StandardScaler, MinMaxScaler
    sc = StandardScaler()
    sc = MinMaxScaler(feature_range=(-100, 100))

    df_all = pd.DataFrame()

    for l in df_his_stock['ticker'].unique():
        df_l = df_his_stock[df_his_stock['ticker'] == l]


        df_l = get_stock_history_Tech_Local(df_l)

        # df_l = pd.read_csv("d_price/" + l + "_stock_history_" + str(opion.name) + ".csv", index_col=False, sep='\t')
        df_l['buy_sell_point'].replace([101, -101], [100, -100], inplace=True)
        df_l = df_l.drop(columns=Utils_col_sele.COLUMNS_DELETE_NO_ENOGH_DATA, errors='ignore')  # luego hay que borrar los nan y daña mucho el dato
        for c in Utils_col_sele.COLUMNS_CANDLE:  # a pesar de que no se haya dado ningun patron de vela el Scaler tiene que respetar el mas menos
            df_l.at[0,c] = -100
            df_l.at[1,c] = 100

        #df_his_stock[df_his_stock.isin([np.nan, np.inf, -np.inf])]
        aux_date_save = df_l.pop('Date') #despues se añade , hay que pasar el sc.fit_transform
        aux_ticker_save = df_l.pop('ticker')

        array_stock = sc.fit_transform(df_l)
        df_l = pd.DataFrame(array_stock, columns=df_l.columns)

        #para poner date la primera y ticker la segunda
        df_l.insert(0, 'ticker', aux_ticker_save)
        df_l.insert(0, 'Date', aux_date_save)

        print("Local d_price/" + l + "_SCALA_stock_history_" + str(opion.name) + ".csv  Shape: " + str(df_l.shape))
        # df_l.to_csv("d_price/" + l + "_SCALA_stock_history_" + str(opion.name) + ".csv", sep='\t', index=None)
        df_all = pd.concat([df_all,df_l ])

    df_all = df_all.sort_values(by=['Date', 'ticker'], ascending=True)
    df_all.insert(1, 'ticker', df_all.pop('ticker'))
    df_all.to_csv("d_price/" + csv_name + "_SCALA_stock_history_L_" + str(opion.name) + "_sep.csv", sep='\t', index=None)
    print("get_favs_SCALA_csv_stocks_history_Download d_price/" + csv_name + "_SCALA_stock_history_L_" + str(opion.name) + ".csv  Shape: " + str(df_l.shape))
    return df_all


STOCKID = "UPST" # "UPST" #"BA"
# # for s in list_stocks:
# get_json_stock_values_history(STOCKID, Option_Historical.YEARS_3, get_technical_data = True, prepost=False )
#get_favs_SCALA_csv_stocks_history_Download(["TWLO"],"TEST_buy_points", Option_Historical.MONTH_3)
# yho_stk = yf.Ticker("MELI")

# hist = yho_stk.history(period="1mo", prepost=True, interval="30m")
#
# print(hist.head())
##PS C:\Users\leci\AppData\Local\Programs\Python\Python38\Scripts> .\jupyter.exe notebook C:\Users\Luis\Desktop\LecTrade