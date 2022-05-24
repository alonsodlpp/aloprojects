# Cryptocurrencies real-time price

In this project, a web app has been created which shows the price in real time of three cryptocurrencies.

The user can analize the price of Bitcoin, Dogecoin and Ethereum and their conversion to USD or Euros by means of Candlestick graphics. At the bottom is also displayed the volume negotiated in the interval of time selected by the user. The user can also set the date from when he wants to visualize the price.  

It is only possible to download 720 data rows from the Kraken API, so, in consequence, if the user wants to get earlier data, he should change the interval of the data and set wider intervals of time. The intervals that are available are:
- 1 minute
- 5 minutes
- 15 minutes
- 30 minutes
- 1 hour
- 4 hours
- 1 day
- 7 days
- 15 days

The Volume-Weighted Average Price (VWAP) is included in two forms. There is a "complete" VWAP that takes into account all the present data and that is allways calculated and displayed. In addition, there is a VWAP that only takes into account the intervals that the user selects. This VWAP is only displayed if the user wants to. There is a button in the sidebar that, when checked, this "interval" VWAP is also graphed.


# Resources
- The programming language used is Python.
- This app is connected to the Kraken API and downloads in real time the price of this three cryptocurrencies.
- The main Python libraries used in this project are: 
    - Pykrakenapi to connect to the API in order to download the data.
    - Plotly to create the candlesticks graphs, the bar charts and the line graphs for the VWAP.
    - Streamlit to create the web app.
 
