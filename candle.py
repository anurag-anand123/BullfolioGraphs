import pandas as pd
import yfinance as yf
import mplfinance as mpf
from datetime import datetime, timedelta

binance_dark = {
    "base_mpl_style": "dark_background",
    "marketcolors": {
        "candle": {"up": "#3dc985", "down": "#ef4f60"},  
        "edge": {"up": "#3dc985", "down": "#ef4f60"},  
        "wick": {"up": "#3dc985", "down": "#ef4f60"},  
        "ohlc": {"up": "green", "down": "red"},
        "volume": {"up": "#247252", "down": "#82333f"},  
        "vcedge": {"up": "green", "down": "red"},  
        "vcdopcod": False,
        "alpha": 1,
    },
    "mavcolors": ("#ad7739", "#a63ab2", "#62b8ba"),
    "facecolor": "#1b1f24",
    "gridcolor": "#2c2e31",
    "gridstyle": "--",
    "y_on_right": True,
    "rc": {
        "axes.grid": True,
        "axes.grid.axis": "y",
        "axes.edgecolor": "#474d56",
        "axes.titlecolor": "red",
        "figure.facecolor": "#161a1e",
        "figure.titlesize": "x-large",
        "figure.titleweight": "semibold",
    },
    "base_mpf_style": "binance-dark",
}

def fetch_stock_data(symbol, start_date, interval='1d'):
    """Fetch historical stock data for a given symbol."""
    data = yf.download(symbol, start=start_date, interval=interval)
    if data.empty:
        print(f"No data found for {symbol}.")
        return None
    return data

def clean_and_prepare_data(data):
    """Clean and prepare the data for mplfinance."""
    try:
        # Flatten multi-level column index if present
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.map('_'.join).str.strip()

        # Rename columns to match mplfinance expectations
        column_mapping = {
            'Close_AAPL': 'Close',
            'High_AAPL': 'High',
            'Low_AAPL': 'Low',
            'Open_AAPL': 'Open',
            'Volume_AAPL': 'Volume',
        }
        data = data.rename(columns=column_mapping)

        # Ensure required columns are present
        required_columns = ['Open', 'High', 'Low', 'Close']
        if not all(col in data.columns for col in required_columns):
            raise KeyError(f"Required columns {required_columns} not found in data.")

        # Select relevant columns and drop NaN values
        data = data[required_columns].apply(pd.to_numeric, errors='coerce').dropna()

        # Ensure the index is a DatetimeIndex
        data.index = pd.to_datetime(data.index)

        return data
    except Exception as e:
        print(f"Error cleaning and preparing data: {e}")
        return None

def save_candlestick_chart(data, symbol, file_name):
    """Save the candlestick chart to a PNG file."""
    try:
        # Plot and save the candlestick chart
        mpf.plot(
            data,
            type='candle',
            style=binance_dark,  # Chart style
            title=f"{symbol} - 1 Year Candlestick Chart",
            ylabel='Price',
            savefig=dict(fname=file_name, dpi=300, bbox_inches='tight'),
            figratio=(20, 9),  # Aspect ratio for wider image
            figscale=1.5  # Scale to increase size
        )
        print(f"Candlestick chart saved as {file_name}.")
    except Exception as e:
        print(f"Error saving candlestick chart for {symbol}: {e}")

def main():
    """Main function to fetch, clean, and plot stock data."""
    symbol = "AAPL"  # Stock symbol for Apple
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # 1 year back
    interval = '1d'  # Daily interval
    file_name = "apple_candlestick_chart.png"  # File name to save the chart

    # Fetch stock data
    data = fetch_stock_data(symbol, start_date, interval)
    if data is not None and not data.empty:
        # Clean and prepare the data
        cleaned_data = clean_and_prepare_data(data)
        if cleaned_data is not None and not cleaned_data.empty:
            save_candlestick_chart(cleaned_data, symbol, file_name)
        else:
            print("Cleaned data is empty or invalid.")
    else:
        print(f"No data fetched for {symbol}.")

if __name__ == "__main__":
    main()
