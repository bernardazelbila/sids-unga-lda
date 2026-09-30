#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ============================================================
# SIDS UNGA CLIMATE DISCOURSE ANALYSIS
#
# Workflow:
#   Part A. Sentence segmentation and annual climate-sentence counts
#   Part B. LDA topic modelling
#   Part C. Topic and theme assignment
#   Part D. Theme distribution and time-trend analysis
#   Part E. Export results
# ============================================================


# ============================================================
# 0. IMPORT LIBRARIES
# ============================================================

import os
import re

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

from gensim import corpora
from gensim.models import LdaModel, CoherenceModel

from scipy.stats import linregress


# ============================================================
# 1. FILE PATHS AND OUTPUT FOLDERS
# ============================================================

BASE_FOLDER = "/Users/user/Desktop/Other Docs/UN/Small Island developing states"
LDA_OUTPUT_FOLDER = "/Users/user/Desktop/Other Docs/UN/LDA Analysis"

os.makedirs(LDA_OUTPUT_FOLDER, exist_ok=True)

# File used for sentence-level annual counts
SENTENCE_INPUT_FILE = os.path.join(
    BASE_FOLDER,
    "SIDS_UNGA_climate_filtered_corpus.xlsx"
)

# File used for LDA analysis
LDA_INPUT_FILE = os.path.join(
    BASE_FOLDER,
    "SIDS_UNGA_climate_filtered_corpus_states_only.xlsx"
)

# Sentence-analysis output
SENTENCE_OUTPUT_FILE = os.path.join(
    BASE_FOLDER,
    "SIDS_UNGA_climate_sentences_by_year.xlsx"
)

# Main LDA/theme-analysis output
LDA_RESULTS_FILE = os.path.join(
    LDA_OUTPUT_FOLDER,
    "results.xlsx"
)

TOPICS_KEYWORDS_FILE = os.path.join(
    LDA_OUTPUT_FOLDER,
    "Topics_Keywords_Table.xlsx"
)

TREND_RESULTS_FILE = os.path.join(
    LDA_OUTPUT_FOLDER,
    "SIDS_theme_trend_analysis_results.xlsx"
)


# ============================================================
# 2. NLTK RESOURCES
# ============================================================

def ensure_nltk_resource(resource_path, download_name):
    """Download an NLTK resource only if it is not already available."""
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(download_name)


ensure_nltk_resource("tokenizers/punkt", "punkt")
ensure_nltk_resource("corpora/stopwords", "stopwords")

# Some newer NLTK versions require punkt_tab
try:
    ensure_nltk_resource("tokenizers/punkt_tab", "punkt_tab")
except Exception:
    pass


# ============================================================
# PART A. SENTENCE SEGMENTATION AND ANNUAL COUNTS
# ============================================================

# ============================================================
# 3. LOAD AND CLEAN DATA FOR SENTENCE ANALYSIS
# ============================================================

sentence_source_df = pd.read_excel(SENTENCE_INPUT_FILE)

print("\n" + "=" * 70)
print("SENTENCE-LEVEL CORPUS ANALYSIS")
print("=" * 70)
print(f"Rows loaded: {len(sentence_source_df):,}")
print("Columns:")
print(sentence_source_df.columns.tolist())

required_sentence_columns = ["Year", "Cleaned_Speech_Text"]

missing_columns = [
    col for col in required_sentence_columns
    if col not in sentence_source_df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required column(s) for sentence analysis: {missing_columns}"
    )

sentence_source_df["Year"] = pd.to_numeric(
    sentence_source_df["Year"],
    errors="coerce"
)

sentence_source_df = sentence_source_df.dropna(
    subset=["Year", "Cleaned_Speech_Text"]
).copy()

sentence_source_df["Year"] = sentence_source_df["Year"].astype(int)

sentence_source_df["Cleaned_Speech_Text"] = (
    sentence_source_df["Cleaned_Speech_Text"]
    .astype(str)
    .str.strip()
)

sentence_source_df = sentence_source_df[
    sentence_source_df["Cleaned_Speech_Text"].str.len() > 0
].copy()


# ============================================================
# 4. SEGMENT SPEECHES INTO SENTENCES
# ============================================================

def segment_sentences(text):
    """Segment text into sentences and remove empty segments."""
    return [
        sentence.strip()
        for sentence in sent_tokenize(text)
        if sentence.strip()
    ]


sentence_source_df["Sentence"] = (
    sentence_source_df["Cleaned_Speech_Text"]
    .apply(segment_sentences)
)

sentence_df = sentence_source_df.explode(
    "Sentence",
    ignore_index=True
)

sentence_df = sentence_df.dropna(
    subset=["Sentence"]
).copy()

sentence_df["Sentence"] = (
    sentence_df["Sentence"]
    .astype(str)
    .str.strip()
)

sentence_df = sentence_df[
    sentence_df["Sentence"].str.len() > 0
].copy()

sentence_df.insert(
    0,
    "Sentence_ID",
    range(1, len(sentence_df) + 1)
)


# ============================================================
# 5. CALCULATE ANNUAL SENTENCE COUNTS
# ============================================================

yearly_sentence_counts = (
    sentence_df
    .groupby("Year")
    .size()
    .reset_index(name="Number_of_Sentences")
    .sort_values("Year")
    .reset_index(drop=True)
)

total_sentences = yearly_sentence_counts[
    "Number_of_Sentences"
].sum()

yearly_sentence_counts["Percentage_of_Total"] = (
    yearly_sentence_counts["Number_of_Sentences"]
    / total_sentences
    * 100
).round(2)

print("\n" + "=" * 70)
print("CLIMATE-RELATED SENTENCE COUNTS BY YEAR")
print("=" * 70)
print(yearly_sentence_counts.to_string(index=False))

print("\n" + "=" * 70)
print(f"Total source rows analysed: {len(sentence_source_df):,}")
print(f"Total sentences identified: {len(sentence_df):,}")
print("=" * 70)


# ============================================================
# 6. SAVE SENTENCE-LEVEL RESULTS
# ============================================================

with pd.ExcelWriter(
    SENTENCE_OUTPUT_FILE,
    engine="openpyxl"
) as writer:

    yearly_sentence_counts.to_excel(
        writer,
        sheet_name="Sentence_Counts_by_Year",
        index=False
    )

    sentence_df.to_excel(
        writer,
        sheet_name="Sentence_Level_Corpus",
        index=False
    )

print(f"\nSentence-level results saved to:\n{SENTENCE_OUTPUT_FILE}")


# ============================================================
# 7. PLOT ANNUAL CLIMATE-SENTENCE TRENDS
# ============================================================

years = yearly_sentence_counts["Year"]

# 7A. Number of climate-related sentences
plt.figure(figsize=(12, 6))

plt.plot(
    yearly_sentence_counts["Year"],
    yearly_sentence_counts["Number_of_Sentences"],
    marker="o",
    linewidth=2,
    markersize=4
)

plt.xlabel("Year", fontsize=12)
plt.ylabel("Number of Climate-Related Sentences", fontsize=12)
plt.title(
    "Annual Number of Climate-Related Sentences in SIDS UNGA Speeches",
    fontsize=14
)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.4
)

plt.xticks(
    range(years.min(), years.max() + 1, 5),
    rotation=45
)

plt.tight_layout()

sentence_count_graph = os.path.join(
    BASE_FOLDER,
    "SIDS_climate_sentence_counts_by_year.png"
)

plt.savefig(
    sentence_count_graph,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# 7B. Annual share of the climate-filtered corpus
plt.figure(figsize=(12, 6))

plt.plot(
    yearly_sentence_counts["Year"],
    yearly_sentence_counts["Percentage_of_Total"],
    marker="o",
    linewidth=2,
    markersize=4
)

plt.xlabel("Year", fontsize=12)
plt.ylabel("Percentage of Total Climate-Related Sentences (%)", fontsize=12)
plt.title(
    "Annual Share of Climate-Related Sentences in SIDS UNGA Speeches",
    fontsize=14
)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.4
)

plt.xticks(
    range(years.min(), years.max() + 1, 5),
    rotation=45
)

plt.tight_layout()

percentage_graph = os.path.join(
    BASE_FOLDER,
    "SIDS_climate_percentage_by_year.png"
)

plt.savefig(
    percentage_graph,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()

print("\nSentence graphs saved:")
print(f"1. {sentence_count_graph}")
print(f"2. {percentage_graph}")


# ============================================================
# PART B. LDA TOPIC MODELLING
# ============================================================

# ============================================================
# 8. LOAD DATA FOR LDA
# ============================================================

df = pd.read_excel(LDA_INPUT_FILE)

print("\n" + "=" * 70)
print("LDA TOPIC MODELLING")
print("=" * 70)
print("Columns in dataset:")
print(df.columns.tolist())

required_lda_columns = ["Year", "Cleaned_Speech_Text"]

missing_columns = [
    col for col in required_lda_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required column(s) for LDA analysis: {missing_columns}"
    )

df["Year"] = pd.to_numeric(
    df["Year"],
    errors="coerce"
)

df = df.dropna(
    subset=["Year", "Cleaned_Speech_Text"]
).copy()

df["Year"] = df["Year"].astype(int)


# ============================================================
# 9. PREPROCESS TEXT
# ============================================================

stop_words = set(stopwords.words("english"))

custom_stopwords = {
    "united", "nations", "general", "assembly", "session",
    "president", "mr", "madam", "world", "international",
    "country", "countries", "people", "must", "also",
    "would", "could", "shall", "today", "year", "years"
}

stop_words.update(custom_stopwords)


def preprocess(text):
    """Clean and tokenize text for LDA modelling."""
    if pd.isna(text):
        return []

    text = str(text).lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = word_tokenize(text)

    tokens = [
        word
        for word in tokens
        if word not in stop_words and len(word) > 3
    ]

    return tokens


df["tokens"] = df["Cleaned_Speech_Text"].apply(preprocess)

df = df[
    df["tokens"].map(len) > 0
].copy()

print(f"\nNumber of documents after preprocessing: {len(df):,}")


# ============================================================
# 10. CREATE DICTIONARY AND CORPUS
# ============================================================

dictionary = corpora.Dictionary(df["tokens"])

dictionary.filter_extremes(
    no_below=10,
    no_above=0.5
)

corpus = [
    dictionary.doc2bow(tokens)
    for tokens in df["tokens"]
]

print(f"Number of terms in dictionary: {len(dictionary):,}")
print(f"Number of documents in corpus: {len(corpus):,}")


# ============================================================
# 11. EVALUATE NUMBER OF TOPICS (K)
# ============================================================

k_range = range(5, 31)

coherence_scores = []
log_perplexity_scores = []

for k in k_range:

    print(f"Training LDA model with K={k}...")

    lda_model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=k,
        random_state=42,
        passes=10
    )

    coherence_model = CoherenceModel(
        model=lda_model,
        texts=df["tokens"],
        dictionary=dictionary,
        coherence="c_v"
    )

    coherence = coherence_model.get_coherence()
    log_perplexity = lda_model.log_perplexity(corpus)

    coherence_scores.append(coherence)
    log_perplexity_scores.append(log_perplexity)

    print(
        f"K={k} | "
        f"Coherence={coherence:.4f} | "
        f"Log Perplexity={log_perplexity:.4f}"
    )


# ============================================================
# 12. SELECT K BASED ON HIGHEST COHERENCE
# ============================================================

k_results_df = pd.DataFrame({
    "K": list(k_range),
    "Coherence": coherence_scores,
    "Log_Perplexity": log_perplexity_scores
})

optimal_k = list(k_range)[np.argmax(coherence_scores)]
best_coherence = max(coherence_scores)

print("\n" + "=" * 70)
print("K EVALUATION")
print("=" * 70)
print(k_results_df.to_string(index=False))

print(
    f"\nSelected K based on highest coherence score: {optimal_k}"
)
print(
    f"Highest coherence score: {best_coherence:.4f}"
)


# ============================================================
# 13. PLOT COHERENCE AND LOG PERPLEXITY
# ============================================================

fig, axes = plt.subplots(
    1,
    2,
    figsize=(16, 6)
)

# Panel A: c_v coherence
axes[0].plot(
    list(k_range),
    coherence_scores,
    marker="o",
    linewidth=2
)

axes[0].set_xlabel(
    "Number of Topics (K)",
    fontsize=12
)

axes[0].set_ylabel(
    "Coherence Score (c_v)",
    fontsize=12
)

axes[0].set_title(
    "A. Topic Coherence",
    fontsize=14
)

axes[0].set_xticks(
    list(k_range)
)

axes[0].tick_params(
    axis="x",
    rotation=45
)

axes[0].grid(
    True,
    alpha=0.3
)

# Panel B: log perplexity
axes[1].plot(
    list(k_range),
    log_perplexity_scores,
    marker="o",
    linewidth=2
)

axes[1].set_xlabel(
    "Number of Topics (K)",
    fontsize=12
)

axes[1].set_ylabel(
    "Log Perplexity",
    fontsize=12
)

axes[1].set_title(
    "B. Log Perplexity",
    fontsize=14
)

axes[1].set_xticks(
    list(k_range)
)

axes[1].tick_params(
    axis="x",
    rotation=45
)

axes[1].grid(
    True,
    alpha=0.3
)

plt.tight_layout()

k_diagnostics_graph = os.path.join(
    LDA_OUTPUT_FOLDER,
    "LDA_K_diagnostics.png"
)

plt.savefig(
    k_diagnostics_graph,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 14. TRAIN FINAL LDA MODEL
# ============================================================

final_lda = LdaModel(
    corpus=corpus,
    id2word=dictionary,
    num_topics=optimal_k,
    random_state=42,
    passes=20
)


# ============================================================
# 15. EXTRACT TOPIC TERMS AND KEYWORDS
# ============================================================

# 15A. Detailed topic-term table
topic_rows = []

for topic_id in range(optimal_k):

    terms = final_lda.show_topic(
        topic_id,
        topn=15
    )

    for rank, (term, weight) in enumerate(
        terms,
        start=1
    ):
        topic_rows.append({
            "Topic": topic_id,
            "Rank": rank,
            "Term": term,
            "Weight": weight
        })

topic_terms_df = pd.DataFrame(topic_rows)


# 15B. Top keywords in compact format
top_n_keywords = 10

topic_keyword_rows = []

for topic_id in range(optimal_k):

    topic_terms = final_lda.show_topic(
        topic_id,
        topn=top_n_keywords
    )

    keywords = [
        term
        for term, weight in topic_terms
    ]

    weights = [
        weight
        for term, weight in topic_terms
    ]

    topic_keyword_rows.append({
        "Topic": topic_id,
        "Top_Keywords": "; ".join(keywords),
        "Keyword_Weights": "; ".join(
            f"{weight:.4f}"
            for weight in weights
        )
    })

topics_keywords_df = pd.DataFrame(
    topic_keyword_rows
)

print("\n" + "=" * 70)
print("TOPICS AND KEYWORDS")
print("=" * 70)

for _, row in topics_keywords_df.iterrows():
    print(f"\nTopic {row['Topic']}:")
    print(row["Top_Keywords"])

topics_keywords_df.to_excel(
    TOPICS_KEYWORDS_FILE,
    index=False
)

print(
    f"\nTopics and keywords saved to:\n{TOPICS_KEYWORDS_FILE}"
)


# ============================================================
# PART C. TOPIC AND THEME ASSIGNMENT
# ============================================================

# ============================================================
# 16. ASSIGN DOMINANT TOPIC TO EACH DOCUMENT
# ============================================================

def get_dominant_topic_and_prob(bow):
    """Return the topic with the highest probability for a document."""
    topics = final_lda.get_document_topics(
        bow,
        minimum_probability=0
    )

    return max(
        topics,
        key=lambda item: item[1]
    )


dominant_results = [
    get_dominant_topic_and_prob(bow)
    for bow in corpus
]

df["Dominant_Topic"] = [
    result[0]
    for result in dominant_results
]

df["Dominant_Topic_Probability"] = [
    result[1]
    for result in dominant_results
]


# ============================================================
# 17. CALCULATE CORPUS-LEVEL TOPIC PERCENTAGES
# ============================================================

topic_totals = np.zeros(
    final_lda.num_topics
)

for bow in corpus:

    document_topics = final_lda.get_document_topics(
        bow,
        minimum_probability=0
    )

    for topic_id, probability in document_topics:
        topic_totals[topic_id] += probability

topic_distribution_df = pd.DataFrame({
    "Topic": range(final_lda.num_topics),
    "Percentage": (
        topic_totals
        / topic_totals.sum()
        * 100
    )
})


# ============================================================
# 18. ASSIGN TOPICS TO MACRO THEMES
# ============================================================

topic_theme_map = {
    0: "Climate Impacts and Vulnerability",
    2: "Climate Impacts and Vulnerability",
    6: "Climate Impacts and Vulnerability",
    8: "Climate Impacts and Vulnerability",

    1: "Governance and Policy Response",
    3: "Governance and Policy Response",
    4: "Governance and Policy Response",

    5: "Socioeconomic Dimensions of Climate Change",
    7: "Socioeconomic Dimensions of Climate Change"
}

df["Theme"] = (
    df["Dominant_Topic"]
    .map(topic_theme_map)
)

unmapped_topics = sorted(
    df.loc[
        df["Theme"].isna(),
        "Dominant_Topic"
    ]
    .dropna()
    .unique()
    .tolist()
)

if unmapped_topics:
    print(
        "\nWarning: The following dominant topics "
        f"have no theme mapping: {unmapped_topics}"
    )


# ============================================================
# PART D. THEME DISTRIBUTION AND TIME-TREND ANALYSIS
# ============================================================

# ============================================================
# 19. THEME DISTRIBUTION
# ============================================================

theme_distribution_df = (
    df["Theme"]
    .value_counts()
    .reset_index()
)

theme_distribution_df.columns = [
    "Theme",
    "Frequency"
]

theme_distribution_df["Percentage"] = (
    theme_distribution_df["Frequency"]
    / theme_distribution_df["Frequency"].sum()
    * 100
).round(2)

print("\n" + "=" * 70)
print("THEME DISTRIBUTION")
print("=" * 70)
print(theme_distribution_df.to_string(index=False))


# ============================================================
# 20. PLOT THEME DISTRIBUTION
# ============================================================

# 20A. Bar chart
plt.figure(figsize=(10, 6))

plt.bar(
    theme_distribution_df["Theme"],
    theme_distribution_df["Percentage"]
)

plt.xlabel("Theme")
plt.ylabel("Percentage (%)")
plt.title("Distribution of Themes Across the Corpus")
plt.xticks(rotation=30, ha="right")
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

theme_bar_graph = os.path.join(
    LDA_OUTPUT_FOLDER,
    "Theme_distribution_bar.png"
)

plt.savefig(
    theme_bar_graph,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# 20B. Pie chart
plt.figure(figsize=(8, 8))

plt.pie(
    theme_distribution_df["Percentage"],
    labels=theme_distribution_df["Theme"],
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Percentage Distribution of Themes")
plt.tight_layout()

theme_pie_graph = os.path.join(
    LDA_OUTPUT_FOLDER,
    "Theme_distribution_pie.png"
)

plt.savefig(
    theme_pie_graph,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# 21. CALCULATE ANNUAL THEME DISTRIBUTION
# ============================================================

theme_by_year_percent = pd.crosstab(
    df["Year"],
    df["Theme"],
    normalize="index"
) * 100

theme_by_year_percent = (
    theme_by_year_percent
    .sort_index()
)


# ============================================================
# 22. LINEAR TIME-TREND ANALYSIS
# ============================================================

trend_results = []

x = (
    theme_by_year_percent
    .index
    .astype(int)
    .values
)

for theme in theme_by_year_percent.columns:

    y = theme_by_year_percent[
        theme
    ].values

    slope, intercept, r_value, p_value, std_error = (
        linregress(x, y)
    )

    # Approximate 95% confidence interval for slope
    ci_lower = slope - (1.96 * std_error)
    ci_upper = slope + (1.96 * std_error)

    trend_results.append({
        "Theme": theme,
        "Slope": slope,
        "SE": std_error,
        "CI_Lower": ci_lower,
        "CI_Upper": ci_upper,
        "R_squared": r_value ** 2,
        "p_value": p_value
    })

theme_trend_results_df = pd.DataFrame(
    trend_results
)

# Add interpretation columns
theme_trend_results_df["Trend"] = np.where(
    theme_trend_results_df["Slope"] > 0,
    "Increasing",
    np.where(
        theme_trend_results_df["Slope"] < 0,
        "Decreasing",
        "Stable"
    )
)

theme_trend_results_df["Significant"] = np.where(
    theme_trend_results_df["p_value"] < 0.05,
    "Yes",
    "No"
)

theme_trend_results_df = (
    theme_trend_results_df
    .sort_values("Theme")
    .reset_index(drop=True)
)

# Save unformatted numerical results
theme_trend_results_df.to_excel(
    TREND_RESULTS_FILE,
    index=False
)


# ============================================================
# 23. DISPLAY ANNUAL THEME AND TREND RESULTS
# ============================================================

theme_by_year_display = (
    theme_by_year_percent
    .round(2)
    .reset_index()
)

print("\n" + "=" * 70)
print("ANNUAL THEME DISTRIBUTION (%)")
print("=" * 70)
print(
    theme_by_year_display.to_string(
        index=False
    )
)

trend_display_df = (
    theme_trend_results_df
    .copy()
)

for column in [
    "Slope",
    "SE",
    "CI_Lower",
    "CI_Upper",
    "R_squared"
]:
    trend_display_df[column] = (
        trend_display_df[column]
        .round(4)
    )

trend_display_df["p_value"] = (
    trend_display_df["p_value"]
    .apply(
        lambda p:
        "< .001"
        if p < 0.001
        else f"{p:.3f}"
    )
)

print("\n" + "=" * 70)
print("LINEAR TIME-TREND ANALYSIS")
print("=" * 70)
print(
    trend_display_df.to_string(
        index=False
    )
)


# ============================================================
# 24. PLOT THEME TRENDS OVER TIME
# ============================================================

plt.figure(figsize=(14, 8))

for theme in theme_by_year_percent.columns:

    plt.plot(
        theme_by_year_percent.index,
        theme_by_year_percent[theme],
        marker="o",
        linewidth=2,
        markersize=4,
        label=str(theme)
    )

plt.xlabel(
    "Year",
    fontsize=12
)

plt.ylabel(
    "Percentage of Climate-Related Sentences (%)",
    fontsize=12
)

plt.title(
    "Temporal Distribution of Climate Change Themes in SIDS UNGA Speeches",
    fontsize=14
)

theme_years = (
    theme_by_year_percent
    .index
    .astype(int)
)

plt.xticks(
    range(
        theme_years.min(),
        theme_years.max() + 1,
        5
    ),
    rotation=45
)

plt.grid(
    axis="y",
    linestyle="--",
    alpha=0.3
)

plt.legend(
    title="Theme",
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    frameon=False
)

plt.tight_layout()

theme_trend_graph = os.path.join(
    LDA_OUTPUT_FOLDER,
    "Theme_trends_over_time.png"
)

plt.savefig(
    theme_trend_graph,
    dpi=300,
    bbox_inches="tight"
)

plt.show()
plt.close()


# ============================================================
# PART E. INDEX THEMES, EXTRACT EXCERPTS, AND SAVE OUTPUT
# ============================================================

# ============================================================
# 25. CREATE DATASET WITH TOPICS AND THEMES
# ============================================================

indexed_theme_df = df.copy()

preferred_columns = [
    "Year",
    "Country",
    "ISO Code",
    "Cleaned_Speech_Text",
    "Dominant_Topic",
    "Dominant_Topic_Probability",
    "Theme"
]

existing_columns = [
    column
    for column in preferred_columns
    if column in indexed_theme_df.columns
]

indexed_theme_df = (
    indexed_theme_df[
        existing_columns
    ]
)


# ============================================================
# 26. EXTRACT ILLUSTRATIVE EXCERPTS
# ============================================================

excerpt_source_col = "Cleaned_Speech_Text"

illustrative_excerpts_df = (
    indexed_theme_df
    .dropna(
        subset=[
            "Theme",
            excerpt_source_col
        ]
    )
    .sort_values(
        by=[
            "Theme",
            "Dominant_Topic_Probability"
        ],
        ascending=[
            True,
            False
        ]
    )
    .groupby(
        "Theme",
        group_keys=False
    )
    .head(5)
    .reset_index(drop=True)
)

illustrative_excerpts_df["Excerpt_No"] = (
    illustrative_excerpts_df
    .groupby("Theme")
    .cumcount()
    + 1
)

excerpt_columns = [
    "Theme",
    "Excerpt_No",
    "Year",
    "Country",
    "ISO Code",
    "Dominant_Topic",
    "Dominant_Topic_Probability",
    excerpt_source_col
]

excerpt_columns = [
    column
    for column in excerpt_columns
    if column in illustrative_excerpts_df.columns
]

illustrative_excerpts_df = (
    illustrative_excerpts_df[
        excerpt_columns
    ]
)


# ============================================================
# 27. SAVE ALL LDA AND THEME RESULTS TO ONE EXCEL WORKBOOK
# ============================================================

with pd.ExcelWriter(
    LDA_RESULTS_FILE,
    engine="openpyxl"
) as writer:

    k_results_df.to_excel(
        writer,
        sheet_name="K_Evaluation",
        index=False
    )

    topic_terms_df.to_excel(
        writer,
        sheet_name="Topic_Terms",
        index=False
    )

    topics_keywords_df.to_excel(
        writer,
        sheet_name="Topics_Keywords",
        index=False
    )

    topic_distribution_df.to_excel(
        writer,
        sheet_name="Topic_Distribution",
        index=False
    )

    theme_distribution_df.to_excel(
        writer,
        sheet_name="Theme_Distribution",
        index=False
    )

    theme_by_year_percent.to_excel(
        writer,
        sheet_name="Theme_by_Year"
    )

    theme_trend_results_df.to_excel(
        writer,
        sheet_name="Trends",
        index=False
    )

    indexed_theme_df.to_excel(
        writer,
        sheet_name="Dataset_with_Themes",
        index=False
    )

    illustrative_excerpts_df.to_excel(
        writer,
        sheet_name="Illustrative_Excerpts",
        index=False
    )


# ============================================================
# 28. FINAL OUTPUT SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)

print(f"\nMain LDA results workbook:\n{LDA_RESULTS_FILE}")
print(f"\nTopic keywords file:\n{TOPICS_KEYWORDS_FILE}")
print(f"\nTrend results file:\n{TREND_RESULTS_FILE}")

print("\nFigures:")
print(f"1. K diagnostics: {k_diagnostics_graph}")
print(f"2. Theme distribution bar chart: {theme_bar_graph}")
print(f"3. Theme distribution pie chart: {theme_pie_graph}")
print(f"4. Theme trends over time: {theme_trend_graph}")

print("\nSentence-analysis outputs:")
print(f"1. Excel workbook: {SENTENCE_OUTPUT_FILE}")
print(f"2. Sentence-count graph: {sentence_count_graph}")
print(f"3. Percentage graph: {percentage_graph}")
