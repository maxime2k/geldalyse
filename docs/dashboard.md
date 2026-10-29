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

Principe : **du plus général au plus détaillé**, de haut en bas, et **le contenu avant la navigation**.

| # | Page | Élément | Forme | Question à laquelle il répond |
|---|---|---|---|---|
| 1 | Barre latérale | Menu des pages, source des données et filtre de période | Menu de navigation, choix de la source, calendrier | Où aller, quelles données, sur quelle période ? |
| 2 | Barre latérale | Transactions non catégorisées | Avertissement et lien « Les classer », dans un même cadre | Le catégoriseur a-t-il besoin de nouveaux mots-clés ? |
| 3 | Vue d'ensemble | Entrées, sorties, solde | Trois chiffres clés en cartes (`st.metric` avec cadre) | Est-ce que je dépense plus que je ne gagne ? |
| 4 | Vue d'ensemble | Sorties et entrées par catégorie | Deux onglets ; barres horizontales triées de la plus grande à la plus petite, avec le montant de chaque barre | Où part mon argent, d'où vient-il ? |
| 5 | Vue d'ensemble | Entrées et sorties par mois | Barres groupées, en pleine largeur | Comment ça évolue ? |
| 6 | Vue d'ensemble | Aller plus loin | Une carte par page, en bas de page | Que puis-je regarder ensuite ? |
| 7 | Transactions | Transactions non catégorisées, par opération | Tableau modifiable : une catégorie à choisir par opération | Que reste-t-il à classer ? |
| 8 | Transactions | Transactions, avec filtre par catégorie | Tableau modifiable en deux onglets, sorties et entrées, les plus récentes en premier | Quelles opérations se cachent derrière les chiffres ? |

## Règles de conception

- **Aucune catégorie écrite en dur** dans le dashboard : les catégories affichées sont celles présentes dans les données. Une nouvelle catégorie apparaît automatiquement.
- **Catégories selon le signe du montant** : une sortie reçoit une catégorie de sortie ; une entrée reçoit une catégorie d'entrée, sauf un remboursement de magasin, qui garde la catégorie de sa dépense.
- **Sorties affichées en valeurs positives** dans les graphiques, pour une lecture naturelle.
- **Les entrées sont exclues** du graphique des sorties par catégorie. Les remboursements de magasin y sont déduits de leur catégorie de dépense.
- **Les retraits d'espèces** apparaissent comme une catégorie à part entière, RETRAITS.
- **Deux vues de l'argent** :
  - les **chiffres clés** et le **graphique mensuel** suivent le compte bancaire : une entrée est un montant positif, une sortie un montant négatif. Leurs totaux sont vérifiables sur le relevé ;
  - les **onglets par catégorie** montrent ce que l'argent représente : un remboursement de magasin est déduit de sa catégorie de dépense, et n'apparaît pas dans les entrées.
- **Cohérence entre les deux vues** : total des entrées par catégorie − total des sorties par catégorie = Solde.
- **Choix manuels selon le sens de l'argent** : une sortie ne peut recevoir qu'une catégorie de sortie, une entrée qu'une catégorie d'entrée. L'utilisateur ne transforme jamais une entrée en sortie.
- **Le filtre de période** s'applique à tout le dashboard ; **le filtre par catégorie** ne s'applique qu'au tableau des transactions. Une sélection de catégories vide affiche toutes les catégories.
- **Une période sans transaction** affiche un message, au lieu d'une page vide.
- **Pas d'information portée uniquement par la couleur** : chaque série est nommée dans une légende.
- **Le libellé court** est affiché en priorité ; **la description complète** reste disponible en dernière colonne, pour ne rien cacher.
- **Le contenu avant la navigation** : les liens vers les autres pages sont en bas de la vue d'ensemble. Sur mobile, les colonnes s'empilent, et l'utilisateur voit ses résultats en premier.

## Limites connues

- **Un choix manuel s'applique à toute l'opération**, pour toutes ses transactions du même sens. La correction d'une seule transaction nécessite un identifiant de transaction.
- **Les choix manuels sont conservés pendant la session uniquement** : ils sont perdus si la page est rechargée.
- **Un salaire versé par un commerçant** dont le nom est un mot-clé, sans le mot « SALAIRE » dans le libellé, est classé comme un remboursement de ce magasin. Une règle manuelle le corrige.

## Suivi de construction

- [x] Squelette de l'application (`app.py`) qui se lance avec `streamlit run app.py`
- [x] Barre latérale : choix de la source (démo ou relevé importé)
- [x] Chargement des données et ajout de la colonne `category`
- [x] Filtre de période
- [x] Trois chiffres clés
- [x] Dépenses par catégorie
- [x] Revenus et dépenses par mois
- [x] Tableau des transactions
- [x] Gestion des erreurs d'import (fichier au mauvais format, fichier vide, relevé sans transaction)
- [x] Filtre du tableau par catégorie
- [x] Indicateur des transactions non catégorisées

## Prévu pour la V2

- [x] Libellé court des transactions
- [x] Regroupement des transactions non catégorisées par opération, pour enrichir les mots-clés
- [x] Correction manuelle de la catégorie d'une opération non catégorisée (`st.data_editor`)
- [x] Catégories d'entrée attribuées automatiquement (salaire, intérêts, remboursement d'une personne, autres entrées) ; un remboursement de magasin garde la catégorie de sa dépense
- [x] Chiffres clés Entrées / Sorties / Solde, et onglets des sorties et des entrées par catégorie
- [x] Totaux nets par catégorie : un remboursement de magasin réduit sa catégorie de dépense
- [x] Correction manuelle de la catégorie depuis le tableau des transactions, pour toute l'opération
- [ ] Dépenses regroupées par commerçant (nombre d'achats et total), filtrables par catégorie
- [ ] Correction de la catégorie d'une seule transaction, avec le numéro de mouvement ING
- [ ] Indicateurs clés du mois, avec comparaison au mois précédent (`st.metric` avec `delta`)
- [ ] Paiements récurrents, sous forme de tableau (nécessite un algorithme de détection : même libellé, montant proche, chaque mois)