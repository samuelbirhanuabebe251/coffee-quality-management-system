
# Coffee Quality Management System - Phase 4: Data Analysis in Python

import warnings
warnings.filterwarnings("ignore")          # hides the harmless pandas/SQLAlchemy warning

import pandas as pd
import numpy as np
import mysql.connector
from sklearn.preprocessing import StandardScaler, LabelEncoder
import os
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.formula.api as smf
import getpass

#for my ML
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
from sklearn.metrics import r2_score, mean_absolute_error

# STEP 1: Load data from MySQL (SQL -> Python integration)
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=getpass.getpass("MySQL password: "),
    database="CoffeeQuality"
)

df = pd.read_sql("SELECT * FROM vw_sample_details", conn)
conn.close()

pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 20)

print("Shape (rows, columns):", df.shape)
print(df.head())

#second phase

# STEP 2: Inspect the dataset (Lecture 9 step 1 + Lecture 10 inspection)

# MySQL returns DECIMAL columns as text-like objects -> convert to numbers
num_cols = ["Altitude", "Aroma", "Flavor", "Acidity", "TotalCupPoints"]
df[num_cols] = df[num_cols].apply(pd.to_numeric, errors="coerce")

print("\n--- Structure: columns, types, non-null counts ---")
df.info()

print("\n--- Summary statistics (numerical columns) ---")
print(df.describe().round(2))

print("\n--- Missing values per column ---")
print(df.isnull().sum())

print("\n--- Duplicated samples (same SampleID) ---")
print(df["SampleID"].duplicated().sum())

print("\n--- Number of unique values per column ---")
print(df.nunique())

print("\n--- Harvest year formats (inconsistent!) ---")
print(df["HarvestYear"].value_counts().head(20))



# STEP 3: Data cleaning (Lecture 10)

clean = df.copy()               # work on a copy, keep the original df untouched
rows_before = len(clean)

# 3.1 Invalid values: a cup score of 0 is impossible
clean = clean[clean["TotalCupPoints"] > 0]

# 3.2 Impossible altitudes: coffee does not grow above ~3,000 m -> entry errors
print("\nImpossible altitudes found:", clean.loc[clean["Altitude"] > 5000, "Altitude"].tolist())
clean.loc[clean["Altitude"] > 5000, "Altitude"] = np.nan

# 3.3 Missing altitude: flag it first, then fill with the median
clean["AltitudeImputed"] = clean["Altitude"].isna()
clean["Altitude"] = clean["Altitude"].fillna(clean["Altitude"].median())

# 3.4 Inconsistent formats: take the first 4-digit year from the HarvestYear text
clean["Year"] = pd.to_numeric(
    clean["HarvestYear"].str.extract(r"(20\d{2})")[0], errors="coerce"
).astype("Int64")

# 3.5 Missing text values: fill with "Unknown" and remove extra spaces
for col in ["CountryName", "FarmName", "OwnerName"]:
    clean[col] = clean[col].fillna("Unknown").str.strip()

# 3.6 Duplicates
clean = clean.drop_duplicates(subset="SampleID")

# 3.7 Outliers: detect with the IQR rule
q1, q3 = clean["TotalCupPoints"].quantile([0.25, 0.75])
iqr = q3 - q1
low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
outliers = clean[(clean["TotalCupPoints"] < low) | (clean["TotalCupPoints"] > high)]

# ---- Cleaning report ----
print("\n--- Cleaning report ---")
print("Rows before:", rows_before, "| Rows after:", len(clean))
print("Altitude values imputed with median:", clean["AltitudeImputed"].sum())
print("Harvest years that could not be read:", clean["Year"].isna().sum())
print(f"Score outliers (outside {low:.2f} - {high:.2f}):", len(outliers))
print("\nClean years:\n", clean["Year"].value_counts().sort_index())
print("\nMissing values after cleaning:\n", clean.isnull().sum())

# STEP 4: Data transformation (Lecture 8 + 10)

# 4.1 Binning: altitude bands (only for REAL altitudes, not imputed ones)
real_alt = clean["Altitude"].where(~clean["AltitudeImputed"])
clean["AltitudeBand"] = pd.cut(
    real_alt, bins=[0, 1000, 1500, np.inf],
    labels=["Low (<1000 m)", "Medium (1000-1500 m)", "High (>1500 m)"]
)

# 4.2 Binning: quality grade (80 = official "specialty coffee" threshold)
clean["QualityGrade"] = pd.cut(
    clean["TotalCupPoints"], bins=[0, 80, 85, 100], right=False,
    labels=["Below specialty (<80)", "Very good (80-85)", "Excellent (85+)"]
)

# 4.3 Encoding: country name -> number (needed for ML models)
clean["CountryCode"] = LabelEncoder().fit_transform(clean["CountryName"])

# 4.4 Scaling: z-scores (mean 0, std 1) so different units are comparable
scale_cols = ["Altitude", "Aroma", "Flavor", "Acidity"]
clean[[c + "_z" for c in scale_cols]] = StandardScaler().fit_transform(clean[scale_cols])

# ---- Transformation report ----
print("\n--- Altitude bands ---")
print(clean["AltitudeBand"].value_counts(dropna=False))
print("\n--- Quality grades ---")
print(clean["QualityGrade"].value_counts())
print("\n--- Scaling check (z columns should have mean 0, std 1) ---")
print(clean[["Aroma", "Aroma_z", "Altitude", "Altitude_z"]].describe().round(2))

# 4.5 Save the clean dataset (goes in your project folder)
clean.to_csv("coffee_clean.csv", index=False)
print("\nSaved coffee_clean.csv with shape", clean.shape)



# STEP 5: Descriptive statistics (Lecture 9 step 2)

score_cols = ["Aroma", "Flavor", "Acidity", "TotalCupPoints"]

# 5.1 Center, spread and shape of the scores
print("\n--- 5.1 Summary of the scores ---")
print(clean[score_cols].agg(["mean", "median", "std", "min", "max", "skew"]).round(2))

# 5.2 Score by altitude band (only real altitudes)
print("\n--- 5.2 Score by altitude band ---")
print(clean.groupby("AltitudeBand", observed=True)["TotalCupPoints"]
      .agg(["count", "mean", "median", "std"]).round(2))

# 5.3 Score by country (at least 10 samples) = same as SQL Query 2
print("\n--- 5.3 Score by country (>= 10 samples) ---")
by_country = (clean[clean["CountryName"] != "Unknown"]
              .groupby("CountryName")["TotalCupPoints"]
              .agg(["count", "mean"])
              .query("count >= 10")
              .sort_values("mean", ascending=False)
              .round(2))
print(by_country)

# 5.4 Share of coffees in each quality grade (%)
print("\n--- 5.4 Quality grades (%) ---")
print(clean["QualityGrade"].value_counts(normalize=True).mul(100).round(1))

# 5.5 Score by harvest year
print("\n--- 5.5 Score by harvest year ---")
print(clean.groupby("Year")["TotalCupPoints"].agg(["count", "mean"]).round(2))



# STEP 6: Correlation analysis (Lecture 9 step 3)

os.makedirs("charts", exist_ok=True)           # folder for all saved charts

corr_cols = ["Altitude", "Aroma", "Flavor", "Acidity", "TotalCupPoints"]
corr_df = clean[corr_cols].copy()
corr_df["Altitude"] = real_alt                  # only REAL altitudes, no imputed ones
corr = corr_df.corr().round(2)

print("\n--- 6. Correlation matrix ---")
print(corr)

plt.figure(figsize=(7, 5))
sns.heatmap(corr, annot=True, cmap="coolwarm", vmin=-1, vmax=1, fmt=".2f")
plt.title("Correlation between altitude and cup scores")
plt.tight_layout()
plt.savefig("charts/01_correlation_heatmap.png", dpi=150)
plt.show()

# STEP 7: Visual exploration (Lecture 9 step 4)

mean_s = clean["TotalCupPoints"].mean()
median_s = clean["TotalCupPoints"].median()

# 7.1 Histogram: distribution of the total score
plt.figure(figsize=(8, 5))
sns.histplot(clean["TotalCupPoints"], bins=40, kde=True, color="saddlebrown")
plt.axvline(mean_s, color="red", linestyle="--", label=f"Mean = {mean_s:.2f}")
plt.axvline(median_s, color="green", label=f"Median = {median_s:.2f}")
plt.axvline(80, color="black", linestyle=":", label="Specialty threshold (80)")
plt.title("Distribution of total cup points")
plt.xlabel("Total cup points")
plt.ylabel("Number of samples")
plt.legend()
plt.tight_layout()
plt.savefig("charts/02_score_histogram.png", dpi=150)
plt.show()

# 7.2 Boxplot: score by altitude band
plt.figure(figsize=(8, 5))
sns.boxplot(data=clean.dropna(subset=["AltitudeBand"]),
            x="AltitudeBand", y="TotalCupPoints", color="tan")
plt.title("Cup score by altitude band")
plt.xlabel("Altitude band")
plt.ylabel("Total cup points")
plt.tight_layout()
plt.savefig("charts/03_score_by_altitude_boxplot.png", dpi=150)
plt.show()

# 7.3 Bar chart: average score by country (>= 10 samples, from Step 5)
bc = by_country.sort_values("mean")
plt.figure(figsize=(8, 6))
plt.barh(bc.index, bc["mean"], color="peru")
plt.axvline(mean_s, color="red", linestyle="--", label=f"Overall mean = {mean_s:.2f}")
plt.xlim(78, 86)        # axis zoomed in so the differences are visible
plt.title("Average cup score by country (countries with 10+ samples)")
plt.xlabel("Average total cup points (axis starts at 78)")
plt.legend()
plt.tight_layout()
plt.savefig("charts/04_score_by_country_bar.png", dpi=150)
plt.show()

# 7.4 Scatter + regression line: altitude vs score (real altitudes only)
plt.figure(figsize=(8, 5))
sns.regplot(x=real_alt, y=clean["TotalCupPoints"],
            scatter_kws={"alpha": 0.3, "s": 15}, line_kws={"color": "red"})
plt.title("Altitude vs total cup points (r = 0.15)")
plt.xlabel("Altitude (m)")
plt.ylabel("Total cup points")
plt.tight_layout()
plt.savefig("charts/05_altitude_vs_score_scatter.png", dpi=150)
plt.show()


# STEP 8: Statistical tests (Lecture 9 step 5)

# 8.1 t-test: do HIGH farms score differently from LOW farms?
high = clean.loc[clean["AltitudeBand"] == "High (>1500 m)", "TotalCupPoints"]
low = clean.loc[clean["AltitudeBand"] == "Low (<1000 m)", "TotalCupPoints"]
t_stat, p_val = stats.ttest_ind(high, low, equal_var=False)

print("\n--- 8.1 t-test: High vs Low altitude ---")
print(f"High: n = {len(high)}, mean = {high.mean():.2f}")
print(f"Low:  n = {len(low)}, mean = {low.mean():.2f}")
print(f"Difference = {high.mean() - low.mean():.2f} points")
print(f"t = {t_stat:.2f}, p-value = {p_val:.6f}")
if p_val < 0.05:
    print("Result: significant difference (p < 0.05) -> reject H0")
else:
    print("Result: no significant difference (p >= 0.05) -> cannot reject H0")

# 8.2 OLS regression: how much does the score change per 1,000 m?
reg_df = clean[~clean["AltitudeImputed"]].copy()      # real altitudes only
reg_df["AltitudeKm"] = reg_df["Altitude"] / 1000       # metres -> km (easier to read)
model = smf.ols("TotalCupPoints ~ AltitudeKm", data=reg_df).fit()

print("\n--- 8.2 OLS regression: TotalCupPoints ~ AltitudeKm ---")
print(model.summary())
print(f"\nEvery +1,000 m of altitude -> {model.params['AltitudeKm']:+.2f} points")
print(f"R-squared = {model.rsquared:.3f} -> altitude explains {model.rsquared*100:.1f}% of score variation")
print(f"p-value of altitude = {model.pvalues['AltitudeKm']:.6f}")





# STEP 9: Machine learning - predicting the cup score (optional)

ml = reg_df.copy()                         # coffees with REAL altitude (n = 1079)
y = ml["TotalCupPoints"]                   # what we want to predict

# Features A: origin only (known BEFORE tasting)
X_a = pd.get_dummies(ml[["AltitudeKm", "CountryName"]],
                     columns=["CountryName"], drop_first=True, dtype=int)
# Features B: tasting attributes (known only AFTER tasting)
X_b = ml[["Aroma", "Flavor", "Acidity"]]

def evaluate(name, model, X):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)          # 80% learn, 20% exam
    model.fit(X_train, y_train)                        # learn
    pred = model.predict(X_test)                       # predict unseen coffees
    print(f"{name:42s} R2 = {r2_score(y_test, pred):6.3f}   "
          f"MAE = {mean_absolute_error(y_test, pred):.2f} points")
    return y_test, pred

print("\n--- 9. Model comparison (on the 20% test set) ---")
evaluate("Baseline: always predict the average", DummyRegressor(), X_a)
evaluate("A1: Linear - altitude + country", LinearRegression(), X_a)
evaluate("A2: Random Forest - altitude + country",
         RandomForestRegressor(n_estimators=200, random_state=42), X_a)
y_test, pred_b = evaluate("B:  Linear - aroma + flavor + acidity", LinearRegression(), X_b)

# Chart: actual vs predicted for model B
plt.figure(figsize=(6, 6))
plt.scatter(y_test, pred_b, alpha=0.5, s=15)
plt.plot([60, 91], [60, 91], color="red", linestyle="--", label="Perfect prediction")
plt.title("Model B: actual vs predicted cup score")
plt.xlabel("Actual score")
plt.ylabel("Predicted score")
plt.legend()
plt.tight_layout()
plt.savefig("charts/06_actual_vs_predicted.png", dpi=150)
plt.show()


