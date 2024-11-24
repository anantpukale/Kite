import time
from configparser import ConfigParser
from yfinance_fisher_app import FisherApp
import os
import datetime
import pandas as pd

def main_function():
    print("Fisher Value Script Running")
    current_directory = os.getcwd()
    print("Current Directory:", current_directory)
    config = ConfigParser()
    config.read(f'{current_directory}/config/config.ini')
    #config.read('../config/config.ini')
    now = datetime.datetime.now().strftime("%Y-%m-%d")
    current_dir = os.path.dirname(__file__)
    #file_path = os.path.join(current_dir, 'config', 'stock_symbol.csv')
    equity_list = pd.read_csv(f'{current_directory}/config/stock_symbol.csv')
    #equity_list = pd.read_csv("../config/stock_symbol.csv")
    app = FisherApp()
    app.log_in()
    stock_list = equity_list['tradingsymbol'].values
    #stock_list = ["AUTOAXLES","SAMPANN-BE","BHINVIT-IV","ALLDIGI","ORIENTALTL","PATINTLOG","SADHNANIQ","DIGIDRIVE","COMSYN","MRO-TEK-BE","JYOTICNC","ADL-BE","ANDHRAPAP","MASFIN","MAZDOCK","IEX","NIRAJ-BE","BALKRISIND","SRPL","BPCL","BAJAJ-AUTO","ASTRAL","MARUTI","SHRIRAMFIN","VOLTAS","PFC","HEROMOTOCO"]
    stock_list = ["HDFCBANK","RELIANCE"]
    print(f"START TIME {datetime.datetime.now()}")
    count = 0
    for stock in stock_list:
        count = count+1
        print(f"{stock} for count {count}" )
        if len(app.df) >= 50:
            break
        # if  count % 20 == 0:
        #     time.sleep(5)
        app.symbol = stock
        try:
            #time.sleep(2)
            #app.get_tradingview_code_fisher_index(config)
            app.get_historic_pe_eps()
        except Exception as e:
            # Print the error message
            print(f"EXCEPTION: {stock} An error occurred: {e}")
            pass
    print(app.df)
    app.df.to_csv(f'data/fundamental_value{now}.csv', mode='w')
    print(f"START TIME {datetime.datetime.now()}")
    app.driver.quit()



if __name__ == "__main__":
    main_function()
