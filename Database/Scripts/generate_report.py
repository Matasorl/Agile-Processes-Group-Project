"""
Generate a Markdown report from existing analytics outputs via an LLM.

Project-specific assumptions:
- CSV summaries live under Database/Data/ (e.g., genre_avg_ratings_from_db.csv, genre_avg_ratings_dashboard.csv,
  avg_rating_by_runtime.csv, runtime_rating_correlations.csv, avg_ratings_directors_stars.csv).
- Plot images live under Database/Images/.
- correlation_matrix.png may exist in the repo root; if found, it is referenced.

The script does not redo analysis; it summarizes existing aggregated files,
passes the summary to an LLM, and writes the LLM-generated Markdown to report.md.
"""

import glob
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

ROOT = Path(__file__).resolve().parents[2]  
DEFAULT_REPORT = ROOT / "report.md"
DATA_DIR = ROOT / "Database" / "Data"
IMAGES_DIR = ROOT / "Database" / "Images"


def read_csv_safe(path: Path) -> Optional[pd.DataFrame]:
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    lower_cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand in lower_cols:
            return lower_cols[cand]
    for col in df.columns:
        for cand in candidates:
            if cand in col.lower():
                return col
    return None


def numeric_series(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def runtime_to_minutes(series: pd.Series) -> pd.Series:
    def extract_minutes(val):
        if pd.isna(val):
            return None
        text = str(val).strip()

       
        try:
            fval = float(text)
            if fval == 0:
                return None
            if fval < 10:
                return int(round(fval * 100))  
            return int(round(fval))
        except ValueError:
            pass

       
        match = re.search(r"([0-9]+(?:\\.[0-9]+)?)", text)
        if match:
            num = float(match.group(1))
            if num == 0:
                return None
            if num < 10:
                return int(round(num * 100))
            return int(round(num))

        return None

    return series.apply(extract_minutes)


def summarize_top(df: pd.DataFrame, label_col: str, value_col: str, top_n: int = 5) -> List[str]:
    df_local = df.copy()
    df_local[value_col] = numeric_series(df_local[value_col])
    df_local = df_local.dropna(subset=[value_col])
    df_local = df_local.sort_values(by=value_col, ascending=False).head(top_n)
    bullets = []
    for _, row in df_local.iterrows():
        label = str(row[label_col]).strip()
        val = row[value_col]
        bullets.append(f"{label} ({val:.2f})")
    return bullets


def summarize_genres(df: pd.DataFrame) -> List[str]:
    genre_col = find_column(df, ["genre"])
    rating_col = find_column(df, ["avg_rating", "rating", "mean_rating"])
    if not genre_col or not rating_col:
        return []
    return summarize_top(df, genre_col, rating_col, top_n=5)


def summarize_runtime(df: pd.DataFrame) -> List[str]:
    runtime_col = find_column(df, ["runtime"])
    rating_col = find_column(df, ["avg_rating", "rating", "mean_rating"])
    if not runtime_col or not rating_col:
        return []
    df_local = df.copy()
    df_local["runtime_minutes"] = runtime_to_minutes(df_local[runtime_col])
    rating_col_name = rating_col
    df_local[rating_col_name] = numeric_series(df_local[rating_col_name])
    df_local = df_local.dropna(subset=["runtime_minutes", rating_col_name])
    filtered = df_local[df_local["runtime_minutes"] >= 40]
    if not filtered.empty:
        df_local = filtered
    df_local = df_local.sort_values(by=rating_col_name, ascending=False).head(5)
    bullets = []
    for _, row in df_local.iterrows():
        bullets.append(f"{int(row['runtime_minutes'])} min ({row[rating_col_name]:.2f})")
    return bullets


def summarize_people(df: pd.DataFrame, entity_hint: str) -> List[str]:
    name_col = find_column(df, [entity_hint, "name", "person"])
    rating_col = find_column(df, ["avg_rating", "rating", "mean_rating"])
    count_col = find_column(df, ["count", "num_movies", "movies"])
    if not name_col or not rating_col:
        return []
    df_local = df.copy()
    df_local[rating_col] = numeric_series(df_local[rating_col])
    if count_col:
        df_local[count_col] = numeric_series(df_local[count_col])
    df_local = df_local.dropna(subset=[rating_col])
    df_local = df_local.sort_values(by=rating_col, ascending=False).head(5)
    bullets = []
    for _, row in df_local.iterrows():
        name = str(row[name_col]).strip()
        rating = row[rating_col]
        count_txt = ""
        if count_col and not pd.isna(row[count_col]):
            count_txt = f", {int(row[count_col])} titles"
        bullets.append(f"{name} ({rating:.2f}{count_txt})")
    return bullets


def load_known_csvs() -> Dict[str, pd.DataFrame]:
    mapping = {}
    candidates = {
        "genre": [
            DATA_DIR / "genre_avg_ratings_from_db.csv",
            DATA_DIR / "genre_avg_ratings_dashboard.csv",
        ],
        "runtime": [
            DATA_DIR / "avg_rating_by_runtime.csv",
            DATA_DIR / "avg_rating_by_runtime_2dp.csv",
            DATA_DIR / "runtime_rating_correlations.csv",
        ],
        "people": [
            DATA_DIR / "avg_ratings_directors_stars.csv",
        ],
    }
    for key, paths in candidates.items():
        for path in paths:
            if path.exists():
                df = read_csv_safe(path)
                if df is not None:
                    mapping[key] = df
                    break
    return mapping


def load_additional_outputs() -> Dict[str, pd.DataFrame]:
    out_dir = DATA_DIR
    mapping = {}
    for path_str in glob.glob(str(out_dir / "*.csv")):
        path = Path(path_str)
        df = read_csv_safe(path)
        if df is not None and path.name not in {
            "genre_avg_ratings_from_db.csv",
            "genre_avg_ratings_dashboard.csv",
            "avg_rating_by_runtime.csv",
            "avg_rating_by_runtime_2dp.csv",
            "runtime_rating_correlations.csv",
            "avg_ratings_directors_stars.csv",
            "movies-cleaned.csv",
            "movies-column-dropped.csv",
            "movies-normalized.csv",
            "movies.csv",
            "movies_category_cleaned.csv",
        }:
            mapping[path.name] = df
    return mapping


def collect_plot_refs() -> List[str]:
    plots = []
    if IMAGES_DIR.exists():
        for p in sorted([p for p in IMAGES_DIR.glob("*.png") if p.is_file()]):
            try:
                plots.append(str(p.relative_to(ROOT)))
            except ValueError:
                plots.append(str(p))
    corr = ROOT / "correlation_matrix.png"
    if corr.exists():
        try:
            plots.append(str(corr.relative_to(ROOT)))
        except ValueError:
            plots.append(str(corr))
    return plots


def build_executive_summary(genre_bullets: List[str], runtime_bullets: List[str],
                            people_bullets: List[str]) -> List[str]:
    summary = []
    if genre_bullets:
        summary.append(f"Top genres by rating include: {', '.join(genre_bullets[:3])}.")
    if runtime_bullets:
        summary.append(f"Best-performing runtimes cluster around: {', '.join(runtime_bullets[:3])}.")
    if people_bullets:
        summary.append(f"Strong influence observed from: {', '.join(people_bullets[:3])}.")
    if not summary:
        summary.append("Summary data present; see detailed findings below.")
    return summary


def build_recommendations_for_audience(genre_bullets: List[str], runtime_bullets: List[str]) -> List[str]:
    recs = []
    if genre_bullets:
        recs.append(f"Prioritize watching titles in: {', '.join(genre_bullets[:3])}.")
    if runtime_bullets:
        recs.append("Pick runtimes in the sweet spot: " + ", ".join(runtime_bullets[:3]) + ".")
    recs.append("Use ratings as a guide; start with the highest-rated titles in your preferred genres.")
    return recs


def build_recommendations_for_stakeholders(genre_bullets: List[str], runtime_bullets: List[str],
                                           people_bullets: List[str]) -> List[str]:
    recs = []
    if genre_bullets:
        recs.append("Commission/feature content in the highest-rated genres: " + ", ".join(genre_bullets[:3]) + ".")
    if runtime_bullets:
        recs.append("Target runtimes that over-index on rating to maximize completion and satisfaction: " +
                    ", ".join(runtime_bullets[:3]) + ".")
    if people_bullets:
        recs.append("Prioritize collaborations with high-performing directors/stars: " +
                    ", ".join(people_bullets[:3]) + ".")
    recs.append("Use the correlation matrix to validate attribute importance and refine acquisition priorities.")
    return recs


def append_section(lines: List[str], title: str, bullets: List[str]) -> None:
    lines.append(f"## {title}")
    lines.append("")
    if bullets:
        for b in bullets:
            lines.append(f"- {b}")
    else:
        lines.append("- No data available.")
    lines.append("")


def build_prompt(genre_bullets: List[str], runtime_bullets: List[str], people_bullets: List[str],
                 extras: Dict[str, pd.DataFrame], plot_refs: List[str], correlation_available: bool) -> str:
    lines = []
    lines.append("You are an analyst producing a concise, professional Markdown report for stakeholders and audiences.")
    lines.append("Use the supplied findings to write the full report in Markdown with these sections:")
    lines.append("- Executive Summary")
    lines.append("- Key Findings (with subsections for Genres, Runtime Trends, Director and Star Influence)")
    lines.append("- Correlations (reference the correlation_matrix.png if available; do not invent numbers)")
    lines.append("- Plot References (list the provided plot files)")
    lines.append("- Recommendations for Audiences")
    lines.append("- Recommendations for Streaming Stakeholders")
    lines.append("")
    lines.append("Findings to use (do not fabricate beyond what is provided):")
    lines.append(f"- Top genres: {', '.join(genre_bullets) if genre_bullets else 'None provided'}")
    lines.append(f"- Runtime trends: {', '.join(runtime_bullets) if runtime_bullets else 'None provided'}")
    lines.append(f"- People influence: {', '.join(people_bullets) if people_bullets else 'None provided'}")
    if correlation_available:
        lines.append("- Correlation matrix available at correlation_matrix.png")
    else:
        lines.append("- Correlation matrix not available")
    if extras:
        lines.append("- Additional CSV summaries:")
        for name, df in extras.items():
            lines.append(f"  - {name}: {len(df)} rows")
    else:
        lines.append("- No additional CSV summaries detected.")
    if plot_refs:
        lines.append("- Plot files:")
        for ref in plot_refs:
            lines.append(f"  - {ref}")
    else:
        lines.append("- No plot files detected.")
    lines.append("")
    lines.append("Constraints:")
    lines.append("- Keep tone concise and data-driven.")
    lines.append("- Do not invent metrics not provided.")
    lines.append("- Return only the final Markdown report content.")
    return "\n".join(lines)


def generate_report_text(genre_bullets: List[str], runtime_bullets: List[str], people_bullets: List[str],
                         extras: Dict[str, pd.DataFrame], plot_refs: List[str], correlation_available: bool,
                         model: str) -> str:
    if OpenAI is None:
        return ("LLM client not available. Install the openai package and set OPENAI_API_KEY "
                "to generate the Markdown report.")

    prompt = build_prompt(genre_bullets, runtime_bullets, people_bullets, extras, plot_refs, correlation_available)
    client = OpenAI()
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a concise, data-grounded reporting assistant."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


def main():
    known = load_known_csvs()
    extras = load_additional_outputs()

    genre_bullets = summarize_genres(known.get("genre")) if "genre" in known else []
    runtime_bullets = summarize_runtime(known.get("runtime")) if "runtime" in known else []
    people_bullets = summarize_people(known.get("people"), "director") + summarize_people(
        known.get("people"), "star"
    ) if "people" in known else []

    plot_refs = collect_plot_refs()
    correlation_available = (ROOT / "correlation_matrix.png").exists()

    model = "gpt-4o-mini"
    try:
        report_text = generate_report_text(
            genre_bullets,
            runtime_bullets,
            people_bullets,
            extras,
            plot_refs,
            correlation_available,
            model,
        )
    except Exception as e:
        report_text = f"Failed to generate LLM report: {e}"

    DEFAULT_REPORT.write_text(report_text, encoding="utf-8")
    print(f"Wrote {DEFAULT_REPORT} ({len(report_text.splitlines())} lines from LLM response).")


if __name__ == "__main__":
    main()
