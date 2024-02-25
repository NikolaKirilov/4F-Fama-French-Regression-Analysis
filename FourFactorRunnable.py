# Pandas to read csv file and other things
import pandas as pd
# Yfinance to download price data from Yahoo Finance
import yfinance as yf
# Statsmodels to run our multiple regression model
import statsmodels.api as smf
# To download the Fama French data from the web
import urllib.request
# To unzip the ZipFile 
import zipfile
import numpy as np


ticker = ['GE','^NDX','^SPX','TSLA']
start = "2022-01-01"
end = "2023-08-31"


def get_fama_french_carhart():
    """This fucntion downloads and prepares the raw economic data from the official webste of Kenneth R. French"""

    # Web url
    ff_url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_CSV.zip"
    mom_url = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_CSV.zip"
    
    # Download the file and save it
    # We will name it fama_french.zip file
    urllib.request.urlretrieve(ff_url,'fama_french.zip')
    zip_file = zipfile.ZipFile('fama_french.zip', 'r')
    
    urllib.request.urlretrieve(mom_url,'MOM.zip')
    MOM_file = zipfile.ZipFile('MOM.zip', 'r')
    
    # Next we extact the file data
    zip_file.extractall()
    MOM_file.extractall()
    
    # Make sure you close the file after extraction
    zip_file.close()
    MOM_file.extractall()
    
    # Now open the CSV file
    ff_factors = pd.read_csv('F-F_Research_Data_Factors.csv', skiprows = 3, index_col = 0)
    FourF = pd.read_csv('F-F_Momentum_Factor.csv', skiprows = 13, index_col = 0)
 
    # We want to find out the row with NULL value
    # We will skip these rows
    ff_row = ff_factors.isnull().any(axis=1).to_numpy().nonzero()[0][0]
    FourF_row = FourF.isnull().any(axis=1).to_numpy().nonzero()[0][0]
    
    # Read the csv file again with skipped rows
    ff_factors = pd.read_csv('F-F_Research_Data_Factors.csv', skiprows = 3, nrows = ff_row, index_col = 0)
    FourF = pd.read_csv('F-F_Momentum_Factor.csv', skiprows = 13, nrows = FourF_row, index_col = 0)
    
    # Format the date index
    ff_factors.index = pd.to_datetime(ff_factors.index, format= '%Y%m')
    FourF.index = pd.to_datetime(FourF.index, format= '%Y%m')
    
    # Format dates to end of month
    ff_factors.index = ff_factors.index + pd.offsets.MonthEnd()
    FourF.index = FourF.index + pd.offsets.MonthEnd()
    
    # Convert from percent to decimal
    ff_factors = ff_factors.apply(lambda x: x/ 100)
    FourF = FourF.apply(lambda x: x/ 100)
    
    #four_factor_data = ff_factors.join(FourF)
    four_factor_data = pd.concat([ff_factors,FourF],axis=1)
    
    return four_factor_data



def get_price_yfin(ticker, start, end):
    '''
    Function to download the historic Adj Close price from Yahoo Finance

    Parameters:
    ticker = The ticker of you need the data for
    start = From when do you want to parse the data
    end = Until when do you want to parse the data

    Returns:
    DataFrame: DataFrame with the historic data of the Adjusted Close Price
    '''
    price = yf.download(tickers=ticker,start=start,end=end)
    price = price['Adj Close'] # keep only the Close Price colmn
    return price

def get_return_data(price_yfin, period = "M"):
    """
    This function calculates the monthly returns of a given stock price.

    Parameters:
    price_yfin (DataFrame): A DataFrame containing the stock price data.
    period (str): The period of the return calculation. Default is set to "M" for monthly returns.

    Returns:
    DataFrame: A DataFrame containing the monthly returns of the stock price.
    """    
    # Resample the data to monthly price
    price = price_yfin.resample(period).last()
    
    # Calculate the percent change
    ret_data = price.pct_change()[1:]
    
    # convert from series to DataFrame
    ret_data = pd.DataFrame(ret_data)
    
    # Rename the Column
    ret_data.columns = ['portfolio']
    return ret_data
    


def run_reg_model(tickers, start, end):
    """
    Runs the Fama-French regression model for a list of tickers and returns a DataFrame of coefficients.

    Parameters:
    tickers (list): List of ticker symbols to run the regression model for.

    Returns:
    DataFrame: DataFrame of regression coefficients for each ticker.
    """
    # Initialize an empty DataFrame to store the coefficients
    coeffs = pd.DataFrame()

    # Iterate over the tickers in the list
    for ticker in tickers:
        # Get FF data
        ff_data = get_fama_french_carhart()
        ff_last = ff_data.index[-1].date()

        #Get the fund price data
        price_data = get_price_yfin(ticker, start, end)
        price_data = price_data.loc[:ff_last]
        ret_data = get_return_data(price_data, "M")
        all_data = pd.merge(pd.DataFrame(ret_data),ff_data, how = 'inner', left_index= True, right_index= True)
        all_data.rename(columns={"Mkt-RF":"mkt_excess"}, inplace=True)
        all_data.rename(columns = {'Mom   ':'mom'}, inplace = True)
        all_data['port_excess'] = all_data['portfolio'] - all_data['RF']

        # Run the model
        model = smf.formula.ols(formula = "port_excess ~ mkt_excess + SMB + HML + mom", data = all_data).fit()
        result = pd.DataFrame(model.params)
        result.rename(columns = {0:ticker}, inplace=True)

        # Concatenate the resulting DataFrame of coefficients to the main DataFrame
        coeffs = pd.concat([coeffs, result], axis=1)

    return coeffs




def run_regression_analysis(tickers, start, end):
    """
    This function runs the Fama-French regression model for a list of tickers and saves the results to a CSV file.

    Parameters:
    tickers (list): A list of stock tickers to analyze.
    start (str): The start date of the analysis.
    end (str): The end date of the analysis.

    Returns:
    DataFrame: A Dataframe with the analysis for the tickers
    """
    # Create a DataFrame from the list of tickers
    TickerList = tickers
    df_ticker = pd.DataFrame(TickerList)

    # Apply the run_reg_model function to each ticker and concatenate the results
    applied = df_ticker.apply(run_reg_model, args=(start, end), axis=1)

    # Turn the resulting DataFrame into a regular DataFrame
    df = pd.DataFrame(applied)

    # Rename the 'Intercept' column to 'FF-alpha'
    df.rename(columns={'Intercept': 'FF-alpha'}, inplace=True)

    # Save the DataFrame to a CSV file
    df.to_csv("outputSid.csv")

    return df



