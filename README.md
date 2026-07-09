# IMDb Top 1000 Exploratory Dashboard

An interactive exploratory data analysis dashboard for the Kaggle IMDb Top 1000 Movies and TV Shows dataset.

The dashboard is available at:

```text
ttps://pariasrz.github.io/IMDB-Data-Representation/
```

## What this dashboard explores

- Dataset dimensions and feature types
- Missing values and preprocessing needs
- Genre distribution and genre co-occurrence
- IMDb rating distribution
- Rating vs audience votes
- Rating vs critic metascore
- Rating vs gross revenue
- Runtime and decade trends
- High-rated movie patterns
- Director and recurring star patterns
- Popularity and revenue outliers

## Files

```text
.
├── index.html                  # Main dashboard file for GitHub Pages
├── create_imdb_dashboard.py     # Optional script used to generate a dashboard from the CSV
├── README.md                    # Project description and instructions
├── .gitignore                   # Files to avoid committing
└── docs/
    └── methodology.md           # Short explanation of preprocessing and analysis
```

## Dataset

Dataset source: Kaggle IMDb Dataset of Top 1000 Movies and TV Shows by Harshit Shankhdhar at the following linK 

```text
https://www.kaggle.com/datasets/babaakki/imdb1000
```


The dashboard is generated from the dataset for educational exploratory analysis.

## How to use locally

Open `index.html` in any modern web browser.


## Notes and limitations

This dataset is a curated Top 1000 IMDb dataset, not a random sample of all movies. Therefore, the dashboard describes patterns among highly rated/popular titles, not the entire movie industry.

Some conclusions involving gross revenue should be treated carefully because the `Gross` field has missing values.



# Synthetic IMDb-Style Movie Dataset

## Overview

This repository also contains a synthetic movie dataset inspired by the structure and characteristics of publicly available IMDb movie data. The goal was to create a realistic dataset that can be used for educational purposes, including data mining, exploratory data analysis (EDA), visualization, machine learning, clustering, and statistical analysis.

The dataset contains 50 fictional movies with attributes commonly found in movie databases, including release information, financial performance, audience ratings, and content classifications.

## Dataset Schema

| Column          | Description                                   |
| --------------- | --------------------------------------------- |
| movie_id        | Unique identifier for each movie              |
| title           | Fictional movie title                         |
| release_year    | Year of release                               |
| genre           | Primary movie genre                           |
| runtime_minutes | Duration of the movie in minutes              |
| country         | Country of production                         |
| average_rating  | Average audience rating on a scale of 1–10    |
| num_votes       | Number of audience votes                      |
| budget_million  | Estimated production budget (millions USD)    |
| revenue_million | Estimated worldwide revenue (millions USD)    |
| content_rating  | Audience suitability rating (G, PG, PG-13, R) |

## Data Generation Approach

Rather than generating completely random values, the dataset was designed to mimic realistic relationships commonly observed in real-world movie data:

* Most ratings fall between 7.0 and 8.5, similar to the distribution seen among well-known films.
* Higher-budget productions generally generate higher revenues, although some movies underperform while others become major successes.
* The number of votes roughly correlates with popularity and commercial performance.
* Certain genres are associated with specific countries:

  * USA: Action, Science Fiction, Crime
  * Japan: Animation, Family
  * South Korea: Thriller, Mystery, Crime
  * France and Italy: Drama and Romance
  * UK and Germany: Historical and Biographical films
* Content ratings were selected to align with genre conventions (e.g., Family films are generally G or PG, while Crime and Thriller films are often rated R).

Movie titles were manually crafted to resemble real film titles rather than randomly generated strings.

## Exploratory Observations

Although the dataset is synthetic, several interesting patterns emerge:

### 1. Science Fiction and Action Films Have the Largest Budgets

Movies such as *The Europa Protocol*, *Titan Station*, and *Echoes of Andromeda* have significantly larger budgets than dramas or romances. This reflects the higher production costs typically associated with visual effects and large-scale productions.

### 2. Animation Shows Strong Financial Performance

Several animated films achieve high audience ratings and strong revenue-to-budget ratios, suggesting a broad audience appeal similar to successful real-world animated releases.

### 3. Revenue Does Not Always Scale Linearly With Budget

While larger budgets often lead to higher revenues, some lower-budget films still achieve respectable financial performance. This creates opportunities to analyze return on investment (ROI) and identify efficient productions.

### 4. Country-Specific Genre Trends

Distinct genre concentrations can be observed:

* Japan contributes primarily Animation and Family films.
* South Korea contributes Mystery, Thriller, and Crime films.
* France and Italy contribute Romance and Drama titles.
* The United States dominates Action and Science Fiction categories.

### 5. Ratings and Popularity Are Positively Correlated

Movies with higher ratings generally receive more audience votes, although there are exceptions. This makes the dataset suitable for correlation analysis and predictive modeling exercises.

### 6. Presence of Outliers

The dataset intentionally includes blockbuster-style outliers with:

* Very high budgets
* Large vote counts
* Exceptional revenues

These records help demonstrate the impact of outliers during visualization and statistical analysis.

## Disclaimer

All movies, titles, ratings, budgets, revenues, and vote counts in this dataset are synthetic and were created solely for educational and research purposes. Any resemblance to real films is coincidental.
