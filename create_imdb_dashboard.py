#!/usr/bin/env python3
"""
Create a standalone HTML exploratory dashboard for the Kaggle IMDb Top 1000 dataset.

How to run:
  1) Download the CSV from Kaggle and unzip it.
  2) Put imdb_top_1000.csv in the same folder as this script.
  3) Install requirements:
       pip install pandas numpy plotly
  4) Run:
       python create_imdb_dashboard.py --input imdb_top_1000.csv --output imdb_dashboard.html

This script is designed for the dataset:
https://www.kaggle.com/datasets/harshitshankhdhar/imdb-dataset-of-top-1000-movies-and-tv-shows
"""

from __future__ import annotations

import argparse
import html
import math
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio


EXPECTED_COLUMNS = [
    "Poster_Link", "Series_Title", "Released_Year", "Certificate", "Runtime",
    "Genre", "IMDB_Rating", "Overview", "Meta_score", "Director", "Star1",
    "Star2", "Star3", "Star4", "No_of_Votes", "Gross"
]


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).strip().replace(" ", "_") for c in df.columns]
    return df


def find_col(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    normalized = {c.lower(): c for c in df.columns}
    for candidate in candidates:
        key = candidate.lower()
        if key in normalized:
            return normalized[key]
    return None


def parse_year(value) -> float:
    if pd.isna(value):
        return np.nan
    text = str(value).strip()
    # Handles normal years and occasional non-year values.
    digits = "".join(ch for ch in text if ch.isdigit())
    if len(digits) >= 4:
        return float(digits[:4])
    return np.nan


def parse_runtime_minutes(value) -> float:
    if pd.isna(value):
        return np.nan
    text = str(value).strip().lower()
    digits = "".join(ch if ch.isdigit() else " " for ch in text)
    parts = [p for p in digits.split() if p]
    if not parts:
        return np.nan
    return float(parts[0])


def parse_money(value) -> float:
    if pd.isna(value):
        return np.nan
    text = str(value).strip()
    text = text.replace("$", "").replace(",", "").replace("M", "")
    if text in {"", "nan", "None"}:
        return np.nan
    try:
        return float(text)
    except ValueError:
        return np.nan


def safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def make_missing_table(df: pd.DataFrame) -> pd.DataFrame:
    missing = (
        pd.DataFrame({
            "Column": df.columns,
            "Missing values": df.isna().sum().values,
            "Missing %": (df.isna().mean().values * 100).round(1),
            "Data type": [str(t) for t in df.dtypes],
        })
        .sort_values(["Missing values", "Column"], ascending=[False, True])
    )
    return missing


def table_html(df: pd.DataFrame, max_rows: int = 15) -> str:
    if df.empty:
        return "<p>No rows to display.</p>"
    return df.head(max_rows).to_html(index=False, escape=False, classes="data-table")


def build_dashboard(input_path: Path, output_path: Path) -> None:
    raw = pd.read_csv(input_path)
    df = normalize_column_names(raw)

    title_col = find_col(df, ["Series_Title", "Title", "Movie_Name"])
    year_col = find_col(df, ["Released_Year", "Year", "Year_of_Release"])
    cert_col = find_col(df, ["Certificate", "Age_Certification", "Rating"])
    runtime_col = find_col(df, ["Runtime", "Duration", "Watch_Time"])
    genre_col = find_col(df, ["Genre", "Genres"])
    imdb_col = find_col(df, ["IMDB_Rating", "IMDb_Rating", "IMDB_Score", "IMDb_Score"])
    meta_col = find_col(df, ["Meta_score", "Metascore", "MetaScore"])
    director_col = find_col(df, ["Director"])
    votes_col = find_col(df, ["No_of_Votes", "Votes", "IMDb_Votes"])
    gross_col = find_col(df, ["Gross", "Revenue", "Gross_Earnings"])
    overview_col = find_col(df, ["Overview", "Description", "Plot"])

    required = {
        "title": title_col,
        "year": year_col,
        "genre": genre_col,
        "imdb_rating": imdb_col,
        "votes": votes_col,
    }
    missing_required = [name for name, col in required.items() if col is None]
    if missing_required:
        raise ValueError(f"Missing required columns or unrecognized names: {missing_required}. Found columns: {list(df.columns)}")

    # Clean and engineer features.
    work = df.copy()
    work["Title_clean"] = work[title_col].astype(str) if title_col else np.nan
    work["Released_Year_clean"] = work[year_col].apply(parse_year) if year_col else np.nan
    work["Decade"] = (work["Released_Year_clean"] // 10 * 10).astype("Int64").astype(str) + "s"
    work.loc[work["Released_Year_clean"].isna(), "Decade"] = "Unknown"

    work["Runtime_min"] = work[runtime_col].apply(parse_runtime_minutes) if runtime_col else np.nan
    work["IMDB_Rating_clean"] = safe_numeric(work[imdb_col])
    work["Meta_score_clean"] = safe_numeric(work[meta_col]) if meta_col else np.nan
    work["Votes_clean"] = safe_numeric(work[votes_col])
    work["Gross_millions_clean"] = work[gross_col].apply(parse_money) if gross_col else np.nan
    work["Gross_millions_clean"] = work["Gross_millions_clean"] / 1_000_000 if work["Gross_millions_clean"].max(skipna=True) and work["Gross_millions_clean"].max(skipna=True) > 1000 else work["Gross_millions_clean"]

    if cert_col:
        work["Certificate_clean"] = work[cert_col].fillna("Unknown").astype(str)
    else:
        work["Certificate_clean"] = "Unknown"

    if director_col:
        work["Director_clean"] = work[director_col].fillna("Unknown").astype(str)
    else:
        work["Director_clean"] = "Unknown"

    if overview_col:
        work["Overview_clean"] = work[overview_col].fillna("").astype(str)
        work["Overview_length_words"] = work["Overview_clean"].str.split().str.len()
    else:
        work["Overview_length_words"] = np.nan

    # Split genre column.
    genre_exploded = (
        work.assign(Genre_split=work[genre_col].fillna("Unknown").astype(str).str.split(","))
        .explode("Genre_split")
    )
    genre_exploded["Genre_split"] = genre_exploded["Genre_split"].astype(str).str.strip()
    genre_exploded.loc[genre_exploded["Genre_split"].eq(""), "Genre_split"] = "Unknown"

    # Basic dataset profile.
    n_rows, n_cols = raw.shape
    year_min = int(work["Released_Year_clean"].min()) if not work["Released_Year_clean"].dropna().empty else "N/A"
    year_max = int(work["Released_Year_clean"].max()) if not work["Released_Year_clean"].dropna().empty else "N/A"
    avg_rating = work["IMDB_Rating_clean"].mean()
    median_runtime = work["Runtime_min"].median()
    gross_missing_pct = work["Gross_millions_clean"].isna().mean() * 100

    # Chart 1: genre counts.
    genre_counts = genre_exploded["Genre_split"].value_counts().reset_index()
    genre_counts.columns = ["Genre", "Count"]
    fig_genres = px.bar(
        genre_counts.head(20),
        x="Genre",
        y="Count",
        title="Most common genres",
        text="Count",
    )
    fig_genres.update_layout(xaxis_title="", yaxis_title="Number of titles")

    # Chart 2: IMDb rating distribution.
    fig_rating_dist = px.histogram(
        work,
        x="IMDB_Rating_clean",
        nbins=20,
        title="IMDb rating distribution",
    )
    fig_rating_dist.update_layout(xaxis_title="IMDb rating", yaxis_title="Number of titles")

    # Chart 3: votes vs rating.
    scatter_cols = ["Title_clean", "IMDB_Rating_clean", "Votes_clean", "Gross_millions_clean", "Decade"]
    if genre_col:
        scatter_cols.append(genre_col)
    scatter_df = work[scatter_cols].dropna(subset=["IMDB_Rating_clean", "Votes_clean"]).copy()
    scatter_df["Votes_log10"] = np.log10(scatter_df["Votes_clean"].where(scatter_df["Votes_clean"] > 0))
    fig_votes = px.scatter(
        scatter_df,
        x="Votes_log10",
        y="IMDB_Rating_clean",
        size="Gross_millions_clean" if not scatter_df["Gross_millions_clean"].isna().all() else None,
        hover_name="Title_clean",
        hover_data={col: True for col in scatter_df.columns if col not in ["Title_clean"]},
        title="Popularity vs rating: do highly voted movies also rate higher?",
    )
    fig_votes.update_layout(xaxis_title="log10(number of votes)", yaxis_title="IMDb rating")

    # Chart 4: average IMDb rating by genre, with a minimum sample size.
    genre_rating = (
        genre_exploded.groupby("Genre_split")
        .agg(
            Count=("Title_clean", "count"),
            Avg_IMDb_Rating=("IMDB_Rating_clean", "mean"),
            Median_Votes=("Votes_clean", "median"),
        )
        .reset_index()
    )
    genre_rating_filtered = genre_rating[genre_rating["Count"] >= 10].sort_values("Avg_IMDb_Rating", ascending=False)
    fig_genre_rating = px.bar(
        genre_rating_filtered.head(15),
        x="Genre_split",
        y="Avg_IMDb_Rating",
        hover_data=["Count", "Median_Votes"],
        title="Genres with the highest average IMDb rating (min. 10 titles)",
    )
    fig_genre_rating.update_layout(xaxis_title="", yaxis_title="Average IMDb rating")

    # Chart 5: titles by decade.
    decade_counts = work["Decade"].value_counts().reset_index()
    decade_counts.columns = ["Decade", "Count"]
    decade_counts["Decade_num"] = decade_counts["Decade"].str.extract(r"(\d+)").astype(float)
    decade_counts = decade_counts.sort_values("Decade_num")
    fig_decade = px.bar(
        decade_counts.drop(columns=["Decade_num"]),
        x="Decade",
        y="Count",
        text="Count",
        title="Which decades dominate the IMDb Top 1000?",
    )
    fig_decade.update_layout(xaxis_title="", yaxis_title="Number of titles")

    # Chart 6: certificate distribution.
    cert_counts = work["Certificate_clean"].value_counts().reset_index()
    cert_counts.columns = ["Certificate", "Count"]
    fig_cert = px.bar(
        cert_counts.head(15),
        x="Certificate",
        y="Count",
        text="Count",
        title="Certificate / age-rating distribution",
    )
    fig_cert.update_layout(xaxis_title="", yaxis_title="Number of titles")

    # Chart 7: correlation heatmap for numeric columns.
    numeric_cols = {
        "IMDb rating": "IMDB_Rating_clean",
        "Metascore": "Meta_score_clean",
        "Votes": "Votes_clean",
        "Runtime": "Runtime_min",
        "Gross (millions)": "Gross_millions_clean",
        "Overview length": "Overview_length_words",
    }
    available_numeric = {label: col for label, col in numeric_cols.items() if col in work and work[col].notna().sum() >= 10}
    corr = work[list(available_numeric.values())].corr(numeric_only=True)
    corr.index = list(available_numeric.keys())
    corr.columns = list(available_numeric.keys())
    fig_corr = px.imshow(
        corr.round(2),
        text_auto=True,
        title="Correlation between numeric features",
        aspect="auto",
    )

    # Chart 8: genre co-occurrence heatmap.
    top_genres = genre_counts.head(12)["Genre"].tolist()
    co_matrix = pd.DataFrame(0, index=top_genres, columns=top_genres)
    for genres in work[genre_col].fillna("").astype(str).str.split(","):
        genres = [g.strip() for g in genres if g.strip() in top_genres]
        for g1 in genres:
            for g2 in genres:
                co_matrix.loc[g1, g2] += 1
    fig_co = px.imshow(
        co_matrix,
        text_auto=True,
        title="Genre co-occurrence: which genres appear together?",
        aspect="auto",
    )

    # High-rated profile.
    high_threshold = max(8.5, work["IMDB_Rating_clean"].quantile(0.90))
    high = work[work["IMDB_Rating_clean"] >= high_threshold].copy()
    high_genre = genre_exploded[genre_exploded["Title_clean"].isin(high["Title_clean"])].copy()

    overall_genre_share = genre_exploded["Genre_split"].value_counts(normalize=True)
    high_genre_share = high_genre["Genre_split"].value_counts(normalize=True)
    lift = (
        pd.DataFrame({
            "Genre": sorted(set(overall_genre_share.index) | set(high_genre_share.index)),
        })
        .assign(
            Overall_share=lambda x: x["Genre"].map(overall_genre_share).fillna(0),
            High_rated_share=lambda x: x["Genre"].map(high_genre_share).fillna(0),
        )
    )
    lift["Lift"] = (lift["High_rated_share"] / lift["Overall_share"].replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
    lift = lift[lift["Overall_share"] > 0].sort_values("Lift", ascending=False)
    fig_lift = px.bar(
        lift.head(15),
        x="Genre",
        y="Lift",
        hover_data={
            "Overall_share": ":.1%",
            "High_rated_share": ":.1%",
            "Lift": ":.2f",
        },
        title=f"Genres over-represented among high-rated titles (rating ≥ {high_threshold:.1f})",
    )
    fig_lift.update_layout(xaxis_title="", yaxis_title="Lift vs overall genre share")

    # Top directors by average rating.
    director_summary = (
        work.groupby("Director_clean")
        .agg(
            Movies=("Title_clean", "count"),
            Avg_IMDb_Rating=("IMDB_Rating_clean", "mean"),
            Median_Votes=("Votes_clean", "median"),
            Total_Gross_Millions=("Gross_millions_clean", "sum"),
        )
        .reset_index()
    )
    director_summary = director_summary[director_summary["Movies"] >= 2].sort_values(
        ["Avg_IMDb_Rating", "Movies"], ascending=[False, False]
    )
    fig_directors = px.bar(
        director_summary.head(15),
        x="Director_clean",
        y="Avg_IMDb_Rating",
        hover_data=["Movies", "Median_Votes", "Total_Gross_Millions"],
        title="Directors with the highest average IMDb rating (min. 2 titles)",
    )
    fig_directors.update_layout(xaxis_title="", yaxis_title="Average IMDb rating")

    # Tables.
    missing_table = make_missing_table(work)

    high_table_cols = ["Title_clean", "Released_Year_clean", "IMDB_Rating_clean", "Votes_clean", "Runtime_min", "Director_clean"]
    if gross_col:
        high_table_cols.append("Gross_millions_clean")
    top_movies = (
        work[high_table_cols]
        .sort_values(["IMDB_Rating_clean", "Votes_clean"], ascending=[False, False])
        .rename(columns={
            "Title_clean": "Title",
            "Released_Year_clean": "Year",
            "IMDB_Rating_clean": "IMDb rating",
            "Votes_clean": "Votes",
            "Runtime_min": "Runtime (min)",
            "Director_clean": "Director",
            "Gross_millions_clean": "Gross (millions)",
        })
    )

    # Interesting computed insights.
    top_genre = genre_counts.iloc[0]["Genre"] if not genre_counts.empty else "N/A"
    top_genre_count = int(genre_counts.iloc[0]["Count"]) if not genre_counts.empty else 0
    best_genre = genre_rating_filtered.iloc[0]["Genre_split"] if not genre_rating_filtered.empty else "N/A"
    best_genre_rating = genre_rating_filtered.iloc[0]["Avg_IMDb_Rating"] if not genre_rating_filtered.empty else np.nan
    top_decade = decade_counts.sort_values("Count", ascending=False).iloc[0]["Decade"] if not decade_counts.empty else "N/A"
    top_decade_count = int(decade_counts.sort_values("Count", ascending=False).iloc[0]["Count"]) if not decade_counts.empty else 0

    corr_with_rating = corr["IMDb rating"].drop(labels=["IMDb rating"], errors="ignore").dropna() if "IMDb rating" in corr else pd.Series(dtype=float)
    if not corr_with_rating.empty:
        strongest_corr_feature = corr_with_rating.abs().idxmax()
        strongest_corr_value = corr_with_rating[strongest_corr_feature]
        corr_text = f"The strongest simple numeric relationship with IMDb rating is <b>{html.escape(str(strongest_corr_feature))}</b> (correlation = <b>{strongest_corr_value:.2f}</b>)."
    else:
        corr_text = "There are not enough numeric features to calculate correlations."

    high_rated_count = len(high)
    high_rated_share = high_rated_count / len(work) * 100 if len(work) else 0

    fig_htmls = []
    for fig in [
        fig_genres,
        fig_rating_dist,
        fig_votes,
        fig_genre_rating,
        fig_decade,
        fig_cert,
        fig_corr,
        fig_co,
        fig_lift,
        fig_directors,
    ]:
        fig_htmls.append(pio.to_html(fig, include_plotlyjs=False, full_html=False))

    plotly_js = '<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>'

    html_doc = f"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>IMDb Top 1000 Exploratory Dashboard</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {plotly_js}
  <style>
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: #f6f7fb;
      color: #202124;
    }}
    header {{
      padding: 28px 40px;
      background: white;
      border-bottom: 1px solid #ddd;
    }}
    header h1 {{
      margin: 0 0 8px 0;
      font-size: 32px;
    }}
    header p {{
      margin: 4px 0;
      color: #555;
      line-height: 1.5;
    }}
    main {{
      padding: 24px 40px 44px 40px;
      max-width: 1400px;
      margin: auto;
    }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 14px;
      margin-bottom: 24px;
    }}
    .card {{
      background: white;
      border: 1px solid #e0e0e0;
      border-radius: 14px;
      padding: 18px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }}
    .metric {{
      font-size: 28px;
      font-weight: 700;
      margin-bottom: 6px;
    }}
    .label {{
      color: #666;
      font-size: 14px;
    }}
    .section {{
      background: white;
      border: 1px solid #e0e0e0;
      border-radius: 14px;
      padding: 20px;
      margin-bottom: 20px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }}
    .section h2 {{
      margin-top: 0;
      font-size: 22px;
    }}
    .insights {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 12px;
    }}
    .insight {{
      padding: 14px;
      border: 1px solid #e5e5e5;
      border-radius: 12px;
      background: #fafafa;
      line-height: 1.45;
    }}
    .chart-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(520px, 1fr));
      gap: 20px;
      align-items: start;
    }}
    .chart-box {{
      border: 1px solid #eee;
      border-radius: 12px;
      padding: 8px;
      overflow-x: auto;
    }}
    .data-table {{
      border-collapse: collapse;
      width: 100%;
      font-size: 14px;
    }}
    .data-table th, .data-table td {{
      border: 1px solid #ddd;
      padding: 8px;
      text-align: left;
    }}
    .data-table th {{
      background: #f1f3f4;
    }}
    .note {{
      color: #666;
      line-height: 1.5;
    }}
    code {{
      background: #f1f3f4;
      padding: 2px 4px;
      border-radius: 4px;
    }}
  </style>
</head>
<body>
<header>
  <h1>IMDb Top 1000 Exploratory Dashboard</h1>
  <p>A classroom-friendly dashboard for understanding dataset dimensions, feature quality, movie genres, ratings, popularity, revenue, and high-rated title patterns.</p>
  <p class="note">Important limitation: this is a curated Top 1000 dataset, not a random sample of all IMDb titles. Patterns should be interpreted as patterns among highly rated/popular titles only.</p>
</header>

<main>
  <section class="cards">
    <div class="card"><div class="metric">{n_rows:,}</div><div class="label">Rows / titles</div></div>
    <div class="card"><div class="metric">{n_cols:,}</div><div class="label">Original columns</div></div>
    <div class="card"><div class="metric">{year_min}–{year_max}</div><div class="label">Release year range</div></div>
    <div class="card"><div class="metric">{avg_rating:.2f}</div><div class="label">Average IMDb rating</div></div>
    <div class="card"><div class="metric">{median_runtime:.0f}</div><div class="label">Median runtime in minutes</div></div>
    <div class="card"><div class="metric">{gross_missing_pct:.1f}%</div><div class="label">Missing gross values</div></div>
  </section>

  <section class="section">
    <h2>1. Fast interpretation</h2>
    <div class="insights">
      <div class="insight">The most frequent genre tag is <b>{html.escape(str(top_genre))}</b>, appearing in <b>{top_genre_count}</b> titles.</div>
      <div class="insight">Among genres with at least 10 titles, <b>{html.escape(str(best_genre))}</b> has the highest average IMDb rating at <b>{best_genre_rating:.2f}</b>.</div>
      <div class="insight">The decade with the largest representation is <b>{html.escape(str(top_decade))}</b>, with <b>{top_decade_count}</b> titles.</div>
      <div class="insight">There are <b>{high_rated_count}</b> high-rated titles using the dashboard threshold of rating ≥ <b>{high_threshold:.1f}</b>, about <b>{high_rated_share:.1f}%</b> of the dataset.</div>
      <div class="insight">{corr_text}</div>
    </div>
  </section>

  <section class="section">
    <h2>2. Dataset structure and cleaning</h2>
    <p class="note">
      The dashboard cleans common fields: release year is converted to a number, runtime is converted from text such as <code>142 min</code> to minutes,
      votes are converted to numeric values, gross revenue is converted to numeric millions, and the comma-separated genre field is exploded for genre-level analysis.
    </p>
    <h3>Missing values and data types</h3>
    {table_html(missing_table, 20)}
  </section>

  <section class="section">
    <h2>3. Visual exploration</h2>
    <div class="chart-grid">
      {''.join(f'<div class="chart-box">{chart}</div>' for chart in fig_htmls)}
    </div>
  </section>

  <section class="section">
    <h2>4. High-rated movies</h2>
    <p class="note">
      This table is sorted first by IMDb rating and then by number of votes. It is useful for asking whether a very high rating is supported by broad audience participation.
    </p>
    {table_html(top_movies, 20)}
  </section>

  <section class="section">
    <h2>5. Suggested 45-minute class activity</h2>
    <ol>
      <li><b>5 minutes:</b> Identify the unit of analysis: one row = one title. Discuss why a Top 1000 dataset is biased toward successful titles.</li>
      <li><b>10 minutes:</b> Inspect dimensions, data types, and missing values. Decide which columns need cleaning.</li>
      <li><b>10 minutes:</b> Explore genre distribution and genre combinations. Ask which genres dominate and which combinations are common.</li>
      <li><b>10 minutes:</b> Compare rating, votes, gross, runtime, and metascore. Ask whether rating seems linked to popularity or revenue.</li>
      <li><b>10 minutes:</b> Focus on high-rated movies. Ask which genres/directors/decades are over-represented and whether the pattern is meaningful or caused by selection bias.</li>
    </ol>
  </section>
</main>
</body>
</html>
"""
    output_path.write_text(html_doc, encoding="utf-8")
    print(f"Dashboard written to: {output_path.resolve()}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Create an IMDb Top 1000 HTML dashboard.")
    parser.add_argument("--input", default="imdb_top_1000.csv", help="Path to the IMDb CSV file.")
    parser.add_argument("--output", default="imdb_dashboard.html", help="Output HTML path.")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}. Download and unzip the Kaggle CSV, then pass its path with --input."
        )

    build_dashboard(input_path, output_path)


if __name__ == "__main__":
    main()
