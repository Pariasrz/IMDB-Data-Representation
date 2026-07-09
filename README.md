# IMDb Top 1000 Exploratory Dashboard

An interactive exploratory data analysis dashboard for the Kaggle IMDb Top 1000 Movies and TV Shows dataset.

## Live dashboard

After enabling GitHub Pages, the dashboard will be available at:

```text
https://YOUR-USERNAME.github.io/imdb-top1000-dashboard/
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

Dataset source: Kaggle IMDb Dataset of Top 1000 Movies and TV Shows by Harshit Shankhdhar.

Because the dataset belongs to its Kaggle source, this repository does **not** need to include the raw CSV file. The dashboard is generated from the dataset for educational exploratory analysis.

## How to use locally

Open `index.html` in any modern web browser.

## How to publish with GitHub Pages

1. Create a new GitHub repository, for example: `imdb-top1000-dashboard`.
2. Upload the files in this folder.
3. Go to **Settings → Pages**.
4. Under **Build and deployment**, choose:
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/root`
5. Save.
6. Wait a minute or two, then open the GitHub Pages URL.

## Notes and limitations

This dataset is a curated Top 1000 IMDb dataset, not a random sample of all movies. Therefore, the dashboard describes patterns among highly rated/popular titles, not the entire movie industry.

Some conclusions involving gross revenue should be treated carefully because the `Gross` field has missing values.
