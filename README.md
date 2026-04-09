Programme Python qui analyse la performance d'un portefeuille d'actions en le comparant à un indice de référence.
À partir d'un fichier de transactions, elle reconstitue l'évolution journalière du portefeuille, calcule des indicateurs financiers et génère des visualisations.


Structure du projet :
- main.py              # Point d'entrée — orchestre l'exécution
- repository.py        # Chargement des données (CSV + Yahoo Finance)
- computations.py      # Calcul des indicateurs financiers
- view.py              # Génération du rapport HTML et du graphique

- Input_Data.csv       # Exemple de fichier de transactions
- Input_Data_2.csv     # Exemple de fichier de transactions


Format du fichier d'input :
Le fichier d'entrée doit être un .csv avec les colonnes suivantes, séparées par des virgules :
- Date -> string -> Date de la transaction (JJ/MM/AAAA)
- Valeur -> string -> Nom complet de l'entreprise
- Ticker -> string -> Symbole boursier Yahoo Finance
- Achat/Vente -> string -> Type d'opération
- Prix -> float -> Prix unitaire au moment de l'ordre
- Quantite -> int -> Nombre de titres échangés


Paramètres à ajuster en fonction des préférences dans main.py :
pythondata_file = 'Input_Data.csv'   # Nom de votre fichier de transactions
capital = 50000                 # Capital de départ disponible (en €/$)
benchmark_ticker = '^GSPC'      # Indice de référence ('^GSPC' = S&P 500)
