import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import os

# Constants
CSV_FILE = 'ind_nifty500list.csv'
GRAPH_FOLDER = 'graph2y'

def read_csv_and_get_symbols(file_path):
    """Read CSV and extract stock symbols."""
    try:
        df = pd.read_csv(file_path)
        if 'Symbol' not in df.columns:
            raise KeyError("The CSV file must contain a 'Symbol' column.")
        return df['Symbol'].head(400).tolist()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except KeyError as e:
        print(e)
        return []

def fetch_stock_data(symbol):
    """Fetch 2-year historical stock data for a given symbol."""
    try:
        symbol_with_suffix = f"{symbol}.NS"
        data = yf.download(symbol_with_suffix, period='2y', interval='1d')
        if data.empty or len(data) < 2:
            print(f"Insufficient data for {symbol}.")
            return None
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def calculate_2y_return(data):
    """Calculate 2-year return for stock data."""
    try:
        start_price = float(data['Close'].iloc[0])  # Ensure numeric conversion
        end_price = float(data['Close'].iloc[-1])  # Ensure numeric conversion
        return ((end_price - start_price) / start_price) * 100
    except Exception as e:
        print(f"Error calculating return: {e}")
        return None

def save_stock_graph(data, symbol, rank):
    """Plot and save the stock's closing price graph in dark mode."""
    try:
        plt.style.use('dark_background')  # Set dark background style
        plt.figure()
        plt.plot(data.index, data['Close'], color='white', linewidth=1.5)  # White line for closing prices
        plt.title(f"{symbol} - 2 Year Closing Prices", color='white')
        plt.xlabel("Date", color='white')
        plt.ylabel("Closing Price", color='white')
        plt.grid(color='gray', linestyle='--', linewidth=0.5)  # Subtle grid lines
        plt.savefig(os.path.join(GRAPH_FOLDER, f"{rank}.png"), dpi=300, bbox_inches='tight')  # High-quality save
        plt.close()
    except Exception as e:
        print(f"Error saving graph for {symbol}: {e}")

def main():
    """Main function to execute the script."""
    # Ensure the graph folder exists
    if not os.path.exists(GRAPH_FOLDER):
        os.makedirs(GRAPH_FOLDER)

    # Step 1: Read the CSV and get symbols
    symbols = read_csv_and_get_symbols(CSV_FILE)
    if not symbols:
        return

    results = []

    # Step 2: Fetch data and calculate returns
    for symbol in symbols:
        print(f"Processing {symbol}...")
        data = fetch_stock_data(symbol)
        if data is not None:
            two_year_return = calculate_2y_return(data)
            if two_year_return is not None:
                results.append((symbol, two_year_return, data))

    # Filter out invalid results
    results = [(symbol, two_year_return, data) for symbol, two_year_return, data in results if isinstance(two_year_return, (int, float))]

    # Step 3: Sort by 2-year returns
    results.sort(key=lambda x: x[1], reverse=True)

    # Step 4: Save graphs and print results
    for rank, (symbol, two_year_return, data) in enumerate(results, start=1):
        save_stock_graph(data, symbol, rank)
        print(f"{rank}. {symbol}: {two_year_return:.2f}% return")

if __name__ == "__main__":
    main()
