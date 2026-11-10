# Brand Performance Prediction using Social Media Sentiment

A machine learning project that monitors social media comments for Pakistani fashion brands and predicts whether a brand's engagement will go **UP**, **DOWN**, or stay **STABLE** in the following month.

---

## Project Goal

Brands want to know how they are perceived online and where they are heading. This project combines:

- **Sentiment** extracted from customer comments (Roman Urdu + English)
- **Engagement metrics** (likes and shares)

to forecast next-month brand performance using a **Random Forest classifier**.

---

## Dataset

| Property | Value |
|----------|-------|
| Rows | 10,600 |
| Brands | 17 (e.g. Khaadi, Zellbury, Outfitters, Alkaram Studio, Agha Noor, ...) |
| Time span | January 2024 – December 2024 (12 months) |
| Platforms | Instagram, Twitter-X, Facebook, Daraz.pk, YouTube |

**Columns**

| Column | Description |
|--------|-------------|
| `Brand` | Brand name |
| `Brand Category` | Category of the brand (e.g. Youth Fashion) |
| `Platform` | Social media platform |
| `Date` | Date of the post / comment |
| `Comment Review` | Customer comment (Roman Urdu / English) |
| `Shares` | Number of shares |
| `Likes` | Number of likes |
| `Collection` | Product collection (e.g. Winter Khaddar 2024) |

> **Note:** The data file is named `Sentiment_project.xls` but is actually a CSV file. Load it with `pd.read_csv()`, not `pd.read_excel()`.

> **Data quality note:** The `Platform` column contains many username-like values in addition to the 5 real platforms. These are not used as a feature in the final pipeline.

---

## Methodology

```
Raw comments
    |
    v
Sentiment labeling (positive / neutral / negative)
    |
    v
Monthly aggregation per brand
(avg likes, avg shares, positive ratio, negative ratio, sentiment score, engagement score)
    |
    v
Target creation: compare next month's engagement with current month
    > +5%  -> UP
    < -5%  -> DOWN
    else   -> STABLE
    |
    v
Time-based split (train: Jan–Oct, test: Nov–Dec)
    |
    v
Random Forest (class_weight='balanced')
    |
    v
Predicted trend per brand
```

### 1. Sentiment Labeling
Each comment is labeled positive, negative or neutral using polarity scoring (TextBlob, threshold ±0.05). The script also contains a Roman Urdu + English word-list (lexicon) labeler, since TextBlob is trained on English only.

### 2. Monthly Aggregation
Comments are grouped by `(brand, month)`. Each row in the final model dataset represents one brand in one month.

### 3. Features

| Feature | Meaning |
|---------|---------|
| `avg_likes` | Average likes in the month |
| `avg_shares` | Average shares in the month |
| `total_posts` | Number of posts in the month |
| `pos_ratio` | Share of positive comments |
| `neg_ratio` | Share of negative comments |
| `sentiment_score` | `pos_ratio - neg_ratio` |
| `engagement_score` | `avg_likes + avg_shares` |
| `brand_enc` | Encoded brand identity |

### 4. Model
`RandomForestClassifier` with 200 trees, `max_depth=8`, `class_weight='balanced'`.

### 5. Validation
A **time-based split** is used (train on the first 10 months, test on the last 2) to simulate real future prediction and avoid look-ahead bias.

---

## Results

> Replace this section with your own output after running the script.

| Metric | Value |
|--------|-------|
| Train accuracy | _fill in_ |
| Test accuracy | _fill in_ |
| Macro F1-score | _fill in_ |

Example output of the model: a list of **UP**, **DOWN** and **STABLE** brands for the test months.

---

## Installation

```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
pip install -r requirements.txt
```

**requirements.txt**
```
pandas
numpy
scikit-learn
scipy
textblob
```

If you use TextBlob, also run:
```bash
python -m textblob.download_corpora
```

---

## Usage

1. Place the dataset in the project folder as `Sentiment_project.xls`.
2. Run:

```bash
python brand_performance_prediction.py
```

The script prints the dataset summary, sentiment distribution, evaluation metrics, a confusion matrix, per-brand predictions and feature importances.

---

## Project Structure

```
.
├── brand_performance_prediction.py   # Main pipeline
├── Sentiment_project.xls             # Dataset (CSV format)
├── requirements.txt
└── README.md
```

---

## Limitations

- **Small time window:** only 12 months of data, so there are few training samples after monthly aggregation (about 190 brand-month rows).
- **Weak labels:** sentiment labels come from TextBlob / a word-list, not human annotation. Accuracy on Roman Urdu text is limited.
- **Trend target:** the UP / DOWN / STABLE label is derived from engagement itself, so results should be read as short-term trend indication, not guaranteed forecasts.
- **Class imbalance:** Khaadi has about 5,200 rows while most other brands have about 360.
- **Single split:** with so little data, results on a 2-month test set can vary; cross-validation by time (rolling windows) is a recommended next step.

---

## Future Work

- Manually label a sample of comments to validate the sentiment labels
- Use a multilingual / Roman Urdu transformer model for sentiment (e.g. XLM-R)
- Add lag features (previous 2–3 months) and rolling averages
- Try Gradient Boosting / XGBoost and compare with Random Forest
- Build a dashboard for brand monitoring

---

## Tech Stack

Python · Pandas · NumPy · Scikit-learn · TextBlob

---

## License

This project is released under the MIT License.
