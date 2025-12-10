# TV & Movie Analytics Report

### Audience & Stakeholder Insights

### Project: TV & Movie Analysis

### Team: Matas Orliukas, Ice Ybañez, Svitozar Menshchykov, Vladyslav Vovk

---

## Executive Summary

This report provides a data-driven analysis of TV and movie metadata, highlighting the factors that most strongly contribute to highly rated content. The study examines genre performance, runtime preferences, and the influence of directors and stars. The findings support both **audience decision-making** and **industry strategy**, helping stakeholders optimise content curation, recommendations, and acquisition choices.

All insights presented below reflect trends derived from the cleaned dataset and previously generated analytics scripts.

---

## Key Findings

### ⭐ Genre Performance

The genres with the highest average normalised ratings (0–1 scale) are:

| Genre           | Avg Rating |
| --------------- | ---------- |
| **Documentary** | 0.69       |
| **History**     | 0.67       |
| **News**        | 0.66       |
| **Talk-Show**   | 0.66       |
| **Biography**   | 0.66       |

**Insight:**  
Non-fiction genres such as _Documentary_ and _Biography_ consistently outperform entertainment genres. This suggests a strong audience appetite for educational, real-world, or knowledge-driven content.

---

### 🎬 Runtime Trends

The highest-rated runtime clusters are:

| Runtime (min) | Avg Rating |
| ------------- | ---------- |
| **98 min**    | 0.99       |
| **100 min**   | 0.90       |
| **69 min**    | 0.90       |
| **64 min**    | 0.89       |
| **80 min**    | 0.87       |

**Insight:**  
Feature-length films around **90–100 minutes** tend to achieve the highest ratings. Ultra-short runtimes (60–70 min) also show competitive performance, likely due to tighter pacing and stronger narrative focus.

---

### 🎥 Director Influence

Directors with the highest average ratings:

| Director             | Avg Rating | # Titles |
| -------------------- | ---------- | -------- |
| **Chuck Jones**      | 0.71       | 306      |
| **Martin Scorsese**  | 0.71       | 148      |
| **Alfred Hitchcock** | 0.68       | 121      |
| **David Fincher**    | 0.67       | 102      |
| **Steven Spielberg** | 0.67       | 89       |

**Insight:**  
High-performing directors maintain consistently strong ratings across large bodies of work, indicating that **director reputation is a powerful predictor of content success**.

---

### ⭐ Star Influence

Top stars by average rating:

| Star           | Avg Rating | # Titles |
| -------------- | ---------- | -------- |
| **Troy Baker** | 0.71       | 306      |
| **Moe Howard** | 0.71       | 148      |
| **Larry Fine** | 0.68       | 121      |
| **Steve Blum** | 0.67       | 102      |
| **Mel Blanc**  | 0.67       | 89       |

**Insight:**  
Stars known for voice acting and classic comedic roles appear among the highest performers, suggesting that specialised talent categories often correlate with higher audience approval.

---

## Correlation Analysis

A correlation matrix was generated to explore relationships between numeric variables such as runtime, votes, and ratings.  
While no extremely strong linear correlations were identified, the patterns support the earlier findings:

- **Runtime** shows a weak–moderate positive correlation with rating in the optimal range (90–100 min).
- **Genres and certifications** show category-driven rating differences rather than numeric correlations.
- **Star and director influence** is more categorical than numeric, best analysed through ranking rather than correlation.

---

## Visual References

The following plot files provide graphical summaries of the dataset:

- `Database/Images/Actor Ratings vs Number of Movies(Scatterplot).png`
- `Database/Images/Top 50 Actors by Average Rating (Above vs Below Global Average).png`
- `Database/Images/avg_rating_by_runtime.png`
- `Database/Images/director_combined_visualizations.png`
- `Database/Images/genre_avg_ratings_from_db.png`
- `Database/Images/genre_dashboard.png`
- `Database/Images/genre_rating_bar.png`
- `Database/Images/genre_rating_correlation_bar.png`
- `Database/Images/model_performance_comparison.png`
- `Database/Images/rating_vs_votes_scatter.png`
- `Database/Images/runtime_rating_scatterplot.png`
- `Database/Images/star_combined_visualizations.png`

---

## Recommendations for Audiences

1. **Explore non-fiction genres**, especially Documentary and Biography, as they consistently deliver high-quality, highly rated content.
2. When choosing a film, **select runtimes around 98–100 minutes** for the most engaging and well-received viewing experience.
3. Consider content created by high-performing directors such as **Scorsese, Hitchcock, Fincher, or Spielberg**, who show strong reliability across titles.
4. For animated or voice-driven content, actors such as **Troy Baker** and **Steve Blum** frequently contribute to higher audience satisfaction.

---

## Recommendations for Streaming Stakeholders

1. **Prioritise acquiring and promoting high-performing genres** — particularly Documentary, Biography, and History — as they demonstrate strong audience approval.
2. **Use renowned directors and stars in marketing campaigns**, since their influence positively correlates with content success.
3. **Optimise catalogue runtime distribution** by highlighting titles in the 90–110 minute range, which align best with viewer preferences.
4. Develop curated content sections such as:
   - _“Director Spotlight: Scorsese / Hitchcock / Spielberg”_
   - _“Top Documentaries of the Last Decade”_
   - _“Tight 90-Minute Films: Highly Rated & Easy to Watch”_
5. Consider these insights when making **content acquisition and recommendation system adjustments**, ensuring that viewers receive more personalised, high-performing suggestions.

---

## Conclusion

The analysis reveals clear patterns in genre preferences, runtime effectiveness, and the impact of directors and stars. These insights equip both audiences and streaming providers with actionable guidance for improving viewing experiences and strategic decision making.

---
