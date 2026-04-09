import os
from repository import (get_raw_data, get_market_data, set_data)
from view import (analysis_html, view_graph)

# Fichiers disponibles : 'transactions.csv', 'transactions 2.csv"
# Capital recommandé : 50 000

# Path
data_file = 'Input Data 2.csv'
data_file_path = os.path.join(os.getcwd(), data_file)

capital = 50000
benchmark_ticker = '^GSPC'
# '^GSPC' = S&P 500

def main():
    # Get data
    transactions = get_raw_data(data_file_path, capital)
    market_data = get_market_data(transactions, benchmark_ticker)
    portefeuille = set_data(transactions, market_data, capital)

    # View
    analysis_html(portefeuille, market_data, benchmark_ticker)
    view_graph(portefeuille, market_data, benchmark_ticker)

if __name__ == '__main__':
    main()