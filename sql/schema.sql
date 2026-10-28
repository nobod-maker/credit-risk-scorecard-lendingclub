-- ==============================================================================
-- 02_Credit_Risk: Dimensional Star-Schema DDL (SQLite / DuckDB Compatible)
-- ==============================================================================

DROP VIEW IF EXISTS vw_credit_risk_master;
DROP TABLE IF EXISTS fact_loan_portfolio;
DROP TABLE IF EXISTS dim_risk_grade;
DROP TABLE IF EXISTS dim_borrower;
DROP TABLE IF EXISTS dim_credit_profile;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS loans_data;

-- -----------------------------------------------------------------------------
-- 1. Raw / Modeled Staging Table: loans_data
-- -----------------------------------------------------------------------------
CREATE TABLE loans_data (
    loan_id BIGINT PRIMARY KEY,
    issue_d TEXT NOT NULL,
    loan_amnt DECIMAL(10,2) NOT NULL,
    term VARCHAR(15) NOT NULL,
    int_rate DECIMAL(5,2) NOT NULL,
    installment DECIMAL(10,2) NOT NULL,
    grade VARCHAR(1) NOT NULL,
    sub_grade VARCHAR(2) NOT NULL,
    emp_title VARCHAR(100),
    emp_length VARCHAR(15),
    home_ownership VARCHAR(10),
    annual_inc DECIMAL(12,2),
    verification_status VARCHAR(20),
    purpose VARCHAR(30),
    dti DECIMAL(6,2),
    delinq_2yrs INTEGER,
    earliest_cr_line TEXT,
    inq_last_6mths INTEGER,
    open_acc INTEGER,
    pub_rec INTEGER,
    revol_bal DECIMAL(12,2),
    revol_util DECIMAL(5,2),
    total_acc INTEGER,
    loan_status VARCHAR(30) NOT NULL,
    total_pymnt DECIMAL(12,2),
    recoveries DECIMAL(10,2)
);

-- -----------------------------------------------------------------------------
-- 2. Dimension: dim_risk_grade
-- -----------------------------------------------------------------------------
CREATE TABLE dim_risk_grade (
    risk_grade_key INTEGER PRIMARY KEY,
    grade VARCHAR(1) NOT NULL,
    sub_grade VARCHAR(2) NOT NULL UNIQUE,
    grade_rank INTEGER NOT NULL,
    benchmark_loss_rate_pct DECIMAL(5,2) NOT NULL
);

-- -----------------------------------------------------------------------------
-- 3. Dimension: dim_borrower
-- -----------------------------------------------------------------------------
CREATE TABLE dim_borrower (
    borrower_key INTEGER PRIMARY KEY,
    emp_length_bucket VARCHAR(20),
    home_ownership VARCHAR(10),
    annual_income DECIMAL(12,2),
    income_bracket VARCHAR(30),
    verification_status VARCHAR(20)
);

-- -----------------------------------------------------------------------------
-- 4. Dimension: dim_credit_profile
-- -----------------------------------------------------------------------------
CREATE TABLE dim_credit_profile (
    credit_profile_key INTEGER PRIMARY KEY,
    dti_band VARCHAR(30),
    revol_util_band VARCHAR(30),
    delinq_2yrs_flag TINYINT,
    inq_last_6mths_band VARCHAR(20),
    credit_history_years DECIMAL(4,1)
);

-- -----------------------------------------------------------------------------
-- 5. Dimension: dim_date
-- -----------------------------------------------------------------------------
CREATE TABLE dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    year_quarter VARCHAR(10) NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(15) NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(15) NOT NULL
);

-- -----------------------------------------------------------------------------
-- 6. Fact Table: fact_loan_portfolio
-- -----------------------------------------------------------------------------
CREATE TABLE fact_loan_portfolio (
    loan_key INTEGER PRIMARY KEY,
    loan_id BIGINT NOT NULL UNIQUE,
    issue_date_key INTEGER NOT NULL,
    borrower_key INTEGER NOT NULL,
    credit_profile_key INTEGER NOT NULL,
    risk_grade_key INTEGER NOT NULL,
    loan_term_months INTEGER NOT NULL,
    loan_amount DECIMAL(10,2) NOT NULL,
    funded_amount DECIMAL(10,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    monthly_installment DECIMAL(10,2) NOT NULL,
    total_collected DECIMAL(10,2) NOT NULL,
    net_charge_off_loss DECIMAL(10,2) NOT NULL,
    is_default TINYINT NOT NULL,
    predicted_default_prob DECIMAL(6,4),
    credit_score INTEGER,
    FOREIGN KEY (issue_date_key) REFERENCES dim_date(date_key),
    FOREIGN KEY (borrower_key) REFERENCES dim_borrower(borrower_key),
    FOREIGN KEY (credit_profile_key) REFERENCES dim_credit_profile(credit_profile_key),
    FOREIGN KEY (risk_grade_key) REFERENCES dim_risk_grade(risk_grade_key)
);

-- -----------------------------------------------------------------------------
-- Performance Indexes
-- -----------------------------------------------------------------------------
CREATE INDEX idx_fact_issue_date ON fact_loan_portfolio(issue_date_key);
CREATE INDEX idx_fact_risk_grade ON fact_loan_portfolio(risk_grade_key);
CREATE INDEX idx_fact_borrower ON fact_loan_portfolio(borrower_key);
CREATE INDEX idx_fact_credit_profile ON fact_loan_portfolio(credit_profile_key);
CREATE INDEX idx_fact_is_default ON fact_loan_portfolio(is_default);
CREATE INDEX idx_fact_credit_score ON fact_loan_portfolio(credit_score);
CREATE INDEX idx_loans_grade ON loans_data(grade, sub_grade);
CREATE INDEX idx_loans_status ON loans_data(loan_status);

-- -----------------------------------------------------------------------------
-- 7. Reporting Master View: vw_credit_risk_master
-- -----------------------------------------------------------------------------
CREATE VIEW vw_credit_risk_master AS
SELECT 
    f.loan_key,
    f.loan_id,
    d.full_date AS issue_date,
    d.year AS issue_year,
    d.quarter AS issue_quarter,
    d.year_quarter AS issue_year_quarter,
    rg.grade,
    rg.sub_grade,
    rg.grade_rank,
    rg.benchmark_loss_rate_pct,
    b.emp_length_bucket,
    b.home_ownership,
    b.annual_income,
    b.income_bracket,
    b.verification_status,
    cp.dti_band,
    cp.revol_util_band,
    cp.delinq_2yrs_flag,
    cp.inq_last_6mths_band,
    cp.credit_history_years,
    f.loan_term_months,
    f.loan_amount,
    f.funded_amount,
    f.interest_rate,
    f.monthly_installment,
    f.total_collected,
    f.net_charge_off_loss,
    f.is_default,
    f.predicted_default_prob,
    f.credit_score,
    CASE 
        WHEN f.credit_score >= 740 THEN '1. Prime (740+)'
        WHEN f.credit_score >= 670 THEN '2. Near Prime (670-739)'
        WHEN f.credit_score >= 600 THEN '3. Subprime (600-669)'
        ELSE '4. Deep Subprime (<600)'
    END AS credit_score_tier
FROM fact_loan_portfolio f
JOIN dim_date d ON f.issue_date_key = d.date_key
JOIN dim_risk_grade rg ON f.risk_grade_key = rg.risk_grade_key
JOIN dim_borrower b ON f.borrower_key = b.borrower_key
JOIN dim_credit_profile cp ON f.credit_profile_key = cp.credit_profile_key;
