# Delta Lake Incremental Processing & SCD Assignment

Incremental data processing pipeline built with **Delta Lake**, **Python**, **DuckDB**, and **Pandas**.

It covers base dataset ingestion, data cleaning, staging deduplication, **SCD Type 1 (overwrite updates)**, **SCD Type 2 (history tracking)**, and integrity validations.

---

## 📁 Repository Structure

```text
delta-lake-assignment/
│
├── data/
│   ├── customer_master.csv               # Base customer dataset (793 records)
│   └── customer_incremental.csv          # Incremental batch (50 records: 30 updates, 15 inserts, 5 duplicates)
│
├── notebooks/
│   └── delta_scd_assignment.ipynb        # Executed notebook with code, outputs, and visualizations
│
├── screenshots/
│   ├── data_loading/                     # Screenshots of raw data loading
│   │   └── data_loading.png
│   ├── data_cleaning/                    # Screenshots of null handling & deduplication
│   │   └── data_cleaning.png
│   ├── scd1/                             # Screenshots of SCD Type 1 MERGE
│   │   └── scd1_merge.png
│   ├── scd2/                             # Screenshots of SCD Type 2 MERGE & history tracking
│   │   └── scd2_merge.png
│   ├── validation/                       # Screenshots of row count & key assertions
│   │   └── validation.png
│   └── final_output/                     # Screenshots of final analytics query & summary chart
│       └── final_output.png
│
├── report/
│   └── assignment_summary.pdf            # PDF summary document
│
└── README.md                             # Documentation
```

---

## 🔄 Workflow Summary

1. **Data Cleaning**: Imputed missing postal codes, set standard active `End_Date` (`9999-12-31`), and dropped dirty staging duplicates from the incoming batch.
2. **SCD Type 1 MERGE**: Overwrites updated customer attributes (`City`, `State`, `Total_Sales`, `Credit_Score`) for matching `Customer_ID`s and inserts new customers.
3. **SCD Type 2 MERGE**: Expires old active version (`Is_Active = False`, `End_Date = '2026-08-02'`) and appends new active version (`Is_Active = True`, `Record_Version = 3`).
4. **Validation**: Enforces zero duplicate active primary keys and verifies active row counts.

---

## 📊 Record Counts & Metrics

| Dataset / Stage | Record Count | Uniqueness Check | Status |
| :--- | :--- | :--- | :--- |
| **customer_master.csv** | 793 | Unique Primary Keys | Initialized |
| **customer_incremental.csv** | 50 | Includes 5 Duplicates | Sanitized to 45 |
| **SCD Type 1 Post-Merge Active** | 808 | 0 Duplicate Active Keys | Verified |
| **SCD Type 2 Total Table Rows** | 810 | 1 History + 808 Active | Verified (100%) |
