import pandas as pd
import yfinance as yf
import mplfinance as mpf
from datetime import datetime, timedelta
import os
import shutil

# Constants
GRAPH_FOLDER = 'graph_custom'

suffix = ""
csv_file = ""

# Binance Dark Theme
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
        "figure.titlesize": 10,   # Reduced title size
        "figure.titleweight": "semibold",
        "axes.labelsize": 5,      # Reduced label size
        "axes.titlesize": 8,      # Reduced axes title size
        "xtick.labelsize": 5,     # Reduced x-axis tick label size
        "ytick.labelsize": 5,     # Reduced y-axis tick label size
    },
    "base_mpf_style": "binance-dark",
}


def read_csv_and_get_symbols(file_path):
    """Read CSV and extract stock symbols."""
    try:
        df = pd.read_csv(file_path)
        if 'Symbol' not in df.columns:
            raise KeyError("The CSV file must contain a 'Symbol' column.")
        # Limit to first 1300 symbols (or adjust as needed)
        return df['Symbol'].head(1300).tolist()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except KeyError as e:
        print(e)
        return []


def fetch_stock_data(symbol, start_date, interval):
    """Fetch historical stock data for the given symbol and time period for charting."""
    try:
        symbol_with_suffix = f"{symbol}{suffix}"
        data = yf.download(symbol_with_suffix, start=start_date, interval=interval)
        if data.empty or len(data) < 2:
            print(f"Insufficient data for {symbol}.")
            return None
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def get_all_time_high(symbol):
    """
    Fetch the full historical data for the symbol and return the maximum closing price.
    This value is treated as the all‐time high.
    """
    try:
        symbol_with_suffix = f"{symbol}{suffix}"
        ticker = yf.Ticker(symbol_with_suffix)
        full_data = ticker.history(period="max")
        if full_data.empty or 'Close' not in full_data.columns:
            print(f"No full historical data for {symbol}.")
            return None
        return full_data["Close"].max()
    except Exception as e:
        print(f"Error fetching full historical data for {symbol}: {e}")
        return None


def clean_and_prepare_data(data, symbol):
    """Clean and prepare the data for mplfinance."""
    try:
        # If data has MultiIndex columns, flatten them
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.map('_'.join).str.strip()

        # Create a mapping for expected column names
        column_mapping = {
            f"Close_{symbol}{suffix}": 'Close',
            f'High_{symbol}{suffix}': 'High',
            f'Low_{symbol}{suffix}': 'Low',
            f'Open_{symbol}{suffix}': 'Open',
            f'Volume_{symbol}{suffix}': 'Volume',
        }
        data = data.rename(columns=column_mapping)

        required_columns = ['Open', 'High', 'Low', 'Close']
        if not all(col in data.columns for col in required_columns):
            raise KeyError(f"Required columns {required_columns} not found in data.")

        # Ensure numeric conversion and drop any rows with missing values
        data = data[required_columns].apply(pd.to_numeric, errors='coerce').dropna()
        data.index = pd.to_datetime(data.index)
        return data
    except Exception as e:
        print(f"Error cleaning and preparing data for {symbol}: {e}")
        return None


def save_candlestick_chart(data, symbol, rank, ath_ratio, all_time_high):
    """Save the candlestick chart with a title showing the ATH ratio."""
    try:
        cleaned_data = clean_and_prepare_data(data, symbol)
        if cleaned_data is None or cleaned_data.empty:
            print(f"Insufficient or invalid data for {symbol}.")
            return

        file_name = os.path.join(GRAPH_FOLDER, f"{rank}.png")
        title = (f"{symbol} - Trading at {ath_ratio * 100:.2f}% of its All-Time High "
                 f"(ATH: {all_time_high:.2f})")
        mpf.plot(
            cleaned_data,
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
    global suffix, csv_file, GRAPH_FOLDER
    """Main function to execute the script."""
    try:
        # Ask user to select the country
        country = input("Do you want to analyze stocks from 'US(us)' or 'India(india)'? ").strip().lower()
        if country not in ['us', 'india']:
            print("Invalid choice. Please enter either 'US' or 'India'.")
            return

        # Set the exchange details based on the selected country
        if country == 'us':
            suffix = ""        # US stocks typically don't require a suffix for yfinance
            csv_file = 'us.csv'  # Replace with your US stock list CSV
        elif country == 'india':
            suffix = ".NS"
            csv_file = 'india.csv'  # Replace with your India stock list CSV

        # Ask user for the time period and interval for the candlestick chart
        duration_type = input("Do you want to enter the duration in 'weeks' or 'months'? ").strip().lower()
        if duration_type not in ['weeks', 'months']:
            print("Invalid choice. Please enter either 'weeks' or 'months'.")
            return

        duration = int(input(f"Enter the number of {duration_type} for historical data: "))
        interval = input("Enter the data interval (e.g., '1d' for daily, '1wk' for weekly, '1mo' for monthly): ").strip()

        # Calculate the start date based on the duration type
        if duration_type == 'weeks':
            start_date = (datetime.now() - timedelta(weeks=duration)).strftime('%Y-%m-%d')
        elif duration_type == 'months':
            start_date = (datetime.now() - timedelta(days=duration * 30)).strftime('%Y-%m-%d')

        print(f"Fetching chart data from {start_date} with interval '{interval}'.")

    except ValueError:
        print("Invalid input. Please enter valid numbers and interval.")
        return

    # Create a unique folder for saving the charts based on the chosen period and interval
    GRAPH_FOLDER = f"{duration}{duration_type}{interval}"
    if os.path.exists(GRAPH_FOLDER):
        shutil.rmtree(GRAPH_FOLDER)
    os.makedirs(GRAPH_FOLDER)

    symbols = read_csv_and_get_symbols(csv_file)
    if not symbols:
        return

    results = []
    # Process each symbol: fetch chart data and calculate how close it is trading to its all-time high.
    for symbol in symbols:
        print(f"Processing {symbol}...")
        chart_data = fetch_stock_data(symbol, start_date, interval)
        if chart_data is not None:
            # Get the full historical data to calculate the all-time high
            all_time_high = get_all_time_high(symbol)
            if all_time_high is None:
                continue
            # Convert the values to float to ensure they are scalars
            try:
                current_price = float(chart_data['Close'].iloc[-1])
                all_time_high_val = float(all_time_high)
            except Exception as e:
                print(f"Error converting price data for {symbol}: {e}")
                continue

            # Calculate the ratio (current price / all-time high)
            ath_ratio = current_price / all_time_high_val
            results.append((symbol, ath_ratio, chart_data, all_time_high_val))

    # Sort symbols by the ATH ratio in descending order (closest to ATH first)
    results.sort(key=lambda x: x[1], reverse=True)

    # Save the candlestick charts with ranking numbers
    for rank, (symbol, ath_ratio, chart_data, all_time_high) in enumerate(results, start=1):
        save_candlestick_chart(chart_data, symbol, rank, ath_ratio, all_time_high)
        print(f"{rank}. {symbol}: Trading at {ath_ratio * 100:.2f}% of its All-Time High")

    # Attempt to open the folder containing the charts
    try:
        if os.name == 'nt':
            os.startfile(GRAPH_FOLDER)
        elif os.name == 'posix':
            # For macOS or Linux
            opener = 'open' if 'darwin' in os.uname().sysname.lower() else 'xdg-open'
            os.system(f'{opener} "{GRAPH_FOLDER}"')
    except Exception as e:
        print(f"Error opening folder: {e}")


if __name__ == "__main__":
    main()
