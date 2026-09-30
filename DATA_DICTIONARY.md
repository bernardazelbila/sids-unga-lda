# Corpus data dictionary

File: `SIDS_UNGA_climate_filtered_corpus.xlsx`

Worksheet: `Sheet1`. The workbook contains 882 data rows and nine columns. Observed years range from 1985 to 2025. Counts below describe the supplied workbook before the script's cleaning steps.

| Column | Observed type | Nonempty rows | Description |
| --- | --- | ---: | --- |
| `ID` | Integer | 882 | Source record identifier. |
| `ISO Code` | Text | 882 | Country code, for example `ATG` or `BHS`. |
| `Session` | Integer | 882 | UNGA session number recorded in the source. |
| `Country` | Text | 882 | Country name recorded in the source. |
| `Continent` | Text | 882 | Continent label recorded in the source. |
| `Post` | Text | 834 | Speaker's recorded position, for example Prime Minister; 48 cells are empty. |
| `Year` | Integer | 882 | Year associated with the record. |
| `Cleaned_Speech_Text` | Text | 882 | Supplied climate-filtered text; input for sentence segmentation. |
| `Standardized_SIDS_Name` | Text | 882 | Standardized SIDS name recorded in the source. |

Descriptions are based on column names, observed values, and how the script reads the workbook. An upstream codebook was not supplied. These are source records, not an asserted count of sentences or unique speeches.

The script requires `Year` and `Cleaned_Speech_Text` for both analysis inputs. It reads the first worksheet by default. For sentence analysis, it removes records with missing years or text and strips empty text before segmentation. 

The analysis script begins with already filtered text. It does not implement or document the upstream climate classifier or the creation of the `states_only` workbook.
