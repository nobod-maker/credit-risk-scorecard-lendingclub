-- ==============================================================================
-- 02_Credit_Risk: Analytical & KPI Transformation Queries
-- ==============================================================================

-- -----------------------------------------------------------------------------
-- Query 1: Default Rate by Risk Grade & Subgrade
-- Evaluates default rate, loan volume, and interest spread across risk tiers
-- -----------------------------------------------------------------------------
SELECT 
    grade,
    sub_grade,
    COUNT(*) AS total_loans,
    ROUND(SUM(loan_amnt), 2) AS total_funded_volume,
    ROUND(AVG(int_rate), 2) AS avg_interest_rate,
    SUM(CASE WHEN loan_status IN ('Charged Off', 'Default') THEN 1 ELSE 0 END) AS default_count,
    ROUND(AVG(CASE WHEN loan_status IN ('Charged Off', 'Default') THEN 1.0 ELSE 0.0 END) * 100.0, 2) AS default_rate_pct,
    ROUND(SUM(CASE WHEN loan_status IN ('Charged Off', 'Default') THEN loan_amnt ELSE 0 END), 2) AS defaulted_volume
FROM loans_data
WHERE loan_status IN ('Fully Paid', 'Charged Off', 'Default')
GROUP BY grade, sub_grade
ORDER BY grade, sub_grade;

-- -----------------------------------------------------------------------------
-- Query 2: Default Rate by Loan Purpose and Term
-- Assesses loan maturity risk and borrowing motive impact on charge-offs
-- -----------------------------------------------------------------------------
SELECT 
    purpose,
    term,
    COUNT(*) AS loan_count,
    ROUND(SUM(loan_amnt), 2) AS total_volume,
    ROUND(AVG(int_rate), 2) AS avg_int_rate,
    ROUND(AVG(dti), 2) AS avg_dti,
    ROUND(AVG(CASE WHEN loan_status IN ('Charged Off', 'Default') THEN 1.0 ELSE 0.0 END) * 100.0, 2) AS default_rate_pct
FROM loans_data
WHERE loan_status IN ('Fully Paid', 'Charged Off', 'Default')
GROUP BY purpose, term
ORDER BY default_rate_pct DESC;

-- -----------------------------------------------------------------------------
-- Query 3: Cumulative Default Share Across Risk Grades (Window Functions)
-- Quantifies how bad loans concentrate in lower credit grades
-- -----------------------------------------------------------------------------
WITH grade_aggregates AS (
    SELECT 
        grade,
        COUNT(*) AS total_loans,
        ROUND(SUM(loan_amnt), 2) AS total_volume,
        SUM(CASE WHEN loan_status IN ('Charged Off', 'Default') THEN 1 ELSE 0 END) AS default_count,
        ROUND(SUM(CASE WHEN loan_status IN ('Charged Off', 'Default') THEN loan_amnt ELSE 0 END), 2) AS default_loss_volume
    FROM loans_data
    WHERE loan_status IN ('Fully Paid', 'Charged Off', 'Default')
    GROUP BY grade
)
SELECT 
    grade,
    total_loans,
    total_volume,
    default_count,
    ROUND(default_count * 100.0 / total_loans, 2) AS grade_default_rate_pct,
    SUM(default_count) OVER (ORDER BY grade) AS cumulative_defaults,
    SUM(total_loans) OVER (ORDER BY grade) AS cumulative_loans,
    ROUND(SUM(default_count) OVER (ORDER BY grade) * 100.0 / SUM(default_count) OVER (), 2) AS cum_default_share_pct,
    ROUND(SUM(default_loss_volume) OVER (ORDER BY grade) * 100.0 / SUM(default_loss_volume) OVER (), 2) AS cum_loss_volume_share_pct
FROM grade_aggregates
ORDER BY grade;

-- -----------------------------------------------------------------------------
-- Query 4: Debt-to-Income (DTI) & Utilization Risk Matrix
-- Analyzes the co-dependence between borrower leverage and credit line strain
-- -----------------------------------------------------------------------------
SELECT 
    CASE 
        WHEN dti < 12.0 THEN '1. Low DTI (<12%)'
        WHEN dti BETWEEN 12.0 AND 20.0 THEN '2. Moderate DTI (12-20%)'
        WHEN dti BETWEEN 20.0 AND 28.0 THEN '3. High DTI (20-28%)'
        ELSE '4. Critical DTI (>28%)'
    END AS dti_tier,
    CASE 
        WHEN revol_util < 30.0 THEN '1. Low Util (<30%)'
        WHEN revol_util BETWEEN 30.0 AND 60.0 THEN '2. Moderate Util (30-60%)'
        WHEN revol_util BETWEEN 60.0 AND 80.0 THEN '3. High Util (60-80%)'
        ELSE '4. Critical Util (>80%)'
    END AS util_tier,
    COUNT(*) AS total_loans,
    ROUND(AVG(loan_amnt), 2) AS avg_loan_amnt,
    SUM(CASE WHEN loan_status IN ('Charged Off', 'Default') THEN 1 ELSE 0 END) AS default_count,
    ROUND(AVG(CASE WHEN loan_status IN ('Charged Off', 'Default') THEN 1.0 ELSE 0.0 END) * 100.0, 2) AS default_rate_pct
FROM loans_data
WHERE loan_status IN ('Fully Paid', 'Charged Off', 'Default')
  AND dti IS NOT NULL AND revol_util IS NOT NULL
GROUP BY 1, 2
ORDER BY 1, 2;

-- -----------------------------------------------------------------------------
-- Query 5: Credit Score Tier & Loss Severity Summary (vw_credit_risk_master)
-- Validates dimensional modeling and calibrated score tier distribution
-- -----------------------------------------------------------------------------
SELECT 
    credit_score_tier,
    COUNT(*) AS total_funded_loans,
    ROUND(SUM(funded_amount), 2) AS total_funded_amount,
    ROUND(AVG(interest_rate), 2) AS avg_interest_rate,
    ROUND(AVG(credit_score), 0) AS avg_credit_score,
    SUM(is_default) AS total_defaults,
    ROUND(AVG(is_default) * 100.0, 2) AS default_rate_pct,
    ROUND(SUM(net_charge_off_loss), 2) AS total_net_loss,
    ROUND(SUM(net_charge_off_loss) * 100.0 / SUM(funded_amount), 2) AS loss_rate_pct
FROM vw_credit_risk_master
GROUP BY credit_score_tier
ORDER BY credit_score_tier;
