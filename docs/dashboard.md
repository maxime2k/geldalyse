# Dashboard Geldalyse — conception

Ce document décrit le contenu du tableau de bord, ses règles de calcul et les choix de conception. Les fonctionnalités et l'avancement du projet sont dans le [README](../README.md).

## Objectif

Permettre à l'utilisateur de répondre en un coup d'œil à trois questions :

1. Est-ce que je dépense plus que je ne gagne ?
2. Où part mon argent ?
3. Comment mes finances évoluent-elles dans le temps ?

## Sources de données

Les données de démo et un relevé importé produisent le même **format standard** (voir l'[architecture](../README.md#architecture)). Tout le tableau de bord fonctionne donc de la même façon, quelle que soit la source.

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
| 9 | Évolution | Mois et base de comparaison | Deux listes déroulantes, côte à côte | Quel mois comparer, et à quoi ? |
| 10 | Évolution | Rappel de la comparaison | Phrase sous les listes | Qu'est-ce que je suis en train de comparer ? |
| 11 | Évolution | Chiffres clés | Trois cartes : Entrées, Sorties, Solde, avec l'écart et la valeur de la base | Globalement, ce mois est-il meilleur ou moins bon que d'habitude ? |
| 12 | Évolution | Plus forte variation | Phrase en gras, dans les onglets Sorties et Entrées | Quelle catégorie a le plus changé ? |
| 13 | Évolution | Écarts par catégorie | Barres divergentes, vert si favorable, rouge sinon, avec le montant au bout | Quelles catégories ont augmenté ou baissé, et de combien ? |

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

### Règles de la page Évolution

- **Des mois entiers** : la page compare un mois complet à une base, et n'utilise pas le filtre de période.
- **Le mois par défaut est l'avant-dernier** : le dernier mois du relevé est souvent incomplet.
- **La base par défaut est la moyenne des 3 mois précédents**, moins sensible à un mois exceptionnel. Le mois précédent et le même mois l'an passé sont proposés quand l'historique le permet. Sans historique, la page affiche un message.
- **Les euros avant les pourcentages** : l'écart s'affiche en euros, puis en pourcentage de la base. « < 1 % » signale un écart trop petit pour être arrondi, et « (nouveau) » une base nulle.
- **Pas de pourcentage sur le solde** : il peut changer de signe ou être proche de zéro, et le pourcentage n'aurait alors plus de sens.
- **La couleur dit si l'écart est favorable** : une hausse des sorties est en rouge, une hausse des entrées en vert. La position des barres et le signe des montants portent la même information, pour ne pas dépendre de la couleur.
- **Les deux vues de l'argent s'appliquent aussi ici** : les chiffres clés suivent le compte bancaire, les onglets sont nets des remboursements. La somme des barres peut donc différer de l'écart des chiffres clés.
- **Une seule réponse par question** : les chiffres clés donnent le total, les onglets donnent le détail par catégorie. Une phrase résumé dans les onglets a été retirée, car elle répétait les chiffres clés avec un montant différent.
- **Chaque bloc se lit seul** : les titres des cartes et la légende du graphique rappellent le mois et la base, car sur mobile le haut de la page n'est plus visible.

## Limites connues

- **Un choix manuel s'applique à toute l'opération**, pour toutes ses transactions du même sens. La correction d'une seule transaction nécessite un identifiant de transaction.
- **Les choix manuels sont conservés pendant la session uniquement** : ils sont perdus si la page est rechargée.
- **Un salaire versé par un commerçant** dont le nom est un mot-clé, sans le mot « SALAIRE » dans le libellé, est classé comme un remboursement de ce magasin. Une règle manuelle le corrige.
- **Un mois sans transaction compte pour 0** dans la moyenne de la page Évolution.