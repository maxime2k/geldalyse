# Spendlens

> Comprendre où part son argent, en quelques secondes.

Spendlens est une application Python qui importe un relevé bancaire au format CSV, catégorise automatiquement les transactions et affiche un tableau de bord des dépenses.

🚧 **Statut : en développement** (V1 en cours)

---

## Fonctionnalités

### V1 — en cours
- [ ] Import d'un relevé de transactions au format CSV (export ING en français)
- [ ] Nettoyage des données (dates, montants, libellés)
- [x] Catégorisation automatique par mots-clés (alimentation, transport, logement…)
- [ ] Tableau de bord : dépenses par catégorie et par mois

### V2 — prévue

**Données et import**
- [ ] Exports ING en néerlandais, anglais et allemand
- [ ] Prise en charge d'autres banques (BNP Paribas Fortis, Belfius…)
- [ ] Import de jeux de données publics (Kaggle, UCI) via le même format standard
- [ ] Générateur produisant des relevés fictifs au format ING, pour une démo à grand volume
- [ ] Extraction du nom du commerçant à partir de la description bancaire

**Catégorisation**
- [ ] Catégorisation par apprentissage automatique
- [ ] Prise en compte du signe du montant (ex. opération bancaire positive → revenu)
- [ ] Mots-clés stockés dans un fichier de configuration, modifiables sans toucher au code
- [ ] Distinction entre abonnements de loisirs (Netflix…) et factures essentielles (Proximus…)
- [ ] Suivi du taux de couverture (part des transactions catégorisées)

**Tableau de bord**
- [ ] Liste des transactions non catégorisées, pour enrichir les mots-clés
- [ ] Détection des dépenses inhabituelles
- [ ] Budgets par catégorie avec alertes

## Stack technique

| Rôle | Outil |
|---|---|
| Langage | Python 3.10+ |
| Manipulation des données | pandas |
| Interface | Streamlit |
| Tests | pytest |

## Données

Le projet utilise exclusivement des **données fictives** : un générateur de transactions et une fixture synthétique au format d'export ING. Aucune donnée bancaire réelle n'est stockée ni versionnée.

## Installation

*À venir.*

## Auteur

**Maxime Kamgue Kamgue** 