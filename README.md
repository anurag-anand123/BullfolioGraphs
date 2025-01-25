# BullfolioGraphs
A Python-based project designed to identify momentum stocks and visualize their performance through dynamically generated graphs. All generated graphs are saved locally for easy access and review.

## Overview

This open-source Python project helps in finding momentum stocks and generates graphical representations of all identified momentum stocks as .png images.

## Requirements

Python (Ensure it is installed and added to the system path)

Visual Studio Code (VSCode) with Python extensions installed

## Installation

Clone or download this repository to your local machine.

Ensure that Python and VSCode with the necessary Python extensions are installed.

# Steps to Run the Project

## Step 1: Open Project Directory in VSCode

Open the directory where the project is located in Visual Studio Code.

## Step 2: Execute the Main Script

Run the script by executing the following command in the terminal:

python Momentum/main.py

## Step 3: Provide Required Inputs

The script will prompt for several inputs:

Stock List Input: Provide the list of stocks to analyze.

Momentum Period Selection: Choose whether you want to see momentum in a weekly or monthly basis. Options: weeks or months.

Momentum Duration: Specify the number of weeks or months to look for high momentum.

Candlestick Timeframe: Define how much time each candlestick should represent. Options include: 5m, 30m, 1d, wk, etc.

Note:

Shorter candlestick timeframes will not support longer periods in steps 2 and 3.

Possible valid combinations: 1week-1m, 12months-1d and similar combinations.

## Step 4: View Results

Once the script completes execution, it will generate graphical representations of momentum stocks.

Output Folder Structure

The graphs will be stored in a folder named based on the selected timeframe combination. For example, if you selected 12 months - 1d, the results will be stored in the directory as:

12months1d/

Inside this folder, the stock graphs will be sorted in descending order of their returns.

1.png → Highest return stock

2.png → Second highest return stock

and so on...

This sorting helps in focusing on top-performing stocks to identify trend continuation patterns, saving time compared to manually analyzing all available stocks.

## Notes

Ensure correct input values are provided as per the described format to avoid execution errors.

Keep your Python environment up-to-date to avoid compatibility issues.


# Happy Trading!

