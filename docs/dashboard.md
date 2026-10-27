# Dashboard Geldalyse — conception et suivi

Ce document décrit le contenu du tableau de bord et suit l'avancement de sa construction.

## Objectif

Permettre à l'utilisateur de répondre en un coup d'œil à trois questions :

1. Est-ce que je dépense plus que je ne gagne ?
2. Où part mon argent ?
3. Comment mes finances évoluent-elles dans le temps ?

## Sources de données

Le dashboard fonctionne avec **les deux sources**, au choix de l'utilisateur :

| Source | Fonctionnement | Module utilisé |
|---|---|---|
| Données de démo | Transactions fictives générées à la volée | `generator.py` |
| Relevé importé | Export ING en français, importé par l'utilisateur | `reader.py` |

Les deux sources produisent le **format standard** (`schema.py`). Tout ce qui suit le choix de la source est donc identique, quelle que soit l'origine des données.

## Mise en page

Principe : **du plus général au plus détaillé**, de haut en bas.

| # | Élément | Forme | Question à laquelle il répond |
|---|---|---|---|
| 1 | Source des données et filtre de période | Barre latérale | Quelles données, sur quelle période ? |
| 2 | Revenus, dépenses, solde | Trois chiffres clés (`st.metric`) | Est-ce que je dépense plus que je ne gagne ? |
| 3 | Dépenses par catégorie | Barres horizontales, triées de la plus grande à la plus petite | Où part mon argent ? |
| 4 | Revenus et dépenses par mois | Barres groupées (une barre revenus, une barre dépenses par mois) | Comment ça évolue ? |
| 5 | Transactions | Tableau | Quelles opérations se cachent derrière les chiffres ? |
| 6 | Transactions, avec filtre par catégorie | Tableau, les plus récentes en premier ; libellé court en 2e colonne, description complète en dernière | Quelles opérations se cachent derrière les chiffres ? |

## Règles de conception

- **Aucune catégorie écrite en dur** dans le dashboard : les catégories affichées sont celles présentes dans les données. Une nouvelle catégorie apparaît automatiquement.
- **Dépenses affichées en valeurs positives** dans les graphiques, pour une lecture naturelle.
- **Les revenus sont exclus** du graphique des dépenses par catégorie.
- **Les retraits d'espèces** apparaissent comme une catégorie à part entière, RETRAITS : le total du graphique des dépenses reste ainsi égal au chiffre clé « Dépenses ».
- **Le filtre de période** s'applique à tout le dashboard ; **le filtre par catégorie** ne s'applique qu'au tableau des transactions.
- **Pas d'information portée uniquement par la couleur** : chaque série est nommée dans une légende.
- **Le libellé court** est affiché en priorité ; **la description complète** reste disponible en dernière colonne, pour ne rien cacher.
- **Deux vues de l'argent** :
  - les **chiffres clés** et le **graphique mensuel** suivent le compte bancaire : une entrée est un montant positif, une sortie un montant négatif. Leurs totaux sont vérifiables sur le relevé ;
  - les **onglets par catégorie** montrent ce que l'argent représente : un remboursement de magasin est déduit de sa catégorie de dépense, et n'apparaît pas dans les entrées.
- **Cohérence entre les deux vues** : total des entrées par catégorie − total des sorties par catégorie = Solde.

## Suivi de construction

- [X] Squelette de l'application (`app.py`) qui se lance avec `streamlit run app.py`
- [X] Barre latérale : choix de la source (démo ou relevé importé)
- [X] Chargement des données et ajout de la colonne `category`
- [X] Filtre de période
- [X] Trois chiffres clés
- [X] Dépenses par catégorie
- [X] Revenus et dépenses par mois
- [X] Tableau des transactions
- [X] Gestion des erreurs d'import (fichier au mauvais format, fichier vide, relevé sans transaction)
- [X] Filtre du tableau par catégorie
- [X] Indicateur des transactions non catégorisées

## Prévu pour la V2
- [ ] Indicateurs clés du mois, avec comparaison au mois précédent (`st.metric` avec `delta`)
- [X] Correction manuelle de la catégorie d'une opération non catégorisée (`st.data_editor`)
-  Correction manuelle de la catégorie d'une transaction (`st.data_editor`)
- [ ] Paiements récurrents, sous forme de tableau (nécessite un algorithme de détection : même libellé, montant proche, chaque mois)
- [ ] Liste des transactions non catégorisées, pour enrichir les mots-clés
- [x] Libellé court des transactions
- [X] Dépenses regroupées par commerçant (nombre d'achats et total), filtrables par catégorie