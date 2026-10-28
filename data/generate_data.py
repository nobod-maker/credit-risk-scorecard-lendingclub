"""
generate_data.py - LendingClub Credit Risk Synthetic Data Generator

Generates high-fidelity consumer loan origination data matching LendingClub schema (25+ features),
with empirical risk gradients across grades A-G, realistic co-dependencies (DTI, utilization, inquiries),
explicit default target definition (excluding active/current loans to prevent leakage),
and temporal Out-of-Time (OOT) train/test splits.
"""

import os
import random
import datetime
import numpy as np
import pandas as pd


def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)


def generate_lending_club_data(num_records=25000, seed=42):
    set_seed(seed)
    
    # 1. Loan IDs
    start_id = 1000001
    loan_ids = np.arange(start_id, start_id + num_records)
    
    # 2. Risk Grades & Subgrades
    grades = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    grade_weights = [0.18, 0.28, 0.26, 0.15, 0.08, 0.03, 0.02]
    assigned_grades = np.random.choice(grades, size=num_records, p=grade_weights)
    
    sub_grades = []
    for g in assigned_grades:
        sub_num = np.random.choice([1, 2, 3, 4, 5], p=[0.25, 0.22, 0.20, 0.18, 0.15])
        sub_grades.append(f"{g}{sub_num}")
    sub_grades = np.array(sub_grades)
    
    # Base parameters per grade: (base_int_rate, base_default_prob)
    grade_risk_map = {
        'A': (7.2, 0.052),
        'B': (11.5, 0.118),
        'C': (15.2, 0.185),
        'D': (19.1, 0.254),
        'E': (24.0, 0.331),
        'F': (28.2, 0.420),
        'G': (30.5, 0.485)
    }
    
    # 3. Loan Amounts ($1,000 to $40,000)
    # Right-skewed distribution centered around $12,500 - $15,000
    loan_amounts = np.round(np.random.gamma(shape=3.0, scale=4500, size=num_records) + 1000, -2)
    loan_amounts = np.clip(loan_amounts, 1000.0, 40000.0)
    
    # 4. Term (' 36 months' or ' 60 months')
    # Higher grades more likely 36m, lower grades more likely 60m
    terms = []
    for g in assigned_grades:
        p_36 = 0.85 if g in ['A', 'B'] else (0.70 if g == 'C' else 0.50)
        t = ' 36 months' if random.random() < p_36 else ' 60 months'
        terms.append(t)
    terms = np.array(terms)
    
    # 5. Interest Rates
    int_rates = []
    for g, sg in zip(assigned_grades, sub_grades):
        base_rate = grade_risk_map[g][0]
        sub_offset = (int(sg[1]) - 3) * 0.5
        noise = np.random.normal(0, 0.6)
        rate = max(5.32, min(30.99, base_rate + sub_offset + noise))
        int_rates.append(round(rate, 2))
    int_rates = np.array(int_rates)
    
    # 6. Monthly Installments
    # Standard amortization formula: M = P * (r*(1+r)^n) / ((1+r)^n - 1)
    installments = []
    for p, r, t in zip(loan_amounts, int_rates, terms):
        n = 36 if '36' in t else 60
        monthly_r = (r / 100.0) / 12.0
        inst = p * (monthly_r * ((1 + monthly_r) ** n)) / (((1 + monthly_r) ** n) - 1)
        installments.append(round(inst, 2))
    installments = np.array(installments)
    
    # 7. Employment Information
    emp_titles_pool = [
        'Software Engineer', 'Registered Nurse', 'Project Manager', 'Teacher',
        'Sales Representative', 'Operations Analyst', 'Accountant', 'Electrician',
        'Administrative Assistant', 'Retail Specialist', 'Store Manager',
        'Truck Driver', 'Executive Assistant', 'Financial Analyst', 'Consultant',
        'Police Officer', 'Mechanic', 'Customer Service Rep', 'Attorney', 'Physician'
    ]
    emp_titles = np.random.choice(emp_titles_pool, size=num_records)
    
    emp_lengths_pool = ['< 1 year', '1 year', '2 years', '3 years', '4 years',
                        '5 years', '6 years', '7 years', '8 years', '9 years', '10+ years']
    emp_len_weights = [0.08, 0.07, 0.09, 0.08, 0.06, 0.07, 0.05, 0.04, 0.04, 0.04, 0.38]
    emp_lengths = np.random.choice(emp_lengths_pool, size=num_records, p=emp_len_weights)
    
    # 8. Home Ownership
    home_ownership_pool = ['MORTGAGE', 'RENT', 'OWN', 'OTHER']
    home_weights = [0.49, 0.40, 0.10, 0.01]
    home_ownerships = np.random.choice(home_ownership_pool, size=num_records, p=home_weights)
    
    # 9. Annual Income
    # Log-normal distribution with median ~$65,000
    annual_incomes = np.round(np.random.lognormal(mean=11.0, sigma=0.55, size=num_records), -2)
    annual_incomes = np.clip(annual_incomes, 18000.0, 350000.0)
    
    # 10. Verification Status
    verif_pool = ['Verified', 'Source Verified', 'Not Verified']
    verif_weights = [0.38, 0.32, 0.30]
    verification_statuses = np.random.choice(verif_pool, size=num_records, p=verif_weights)
    
    # 11. Loan Purpose
    purposes_pool = [
        'debt_consolidation', 'credit_card', 'home_improvement',
        'major_purchase', 'small_business', 'medical', 'car', 'vacation', 'other'
    ]
    purpose_weights = [0.57, 0.22, 0.07, 0.04, 0.03, 0.03, 0.02, 0.01, 0.01]
    purposes = np.random.choice(purposes_pool, size=num_records, p=purpose_weights)
    
    # 12. Debt to Income (dti)
    # Higher for lower grades, clip to realistic bounds [0.0, 45.0]
    dtis = []
    for g in assigned_grades:
        mean_dti = 14.0 if g in ['A', 'B'] else (18.5 if g in ['C', 'D'] else 22.5)
        d = np.random.normal(mean_dti, 6.0)
        dtis.append(round(max(1.0, min(44.9, d)), 2))
    dtis = np.array(dtis)
    
    # 13. Delinquencies in Past 2 Years
    delinqs = []
    for g in assigned_grades:
        p_zero = 0.92 if g in ['A', 'B'] else (0.82 if g in ['C', 'D'] else 0.65)
        if random.random() < p_zero:
            delinqs.append(0)
        else:
            delinqs.append(int(np.random.choice([1, 2, 3, 4, 5], p=[0.60, 0.25, 0.10, 0.03, 0.02])))
    delinqs = np.array(delinqs)
    
    # 14. Earliest Credit Line & Inquiries in past 6 months
    # Credit history length 3 to 35 years
    base_date = datetime.date(2016, 1, 1)
    end_date = datetime.date(2020, 12, 31)
    total_days = (end_date - base_date).days
    
    issue_dates = []
    earliest_cr_lines = []
    for _ in range(num_records):
        iss_day = base_date + datetime.timedelta(days=random.randint(0, total_days))
        # Earliest cr line 3 to 30 years prior
        cr_years_prior = random.randint(3, 30)
        cr_day = iss_day - datetime.timedelta(days=cr_years_prior * 365 + random.randint(0, 364))
        issue_dates.append(iss_day.strftime('%Y-%m-%d'))
        earliest_cr_lines.append(cr_day.strftime('%Y-%m-%d'))
    issue_dates = np.array(issue_dates)
    earliest_cr_lines = np.array(earliest_cr_lines)
    
    # Inquiries in last 6 months
    inquiries = []
    for g in assigned_grades:
        p_zero = 0.65 if g in ['A', 'B'] else (0.45 if g in ['C', 'D'] else 0.25)
        if random.random() < p_zero:
            inquiries.append(0)
        else:
            inquiries.append(int(np.random.choice([1, 2, 3, 4, 5], p=[0.50, 0.28, 0.12, 0.07, 0.03])))
    inquiries = np.array(inquiries)
    
    # 15. Open Accounts & Total Accounts
    open_accs = np.random.poisson(lam=11.5, size=num_records)
    open_accs = np.clip(open_accs, 2, 38)
    total_accs = open_accs + np.random.poisson(lam=12.0, size=num_records)
    total_accs = np.clip(total_accs, open_accs + 1, 75)
    
    # 16. Public Derogatory Records (Bankruptcies / liens)
    pub_recs = []
    for g in assigned_grades:
        p_zero = 0.95 if g in ['A', 'B'] else (0.85 if g in ['C', 'D'] else 0.70)
        pub_recs.append(0 if random.random() < p_zero else np.random.choice([1, 2, 3], p=[0.80, 0.15, 0.05]))
    pub_recs = np.array(pub_recs)
    
    # 17. Revolving Balance and Revolving Utilization
    revol_bals = np.round(np.random.lognormal(mean=9.5, sigma=0.8, size=num_records), 2)
    revol_bals = np.clip(revol_bals, 200.0, 120000.0)
    
    revol_utils = []
    for g in assigned_grades:
        mean_util = 38.0 if g in ['A', 'B'] else (55.0 if g in ['C', 'D'] else 72.0)
        u = np.random.normal(mean_util, 18.0)
        revol_utils.append(round(max(0.5, min(108.5, u)), 2))
    revol_utils = np.array(revol_utils)
    
    # 18. Determine Loan Status & Target Flag
    # Terminal vs Non-Terminal:
    # 82% terminal (Fully Paid, Charged Off, Default)
    # 18% ongoing/active ('Current', 'Late (31-120 days)')
    loan_statuses = []
    total_payments = []
    recoveries_list = []
    
    for i in range(num_records):
        g = assigned_grades[i]
        dti_val = dtis[i]
        util_val = revol_utils[i]
        inq_val = inquiries[i]
        delinq_val = delinqs[i]
        amt = loan_amounts[i]
        rate = int_rates[i]
        t = terms[i]
        term_months = 36 if '36' in t else 60
        
        # Calculate dynamic default probability
        base_pd = grade_risk_map[g][1]
        
        # Risk multipliers
        dti_mult = 1.0 + max(0.0, (dti_val - 18.0) * 0.02)
        util_mult = 1.0 + max(0.0, (util_val - 50.0) * 0.015)
        inq_mult = 1.0 + inq_val * 0.08
        delinq_mult = 1.0 + (0.35 if delinq_val > 0 else 0.0)
        
        adj_pd = min(0.85, base_pd * dti_mult * util_mult * inq_mult * delinq_mult)
        
        # Status distribution: 82% terminal, 18% non-terminal
        is_active = random.random() < 0.18
        
        if is_active:
            if random.random() < 0.90:
                status = 'Current'
            else:
                status = 'Late (31-120 days)'
            # Partial payments made so far
            pymnt = round(amt * (random.uniform(0.15, 0.65)), 2)
            rec = 0.0
        else:
            # Terminal loan: Fully Paid vs Charged Off / Default
            is_def = random.random() < adj_pd
            if is_def:
                status = 'Charged Off' if random.random() < 0.92 else 'Default'
                # Defaulted loans paid partial payments before charge-off
                fraction_paid = random.uniform(0.10, 0.55)
                pymnt = round(amt * fraction_paid, 2)
                # Some recoveries after charge-off
                rec = round(amt * (random.uniform(0.02, 0.12) if random.random() < 0.40 else 0.0), 2)
            else:
                status = 'Fully Paid'
                total_interest = amt * (rate / 100.0) * (term_months / 12.0) * 0.55
                pymnt = round(amt + total_interest, 2)
                rec = 0.0
                
        loan_statuses.append(status)
        total_payments.append(pymnt)
        recoveries_list.append(rec)
        
    df = pd.DataFrame({
        'loan_id': loan_ids,
        'issue_d': issue_dates,
        'loan_amnt': loan_amounts,
        'term': terms,
        'int_rate': int_rates,
        'installment': installments,
        'grade': assigned_grades,
        'sub_grade': sub_grades,
        'emp_title': emp_titles,
        'emp_length': emp_lengths,
        'home_ownership': home_ownerships,
        'annual_inc': annual_incomes,
        'verification_status': verification_statuses,
        'purpose': purposes,
        'dti': dtis,
        'delinq_2yrs': delinqs,
        'earliest_cr_line': earliest_cr_lines,
        'inq_last_6mths': inquiries,
        'open_acc': open_accs,
        'pub_rec': pub_recs,
        'revol_bal': revol_bals,
        'revol_util': revol_utils,
        'total_acc': total_accs,
        'loan_status': loan_statuses,
        'total_pymnt': total_payments,
        'recoveries': recoveries_list
    })
    
    return df


def prepare_and_export_datasets(df, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Full raw dataset
    raw_path = os.path.join(output_dir, 'loans_data.csv')
    df.to_csv(raw_path, index=False)
    print(f"Generated raw loans dataset: {raw_path} ({len(df)} records)")
    
    # 2. Terminal Modeled Dataset (Strictly exclude 'Current' and active loans to eliminate target leakage)
    terminal_statuses = ['Fully Paid', 'Charged Off', 'Default']
    df_modeled = df[df['loan_status'].isin(terminal_statuses)].copy()
    df_modeled['default_flag'] = df_modeled['loan_status'].apply(
        lambda s: 1 if s in ['Charged Off', 'Default'] else 0
    )
    
    modeled_path = os.path.join(output_dir, 'loans_modeled.csv')
    df_modeled.to_csv(modeled_path, index=False)
    print(f"Modeled terminal loans dataset: {modeled_path} ({len(df_modeled)} records, default rate: {df_modeled['default_flag'].mean():.2%})")
    
    # 3. Temporal Out-of-Time (OOT) Split
    # Earlier 75% issue dates -> Train; Later 25% issue dates -> Test
    df_modeled['issue_dt'] = pd.to_datetime(df_modeled['issue_d'])
    df_modeled = df_modeled.sort_values('issue_dt').reset_index(drop=True)
    
    split_idx = int(len(df_modeled) * 0.75)
    split_date = df_modeled.loc[split_idx, 'issue_dt']
    
    train_df = df_modeled[df_modeled['issue_dt'] < split_date].copy().drop(columns=['issue_dt'])
    test_df = df_modeled[df_modeled['issue_dt'] >= split_date].copy().drop(columns=['issue_dt'])
    
    train_path = os.path.join(output_dir, 'train_loans.csv')
    test_path = os.path.join(output_dir, 'test_loans.csv')
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"OOT Train dataset: {train_path} ({len(train_df)} records, date < {split_date.strftime('%Y-%m-%d')}, default rate: {train_df['default_flag'].mean():.2%})")
    print(f"OOT Test dataset: {test_path} ({len(test_df)} records, date >= {split_date.strftime('%Y-%m-%d')}, default rate: {test_df['default_flag'].mean():.2%})")
    
    # 4. Generate Star Schema Dimension & Fact CSVs
    # dim_risk_grade
    subgrades_all = []
    grades_all = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
    benchmark_losses = [2.5, 5.0, 9.5, 15.0, 22.0, 30.0, 38.0]
    
    rank = 1
    for i, g in enumerate(grades_all):
        for s in range(1, 6):
            sg = f"{g}{s}"
            subgrades_all.append({
                'risk_grade_key': rank,
                'grade': g,
                'sub_grade': sg,
                'grade_rank': rank,
                'benchmark_loss_rate_pct': round(benchmark_losses[i] + (s - 1) * 0.6, 2)
            })
            rank += 1
    dim_risk_grade = pd.DataFrame(subgrades_all)
    dim_risk_grade.to_csv(os.path.join(output_dir, 'dim_risk_grade.csv'), index=False)
    
    # dim_date
    date_range = pd.date_range(start='2015-01-01', end='2021-12-31', freq='D')
    dim_date = pd.DataFrame({
        'date_key': date_range.strftime('%Y%m%d').astype(int),
        'full_date': date_range.strftime('%Y-%m-%d'),
        'year': date_range.year,
        'quarter': date_range.quarter,
        'year_quarter': date_range.strftime('%Y-Q') + date_range.quarter.astype(str),
        'month': date_range.month,
        'month_name': date_range.strftime('%B'),
        'day_of_month': date_range.day,
        'day_of_week': date_range.dayofweek + 1,
        'day_name': date_range.strftime('%A')
    })
    dim_date.to_csv(os.path.join(output_dir, 'dim_date.csv'), index=False)
    
    # dim_borrower
    # Unique borrower profiles from dataset
    borrower_df = df[['loan_id', 'emp_length', 'home_ownership', 'annual_inc', 'verification_status']].copy()
    borrower_df['borrower_key'] = np.arange(1, len(borrower_df) + 1)
    
    def bucket_income(inc):
        if inc < 35000:
            return '< $35k'
        elif inc < 60000:
            return '$35k-$60k'
        elif inc < 100000:
            return '$60k-$100k'
        else:
            return '$100k+'
            
    borrower_df['income_bracket'] = borrower_df['annual_inc'].apply(bucket_income)
    borrower_df = borrower_df.rename(columns={'annual_inc': 'annual_income', 'emp_length': 'emp_length_bucket'})
    dim_borrower = borrower_df[['borrower_key', 'emp_length_bucket', 'home_ownership', 'annual_income', 'income_bracket', 'verification_status']]
    dim_borrower.to_csv(os.path.join(output_dir, 'dim_borrower.csv'), index=False)
    
    # dim_credit_profile
    profile_df = df[['loan_id', 'dti', 'revol_util', 'delinq_2yrs', 'inq_last_6mths', 'earliest_cr_line', 'issue_d']].copy()
    profile_df['credit_profile_key'] = np.arange(1, len(profile_df) + 1)
    
    def bucket_dti(d):
        if d < 12.0:
            return '1. Low DTI (<12%)'
        elif d < 20.0:
            return '2. Moderate DTI (12-20%)'
        elif d < 28.0:
            return '3. High DTI (20-28%)'
        else:
            return '4. Critical DTI (>28%)'
            
    def bucket_util(u):
        if u < 30.0:
            return '1. Low Util (<30%)'
        elif u < 60.0:
            return '2. Moderate Util (30-60%)'
        elif u < 80.0:
            return '3. High Util (60-80%)'
        else:
            return '4. Critical Util (>80%)'
            
    def bucket_inq(q):
        if q == 0:
            return '0'
        elif q <= 2:
            return '1-2'
        else:
            return '3+'
            
    profile_df['dti_band'] = profile_df['dti'].apply(bucket_dti)
    profile_df['revol_util_band'] = profile_df['revol_util'].apply(bucket_util)
    profile_df['delinq_2yrs_flag'] = (profile_df['delinq_2yrs'] > 0).astype(int)
    profile_df['inq_last_6mths_band'] = profile_df['inq_last_6mths'].apply(bucket_inq)
    
    cr_hist_years = (pd.to_datetime(profile_df['issue_d']) - pd.to_datetime(profile_df['earliest_cr_line'])).dt.days / 365.25
    profile_df['credit_history_years'] = cr_hist_years.round(1)
    
    dim_credit_profile = profile_df[['credit_profile_key', 'dti_band', 'revol_util_band', 'delinq_2yrs_flag', 'inq_last_6mths_band', 'credit_history_years']]
    dim_credit_profile.to_csv(os.path.join(output_dir, 'dim_credit_profile.csv'), index=False)
    
    # fact_loan_portfolio
    fact_df = df.copy()
    fact_df['loan_key'] = np.arange(1, len(fact_df) + 1)
    fact_df['borrower_key'] = borrower_df['borrower_key']
    fact_df['credit_profile_key'] = profile_df['credit_profile_key']
    
    # Lookup risk_grade_key
    sg_map = dim_risk_grade.set_index('sub_grade')['risk_grade_key'].to_dict()
    fact_df['risk_grade_key'] = fact_df['sub_grade'].map(sg_map)
    
    # Date key
    fact_df['issue_date_key'] = pd.to_datetime(fact_df['issue_d']).dt.strftime('%Y%m%d').astype(int)
    fact_df['loan_term_months'] = fact_df['term'].apply(lambda x: 36 if '36' in str(x) else 60)
    fact_df['loan_amount'] = fact_df['loan_amnt']
    fact_df['funded_amount'] = fact_df['loan_amnt']
    fact_df['interest_rate'] = fact_df['int_rate']
    fact_df['monthly_installment'] = fact_df['installment']
    fact_df['total_collected'] = fact_df['total_pymnt']
    
    fact_df['is_default'] = fact_df['loan_status'].apply(lambda s: 1 if s in ['Charged Off', 'Default'] else 0)
    
    # Net charge-off loss: principal - recoveries - payments
    def calc_loss(row):
        if row['is_default'] == 1:
            loss = max(0.0, row['loan_amount'] - row['total_collected'] - row['recoveries'])
            return round(loss, 2)
        return 0.0
        
    fact_df['net_charge_off_loss'] = fact_df.apply(calc_loss, axis=1)
    
    # Synthetic baseline predicted default prob and calibrated credit score
    # (Will be refined by ML scorecard script)
    grade_score_map = {
        'A': (760, 0.04), 'B': (710, 0.10), 'C': (665, 0.17),
        'D': (620, 0.24), 'E': (575, 0.32), 'F': (530, 0.40), 'G': (490, 0.48)
    }
    pred_probs = []
    credit_scores = []
    for g, is_def in zip(fact_df['grade'], fact_df['is_default']):
        base_s, base_p = grade_score_map[g]
        score = int(np.random.normal(base_s, 22))
        score = max(300, min(850, score))
        p = round(max(0.01, min(0.95, base_p + np.random.normal(0, 0.04))), 4)
        pred_probs.append(p)
        credit_scores.append(score)
        
    fact_df['predicted_default_prob'] = pred_probs
    fact_df['credit_score'] = credit_scores
    
    fact_cols = [
        'loan_key', 'loan_id', 'issue_date_key', 'borrower_key', 'credit_profile_key',
        'risk_grade_key', 'loan_term_months', 'loan_amount', 'funded_amount',
        'interest_rate', 'monthly_installment', 'total_collected', 'net_charge_off_loss',
        'is_default', 'predicted_default_prob', 'credit_score'
    ]
    fact_loan_portfolio = fact_df[fact_cols]
    fact_loan_portfolio.to_csv(os.path.join(output_dir, 'fact_loan_portfolio.csv'), index=False)
    print(f"Star-schema facts and dimensions saved to: {output_dir}")


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = script_dir  # writes CSVs directly to 02_Credit_Risk/data/
    
    print("=" * 70)
    print("LendingClub Credit Risk Synthetic Data Generator")
    print("=" * 70)
    
    df = generate_lending_club_data(num_records=25000, seed=42)
    prepare_and_export_datasets(df, output_dir)
    print("=" * 70)
    print("Data generation completed successfully.")


if __name__ == '__main__':
    main()
