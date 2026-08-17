# Smart Energy Consumption Anomaly Detection System

An analytics platform for processing IoT smart meter data, detecting consumption anomalies (spikes, extended zero outages, pattern deviations), computing usage aggregations, and forecasting demand using a 7-day Simple Moving Average (SMA).

Uses the Medallion Architecture (Bronze -> Silver -> Gold).

---

## Architecture Overview

```
+-----------------------------------------------------------------------+
|                         RAW DATA SOURCES                              |
|          meter_readings.csv (IoT)  |  household_info.csv              |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                      BRONZE LAYER (RAW INGESTION)                     |
|  - Partitioning by date (/bronze/meter_readings/date=YYYY-MM-DD/)     |
|  - Tagging ingestion timestamps (_ingestion_time)                     |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    SILVER LAYER (CURATED PROCESSING)                  |
|  - Deduplication by (meter_id, timestamp)                             |
|  - Validation and null/negative filtering                             |
|  - Sequence gap filling (Forward-fill, is_imputed = true)             |
|  - Merging household metadata (city, house_type)                      |
|  - Anomaly detection (Spike, Zero-Extended, Deviation)                |
+-----------------------------------+-----------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------+
|                    GOLD LAYER (ANALYTICS & PREDICTIONS)               |
|  - Hourly, Daily, and Monthly Aggregations                            |
|  - 7-Day Simple Moving Average (SMA) Demand Forecasting               |
|  - Anomaly alerts and consumption trends                              |
+-----------------------------------------------------------------------+
```

---

## Anomaly Detection Rules

1. **Spike (`is_spike`)**: Consumption >= 3x meter's rolling average.
2. **Zero Outage (`is_zero_extended`)**: Zero consumption (0.0 kWh) for >= 3 consecutive hours.
3. **Pattern Deviation (`is_deviation`)**: Reading outside Mean ± 2σ for the same hour-of-week window.

---

## Repository Structure

```
Smart-Energy-Consumption-Anomaly-Detection-System-main/
├── Smart_Meter_Problem_Statement.docx
├── household_info.csv
├── meter_readings.csv
├── requirements.txt
├── README.md
├── data/
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── notebooks/
│   └── smart_meter_analytics.ipynb
└── output/
    ├── reports/
    └── visualizations/
```

---

## Performance & Metrics

| Metric | Target KPI | Achieved | Status |
| --- | --- | --- | --- |
| Pipeline Latency | < 15.0 minutes | 0.29 seconds | PASS |
| Data Completeness | >= 98.0% | 98.57% | PASS |
| 7-Day SMA Forecast MAPE | <= 15.0% | 11.73% | PASS |
| Anomaly Detection | Multi-rule | 27 Flagged | PASS |
