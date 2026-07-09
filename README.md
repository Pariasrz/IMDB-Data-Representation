# IMDb Top 1000 Exploratory Dashboard

An interactive exploratory data analysis dashboard for the Kaggle IMDb Top 1000 Movies and TV Shows dataset.

## Live dashboard

The dashboard is available at:

```text
https://pariasrz.github.io/imdb-top1000-dashboard/
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
[https://pariasrz.github.io/imdb-top1000-dashboard/](https://www.kaggle.com/datasets/babaakki/imdb1000)
```


The dashboard is generated from the dataset for educational exploratory analysis.

## How to use locally

Open `index.html` in any modern web browser.


## Notes and limitations

This dataset is a curated Top 1000 IMDb dataset, not a random sample of all movies. Therefore, the dashboard describes patterns among highly rated/popular titles, not the entire movie industry.

Some conclusions involving gross revenue should be treated carefully because the `Gross` field has missing values.
