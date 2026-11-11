# =====================================================
# PROJET : RETAIL SALES ANALYSIS
# Auteur : Grâce
# Source : UCI Machine Learning Repository
# Objectif : Analyse exploratoire des ventes en ligne
# =====================================================


# 1. IMPORTATION DES BIBLIOTHÈQUES

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from pathlib import Path

# Utiliser le dossier du script comme dossier de référence
BASE_DIR = Path(__file__).resolve().parent
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"
FIGURES_DIR = BASE_DIR / "figures"

# Créer les dossiers de sortie s'ils n'existent pas encore
DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# 2. VÉRIFICATION DES BIBLIOTHÈQUES

print("===================================")
print("     RETAIL SALES ANALYSIS")
print("===================================")

print("Pandas :", pd.__version__)
print("NumPy :", np.__version__)

print("Les bibliothèques sont prêtes !")

# 3. CHARGEMENT DU JEU DE DONNÉES

file_path = DATA_RAW_DIR / "Online Retail.xlsx"

if not file_path.exists():
    raise FileNotFoundError(
        f"Fichier introuvable : {file_path}. "
        "Placez Online Retail.xlsx dans data/raw/."
    )

df = pd.read_excel(file_path)

print("\nFichier chargé avec succès !")

# 4. PREMIÈRE EXPLORATION

print("\nDimensions du jeu de données :")
print(df.shape)

print("\nAperçu des données :")
print(df.head())

# 5. INFORMATIONS GENERALES SUR LES DONNEES

print("\n===== INFORMATIONS GENERALES =====")

df.info()
# 6. VERIFICATION DES VALEURS MANQUANTES

print("\n===== VALEURS MANQUANTES =====")

print(df.isnull().sum())


# 7. STATISTIQUES DESCRIPTIVES

print("\n===== STATISTIQUES DESCRIPTIVES =====")

print(df.describe())
# ==========================================
# 8. ANALYSE DES TRANSACTIONS PARTICULIERES
# ==========================================

# Identifier les quantités négatives
negative_quantity = df[df["Quantity"] < 0]

print("\n===== QUANTITES NEGATIVES =====")
print("Nombre de lignes avec quantité négative :",
      len(negative_quantity))


# Identifier les factures annulées
cancelled_invoices = df[
    df["InvoiceNo"].astype(str).str.startswith("C")
]

print("\n===== FACTURES ANNULEES =====")
print("Nombre de lignes associées aux annulations :",
      len(cancelled_invoices))


# Identifier les prix nuls ou négatifs
invalid_prices = df[df["UnitPrice"] <= 0]

print("\n===== PRIX NULS OU NEGATIFS =====")
print("Nombre de lignes concernées :", len(invalid_prices))


# Afficher quelques exemples de transactions négatives
print("\n===== EXEMPLES DE TRANSACTIONS NEGATIVES =====")
print(negative_quantity.head())
# ==========================================

# ==========================================


# ==========================================
# 9. PREPARATION ET CORRECTION DES ANNULATIONS
# ==========================================

# 1. Identifier les ventes initiales
ventes_initiales = df[
    (~df["InvoiceNo"].astype(str).str.startswith("C")) &
    (df["Quantity"] > 0) &
    (df["UnitPrice"] > 0)
].copy()


# 2. Identifier les lignes d'annulation
annulations = df[
    (df["InvoiceNo"].astype(str).str.startswith("C")) &
    (df["Quantity"] < 0)
].copy()


# 3. Construire une clé de rapprochement
def creer_cle(client_id, stock_code, quantity, unit_price):

    # Ne pas rapprocher automatiquement les transactions
    # lorsque l'identifiant du client est manquant.
    if pd.isna(client_id):
        return None

    return (
        str(client_id),
        str(stock_code),
        round(abs(float(quantity)), 6),
        round(float(unit_price), 4)
    )


# 4. Regrouper les ventes par clé
# itertuples() est plus rapide que iterrows()
# pour parcourir un grand tableau.

ventes_par_cle = defaultdict(list)

for ligne in ventes_initiales.itertuples():

    cle = creer_cle(
        ligne.CustomerID,
        ligne.StockCode,
        ligne.Quantity,
        ligne.UnitPrice
    )

    if cle is not None:
        ventes_par_cle[cle].append(
            (ligne.InvoiceDate, ligne.Index)
        )


# Trier les ventes par date
for cle in ventes_par_cle:
    ventes_par_cle[cle].sort(key=lambda x: x[0])


# 5. Rapprocher les annulations avec les ventes antérieures

indices_ventes_annulees = set()
correspondances = []

annulations = annulations.sort_values("InvoiceDate")

for ligne_annulation in annulations.itertuples():

    index_annulation = ligne_annulation.Index

    cle = creer_cle(
        ligne_annulation.CustomerID,
        ligne_annulation.StockCode,
        ligne_annulation.Quantity,
        ligne_annulation.UnitPrice
    )

    # Ignorer les annulations sans identifiant client
    if cle is None:
        continue

    candidates = ventes_par_cle.get(cle, [])

    for date_vente, index_vente in reversed(candidates):

        if (
            date_vente < ligne_annulation.InvoiceDate
            and index_vente not in indices_ventes_annulees
        ):

            indices_ventes_annulees.add(index_vente)

            ligne_vente = df.loc[index_vente]

            correspondances.append({
                "Facture_origine": ligne_vente["InvoiceNo"],
                "Facture_annulation": ligne_annulation.InvoiceNo,
                "Client": ligne_vente["CustomerID"],
                "Produit": ligne_vente["Description"],
                "Quantite": ligne_vente["Quantity"],
                "Montant": ligne_vente["Quantity"] * ligne_vente["UnitPrice"],
                "Date_vente": ligne_vente["InvoiceDate"],
                "Date_annulation": ligne_annulation.InvoiceDate
            })

            break


# 6. Créer le tableau des correspondances

correspondances_df = pd.DataFrame(correspondances)

print("\n===== RAPPROCHEMENT DES ANNULATIONS =====")
print("Lignes d'annulation :", len(annulations))
print("Ventes initiales rapprochées :", len(indices_ventes_annulees))

print("\nExemples de correspondances :")
print(correspondances_df.head(10))


# 7. Retirer les ventes initiales rapprochées

sales_df = df.drop(
    index=list(indices_ventes_annulees)
).copy()


# 8. Conserver uniquement les ventes positives valides

sales_df = sales_df[
    (~sales_df["InvoiceNo"].astype(str).str.startswith("C")) &
    (sales_df["Quantity"] > 0) &
    (sales_df["UnitPrice"] > 0)
].copy()


# 9. Traiter un cas particulier identifié
# La facture 556444 est associée à C556448.
# Client, produit et quantité identiques.
# Le prix unitaire diffère : 649.50 £ contre 4.95 £.
# Cette vente est exclue de l'analyse, avec cette réserve documentée.

facture_suspecte = "556444"

nombre_avant_exclusion = len(sales_df)

sales_df = sales_df[
    sales_df["InvoiceNo"].astype(str) != facture_suspecte
].copy()

nombre_exclu = nombre_avant_exclusion - len(sales_df)

print("\n===== TRAITEMENT DU CAS PARTICULIER =====")
print("Facture examinée :", facture_suspecte)
print("Facture d'annulation associée : C556448")
print("Nombre de lignes supplémentaires exclues :", nombre_exclu)
print("Motif : correspondance client, produit et quantité,")
print("mais différence de prix unitaire entre vente et annulation.")


# 10. Calculer le montant de chaque vente

sales_df["TotalSales"] = (
    sales_df["Quantity"] * sales_df["UnitPrice"]
)

print("\n===== DONNEES APRES NETTOYAGE =====")
print("Nombre de lignes conservées :", len(sales_df))

print(
    "Montant total des ventes conservées :",
    round(sales_df["TotalSales"].sum(), 2),
    "£"
)

# ==========================================
# 10. ANALYSE DU CHIFFRE D'AFFAIRES MENSUEL
# ==========================================

# Extraire le mois et l'année
sales_df["Month"] = sales_df["InvoiceDate"].dt.to_period("M")

# Calculer le chiffre d'affaires par mois
monthly_sales = sales_df.groupby("Month")["TotalSales"].sum()

print("\n===== CHIFFRE D'AFFAIRES PAR MOIS =====")
print(monthly_sales.round(2))

# Identifier le meilleur mois
best_month = monthly_sales.idxmax()
best_revenue = monthly_sales.max()

print("\nMeilleur mois :", best_month)
print("Chiffre d'affaires :", round(best_revenue, 2))

# Créer un graphique
plt.figure(figsize=(12, 6))

monthly_sales.plot(kind="bar")

plt.title("Chiffre d'affaires mensuel")
plt.xlabel("Mois")
plt.ylabel("Chiffre d'affaires (£)")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(FIGURES_DIR / "monthly_sales.png")
plt.show()
# ==========================================
# 11. ANALYSE DES PRODUITS LES PLUS RENTABLES
# ==========================================

# Regrouper les ventes par produit
top_products = (
    sales_df.groupby("Description")["TotalSales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n===== TOP 10 DES PRODUITS PAR CHIFFRE D'AFFAIRES =====")
print(top_products.round(2))

# Créer un graphique
plt.figure(figsize=(12, 7))

top_products.sort_values().plot(kind="barh")

plt.title("Top 10 des produits par chiffre d'affaires")
plt.xlabel("Chiffre d'affaires (£)")
plt.ylabel("Produits")
plt.tight_layout()

plt.savefig(FIGURES_DIR / "top_10_products.png")
plt.show()
# ==========================================
# 12. TOP 10 DES PRODUITS PHYSIQUES
# ==========================================

# Exclure les frais d'expédition et les descriptions particulières
excluded_products = [
    "DOTCOM POSTAGE",
    "POSTAGE",
    "Manual"
]

physical_products = sales_df[
    ~sales_df["Description"].isin(excluded_products)
].copy()

# Calculer le chiffre d'affaires par produit
top_physical_products = (
    physical_products.groupby("Description")["TotalSales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\n===== TOP 10 DES PRODUITS PHYSIQUES =====")
print(top_physical_products.round(2))

# Graphique
plt.figure(figsize=(12, 7))

top_physical_products.sort_values().plot(kind="barh")

plt.title("Top 10 des produits physiques par chiffre d'affaires")
plt.xlabel("Chiffre d'affaires (£)")
plt.ylabel("Produits")

plt.tight_layout()
plt.savefig(FIGURES_DIR / "top_10_physical_products.png")
plt.show()
# ==========================================
# 13. ANALYSE DES VENTES PAR PAYS
# ==========================================

country_sales = (
    sales_df.groupby("Country")["TotalSales"]
    .sum()
    .sort_values(ascending=False)
)

print("\n===== TOP 10 DES PAYS PAR CHIFFRE D'AFFAIRES =====")
print(country_sales.head(10).round(2))

# Graphique
plt.figure(figsize=(12, 7))

country_sales.head(10).sort_values().plot(kind="barh")

plt.title("Top 10 des pays par chiffre d'affaires")
plt.xlabel("Chiffre d'affaires (£)")
plt.ylabel("Pays")

plt.tight_layout()
plt.savefig(FIGURES_DIR / "top_10_countries.png")
plt.show()
# ==========================================
# 14. ANALYSE DU COMPORTEMENT DES CLIENTS
# ==========================================

# Garder uniquement les lignes avec un identifiant client
customer_df = sales_df.dropna(subset=["CustomerID"]).copy()

# Calculer les indicateurs par client
customer_analysis = customer_df.groupby("CustomerID").agg(
    TotalRevenue=("TotalSales", "sum"),
    TotalOrders=("InvoiceNo", "nunique"),
    TotalQuantity=("Quantity", "sum")
)

# Classer les clients par chiffre d'affaires
top_customers = customer_analysis.sort_values(
    by="TotalRevenue",
    ascending=False
).head(10)

print("\n===== TOP 10 DES CLIENTS =====")
print(top_customers.round(2))

# Calculer le montant moyen d'une commande
order_totals = customer_df.groupby("InvoiceNo")["TotalSales"].sum()

average_order_value = order_totals.mean()

print("\n===== INDICATEUR DES COMMANDES =====")
print("Nombre de commandes :", len(order_totals))
print("Montant moyen d'une commande :",
      round(average_order_value, 2), "£")

# Graphique des 10 meilleurs clients
plt.figure(figsize=(12, 7))

top_customers["TotalRevenue"].sort_values().plot(kind="barh")

plt.title("Top 10 des clients par chiffre d'affaires")
plt.xlabel("Chiffre d'affaires (£)")
plt.ylabel("Identifiant client")

plt.tight_layout()
plt.savefig(FIGURES_DIR / "top_10_customers.png")
plt.show()
# ==========================================
# 15. ANALYSE DU MONTANT DES COMMANDES
# ==========================================

# Calculer la moyenne et la médiane
average_order = order_totals.mean()
median_order = order_totals.median()

print("\n===== MOYENNE ET MEDIANE DES COMMANDES =====")

print("Montant moyen :", round(average_order, 2), "£")
print("Montant médian :", round(median_order, 2), "£")

# Distribution des montants des commandes
plt.figure(figsize=(10, 6))

plt.hist(order_totals, bins=50)

plt.title("Distribution du montant des commandes")
plt.xlabel("Montant de la commande (£)")
plt.ylabel("Nombre de commandes")

plt.tight_layout()
plt.savefig(FIGURES_DIR / "order_distribution.png")
plt.show()
# ==========================================
# 16. STATISTIQUES DETAILLEES DES COMMANDES
# ==========================================

print("\n===== STATISTIQUES DETAILLEES DES COMMANDES =====")

print("Commande minimale :", round(order_totals.min(), 2), "£")
print("Commande maximale :", round(order_totals.max(), 2), "£")

print("Premier quartile :", round(order_totals.quantile(0.25), 2), "£")
print("Troisième quartile :", round(order_totals.quantile(0.75), 2), "£")

print("Ecart-type :", round(order_totals.std(), 2), "£")
# ==========================================
# 17. DETECTION DES COMMANDES EXTREMES
# ==========================================

Q1 = order_totals.quantile(0.25)
Q3 = order_totals.quantile(0.75)

IQR = Q3 - Q1

limite_superieure = Q3 + 1.5 * IQR

commandes_extremes = order_totals[
    order_totals > limite_superieure
]

print("\n===== DETECTION DES COMMANDES EXTREMES =====")

print("Limite supérieure :", round(limite_superieure, 2), "£")

print("Nombre de commandes extrêmes :",
      len(commandes_extremes))

print("Pourcentage de commandes extrêmes :",
      round(len(commandes_extremes) / len(order_totals) * 100, 2), "%")

print("\nLes 10 commandes les plus élevées :")

print(order_totals.sort_values(ascending=False).head(10))
# 18. VERIFICATION DANS LES DONNEES BRUTES
# ==========================================

factures_a_verifier = ["581483", "541431", "556444"]

print("\n===== VERIFICATION DES FACTURES DANS LES DONNEES BRUTES =====")

for facture in factures_a_verifier:

    details_bruts = df[
        df["InvoiceNo"].astype(str) == facture
    ]

    print("\nFacture :", facture)

    print(
        details_bruts[
            [
                "InvoiceNo",
                "StockCode",
                "Description",
                "Quantity",
                "UnitPrice",
                "InvoiceDate",
                "CustomerID",
                "Country"
            ]
        ]
    )
    # ==========================================
# ==========================================
# 19. COMPARAISON DES PRODUITS
# ==========================================

codes_produits = ["23843", "23166", "22502"]

print("\n===== COMPARAISON DES PRODUITS =====")

for code in codes_produits:

    produit = df[
        df["StockCode"].astype(str) == code
    ]

    print("\nCode produit :", code)

    print("Nombre de transactions :", len(produit))

    print(
        "Description :",
        produit["Description"].dropna().iloc[0]
        if not produit["Description"].dropna().empty
        else "Inconnue"
    )

    print("Quantité médiane :", produit["Quantity"].median())

    print("Quantité maximale :", produit["Quantity"].max())

    print("Prix unitaire médian :", produit["UnitPrice"].median())

    print("Prix unitaire maximal :", produit["UnitPrice"].max())


# ==========================================
# 20. ANALYSE DETAILLEE DES TRANSACTIONS ATYPIQUES
# ==========================================

# Ces factures ont été retirées de sales_df pendant le nettoyage.
# On les examine donc dans les données brutes (df).
# Pour comparer leurs produits, on utilise les ventes positives initiales.

factures_atypiques = ["581483", "541431", "556444"]

print("\n===== ANALYSE DETAILLEE DES TRANSACTIONS ATYPIQUES =====")

for facture in factures_atypiques:

    transaction = df[
        df["InvoiceNo"].astype(str) == facture
    ]

    if transaction.empty:
        print(f"Facture {facture} introuvable dans les données brutes.")
        continue

    ligne_vente = transaction[
        (transaction["Quantity"] > 0) &
        (transaction["UnitPrice"] > 0)
    ]

    if ligne_vente.empty:
        print(f"Aucune ligne de vente positive pour la facture {facture}.")
        continue

    ligne = ligne_vente.iloc[0]
    code = str(ligne["StockCode"])

    produit = ventes_initiales[
        ventes_initiales["StockCode"].astype(str) == code
    ]

    print("\nFacture :", facture)
    print("Produit :", ligne["Description"])
    print("Quantité de la transaction :", ligne_vente["Quantity"].sum())
    print("Quantité médiane du produit :", produit["Quantity"].median())
    print("Prix unitaire de la transaction :", ligne["UnitPrice"])
    print("Prix unitaire médian du produit :", produit["UnitPrice"].median())
    print("Nombre de ventes initiales du produit :", len(produit))


# ==========================================
# 21. EXPORTATION DES DONNEES NETTOYEES
# ==========================================

print("\n===== EXPORTATION DES DONNEES =====")

sales_df.to_csv(
    DATA_PROCESSED_DIR / "retail_cleaned.csv",
    index=False
)

print("Les données nettoyées ont été enregistrées avec succès !")
