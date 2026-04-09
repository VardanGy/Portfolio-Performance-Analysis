import pandas as pd
import webbrowser
from computations import (compute_indicators, set_graph)

def analysis_html(portefeuille: pd.DataFrame, market_data: pd.DataFrame, benchmark_ticker: str) -> webbrowser:
    """
    But: Affiche les indicateurs du portefeuille et de l'indice de manière organisé sur une page html
    :param portefeuille: Dataframe contenant la valeur boursière de chaque position, du portefeuille
                         et du portefeuille cumulé du cash disponible à chaque journée boursière
    :param market_data: Dataframe contenant les données boursières des valeurs et de l'indice
    :param benchmark_ticker: Ticker de l'indice de référence choisi pour comparer avec le portefeuille
    :return: fichier html ouvert sur un navigateur contenant 3 tableaux d'indicateurs
    """
    # Récupération des indicateurs et intégration dans un dictionnaire de dataframes
    indicateurs = compute_indicators(portefeuille, market_data, benchmark_ticker)
    tables = {}
    for k, v in indicateurs.items():
        table = pd.DataFrame.from_dict(v, orient="index")
        table.columns = ['Portefeuille', 'Indice']
        tables[k] = table

    # Insertion des dataframes dans un fichier html
    html_path = "Indicateurs.html"
    file = open(html_path, "w")

    try:
        file.write("<h1>Analyse de performance du portefeuille</h1>")

        for nom, table in tables.items():
            file.write(f"<h2> {nom}</h2>\n")
            file.write(table.to_html(index=True))
            file.write("<hr>\n")

    finally:
        file.close()

    return webbrowser.open_new_tab(html_path)

def view_graph(portefeuille, market_data, benchmark_ticker):
    """
    But: Affiche le graphique de comparaison entre la valeur du portefeuille et de l'indice
    :param portefeuille: //
    :param market_data: //
    :param benchmark_ticker: //
    :return: Graphique du rendement cumulé du portefeuille et de l'indice sur la période concernée par les transactions
    """
    graph_cumul_return = set_graph(portefeuille, market_data, benchmark_ticker)
    return graph_cumul_return.show()