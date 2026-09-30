# SIDS UNGA Climate Discourse: LDA Analysis

Python workflow and a climate-filtered corpus for analysing climate discourse in Small Island Developing States (SIDS) speeches at the United Nations General Assembly (UNGA).

The supplied corpus contains **882 records spanning 1985–2025**. The workflow performs sentence segmentation, annual sentence counts, Latent Dirichlet Allocation (LDA) topic modelling, topic-to-theme assignment, and linear time-trend analysis.

## Repository contents

| File | Description |
| --- | --- |
| `SIDS_UNGA_LDA_analysis_reorganised(1).py` | Original analysis script, preserved byte-for-byte. |
| `SIDS_UNGA_climate_filtered_corpus.xlsx` | Original climate-filtered workbook, preserved byte-for-byte. |
| `requirements.txt` | Direct third-party dependencies identified from the script. |
| `DATA_DICTIONARY.md` | Workbook structure and column descriptions. |
| `CHECKSUMS.sha256` | SHA-256 checksums of the two original files. |
| `.gitignore` | Excludes local environments, caches, and generated analysis outputs. |
| `.gitattributes` | Prevents Git from changing the Python file's line endings. |

## Reproduction status

This package preserves the supplied research materials. **The complete analysis cannot run from these two input files alone.** The script also reads `SIDS_UNGA_climate_filtered_corpus_states_only.xlsx`, which was not supplied. This additional workbook must be obtained from the project author; it has not been generated or substituted with the attached corpus.

The script uses these fixed paths:

| Setting | Path in the original script |
| --- | --- |
| `BASE_FOLDER` | `/Users/user/Desktop/Other Docs/UN/Small Island developing states` |
| `LDA_OUTPUT_FOLDER` | `/Users/user/Desktop/Other Docs/UN/LDA Analysis` |

To execute the script without changing it, both input workbooks must be present in `BASE_FOLDER`, and the output locations must be writable. The script creates `LDA_OUTPUT_FOLDER` if necessary. Simply putting the files together in a cloned repository does not redirect these paths. No path changes, wrappers, or changes to the analysis have been made in this package.

## Dependencies and execution

Use Python 3. The original Python version and package versions were not supplied, so `requirements.txt` is an unpinned dependency list, not a validated reproduction environment.

From the repository directory, install dependencies in your Python environment:

```bash
python3 -m pip install -r requirements.txt
```

Once the additional workbook and the original directory layout are available, run:

```bash
python3 "SIDS_UNGA_LDA_analysis_reorganised(1).py"
```

The script checks for NLTK `punkt`, `stopwords`, and `punkt_tab` resources and attempts to download missing resources. Those downloads require internet access. It also displays Matplotlib figures during execution.

## Analysis implemented in the script

1. Read the supplied climate-filtered workbook, split `Cleaned_Speech_Text` into sentences, and calculate annual sentence counts and each year's share of the filtered sentence corpus.
2. Read the separate `states_only` workbook for LDA. Each retained row is one LDA document; the sentence table from step 1 is not used as the LDA input.
3. Lowercase text, remove characters outside `a–z` and whitespace, tokenize, remove English and custom stopwords, and retain tokens longer than three characters.
4. Filter the dictionary with `no_below=10` and `no_above=0.5`.
5. Evaluate K from 5 through 30 with 10 passes and `random_state=42`. Record `c_v` coherence and in-sample log perplexity; select K using the highest coherence.
6. Fit the final model with 20 passes and `random_state=42`; extract keywords, document-level dominant topics, and aggregate topic probabilities.
7. Map dominant topic IDs to three predefined themes, calculate theme distributions, fit annual linear trends, and export tables and figures.

The supplied theme mapping covers topic IDs 0–8. Because K is selected automatically, additional dominant topic IDs may remain unmapped. The script prints a warning for these IDs; theme summaries exclude unmapped records. Topic meanings and the predefined mapping should be interpreted in relation to the fitted model.

Annual sentence percentages use all climate-filtered sentences across years as the denominator; they are not the percentage of all UNGA speech content that concerns climate. Topic percentages aggregate document-topic probabilities, while theme percentages count mapped dominant-topic assignments.

## Generated outputs

Under `BASE_FOLDER`:

- `SIDS_UNGA_climate_sentences_by_year.xlsx`
- `SIDS_climate_sentence_counts_by_year.png`
- `SIDS_climate_percentage_by_year.png`

Under `LDA_OUTPUT_FOLDER`:

- `results.xlsx` — K evaluation, topic terms and keywords, topic and theme distributions, annual theme percentages, trend estimates, indexed records, and illustrative excerpts.
- `Topics_Keywords_Table.xlsx`
- `SIDS_theme_trend_analysis_results.xlsx`
- `LDA_K_diagnostics.png`
- `Theme_distribution_bar.png`
- `Theme_distribution_pie.png`
- `Theme_trends_over_time.png`

These outputs are not included in this package. Existing files at these output paths may be overwritten by a run.

## Uploading to GitHub

Suggested repository name: `sids-unga-climate-lda`

Suggested description: `LDA topic modelling and temporal analysis of climate discourse in SIDS UNGA speeches, with a climate-filtered corpus (1985–2025).`

Extract the ZIP and upload the contents of the `sids-unga-lda` folder to the root of your GitHub repository, including `.gitignore` and `.gitattributes`. Upload the extracted files rather than the ZIP so GitHub can display the README and code directly. No repository has been published by preparing this package.

## Provenance, licensing, and validation

The script and workbook are the original project materials supplied for this repository. The original corpus source citation, filtering procedure, redistribution terms, and a software license were not supplied. No license or publication citation has been invented; the project author should add those details when available.

Packaging validation confirmed Python syntax, inspected the workbook structure, and verified that both original files match their supplied bytes using SHA-256 checksums. The LDA analysis was not executed, and its outputs have not been independently reproduced.
