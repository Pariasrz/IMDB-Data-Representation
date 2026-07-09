# Methodology

## Preprocessing

The dashboard applies light preprocessing before visualization:

- `Released_Year` is converted into a numeric year and decade.
- `Runtime` is converted from text such as `142 min` into numeric minutes.
- `Gross` is cleaned by removing commas and converting values into millions of dollars.
- `Genre` is split into separate genre tags because each title may have multiple genres.
- `No_of_Votes`, `IMDB_Rating`, and `Meta_score` are converted into numeric fields.
- Missing values are preserved and summarized rather than silently removed.

## Exploratory analysis

The dashboard includes:

- Frequency analysis for categorical variables.
- Multi-label genre analysis.
- Genre co-occurrence heatmap.
- Correlation analysis for numerical variables.
- High-rated movie lift analysis.
- Director and star aggregation with minimum sample-size filters.
- Outlier tables for most-voted and highest-grossing titles.

## Interpretation caution

The dataset is not a complete movie-industry dataset. It is a Top 1000 IMDb collection, so the observed patterns may reflect selection bias, popularity bias, and IMDb user demographics.
