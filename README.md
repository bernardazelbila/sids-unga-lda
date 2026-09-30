# SIDS UNGA Climate Discourse: LDA Analysis

Python workflow and a climate-filtered corpus for analysing climate discourse in Small Island Developing States (SIDS) speeches at the United Nations General Assembly (UNGA).

The supplied corpus contains **882 records spanning 1985–2025**. The workflow performs sentence segmentation, annual sentence counts, Latent Dirichlet Allocation (LDA) topic modelling, topic-to-theme assignment, and linear time-trend analysis.

## Repository contents

| File | Description |
| --- | --- |
| `SIDS_UNGA_LDA_analysis_reorganised(1).py` | Original analysis script, preserved byte-for-byte. |
| `SIDS_UNGA_climate_filtered_corpus.xlsx` | Original climate-filtered workbook, preserved byte-for-byte. |
| `requirements.txt` | Direct third-party dependencies. |
| `DATA_DICTIONARY.md` | Workbook structure and column descriptions. |
| `.gitignore` | Excludes local environments, caches, and generated analysis outputs. |
| `.gitattributes` | Prevents Git from changing the Python file's line endings. |
