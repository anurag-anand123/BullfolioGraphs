import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
import shutil

# Constants
CSV_FILE = 'ind_nifty500list.csv'
GRAPH_FOLDER = 'graph_custom'

def read_csv_and_get_symbols(file_path):
    """Read CSV and extract stock symbols."""
    try:
        df = pd.read_csv(file_path)
        if 'Symbol' not in df.columns:
            raise KeyError("The CSV file must contain a 'Symbol' column.")
        return df['Symbol'].head(500).tolist()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return []
    except KeyError as e:
        print(e)
        return []

def fetch_stock_data(symbol, start_date, interval):
    """Fetch historical stock data for a given symbol."""
    try:
        symbol_with_suffix = f"{symbol}.NS"
        data = yf.download(symbol_with_suffix, start=start_date, interval=interval)
        if data.empty or len(data) < 2:
            print(f"Insufficient data for {symbol}.")
            return None
        return data
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def calculate_return(data):
    """Calculate stock return for the given data."""
    try:
        start_price = float(data['Close'].iloc[0])  # Ensure numeric conversion
        end_price = float(data['Close'].iloc[-1])  # Ensure numeric conversion
        return ((end_price - start_price) / start_price) * 100
    except Exception as e:
        print(f"Error calculating return: {e}")
        return None

def save_stock_graph(data, symbol, rank, return_percent):
    """Plot and save the stock's closing price graph in dark mode."""
    try:
        plt.style.use('dark_background')  # Set dark background style
        plt.figure(figsize=(12, 6))  # Wider figure with 12 inches width and 6 inches height
        plt.plot(data.index, data['Close'], color='white', linewidth=1)  # White line for closing prices
        plt.title(f"{symbol} - Return: {return_percent:.2f}%", color='white')
        plt.xlabel("Date", color='white')
        plt.ylabel("Closing Price", color='white')
        plt.grid(color='gray', linestyle='--', linewidth=0.2)  # Subtle grid lines
        plt.savefig(os.path.join(GRAPH_FOLDER, f"{rank}.png"), dpi=300, bbox_inches='tight')  # High-quality save
        plt.close()
    except Exception as e:
        print(f"Error saving graph for {symbol}: {e}")

def main():
    """Main function to execute the script."""
    # Ask user for number of months and interval
    try:
        months = int(input("Enter the number of months for historical data (e.g., 18 for 1.5 years): "))
        interval = input("Enter the data interval (e.g., '1d' for daily, '1wk' for weekly, '1mo' for monthly): ").strip()
    except ValueError:
        print("Invalid input. Please enter valid numbers and interval.")
        return

    # Calculate start date based on user input
    start_date = (datetime.now() - timedelta(days=months * 30)).strftime('%Y-%m-%d')
    print(f"Fetching data from {start_date} with interval '{interval}'.")

    # Ensure the graph folder exists and clear it if it does
    if os.path.exists(GRAPH_FOLDER):
        for filename in os.listdir(GRAPH_FOLDER):
            file_path = os.path.join(GRAPH_FOLDER, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove file or symbolic link
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove directory
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")
    else:
        os.makedirs(GRAPH_FOLDER)  # Create the folder if it doesn't exist

    # Step 1: Read the CSV and get symbols
    symbols = read_csv_and_get_symbols(CSV_FILE)
    if not symbols:
        return

    results = []

    # Step 2: Fetch data and calculate returns
    for symbol in symbols:
        print(f"Processing {symbol}...")
        data = fetch_stock_data(symbol, start_date, interval)
        if data is not None:
            stock_return = calculate_return(data)
            if stock_return is not None:
                results.append((symbol, stock_return, data))

    # Filter out invalid results
    results = [(symbol, stock_return, data) for symbol, stock_return, data in results if isinstance(stock_return, (int, float))]

    # Step 3: Sort by returns
    results.sort(key=lambda x: x[1], reverse=True)

    # Step 4: Save graphs and print results
    for rank, (symbol, stock_return, data) in enumerate(results, start=1):
        save_stock_graph(data, symbol, rank, stock_return)
        print(f"{rank}. {symbol}: {stock_return:.2f}% return")

    # Step 5: Open the graph folder
    try:
        print(f"Opening folder: {GRAPH_FOLDER}")
        if os.name == 'nt':  # Windows
            os.startfile(GRAPH_FOLDER)
        elif os.name == 'posix':  # macOS or Linux
            os.system(f'open "{GRAPH_FOLDER}"' if 'darwin' in os.uname().sysname.lower() else f'xdg-open "{GRAPH_FOLDER}"')
    except Exception as e:
        print(f"Error opening folder: {e}")

if __name__ == "__main__":
    main()
