# Project-INF8808 - Jeux Olympiques d'Hiver

Tableau de bord interactif pour l'analyse des performances des Jeux Olympiques d'hiver, développé dans le cadre du cours INF8808 (Visualisation de données) à Polytechnique Montréal.

---

## Table des matières

1. [Aperçu](#aperçu)
2. [Structure du projet](#structure-du-projet)
3. [Prérequis](#prérequis)
4. [Installation](#installation)
5. [Lancement de l'application](#lancement-de-lapplication)
6. [Fonctionnement du code](#fonctionnement-du-code)
7. [Données](#données)

---

## Aperçu

L'application Dash présente deux grandes sections de visualisation :

- **Viz 1 - Facteurs physiologiques** : Analyse de l'âge, de la taille et du poids des athlètes selon leur discipline et leurs résultats (boxplot, nuage de points, tendance temporelle).
- **Viz 2 - Facteurs géographiques** : Distribution des médailles par pays et par continent, avec une carte interactive permettant le drill-down continental (carte mondiale → vue continent avec bulles proportionnelles au nombre de médailles).

Un bandeau KPI en haut de page affiche le nombre total d'athlètes, de sports, d'années et de pays couverts par les données.

---

## Structure du projet

```
Project-INF8808/
├── app.py                              # Point d'entrée principal de l'application Dash
├── viz1.py                             # Visualisation 1 (facteurs physiologiques)
├── viz2.py                             # Visualisation 2 (facteurs géographiques)
├── requirements.txt                    # Dépendances Python
├── assets/
│   └── style.css                       # Feuille de styles CSS personnalisée
└── data/
    ├── Olympic_Athlete_Bio.csv         # Profils des athlètes (taille, poids, sexe, date de naissance)
    ├── Olympic_Athlete_Event_Results.csv  # Résultats par épreuve (sport, médaille, pays, athlète)
    ├── Olympic_Games_Medal_Tally.csv   # Tableau des médailles par édition
    ├── Olympic_Results.csv             # Résultats détaillés
    ├── Olympics_Country.csv            # Données des pays participants
    └── Olympics_Games.csv              # Informations sur chaque édition (année, lieu)
```

---

## Prérequis

- **Python 3.10+**
- pip (inclus avec Python)

---

## Installation

### 1. Cloner ou télécharger le projet

```bash
git clone <url-du-dépôt>
cd Project-INF8808
```

### 2. (Optionnel) Créer un environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

Les dépendances installées sont :

| Paquet   | Version minimale | Rôle                                      |
|----------|-----------------|-------------------------------------------|
| dash     | 3.4.0           | Framework web pour l'interface réactive   |
| plotly   | 6.5.2           | Bibliothèque de graphiques interactifs    |
| pandas   | 2.3.3           | Manipulation et analyse des données CSV   |
| numpy    | 2.2.5           | Calculs numériques (outliers, NaN, etc.)  |

---

## Lancement de l'application

```bash
python app.py
```

Puis ouvrez votre navigateur à l'adresse : [http://127.0.0.1:8050/](http://127.0.0.1:8050/)

> En mode `debug=True` (activé par défaut), l'application se rechargera automatiquement à chaque modification du code.

---

## Fonctionnement du code

### `app.py` — Point d'entrée

1. **Chargement des données** : appelle `load_and_preprocess_data()` depuis `viz1.py` et `viz2.py` au démarrage.
2. **Construction du layout** : assemble les sections (header, KPI, viz1, viz2) dans un `html.Div` principal.
3. **Enregistrement des callbacks** : appelle `register_viz1_callbacks()` et `register_viz2_callbacks()` pour connecter les filtres aux graphiques.
4. **Lancement** : `app.run(debug=True)`.

### `viz1.py` — Facteurs physiologiques

| Fonction | Rôle |
|---|---|
| `load_and_preprocess_data(...)` | Fusionne les CSV résultats, biographies et éditions ; filtre sur 3 sports d'hiver (Biathlon, Hockey sur glace, Patinage de vitesse) ; nettoie et traduit les données en français |
| `make_boxplot_figure(df, variable_key)` | Génère un boxplot de la variable choisie (âge / taille / poids) par discipline |
| `make_scatter_figure(df, selected_sport)` | Génère un nuage de points taille vs poids, coloré par médaille |
| `make_trend_figure(df, variable_key)` | Génère une courbe temporelle de la moyenne de la variable choisie par discipline |
| `register_viz1_callbacks(app, df, prefix)` | Enregistre le callback Dash qui relie les 4 filtres (sexe, médailles, variable, sport) aux 3 graphiques |

Filtres disponibles :
- **Sexe** : Tous / M / F
- **Médailles** : Tous / Uniquement médaillés
- **Variable** : Âge / Taille / Poids
- **Sport (nuage de points)** : Tous / Biathlon / Hockey sur glace / Patinage de vitesse

### `viz2.py` — Facteurs géographiques

| Fonction | Rôle |
|---|---|
| `load_and_preprocess_data(event_results_path)` | Charge et nettoie les résultats ; traduit les médailles et sports en français ; génère un identifiant de déduplication par médaille |
| `make_world_figure(df, selected_sport)` | Carte choroplèthe mondiale : coloration par continent selon le total de médailles ; clic pour drill-down |
| `make_bubble_figure(df, selected_sport, continent)` | Vue continent : bulles proportionnelles au total de médailles par pays, avec détail or/argent/bronze au survol |
| `make_barchart_figure(df, selected_sport)` | Diagramme en barres groupées (or / argent / bronze) par pays, trié par total décroissant |
| `register_viz2_callbacks(app, df, prefix)` | Enregistre 2 callbacks : mise à jour du bar chart + gestion du drill-down carte (clic continent : vue bulles, bouton « Retour » : vue monde) |

Filtre disponible :
- **Sport** : Tous / Biathlon / Hockey sur glace / Patinage de vitesse

La carte conserve un `dcc.Store` pour mémoriser le continent actif entre les interactions.

### `assets/style.css`

Style global de l'application (palette de couleurs, typographie Inter, mise en page responsive des grilles, cartes KPI, cartes de visualisation).

---

## Données

Les données proviennent du jeu de données public des Jeux Olympiques (hiver et été). Seules les éditions hivernales sont retenues, filtrées sur les 3 disciplines : **Biathlon**, **Ice Hockey** et **Speed Skating**.

Les fichiers CSV doivent rester dans le dossier `data/` tel que fourni ; les chemins sont référencés directement dans `app.py`.
