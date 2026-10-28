"""
build_db.py - SQLite Star-Schema Database Builder and Query Runner

Initializes credit_risk.db, executes schema.sql DDL, ingests all generated CSVs,
executes analytical risk queries from queries.sql, and validates integrity.
"""

import os
import sqlite3
import pandas as pd


def build_database():
    sql_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(sql_dir)
    data_dir = os.path.join(project_dir, 'data')
    db_path = os.path.join(sql_dir, 'credit_risk.db')
    schema_path = os.path.join(sql_dir, 'schema.sql')
    queries_path = os.path.join(sql_dir, 'queries.sql')
    
    print("=" * 70)
    print("Building Credit Risk SQLite Database")
    print(f"Database destination: {db_path}")
    print("=" * 70)
    
    # 1. Connect and initialize schema
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    print("Successfully executed schema.sql DDL.")
    
    # 2. Ingest datasets
    tables_to_csv = [
        ('loans_data', os.path.join(data_dir, 'loans_data.csv')),
        ('dim_risk_grade', os.path.join(data_dir, 'dim_risk_grade.csv')),
        ('dim_borrower', os.path.join(data_dir, 'dim_borrower.csv')),
        ('dim_credit_profile', os.path.join(data_dir, 'dim_credit_profile.csv')),
        ('dim_date', os.path.join(data_dir, 'dim_date.csv')),
        ('fact_loan_portfolio', os.path.join(data_dir, 'fact_loan_portfolio.csv'))
    ]
    
    for table_name, csv_path in tables_to_csv:
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Required data file missing: {csv_path}. Run generate_data.py first.")
        
        df = pd.read_csv(csv_path)
        df.to_sql(table_name, conn, if_exists='append', index=False)
        row_count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"Ingested {row_count:>6} rows into table: {table_name}")
        
    conn.commit()
    print("-" * 70)
    print("Database tables populated successfully.")
    
    # 3. Test Master View
    view_count = cursor.execute("SELECT COUNT(*) FROM vw_credit_risk_master").fetchone()[0]
    print(f"Verified vw_credit_risk_master contains {view_count} rows.")
    
    # 4. Execute analytical queries from queries.sql
    print("=" * 70)
    print("Executing Analytical Queries from queries.sql")
    print("=" * 70)
    
    with open(queries_path, 'r', encoding='utf-8') as f:
        queries_content = f.read()
        
    # Split queries by semicolon separator
    raw_queries = queries_content.split(';')
    query_num = 1
    
    for raw_q in raw_queries:
        cleaned_q = raw_q.strip()
        if not cleaned_q:
            continue
            
        print(f"\n--- Query {query_num} ---")
        lines = [line.strip() for line in cleaned_q.split('\n') if line.strip().startswith('--')]
        header = " ".join(lines).replace('--', '').strip()
        if header:
            print(f"Description: {header}")
            
        result_df = pd.read_sql_query(cleaned_q, conn)
        print(f"Result shape: {result_df.shape[0]} rows x {result_df.shape[1]} cols")
        # Print top rows
        print(result_df.head(8).to_string(index=False))
        query_num += 1
        
    conn.close()
    print("\n" + "=" * 70)
    print(f"Credit risk database build & verification passed cleanly: {db_path}")
    print("=" * 70)


def main():
    build_database()


if __name__ == '__main__':
    main()
