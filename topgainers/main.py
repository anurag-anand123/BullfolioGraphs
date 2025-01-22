import pandas as pd
import yfinance as yf
import mplfinance as mpf
from datetime import datetime, timedelta
import os
import shutil

# Constants
GRAPH_FOLDER = 'graph_custom'

# Binance Dark Theme
binance_dark = {
    "base_mpl_style": "dark_background",
    "marketcolors": {
        "candle": {"up": "#3dc985", "down": "#ef4f60"},
        "edge": {"up": "#3dc985", "down": "#ef4f60"},
        "wick": {"up": "#3dc985", "down": "#ef4f60"},
        "volume": {"up": "#247252", "down": "#82333f"},
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
        "axes.labelsize": 8,
        "axes.titlesize": 10,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7,
    },
}

def read_csv_and_get_symbols(file_path):
    """Read CSV and extract stock symbols."""
    try:
        df = pd.read_csv(file_path)
        if 'Symbol' not in df.columns:
            raise KeyError("The CSV file must contain a 'Symbol' column.")
        return df['Symbol'].tolist()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except KeyError as e:
        print(e)
        return []

def fetch_stock_data(symbol, interval):
    """Fetch historical stock data for a given symbol."""
    try:
        data = yf.download(symbol, period='2d', interval=interval)
        if data.empty or len(data) < 2:
            print(f"Insufficient data for {symbol}.")
            return None
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def calculate_percentage_change(data):
    """Calculate today's or last trading day's percentage change."""
    try:
        close_prices = data['Close']
        percent_change = ((close_prices.iloc[-1] - close_prices.iloc[-2]) / close_prices.iloc[-2]) * 100
        return percent_change
    except Exception as e:
        print(f"Error calculating percentage change: {e}")
        return None

def save_candlestick_chart(data, symbol, rank, return_percent):
    """Save the candlestick chart."""
    try:
        file_name = os.path.join(GRAPH_FOLDER, f"{rank}.png")
        title = f"{symbol} - Change: {return_percent:.2f}%"
        mpf.plot(
            data,
            type='candle',
            style=binance_dark,
            title=title,
            ylabel='Price',
            savefig=dict(fname=file_name, dpi=300, bbox_inches='tight'),
            figratio=(20, 9),
            figscale=0.8,
        )
        print(f"Candlestick chart saved for {symbol} as {file_name}.")
    except Exception as e:
        print(f"Error saving candlestick chart for {symbol}: {e}")

def main():
    """Main function to execute the script."""
    try:
        # Get input from user
        csv_file = input("Enter the path to the CSV file containing stock symbols: ").strip()
        interval = input("Enter the data interval (e.g., '1d' for daily, '1wk' for weekly, '1mo' for monthly): ").strip()

        # Ensure the graph folder exists
        if os.path.exists(GRAPH_FOLDER):
            shutil.rmtree(GRAPH_FOLDER)
        os.makedirs(GRAPH_FOLDER)

        # Get stock symbols
        symbols = read_csv_and_get_symbols(csv_file)
        if not symbols:
            return

        results = []
        for symbol in symbols:
            print(f"Processing {symbol}...")
            data = fetch_stock_data(symbol, interval)
            if data is not None:
                percent_change = calculate_percentage_change(data)
                if percent_change is not None:
                    results.append((symbol, percent_change, data))

        results.sort(key=lambda x: x[1], reverse=True)

        for rank, (symbol, percent_change, data) in enumerate(results, start=1):
            save_candlestick_chart(data, symbol, rank, percent_change)
            print(f"{rank}. {symbol}: {percent_change:.2f}% change")

        try:
            if os.name == 'nt':
                os.startfile(GRAPH_FOLDER)
            elif os.name == 'posix':
                os.system(f'open "{GRAPH_FOLDER}"' if 'darwin' in os.uname().sysname.lower() else f'xdg-open "{GRAPH_FOLDER}"')
        except Exception as e:
            print(f"Error opening folder: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()
