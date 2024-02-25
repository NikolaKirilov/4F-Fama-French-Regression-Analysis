# 4F-Fama-French-Regression-Analysis
This code performs a Fama-Frenchression analysis for a list of stock tickers and saves the results to a CSV file. It is based on the Fama-French-factor model, which includes the market risk premium, the size factor, and the value factor.

# Requirements
To run this code, you need to install the following Python packages:

* pandas
* yfinance
* statsmodels
* numpy
* urllib
* zipfile


# Usage
Import the run_regression_analysis function from the fama_french_regression.py module.

from fama_french_regression import run_regression_analysis

Define a list of stock tickers to analyze.<br />
For exmaple: tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

Define the start and end dates for the analysis:<br />
start = 'YYYY-MM-DD'<br />
end = 'YYYY-MM-DD'<br />

Call the run_regression_analysis function with the list of tickers and the start and end dates.<br />
df = run_regression_analysis(tickers, start, end)<br />
The function will return a DataFrame with the analysis for the tickers. 

The results will be saved to a CSV file named "outputSid.csv" in the same directory as the script.

# Code Overview
The code consists of the following functions:

get_fama_french_carhart(): This function downloads and prepares the raw economic data from the official website of Kenneth R. French.<br />
get_price_yfin(ticker, start, end): This function downloads the historic Adj Close price from Yahoo Finance.<br />
get_return_data(price_yfin, period = "M"): This function calculates the monthly returns of a given stock price.<br />
run_reg_model(tickers, start, end): This function runs the Fama-French regression model for a list of tickers and returns a DataFrame of coefficients.<br />
run_regression_analysis(tickers, start, end): This function runs the Fama-French regression model for a list of tickers and saves the results to a CSV file.<br />

# License
This code is released under the MIT License. See the LICENSE file for more information.

# Acknowledgements
The Fama-French regression analysis is based on the Fama-French three-factor model, which was developed by Eugene Fama and Kenneth French. The raw economic data is provided by Kenneth R. French.

# Disclaimer
This code is provided as-is, without any warranty or support. The author is not responsible for any errors, omissions, or damages that may result from using this code.
