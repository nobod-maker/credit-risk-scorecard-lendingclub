"""
build_pbi_model.py - Generates Enterprise PBIR and TMDL Power BI Project Structure

Creates:
- Credit_Risk_Command_Center.pbip
- Credit_Risk_Command_Center.Report/ (definition.pbir, .platform, definition/version.json, report.json, pages, visuals)
- Credit_Risk_Command_Center.SemanticModel/ (definition.pbism, .platform, model.tmdl, relationships.tmdl, tables/*.tmdl)
"""

import os
import json


def create_pbi_structure():
    pbi_dir = os.path.dirname(os.path.abspath(__file__))
    
    report_folder = os.path.join(pbi_dir, "Credit_Risk_Command_Center.Report")
    semantic_folder = os.path.join(pbi_dir, "Credit_Risk_Command_Center.SemanticModel")
    
    os.makedirs(report_folder, exist_ok=True)
    os.makedirs(semantic_folder, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # 1. PBIP Project Root File
    # -------------------------------------------------------------------------
    pbip_path = os.path.join(pbi_dir, "Credit_Risk_Command_Center.pbip")
    pbip_content = {
        "version": "1.0",
        "artifacts": [
            {
                "report": {
                    "path": "Credit_Risk_Command_Center.Report"
                }
            }
        ],
        "settings": {}
    }
    with open(pbip_path, "w", encoding="utf-8") as f:
        json.dump(pbip_content, f, indent=2)
    print(f"Created: {pbip_path}")
    
    # -------------------------------------------------------------------------
    # 2. Report Folder & Definition
    # -------------------------------------------------------------------------
    definition_pbir = {
        "version": "4.0",
        "datasetReference": {
            "byPath": {
                "path": "../Credit_Risk_Command_Center.SemanticModel"
            }
        }
    }
    with open(os.path.join(report_folder, "definition.pbir"), "w", encoding="utf-8") as f:
        json.dump(definition_pbir, f, indent=2)

    report_platform = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {
            "type": "Report",
            "displayName": "Credit_Risk_Command_Center"
        },
        "config": {
            "version": "2.0",
            "logicalId": "02000000-0000-0000-0000-000000000002"
        }
    }
    with open(os.path.join(report_folder, ".platform"), "w", encoding="utf-8") as f:
        json.dump(report_platform, f, indent=2)

    report_def_dir = os.path.join(report_folder, "definition")
    os.makedirs(report_def_dir, exist_ok=True)

    version_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
        "version": "2.0.0"
    }
    with open(os.path.join(report_def_dir, "version.json"), "w", encoding="utf-8") as f:
        json.dump(version_json, f, indent=2)

    report_json = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/1.2.0/schema.json",
        "themeCollection": {
            "baseTheme": {
                "name": "CY24SU02",
                "reportVersionAtImport": "5.55"
            }
        },
        "layoutOptimization": "None",
        "settings": {
            "useStylableVisualContainerHeader": True,
            "defaultDrillFilterOtherVisuals": True,
            "allowChangeFilterTypes": True,
            "useEnhancedTooltips": True,
            "useDefaultAggregateDisplayName": True
        }
    }
    with open(os.path.join(report_def_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report_json, f, indent=2)

    # Pages setup
    pages_dir = os.path.join(report_def_dir, "pages")
    os.makedirs(pages_dir, exist_ok=True)

    pages_metadata = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
        "pageOrder": ["page_portfolio_overview", "page_score_distribution", "page_cutoff_simulator"],
        "activePageName": "page_portfolio_overview"
    }
    with open(os.path.join(pages_dir, "pages.json"), "w", encoding="utf-8") as f:
        json.dump(pages_metadata, f, indent=2)

    pages = [
        {
            "id": "page_portfolio_overview",
            "name": "page_portfolio_overview",
            "displayName": "Portfolio Risk & Losses",
            "visuals": [
                {
                    "name": "card_portfolio_volume",
                    "position": {"x": 20, "y": 20, "z": 1000, "height": 110, "width": 260, "tabOrder": 1000},
                    "visualType": "card",
                    "projection": "Total Funded Volume"
                },
                {
                    "name": "card_default_rate",
                    "position": {"x": 300, "y": 20, "z": 2000, "height": 110, "width": 260, "tabOrder": 2000},
                    "visualType": "card",
                    "projection": "Default Rate %"
                },
                {
                    "name": "card_default_losses",
                    "position": {"x": 580, "y": 20, "z": 3000, "height": 110, "width": 260, "tabOrder": 3000},
                    "visualType": "card",
                    "projection": "Total Default Losses"
                },
                {
                    "name": "bar_grade_risk",
                    "position": {"x": 20, "y": 150, "z": 4000, "height": 520, "width": 620, "tabOrder": 4000},
                    "visualType": "barChart",
                    "projection": "Default Rate % by Grade"
                }
            ]
        },
        {
            "id": "page_score_distribution",
            "name": "page_score_distribution",
            "displayName": "Credit Score & Calibration",
            "visuals": [
                {
                    "name": "card_avg_credit_score",
                    "position": {"x": 20, "y": 20, "z": 1000, "height": 110, "width": 280, "tabOrder": 1000},
                    "visualType": "card",
                    "projection": "Avg Credit Score"
                },
                {
                    "name": "matrix_dti_util",
                    "position": {"x": 20, "y": 150, "z": 2000, "height": 520, "width": 600, "tabOrder": 2000},
                    "visualType": "matrix",
                    "projection": "DTI vs Revolving Utilization Matrix"
                },
                {
                    "name": "column_score_hist",
                    "position": {"x": 640, "y": 150, "z": 3000, "height": 520, "width": 600, "tabOrder": 3000},
                    "visualType": "columnChart",
                    "projection": "Applicant Score Distribution"
                }
            ]
        },
        {
            "id": "page_cutoff_simulator",
            "name": "page_cutoff_simulator",
            "displayName": "Profit & Cut-Off Simulator",
            "visuals": [
                {
                    "name": "slicer_cutoff",
                    "position": {"x": 20, "y": 20, "z": 1000, "height": 110, "width": 240, "tabOrder": 1000},
                    "visualType": "slicer",
                    "projection": "Cut-Off Score Slider"
                },
                {
                    "name": "card_approval_rate",
                    "position": {"x": 280, "y": 20, "z": 2000, "height": 110, "width": 240, "tabOrder": 2000},
                    "visualType": "card",
                    "projection": "Approval Rate %"
                },
                {
                    "name": "card_approved_bad_rate",
                    "position": {"x": 540, "y": 20, "z": 3000, "height": 110, "width": 240, "tabOrder": 3000},
                    "visualType": "card",
                    "projection": "Portfolio Default Rate @ Cutoff %"
                },
                {
                    "name": "card_expected_profit",
                    "position": {"x": 800, "y": 20, "z": 4000, "height": 110, "width": 280, "tabOrder": 4000},
                    "visualType": "card",
                    "projection": "Expected Portfolio Profit"
                }
            ]
        }
    ]

    for p in pages:
        p_dir = os.path.join(pages_dir, p["id"])
        os.makedirs(p_dir, exist_ok=True)
        page_json = {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
            "name": p["name"],
            "displayName": p["displayName"],
            "displayOption": "FitToPage",
            "height": 720,
            "width": 1280
        }
        with open(os.path.join(p_dir, "page.json"), "w", encoding="utf-8") as f:
            json.dump(page_json, f, indent=2)

        vis_dir = os.path.join(p_dir, "visuals")
        os.makedirs(vis_dir, exist_ok=True)
        for v in p["visuals"]:
            v_dir = os.path.join(vis_dir, v["name"])
            os.makedirs(v_dir, exist_ok=True)
            vis_json = {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json",
                "name": v["name"],
                "position": v["position"],
                "visual": {
                    "visualType": v["visualType"],
                    "query": {
                        "queryState": {
                            "Values": {
                                "projections": [v["projection"]]
                            }
                        }
                    },
                    "drillFilterOtherVisuals": True
                }
            }
            with open(os.path.join(v_dir, "visual.json"), "w", encoding="utf-8") as f:
                json.dump(vis_json, f, indent=2)

    print("Created PBIR Report metadata and visual schemas.")

    # -------------------------------------------------------------------------
    # 3. Semantic Model Folder & TMDL Schemas
    # -------------------------------------------------------------------------
    pbism = {
        "version": "4.0",
        "settings": {}
    }
    with open(os.path.join(semantic_folder, "definition.pbism"), "w", encoding="utf-8") as f:
        json.dump(pbism, f, indent=2)

    semantic_platform = {
        "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
        "metadata": {
            "type": "SemanticModel",
            "displayName": "Credit_Risk_Command_Center"
        },
        "config": {
            "version": "2.0",
            "logicalId": "02000000-0000-0000-0000-000000000001"
        }
    }
    with open(os.path.join(semantic_folder, ".platform"), "w", encoding="utf-8") as f:
        json.dump(semantic_platform, f, indent=2)

    sem_def_dir = os.path.join(semantic_folder, "definition")
    os.makedirs(sem_def_dir, exist_ok=True)

    # model.tmdl (tab indentation required)
    model_tmdl = (
        "model Model\n"
        "\tculture: en-US\n"
        "\tdefaultPowerBIDataSourceVersion: powerBI_V3\n"
        "\tsourceQueryCulture: en-US\n"
        "\tdataAccessOptions\n"
        "\t\tlegacyRedirects\n"
        "\t\treturnErrorValuesAsNull\n"
    )
    with open(os.path.join(sem_def_dir, "model.tmdl"), "w", encoding="utf-8") as f:
        f.write(model_tmdl)

    # relationships.tmdl
    rel_tmdl = (
        "relationship Rel_IssueDate_Fact\n"
        "\tfromColumn: fact_loan_portfolio.issue_date_key\n"
        "\ttoColumn: dim_date.date_key\n\n"
        "relationship Rel_RiskGrade_Fact\n"
        "\tfromColumn: fact_loan_portfolio.risk_grade_key\n"
        "\ttoColumn: dim_risk_grade.risk_grade_key\n\n"
        "relationship Rel_Borrower_Fact\n"
        "\tfromColumn: fact_loan_portfolio.borrower_key\n"
        "\ttoColumn: dim_borrower.borrower_key\n\n"
        "relationship Rel_CreditProfile_Fact\n"
        "\tfromColumn: fact_loan_portfolio.credit_profile_key\n"
        "\ttoColumn: dim_credit_profile.credit_profile_key\n"
    )
    with open(os.path.join(sem_def_dir, "relationships.tmdl"), "w", encoding="utf-8") as f:
        f.write(rel_tmdl)

    # tables/ directory
    tables_dir = os.path.join(sem_def_dir, "tables")
    os.makedirs(tables_dir, exist_ok=True)

    # fact_loan_portfolio.tmdl
    fact_tmdl = (
        "table fact_loan_portfolio\n"
        "\tlineageTag: 20000000-0000-0000-0000-000000000001\n\n"
        "\tcolumn loan_key\n"
        "\t\tdataType: int64\n"
        "\t\tisKey\n"
        "\t\tformatString: 0\n"
        "\t\tsourceColumn: loan_key\n\n"
        "\tcolumn loan_id\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: loan_id\n\n"
        "\tcolumn issue_date_key\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: issue_date_key\n\n"
        "\tcolumn borrower_key\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: borrower_key\n\n"
        "\tcolumn credit_profile_key\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: credit_profile_key\n\n"
        "\tcolumn risk_grade_key\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: risk_grade_key\n\n"
        "\tcolumn loan_term_months\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: loan_term_months\n\n"
        "\tcolumn loan_amount\n"
        "\t\tdataType: decimal\n"
        "\t\tformatString: \"$#,##0\"\n"
        "\t\tsourceColumn: loan_amount\n\n"
        "\tcolumn funded_amount\n"
        "\t\tdataType: decimal\n"
        "\t\tformatString: \"$#,##0\"\n"
        "\t\tsourceColumn: funded_amount\n\n"
        "\tcolumn interest_rate\n"
        "\t\tdataType: double\n"
        "\t\tformatString: \"0.0%\"\n"
        "\t\tsourceColumn: interest_rate\n\n"
        "\tcolumn monthly_installment\n"
        "\t\tdataType: decimal\n"
        "\t\tsourceColumn: monthly_installment\n\n"
        "\tcolumn total_collected\n"
        "\t\tdataType: decimal\n"
        "\t\tsourceColumn: total_collected\n\n"
        "\tcolumn net_charge_off_loss\n"
        "\t\tdataType: decimal\n"
        "\t\tformatString: \"$#,##0\"\n"
        "\t\tsourceColumn: net_charge_off_loss\n\n"
        "\tcolumn is_default\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: is_default\n\n"
        "\tcolumn predicted_default_prob\n"
        "\t\tdataType: double\n"
        "\t\tformatString: \"0.0%\"\n"
        "\t\tsourceColumn: predicted_default_prob\n\n"
        "\tcolumn credit_score\n"
        "\t\tdataType: int64\n"
        "\t\tformatString: 0\n"
        "\t\tsourceColumn: credit_score\n\n"
        "\tmeasure 'Total Applications' = COUNTROWS(fact_loan_portfolio)\n"
        "\t\tformatString: \"#,##0\"\n\n"
        "\tmeasure 'Total Funded Volume' = SUM(fact_loan_portfolio[funded_amount])\n"
        "\t\tformatString: \"$#,##0\"\n\n"
        "\tmeasure 'Default Loans' = CALCULATE(COUNTROWS(fact_loan_portfolio), fact_loan_portfolio[is_default] = 1)\n"
        "\t\tformatString: \"#,##0\"\n\n"
        "\tmeasure 'Default Rate %' = DIVIDE([Default Loans], [Total Applications], 0.0)\n"
        "\t\tformatString: \"0.0%\"\n\n"
        "\tmeasure 'Total Default Losses' = CALCULATE(SUM(fact_loan_portfolio[net_charge_off_loss]), fact_loan_portfolio[is_default] = 1)\n"
        "\t\tformatString: \"$#,##0\"\n\n"
        "\tmeasure 'Avg Credit Score' = AVERAGE(fact_loan_portfolio[credit_score])\n"
        "\t\tformatString: 0\n\n"
        "\tpartition fact_loan_portfolio = m\n"
        "\t\tmode: import\n"
        "\t\tsource = \n"
        "\t\t\tlet\n"
        "\t\t\t\tSource = Csv.Document(File.Contents(\"data/fact_loan_portfolio.csv\"), [Delimiter=\",\", Columns=16, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
        "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
        "\t\t\tin\n"
        "\t\t\t\t#\"Promoted Headers\"\n"
    )
    with open(os.path.join(tables_dir, "fact_loan_portfolio.tmdl"), "w", encoding="utf-8") as f:
        f.write(fact_tmdl)

    # dim_risk_grade.tmdl
    grade_tmdl = (
        "table dim_risk_grade\n"
        "\tlineageTag: 20000000-0000-0000-0000-000000000002\n\n"
        "\tcolumn risk_grade_key\n"
        "\t\tdataType: int64\n"
        "\t\tisKey\n"
        "\t\tformatString: 0\n"
        "\t\tsourceColumn: risk_grade_key\n\n"
        "\tcolumn grade\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: grade\n\n"
        "\tcolumn sub_grade\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: sub_grade\n\n"
        "\tcolumn grade_rank\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: grade_rank\n\n"
        "\tcolumn benchmark_loss_rate_pct\n"
        "\t\tdataType: double\n"
        "\t\tformatString: \"0.0%\"\n"
        "\t\tsourceColumn: benchmark_loss_rate_pct\n\n"
        "\tpartition dim_risk_grade = m\n"
        "\t\tmode: import\n"
        "\t\tsource = \n"
        "\t\t\tlet\n"
        "\t\t\t\tSource = Csv.Document(File.Contents(\"data/dim_risk_grade.csv\"), [Delimiter=\",\", Columns=5, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
        "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
        "\t\t\tin\n"
        "\t\t\t\t#\"Promoted Headers\"\n"
    )
    with open(os.path.join(tables_dir, "dim_risk_grade.tmdl"), "w", encoding="utf-8") as f:
        f.write(grade_tmdl)

    # dim_borrower.tmdl
    borrower_tmdl = (
        "table dim_borrower\n"
        "\tlineageTag: 20000000-0000-0000-0000-000000000003\n\n"
        "\tcolumn borrower_key\n"
        "\t\tdataType: int64\n"
        "\t\tisKey\n"
        "\t\tformatString: 0\n"
        "\t\tsourceColumn: borrower_key\n\n"
        "\tcolumn emp_length_bucket\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: emp_length_bucket\n\n"
        "\tcolumn home_ownership\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: home_ownership\n\n"
        "\tcolumn annual_income\n"
        "\t\tdataType: decimal\n"
        "\t\tformatString: \"$#,##0\"\n"
        "\t\tsourceColumn: annual_income\n\n"
        "\tcolumn income_bracket\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: income_bracket\n\n"
        "\tcolumn verification_status\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: verification_status\n\n"
        "\tpartition dim_borrower = m\n"
        "\t\tmode: import\n"
        "\t\tsource = \n"
        "\t\t\tlet\n"
        "\t\t\t\tSource = Csv.Document(File.Contents(\"data/dim_borrower.csv\"), [Delimiter=\",\", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
        "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
        "\t\t\tin\n"
        "\t\t\t\t#\"Promoted Headers\"\n"
    )
    with open(os.path.join(tables_dir, "dim_borrower.tmdl"), "w", encoding="utf-8") as f:
        f.write(borrower_tmdl)

    # dim_credit_profile.tmdl
    profile_tmdl = (
        "table dim_credit_profile\n"
        "\tlineageTag: 20000000-0000-0000-0000-000000000004\n\n"
        "\tcolumn credit_profile_key\n"
        "\t\tdataType: int64\n"
        "\t\tisKey\n"
        "\t\tformatString: 0\n"
        "\t\tsourceColumn: credit_profile_key\n\n"
        "\tcolumn dti_band\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: dti_band\n\n"
        "\tcolumn revol_util_band\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: revol_util_band\n\n"
        "\tcolumn delinq_2yrs_flag\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: delinq_2yrs_flag\n\n"
        "\tcolumn inq_last_6mths_band\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: inq_last_6mths_band\n\n"
        "\tcolumn credit_history_years\n"
        "\t\tdataType: double\n"
        "\t\tsourceColumn: credit_history_years\n\n"
        "\tpartition dim_credit_profile = m\n"
        "\t\tmode: import\n"
        "\t\tsource = \n"
        "\t\t\tlet\n"
        "\t\t\t\tSource = Csv.Document(File.Contents(\"data/dim_credit_profile.csv\"), [Delimiter=\",\", Columns=6, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
        "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
        "\t\t\tin\n"
        "\t\t\t\t#\"Promoted Headers\"\n"
    )
    with open(os.path.join(tables_dir, "dim_credit_profile.tmdl"), "w", encoding="utf-8") as f:
        f.write(profile_tmdl)

    # dim_date.tmdl
    date_tmdl = (
        "table dim_date\n"
        "\tlineageTag: 20000000-0000-0000-0000-000000000005\n\n"
        "\tcolumn date_key\n"
        "\t\tdataType: int64\n"
        "\t\tisKey\n"
        "\t\tformatString: 0\n"
        "\t\tsourceColumn: date_key\n\n"
        "\tcolumn full_date\n"
        "\t\tdataType: dateTime\n"
        "\t\tformatString: \"yyyy-mm-dd\"\n"
        "\t\tsourceColumn: full_date\n\n"
        "\tcolumn year\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: year\n\n"
        "\tcolumn quarter\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: quarter\n\n"
        "\tcolumn year_quarter\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: year_quarter\n\n"
        "\tcolumn month\n"
        "\t\tdataType: int64\n"
        "\t\tsourceColumn: month\n\n"
        "\tcolumn month_name\n"
        "\t\tdataType: string\n"
        "\t\tsourceColumn: month_name\n\n"
        "\tpartition dim_date = m\n"
        "\t\tmode: import\n"
        "\t\tsource = \n"
        "\t\t\tlet\n"
        "\t\t\t\tSource = Csv.Document(File.Contents(\"data/dim_date.csv\"), [Delimiter=\",\", Columns=10, Encoding=65001, QuoteStyle=QuoteStyle.None]),\n"
        "\t\t\t\t#\"Promoted Headers\" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])\n"
        "\t\t\tin\n"
        "\t\t\t\t#\"Promoted Headers\"\n"
    )
    with open(os.path.join(tables_dir, "dim_date.tmdl"), "w", encoding="utf-8") as f:
        f.write(date_tmdl)

    # Cutoff_Parameter.tmdl
    param_tmdl = (
        "table Cutoff_Parameter\n"
        "\tlineageTag: 20000000-0000-0000-0000-000000000006\n\n"
        "\tcolumn Cutoff_Value\n"
        "\t\tdataType: int64\n"
        "\t\tisKey\n"
        "\t\tformatString: 0\n"
        "\t\tsourceColumn: Cutoff_Value\n\n"
        "\tpartition Cutoff_Parameter = calculated\n"
        "\t\tmode: import\n"
        "\t\tsource = GENERATESERIES(500, 750, 10)\n"
    )
    with open(os.path.join(tables_dir, "Cutoff_Parameter.tmdl"), "w", encoding="utf-8") as f:
        f.write(param_tmdl)

    print("Created TMDL semantic model schemas.")
    print("=" * 70)
    print("Power BI PBIR and TMDL generation completed successfully.")


def main():
    create_pbi_structure()


if __name__ == '__main__':
    main()
