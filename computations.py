# Import
import pandas as pd
from datetime import date
import matplotlib.pyplot as plt
import numpy as np

def compute_indicators(portefeuille: pd.DataFrame, market_data: pd.DataFrame, benchmark_ticker: str) -> dict:
    """
    But: Calcule les indicateurs de rendement, de risque et les ratios de performance du portefeuille et de
         l'indice et met toutes les infos dans un dictionnaire
    :param portefeuille: Dataframe contenant la valeur boursière de chaque position, du portefeuille
                         et du portefeuille cumulé du cash disponible à chaque journée boursière
    :param market_data: Dataframe contenant les données boursières des valeurs et de l'indice
    :param benchmark_ticker: Ticker de l'indice de référence choisi pour comparer avec le portefeuille
    :return: Dictionnaire imbriqué qui contient tous les indicateurs du potefeuille et de l'indice, rangé
             par type d'indicateurs dans des dictionnaires imbriqués
    """
    indicators = {}

    # Indicateurs de rendement
    rendements = {}

    # Calcul du rendement
    portefeuille['Rendement portefeuille'] = portefeuille["Capital"].pct_change()
    portefeuille['Rendement indice'] = market_data[benchmark_ticker].pct_change()
    daily_returns_port = portefeuille['Rendement portefeuille']
    daily_returns_bmk = portefeuille['Rendement indice']

    # Calcul du rendement journalier moyen
    mean_daily_return_port = daily_returns_port.mean()
    mean_daily_return_bmk = daily_returns_bmk.mean()
    rendements['Rendement journalier moyen'] = [f"{round(mean_daily_return_port*100, 2)}%", f"{round(mean_daily_return_bmk*100, 2)}%"]

    # Calcul du rendement cumulé
    daily_cum_return_port = (1 + daily_returns_port).cumprod()
    daily_cum_return_bmk = (1 + daily_returns_bmk).cumprod()

    # Calcul du rendement total
    total_return_port = (portefeuille['Capital'][-1] - portefeuille['Capital'][0]) / portefeuille['Capital'][0]
    total_return_bmk = (market_data[benchmark_ticker][-1] - market_data[benchmark_ticker][0])/market_data[benchmark_ticker][0]
    rendements['Rendement total'] = [f"{round(total_return_port*100, 2)}%", f"{round(total_return_bmk*100, 2)}%"]

    # Calcul du rendement annualisé
    months = (date.today().year - portefeuille.index[0].year) * 12 + (date.today().month - portefeuille.index[0].month)
    annualized_return_port = ((1 + total_return_port)**(12/months)) - 1
    annualized_return_bmk = ((1 + total_return_bmk)**(12/months)) - 1
    rendements['Rendement annualisé'] = [f"{round(annualized_return_port*100, 2)}%", f"{round(annualized_return_bmk*100, 2)}%"]

    indicators['Indicateurs de rendement'] = rendements


    # Indicateurs de risque
    risques = {}

    # Calcul de la volatilté journalière
    daily_volatility_port = daily_returns_port.std()
    daily_volatility_bmk = daily_returns_bmk.std()
    risques['Volatilité journalière'] = [f"{round(daily_volatility_port*100, 2)}%", f"{round(daily_volatility_bmk*100, 2)}%"]

    # Calcul de la volatilité annualisée
    annualized_volatility_port = daily_volatility_port * np.sqrt(252)
    annualized_volatility_bmk = daily_volatility_bmk * np.sqrt(252)
    risques['Volatilité annualisée'] = [f"{round(annualized_volatility_port*100, 2)}%", f"{round(annualized_volatility_bmk*100, 2)}%"]

    # Calcul du skewness
    skewness_port = daily_returns_port.skew()
    skewness_bmk = daily_returns_bmk.skew()
    risques['Skewness'] = [round(skewness_port, 2), round(skewness_bmk, 2)]

    # Calcul du kurtosis
    kurtosis_port = daily_returns_port.kurtosis()
    kurtosis_bmk = daily_returns_bmk.kurtosis()
    risques['Kurtosis'] = [round(kurtosis_port, 2), round(kurtosis_bmk, 2)]

    # Calcul du maximum drawdown
    daily_cum_return_port.dropna(inplace=True)
    running_max_port = np.maximum.accumulate(daily_cum_return_port)
    running_max_port[running_max_port < 1] = 1
    drawdown_port = (daily_cum_return_port / running_max_port - 1)
    max_drawdown_port = drawdown_port.min()

    daily_cum_return_bmk.dropna(inplace=True)
    running_max_bmk = np.maximum.accumulate(daily_cum_return_bmk)
    running_max_bmk[running_max_bmk < 1] = 1
    drawdown_bmk = (daily_cum_return_bmk / running_max_bmk - 1)
    max_drawdown_bmk = drawdown_bmk.min()

    risques['Maximum drawdown'] = [f"{round(max_drawdown_port*100, 2)}%", f"{round(max_drawdown_bmk*100, 2)}%"]

    # Calcul de la Value at Risk
    var_level = 95
    daily_returns_port.fillna(0, inplace=True)
    daily_returns_bmk.fillna(0, inplace=True)
    var_port = np.percentile(daily_returns_port, 100 - var_level)
    var_bmk = np.percentile(daily_returns_bmk, 100 - var_level)
    risques[f'Value at Risk ({var_level}%)'] = [f"{round(var_port*100, 2)}%", f"{round(var_bmk*100, 2)}%"]

    # Calcul de la Conditional Value at Risk
    cvar_port = daily_returns_port[daily_returns_port <= var_port].mean()
    cvar_bmk = daily_returns_bmk[daily_returns_bmk <= var_bmk].mean()
    risques[f'Conditional Value at Risk ({var_level}%)'] = [f"{round(cvar_port*100, 2)}%", f"{round(cvar_bmk*100, 2)}%"]

    indicators['Indicateurs de risque'] = risques


    # Ratios de performance
    ratios = {}

    # Calcul du ratio de Sharpe
    t_bonds_rate = 0.046
    sharpe_ratio_port = (annualized_return_port - t_bonds_rate) / annualized_volatility_port
    sharpe_ratio_bmk = (annualized_return_bmk - t_bonds_rate) / annualized_volatility_bmk
    ratios['Ratio de Sharpe'] = [round(sharpe_ratio_port, 2), round(sharpe_ratio_bmk, 2)]

    # Calcul du beta
    cov_matrix = portefeuille[["Rendement portefeuille", "Rendement indice"]].cov()
    beta_port = cov_matrix.iloc[0,1] / cov_matrix.iloc[1,1]
    ratios['Beta'] = [round(beta_port, 2), 1]

    # Calcul du ratio de Sortino
    negative_returns_port = daily_returns_port[daily_returns_port < 0]
    down_std_port = negative_returns_port.std() * np.sqrt(252)
    sortino_ratio_port = (annualized_return_port - t_bonds_rate)/down_std_port

    negative_returns_bmk = daily_returns_bmk[daily_returns_bmk < 0]
    down_std_bmk = negative_returns_bmk.std() * np.sqrt(252)
    sortino_ratio_bmk = (annualized_return_bmk - t_bonds_rate)/down_std_bmk

    ratios['Ratio de Sortino'] = [round(sortino_ratio_port, 2), round(sortino_ratio_bmk, 2)]

    # Calcul du ratio de Calmar
    calmar_ratio_port = annualized_return_port / -max_drawdown_port
    calmar_ratio_bmk = annualized_return_bmk / -max_drawdown_bmk
    ratios['Ratio de Calmar'] = [round(calmar_ratio_port, 2), round(calmar_ratio_bmk, 2)]

    indicators['Ratios de performance'] = ratios

    return indicators


def set_graph(portefeuille: pd.DataFrame, market_data: pd.DataFrame, benchmark_ticker: str) -> plt:
    """
    But: Crée un graphique qui montre l'évolution de la valeur du portefeuille et de l'indice sur la période
         concernée par les opérations pour comparer la performance
    :param portefeuille: Dataframe contenant la valeur boursière de chaque position, du portefeuille
                         et du portefeuille cumulé du cash disponible à chaque journée boursière
    :param market_data: Dataframe contenant les données boursières des valeurs et de l'indice
    :param benchmark_ticker: Ticker de l'indice de référence choisi pour comparer avec le portefeuille
    :return: Graphique du rendement cumulé du portefeuille et de l'indice sur la période concernée par les transactions
    """
    norm_port = portefeuille["Capital"] / portefeuille["Capital"][0]
    norm_bmk = market_data[benchmark_ticker] / market_data[benchmark_ticker][0]
    norm = pd.DataFrame({'Portefeuille': norm_port, 'Indice': norm_bmk})

    norm.plot(figsize=(10, 4.5))
    plt.title("Portefeuille vs Indice")
    plt.xlabel("Date")
    plt.ylabel("Rendement cumulé")
    plt.tight_layout()

    return plt