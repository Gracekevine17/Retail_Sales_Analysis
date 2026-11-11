1. Présentation du projet

Dans ce projet, j’analyse les ventes d’un site de commerce en ligne à partir d’un vrai jeu de données. Je voulais comprendre comment les ventes évoluent, quels produits rapportent le plus, dans quels pays on vend le plus et comment se comportent les clients.

C’était pour moi l’occasion de suivre toutes les étapes d’une analyse de données : récupérer les données, les explorer, les nettoyer, les transformer, puis faire les analyses et les graphiques.

2. Ce que je voulais faire
Comprendre comment le jeu de données est organisé.
Repérer les valeurs manquantes et les anomalies.
Nettoyer les données pour avoir une base fiable.
Regarder l’évolution des ventes mois par mois.
Trouver les produits qui font le plus de chiffre d’affaires.
Comparer les pays.
Étudier les commandes et les meilleurs clients.
Repérer les commandes dont le montant sort de l’ordinaire.
Présenter tout ça avec des graphiques.
3. Le jeu de données

J’ai utilisé le jeu Online Retail de l’UCI Machine Learning Repository :
https://archive.ics.uci.edu/dataset/352/online+retail

Il contient les transactions d’un site de vente en ligne britannique entre décembre 2010 et décembre 2011.

3.1 En bref
541 909 lignes au départ
8 colonnes
Période : décembre 2010 à décembre 2011
Le Royaume-Uni est le pays principal
3.2 Les variables
Variable	Description
InvoiceNo	Numéro de facture
StockCode	Code du produit
Description	Nom du produit
Quantity	Quantité achetée ou retournée
InvoiceDate	Date et heure de la transaction
UnitPrice	Prix unitaire
CustomerID	Identifiant du client
Country	Pays du client
3.3 Valeurs manquantes
Variable	Valeurs manquantes
Description	1 454
CustomerID	135 080

Il manque l’identifiant client sur environ 24,93 % des lignes, ce qui est beaucoup. Je n’ai pas supprimé ces lignes pour l’analyse générale des ventes. En revanche, pour tout ce qui concerne les clients, j’ai gardé uniquement les lignes qui ont un identifiant.

4. Nettoyage des données

Avant d’analyser les ventes, j’ai cherché les lignes qui pouvaient fausser les résultats.

4.1 Les anomalies que j’ai trouvées
10 624 lignes avec une quantité négative
9 288 lignes dont le numéro de facture commence par la lettre C (ce sont des annulations)
2 517 lignes avec un prix unitaire nul ou négatif

Ces groupes se chevauchent : une même ligne peut être dans plusieurs catégories. Je ne peux donc pas additionner ces nombres pour savoir combien de lignes j’enlève.

4.2 Les annulations

J’ai essayé de rapprocher des lignes de vente avec les lignes d’annulation correspondantes. Pour cela, j’ai comparé :

l’identifiant du client
le code du produit
la quantité
le prix unitaire
le fait que la vente soit avant l’annulation

J’ai trouvé 2 910 lignes de vente qui pourraient correspondre à une annulation.

J’ai vérifié à la main deux exemples :

facture 581483 et annulation C581484
facture 541431 et annulation C541433

Dans les deux cas, tout correspond (quantité, produit, client, prix).

J’ai aussi regardé la facture 556444 et l’annulation C556448. Le client, le produit et la quantité sont les mêmes, mais le prix unitaire est différent. J’ai donc exclu cette ligne de vente séparément, comme cas particulier.

Limite : ma méthode repose seulement sur des critères de correspondance, donc je ne peux pas être sûre à 100 % que les 2 910 rapprochements sont tous de vraies annulations. Ce sont des rapprochements possibles, que je n’ai pas tous vérifiés un par un.

4.3 Le jeu de données nettoyé

J’ai gardé uniquement les lignes où :

la facture n’est pas une annulation
la quantité est strictement positive
le prix unitaire est strictement positif

J’ai ensuite créé une colonne TotalSales :

TotalSales = Quantity × UnitPrice

Après ce nettoyage :

il reste 527 193 lignes
les ventes positives conservées s’élèvent à 10 203 599,53 £

Ce montant n’est pas un bénéfice : on n’a pas les coûts de l’entreprise.

5. Évolution des ventes
5.1 Ventes par mois
Mois	Ventes (£)
Décembre 2010	801 236,44
Janvier 2011	586 122,01
Février 2011	519 719,73
Mars 2011	709 785,85
Avril 2011	524 468,18
Mai 2011	760 333,57
Juin 2011	710 125,54
Juillet 2011	712 217,82
Août 2011	749 975,72
Septembre 2011	1 047 802,05
Octobre 2011	1 118 436,14
Novembre 2011	1 493 640,62
Décembre 2011	469 735,86
5.2 Ce que j’observe

Le meilleur mois est novembre 2011, avec 1 493 640,62 £. Les ventes montent nettement entre août et novembre. Mon hypothèse est que les clients achètent avant Noël, d’autant que plusieurs produits du top 10 sont liés à cette période (par exemple PAPER CHAIN KIT 50’S CHRISTMAS). Je n’ai pas vérifié cette explication avec une analyse par produit et par mois, donc ça reste une piste.

En décembre 2011, les ventes retombent. Il faut faire attention : je pense que le mois n’est pas complet dans les données, donc on ne peut pas conclure à une vraie baisse.

6. Produits et pays
6.1 Les produits qui rapportent le plus

Voici le top 10 :

Produit	Ventes (£)
DOTCOM POSTAGE	206 248,77
REGENCY CAKESTAND 3 TIER	170 595,84
WHITE HANGING HEART T-LIGHT HOLDER	99 818,97
PARTY BUNTING	98 629,38
JUMBO BAG RED RETROSPOT	92 781,47
POSTAGE	77 415,93
RABBIT NIGHT LIGHT	66 902,59
PAPER CHAIN KIT 50’S CHRISTMAS	63 911,64
Manual	60 585,17
ASSORTED COLOUR BIRD ORNAMENT	58 991,84

Je me suis rendu compte que « DOTCOM POSTAGE », « POSTAGE » et « Manual » ne sont pas de vrais produits : ce sont des frais de port et des lignes saisies manuellement. Si on les retire, le produit n°1 est REGENCY CAKESTAND 3 TIER, avec 170 595,84 £.

6.2 Les pays
Pays	Ventes (£)
United Kingdom	8 600 805,06
Netherlands	285 036,54
EIRE	269 421,52
Germany	225 731,13
France	206 668,40
Australia	137 541,55
Spain	57 900,52
Switzerland	56 619,75
Belgium	41 082,69
Sweden	37 880,33

Le Royaume-Uni représente environ 84,29 % des ventes conservées. L’activité dépend donc beaucoup du marché britannique, même si d’autres pays achètent aussi.

7. Clients et commandes

Pour cette partie, j’ai enlevé les lignes sans CustomerID.

7.1 Les 10 meilleurs clients
Client	Ventes (£)	Commandes
14646	279 846,02	73
18102	259 657,30	60
17450	189 767,53	45
14911	137 267,81	198
12415	124 156,88	20
14156	114 685,83	55
17511	88 556,38	30
16029	66 336,60	59
16684	65 920,12	28
14096	65 164,79	17

On voit que le client 14911 passe beaucoup plus de commandes que les autres (198), mais dépense moins que les trois premiers. Son panier moyen est donc bien plus petit : environ 693 £ par commande, contre plus de 3 800 £ pour le client 14646. Je pense qu’il commande souvent de petites quantités, par exemple un commerçant qui se réapprovisionne régulièrement. C’est une hypothèse, je n’ai pas de donnée pour la confirmer.

7.2 Montants des commandes
Nombre de commandes : 18 397
Montant moyen : 460,38 £
Médiane : 302,10 £
Minimum : 0,38 £
Maximum : 27 872,80 £
Premier quartile : 157,53 £
Troisième quartile : 467,30 £

La moyenne est plus haute que la médiane, donc quelques grosses commandes tirent la moyenne vers le haut.

7.3 Les commandes extrêmes

Pour repérer les commandes atypiques, j’ai utilisé la méthode de l’écart interquartile (IQR). La limite haute est de 931,96 £.

1 451 commandes dépassent cette limite
soit 7,89 % des commandes

La plus grosse est la facture 567423 : 27 872,80 £.

Je ne les ai pas supprimées, car une grosse commande n’est pas forcément une erreur. Ça peut être un achat en gros ou un client professionnel.

8. Limites
Beaucoup de CustomerID manquants : je ne peux pas faire d’analyse client sur toutes les lignes.
Annulations : mon rapprochement n’est pas totalement sûr, certains cas demanderaient plus de vérification.
Pas de coûts : je ne peux pas calculer le vrai bénéfice.
Une seule année : on ne peut pas en déduire une saisonnalité fiable.
Valeurs extrêmes : je les ai gardées, mais leur interprétation dépend du contexte.
Chiffre d’affaires : ce sont des ventes positives après nettoyage, pas un chiffre d’affaires comptable officiel.
9. Conclusion

Ce projet m’a permis de travailler sur un vrai jeu de données, avec ses défauts : valeurs manquantes, quantités négatives, annulations et valeurs extrêmes. J’ai dû faire des choix de nettoyage avant de pouvoir analyser quoi que ce soit.

Les principaux résultats sont une très forte part du Royaume-Uni dans les ventes (84,29 %), un pic en novembre 2011, et des grosses commandes qui font monter la moyenne au-dessus de la médiane.

J’ai utilisé Python, Pandas, NumPy et Matplotlib. La partie la plus délicate a été le traitement des annulations : il a fallu choisir des critères de rapprochement (client, produit, quantité, prix, date) et accepter qu’on ne puisse pas tout vérifier avec certitude. J’ai aussi compris qu’il faut regarder le contenu des données avant d’analyser, par exemple pour repérer que POSTAGE et Manual ne sont pas de vrais produits.

Pour aller plus loin, j’aimerais faire des analyses statistiques plus poussées et essayer de la modélisation.

Outils : Python 3.12, Pandas, NumPy, Matplotlib, OpenPyXL
Source : UCI Machine Learning Repository – Online Retail