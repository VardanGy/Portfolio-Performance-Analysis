# Import
import yfinance as yf
import pandas as pd
from datetime import date
import time

def get_raw_data(data_file_path: str, capital: float) -> pd.DataFrame:
    """
    But: Récupère un fichier csv et intègre les données dans un dataframe avec quelques modificitations
    :param data_file_path: Chemin qui mène au fichier contenant les transactions réalisées
    :param capital: Montant disponible au départ pour réaliser les opérations
    :return: DataFrame contenant les transactions réalisées
    """
    # Importation des données dans un DataFrame
    transactions = pd.read_csv(data_file_path, delimiter=',', parse_dates=True)

    # Transformation rapide des données
    transactions["Date"] = pd.to_datetime(transactions["Date"], format="%d/%m/%Y")

    for i in range(len(transactions)):
        if transactions.loc[i, 'Achat/Vente'] == "Achat":
            transactions.loc[i, 'Montant'] = transactions.loc[i, 'Prix'] * transactions.loc[i, 'Quantite']
        else:
            transactions.loc[i, 'Montant'] = -transactions.loc[i, 'Prix'] * transactions.loc[i, 'Quantite']

    transactions['Montants investis'] = transactions['Montant'].cumsum()

    # Test pour vérifier si le capital utilisé est suffisant
    for t in range(len(transactions)):
        if transactions.loc[t, 'Montants investis'] > capital:
            print("ATTENTION : VOUS N'AVEZ PAS UN CAPITAL SUFFISANT POUR REALISER CES OPERATIONS !!!")
            break

    return transactions


def get_market_data(transactions: pd.DataFrame, benchmark_ticker: str) -> pd.DataFrame:
    """
    But: Récupère depuis Yahoo Finance les données boursières des valeurs concernées par les transactions
          et de l'indice de référence choisi sur une période distincte pour chaque valeur (allant de la
          première transaction jusqu'à aujourd'hui (date de fin de détention si tout est vendu entre temps))
    :param transactions: Dataframe contenant les transactions réalisées
    :param benchmark_ticker: Ticker de l'indice de référence choisi pour comparer avec le portefeuille
    :return: Dataframe contenant les données boursières des valeurs et de l'indice
    """
    # Récupération de la date de premier achat de chaque valeur
    tickers = transactions['Ticker'].unique().tolist()
    tickers.append(benchmark_ticker)
    dates_debut = {}

    for ticker in tickers:
        count = 0
        for i in range(len(transactions)):
            if transactions.loc[i, 'Ticker'] == ticker and count == 0:
                dates_debut[ticker] = transactions.loc[i, 'Date']
                count = 1
    dates_debut[benchmark_ticker] = transactions.loc[0, 'Date']

    # Récupération des données boursières à partir de Yahoo Finance
    period = pd.date_range(start=transactions.loc[0, 'Date'], end=date.today(), freq='D')
    market_data = pd.DataFrame(index=period)

    for ticker in tickers:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                data_stock = yf.download(ticker, start=dates_debut[ticker], end=date.today(), multi_level_index=False)
                if data_stock.empty:
                    print(f"Avertissement : aucune donnée récupérée pour {ticker}")
                    break
                data_stock = data_stock[["Close"]]
                data_stock = data_stock.rename(columns={'Close': ticker})
                market_data = market_data.join(data_stock)
                market_data.dropna(how="all", inplace=True)
                market_data.fillna(0, inplace=True)
                break
            except Exception as e:
                print(f"Erreur pour {ticker} (tentative {attempt + 1}/{max_retries}) : {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                else:
                    print(f"Échec définitif pour {ticker} après {max_retries} tentatives.")
        time.sleep(2)
    return market_data


def set_data(transactions: pd.DataFrame, market_data: pd.DataFrame, capital: float) -> pd.DataFrame:
    """
    But: Relève les quantités détenues de chaque valeur à la fin de chaque journée boursière
         Cela permet d'obtenir la situation du portefeuille à la fin de chaque journée boursière
         Prend aussi en compte le capital non dépensé pour avoir une vision plus juste de l'évolution du portefeuille
    :param transactions: Dataframe contenant les transactions réalisées
    :param market_data: Dataframe contenant les données boursières des valeurs et de l'indice
    :param capital: Montant disponible au départ pour réaliser les opérations
    :return: Dataframe contenant la valeur boursière de chaque position, du portefeuille et du portefeuille
             cumulé du cash disponible à chaque journée boursière
    """
    # Récupération de la quantité de titres de chaque valeur détenue à chaque jounée
    tickers = market_data.columns.tolist()

    quantities = {}
    for ticker in tickers:
        quantities[ticker] = {}
        quantity = 0
        for i in range(len(transactions)):
            if transactions.loc[i, 'Ticker'] == ticker:
                if transactions.loc[i, 'Achat/Vente'] == 'Achat':
                    quantity += transactions.loc[i, 'Quantite']
                    quantities[ticker][transactions.loc[i, 'Date']] = quantity
                else:
                    quantity -= transactions.loc[i, 'Quantite']
                    quantities[ticker][transactions.loc[i, 'Date']] = quantity
        if quantities == 0:
            del quantities[ticker]

    # Calcul de la valeur boursière de chaque position à la fin de chaque journée
    portfolio = market_data.copy()
    for ticker, composition in quantities.items():
        for stock in list(market_data.columns):
            if ticker == stock:
                q = 0
                for index, row in market_data.iterrows():
                    for date, quant in composition.items():
                        if index == date:
                            q = quant
                    portfolio.loc[index, stock] = market_data.loc[index, stock] * q

    # Ajout de colonnes qui donnent un meilleur aperçu de la performance de l'investisseur sur la période
    portfolio['Valeur portefeuille'] = portfolio.sum(axis=1, skipna=True)

    cash = {}
    for i in range(len(transactions)):
        cash[transactions.loc[i, 'Date']] = capital - transactions.loc[i, 'Montants investis']

    for index, row in portfolio.iterrows():
        for date, montant in cash.items():
            if index == date:
                m = montant
        portfolio.loc[index, "Capital"] = portfolio.loc[index, "Valeur portefeuille"] + m

    return portfolio