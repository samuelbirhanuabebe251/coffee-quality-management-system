 Coffee Quality Management System
Tracing Arabica cup scores from farm to country

University project for the *Data Management* course (University of Cassino and Southern Lazio).
Dataset: [Coffee Quality Database from CQI](https://www.kaggle.com/datasets/volpatto/coffee-quality-database-from-cqi) — 1,311 Arabica samples.

#Project phases
1. ER design(draw.io): 5 entities — Country, Owner, Farm, CoffeeSample, QualityAssessment
2. Relational model (MySQL Workbench): forward engineering, PK/FK, delete rules
   SQL**: staging-table load, data distribution with `INSERT … SELECT DISTINCT`, 9 analysis queries (JOIN, GROUP BY/HAVING, subqueries, CASE, VIEW)
4. Python analysis: data quality assessment, cleaning, transformation, statistics, visualisation, machine learning

# Key findings
- High-altitude coffees (>1,500 m) score **1.34 points higher** than low-altitude ones (t = 6.54, p < 0.001)
- Each +1,000 m adds **+0.84 points**, but altitude explains only **2.3%** of quality (R² = 0.023): real but small
- **Flavor** is the strongest driver of the total score (r = 0.83)
- Origin (altitude + country) predicts only **12.7%** of score variation; a Random Forest overfitted

## Repository structure
| Path | Content |
|---|---|
| `coffee_er_diagram.drawio` | ER diagram |
| `data project 101.mwb` | MySQL Workbench model |
| `SQL/` | table creation, data load and analysis queries |
| `main.py` | Python analysis (cleaning → statistics → charts → tests → ML) |
| `charts/` | generated figures |
| `arabica_data_cleaned.csv` | original Kaggle data |
| `coffee_clean.csv` | cleaned dataset |

## How to run
1. Run the scripts in `SQL/` in MySQL: `coffee_quality.sql` → `raw_coffee.sql` → `Query 1 101.sql` → `All queries 101.sql`
2. `pip install pandas numpy matplotlib seaborn scipy statsmodels scikit-learn mysql-connector-python`
3. `python main.py` (it asks for your MySQL password)

## Tools
MySQL · MySQL Workbench · draw.io · Python · pandas · seaborn · statsmodels · scikit-learn

*Author: Samuel Birhanu Abebe*
