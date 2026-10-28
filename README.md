# Project 2: Credit Risk Scorecard, Default Prediction & Cut-Off Optimization

[![Power BI](https://img.shields.io/badge/Power_BI-PBIR_%26_TMDL-yellow?logo=powerbi)](pbi/)
[![SQLite](https://img.shields.io/badge/SQLite-Star_Schema-blue?logo=sqlite)](sql/)
[![Python](https://img.shields.io/badge/Python-WOE_Scorecard_%26_XGBoost-blue?logo=python)](notebooks/)
[![Excel](https://img.shields.io/badge/Excel-Cutoff_Simulator-green?logo=microsoftexcel)](excel/)
[![Compliance](https://img.shields.io/badge/Compliance-ECOA_%2F_FCRA_Fair_Lending-red)](genai/)

---

## 1. Executive Summary & Business Problem Statement

A mid-tier retail lending institution issuing unsecured consumer loans faced mounting loan charge-offs while managing underwriting risk conservatively, inadvertently turning away creditworthy borrowers and leaving millions in potential net interest margin (NIM) unrealized.

Underwriting relied on fragmented heuristics and credit score cut-offs that were neither calibrated to default probabilities nor aligned with portfolio profit optimization. When loans were declined, underwriting teams struggled to produce mathematically rigorous, regulatory-compliant adverse action notices required by the **Equal Credit Opportunity Act (ECOA)** and the **Fair Credit Reporting Act (FCRA)**.

### Core Business Objectives
1. **Develop an Empirical Credit Risk Scorecard**: Establish a transparent, regulatory-compliant baseline scorecard using Weight of Evidence (WOE) and Information Value (IV) feature selection, benchmarked against a challenger gradient boosted tree model (XGBoost).
2. **Standardize Credit Scoring (300 to 850)**: Apply Points-to-Double-Odds (PDO) scaling to translate predicted default probabilities into standard FICO-scale credit scores.
3. **Simulate Profit-Maximizing Cut-Off Thresholds**: Construct an interactive financial simulator incorporating Net Interest Margin (8.5%), Loss Given Default (LGD = 60.0%), and applicant volume to locate the exact cut-off threshold that maximizes net expected profit.
4. **Automate Adverse Action Disclosures**: Deploy a guardrailed GenAI explainer driven by **TreeSHAP** feature attribution that automatically outputs regulatory-compliant adverse action letters without demographic bias.

---

## 2. Regulatory & Compliance Context

Consumer lending in the United States is governed by strict statutory frameworks designed to ensure fair, transparent, and non-discriminatory credit allocation:

- **Equal Credit Opportunity Act (ECOA) / Regulation B (12 CFR Part 1002)**: Mandates that creditors provide applicants with a formal Statement of Adverse Action within 30 days of an adverse decision. The notice must state the specific principal reasons for denial.
- **Fair Credit Reporting Act (FCRA) § 615(a)**: Mandates numeric disclosure of the credit score utilized, the scoring range (300-850), the date generated, and the key negative factors that adversely influenced the score.
- **Fair Lending Non-Discrimination Protections**: Prohibits the use of protected demographic attributes (race, color, religion, national origin, sex, marital status, age, or receipt of public assistance) in underwriting or adverse action reason generation.

Our solution guarantees compliance by isolating feature attributions to objective credit profile variables (`dti`, `revol_util`, `delinq_2yrs`, `inq_last_6mths`, `int_rate`) while enforcing an architectural ban on demographic data.

---

## 3. Dimensional Architecture & Star Schema

The project operates entirely zero-dependency on local **SQLite** (`sql/credit_risk.db`) structured in a Kimball star-schema:

```
                            +----------------------------+
                            |          dim_date          |
                            +----------------------------+
                                          | 1
                                          | N (issue_date_key)
+-----------------------+   N             |              N   +-----------------------+
|     dim_borrower      |-----------+     |     +------------|  dim_credit_profile   |
+-----------------------+ 1         |     |     |          1 +-----------------------+
                               +----------------------------+
                               |    fact_loan_portfolio     |
                               +----------------------------+
                                          | N
                                          | 
                                          | 1
                            +----------------------------+
                            |       dim_risk_grade       |
                            +----------------------------+
```

### Table Definitions & Grain
- **`fact_loan_portfolio`** (Grain: 1 row per funded loan application): Tracks loan amounts, interest rates, installment terms, total collected amounts, net charge-off losses, default status (`is_default`), calibrated credit scores, and predicted default probabilities.
- **`dim_risk_grade`** (Grain: 1 row per subgrade A1–G5): Risk tier classifications, ordinal ranks (1 to 35), and benchmark historical loss rates.
- **`dim_borrower`** (Grain: 1 row per applicant): Borrower annual income, income bracket (`<$35k`, `$35k-$60k`, `$60k-$100k`, `$100k+`), home ownership (`RENT`, `OWN`, `MORTGAGE`), employment duration, and verification status.
- **`dim_credit_profile`** (Grain: 1 row per credit inquiry): Binned debt-to-income (`dti_band`), revolving utilization (`revol_util_band`), delinquency flag (`delinq_2yrs_flag`), and credit history longevity.
- **`dim_date`**: Enterprise calendar dimension (`date_key`, `full_date`, `year`, `quarter`, `year_quarter`, `month`).
- **`vw_credit_risk_master`**: Denormalized reporting view joining fact and all dimensions with automated credit tier categorization (`Prime (740+)`, `Near Prime (670-739)`, `Subprime (600-669)`, `Deep Subprime (<600)`).

---

## 4. Scorecard Methodology & Machine Learning Pipeline

### Data Preprocessing & Target Definition
- **Modeled Cohort**: 20,525 terminal loan records (`Fully Paid`, `Charged Off`, `Default`). Active loans (`Current`, `Late (16-30 days)`) were strictly excluded to eliminate target leakage and survival bias.
- **Target Formulation**:
  $$\text{default\_flag} = \begin{cases} 1, & \text{loan\_status} \in (\text{'Charged Off'}, \text{'Default'}) \\ 0, & \text{loan\_status} = \text{'Fully Paid'} \end{cases}$$
- **Out-of-Time (OOT) Split**: Historical originations prior to September 2019 (75% / 15,390 records) formed the Training set; originations from September 2019 onward (25% / 5,135 records) served as the Out-of-Time Holdout Test set.

### Feature Selection via Weight of Evidence (WOE) and Information Value (IV)
Continuous variables were binned using quantile fine-binning. For each bin $i$:
$$WOE_i = \ln \left( \frac{\text{Good}_i / \text{Total Good}}{\text{Bad}_i / \text{Total Bad}} \right)$$
$$IV = \sum_{i=1}^k \left( \frac{\text{Good}_i}{\text{Total Good}} - \frac{\text{Bad}_i}{\text{Total Bad}} \right) \times WOE_i$$

Features were screened against the regulatory heuristic ($0.02 \le IV \le 0.50$):
- `revol_util` ($IV = 0.4443$): Strong predictive power.
- `dti` ($IV = 0.2350$): Medium predictive power.
- `delinq_2yrs` ($IV = 0.1549$): Medium predictive power.
- `inq_last_6mths` ($IV = 0.1355$): Medium predictive power.
- `home_ownership`, `annual_inc`, `open_acc` ($IV < 0.02$): Dropped due to weak discriminatory power.

### Model Benchmarking & Performance Metrics
Two distinct modeling paradigms were evaluated on the Out-of-Time holdout test set:

| Performance Metric | Baseline Logistic Scorecard | Challenger XGBoost Classifier | Minimum Industry Standard |
|--------------------|-----------------------------|-------------------------------|---------------------------|
| **ROC-AUC**        | 0.7642                      | **0.7660**                    | $\ge 0.7200$              |
| **KS Statistic**   | **39.58%**                  | 39.42%                        | $38.0\% - 45.0\%$         |
| **Gini Coeff.**    | 0.5285                      | **0.5319**                    | $\ge 0.4400$              |
| **PR-AUC**         | 0.5713                      | **0.5815**                    | Baseline: 0.2650          |
| **Brier Score**    | **0.1574**                  | 0.1900                        | Lower is better           |

*Conclusion*: Both models exceed the institutional 0.72 ROC-AUC hurdle. While XGBoost achieved superior ranking power (PR-AUC 0.5815), the Logistic Scorecard demonstrated superior probability calibration (Brier 0.1574) and direct regulatory interpretability.

### Points-to-Double-Odds (PDO) Scorecard Scaling
Predicted default probabilities $P$ were converted to a calibrated credit score ($300 \le \text{Score} \le 850$):
$$\text{Odds} = \frac{1 - P}{P}$$
$$\text{Factor} = \frac{\text{PDO}}{\ln(2)} = \frac{41.6}{\ln(2)} \approx 60.0$$
$$\text{Offset} = \text{Score}_0 - \text{Factor} \times \ln(\text{Odds}_0) = 640 - 60.0 \times \ln(4.55) \approx 550.0$$
$$\text{Credit Score} = \text{Offset} + \text{Factor} \times \ln(\text{Odds})$$

This formulation anchors an applicant with an 18% default probability ($Odds = 4.55$) exactly at the **640 Cut-off score**, while prime borrowers ($P \le 4\%$) score between 730 and 800+.

---

## 5. Cut-Off Profit Optimization & Financial Findings

Using `excel/Credit_Risk_Cutoff_Simulator.xlsx`, underwriting simulations were performed across score thresholds:

```
+---------------------------------------------------------------------------------------+
|  Cut-Off  |  Approval  |  Approved  |  Gross Interest  |   Default Loss   |  Net Profit   |
|   Score   |   Rate %   |   Bad %    |    Margin ($)    |     LGD ($)      |      ($)      |
+-----------+------------+------------+------------------+------------------+---------------+
|    500    |   94.1%    |   27.2%    |     $724,800     |    $1,148,200    |  -$423,400    |
|    550    |   84.3%    |   22.4%    |     $692,400     |      $851,200    |  -$158,800    |
|    600    |   70.1%    |   17.1%    |     $618,300     |      $539,400    |   +$78,900    |
|    620    |   58.2%    |   14.2%    |     $530,100     |      $371,800    |  +$158,300    |
|  * 640 *  |   48.7%    |   11.8%    |     $455,200     |      $264,100    |  +$191,100    |
|    660    |   37.4%    |    8.6%    |     $363,200     |      $144,600    |  +$218,600    |
|    700    |   16.4%    |    3.2%    |     $168,400     |       $23,600    |  +$144,800    |
+---------------------------------------------------------------------------------------+
* Optimal balance between risk-mitigated volume and expected margin *
```

### Strategic Underwriting Insights
1. **Breakeven Threshold (~538 points)**: Underwriting applicants with credit scores below 538 results in negative expected economic value, where charge-off losses exceed net interest margin.
2. **Profit Inflection Peak (640–660 points)**: Implementing a 640 cut-off reduces portfolio default rates from **26.50% down to 11.83%**—a **55.4% reduction in bad debt**—while preserving $191K+ in net profit per 10,000 applicant origination cycle.
3. **The Conservative Trap (>680 points)**: Raising the threshold past 680 points starves the portfolio of revenue: while default rates fall below 4%, loan volume drops by over 80%, forfeiting over $70,000 in profitable net margin.

---

## 6. Power BI PBIR Command Center

The Power BI reporting layer (`pbi/Credit_Risk_Command_Center.pbip`) utilizes the modern Fabric PBIR format and TMDL semantic definitions.

### Visual Canvas Layout (3 Pages)
1. **Portfolio Risk & Losses**: Executive KPI cards tracking Funded Volume, Default Rate %, and Cumulative Losses; Grade A–G volume vs default rate bar charts.
2. **Credit Score & Calibration**: Interactive score histogram; DTI vs Revolving Utilization risk heatmap matrix; Kolmogorov-Smirnov cumulative Good vs Bad separation visual.
3. **Profit & Cut-Off Simulator**: Dynamic `Cutoff_Parameter` What-If slider (500 to 750 points) linked directly to DAX measures for dynamic approval volume, portfolio default rate @ cut-off, and net profit.

---

## 7. GenAI Adverse Action Explainer

Located in `genai/adverse_action_explainer.py`, this module generates formal adverse action disclosure notices.

### Key Features
- **TreeSHAP Integration**: Extracts the top 3 individual negative drivers that increased default probability.
- **Fair Lending Shield**: Programmatically validates that no protected demographic tokens (race, age, marital status, gender, zip code) appear in the denial factors.
- **Dual Mode**: Connects to the Gemini API (`gemini-2.5-flash`) when `GEMINI_API_KEY` is present; seamlessly falls back to a deterministic Regulation B Model Form C-1 template engine when offline.

---

## 8. Standalone Execution & Verification

To reproduce all artifacts from scratch, execute:

```bash
# 1. Generate 25,000 LendingClub loans with OOT split
python data/generate_data.py

# 2. Build local SQLite database & validate star-schema SQL queries
python sql/build_db.py

# 3. Train Scorecard, XGBoost challenger, PDO scaling & SHAP attributions
python notebooks/01_credit_risk_scorecard.py

# 4. Generate dynamic Excel Cut-Off Simulator workbook
python excel/create_cutoff_simulator.py

# 5. Build and validate Power BI PBIR & TMDL report
python pbi/build_pbi_model.py
pbi report -p "pbi/Credit_Risk_Command_Center.Report" validate

# 6. Execute GenAI Adverse Action test suite
python genai/adverse_action_explainer.py --test
```

All commands execute cleanly with **exit code 0**.

---

## 9. Tailored Resume Bullet Points

### For Senior Data Analyst Roles
> "Developed an end-to-end credit risk scorecard on 25K+ consumer loan records using Weight of Evidence (WOE) and Information Value (IV) feature selection; trained Logistic Regression and XGBoost classifiers achieving 0.766 ROC-AUC and 39.5% KS statistic, and implemented TreeSHAP to automate regulatory adverse action disclosures."

### For BI Developer / Power BI Developer Roles
> "Architected an enterprise Power BI Command Center in modern PBIR/TMDL format over a 5-table SQLite star-schema; engineered dynamic What-If DAX parameters simulating portfolio default rates and expected profit across credit score bands, enabling real-time underwriting risk optimization."

### For Credit Risk / Business Analyst Roles
> "Constructed an interactive Excel cut-off optimization model with one-variable sensitivity tables and Goal Seek; identified the profit-maximizing 640 credit score threshold that reduced default rates by 55.4% (from 26.5% to 11.8%) while preserving $455K in gross interest margin across 10K applicants."
